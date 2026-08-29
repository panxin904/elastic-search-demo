---
title: 使用场景与最佳实践
date: 2026-08-15  # date-auto-injected
---

<span class="kg-badge kg-badge-ops">Scenarios</span>

# 使用场景与最佳实践

> 按 **业务场景** 组织的 ES 落地方案。覆盖 **8 个企业级场景**：日志分析 / 全文搜索 / 时序监控 / 电商搜索 / 向量 RAG / 地理位置 / 安全审计 / 实时报表。
>
> 每个场景含典型用例、数据特征、关键 Mapping、索引设计、典型查询、常见陷阱与最佳实践。点开折叠详情查看完整代码与可关联的 Java SDK 代码片段。

<EsScenarios />

## 🎯 如何选择场景？

| 你的业务 | 推荐场景 |
|---|---|
| 聚合 Nginx / App / Syslog 做检索 + 告警 | 📋 [日志分析](#日志分析elk-经典栈) |
| 站内文章 / 文档搜索（中文） | 🔍 [全文搜索](#全文搜索文档文章搜索) |
| APM / IoT / 业务指标采集 | 📈 [时序数据/监控指标](#时序数据监控指标) |
| 电商商品多条件筛选 + 排序 + 分面 | 🛒 [电商商品搜索](#电商商品搜索) |
| RAG / 知识库 / 语义搜索 / 以文搜图 | 🤖 [向量搜索/RAG](#向量搜索ragai-时代重点) |
| 附近门店 / 配送范围 / 外卖 | 🌍 [地理位置搜索](#地理位置搜索) |
| 金融交易 / 等保 / SOX 合规 | 🔒 [安全审计/合规](#安全审计合规) |
| GMV 大屏 / 漏斗 / 留存 / AB 测试 | 📊 [实时报表/BI 分析](#实时报表bi-分析) |

## 📚 通用设计原则

不论哪种场景，以下原则都适用：

1. **Mapping 先行**：业务代码不直接 PUT 索引，用 index template 统一管理
2. **别名读写分离**：物理索引滚动（`logs-2025.07.16`），写入别名指向最新（`logs-write`），读取别名覆盖全量
3. **ILM 分层**：热/温/冷/冻四层数据节点，配合 rollover 自动滚动
4. **副本按数据定**：日志/时序 1 副本足够，审计/交易 2 副本
5. **禁用 deep paging**：`from + size` 超过 10000 必须用 `search_after` 或 `PIT`
6. **定期 snapshot**：跨集群 / 跨地域备份，保留期独立于 ES

## 🔗 关联工具

- **[☕ Java SDK 速查](/05-tools/java)** — 每个场景关联的完整 Java 代码（含 RHLC ↔ New Client 切换）
- **[📚 DSL 速查](/05-tools/dsl)** — Mapping / Query DSL 一一对应
- **[🚀 调试器](/05-tools/curl-client)** — 看到 DSL 后实际验证再写 Java
- **[📊 集群仪表板](/05-tools/dashboard)** — 用 health 接口验证集群可用

## 🔗 关联文档

- [ES 官方文档 - Use Cases](https://www.elastic.co/guide/en/elasticsearch/reference/current/use-cases.html)
- [ILM 索引生命周期管理](/04-ops/ilm)
- [Mapping 设计](/01-storage/mapping)
- [Search DSL](../02-query)