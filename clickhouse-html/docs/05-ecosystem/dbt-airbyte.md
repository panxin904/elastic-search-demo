---
title: dbt + Airbyte 集成
date: 2026-08-15  # date-auto-injected
description: ETL 编排：dbt-clickhouse 模型转换 + Airbyte CDC 同步
---

# dbt + Airbyte 集成

dbt 和 Airbyte 是 ClickHouse 生态中常用的 ETL 工具，本章给出完整实战。

## dbt-clickhouse

[dbt](https://www.getdbt.com/)（data build tool）是流行的 SQL 转换工具，支持 ClickHouse 通过 [dbt-clickhouse](https://github.com/ClickHouse/dbt-clickhouse)。

### 安装

```bash
pip install dbt-clickhouse
```

### 配置 profiles.yml

```yaml
# ~/.dbt/profiles.yml
my_clickhouse_project:
  target: dev
  outputs:
    dev:
  type: clickhouse
  host: localhost
  port: 8123
  user: default
  password: ''
  database: analytics
  schema: default
  secure: false
```

### 项目结构

```text
my_dbt_project/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── staging/
│   │   ├── stg_events.sql
│   │   ├── stg_orders.sql
│   ├── intermediate/
│   │   ├── int_events_with_user.sql
│   ├── marts/
│   │   ├── daily_active_users.sql
```

### 基础模型

```sql
-- models/staging/stg_events.sql
{{ config(materialized='table') }}

SELECT
  event_time,
  event_date,
  user_id,
  event_type,
  page_url,
  amount,
  duration_ms
FROM {{ source('raw', 'events') }}
WHERE event_time >= '2024-01-01'
```

### 物化视图（dbt-clickhouse 扩展）

```sql
{{ config(materialized='materialized_view') }}

SELECT
  event_date,
  event_type,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv
FROM {{ ref('stg_events') }}
GROUP BY event_date, event_type
```

### 增量模型

```sql
{{ config(
  materialized='incremental',
  incremental_strategy='append',
  partition_by='event_date'
) }}

SELECT *
FROM {{ source('raw', 'events') }}

{% if is_incremental() %}
  WHERE event_time > (SELECT max(event_time) FROM {{ this }})
{% endif %}
```

### AggregateFunction 列

```sql
{{ config(materialized='aggregating_merge_tree') }}

SELECT
  event_date,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv
FROM {{ ref('stg_events') }}
GROUP BY event_date
```

### 字典模型

```sql
{{ config(materialized='dictionary') }}

SELECT
  user_id,
  user_name,
  country
FROM {{ ref('stg_users') }}
```

## Airbyte CDC

[Airbyte](https://airbyte.com/) 是开源的 ELT 平台，提供 300+ 数据连接器，ClickHouse 是官方 Destination。

### ClickHouse Destination 配置

```json
{
  "destination_definition_id": "...",
  "connection": {
    "configuration": {
      "host": "clickhouse-1",
      "port": "8123",
      "database": "analytics",
      "username": "default",
      "password": "",
      "ssl": false,
      "tunnel_method": {
        "tunnel_method": "NO_TUNNEL"
      },
      "JdbcUrlParams": "",
      "maintenance_mode": false
    }
  }
}
```

### MySQL → ClickHouse CDC

1. **Source**：MySQL（开启 binlog）
2. **Destination**：ClickHouse
3. **Replication Method**：Standard + CDC（`Logical Replication (CDC)`）

Airbyte 自动创建目标表：

```sql
CREATE TABLE raw.users (
  id UInt64,
  name String,
  email String,
  created_at DateTime,
  _airbyte_emitted_at DateTime,
  _airbyte_deleted_at Nullable(DateTime)
) ENGINE = MergeTree() ORDER BY id
```

### Postgres → ClickHouse

类似 MySQL CDC，使用 `Logical Replication` 或 `pgoutput`。

### Kafka → ClickHouse

Kafka Source + ClickHouse Destination，Airbyte 自动消费。

## 实战：实时数仓 + dbt + Airbyte

```text
MySQL → Airbyte CDC → ClickHouse ODS
                              │
                              ├── dbt: stg_events.sql（清洗）
                              │
                              ├── dbt: int_events_enriched.sql（维度补全）
                              │
                              ├── dbt: fct_daily_user_metrics.sql（每日指标）
                              │
                              └── 物化视图：实时 UV/PV
```

### dbt_project.yml

```yaml
name: 'analytics'
version: '1.0.0'
profile: 'my_clickhouse_project'

models:
  analytics:
    staging:
      +materialized: view
    intermediate:
      +materialized: table
    marts:
      +materialized: table
```

### models/staging/stg_events.sql

```sql
{{ config(materialized='view') }}

SELECT
  event_time,
  event_date,
  user_id,
  event_type,
  page_url,
  amount,
  duration_ms,
  -- 维度补全
  dictGet('users_dict', 'country', user_id) AS country,
  dictGet('products_dict', 'category', product_id) AS category
FROM {{ source('airbyte', 'events') }}
```

### models/marts/daily_metrics.sql

```sql
{{ config(
  materialized='aggregating_merge_tree',
  partition_by='event_date',
  order_by='(event_date, country, event_type)'
) }}

SELECT
  event_date,
  country,
  event_type,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv,
  sumState(amount) AS gmv
FROM {{ ref('stg_events') }}
GROUP BY event_date, country, event_type
```

### 运行 dbt

```bash
# 调试
dbt run --select stg_events

# 全量
dbt run

# 增量（仅最近）
dbt run --select fct_daily_user_metrics --vars '{"start_date": "2024-01-01"}'

# 测试
dbt test

# 文档
dbt docs generate
dbt docs serve  # http://localhost:8080
```

## 监控与告警

```sql
-- Airbyte 同步延迟
SELECT
  table_name,
  max(_airbyte_emitted_at) AS last_sync
FROM airbyte._airbyte_meta
GROUP BY table_name

-- dbt 模型最近运行时间
SELECT * FROM analytics.dbt_run_results ORDER BY generated_at DESC LIMIT 10
```

## 大厂实践

- **Airbnb**：Airbyte + dbt + ClickHouse 实时数据栈
- **GitHub**：Airbyte CDC + ClickHouse
- **Cloudflare**：自研 + dbt-clickhouse 报表

## 下一步

- 学习 SQL 聚合：见 [02-sql/select-aggregate.md](../02-sql/select-aggregate.md)
- 学习对比选型：见 [06-compare/overview.md](../06-compare/overview.md)


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
