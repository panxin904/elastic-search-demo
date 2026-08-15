---
title: 数据湖三剑客
---
# 数据湖三剑客

## 1. 是什么

数据湖（Data Lake）= 存储原始数据（结构化 + 半结构化 + 非结构化）的存储系统。

核心特点：
  - Schema-on-read（读取时定义）
  - 原始数据 + 灵活分析
  - 大规模 + 低成本

三大开源数据湖格式：
  - **Apache Iceberg**（Netflix 出品）
  - **Delta Lake**（Databricks 出品）
  - **Apache Hudi**（Uber 出品）

## 2. 为什么需要数据湖

传统 Hive / 数仓痛点：
  - 写入后修改难（partition 不可变）
  - ACID 不支持（仅 final 写）
  - Schema 演进难
  - 元数据查询慢（MSCK REPAIR）

数据湖目标：
  - ACID 事务
  - Schema 演进
  - 隐藏分区
  - 时间旅行
  - 高性能查询

## 3. 三大开源对比

| 特性 | Iceberg | Delta Lake | Hudi |
|------|---------|-----------|------|
| 出品 | Netflix | Databricks | Uber |
| 多引擎 | Spark / Flink / Trino / Hive | Spark（强）/ Flink | Spark / Flink |
| 写入 | Append / Overwrite / Merge | Append / Overwrite / Merge | Insert / Upsert / Delete |
| 更新 | Merge Into | Merge Into | Upsert / Delete |
| 时间旅行 | 支持（snapshot） | 支持（version） | 支持（commit） |
| 隐藏分区 | 支持 | 部分支持 | 不支持 |
| Schema 演进 | 支持 | 支持 | 支持 |
| 社区 | 活跃 | 商业强 | 活跃 |

## 4. Apache Iceberg

### 4.1 架构

```
Iceberg Table
  ├── Metadata（manifest 列表）
  │    ├── Manifest File（数据文件清单）
  │    │    ├── Data File（Parquet / ORC）
  │    │    └── ...
  │    └── ...
  └── Snapshot（版本快照）
```

### 4.2 核心特性

```sql
-- 1. 建表（隐藏分区）
CREATE TABLE iceberg.db.events (
  event_id BIGINT,
  user_id BIGINT,
  ts TIMESTAMP
) USING iceberg
PARTITIONED BY (days(ts));  -- 隐藏分区，自动按天

-- 2. 写入
INSERT INTO iceberg.db.events VALUES (1, 100, '2024-01-15 10:00:00');

-- 3. 时间旅行
SELECT * FROM iceberg.db.events
FOR SYSTEM_TIME AS OF '2024-01-15 12:00:00';

-- 4. Schema 演进
ALTER TABLE iceberg.db.events ADD COLUMN country STRING;

-- 5. Merge Into
MERGE INTO iceberg.db.events t
USING updates s ON t.event_id = s.event_id
WHEN MATCHED THEN UPDATE SET country = s.country
WHEN NOT MATCHED THEN INSERT *;
```

## 5. Delta Lake

### 5.1 架构

```
Delta Table
  ├── _delta_log/
  │    ├── 000.json（事务日志）
  │    └── ...
  └── Data Files（Parquet）
```

### 5.2 核心特性

```python
# 1. 写入（Delta Lake 2.0+）
df.write.format("delta").mode("append").save("/path/events")

# 2. Upsert
from delta.tables import DeltaTable

delta = DeltaTable.forPath(spark, "/path/events")
delta.merge(
  updates_df,
  "events.event_id = updates.event_id"
).whenMatchedUpdateAll()  .whenNotMatchedInsertAll()  .execute()

# 3. 时间旅行
spark.read.format("delta")   .option("versionAsOf", 5)   .load("/path/events")

# 4. 流批一体（Delta Live Tables）
spark.readStream.format("delta")   .load("/path/events")   .writeStream.format("delta")   .option("checkpointLocation", "/path/checkpoint")   .start("/path/events_stream")
```

## 6. Apache Hudi

### 6.1 架构

```
Hudi Table
  ├── .hoodie/
  │    ├── hoodie.log（事务日志）
  │    └── ...
  └── Data Files（Parquet / Avro）
  - Copy on Write（CoW）
  - Merge on Read（MoR）
```

### 6.2 核心特性

```python
# 1. 写入（Hudi 0.12+）
df.write.format("hudi")   .option("hoodie.table.name", "events")   .option("hoodie.datasource.write.recordkey.field", "event_id")   .option("hoodie.datasource.write.operation", "upsert")   .mode("append")   .save("/path/events")

# 2. 增量查询
spark.read.format("hudi")   .option("hoodie.datasource.query.type", "incremental")   .option("hoodie.datasource.query.incremental.enable", "true")   .load("/path/events")

# 3. CoW（重写数据文件）
.option("hoodie.datasource.write.table.type", "COPY_ON_WRITE")

# 4. MoR（追加 + 定期合并）
.option("hoodie.datasource.write.table.type", "MERGE_ON_READ")
```

## 7. 实战选型

| 场景 | 选 | 原因 |
|------|-----|------|
| 多引擎（Spark + Flink + Trino） | **Iceberg** | 通用性强 |
| Spark 深度集成 + Databricks | **Delta Lake** | 商业强 |
| CDC + 实时更新 | **Hudi** | Upsert 强 |
| 实时数仓 | Iceberg / Hudi | 性能好 |
| 云（AWS / Azure） | Delta / Iceberg | 云集成 |
| 新项目（2024+） | **Iceberg** | 趋势 |

## 8. 实战架构

```
Kafka → Flink / Spark → Iceberg（Hudi / Delta）
  　　　　　　　↓
  　　　 Trino / Doris / StarRocks（查询）
  　　　　　　　↓
  　　　　　Grafana（可视化）
```

## 9. 实战建议

1. **选 Iceberg**（新项目首选）
2. **多引擎集成**（Spark + Flink + Trino）
3. **隐藏分区**（自动维护）
4. **时间旅行**（回溯 / 审计）
5. **监控**（manifest 大小 / 快照数）

## 10. 实战 checklist

- [ ] 选 Iceberg / Delta / Hudi
- [ ] 多引擎集成
- [ ] 隐藏分区设计
- [ ] 时间旅行（snapshot / version）
- [ ] 监控（manifest / snapshot）

## 🔗 下一步
- [Delta / Iceberg / Hudi](/10-data-lake/delta-iceberg-hudi)
- [Lakehouse](/10-data-lake/lakehouse)
- [Snowflake 架构](/09-dw-architecture/snowflake)
