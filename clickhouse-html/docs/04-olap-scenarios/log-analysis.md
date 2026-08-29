---
title: 日志分析
description: Uber / Cloudflare / GitHub 都在用：ClickHouse 替代 Elasticsearch 做日志分析
---

# 日志分析

日志分析是 ClickHouse 第二个主战场。Uber / Cloudflare / GitHub 等大厂用 CK 替代 Elasticsearch，成本降 10x、查询快 10x。

## vs Elasticsearch 对比

| 维度 | ClickHouse | Elasticsearch |
|---|---|---|
| **架构** | 列存 LSM | 倒排索引 |
| **存储成本** | 低（10-20x 压缩） | 高（原始文本） |
| **聚合查询** | 快（10x+） | 中等 |
| **文本搜索** | 中（正则 / 分词） | 极强（原生倒排） |
| **写入吞吐** | 高（100w+ rows/s） | 中（10w+ rows/s） |
| **运维** | 中（Keeper） | 高（Master + Data + Coordinating） |
| **生态** | Grafana / Kafka / dbt | ELK 全家桶 |
| **典型用户** | Uber / Cloudflare / GitHub | 几乎所有互联网公司 |

**结论**：聚合 / 统计为主 → ClickHouse；全文搜索为主 → Elasticsearch；两者共存也很常见。

## 完整架构

```text
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ App/Service│ → │ Vector / │ → │ Kafka    │ → │ CK Kafka  │
│            │   │ Fluent Bit│   │          │   │ Engine   │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
                                                       │
                                                       ▼
                                                ┌──────────┐
                                                │ MergeTree│
                                                │ logs     │
                                                └──────────┘
                                                       │
                                                       ▼
                                                  Grafana
                                                  BI Tools
```

## Schema 设计

### Nginx 访问日志

```sql
CREATE TABLE nginx_logs (
  event_time DateTime,
  event_date Date DEFAULT toDate(event_time),
  remote_addr IPv4,
  remote_user String,
  method LowCardinality(String),       -- GET / POST / PUT
  path String,
  http_version LowCardinality(String),
  status_code UInt16,
  body_bytes_sent UInt64,
  referer String,
  user_agent String,
  -- 解析字段
  browser LowCardinality(String),
  os LowCardinality(String),
  device_type LowCardinality(String),
  country LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (event_time, status_code)
```

### 应用日志

```sql
CREATE TABLE app_logs (
  event_time DateTime64(3),
  event_date Date DEFAULT toDate(event_time),
  service LowCardinality(String),
  level LowCardinality(String),         -- INFO / WARN / ERROR
  trace_id String,
  message String,
  -- 结构化字段
  user_id UInt64,
  request_id String,
  duration_ms UInt32,
  error_code String,
  stack_trace String
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (service, level, event_time)
```

### 系统日志（syslog / kubelet）

```sql
CREATE TABLE syslog (
  event_time DateTime,
  hostname LowCardinality(String),
  process LowCardinality(String),
  severity UInt8,
  message String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (hostname, event_time)
```

## 数据接入

### Nginx 日志格式

```nginx
log_format json escape=json '{'
  '"time": "$time_iso8601",'
  '"remote_addr": "$remote_addr",'
  '"method": "$request_method",'
  '"path": "$request_uri",'
  '"status": $status,'
  '"body_bytes_sent": $body_bytes_sent,'
  '"referer": "$http_referer",'
  '"user_agent": "$http_user_agent",'
  '"duration": "$request_time"'
'}';
```

### Vector 收集 + 解析

```yaml
# vector.toml
sources:
  nginx:
    type: file
    include:
      - /var/log/nginx/access.log

transforms:
  parse_nginx:
    type: remap
    inputs:
      - nginx
    source: |
      .event_time = parse_timestamp!(.timestamp, format: "%Y-%m-%dT%H:%M:%S%.f")
      .browser = parse_user_agent!(.user_agent).browser
      .os = parse_user_agent!(.user_agent).os
      .country = parse_regex!(.remote_addr, r'^(?P<ip>\d+\.\d+\.\d+\.\d+)$') ? .ip : "unknown"

sinks:
  kafka:
    type: kafka
    inputs:
      - parse_nginx
    brokers:
      - kafka-1:9092
    topic: nginx_logs
    encoding:
      codec: json
```

### ClickHouse Kafka 表

```sql
CREATE TABLE nginx_logs_kafka (...)
ENGINE = Kafka()
SETTINGS
  kafka_broker_list = 'kafka-1:9092',
  kafka_topic_list = 'nginx_logs',
  kafka_group_name = 'ch_nginx_consumer',
  kafka_format = 'JSONEachRow'

CREATE MATERIALIZED VIEW nginx_logs_mv TO nginx_logs AS
SELECT ... FROM nginx_logs_kafka
```

## 常见查询

### 1. 错误率统计（按接口）

```sql
SELECT
  path,
  countIf(status_code >= 500) AS errors,
  count() AS total,
  countIf(status_code >= 500) / count() AS error_rate,
  quantile(0.95)(duration_ms) AS p95_latency
FROM app_logs
WHERE event_date = today()
GROUP BY path
HAVING error_rate > 0.01
ORDER BY error_rate DESC
```

### 2. Top 慢接口

```sql
SELECT
  path,
  count() AS req_count,
  avg(duration_ms) AS avg_latency,
  quantile(0.5)(duration_ms) AS p50,
  quantile(0.95)(duration_ms) AS p95,
  quantile(0.99)(duration_ms) AS p99
FROM app_logs
WHERE event_date >= today() - INTERVAL 7 DAY
  AND duration_ms > 0
GROUP BY path
ORDER BY p99 DESC
LIMIT 20
```

### 3. 异常 IP / User Agent

```sql
-- 高频访问 IP（潜在爬虫）
SELECT
  remote_addr,
  count() AS req_count,
  uniq(path) AS unique_paths
FROM nginx_logs
WHERE event_date = today()
GROUP BY remote_addr
HAVING req_count > 10000
ORDER BY req_count DESC
LIMIT 100

-- User-Agent 分布
SELECT
  user_agent,
  count() AS count
FROM nginx_logs
WHERE event_date = today()
GROUP BY user_agent
ORDER BY count DESC
LIMIT 20
```

### 4. 链路追踪（trace_id）

```sql
-- 单次请求全链路
SELECT
  event_time,
  service,
  level,
  message,
  duration_ms
FROM app_logs
WHERE trace_id = 'abc-123-def-456'
ORDER BY event_time
```

### 5. 错误堆栈聚类

```sql
-- 相似错误聚合（按 stack_trace 前 200 字符）
SELECT
  substring(stack_trace, 1, 200) AS error_signature,
  count() AS error_count,
  uniq(trace_id) AS affected_traces,
  max(event_time) AS last_seen
FROM app_logs
WHERE event_date = today()
  AND level = 'ERROR'
  AND stack_trace != ''
GROUP BY error_signature
ORDER BY error_count DESC
LIMIT 20
```

## TTL 与存储优化

```sql
-- 30 天后自动删除
ALTER TABLE nginx_logs MODIFY TTL event_date + INTERVAL 30 DAY

-- 多级 TTL（30 天后降级到冷存储）
ALTER TABLE nginx_logs MODIFY TTL event_date + INTERVAL 7 DAY,
  event_date + INTERVAL 30 DAY TO VOLUME 'cold'

-- 按列 TTL（详细字段 7 天后删除）
ALTER TABLE nginx_logs MODIFY COLUMN stack_trace TTL event_date + INTERVAL 7 DAY
```

## Grafana 集成

```yaml
# Grafana 数据源
type: clickhouse
url: http://clickhouse-1:8123
database: default
username: default
```

常用面板：
- 请求量时间线：`SELECT count() FROM nginx_logs GROUP BY toStartOfMinute(event_time)`
- 错误率：`countIf(status >= 500) / count()`
- P95 / P99：`quantile(0.95)(duration_ms)`
- Top 接口：`SELECT path, count() ... GROUP BY path ORDER BY count DESC LIMIT 10`

## 大厂案例

### Uber

- 日志接入：Fluent Bit → Kafka → CK
- 替代 ES：成本降低 90%
- 自研 LogGlass UI（Grafana 包装）

### Cloudflare

- DNS 日志：50+ PB
- 自研 ch-go 客户端（Go 二进制）
- 实时告警：error_rate > 5% → 触发

### GitHub

- 2019-2020 迁移：ES → CK
- 数据完整性迁移：`clickhouse-migrator` 工具

## 下一步

- 学习指标 TSDB：见 [metrics-storage.md](./metrics-storage.md)
- 学习高基数 UV：见 [bitmap.md](./bitmap.md)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [es](https://java-px.bot.cd/es/):ES 对比
- [bigdata](https://java-px.bot.cd/bigdata/):大数据生态
- [postgresql](https://java-px.bot.cd/postgresql/):PostgreSQL 对比
