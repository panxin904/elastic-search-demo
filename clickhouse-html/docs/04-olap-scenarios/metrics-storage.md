---
title: 指标 TSDB 存储
description: 用 ClickHouse 做 Prometheus / Grafana 的后端存储：remote_write / 指标标签 / PromQL
---

# 指标 TSDB 存储

ClickHouse 是 Prometheus 之外的另一个指标存储选择，特别适合**大基数标签 + 长保留周期**场景。

## Prometheus vs ClickHouse

| 维度 | Prometheus | ClickHouse |
|---|---|---|
| **架构** | 本地 TSDB | 分布式列存 |
| **数据保留** | 默认 15 天 | 无限制（按磁盘） |
| **查询** | PromQL（强大） | SQL（更通用） |
| **基数** | < 1000 万时间序列 | 任意（亿级） |
| **集群** | 联邦 / Thanos | 原生分布式 |
| **压缩** | 中（1-2x） | 强（10x+） |
| **告警** | Alertmanager | 自建（Grafana Alerting） |

**结论**：
- 数据量 < 1000 万时间序列 + 短期保留 → Prometheus
- 数据量 > 1000 万时间序列 + 长期保留 → ClickHouse
- 需要 SQL 分析（关联业务数据）→ ClickHouse
- 需要多团队共用 → ClickHouse

## Prometheus remote_write 写入 ClickHouse

### 1. ClickHouse 建表

```sql
CREATE TABLE metrics (
  event_time DateTime64(3),
  name LowCardinality(String),
  labels Map(LowCardinality(String), String),
  value Float64
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (name, event_time)
SETTINGS index_granularity = 8192
```

### 2. ClickHouse 暴露 HTTP 接收端点

ClickHouse v22.x+ 支持原生 Prometheus 协议，但更通用的是用 `prometheus_remote_write` 中间件。

```bash
# 启动 ClickHouse HTTP 服务（默认 8123 端口）
clickhouse-server --config-file=/etc/clickhouse-server/config.xml
```

### 3. Prometheus 配置 remote_write

```yaml
# prometheus.yml
remote_write:
  - url: 'http://clickhouse-bridge:9201/write'
    # ClickHouse 不直接支持 PromWire 协议，需要用 Vector 或 prometheus-clickhouse-bridge
```

### 4. 用 Vector 桥接（推荐）

```yaml
# vector.toml
sources:
  prometheus_remote_write:
    type: prometheus_remote_write
    address: 0.0.0.0:9201

transforms:
  parse:
    type: remap
    inputs:
      - prometheus_remote_write
    source: |
      .event_time = .timestamp
      .name = .name
      .labels = .labels
      .value = .value

sinks:
  clickhouse:
    type: clickhouse
    inputs:
      - parse
    database: default
    table: metrics
    endpoint: http://clickhouse-1:8123
```

### 5. 自研 bridge 服务（高性能）

[prometheus-clickhouse-bridge](https://github.com/Altinity/prometheus-clickhouse-bridge) 提供官方兼容的 PromWire 协议：

```bash
# 启动 bridge
prometheus-clickhouse-bridge \
  -clickhouse.dsn=clickhouse://default:@localhost:9000/default \
  -listen=:9201

# Prometheus 配置
remote_write:
  - url: 'http://localhost:9201/write'
```

## 替代 Prometheus 的存储

Cloudflare 和 Uber 直接用 ClickHouse 替换 Prometheus：

```sql
-- 写入（HTTP API）
INSERT INTO metrics FORMAT JSONEachRow
{"event_time": "2024-01-15 12:00:00.123", "name": "http_requests_total", "labels": {"method": "GET", "status": "200", "path": "/api/users"}, "value": 1234}
```

```python
# 应用端：指标采集
from prometheus_client import Counter, Histogram
import clickhouse_connect

counter = Counter('http_requests_total', 'HTTP requests', ['method', 'status', 'path'])

client = clickhouse_connect.get_client(host='clickhouse-1')

# 定期 flush
def flush_metrics():
    metrics = []
    for metric in counter.collect():
        for sample in metric.samples:
            metrics.append({
                'event_time': datetime.now(),
                'name': sample.name,
                'labels': sample.labels,
                'value': sample.value
            })
    client.insert('metrics', metrics, column_names=['event_time', 'name', 'labels', 'value'])
```

## 常见查询

### 1. 单指标查询（PromQL 风格）

```sql
-- PromQL: rate(http_requests_total[5m])
SELECT
  toStartOfMinute(event_time) AS t,
  labels['method'] AS method,
  labels['status'] AS status,
  sum(value) / 60 AS rps
FROM metrics
WHERE name = 'http_requests_total'
  AND event_time >= now() - INTERVAL 5 MINUTE
GROUP BY t, method, status
ORDER BY t

-- PromQL: histogram_quantile(0.95, ...)
SELECT
  labels['path'] AS path,
  quantile(0.95)(value) AS p95
FROM metrics
WHERE name = 'http_request_duration_seconds_bucket'
  AND event_time >= now() - INTERVAL 5 MINUTE
  AND labels['le'] != '+Inf'
GROUP BY path
```

### 2. 高基数标签查询

```sql
-- 找出基数最高的标签
SELECT
  name,
  uniq(mapKeys(labels)) AS distinct_label_keys,
  uniqExact(mapValues(labels)) AS distinct_label_values
FROM metrics
WHERE event_time >= today()
GROUP BY name
ORDER BY distinct_label_values DESC
LIMIT 10
```

### 3. 多指标关联分析

```sql
-- HTTP QPS × 服务端 CPU 使用率
SELECT
  toStartOfMinute(t1.event_time) AS t,
  t1.rps,
  t2.cpu_usage
FROM (
  SELECT event_time, sum(value) / 60 AS rps
  FROM metrics
  WHERE name = 'http_requests_total' AND event_time >= now() - INTERVAL 1 HOUR
  GROUP BY event_time
) t1
JOIN (
  SELECT event_time, avg(value) AS cpu_usage
  FROM metrics
  WHERE name = 'process_cpu_seconds_total' AND event_time >= now() - INTERVAL 1 HOUR
  GROUP BY event_time
) t2 ON t1.event_time = t2.event_time
```

## 物化视图：预聚合

```sql
-- 每分钟 QPS / P95 / P99
CREATE TABLE metrics_minute_agg (
  event_minute DateTime,
  name LowCardinality(String),
  method LowCardinality(String),
  status LowCardinality(String),
  sum_value AggregateFunction(sum, Float64),
  count_value AggregateFunction(count),
  max_value AggregateFunction(max, Float64)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_minute)
ORDER BY (event_minute, name, method, status)

CREATE MATERIALIZED VIEW metrics_minute_mv TO metrics_minute_agg AS
SELECT
  toStartOfMinute(event_time) AS event_minute,
  name,
  labels['method'] AS method,
  labels['status'] AS status,
  sumState(value) AS sum_value,
  countState() AS count_value,
  maxState(value) AS max_value
FROM metrics
GROUP BY event_minute, name, method, status
```

## TTL 管理

```sql
-- 原始数据保留 7 天
ALTER TABLE metrics MODIFY TTL event_time + INTERVAL 7 DAY

-- 分级存储（7 天后移到冷存储卷）
ALTER TABLE metrics MODIFY TTL event_time + INTERVAL 3 DAY TO VOLUME 'cold',
                       event_time + INTERVAL 30 DAY DELETE
```

## 告警

ClickHouse 本身无原生告警系统，用 Grafana Alerting：

```yaml
# Grafana alert rule
- name: 'HighErrorRate'
  condition: >
    A = avg_over_time(metrics{__name__="http_requests_total"}[5m])
    WHERE labels.status >= "500"
    / avg_over_time(metrics{__name__="http_requests_total"}[5m]) > 0.05
  for: 5m
  to: pagerduty
```

## 实战：Cloudflare 50+ PB 指标

- 自研 `ch-go` 客户端，二进制协议
- 写入吞吐：单节点 15w rows/s
- 存储：每节点 100+ TB SSD
- 查询：10 亿时间序列扫描 < 5s

详见 [../case-study.md](../case-study.md) 案例 2。

## 下一步

- 学习高基数 UV：见 [bitmap.md](./bitmap.md)
- 学习实时数仓：见 [realtime-warehouse.md](./realtime-warehouse.md)
