---
layout: home

hero:
  name: "ClickHouse"
  text: "OLAP 列式数据库深度图谱"
  tagline: "实时数仓 · 物化视图 · 生态集成 · 与 Doris / StarRocks / TiDB 对比选型"
  image:
    src: /favicon.svg
    alt: ClickHouse
  actions:
    - theme: brand
      text: 开始学习
      link: /01-basics/overview
    - theme: alt
      text: 大厂案例
      link: /case-study

features:
  - title: 🟡 基础与历史
    details: Yandex.Metrica 出身的列式 OLAP 数据库，2016 年开源。MergeTree 引擎族 + 主键排序 + 数据分区 + 向量化执行，亿级数据秒级聚合。
    link: /01-basics/overview
    linkText: 总览
  - title: 🔍 SQL 实战
    details: ClickHouse SQL 语法、聚合函数、JOIN、窗口函数、Dictionary 字典；与 MySQL/PG 语法的差异；TOP 50 常用函数实战用法。
    link: /02-sql/overview
    linkText: SQL 入门
  - title: ⚙️ 表引擎
    details: MergeTree / ReplacingMergeTree / AggregatingMergeTree / CollapsingMergeTree / VersionedCollapsing；Log / Memory / Kafka / Distributed / MaterializedView。
    link: /03-table-engine/overview
    linkText: 引擎选型
  - title: 📊 OLAP 实战
    details: 用户行为埋点 / 日志分析 / 指标存储 / 实时数仓 / 物化视图 / Bitmap 去重；Yandex / Uber / Cloudflare / 字节 / B 站真实案例。
    link: /04-olap-scenarios/overview
    linkText: 实战场景
  - title: 🔌 生态工具
    details: Kafka 引擎直接消费 / Grafana 可视化 / Prometheus remote_write / Go ch-go 客户端 / Python clickhouse-driver / dbt 转换 / Airbyte 同步。
    link: /05-ecosystem/overview
    linkText: 生态集成
  - title: 🆚 对比选型
    details: vs MySQL/PG（OLTP vs OLAP）/ vs Doris（百度）/ vs StarRocks（小米）/ vs TiDB（PingCAP）/ vs Snowflake；架构、性能、生态、选型决策。
    link: /06-compare/overview
    linkText: 选型决策
---


<ClientOnly>
  <WhyThisGraph
    :pain-points="[
      "列存 vs 行存：为什么 OLAP 要用列存？",
      "MergeTree 引擎家族（Replacing / Summing / Aggregating）怎么选？",
      "实时数仓（Lambda / Kappa / 湖仓一体）架构怎么选？",
      "集群扩容、副本、数据分片怎么平衡成本与可用性？",
      "SQL 优化：ORDER BY / PARTITION BY / INDEX / SAMPLE 怎么用？"
    ]"
    :goals="[
      "列存原理 + MergeTree 引擎对比",
      "表引擎（Log / MergeTree / Distributed / MaterializedView）",
      "数仓场景（Lambda / Kappa / 湖仓一体）",
      "生态集成（Kafka 引擎 / MySQL CDC / PG FDW）",
      "可观测性存储（Grafana Mimir / VictoriaMetrics / Loki 替代）",
      "性能调优 + 运维实战"
    ]"
    :related-sites="[
      { site: "kafka", path: "/05-ecosystem/kafka-engine", label: "Kafka 引擎消费" },
      { site: "observability", path: "/04-olap-scenarios/observability", label: "可观测性存储" },
      { site: "mysql", path: "/06-compare/mysql", label: "MySQL → ClickHouse 实时数仓" },
      { site: "postgresql", path: "/06-compare/postgresql", label: "PG → ClickHouse HTAP" },
      { site: "architecture", path: "/04-olap-scenarios/lambda-kappa", label: "实时数仓架构" }
    ]"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>

## 学习路径建议

| 阶段 | 时长 | 路径 |
|------|------|------|
| 入门 | 1 周 | 01-foundations → 02-column-store |
| 进阶 | 2 周 | 03-table-engine → 04-olap-scenarios |
| 高级 | 2 周 | 05-ecosystem → 06-compare |
