---
title: Prometheus remote_write
description: ClickHouse 作为 Prometheus 长期存储：bridge 工具 + 实战
---

# Prometheus remote_write

Prometheus 默认保留 15 天，但很多场景需要更长（合规 / 趋势分析）。ClickHouse 作为远程存储是常见方案。

## 架构

```text
┌──────────┐                       ┌──────────┐
│Prometheus│ ──remote_write──→  │ Bridge   │ ──HTTP INSERT──→ ┌──────────┐
└──────────┘                       └──────────┘                 │ ClickHouse│
                                                              └──────────┘
```

## 方案 1：prometheus-clickhouse-bridge（推荐）

[Altinity 开源](https://github.com/Altinity/prometheus-clickhouse-bridge) 的官方兼容桥接器：

### 安装

```bash
# 二进制下载
wget https://github.com/Altinity/prometheus-clickhouse-bridge/releases/download/v0.7.0/prometheus-clickhouse-bridge-0.7.0-linux-amd64.tar.gz
tar -xzf prometheus-clickhouse-bridge-0.7.0-linux-amd64.tar.gz

# 启动
./prometheus-clickhouse-bridge \
  -clickhouse.dsn="clickhouse://default:@localhost:9000/default" \
  -listen=":9201" \
  -metrics.listen=":9201/metrics" \
  -log.level=info
```

### Prometheus 配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

remote_write:
  - url: 'http://localhost:9201/write'
    queue_config:
      capacity: 10000
      max_samples_per_send: 1000
      batch_send_deadline: 5s

remote_read:
  - url: 'http://localhost:9201/read'

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

### ClickHouse 表

Bridge 会自动建表，也可以手动创建：

```sql
CREATE TABLE prometheus_metrics (
  timestamp DateTime64(3),
  name LowCardinality(String),
  labels Map(LowCardinality(String), String),
  value Float64
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (name, timestamp)
TTL timestamp + INTERVAL 30 DAY
```

## 方案 2：Vector 桥接

```yaml
# vector.toml
sources:
  prom_remote_write:
    type: prometheus_remote_write
    address: 0.0.0.0:9201

transforms:
  parse:
    type: remap
    inputs:
      - prom_remote_write
    source: |
      .timestamp = from_unix_timestamp!(.timestamp, "ms")
      .labels = .labels

sinks:
  clickhouse:
    type: clickhouse
    inputs:
      - parse
    database: default
    table: prometheus_metrics
    endpoint: http://clickhouse-1:8123
    encoding:
      codec: json
```

## 方案 3：直接 HTTP（自研）

```python
# 自研 bridge（适合简单场景）
from http.server import BaseHTTPRequestHandler, HTTPServer
from prometheus_api_client import PrometheusConnect
import clickhouse_connect

class Bridge(BaseHTTPRequestHandler):
    def do_POST(self):
        # 解析 Prometheus remote_write 协议（protobuf）
        # ...
        # 写入 ClickHouse
        client.insert('prometheus_metrics', data)

HTTPServer(('0.0.0.0', 9201), Bridge).serve_forever()
```

## 查询示例

### PromQL → ClickHouse SQL 翻译

#### 1. `rate()` 计算

```sql
-- PromQL: rate(http_requests_total[5m])
SELECT
  toStartOfMinute(timestamp) AS t,
  labels['path'] AS path,
  sum(value) / 60 AS rate
FROM prometheus_metrics
WHERE name = 'http_requests_total'
  AND timestamp >= now() - INTERVAL 5 MINUTE
GROUP BY t, path
ORDER BY t
```

#### 2. histogram_quantile

```sql
-- PromQL: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
WITH bucketed AS (
  SELECT
    toStartOfMinute(timestamp) AS t,
    labels['le'] AS le,
    labels['path'] AS path,
    sum(value) AS cumulative_count
  FROM prometheus_metrics
  WHERE name = 'http_request_duration_seconds_bucket'
    AND timestamp >= now() - INTERVAL 5 MINUTE
  GROUP BY t, le, path
)
SELECT
  t,
  path,
  -- 线性插值计算 P95
  arrayElement(arrayMap(i -> le[i], arrayFilter(i -> le[i] != '+Inf', range(length(le)))), ...)
FROM bucketed
```

实际生产中建议用 Grafana + ClickHouse 的 PromQL 翻译插件，或自研函数。

### 3. 标签组合查询

```sql
-- 按 method + status 聚合
SELECT
  labels['method'] AS method,
  labels['status'] AS status,
  avg(value) AS avg_value,
  count() AS sample_count
FROM prometheus_metrics
WHERE name = 'http_request_duration_seconds'
  AND timestamp >= now() - INTERVAL 1 HOUR
GROUP BY method, status
ORDER BY method, status
```

### 4. 高基数检测

```sql
-- 时间序列数（按 name + labels）
SELECT
  name,
  uniqExact(mapKeys(labels), mapValues(labels)) AS series_count
FROM prometheus_metrics
WHERE timestamp >= now() - INTERVAL 1 HOUR
GROUP BY name
ORDER BY series_count DESC
```

## 物化视图：预聚合

```sql
-- 每 5 分钟指标聚合
CREATE TABLE prometheus_5min_agg (
  event_5min DateTime,
  name LowCardinality(String),
  method LowCardinality(String),
  path LowCardinality(String),
  sum_value AggregateFunction(sum, Float64),
  count_value AggregateFunction(count),
  max_value AggregateFunction(max, Float64)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMMDD(event_5min)
ORDER BY (event_5min, name, method, path)

CREATE MATERIALIZED VIEW prometheus_5min_mv TO prometheus_5min_agg AS
SELECT
  toStartOfFiveMinute(timestamp) AS event_5min,
  name,
  labels['method'] AS method,
  labels['path'] AS path,
  sumState(value) AS sum_value,
  countState() AS count_value,
  maxState(value) AS max_value
FROM prometheus_metrics
GROUP BY event_5min, name, method, path

-- 查询
SELECT
  event_5min,
  name,
  method,
  path,
  sumMerge(sum_value) / sumMerge(count_value) AS avg,
  maxMerge(max_value) AS max
FROM prometheus_5min_agg
WHERE event_5min >= now() - INTERVAL 1 HOUR
GROUP BY event_5min, name, method, path
```

## TTL 与存储管理

```sql
-- 30 天后自动删除
ALTER TABLE prometheus_metrics MODIFY TTL timestamp + INTERVAL 30 DAY

-- 分级存储
ALTER TABLE prometheus_metrics MODIFY TTL
  timestamp + INTERVAL 3 DAY TO VOLUME 'cold',
  timestamp + INTERVAL 30 DAY DELETE

-- 按 name 分级（高频指标保留更久）
ALTER TABLE prometheus_metrics MODIFY TTL
  timestamp + INTERVAL 90 DAY DELETE
  WHERE name LIKE 'business_%'
```

## 实战：Cloudflare 监控

Cloudflare 用 ClickHouse 替代 Prometheus 自研指标系统：

- 写入吞吐：单节点 15w+ rows/s
- 存储：每节点 100+ TB
- 查询：10 亿时间序列 < 5s
- 自研客户端：[ch-go](https://github.com/ClickHouse/ch-go)

详见 [../case-study.md](../case-study.md) 案例 2。

## 大厂实践

- **Cloudflare**：DNS / CDN 监控（替代 Prometheus）
- **Uber**：业务指标 + 服务监控
- **GitHub**：仓库 / PR 指标

## 下一步

- 学习 Go 客户端：见 [go-client.md](./go-client.md)
- 学习 dbt 集成：见 [dbt-airbyte.md](./dbt-airbyte.md)


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
