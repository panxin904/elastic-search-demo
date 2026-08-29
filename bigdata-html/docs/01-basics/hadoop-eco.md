---
title: Hadoop 生态
date: 2026-08-15  # date-auto-injected
---
# Hadoop 生态

## 1. Hadoop 核心

Hadoop = HDFS（存储）+ MapReduce（计算）+ YARN（调度）

```
        HDFS (Hadoop Distributed File System)
        - 大文件分块（默认 128MB）
        - 副本（默认 3 份）
        - NameNode（主）+ DataNode（从）

        YARN (Yet Another Resource Negotiator)
        - ResourceManager（主）
        - NodeManager（从）
        - 调度 + 资源管理

        MapReduce
        - Map（映射）
        - Shuffle（混洗）
        - Reduce（归约）
```

## 2. 周边生态

### 2.1 存储层

| 项目 | 用途 |
|------|------|
| **HDFS** | 分布式文件系统 |
| **HBase** | 列式 NoSQL（基于 HDFS） |
| **Kafka** | 消息队列（流处理核心） |
| **Pulsar** | 新一代消息队列（腾讯 / 雅虎） |
| **Iceberg** | 表格式（Netflix / Apple） |
| **Hudi** | 表格式（Uber） |
| **Delta Lake** | 表格式（Databricks） |

### 2.2 计算层

| 项目 | 用途 |
|------|------|
| **MapReduce** | 离线批处理 |
| **Spark** | 内存计算（统一批 / 流 / ML） |
| **Flink** | 真正的流处理（低延迟） |
| **Tez** | DAG 执行引擎（Hive / Pig 用） |
| **Presto / Trino** | 分布式 SQL 查询引擎 |
| **Impala** | C++ 实现的低延迟 SQL |
| **Hive** | SQL on Hadoop |

### 2.3 调度 / 协调

| 项目 | 用途 |
|------|------|
| **YARN** | 资源调度 |
| **Mesos** | 集群调度（被 K8s 取代） |
| **Kubernetes** | 容器编排（事实标准） |
| **Airflow** | DAG 任务调度 |

### 2.4 其他生态

| 项目 | 用途 |
|------|------|
| **ZooKeeper** | 分布式协调（替代品：etcd） |
| **Oozie** | 任务工作流 |
| **Sqoop** | 关系数据库 ↔ HDFS |
| **Flume** | 日志采集（替代品：Fluentd / Vector） |
| **Pig** | 脚本化数据处理（被 Spark SQL 取代） |

## 3. 完整生态图

```
采集层
  Flume / Kafka Connect / Logstash / Sqoop
       ↓
消息层
  Kafka / Pulsar / RocketMQ
       ↓
存储层
  HDFS / HBase / S3 / Iceberg / Hudi / Delta
       ↓
调度层
  YARN / Mesos / Kubernetes
       ↓
计算层
  Spark / Flink / Hive / Tez / Presto
       ↓
服务层
  Presto / Trino / Impala / HiveServer
       ↓
应用层
  BI / 推荐 / 风控 / 搜索 / 画像
```

## 4. Hadoop vs Spark vs Flink

| | Hadoop MR | Spark | Flink |
|--|-----------|--------|--------|
| 计算模型 | 批（迭代） | 内存迭代 | 流（持续） |
| 延迟 | 分钟 | 秒 | 毫秒 |
| 状态 | 磁盘（HDFS） | 内存 | 内存 + 磁盘 |
| ML | 弱 | 强（MLlib） | 中 |
| 流 | 弱 | Structured Streaming | 强（核心） |
| SQL | Hive | Spark SQL | Flink SQL |
| 适合 | 离线超大数据 | 通用数据处理 | 实时低延迟 |

## 5. 现代数据栈变迁

```
传统栈（2010）：
  RDBMS → ETL → Hadoop → BI

Lambda 架构（2015）：
  Batch Layer (Hadoop) + Speed Layer (Storm/Flink) + Serving Layer

Kappa 架构（2016）：
  单一 Kafka 流 → Flink → Serving

Lakehouse 架构（2020+）：
  对象存储 + Delta/Iceberg/Hudi + Spark/Flink

AI 架构（2024+）：
  LLM + RAG + Agent + 向量数据库 + 传统数仓
```

## 6. 实战选型

| 场景 | 选 |
|------|-----|
| 离线大数据 | Hadoop + Spark + Hive |
| 实时数据 | Kafka + Flink + ClickHouse |
| 数据湖 | S3 + Spark + Iceberg |
| 容器化 | K8s + Spark Operator / Flink Operator |
| 资源受限 | 云服务（EMR / MaxCompute / Databricks） |

## 7. 实际公司技术栈样本

| 公司 | 栈 |
|------|-----|
| Netflix | Kafka + Flink + S3 + Iceberg + Athena |
| Uber | Kafka + Flink + Hudi + Pinot |
| 字节 | Kafka + Flink + Iceberg + Doris |
| 美团 | Kafka + Flink + HDFS + ElasticSearch |
| 阿里 | MaxCompute + Pangu + 各种引擎 |

## 8. 经典学习路径

```
1. Linux 命令 + Shell
2. SQL + 数据库基础
3. Hadoop 3 大件（HDFS + MR + YARN）
4. Hive SQL（数仓 SQL）
5. Spark SQL（数据处理）
6. Kafka（消息队列）
7. Flink（实时计算）
8. Iceberg / Hudi（数据湖）
9. OLAP 引擎（ClickHouse / Doris）
```

## 9. 常见误区

- ❌ Hadoop 已死 → ❌ 实际：HDFS 仍是大数据基础
- ❌ Spark 取代 Hadoop → ❌ 实际：Spark 跑在 YARN/K8s 上
- ❌ Flink 取代 Spark → ❌ 实际：两者互补
- ❌ 数据库能解决一切 → ❌ 大数据需要专门基础设施

## 10. 学习资源

- **官方文档**：Hadoop / Spark / Flink / Kafka
- **数据实战**：Apache Kafka 实战 / Spark 权威指南
- **中文社区**：阿里云 / 美团 / 字节技术博客
- **实操**：CDH / HDP（Cloudera / Hortonworks）

## 🔗 下一步
- [HDFS 架构](/02-hdfs/architecture)
- [Spark Core / RDD](/04-spark/rdd)
- [Flink 架构](/05-flink/architecture)
