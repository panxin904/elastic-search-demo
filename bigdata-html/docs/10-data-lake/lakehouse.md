---
title: Lakehouse 架构
date: 2026-08-15  # date-auto-injected
---
# Lakehouse 架构

## 1. 是什么

Lakehouse = 数据湖（灵活 + 廉价）+ 数据仓库（事务 + 性能）。

```
传统数据湖：原始 + 灵活 + 廉价
  无事务
  无性能保障
  难管理

传统数据仓库：事务 + 性能
  格式受限
  存储贵
  难探索

Lakehouse = 两者结合
  对象存储（S3 / OSS）+ 事务（Iceberg / Delta / Hudi）
  列式查询（Doris / Trino）
  流批一体（Spark / Flink）
```

## 2. 三大特性

### 2.1 事务（ACID）

Lakehouse = 对象存储 + ACID
  - 表格式（Iceberg / Delta / Hudi）提供 ACID
  - 不需要专门数仓
  - 既灵活又可靠

### 2.2 流批一体

同一张表：
  - 批处理：批量写入（高吞吐）
  - 流处理：实时 upsert（低延迟）
  - 同一份数据
  - 互不冲突

### 2.3 Schema 演进

字段加 / 改 / 类型变
  - 旧数据兼容
  - 不需要 ETL 重导
  - 渐进迁移

## 3. 架构

源（Kafka / MySQL / Logs）
   ↓
  Spark / Flink
   ↓
  Lakehouse 存储（Iceberg / Delta / Hudi）
  - 原始层（bronze）
  - 整合层（silver）
  - 应用层（gold）
   ↓
  查询引擎（Spark / Trino / Doris / ClickHouse）
   ↓
  BI / ML / 应用
```

## 4. 实战案例

### 案例 1：电商湖仓

源：
  MySQL（业务库）
  Kafka（订单事件 / 用户行为）

  ↓ Flink CDC

Lakehouse（Iceberg）：
  bronze.orders（原始，1:1 复制）
  silver.orders（清洗 + 合并 user / product）
  gold.user_daily（聚合）

  ↓ Doris / StarRocks（OLAP 查询）

应用：
  推荐系统（毫秒级查询）
  BI 报表（每日）
  风控（实时特征）

### 案例 2：金融湖仓

源：
  Kafka（交易事件）
  CDC（核心系统）

  ↓ Flink

Lakehouse（Hudi）：
  bronze.tx（原始）
  silver.tx_dwd（清洗 + 风控打标）
  gold.account_balance（账户余额快照）

  ↓ ClickHouse（OLAP）

应用：
  风控（实时）
  监管报送（T+1）
  BI 报表

## 5. 技术栈选型

存储层：
  对象存储：S3 / OSS / GCS / MinIO
  表格式：Iceberg（多引擎）/ Delta（Databricks）/ Hudi（增量）

计算层：
  流：Flink / Spark Streaming
  批：Spark SQL / Hive / Trino
  ML：Spark MLlib / MLflow

查询层：
  OLAP：Doris / StarRocks / ClickHouse / Trino
  BI：Tableau / Looker / Superset
  ML：MLflow / Jupyter
```

## 6. 实战选型

| 规模 | 存储 | 计算 | 查询 |
|------|------|------|------|
| 中小 | Iceberg | Spark | Doris / ClickHouse |
| 大 | Iceberg / Delta | Spark / Flink | Doris / StarRocks |
| 私有化 | MinIO + Iceberg | Flink | Doris |
| 云 | S3 + Iceberg | Spark + Glue | Athena / BigQuery |

## 7. 实战案例：Databricks Lakehouse

Delta Live Tables (DLT) = 声明式 ETL
  - 自动建表
  - 自动增量处理
  - 自动数据质量检查
  - 自动 schema 演进
  - 一键发布到生产

Unity Catalog：
  - 统一元数据
  - 跨引擎访问
  - 细粒度权限

## 8. 实战案例：Apache Iceberg + Trino

数据湖（Iceberg on S3）
   ↓
Trino（查询引擎，跨源）
  - Hive / Iceberg / Delta / JDBC 全部
  - 联邦查询（多个数据源）
   ↓
  BI 工具（直接连 Trino）
```

## 9. 实战选型

```
选择存储（Iceberg / Delta / Hudi）：
  多引擎 → Iceberg
  Spark 深度 → Delta
  CDC 实时 → Hudi

选择查询（Doris / StarRocks / Trino / ClickHouse）：
  Doris / StarRocks → MPP OLAP（推荐）
  Trino → 联邦查询
  ClickHouse → 海量日志
```

## 10. 实战 checklist

- [ ] 选表格式（Iceberg / Delta / Hudi）
- [ ] 选查询引擎（Doris / Trino / ClickHouse）
- [ ] 选存储（S3 / OSS / MinIO）
- [ ] 选 Catalog（Hive Metastore / Nessie / Glue）
- [ ] 选 ETL（Spark / Flink / DataX）
- [ ] 选 BI 工具（Tableau / Looker / Superset）
- [ ] 监控（commit / 性能 / 成本）

## 11. 实战建议

1. 不要混用三剑客：一个湖仓用一种格式
2. Iceberg 优先：多引擎 + 社区活跃
3. 不要过度表格式：Hive 外表 + Iceberg = 简单又强
4. 批流一体：Flink 写入 + Trino 查询
5. 监控：commit 失败 / 性能 / 成本

## 12. 实战对比

| 栈 | 优势 | 适用 |
|------|------|------|
| Iceberg + Trino + S3 | 多引擎、灵活 | 大型互联网 |
| Delta + Databricks + S3 | 简单、强集成 | AWS 用户 |
| Hudi + Hive + HDFS | 实时 upsert | CDC 场景 |
| Doris + MinIO + Iceberg | 私有化高性能 | 金融 / 政企 |

## 13. 实战：完整 Lakehouse 项目

```python
# 1. 加载（PyIceberg）
from pyiceberg.catalog import load_catalog
catalog = load_catalog(
  "prod",
  warehouse="s3://my-warehouse/",
  uri="https://glue.us-east-1.amazonaws.com/iceberg"
)

# 2. 写（流处理，PyFlink）
from pyflink.datastream import StreamExecutionEnvironment
from pyiceberg.flink import IcebergSink
env = StreamExecutionEnvironment.getExecutionEnvironment()
stream.add_sink(IcebergSink.builder()
  .catalog(catalog)
  .table_identifier("default.events")
  .build())

# 3. 查（Trino）
# trino> SELECT * FROM iceberg.dwd.events WHERE ts > '2024-01-15';
```

## 14. 实战场景 vs 选型

| 场景 | 湖仓栈 |
|------|-------|
| 互联网电商 | Iceberg + Doris + S3 |
| 金融银行 | Hudi + Hive + HDFS |
| 物流交通 | Iceberg + Trino + S3 |
| 制造能源 | Delta + Databricks + Azure |
| 政企 | Iceberg + Doris + MinIO（私有化） |

## 15. 实战选型决策流程

1. 评估规模（数据量 / QPS / 延迟）
2. 选择存储（对象存储 S3 / OSS / MinIO）
3. 选择表格式（Iceberg / Delta / Hudi）
4. 选择引擎（Spark / Flink / Trino / Doris）
5. 选择 ETL（Spark SQL / Flink SQL / DataX）
6. 选择 BI（Tableau / Looker / Superset）

## 16. 实战总结

- 没有最好，只有最合适
- 多引擎 → Iceberg
- Spark 深度 → Delta
- CDC 实时 → Hudi
- 私有化 → Doris + MinIO + Iceberg
- 趋势：Iceberg 成为事实标准

## 🔗 下一步

- [数据湖三剑客](/10-data-lake/three-pillars)
- [Delta / Iceberg / Hudi](/10-data-lake/delta-iceberg-hudi)
- [Doris / StarRocks](/12-olap-engine/doris-starrocks)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [kafka](https://java-px.bot.cd/kafka/):Kafka 流处理
- [es](https://java-px.bot.cd/es/):Elasticsearch
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
