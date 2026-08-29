---
title: 学习路径
date: 2026-08-29  # date-auto-injected
---

# 📖 ES 学习路径

> 根据你的角色选择对应路径，每条路径推荐了核心阅读顺序。

## 🌱 入门路径（1-2 天）

适合**刚接触 ES**的初学者。

1. [❓ ES 是什么](/01-storage/overview) - 5 分钟了解 ES 核心概念
2. [📥 安装部署](/04-ops/installation) - 单机/集群 Docker/Tar 部署
3. [🏗️ 集群架构](/01-storage/cluster) - Master/Data/Coordinating 节点
4. [📝 索引文档](/01-storage/document) - 基本 CRUD 操作
5. [🔍 Match Query](/02-query/match) - 第一个查询
6. [📋 速查表](/cheatsheet) - 高频命令速查

## 🚀 进阶路径（3-5 天）

适合**已经会用 ES 基础**的开发者。

- **存储层**：[分片 Shard](/01-storage/shard) → [副本 Replica](/01-storage/replica) → [段 Segment](/01-storage/segment) → [Refresh](/01-storage/refresh) → [Translog](/01-storage/translog)
- **查询层**：[Bool Query](/02-query/bool) → [Aggregation](/02-query/aggregation) → [分页](/02-query/pagination) → [Sort](/02-query/sort) → [Highlight](/02-query/highlight)
- **分析层**：[Analyzer](/03-analysis/analyzer) → [IK 分词器](/03-analysis/ik-analyzer) → [倒排索引](/03-analysis/inverted-index) → [BM25](/03-analysis/bm25)
- **实战**：[Query Profile](/02-query/profile) + [慢日志](/04-ops/slow-log)

## 🏆 高级路径（1-2 周）

适合**要落地生产 ES 集群**的工程师。

- **性能**：[JVM 调优](/04-ops/jvm-tuning) + [分片分配](/04-ops/shard-allocation) + [Query Profile](/02-query/profile)
- **可靠性**：[ILM 生命周期](/04-ops/ilm) + [Snapshot 备份](/04-ops/snapshot) + [别名切换](/04-ops/alias)
- **可维护**：[索引模板](/04-ops/index-template) + [自定义分词](/03-analysis/custom-analyzer) + 同义词
- **进阶查询**：[Script Query](/02-query/script) + [Search After](/02-query/search-after) + [跨索引查询](/02-query/multi-search)
- **生态集成**：Logstash / Beats / Kibana / Filebeat

## 🔬 对比选型路径

适合**做技术选型**的架构师。

- [ES vs ClickHouse vs Solr](/99-compare/diff) - 搜索引擎选型
- [CH 索引设计对比](https://java-px.bot.cd/clickhouse/01-storage/index-design) - 列存 vs 倒排
- [MySQL 全文索引对比](https://java-px.bot.cd/mysql/03-index) - 关系库 vs ES
- [SRE 实践](https://java-px.bot.cd/devops/05-cicd-observability/sre) - 生产监控体系
