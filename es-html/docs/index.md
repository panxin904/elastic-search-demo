---
layout: home
title: ES Knowledge Atlas
hero:
  name: "ES Knowledge Atlas"
  text: "用知识图谱方式系统化学习 Elasticsearch"
  tagline: "按 ES 架构四层组织 · 51 个核心节点 · 可交互式图谱导航"
  actions:
    - theme: brand
      text: 开始学习
      link: /01-storage/overview
    - theme: alt
      text: 查看完整图谱
      link: "#complete-graph"
    - theme: alt
      text: 7 vs 8
      link: /99-compare/diff

features:
  - title: 🗄️ 存储层
    details: 集群、节点、索引、文档、分片、副本、段、Mapping、字段类型、_source、Translog、Refresh 等 12 个核心概念
    link: /01-storage/overview
    linkText: 查看存储层 →
  - title: 🔍 查询层
    details: Query DSL、Match、Term、Bool、Range、Boost、分页、排序、高亮、聚合、Script、Search After 等 16 个查询机制
    link: /02-query/overview
    linkText: 查看查询层 →
  - title: 🧪 分析层
    details: Analyzer、Tokenizer、Token Filter、Char Filter、IK、pinyin、倒排索引、BM25、Explain 等 11 个文本分析机制
    link: /03-analysis/overview
    linkText: 查看分析层 →
  - title: ⚙️ 运维层
    details: 安装、JVM 调优、分片分配、集群健康、Snapshot、ILM、Curator、Cerebro、慢日志、索引模板、别名 等 12 个运维主题
    link: /04-ops/overview
    linkText: 查看运维层 →
---


<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>

<script setup>
// WhyThisGraph 数据从 frontmatter 读不到（YAML 数组太复杂），放这里
const painPoints = [
  "倒排索引原理（分词 / 词典 / Posting List）讲不清？",
  "ES 集群架构（Master / Data / Coordinating 节点）怎么设计？",
  "Mapping / Analyzer / 分词器怎么配置才高效？",
  "查询性能调优（Query DSL / Profile / 慢查询）？",
  "ES vs ClickHouse vs Solr 选哪个？"
]
const goals = [
  "ES 基础（倒排索引 / 集群架构 / 分片副本）",
  "Mapping + Analyzer + 分词器",
  "Query DSL 深度（Match / Term / Bool / Aggregation）",
  "集群运维（Master 选举 / 脑裂 / 快照恢复）",
  "性能调优（Profile / 慢查询 / JVM / 磁盘）",
  "生态集成（Logstash / Beats / Kibana / Filebeat）"
]
const relatedSites = [
  { site: "clickhouse", path: "/01-storage/index-design", label: "CH 索引对比" },
  { site: "mysql", path: "/03-index", label: "MySQL 索引" },
  { site: "observability", path: "/02-logs/es", label: "ES 日志存储" },
  { site: "bigdata", path: "/06-warehouse/overview", label: "数仓架构" },
  { site: "devops", path: "/05-cicd-observability/sre", label: "SRE 实践" }
]
</script>

## 🗺️ 完整知识图谱 {#complete-graph}

> 💡 鼠标拖拽节点、滚轮缩放、**点击节点跳转到对应文档**。点击顶部图例可切换层级显隐。

<KnowledgeGraph mode="full" :height="700" />

## 📊 站点统计

<div class="kg-stats">
  <div class="kg-stat">
    <div class="kg-stat-num">51</div>
    <div class="kg-stat-label">核心概念节点</div>
  </div>
  <div class="kg-stat">
    <div class="kg-stat-num">65</div>
    <div class="kg-stat-label">关系边</div>
  </div>
  <div class="kg-stat">
    <div class="kg-stat-num">4</div>
    <div class="kg-stat-label">架构层次</div>
  </div>
  <div class="kg-stat">
    <div class="kg-stat-num">50+</div>
    <div class="kg-stat-label">深度文档</div>
  </div>
</div>

## 🎯 学习路径建议

### 🌱 入门路径 (1-2 天)

1. [集群 Cluster](/01-storage/cluster) → [节点 Node](/01-storage/node) → [索引 Index](/01-storage/index)
2. [文档 Document](/01-storage/document) → [映射 Mapping](/01-storage/mapping)
3. [Match Query](/02-query/match) → [Term Query](/02-query/term) → [Bool Query](/02-query/bool)
4. [安装部署](/04-ops/installation) → [集群健康](/04-ops/cluster-health)

### 🚀 进阶路径 (3-5 天)

- 存储层：[分片 Shard](/01-storage/shard) → [副本 Replica](/01-storage/replica) → [段 Segment](/01-storage/segment) → [Refresh](/01-storage/refresh) → [Translog](/01-storage/translog)
- 查询层：[聚合 Aggregation](/02-query/aggregation) → [分页](/02-query/pagination) → [Sort](/02-query/sort) → [Highlight](/02-query/highlight) → [Query Profile](/02-query/profile)
- 分析层：[Analyzer](/03-analysis/analyzer) → [IK 分词器](/03-analysis/ik-analyzer) → [倒排索引](/03-analysis/inverted-index) → [BM25](/03-analysis/bm25)

### 🏆 高级路径 (1-2 周)

- [JVM 调优](/04-ops/jvm-tuning) + [分片分配](/04-ops/shard-allocation)
- [ILM 生命周期](/04-ops/ilm) + [Snapshot 备份](/04-ops/snapshot)
- [索引模板](/04-ops/index-template) + [别名 Alias](/04-ops/alias)
- [自定义分词](/03-analysis/custom-analyzer) + 同义词
- [Script Query](/02-query/script) + [Search After](/02-query/search-after)

## 🔗 关联项目

本站点配套 [elastic-search-demo](https://github.com/your-repo) Java 项目，所有代码示例均与本项目 [`ElasticsearchService.java`](https://github.com/your-repo/blob/main/src/main/java/com/example/esdemo/service/ElasticsearchService.java) 中的 Java API 对应。

## 📖 推荐资源

- 📘 [Elasticsearch 7.17 官方文档](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/index.html)
- 🎓 [Elastic 官方培训](https://www.elastic.co/training/)
- 📚 [Elasticsearch 权威指南](https://www.elastic.co/guide/en/elasticsearch/guide/current/index.html)
- 🔬 [Lucene 官方文档](https://lucene.apache.org/core/)

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [mysql](https://java-px.bot.cd/mysql/)：MySQL 全文索引对比
- [clickhouse](https://java-px.bot.cd/clickhouse/)：ClickHouse OLAP 对比
- [bigdata](https://java-px.bot.cd/bigdata/)：大数据生态
- [system-design](https://java-px.bot.cd/system-design/)：搜索引擎架构
- [java](https://java-px.bot.cd/java-web-manual/)：Java ES Client
- [observability](https://java-px.bot.cd/observability/)：ES 集群监控
