---
layout: home

hero:
  name: 大数据 / 数据仓库 / 数据湖仓 知识图谱
  text: 系统化学习大数据全栈
  tagline: Hadoop 生态 / Spark / Flink / Hive / Kafka / Iceberg / ClickHouse / Airflow
  actions:
    - theme: brand
      text: 🧭 学习路径
      link: /path
    - theme: alt
      text: 🌐 知识图谱
      link: /graph
    - theme: alt
      text: 🧠 思维导图
      link: /mindmap
    - theme: alt
      text: 📋 命令速查
      link: /cheatsheet

features:
  - icon: 🧠
    title: 大数据基础
    details: 4V 特征 · Hadoop 生态 · 批 / 流计算 · CAP 选型
    link: /01-basics/4v
    linkText: 看基础 →
  - icon: 📦
    title: HDFS
    details: 架构 · 副本机制 · NameNode HA · 常用命令
    link: /02-hdfs/architecture
    linkText: 看 HDFS →
  - icon: ⚙️
    title: MapReduce
    details: 原理 · Shuffle · Combiner · Partitioner
    link: /03-mapreduce/principle
    linkText: 看 MR →
  - icon: 🔥
    title: Spark
    details: Core / RDD · SQL / DataFrame · Streaming · 调优
    link: /04-spark/rdd
    linkText: 看 Spark →
  - icon: 🌊
    title: Flink
    details: 架构 · 状态 · Checkpoint · Exactly-once
    link: /05-flink/architecture
    linkText: 看 Flink →
  - icon: 🏛️
    title: Hive
    details: 架构 · 优化 · Hive on Spark/Tez
    link: /06-hive/architecture
    linkText: 看 Hive →
  - icon: 📨
    title: Kafka 流
    details: Streams · CDC 同步 · 数据血缘
    link: /07-kafka-streaming/streams
    linkText: 看 Kafka →
  - icon: 🏛️
    title: 数据建模
    details: Inmon vs Kimball · 星型 / 雪花 · Data Vault
    link: /08-modeling/inmon-kimball
    linkText: 看建模 →
  - icon: 🏢
    title: 数仓架构
    details: Snowflake · Redshift · BigQuery
    link: /09-dw-architecture/snowflake
    linkText: 看数仓 →
  - icon: 💧
    title: 数据湖
    details: 三剑客 Delta / Iceberg / Hudi · Lakehouse
    link: /10-data-lake/three-pillars
    linkText: 看数据湖 →
  - icon: 🔄
    title: ELT 流水线
    details: Airflow / dbt · CDC 同步 · 数据血缘
    link: /11-elt-pipeline/airflow-dbt
    linkText: 看 ELT →
  - icon: 📊
    title: OLAP 引擎
    details: ClickHouse · Doris · StarRocks · 选型
    link: /12-olap-engine/clickhouse
    linkText: 看 OLAP →
  - icon: 🏢
    title: 企业案例
    details: 用户画像 · 推荐 · 风控 · 日志分析
    link: /13-cases/user-profile
    linkText: 看案例 →
  - icon: 🎯
    title: 面试 / 实战
    details: 高频面试题 · 项目案例 · 学习路径
    link: /14-interview-practice/questions
    linkText: 看面试 →
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "Hadoop / Spark / Flink / Hive / Kafka 各自独立文档",
      "数据仓库 vs 数据湖 vs Lakehouse 怎么选",
      "离线数仓 vs 实时数仓 怎么统一",
      "ClickHouse / Doris / StarRocks 怎么选",
      "模型设计 Inmon vs Kimball vs Data Vault 怎么选"
    ]
const goals = [
      "4V特征 / Hadoop生态 / 分布式存储原理",
      "Spark / Flink / Hive 核心原理与调优",
      "Kafka 流处理 / CDC / 数据血缘",
      "数据建模 Inmon / Kimball / Data Vault",
      "现代数仓架构 Snowflake / Redshift / BigQuery",
      "数据湖三剑客 Delta / Iceberg / Hudi",
      "OLAP 引擎 ClickHouse / Doris / StarRocks",
      "ELT 流水线 Airflow / dbt",
      "真实业务案例：用户画像 / 推荐 / 风控 / 日志"
    ]
const relatedSites = [
      { site: "kafka", path: "/03-stream/overview", label: "流处理引擎" },
      { site: "mysql", path: "/01-foundation/architecture", label: "OLTP 数据库" },
      { site: "clickhouse", path: "/01-basics/overview", label: "ClickHouse 列存" },
      { site: "filesystem", path: "/03-distributed/hdfs", label: "HDFS 分布式存储" },
      { site: "architecture", path: "/01-distributed/cap", label: "分布式理论" }
    ]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>
## 🎯 学习路径

```
🧠 基础    →  4V / Hadoop 生态 / CAP
📦 HDFS    →  架构 / 副本 / HA
⚙️ 计算   →  MapReduce / Spark / Flink
🏛️ Hive    →  架构 / 优化 / Engine
📨 Kafka    →  Streams / CDC / 血缘
🏛️ 建模   →  Inmon / Kimball / 星型
🏢 数仓    →  Snowflake / Redshift
💧 数据湖  →  Delta / Iceberg / Hudi / Lakehouse
🔄 ELT    →  Airflow / dbt
📊 OLAP    →  ClickHouse / Doris / StarRocks
🏢 案例    →  用户画像 / 推荐 / 风控 / 日志
🎯 面试    →  高频题 / 项目案例
```

完整路径请看 [📖 学习路径](/path)。

## 💡 学习建议

```
1. 数据工程师入门  →  大数据基础 + HDFS + MapReduce
2. 离线数仓      →  Hive + Spark SQL + 数据建模 + 数仓架构
3. 实时计算      →  Kafka Streams + Flink + CDC
4. 数据湖 / Lakehouse  →  Delta / Iceberg / Hudi
5. 面试       →  OLAP 选型 + 案例 + 高频题
```

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [kafka](https://java-px.bot.cd/kafka/)：Kafka 流处理
- [es](https://java-px.bot.cd/es/)：Elasticsearch
- [clickhouse](https://java-px.bot.cd/clickhouse/)：ClickHouse OLAP
- [hadoop](https://java-px.bot.cd/hadoop/)：Hadoop 生态
- [python](https://java-px.bot.cd/python/)：Python 数据处理
