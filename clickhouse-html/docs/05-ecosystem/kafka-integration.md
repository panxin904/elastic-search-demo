---
title: Kafka 集成实战
date: 2026-08-15  # date-auto-injected
description: ClickHouse Kafka 表引擎 + MaterializedView 完整实战 + 多 topic 流
---

# Kafka 集成实战

Kafka 是 ClickHouse 最常见的数据源，本章给出生产级完整实战。

## 完整架构

```text
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 业务系统 │ →  │ Kafka    │ →  │ CK Kafka │ →  │ CK MergeTree│
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                      │
                                       ┌──────────────┼──────────────┐
                                       ▼              ▼              ▼
                                  MV: 实时 UV   MV: 留存      MV: 漏斗
```

## 单 Topic 消费

### Step 1：Kafka 表

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
  kafka_topic_list = 'user_events',
  kafka_group_name = 'clickhouse_events_consumer',
  kafka_format = 'JSONEachRow',
  kafka_num_consumers = 1,
  kafka_max_block_size = 1000,
  kafka_poll_timeout_ms = 1000,
  kafka_flush_interval_ms = 1000
```

### Step 2：本地表

```sql
CREATE TABLE events_local (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  payload String,
  event_date Date DEFAULT toDate(event_time)
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (user_id, event_time)
```

### Step 3：物化视图

```sql
CREATE MATERIALIZED VIEW events_mv TO events_local AS
SELECT
  event_time,
  user_id,
  event_type,
  payload
FROM events_kafka
```

**完成！现在 Kafka 数据自动写入 `events_local`。**

## 多 Topic 消费（共享 Schema）

```sql
-- 一个 Kafka 表消费多个 topic
CREATE TABLE events_multi_kafka (
  event_time DateTime,
  user_id UInt64,
  event_type LowCardinality(String),
  source_topic LowCardinality(String),  -- 标记 topic 来源
  payload String
)
ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-1:9092',
  kafka_topic_list = 'events_a,events_b,events_c',
  kafka_group_name = 'multi_topic_consumer',
  kafka_format = 'JSONEachRow'

-- 在物化视图中分流
CREATE MATERIALIZED VIEW events_a_mv TO events_a_local AS
SELECT * FROM events_multi_kafka WHERE source_topic = 'events_a'

CREATE MATERIALIZED VIEW events_b_mv TO events_b_local AS
SELECT * FROM events_multi_kafka WHERE source_topic = 'events_b'
```

## 多 Topic 流式处理

```sql
-- 一个 topic 写入多个表（按 event_type 分流）
CREATE MATERIALIZED VIEW page_view_mv TO page_views_local AS
SELECT event_time, user_id, page_url FROM events_kafka
WHERE event_type = 'page_view'

CREATE MATERIALIZED VIEW click_mv TO clicks_local AS
SELECT event_time, user_id, page_url, click_target FROM events_kafka
WHERE event_type = 'click'

CREATE MATERIALIZED VIEW purchase_mv TO purchases_local AS
SELECT event_time, user_id, product_id, amount FROM events_kafka
WHERE event_type = 'purchase'
```

## Avro / Protobuf

### Avro（Confluent Schema Registry）

```sql
CREATE TABLE events_avro_kafka (...)
ENGINE = Kafka()
SETTINGS
  kafka_format = 'AvroConfluent',
  kafka_schema_registry_url = 'http://schema-registry:8081'
```

### Protobuf

```sql
CREATE TABLE events_proto_kafka (...)
ENGINE = Kafka()
SETTINGS
  kafka_format = 'Protobuf',
  format_protobuf_schema_path = '/etc/clickhouse-protobuf/schema.proto',
  format_protobuf_message_name = 'Event'
```

```protobuf
// schema.proto
syntax = "proto3";
message Event {
  int64 user_id = 1;
  string event_type = 2;
  int64 timestamp = 3;
  map<string, string> properties = 4;
}
```

## 容错处理

### 错误数据处理

```sql
SETTINGS
  kafka_handle_error_mode = 'stream'  -- 错误数据进入虚拟列
```

错误数据在物化视图中自动生成：

```sql
SELECT
  _error,
  _raw_message
FROM events_kafka
WHERE _error != ''
```

### 重置 Offset

```sql
-- 方法 1：修改 consumer group
DETACH TABLE events_kafka
ALTER TABLE events_kafka MODIFY SETTING kafka_group_name = 'new_group'
ATTACH TABLE events_kafka

-- 方法 2：直接修改 Kafka topic 的 offset（用 kafka-consumer-groups.sh）
kafka-consumer-groups.sh --bootstrap-server kafka-1:9092 \
  --group clickhouse_events_consumer \
  --reset-offsets --to-earliest \
  --topic user_events --execute
```

### 监控消费进度

```sql
SELECT
  database,
  table,
  consumer_id,
  last_poll_time,
  last_commit_time,
  num_messages_read
FROM system.kafka_consumers
```

## 实战：实时用户行为流

### 应用层埋点

```python
# 应用端：写入 Kafka
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['kafka-1:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

producer.send('user_events', value={
    'event_time': '2024-01-15 12:00:00',
    'user_id': 12345,
    'event_type': 'click',
    'page_url': '/api/users',
    'duration_ms': 150
})
```

### ClickHouse 端消费 + 实时看板

```sql
-- Kafka 表
CREATE TABLE user_behavior_kafka (...)
ENGINE = Kafka() ...

-- 本地表
CREATE TABLE user_behavior_local (...)
ENGINE = MergeTree() ...

-- 物化视图
CREATE MATERIALIZED VIEW user_behavior_mv TO user_behavior_local AS ...

-- 实时看板（每 5 分钟 UV/PV）
CREATE MATERIALIZED VIEW user_behavior_5min_mv
ENGINE = AggregatingMergeTree()
ORDER BY (event_5min, country)
AS
SELECT
  toStartOfFiveMinute(event_time) AS event_5min,
  dictGet('users_dict', 'country', user_id) AS country,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv
FROM user_behavior_kafka
GROUP BY event_5min, country

-- 查询
SELECT
  event_5min,
  country,
  bitmapCardinality(merge(uv_bitmap)) AS uv,
  sumMerge(pv) AS pv
FROM user_behavior_5min
WHERE event_5min >= now() - INTERVAL 1 HOUR
GROUP BY event_5min, country
ORDER BY event_5min, country
```

## 高级特性

### 消费事务支持

```sql
SETTINGS
  kafka_transactional_id = 'tx-1'
```

### 压缩传输

```sql
SETTINGS
  kafka_format = 'JSONEachRow',
  kafka_compression_method = 'lz4'
```

### 安全认证（SASL/SSL）

```sql
SETTINGS
  kafka_broker_list = 'kafka-1:9092',
  kafka_security_protocol = 'sasl_ssl',
  kafka_sasl_mechanism = 'PLAIN',
  kafka_sasl_username = 'readonly',
  kafka_sasl_password = 'xxx',
  kafka_ssl_ca_cert_file = '/etc/ssl/ca-cert.pem'
```

## 下一步

- 学习 Grafana 集成：见 [grafana.md](./grafana.md)
- 学习 Prometheus 集成：见 [prometheus.md](./prometheus.md)


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
