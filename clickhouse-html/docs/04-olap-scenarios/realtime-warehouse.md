---
title: 实时数仓
description: Kafka + MV 链式分层：DWD / DWS / ADS 三层实时数仓完整架构
---

# 实时数仓

实时数仓是 ClickHouse 最强的场景之一，本章展示从 Kafka 到 DWD/DWS/ADS 三层的完整架构。

## 实时数仓 vs 离线数仓

| 维度 | 实时数仓 | 离线数仓 |
|---|---|---|
| **延迟** | 秒级 | T+1（小时/天） |
| **架构** | Kafka + ClickHouse MV | Hive + Spark / Flink |
| **更新** | 增量 | 全量重算 |
| **成本** | 中（CK 集群） | 高（Hive 集群） |
| **灵活性** | 低（强 Schema） | 高（任意 SQL） |
| **典型场景** | 实时看板 / 风控 / 推荐 | 月度报表 / 用户画像 |

## 三层架构

```text
┌──────────┐    Kafka    ┌──────────┐
│ 业务系统 │ ─────────→  │ ODS（原始）│
└──────────┘             └──────────┘
                             │
                             │ MV1: 明细清洗
                             ▼
                        ┌──────────┐
                        │ DWD（明细）│
                        └──────────┘
                             │
                             │ MV2: 主题汇总
                             ▼
                        ┌──────────┐
                        │ DWS（汇总）│
                        └──────────┘
                             │
                             │ MV3: 应用层
                             ▼
                        ┌──────────┐
                        │ ADS（应用）│
                        └──────────┘
                             │
                             ▼
                       Grafana / BI
```

## Schema 设计

### 1. ODS（原始层）

```sql
-- 接 Kafka 写入
CREATE TABLE events_ods (
  event_time DateTime64(3),
  user_id UInt64,
  event_type LowCardinality(String),
  country LowCardinality(String),
  device_type LowCardinality(String),
  page_url String,
  duration_ms UInt32,
  amount Decimal(18, 2),
  properties Map(String, String),
  raw_message String  -- 保留原始数据，便于回溯
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_time)
TTL event_time + INTERVAL 30 DAY  -- 原始数据保留 30 天
```

### 2. DWD（明细层）

```sql
-- 清洗 + 维度补全
CREATE TABLE events_dwd (
  event_time DateTime64(3),
  event_date Date DEFAULT toDate(event_time),
  user_id UInt64,
  user_name String,
  user_country LowCardinality(String),
  user_age UInt8,
  event_type LowCardinality(String),
  page_url String,
  product_id UInt64,
  product_name String,
  product_category LowCardinality(String),
  amount Decimal(18, 2),
  duration_ms UInt32
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (user_id, event_time)

-- 物化视图
CREATE MATERIALIZED VIEW events_dwd_mv TO events_dwd AS
SELECT
  event_time,
  event_time AS event_date,
  user_id,
  dictGet('users_dict', 'user_name', user_id) AS user_name,
  dictGet('users_dict', 'country', user_id) AS user_country,
  dictGet('users_dict', 'age', user_id) AS user_age,
  event_type,
  page_url,
  dictGet('page_dict', 'product_id', page_url) AS product_id,
  dictGet('products_dict', 'product_name', product_id) AS product_name,
  dictGet('products_dict', 'category', product_id) AS product_category,
  amount,
  duration_ms
FROM events_ods
```

### 3. DWS（汇总层）

```sql
-- 每分钟 UV/PV/GMV（按国家 + 事件类型）
CREATE TABLE events_dws_minute (
  event_minute DateTime,
  country LowCardinality(String),
  category LowCardinality(String),
  uv_bitmap AggregateFunction(groupBitmap, UInt64),
  pv_count AggregateFunction(count),
  gmv_sum AggregateFunction(sum, Decimal(18, 2))
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_minute)
ORDER BY (event_minute, country, category)

CREATE MATERIALIZED VIEW events_dws_minute_mv TO events_dws_minute AS
SELECT
  toStartOfMinute(event_time) AS event_minute,
  user_country AS country,
  product_category AS category,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv_count,
  sumState(amount) AS gmv_sum
FROM events_dwd
GROUP BY event_minute, country, category

-- 每小时汇总（DWS-Hour）
CREATE TABLE events_dws_hour (...)

-- 每日汇总（DWS-Day）
CREATE TABLE events_dws_day (...)
```

### 4. ADS（应用层）

```sql
-- 实时看板（最近 1 小时）
CREATE TABLE events_ads_realtime (
  event_minute DateTime,
  country LowCardinality(String),
  category LowCardinality(String),
  uv AggregateFunction(groupBitmap, UInt64),
  pv AggregateFunction(count),
  gmv AggregateFunction(sum, Decimal(18, 2))
)
ENGINE = AggregatingMergeTree()
ORDER BY (event_minute, country, category)

CREATE MATERIALIZED VIEW events_ads_realtime_mv TO events_ads_realtime AS
SELECT
  event_minute,
  country,
  category,
  groupBitmapState(user_id) AS uv,
  countState() AS pv,
  sumState(amount) AS gmv
FROM events_dwd
WHERE event_time >= now() - INTERVAL 1 HOUR
GROUP BY event_minute, country, category

-- 数据回填（每小时跑一次，刷新 ADS）
INSERT INTO events_ads_realtime
SELECT
  event_minute,
  country,
  category,
  uv_bitmap,
  pv_count,
  gmv_sum
FROM events_dws_minute
WHERE event_minute >= now() - INTERVAL 1 HOUR
```

## 监控与告警

### 数据延迟监控

```sql
-- Kafka 消费延迟
SELECT
  database,
  table,
  lag,
  last_poll_time
FROM system.kafka_consumers

-- 物化视图积压
SELECT
  database,
  table,
  parts,
  rows
FROM system.parts
WHERE table LIKE '%_mv%'
```

### 数据质量监控

```sql
-- 字段空值率
SELECT
  event_date,
  countIf(user_id = 0) AS missing_user_id,
  countIf(amount = 0) AS missing_amount,
  count() AS total
FROM events_dwd
WHERE event_date = today()
GROUP BY event_date

-- 异常数据（金额 > 10000）
SELECT countIf(amount > 10000) FROM events_dwd WHERE event_date = today()
```

## 数据回溯与重放

### 历史数据回填

```sql
-- 重新消费 Kafka 历史数据（修改 consumer group）
DETACH TABLE events_ods_kafka
ALTER TABLE events_ods_kafka MODIFY SETTING kafka_group_name = 'replay_2024_01_01'
ATTACH TABLE events_ods_kafka
```

### 重新计算 DWD/DWS

```sql
-- 删除 DWS 表，重新构建
DROP TABLE events_dws_minute
DROP TABLE events_dws_minute_mv

CREATE TABLE events_dws_minute (...)
CREATE MATERIALIZED VIEW events_dws_minute_mv TO events_dws_minute AS
SELECT ... FROM events_dwd

-- 手动回填
INSERT INTO events_dws_minute
SELECT ... FROM events_dwd
```

## 大厂案例

### 字节跳动

- 实时数据量：PB 级
- 数仓分层：ODS + DWD + DWS + ADS
- 物化视图：100+ MV 链式触发
- 应用场景：抖音推荐、广告归因

### 京东

- 订单实时数仓：Kafka → DWD → DWS → 履约看板
- 延迟：秒级
- 数据量：TB/天

### 滴滴

- 行程数据实时分析（与 StarRocks 共存）
- ClickHouse 单表聚合，StarRocks 多表 JOIN

详见 [../case-study.md](../case-study.md) 案例 3、6、9。

## 常见问题

### Q1：MV 链式触发延迟？

通常秒级。监控 `system.parts` 看 parts 数是否持续增长。

### Q2：数据倾斜（热点 key）？

- 单分片过大：用 `SAMPLE 0.01` + 加权聚合
- 单用户过大：拆分（按 hash(user_id) 分多行）

### Q3：MV 修改怎么办？

1. DROP 旧 MV
2. 修改目标表
3. CREATE 新 MV
4. 历史数据手动 INSERT 回填

## 下一步

- 学习 Kafka 集成：见 [05-ecosystem/kafka-integration.md](../05-ecosystem/kafka-integration.md)
- 学习对比选型：见 [06-compare/overview.md](../06-compare/overview.md)
