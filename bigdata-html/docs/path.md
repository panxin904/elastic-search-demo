---
title: 学习路径
date: 2026-08-15  # date-auto-injected
---
# 📖 大数据全栈 学习路径

## 🛤️ 路径 1：数据工程入门（2 周）
1. [4V 特征](/01-basics/4v) — 大数据根
2. [Hadoop 生态](/01-basics/hadoop-eco) — 整体版图
3. [HDFS 架构](/02-hdfs/architecture) — 分布式存储原理
4. [MapReduce 原理](/03-mapreduce/principle) — 经典计算模式
5. [Spark Core / RDD](/04-spark/rdd) — 事实标准
6. [Hive 架构](/06-hive/architecture) — 数仓 SQL

**目标**：能理解 Hadoop 三大件 + 写简单 Spark 任务。

## 🛤️ 路径 2：离线数仓工程师（3-4 周）
- 完成"入门"路径
- [Spark SQL / DataFrame](/04-spark/dataframe) — 数据处理核心
- [Spark 调优](/04-spark/tuning) — 性能优化
- [Hive 优化](/06-hive/optimize) — SQL 调优
- [Inmon vs Kimball](/08-modeling/inmon-kimball) — 数仓建模
- [星型 / 雪花模型](/08-modeling/star-snowflake) — 维度建模
- [Snowflake 架构](/09-dw-architecture/snowflake) — 现代数仓
- [Airflow / dbt](/11-elt-pipeline/airflow-dbt) — 调度 + 转换
- [ClickHouse 架构](/12-olap-engine/clickhouse) — OLAP 引擎

**目标**：能搭建完整离线数仓 + 写 ETL 任务。

## 🛤️ 路径 3：实时计算 / 实时数仓（3 周）
- 完成"离线数仓"路径
- [Kafka Streams](/07-kafka-streaming/streams) — 流处理基础
- [Flink 架构](/05-flink/architecture) — 流处理事实标准
- [Flink 状态与 Checkpoint](/05-flink/state) — Exactly-once
- [Flink CDC](/05-flink/cdc) — 实时同步
- [数据血缘](/07-kafka-streaming/lineage) — 可观测性
- [数据湖 三剑客](/10-data-lake/three-pillars) — 流批一体
- [Lakehouse 架构](/10-data-lake/lakehouse) — 现代架构

**目标**：能搭建实时 + 离线融合的现代数据平台。

## 🛤️ 路径 4：数据湖 / Lakehouse 架构师（3 周）
- 完成"实时"路径
- [Delta Lake / Iceberg / Hudi](/10-data-lake/delta-iceberg-hudi) — 三大格式
- [Lakehouse 架构](/10-data-lake/lakehouse) — 落地
- [Doris / StarRocks](/12-olap-engine/doris-starrocks) — MPP 查询
- [OLAP 选型](/12-olap-engine/selection) — 业务匹配
- [CDC 同步](/11-elt-pipeline/cdc) — 实时入湖
- [Airflow / dbt](/11-elt-pipeline/airflow-dbt) — 调度 + 转换

**目标**：能设计 Lakehouse 架构 + 选型 OLAP 引擎。

## 🛤️ 路径 5：面试冲刺（2 周）
- 复习 [HDFS 架构](/02-hdfs/architecture) + [副本机制](/02-hdfs/replication)
- 复习 [MapReduce 原理](/03-mapreduce/principle) + [Shuffle 详解](/03-mapreduce/shuffle)
- 复习 [Spark Core / RDD](/04-spark/rdd) + [Spark SQL / DataFrame](/04-spark/dataframe)
- 复习 [Flink 架构](/05-flink/architecture) + [Exactly-once](/05-flink/exactly-once)
- 复习 [Inmon vs Kimball](/08-modeling/inmon-kimball) + [Data Vault](/08-modeling/data-vault)
- 复习 [数据湖 三剑客](/10-data-lake/three-pillars) + [Lakehouse](/10-data-lake/lakehouse)
- 复习 [用户画像案例](/13-cases/user-profile) + [推荐系统](/13-cases/recommendation)

## 🎯 速查卡片
| 我想 | 推荐先看 |
|------|---------|
| 入门大数据 | [4V 特征](/01-basics/4v) → [HDFS](/02-hdfs/architecture) → [Spark RDD](/04-spark/rdd) |
| 学数仓建模 | [Inmon vs Kimball](/08-modeling/inmon-kimball) → [星型雪花](/08-modeling/star-snowflake) |
| 学实时计算 | [Flink 架构](/05-flink/architecture) → [Kafka Streams](/07-kafka-streaming/streams) |
| 学数据湖 | [三剑客](/10-data-lake/three-pillars) → [Lakehouse](/10-data-lake/lakehouse) |
| 学 Pipeline | [Airflow / dbt](/11-elt-pipeline/airflow-dbt) → [CDC 同步](/11-elt-pipeline/cdc) |
| 选型 OLAP | [OLAP 选型](/12-olap-engine/selection) |
| 找工作 | [高频题](/14-interview-practice/questions) + [案例](/13-cases/user-profile) |
