---
title: Kafka 表引擎
description: 直接消费 Kafka topic，配合物化视图实现秒级实时数仓
---

# Kafka 表引擎

Kafka 引擎是 ClickHouse 实时数仓的核心，让你无需 Kafka Consumer 客户端，直接消费 topic。

## 基础用法

### 1. 创建 Kafka 表（消费者）

```sql
CREATE TABLE events_kafka (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  payload String
)
ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-1:9092,kafka-2:9092',
  kafka_topic_list = 'events',
  kafka_group_name = 'clickhouse_consumer_1',
  kafka_format = 'JSONEachRow',
  kafka_num_consumers = 1
```

**关键参数**：

| 参数 | 说明 |
|---|---|
| `kafka_broker_list` | Kafka broker（逗号分隔） |
| `kafka_topic_list` | topic 列表（逗号分隔） |
| `kafka_group_name` | 消费组（务必唯一） |
| `kafka_format` | 数据格式（JSONEachRow / CSV / Avro 等） |
| `kafka_num_consumers` | 消费者数量（建议 = broker 数） |

### 2. 创建本地表（实际存储）

```sql
CREATE TABLE events_local (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  payload String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (user_id, event_time)
```

### 3. 创建物化视图（自动消费）

```sql
CREATE MATERIALIZED VIEW events_mv TO events_local AS
SELECT
  event_time,
  user_id,
  event_type,
  payload
FROM events_kafka
```

**完成！现在 Kafka 中的数据会自动写入 `events_local`。**

## 多 topic 消费

```sql
CREATE TABLE events_kafka_multi (
  event_time DateTime,
  user_id UInt64,
  event_type String,
  source LowCardinality(String)  -- 标记来自哪个 topic
)
ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-1:9092',
  kafka_topic_list = 'events_a,events_b,events_c',
  kafka_group_name = 'multi_topic_consumer',
  kafka_format = 'JSONEachRow'

CREATE MATERIALIZED VIEW events_multi_mv TO events_local AS
SELECT
  event_time,
  user_id,
  event_type,
  source
FROM events_kafka_multi
```

## Avro / Protobuf 格式

```sql
-- Avro（Confluent Schema Registry）
CREATE TABLE events_avro (...)
ENGINE = Kafka()
SETTINGS
  kafka_format = 'AvroConfluent',
  kafka_schema_registry_url = 'http://schema-registry:8081'

-- Protobuf
CREATE TABLE events_proto (...)
ENGINE = Kafka()
SETTINGS
  kafka_format = 'Protobuf',
  format_protobuf_schema_path = '/path/to/schema.proto',
  format_protobuf_message_name = 'Event'
```

## 容错与监控

### 监控消费进度

```sql
-- 查看 Kafka 引擎表
SELECT * FROM system.tables WHERE engine = 'Kafka'

-- 查看 Kafka consumer 状态
SELECT * FROM system.kafka_consumers FORMAT Vertical
```

### 死信队列（DLQ）

ClickHouse Kafka 引擎**没有原生 DLQ**，但可以通过 `kafka_handle_error_mode` 处理错误：

```sql
SETTINGS
  kafka_format = 'JSONEachRow',
  kafka_handle_error_mode = 'stream'  -- 错误数据进入虚拟列 _error / _raw_message
```

### 重置 offset

```sql
-- 暂停消费
DETACH TABLE events_kafka

-- 修改 group_name（重置 offset）
ALTER TABLE events_kafka MODIFY SETTING kafka_group_name = 'new_group'

-- 重新启动
ATTACH TABLE events_kafka
```

## 实战：实时用户行为日志

```sql
-- Kafka 表
CREATE TABLE user_behavior_kafka (
  user_id UInt64,
  event_time DateTime,
  event_type LowCardinality(String),
  page_url String,
  duration_ms UInt32,
  properties Map(String, String)
)
ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-broker:9092',
  kafka_topic_list = 'user_behavior',
  kafka_group_name = 'ch_user_behavior_consumer',
  kafka_format = 'JSONEachRow',
  kafka_num_consumers = 3,
  kafka_row_delimiter = '\n'

-- 本地表
CREATE TABLE user_behavior_local (
  user_id UInt64,
  event_time DateTime,
  event_type LowCardinality(String),
  page_url String,
  duration_ms UInt32,
  properties Map(String, String),
  event_date Date DEFAULT toDate(event_time)
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (user_id, event_time)

-- 物化视图
CREATE MATERIALIZED VIEW user_behavior_mv TO user_behavior_local AS
SELECT
  user_id,
  event_time,
  event_type,
  page_url,
  duration_ms,
  properties,
  toDate(event_time) AS event_date
FROM user_behavior_kafka

-- 实时看板查询（最近 1 小时）
SELECT
  toStartOfFiveMinute(event_time) AS t,
  uniq(user_id) AS uv,
  count() AS pv,
  avg(duration_ms) AS avg_duration
FROM user_behavior_local
WHERE event_time >= now() - INTERVAL 1 HOUR
GROUP BY t
ORDER BY t
```

## 实战：Kafka → MV → 多表分流

```sql
-- 一个 Kafka topic 写入多个本地表（按 event_type 分流）
CREATE MATERIALIZED VIEW page_view_mv TO page_views_local AS
SELECT * FROM events_kafka WHERE event_type = 'page_view'

CREATE MATERIALIZED VIEW click_mv TO clicks_local AS
SELECT * FROM events_kafka WHERE event_type = 'click'

CREATE MATERIALIZED VIEW purchase_mv TO purchases_local AS
SELECT * FROM events_kafka WHERE event_type = 'purchase'
```

## 高级：Kafka 事务支持

ClickHouse v23.x 支持 Kafka 事务：

```sql
SETTINGS
  kafka_format = 'JSONEachRow',
  kafka_transactional_id = 'tx-1'
```

## 与传统 Kafka Consumer 对比

| 维度 | ClickHouse Kafka 引擎 | Kafka Consumer + SDK |
|---|---|---|
| **部署复杂度** | 一行 SQL | 客户端 + Offset 管理 |
| **Exactly-Once** | 弱（异步） | 强（事务） |
| **吞吐** | 高（10w+ rows/s） | 取决于客户端 |
| **背压** | 自动（合并慢时滞后） | 手动管理 |
| **监控** | `system.kafka_consumers` | 自建 |
| **多表写入** | 一个 topic → 多 MV | 手动 partition 分配 |

## 下一步

- 学习 Distributed 表：见 [distributed.md](./distributed.md)
- 学习物化视图：见 [materialized-view.md](./materialized-view.md)
