---
title: 数据血缘
---
# 数据血缘（Data Lineage）

## 1. 是什么

数据血缘 = 数据的来源、转换、消费全链路可追溯。

```
源（MySQL / Kafka）
  ↓ ETL（Spark / Flink）
  中间表（ODS / DWD / DWS / ADS）
  ↓
消费（BI / 推荐 / 报表）
```

## 2. 血缘分类

| 血缘类型 | 描述 | 工具 |
|----------|------|------|
| **表级血缘** | 表 A ← 表 B（哪些列来自哪些源） | OpenLineage / DataHub |
| **字段级血缘** | A.c1 ← B.c2 | OpenLineage / Marquez |
| **任务级血缘** | Job X 读 A 写 B | Airflow / Flink |
| **脚本级血缘** | parse SQL → 提取血缘 | sqlglot |

## 3. 实战：自动采集血缘

### 3.1 Airflow + OpenLineage

```python
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from openlineage.airflow import DAG as OLDAG

with DAG('etl_orders', start_date=..., schedule='@daily') as dag:
  extract = PostgresOperator(
    task_id='extract',
    postgres_conn_id='mysql_src',
    sql='SELECT * FROM orders WHERE dt = {{ ds }}'
  )
  load = PostgresOperator(
    task_id='load',
    postgres_conn_id='mysql_dw',
    sql='INSERT INTO dwd.orders SELECT * FROM extract'
  )
  extract >> load

# 自动产生血缘事件
# → Marquez（OpenLineage 后端）
# → 表 / 列 / 任务 / 时间 全记录
```

### 3.2 Spark + OpenLineage

```python
from openlineage.spark import OpenLineageSparkListener
spark = SparkSession.builder
  .config("spark.extraListeners", "io.openlineage.spark.agent.OpenLineageSparkListener")
  .getOrCreate()

# 自动产生血缘
spark.read.parquet("...").write.parquet("...")
```

### 3.3 Flink + OpenLineage

```xml
<dependency>
  <groupId>io.openlineage</groupId>
  <artifactId>openlineage-flink</artifactId>
</dependency>
```

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
env.getConfig().registerPlugin(new OpenLineagePlugin());
```

## 4. 主流工具

| 工具 | 特点 |
|------|------|
| **OpenLineage** | CNCF 标准，跨工具 |
| **Marquez** | OpenLineage 参考实现 |
| **DataHub** | LinkedIn 出品，元数据 + 血缘 + 治理 |
| **Apache Atlas** | Hadoop 生态元数据 + 血缘 |
| **Amundsen** | Lyft 出品，数据发现 + 血缘 |

## 5. 实战案例：电商数仓血缘

```
源：
  MySQL orders (dt, user_id, amount)
  Kafka order_events
   ↓
ODS：
  Hive ods_orders (id, user_id, amount, dt)
   ↓
DWD：
  Spark dwd_orders (清洗：去掉无效订单、合并 user_info)
   ↓
DWS：
  Spark dws_user_daily (按 user_id 聚合 PV / GMV)
   ↓
ADS：
  ClickHouse ads_user_metrics (写入 OLAP 引擎)
   ↓
消费：
  BI 报表 / 推荐系统
```

每一步都有血缘记录 → 出问题时秒级定位。

## 6. 血缘存储模型

| 存储 | 特点 |
|------|------|
| **Neo4j** | 图数据库（推荐） |
| **JanusGraph** | 分布式图 |
| **MySQL** | 简单（关联表） |
| **OpenLineage + Marquez** | 事件流 + 图存储 |

## 7. 实战：从零搭建

```python
# 1. 启动 Marquez
docker run -d --name marquez   -p 9000:9000   marquezproject/marquez:latest

# 2. Spark 集成
spark = SparkSession.builder
  .config("spark.extraListeners", "io.openlineage.spark.agent.OpenLineageSparkListener")
  .config("spark.openlineage.transport.type", "http")
  .config("spark.openlineage.url", "http://localhost:9000")
  .getOrCreate()

# 3. 自动产生血缘
df = spark.read.parquet("hdfs:///data/orders/")
df.write.parquet("hdfs:///data/dwd_orders/")
# → 自动推送血缘到 Marquez
# → OpenLineage UI 可视化
```

## 8. 实战选型

| 规模 | 选 |
|------|-----|
| 小 / 中 | DataHub（all-in-one） |
| 大 / 跨团队 | OpenLineage + Marquez（标准） |
| 已有 Hadoop | Apache Atlas |
| 数据发现 | Amundsen（轻量） |

## 9. 实战技巧

1. **自动采集**：优先 OpenLineage（少人工）
2. **字段级**：高级需求（隐私 / 合规）
3. **版本控制**：血缘变更进 Git
4. **跨平台**：用 OpenLineage 标准，避免锁定
5. **与元数据集成**：血缘 + 字段 Schema = 完整元数据

## 10. 实战案例：数仓治理

```
场景：分析师发现 dws_user_daily 数据异常
传统方式：查 ETL 脚本 → 看 SQL → 找源 → 验证
  → 平均 2 小时

血缘方式：DataHub → 点击 dws_user_daily → 自动展示上游链路
  → 上游：ods_orders → dwd_orders → dws_user_daily
  → 2 秒定位
```

## 11. 实战 checklist

- [ ] 选型（OpenLineage / DataHub / Atlas）
- [ ] 部署（Marquez / Neo4j 后端）
- [ ] 集成 ETL（Airflow / Spark / Flink）
- [ ] 字段级血缘（高级）
- [ ] 监控（血缘缺失 / 异常）
- [ ] 与数据治理集成

## 🔗 下一步
- [Flink CDC](/05-flink/cdc)
- [数据湖 三剑客](/10-data-lake/three-pillars)
