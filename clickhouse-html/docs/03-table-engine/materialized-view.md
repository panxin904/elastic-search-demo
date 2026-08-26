---
title: MaterializedView 物化视图
description: ClickHouse 实时数仓核心：增量更新 / 自动触发 / 多链路组合
---

# MaterializedView 物化视图

MaterializedView 是 ClickHouse 实时数仓的杀手锏：**源表写入时自动触发，链式增量更新**，无需任何调度。

## 基础概念

```text
源表 INSERT
    │
    ▼
物化视图触发
    │
    ▼
目标表写入
```

**关键特性**：
- **增量更新**：源表每次 INSERT，物化视图都会处理新数据
- **链式触发**：物化视图的输出可以写入另一张表的源
- **可独立查询**：物化视图本质上是一张表，可以直接查询

## 基础示例

```sql
-- 源表
CREATE TABLE events (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  amount Decimal(18, 2)
)
ENGINE = MergeTree()
ORDER BY (event_time, user_id)

-- 物化视图（写入 target_table）
CREATE TABLE events_daily (
  event_date Date,
  event_type LowCardinality(String),
  uv AggregateFunction(groupBitmap, UInt64),
  pv AggregateFunction(count),
  gmv AggregateFunction(sum, Decimal(18, 2))
)
ENGINE = AggregatingMergeTree()
PARTITION BY event_date
ORDER BY (event_date, event_type)

CREATE MATERIALIZED VIEW events_daily_mv TO events_daily AS
SELECT
  toDate(event_time) AS event_date,
  event_type,
  groupBitmapState(user_id) AS uv,
  countState() AS pv,
  sumState(amount) AS gmv
FROM events
GROUP BY event_date, event_type
```

## 三种物化视图类型

### 1. TO 表（默认）

```sql
CREATE MATERIALIZED VIEW mv_name TO target_table AS
SELECT ... FROM source_table
```

数据写入 `target_table`，原表无变化。

### 2. 直接物化（不带 TO）

```sql
CREATE MATERIALIZED VIEW mv_name AS
SELECT ... FROM source_table
```

数据存在物化视图自身（不能修改），适合纯计算场景。

### 3. POPULATE（回填历史）

```sql
CREATE MATERIALIZED VIEW events_daily_mv TO events_daily
POPULATE AS  -- 回填历史数据
SELECT ...
FROM events
```

**警告**：`POPULATE` + 实时写入之间有数据缺失窗口，建议**离线回填**：

```sql
-- 1. 创建物化视图（不带 POPULATE）
CREATE MATERIALIZED VIEW events_daily_mv TO events_daily AS ...

-- 2. 暂停源表写入
DETACH TABLE events

-- 3. 手动回填
INSERT INTO events_daily SELECT
  toDate(event_time) AS event_date,
  event_type,
  groupBitmapState(user_id) AS uv,
  ...
FROM events
GROUP BY event_date, event_type

-- 4. 重新附加源表
ATTACH TABLE events
```

## 链式物化视图（实时数仓分层）

```text
Kafka → events_raw → MV1 → events_dwd → MV2 → events_dws → MV3 → events_ads
                       （明细）          （轻度汇总）       （高度汇总）
```

```sql
-- 第一层：DWD（明细）
CREATE TABLE events_dwd (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  country LowCardinality(String),
  amount Decimal(18, 2)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_time)

CREATE MATERIALIZED VIEW events_dwd_mv TO events_dwd AS
SELECT
  event_time,
  user_id,
  event_type,
  dictGet('user_dict', 'country', user_id) AS country,
  amount
FROM events_raw

-- 第二层：DWS（每日汇总）
CREATE TABLE events_dws (
  event_date Date,
  country LowCardinality(String),
  uv AggregateFunction(groupBitmap, UInt64),
  pv AggregateFunction(count),
  gmv AggregateFunction(sum, Decimal(18, 2))
)
ENGINE = AggregatingMergeTree()
PARTITION BY event_date
ORDER BY (event_date, country)

CREATE MATERIALIZED VIEW events_dws_mv TO events_dws AS
SELECT
  toDate(event_time) AS event_date,
  country,
  groupBitmapState(user_id) AS uv,
  countState() AS pv,
  sumState(amount) AS gmv
FROM events_dwd
GROUP BY event_date, country

-- 第三层：ADS（应用层）
CREATE TABLE events_ads_country_daily (...)
ENGINE = AggregatingMergeTree()
ORDER BY (event_date, country)
```

## 实战：实时数仓 + 多维看板

```sql
-- 1. 明细表（接 Kafka）
CREATE TABLE events_raw (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  country LowCardinality(String),
  page_url String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_time)

-- 2. 每分钟 UV/PV（分钟级实时看板）
CREATE TABLE events_minute_agg (
  event_minute DateTime,
  country LowCardinality(String),
  event_type LowCardinality(String),
  uv AggregateFunction(groupBitmap, UInt64),
  pv AggregateFunction(count)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_minute)
ORDER BY (event_minute, country, event_type)

CREATE MATERIALIZED VIEW events_minute_mv TO events_minute_agg AS
SELECT
  toStartOfMinute(event_time) AS event_minute,
  country,
  event_type,
  groupBitmapState(user_id) AS uv,
  countState() AS pv
FROM events_raw
GROUP BY event_minute, country, event_type

-- 3. 用户活跃度画像（最近 7 天）
CREATE TABLE user_active_7d (
  user_id UInt64,
  active_days AggregateFunction(groupBitmap, Date),
  event_count AggregateFunction(sum, UInt64)
)
ENGINE = AggregatingMergeTree()
ORDER BY user_id

CREATE MATERIALIZED VIEW user_active_7d_mv TO user_active_7d AS
SELECT
  user_id,
  groupBitmapState(toDate(event_time)) AS active_days,
  sumState(1) AS event_count
FROM events_raw
GROUP BY user_id

-- 实时查询
SELECT
  event_minute,
  country,
  bitmapCardinality(merge(uv)) AS uv,
  sum(pv) AS pv
FROM events_minute_agg
WHERE event_minute >= now() - INTERVAL 10 MINUTE
GROUP BY event_minute, country
```

## 删除物化视图

```sql
-- 删除物化视图（不会删除目标表）
DROP TABLE events_daily_mv

-- 删除目标表（注意顺序）
DROP TABLE events_daily_mv  -- 先删 MV
DROP TABLE events_daily       -- 再删表
```

## 修改物化视图

⚠️ **物化视图不能直接 ALTER**。如需修改：

1. DROP 旧视图
2. 修改目标表（如需要）
3. CREATE 新视图
4. 回填历史数据

## 监控

```sql
-- 查看所有物化视图
SELECT * FROM system.tables WHERE engine = 'MaterializedView'

-- 查看物化视图写入量
SELECT
  database,
  table,
  parts,
  rows
FROM system.parts
WHERE database = 'default' AND table LIKE '%_mv%'

-- 关键：materialized_view_block 计数器
SELECT * FROM system.events WHERE event LIKE '%MaterializedView%'
```

## 性能提示

### 1. 物化视图不要太多

每张 MV 都增加写入开销，建议：
- 高频查询（每分钟 100+ 次）：用 MV 预聚合
- 低频查询（每小时）：直接查明细

### 2. 避免在 MV 中做复杂 JOIN

```sql
-- ❌ 慢
CREATE MATERIALIZED VIEW slow_mv AS
SELECT a.*, b.user_name
FROM events_raw a
JOIN users b ON a.user_id = b.id

-- ✅ 好：用 Dictionary
CREATE MATERIALIZED VIEW fast_mv AS
SELECT
  event_time,
  user_id,
  dictGet('users_dict', 'user_name', user_id) AS user_name
FROM events_raw
```

### 3. 物化视图的 Order By 优化

```sql
CREATE TABLE events_daily (...)
ENGINE = AggregatingMergeTree()
ORDER BY (event_date, event_type)  -- 与查询 GROUP BY 顺序一致
```

## 下一步

- 学习 Kafka 引擎：见 [kafka-engine.md](./kafka-engine.md)
- 学习 OLAP 场景：见 [04-olap-scenarios/overview.md](../04-olap-scenarios/overview.md)


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
