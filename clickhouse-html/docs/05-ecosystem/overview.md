---
title: 生态工具链
---

# ClickHouse 生态工具链

**ClickHouse 不是孤岛**——与 Kafka / Grafana / Prometheus / Go / Python / dbt / Airbyte 深度集成。

## 一句话总结

> **ClickHouse 生态 = Kafka 引擎 + Grafana 可视化 + Prometheus remote_write + 多语言客户端 + dbt / Airbyte 集成**。**整个现代数据栈的中枢**。

---

## 一、生态全景

```
┌──────────┐     ┌──────────┐     ┌────────────┐
│  Kafka   │────▶│          │     │            │
└──────────┘     │          │     │  Grafana   │
┌──────────┐     │          │────▶│  Superset  │
│  MySQL   │────▶│ ClickHou │     │  Tabix     │
└──────────┘     │   se     │     │  Metabase  │
┌──────────┐     │          │     └────────────┘
│  PG      │────▶│          │
└──────────┘     │          │     ┌────────────┐
┌──────────┐     │          │     │  BI/Ad-hoc │
│  S3/HDFS │────▶│          │────▶│  DBeaver   │
└──────────┘     └──────────┘     │  DataGrip  │
                                 └────────────┘
┌──────────┐     ┌──────────┐
│Prometheus│────▶│ remote_  │
│ /Grafana │     │  write   │
└──────────┘     └──────────┘
```

## 二、Kafka 实时集成

### Kafka 引擎

```sql
-- 1. 创建 Kafka 表
CREATE TABLE kafka_users (
    id UInt64,
    name String,
    age UInt8,
    ts DateTime
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'kafka1:9092,kafka2:9092',
    kafka_topic_list = 'user_events',
    kafka_group_name = 'clickhouse_consumer',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 1,
    kafka_max_block_size = 65536;

-- 2. 创建本地存储表
CREATE TABLE users (
    id UInt64,
    name String,
    age UInt8,
    ts DateTime
) ENGINE = MergeTree()
ORDER BY id;

-- 3. 物化视图自动消费
CREATE MATERIALIZED VIEW kafka_to_users TO users AS
SELECT id, name, age, ts
FROM kafka_users;

-- 4. 也可以用 Kafka 表作为 INSERT 目标
INSERT INTO kafka_users SELECT id, name, age, now()
FROM users
WHERE age >= 18;
```

**Kafka 表格式支持**：
- `JSONEachRow`（最常用）
- `CSV`
- `Protobuf`
- `Avro`（需 schema registry）
- `Parquet`
- `Raw`（二进制）

### MaterializedPostgreSQL（PG → CH 实时同步）

```sql
-- 1. 创建 PG 同步表
CREATE TABLE users_pg_sync (
    id UInt64,
    name String,
    age UInt8
) ENGINE = MaterializedPostgreSQL(
    'postgres-host:5432', 'mydb', 'users', 'postgres', 'password'
)
PRIMARY KEY id;

-- 2. 自动同步
-- 后续 PG 上 INSERT/UPDATE/DELETE → ClickHouse 自动同步
```

## 三、Grafana 可视化

### Grafana ClickHouse 数据源

```bash
# Grafana 9.0+ 内置 ClickHouse 数据源
# 配置：URL = http://clickhouse:8123, User = default
```

**Grafana Dashboard 示例**：

```json
{
  "panels": [
    {
      "title": "DAU 趋势",
      "targets": [{
        "query": "SELECT\n  toDate(event_time) AS time,\n  uniqExact(user_id) AS dau\nFROM events\nWHERE event_time >= $__fromTime AND event_time <= $__toTime\nGROUP BY time\nORDER BY time"
      }],
      "type": "timeseries"
    },
    {
      "title": "GMV 趋势",
      "targets": [{
        "query": "SELECT\n  toStartOfHour(created_at) AS time,\n  sum(amount) AS gmv\nFROM orders\nWHERE created_at >= $__fromTime AND created_at <= $__toTime\n  AND status = 'paid'\nGROUP BY time"
      }],
      "type": "timeseries"
    }
  ]
}
```

**内置宏**：
- `$__fromTime` / `$__toTime`：时间范围
- `$__timeInterval(column)`：自动聚合
- `$__dateFilter(column)`：日期过滤

## 四、Prometheus remote_write

**目标**：用 ClickHouse 替代 Prometheus TSDB（10x 存储节省）。

**ClickHouse 端配置**：

```sql
-- 1. 启用 Prometheus 协议端点（默认开启）
-- /api/v1/prom/write 接收
-- /api/v1/prom/read 查询
-- /api/v1/prom/query 查询

-- 2. 创建 metrics 表
CREATE TABLE prometheus_metrics (
    -- Prometheus 协议字段
    timestamp DateTime64(3),
    value Float64,
    labels Map(LowCardinality(String), String),
    name LowCardinality(String)
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (name, timestamp)
TTL timestamp + INTERVAL 90 DAY;
```

**Prometheus 配置**：

```yaml
# prometheus.yml
remote_write:
  - url: http://clickhouse:8123/api/v1/prom/write
    basic_auth:
      username: default
      password: ''
    write_relabel_configs:
      - source_labels: [__name__]
        regex: 'go_.*|process_.*'
        action: keep

remote_read:
  - url: http://clickhouse:8123/api/v1/prom/read
    read_recent: true
```

**查询**：

```bash
# Prometheus 风格
curl -G http://clickhouse:8123/api/v1/prom/query \
  --data-urlencode 'query=rate(http_requests_total[5m])' \
  --data-urlencode 'time=2026-08-11T12:00:00Z'
```

**优势**：
- 存储节省 5-10x
- 长保留（90 天+）
- SQL 查询（不限于 PromQL）
- 远端存储

**案例**：
- Cloudflare：ClickHouse 存网络指标
- Uber：业务指标从 Prometheus 迁到 ClickHouse

## 五、Go 客户端

### ch-go（官方推荐）

```go
import (
    "context"
    "fmt"
    "github.com/ClickHouse/ch-go"
    "github.com/ClickHouse/ch-go/proto"
)

func main() {
    // 1. 连接
    conn, err := ch.Dial(context.Background(), ch.Options{
        Address: "clickhouse:9000",
        Database: "default",
        User:     "default",
        Password: "",
    })
    if err != nil { panic(err) }
    defer conn.Close()
    
    // 2. 简单查询
    var result struct {
        Count uint64
    }
    err = conn.Query(context.Background(), "SELECT count() FROM events").
        Scan(&result)
    fmt.Println("count:", result.Count)
    
    // 3. 流式查询
    err = conn.Select(context.Background(), ch.Query{
        Body: "SELECT user_id, event_type, ts FROM events LIMIT 100",
    }, func(row proto.Row) {
        var userID uint64
        var eventType string
        var ts time.Time
        row.Scan(&userID, &eventType, &ts)
        fmt.Println(userID, eventType, ts)
    })
    
    // 4. 批量插入
    var input proto.Input
    err = conn.Insert(context.Background(), ch.Query{
        Body: "INSERT INTO events (user_id, event_type, ts)",
        Input: input,
    })
}
```

### go-clickhouse（clickhouse-go v2）

```go
import (
    "context"
    "github.com/ClickHouse/clickhouse-go/v2"
    "github.com/ClickHouse/clickhouse-go/v2/lib/driver"
)

func main() {
    conn, err := clickhouse.Open(&clickhouse.Options{
        Addr: []string{"clickhouse:9000"},
        Auth: clickhouse.Auth{
            Database: "default",
            Username: "default",
            Password: "",
        },
    })
    
    // 批量插入
    batch, _ := conn.PrepareBatch(context.Background(), "INSERT INTO events")
    for i := 0; i < 1000; i++ {
        batch.Append(uint64(i), "click", time.Now())
    }
    batch.Send()
}
```

**库选择**：
- **ch-go**（官方）：底层 + 高性能 + 无反射
- **clickhouse-go**（v2）：高级 + 易用 + 反射

## 六、Python 客户端

```python
import clickhouse_connect

# 1. 连接
client = clickhouse_connect.get_client(
    host='clickhouse',
    port=8123,
    username='default',
    password='',
    database='default'
)

# 2. 查询
result = client.query('SELECT user_id, count() FROM events GROUP BY user_id LIMIT 10')
for row in result.result_rows:
    print(row)

# 3. 插入
data = [
    [1, 'click', '2026-08-11 12:00:00'],
    [2, 'view', '2026-08-11 12:00:01'],
]
client.insert('events', data, column_names=['user_id', 'event_type', 'ts'])

# 4. 异步
import asyncio
async def main():
    client = clickhouse_connect.get_client(host='clickhouse', port=8123, async_mode=True)
    await client.query('SELECT 1')
asyncio.run(main())
```

**库**：
- `clickhouse-connect`（官方推荐）：HTTP 协议，最常用
- `clickhouse-driver`：原生 TCP 协议，更快
- `sqlalchemy-clickhouse`：ORM 集成
- `pandas` / `polars`：DataFrame 互转

## 七、dbt + Airbyte 集成

### dbt-clickhouse

```yaml
# dbt_project.yml
models:
  my_project:
    +materialized: view  # ClickHouse 支持 view / table / incremental

# schema.yml
models:
  - name: daily_users
    description: "每日活跃用户"
    columns:
      - name: date
        tests:
          - not_null
```

```sql
-- daily_users.sql
{{ config(materialized='incremental', unique_key='date') }}

SELECT
    toDate(event_time) AS date,
    uniqExact(user_id) AS dau
FROM {{ ref('events') }}
{% if is_incremental() %}
WHERE event_time >= now() - INTERVAL 1 DAY
{% endif %}
GROUP BY date
```

### Airbyte

**Source / Destination**：
- Source：MySQL / PG / MongoDB / S3 / Kafka
- Destination：ClickHouse（airbyte/destination-clickhouse）

**典型架构**：
```
MySQL → Airbyte → ClickHouse（数据仓库）
PG → Airbyte → ClickHouse
S3 → Airbyte → ClickHouse
```

## 八、监控 ClickHouse 自身

```sql
-- 1. 慢查询
SELECT
    query_id,
    query_kind,
    query_duration_ms,
    query,
    user,
    type
FROM system.query_log
WHERE query_duration_ms > 1000
  AND event_time >= now() - INTERVAL 1 HOUR
ORDER BY query_duration_ms DESC
LIMIT 50;

-- 2. 当前运行的查询
SELECT
    query_id,
    elapsed,
    query,
    user,
    memory_usage
FROM system.processes
ORDER BY elapsed DESC;

-- 3. 集群状态
SELECT
    cluster,
    shard_num,
    host_name,
    port
FROM system.clusters;

-- 4. 副本状态
SELECT
    database,
    table,
    replica_name,
    is_readonly,
    absolute_delay,
    queue_size
FROM system.replicas;
```

## 九、其他工具

| 工具 | 用途 |
|---|---|
| **Tabix** | ClickHouse 官方 Web UI |
| **DBeaver** | 通用 SQL 客户端 |
| **DataGrip** | JetBrains SQL 客户端 |
| **Metabase** | 自助 BI |
| **Superset** | Apache 自助 BI |
| **Vector** | 数据管道（替换 Logstash） |
| **Vector.dev** | ClickHouse sink |
| **Altinity Operator** | K8s Operator |
| **clickhouse-backup** | 备份工具 |
| **clickhouse-copier** | 数据迁移 |

## 关联章节

- **04-olap-scenarios/overview**：OLAP 场景
- **05-ecosystem/kafka-integration**：Kafka 深入
- **05-ecosystem/prometheus**：Prometheus 集成
- **05-ecosystem/case-study**：真实案例

## 一句话总结

> **ClickHouse 生态 = Kafka + Grafana + Prometheus + 多语言客户端 + dbt/Airbyte**。**整个现代数据栈的中枢**。


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

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
