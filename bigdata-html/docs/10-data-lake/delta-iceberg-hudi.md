---
title: Delta Iceberg Hudi 选型
---
# Delta / Iceberg / Hudi 详解

## 1. Delta Lake 详解

### 架构

```
Delta Lake = Parquet + _delta_log (JSON)
  - 数据：Parquet 列式
  - 元数据：_delta_log（每次 commit 一行 JSON）
  - Checkpoint：parquet 快照
  - Schema：JSON in _delta_log
```

### 核心特性

```sql
-- ACID 事务
BEGIN;
INSERT INTO events VALUES (1, 'Alice', 100);
INSERT INTO events VALUES (2, 'Bob', 200);
COMMIT;

-- Time Travel
SELECT * FROM events VERSION AS OF 5;
SELECT * FROM events TIMESTAMP AS OF '2024-01-15 10:00:00';

-- Schema 演进
ALTER TABLE events ADD COLUMN country STRING;
```

### 实战

```python
# PySpark + Delta Lake
df = spark.read.format("delta").load("hdfs:///data/delta/events")
df.write.format("delta").mode("overwrite").save("hdfs:///data/delta/events_v2")
```

## 2. Apache Iceberg 详解

### 架构

```
Iceberg = 数据 + 元数据（metadata.json）
  - 数据：Parquet / ORC / Avro
  - 元数据：metadata.json + manifest list + manifest
  - 分区：隐藏分区（spec）
  - 版本：snapshot ID（每次 commit）
```

### 核心特性

```sql
-- Hidden Partitioning
CREATE TABLE events (
  id BIGINT, ts TIMESTAMP, user_id BIGINT
) PARTITIONED BY (days(ts));

-- Time Travel
SELECT * FROM events
FOR SYSTEM_TIME AS OF '2024-01-15 10:00:00';

-- Schema 演进
ALTER TABLE events ADD COLUMN country STRING;
```

## 3. Apache Hudi 详解

### 架构

```
Hudi = 数据 + 增量日志（.hoodie）
  - Copy-on-Write（COW）：读优化
  - Merge-on-Read（MOR）：写优化
  - 增量 upsert（准实时摄取）
```

### 核心特性

```sql
-- 增量 upsert
INSERT INTO events
SELECT * FROM kafka_events;
```

## 4. 选型对比

| 维度 | Delta Lake | Iceberg | Hudi |
|------|-----------|---------|------|
| 事务 | ACID | ACID | ACID |
| Time Travel | 是 | 是 | 是 |
| Schema 演进 | 强 | 极强 | 强 |
| 多引擎 | Spark 为主 | 多 | 多 |
| 实时 upsert | 弱 | 弱 | 强 |
| 增量查询 | 否 | 否 | 强 |
| 生态 | Spark 强 | Trino/Spark/Flink | Spark/Flink |
| 成熟度 | 高 | 中 | 中 |

## 5. 实战选型

| 场景 | 选 | 原因 |
|------|-----|------|
| Spark 生态深度 | Delta Lake | 原生集成 |
| 多引擎（Trino + Spark） | Iceberg | 引擎无关 |
| 实时 upsert（CDC） | Hudi | 增量强 |
| 大量历史数据 | Iceberg | 隐藏分区 + 压缩 |
| 快速试错 | Iceberg | 社区活跃 |
| 已有 Hive 升级 | Iceberg / Hudi | 兼容 |

## 6. 实战案例

### 案例 1：Iceberg Lakehouse

```
MySQL → Flink CDC → Kafka → Flink → Iceberg → Doris / Trino
```

### 案例 2：Hudi 实时摄取

```
Kafka → Flink → Hudi (MOR) → Hive / Spark / Presto
```

### 案例 3：Delta + Databricks

```
S3 → Auto Loader → Delta Lake → Databricks SQL
```

## 7. 实战选型决策

```
选 Iceberg：
  - 多引擎
  - 大数据湖
  - 灵活

选 Delta Lake：
  - Spark 生态
  - Databricks 用户
  - 简单

选 Hudi：
  - 实时 upsert（CDC）
  - 增量
  - 准实时
```

## 8. 实战对比：Iceberg vs Delta Lake

| 维度 | Iceberg | Delta Lake |
|------|---------|-----------|
| 推出 | 2017（Netflix） | 2015（Databricks） |
| 规范 | Apache 顶级 | 私有（部分开源） |
| 引擎 | Trino / Spark / Flink / Dremio | Spark 为主 |
| Schema 演进 | 极强 | 强 |
| Time Travel | 是 | 是 |
| 隐藏分区 | 是 | 否 |
| 多 catalog | Hive / Nessie / Glue | Hive / Glue |
| 社区 | 活跃 | 大（Databricks 主导）|

## 9. 实战技巧

1. 选择合适格式（Delta Lake / Iceberg / Hudi）
2. 启用事务、Time Travel（7 天保留）、Schema 演进
3. 监控 commit / snapshot 失败告警
4. 小数据 + 1 周压测再上

## 10. 实战 checklist

- [ ] 选择格式（Iceberg / Delta / Hudi）
- [ ] 选择引擎（Spark / Flink / Trino）
- [ ] 配置 Catalog（Hive / Nessie / Glue）
- [ ] 启用事务
- [ ] 启用 Time Travel（7 天）
- [ ] 启用 Schema 演进
- [ ] 监控（commit / 失败）
- [ ] 备份（重要数据）

## 11. 实战代码

```python
# Iceberg 写入（PyIceberg）
from pyiceberg.catalog import load_catalog
catalog = load_catalog("prod", **config)
table = catalog.load_table("default.events")

# 事务
with table.transaction() as tx:
    tx.append(df_new)
    tx.delete(filter_expr="user_id = 123")

# Time Travel
table = catalog.load_table(
    "default.events", snapshot_id=1234567890
)
df = table.scan().to_df()
```

## 12. 实战建议

- 不要从零写：用现成（Spark / Flink / Trino / Presto）
- 选择合适的 Catalog（Hive / Nessie / Glue）
- 测试小数据 + 1 周压测再上
- 监控（commit / 失败 / 延迟）
- 备份（重要数据）

## 13. 实战场景 vs 选型

| 场景 | 湖仓栈 |
|------|-------|
| 互联网电商 | Iceberg + Doris + S3 |
| 金融银行 | Hudi + Hive + HDFS |
| 物流交通 | Iceberg + Trino + S3 |
| 制造能源 | Delta + Databricks + Azure |
| 政企 | Iceberg + Doris + MinIO（私有化）|

## 14. 实战 checklist

- [ ] 表格式选型（Iceberg / Delta / Hudi）
- [ ] 引擎选型（Spark / Flink / Trino / Doris）
- [ ] 存储选型（S3 / OSS / MinIO / HDFS）
- [ ] Catalog 配置（Hive Metastore / Nessie / Glue）
- [ ] ETL 选型（Spark / Flink / DataX）
- [ ] BI 工具（Tableau / Looker / Superset）
- [ ] 监控（commit / 性能 / 成本）

## 15. 实战选型决策流程

1. 评估规模（数据量 / QPS / 延迟）
2. 选择存储（对象存储 S3 / OSS / MinIO）
3. 选择表格式（Iceberg / Delta / Hudi）
4. 选择引擎（Spark / Flink / Trino / Doris）
5. 选择 ETL（Spark SQL / Flink SQL / DataX）
6. 选择 BI（Tableau / Looker / Superset）

## 16. 实战对比

| 组合 | 性能 | 成本 | 复杂度 | 适合 |
|------|------|------|--------|------|
| Iceberg + Doris + S3 | 高 | 中 | 中 | 大型互联网 |
| Iceberg + StarRocks | 极高 | 中 | 中 | 实时 OLAP |
| Delta + Databricks | 高 | 高 | 低 | AWS 用户 |
| Hudi + Flink | 高 | 低 | 高 | CDC 实时摄取 |
| ClickHouse + S3 | 高 | 低 | 低 | 海量日志 |

## 17. 实战选型建议

- 灵活 + 多引擎 → **Iceberg + Doris / Trino**（首选）
- Spark 生态 → **Delta + Databricks**
- 实时 upsert（CDC）→ **Hudi + Flink**
- 海量日志 → **ClickHouse + S3**
- 私有化 → **Doris + MinIO + Iceberg**

## 18. 实战总结

- 没有最好，只有最合适
- 多引擎 → Iceberg
- Spark 深度 → Delta
- CDC 实时 → Hudi
- 私有化 → Doris + MinIO + Iceberg
- 趋势：Iceberg 成为事实标准

## 🔗 下一步

- [数据湖三剑客](/10-data-lake/three-pillars)
- [Lakehouse 架构](/10-data-lake/lakehouse)
- [Doris / StarRocks](/12-olap-engine/doris-starrocks)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [kafka](https://java-px.bot.cd/kafka/):Kafka 流处理
- [es](https://java-px.bot.cd/es/):Elasticsearch
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
