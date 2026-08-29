---
title: 用户埋点分析
date: 2026-08-15  # date-auto-injected
description: 抖音 / B 站级埋点场景：Kafka + RoaringBitmap + 留存 / 漏斗 / 路径分析
---

# 用户埋点分析

用户埋点是 ClickHouse 主战场之一，每天 PB 级数据，秒级查询。

## 场景特征

```text
数据规模：    PB 级
写入频率：    100w+ events/s
查询延迟：    秒级
典型查询：    留存 / 漏斗 / 路径 / 人群画像 / 用户行为序列
用户：        抖音 / B 站 / 京东 / 网易 / 头条
```

## 完整架构

```text
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 客户端 SDK │ → │ Kafka    │ → │ CK Kafka │ → │ CK MergeTree│
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                     │
                     ├→ MV1: 实时 UV/PV
                     ├→ MV2: 留存 cohort
                     ├→ MV3: 漏斗
                     └→ MV4: 用户活跃度画像
```

## Schema 设计

### 基础事件表

```sql
CREATE TABLE events (
  event_time DateTime64(3),  -- 毫秒精度
  event_date Date DEFAULT toDate(event_time),
  user_id UInt64,
  session_id UUID,
  event_type LowCardinality(String),  -- 'click', 'view', 'like', 'share'
  page_url String,
  duration_ms UInt32,
  properties Map(String, String),  -- 灵活扩展字段
  -- 维度（业务经常加字段，建议预留）
  country LowCardinality(String) DEFAULT '',
  device_type LowCardinality(String) DEFAULT '',
  app_version String DEFAULT '',
  channel LowCardinality(String) DEFAULT ''
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (user_id, event_time)
SETTINGS index_granularity = 8192
```

**关键设计**：
- `DateTime64(3)`：毫秒精度（推荐）
- `LowCardinality`：状态/国家/设备类型等低基数字段
- `Map(String, String)`：灵活扩展字段（性能换灵活）
- `ORDER BY (user_id, event_time)`：用户行为查询为主

### 宽表（推荐做法）

如果业务需要经常 JOIN 维度表，建议用宽表：

```sql
CREATE TABLE events_wide (
  event_time DateTime64(3),
  event_date Date,
  user_id UInt64,
  user_name String,             -- 冗余 user 字段
  user_country LowCardinality(String),
  event_type LowCardinality(String),
  page_url String,
  duration_ms UInt32,
  product_id UInt64,            -- 冗余 product 字段
  product_name String,
  product_category LowCardinality(String),
  amount Decimal(18, 2)
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (user_id, event_time)
```

**优势**：单表查询，无需 JOIN，性能最佳。

## 实时 UV / PV

```sql
-- 物化视图
CREATE TABLE events_uv_pv_1m (
  event_minute DateTime,
  country LowCardinality(String),
  event_type LowCardinality(String),
  uv AggregateFunction(groupBitmap, UInt64),
  pv AggregateFunction(count)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_minute)
ORDER BY (event_minute, country, event_type)

CREATE MATERIALIZED VIEW events_uv_pv_1m_mv TO events_uv_pv_1m AS
SELECT
  toStartOfMinute(event_time) AS event_minute,
  country,
  event_type,
  groupBitmapState(user_id) AS uv,
  countState() AS pv
FROM events
GROUP BY event_minute, country, event_type

-- 查询（最近 10 分钟 UV/PV）
SELECT
  event_minute,
  country,
  bitmapCardinality(merge(uv)) AS uv,
  sumMerge(pv) AS pv
FROM events_uv_pv_1m
WHERE event_minute >= now() - INTERVAL 10 MINUTE
GROUP BY event_minute, country
ORDER BY event_minute, country
```

## 用户留存分析

```sql
-- Cohort 留存（按注册日分组，看后续活跃率）
WITH cohorts AS (
  SELECT
    user_id,
    min(event_date) AS signup_date
  FROM events
  GROUP BY user_id
)
SELECT
  cohort_date,
  dateDiff('day', cohort_date, event_date) AS day_offset,
  uniq(user_id) AS active_users
FROM cohorts c
JOIN events e ON c.user_id = e.user_id
WHERE cohort_date >= today() - INTERVAL 30 DAY
GROUP BY cohort_date, day_offset
ORDER BY cohort_date, day_offset

-- D1 / D7 / D30 留存（单日注册用户的后续活跃率）
WITH new_users AS (
  SELECT user_id FROM events
  WHERE event_date = '2024-01-15'
  GROUP BY user_id
)
SELECT
  countIf(d1) / count() AS d1_retention,
  countIf(d7) / count() AS d7_retention,
  countIf(d30) / count() AS d30_retention
FROM (
  SELECT
    n.user_id,
    max(e.event_date = '2024-01-16') AS d1,
    max(e.event_date = '2024-01-22') AS d7,
    max(e.event_date = '2024-02-14') AS d30
  FROM new_users n
  LEFT JOIN events e ON n.user_id = e.user_id
  GROUP BY n.user_id
)
```

## 漏斗分析

```sql
-- 注册 → 实名 → 首次下单 → 复购
SELECT
  countIf(step1) AS register,
  countIf(step1 AND step2) AS verify,
  countIf(step1 AND step2 AND step3) AS first_order,
  countIf(step1 AND step2 AND step3 AND step4) AS repurchase,
  verify / register AS c1,
  first_order / verify AS c2,
  repurchase / first_order AS c3
FROM (
  SELECT
    user_id,
    min(event_date) FILTER (WHERE event_type = 'register') AS reg_date,
    min(event_date) FILTER (WHERE event_type = 'verify') AS verify_date,
    min(event_date) FILTER (WHERE event_type = 'first_order') AS order_date,
    min(event_date) FILTER (WHERE event_type = 'repurchase') AS repurchase_date,
    countIf(event_type = 'register') > 0 AS step1,
    countIf(event_type = 'verify') > 0 AS step2,
    countIf(event_type = 'first_order') > 0 AS step3,
    countIf(event_type = 'repurchase') > 0 AS step4
  FROM events
  WHERE event_date BETWEEN '2024-01-01' AND '2024-01-31'
  GROUP BY user_id
)
```

## 用户路径分析

```sql
-- 用户典型路径（点击流）
WITH user_paths AS (
  SELECT
    user_id,
    session_id,
    groupArray(event_type) AS path
  FROM events
  WHERE event_date = '2024-01-15'
  GROUP BY user_id, session_id
)
SELECT
  arrayStringConcat(arraySlice(path, 1, 5), '→') AS first_5_steps,
  count() AS user_count
FROM user_paths
GROUP BY first_5_steps
ORDER BY user_count DESC
LIMIT 20
```

## 人群画像

```sql
-- 高价值用户（最近 30 天消费 ≥ 1000）
SELECT
  user_id,
  sum(amount) AS total_amount,
  count() AS order_count,
  uniq(page_url) AS visited_pages
FROM events
WHERE event_date >= today() - INTERVAL 30 DAY
  AND event_type = 'purchase'
GROUP BY user_id
HAVING total_amount >= 1000
ORDER BY total_amount DESC
LIMIT 1000
```

## 性能基准

```text
数据量：     100 亿事件
写入吞吐：   50w rows/s
UV 查询：    < 100ms（RoaringBitmap 预聚合）
留存查询：   < 1s（D1-D30 cohort 表）
漏斗查询：   < 500ms
路径查询：   < 2s（限制 path 长度 ≤ 5）
```

## 大厂案例

- **字节跳动**：抖音埋点，单集群数千节点
- **B 站**：用户行为 + 弹幕反垃圾
- **京东**：商品点击 + 订单分析
- **网易**：游戏埋点 + 反作弊
- **头条**：新闻推荐实时数仓

详见 [../case-study.md](../case-study.md)。

## 下一步

- 学习日志分析：见 [log-analysis.md](./log-analysis.md)
- 学习实时数仓：见 [realtime-warehouse.md](./realtime-warehouse.md)


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [es](https://java-px.bot.cd/es/):ES 对比
- [bigdata](https://java-px.bot.cd/bigdata/):大数据生态
- [postgresql](https://java-px.bot.cd/postgresql/):PostgreSQL 对比
