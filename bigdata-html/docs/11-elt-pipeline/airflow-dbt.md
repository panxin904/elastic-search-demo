---
title: Airflow / dbt
---
# Airflow / dbt

## 1. Airflow 简介

Airflow = 任务编排平台（DAG + 调度 + 监控）。

## 2. 核心概念

DAG（有向无环图）：任务 + 依赖
  - Task A → Task B → Task C
  - 并行 / 串行

## 3. Airflow 实战

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
  'owner': 'data',
  'retries': 3,
  'retry_delay': timedelta(minutes=5),
}

with DAG(
  'etl_daily',
  default_args=default_args,
  start_date=datetime(2024, 1, 1),
  schedule_interval='0 2 * * *',  # 每天 2:00
  catchup=False,
  tags=['etl', 'prod']
) as dag:

  extract = BashOperator(
    task_id='extract',
    bash_command='hive -e "INSERT OVERWRITE TABLE ods.orders PARTITION (dt={{ ds }}) SELECT * FROM mysql_orders"'
  )

  transform = SparkSubmitOperator(
    task_id='transform',
    application='/jobs/etl/dwd_orders.py',
    conf={
      'spark.master': 'yarn',
      'spark.executor.memory': '4g',
      'dt': '{{ ds }}'
    }
  )

  load = BashOperator(
    task_id='load',
    bash_command='hive -e "INSERT OVERWRITE TABLE dws.orders PARTITION (dt={{ ds }}) SELECT * FROM dwd_orders_temp"'
  )

  quality_check = PythonOperator(
    task_id='quality_check',
    python_callable=check_data_quality,
    op_kwargs={'dt': '{{ ds }}'}
  )

  extract >> transform >> load >> quality_check
```

## 4. dbt 简介

dbt = data build tool（SQL + Jinja 转换 + 测试 + 文档）。

```
原始 SQL → dbt model（.sql + Jinja）
  - 自动生成 schema（schema.yml）
  - 自动测试
  - 自动文档
  - 自动 lineage
```

## 5. dbt 实战

```sql
-- models/staging/stg_orders.sql
{{ config(materialized='view') }}

with source as (
  select * from {{ source('raw', 'orders') }}
),

renamed as (
  select
    id as order_id,
    user_id,
    amount,
    order_time,
    date_trunc('day', order_time) as dt
  from source
)

select * from renamed
```

```sql
-- models/marts/fct_orders.sql
{{ config(materialized='incremental') }}

select * from {{ ref('stg_orders') }}
where dt >= '{{ var("start_date") }}'
```

```yaml
# models/staging/schema.yml
version: 2

models:
  - name: stg_orders
    columns:
      - name: order_id
        tests:
          - not_null
          - unique
      - name: user_id
        tests:
          - not_null
      - name: amount
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: ">= 0"
```

## 6. dbt 实战命令

```bash
# 初始化
dbt init my_dbt_project

# 编译（不运行）
dbt compile

# 运行
dbt run --select stg_orders
dbt run --select tag:nightly

# 测试
dbt test
dbt test --select fct_orders

# 文档
dbt docs generate
dbt docs serve

# 血缘
dbt ls --resource-type model
```

## 7. dbt + Airflow 集成

```python
# Airflow 调用 dbt
from airflow.operators.bash import BashOperator

dbt_run = BashOperator(
  task_id='dbt_run',
  bash_command='cd /opt/dbt && dbt run --select fct_orders',
  dag=dag
)
```

## 8. 实战选型

| 场景 | 选 |
|------|-----|
| 复杂 ETL 编排 | Airflow |
| 简单 SQL 转换 | dbt |
| 完整数仓 | Airflow + dbt |
| 轻量级 | Dagster / Prefect |
| 云原生 | Astronomer / Managed Airflow |

## 9. dbt vs Airflow

| | dbt | Airflow |
|--|-----|---------|
| 用途 | SQL 转换 | 任务编排 |
| 输入 | SQL + Jinja | Python / SQL / Bash |
| 输出 | 表 | DAG run |
| 测试 | 内置 | 需自实现 |
| 文档 | 自动 | 需自实现 |
| 适合 | 转换层 | 调度层 |

## 10. 实战案例

### 案例 1：电商数仓

```
Airflow（编排）：
  - extract → transform → load
  - 每天 02:00 跑
  - 重试 + 告警

  ↓ 调用

dbt（转换）：
  - staging/stg_orders.sql
  - marts/fct_orders.sql
  - marts/dim_user.sql
  - 测试 + 血缘 + 文档

  ↓ 写

Lakehouse（Iceberg）：
  bronze.orders / silver.orders / gold.fct_orders
```

### 案例 2：dbt + Snowflake / BigQuery

```yaml
# dbt_project.yml
name: my_project
profile: snowflake

models:
  my_project:
    staging:
      +materialized: view
    marts:
      +materialized: table
      +schema: analytics
```

## 11. 实战 checklist

- [ ] 选 Airflow / Dagster / Prefect
- [ ] 选 dbt（必须）
- [ ] 设计 DAG（任务粒度）
- [ ] 监控（DAG 失败 / 慢任务）
- [ ] 告警（Slack / 邮件）
- [ ] 文档（DAG + dbt 自动）
- [ ] 测试（dbt test + Airflow 集成测试）

## 12. 实战技巧

```
1. 任务粒度适中（不要过细或过粗）
2. 幂等（重新跑结果一致）
3. 重试 + 告警（生产必备）
4. dbt 测试 + Airflow 监控（双保险）
5. 文档（自动 + 手动）
```

## 13. 实战选型决策

```
轻量 → dbt alone（无调度）
中等 → Airflow + dbt
复杂 → Airflow + dbt + Airbyte
云原生 → Astronomer / Dagster Cloud
```

## 14. 实战清单

- [ ] Airflow（自建 / MWAA / Astronomer）
- [ ] dbt（cloud / dbt Core）
- [ ] 任务粒度适中
- [ ] 测试覆盖（dbt test + Airflow 测试）
- [ ] 监控（DAG 失败 / 慢）
- [ ] 文档（自动生成）

## 15. 实战 dbt + Airflow 完整模板

```python
# airflow/dags/etl_daily.py
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

with DAG('etl_daily', start_date=datetime(2024,1,1), schedule='@daily') as dag:
  extract = BashOperator(task_id='extract', bash_command='hive -e "..."')
  dbt = BashOperator(task_id='dbt', bash_command='dbt run --select staging marts')
  test = BashOperator(task_id='test', bash_command='dbt test')
  extract >> dbt >> test
```

## 16. 实战选型对比

| 工具 | 优势 | 适合 |
|------|------|------|
| Airflow | 成熟、社区大 | 通用 |
| Dagster | 现代化、Asset-based | 新项目 |
| Prefect | 云原生、Pythonic | 云优先 |
| dbt | SQL 转换黄金标准 | 数仓 |

## 17. 实战 checklist

- [ ] 选编排（Airflow / Dagster / Prefect）
- [ ] 选 dbt（必备）
- [ ] DAG 设计
- [ ] 任务粒度适中
- [ ] 重试 + 告警
- [ ] 测试（dbt test）
- [ ] 监控
- [ ] 文档

## 18. 实战建议

1. Airflow + dbt 是 90% 公司的标配
2. 简单项目可只用 dbt
3. 复杂项目用 Dagster 替代 Airflow
4. 云优先用 Prefect 或 Managed Airflow
5. 测试和文档不能省

## 19. 实战选型对比

| 组合 | 适合 |
|------|------|
| Airflow + dbt | 传统数仓 |
| Dagster + dbt | 现代新项目 |
| Prefect + dbt | 云原生 |
| dbt 单独 | 轻量级 |

## 20. 实战建议

- Airflow / Dagster 二选一
- dbt 是必备（转换层）
- 测试和文档是底线

## 21. 实战建议

- Airflow / Dagster 选一个就好
- dbt 是 SQL 转换的事实标准
- 测试不能省
- 文档自动生成

## 🔗 下一步
- [CDC 同步](/11-elt-pipeline/cdc)
- [数据血缘](/07-kafka-streaming/lineage)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [kafka](https://java-px.bot.cd/kafka/):Kafka 流处理
- [es](https://java-px.bot.cd/es/):Elasticsearch
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
