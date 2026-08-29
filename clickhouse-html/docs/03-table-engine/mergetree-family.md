---
title: MergeTree 表引擎家族
date: 2026-08-15  # date-auto-injected
description: MergeTree / ReplacingMergeTree / AggregatingMergeTree / CollapsingMergeTree / VersionedCollapsingMergeTree / SummingMergeTree 完整对比
---

# MergeTree 表引擎家族

MergeTree 是 ClickHouse 的核心引擎，LSM 风格（写入即后台合并），家族有 6 个变种，覆盖 80% 的场景。

## MergeTree（基础）

```sql
CREATE TABLE events (
  event_date Date,
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  amount Decimal(18, 2)
)
ENGINE = MergeTree()
PARTITION BY event_date       -- 按天分区
ORDER BY (user_id, event_time) -- 排序键（主键）
SETTINGS index_granularity = 8192;  -- 索引粒度（默认 8192）
```

**关键参数**：
- `PARTITION BY`：分区键（通常按时间），影响查询时数据扫描量
- `ORDER BY`：排序键（必填），决定主键索引和压缩比
- `SETTINGS.index_granularity`：索引粒度（默认 8192 行），越小查询越快但索引越大

## ReplacingMergeTree（去重）

**场景**：支持重复写入（如 Kafka 重投），后台自动去重。

```sql
CREATE TABLE user_events (
  event_time DateTime,
  user_id UInt64,
  event_type String,
  payload String
)
ENGINE = ReplacingMergeTree(event_time)  -- 按 event_time 列保留最新
PARTITION BY toYYYYMM(event_time)
ORDER BY (user_id, event_type)

-- 写入重复数据
INSERT INTO user_events VALUES (now(), 1, 'click', '{}')
INSERT INTO user_events VALUES (now(), 1, 'click', '{...new...}')
-- 后台合并时保留 event_time 最大的那一行

-- ⚠️ ReplacingMergeTree 去重是异步的（合并时执行）
-- 实时查询可能看到重复数据，需要 FINAL 强制合并
SELECT * FROM user_events FINAL WHERE user_id = 1
```

**最佳实践**：业务层保证幂等（按唯一键去重），ReplacingMergeTree 是兜底。

## AggregatingMergeTree（预聚合）

**场景**：实时指标、UV / DAU / 漏斗等高频聚合查询。

```sql
-- 基础表（存明细）
CREATE TABLE events (
  event_date Date,
  user_id UInt64,
  event_type LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (event_date, event_type)

-- 物化视图（预聚合）
CREATE TABLE events_agg (
  event_date Date,
  event_type LowCardinality(String),
  uv_bitmap AggregateFunction(groupBitmap, UInt64),
  pv_count AggregateFunction(count, UInt64)
)
ENGINE = AggregatingMergeTree()
PARTITION BY event_date
ORDER BY (event_date, event_type)

CREATE MATERIALIZED VIEW events_agg_mv
TO events_agg AS
SELECT
  event_date,
  event_type,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv_count
FROM events
GROUP BY event_date, event_type

-- 查询（自动合并 State）
SELECT
  event_date,
  event_type,
  bitmapCardinality(merge(uv_bitmap)) AS uv,
  sumMerge(pv_count) AS pv
FROM events_agg
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-07'
GROUP BY event_date, event_type
```

**核心 State 函数**：

| 聚合函数 | State 函数 | Merge 函数 |
|---|---|---|
| `count` | `countState` | `countMerge` |
| `sum` | `sumState` | `sumMerge` |
| `avg` | `avgState` | `avgMerge` |
| `uniq` | `uniqState` | `uniqMerge` |
| `groupBitmap` | `groupBitmapState` | `groupBitmapMerge` |
| `quantile` | `quantileState` | `quantileMerge` |

## CollapsingMergeTree（折叠删除）

**场景**：支持删除操作（异步），用 `sign` 列标记。

```sql
CREATE TABLE user_balance (
  user_id UInt64,
  balance Int64,
  sign Int8  -- 1 = 新增，-1 = 折叠
)
ENGINE = CollapsingMergeTree(sign)
ORDER BY user_id

-- 插入
INSERT INTO user_balance VALUES (1, 100, 1)
INSERT INTO user_balance VALUES (1, 100, -1)
INSERT INTO user_balance VALUES (1, 200, 1)
-- 合并后只剩 balance=200 的那一行

-- 查询（必须 FINAL）
SELECT * FROM user_balance FINAL WHERE user_id = 1
```

**问题**：`sign` 错乱会导致数据不一致，建议改用 `VersionedCollapsingMergeTree`。

## VersionedCollapsingMergeTree（版本折叠）

**场景**：避免 `sign` 错乱导致的数据问题。

```sql
CREATE TABLE user_balance (
  user_id UInt64,
  balance Int64,
  sign Int8,        -- 1/-1
  version UInt64    -- 版本号（递增）
)
ENGINE = VersionedCollapsingMergeTree(sign, version)
ORDER BY user_id

-- 写入（version 必须递增）
INSERT INTO user_balance VALUES (1, 100, 1, 1)
INSERT INTO user_balance VALUES (1, 100, -1, 2)  -- 折叠上一行
INSERT INTO user_balance VALUES (1, 200, 1, 3)  -- 新增

-- 查询
SELECT * FROM user_balance FINAL WHERE user_id = 1
```

**优势**：即使 `sign` 错乱，`version` 保证折叠正确。

## SummingMergeTree（数值合并）

**场景**：所有列都是可累加的指标（如流量、点击量）。

```sql
CREATE TABLE metrics (
  metric_date Date,
  metric_name LowCardinality(String),
  value UInt64
)
ENGINE = SummingMergeTree()
PARTITION BY metric_date
ORDER BY (metric_date, metric_name)

-- 多次插入同 key 的数据，后台合并时会求和
INSERT INTO metrics VALUES ('2024-01-01', 'pv', 100)
INSERT INTO metrics VALUES ('2024-01-01', 'pv', 50)
-- 合并后：pv = 150
```

## 选型决策树

```text
                    你的表是？
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
    明细事件         需要去重          需要预聚合
        │               │               │
   MergeTree      ReplacingMergeTree  AggregatingMergeTree
                        │
                删除场景？
                ┌───────┴────────┐
                ▼                ▼
         CollapsingMergeTree  VersionedCollapsingMergeTree
                │
                ▼
           SummingMergeTree（全部是数值列）
```

## 实战：实时指标看板

```sql
-- 明细表（接收 Kafka 写入）
CREATE TABLE events_local (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  country LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_type)

-- 物化视图：每分钟 UV / PV
CREATE TABLE events_minute_agg (
  event_minute DateTime,
  country LowCardinality(String),
  event_type LowCardinality(String),
  uv_bitmap AggregateFunction(groupBitmap, UInt64),
  pv_count AggregateFunction(count)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_minute)
ORDER BY (event_minute, country, event_type)

CREATE MATERIALIZED VIEW events_minute_mv
TO events_minute_agg AS
SELECT
  toStartOfMinute(event_time) AS event_minute,
  country,
  event_type,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv_count
FROM events_local
GROUP BY event_minute, country, event_type

-- 查询
SELECT
  event_minute,
  country,
  sum(pv_count) AS pv,
  bitmapCardinality(merge(uv_bitmap)) AS uv
FROM events_minute_agg
WHERE event_minute >= now() - INTERVAL 1 HOUR
GROUP BY event_minute, country
```

## 下一步

- 学习 Kafka 引擎：见 [kafka-engine.md](./kafka-engine.md)
- 学习物化视图：见 [materialized-view.md](./materialized-view.md)

<!-- svg-injected:do-not-edit -->

## 图示：ClickHouse MergeTree 原理

![ClickHouse MergeTree 原理](/clickhouse-mergetree.svg)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [es](https://java-px.bot.cd/es/):ES 对比
- [bigdata](https://java-px.bot.cd/bigdata/):大数据生态
- [postgresql](https://java-px.bot.cd/postgresql/):PostgreSQL 对比
