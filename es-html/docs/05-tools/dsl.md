---
title: Query DSL 速查
---

<span class="kg-badge kg-badge-query">DSL</span>

# Query DSL 速查

> **67 个**常用 ES 7 Query DSL 模板，按 **16 大类** 整理，可直接复制或一键转到 [调试器](/05-tools/curl-client) 预填。

## 📚 分类索引

按 **16 大类** 整理，共 **67 个** Query DSL 模板：

| 分类 | 数量 | 包含 |
|---|---|---|
| 🍃 **叶子查询** | 4 | Term / Terms / Exists / IDs |
| 🎯 **复合查询** | 2 | Bool / Constant Score |
| 🔀 **复合扩展** | 4 | Boosting / Dis Max / More Like This / Percolator |
| 📏 **范围查询** | 2 | Range / Date Range |
| 🔎 **全文检索** | 4 | Match / Match Phrase / Multi Match / Query String |
| 🔤 **模糊与模式** | 6 | Prefix / Wildcard / Fuzzy / Regexp / Match Phrase Prefix / Simple Query String |
| 🌐 **地理空间** | 4 | Geo Bounding Box / Geo Distance / Geo Polygon / Geo Shape |
| 🔗 **Span 查询** | 3 | Span Term / Span Near / Span Or |
| 🔍 **嵌套与连接** | 2 | Nested / Has Child |
| 📊 **聚合分析** | 4 | Terms / Metrics / Sub-Agg / Date Histogram |
| 🔢 **指标聚合** | 7 | Percentiles / Stats / Extended Stats / Cardinality / Value Count / Scripted Metric / Top Hits |
| 📈 **桶聚合** | 5 | Histogram / Range / Geo Distance / IP Range / Missing |
| 🔄 **Pipeline 聚合** | 5 | Derivative / Cumulative Sum / Moving Avg / Bucket Sort / Bucket Selector |
| 🔃 **排序与高亮** | 5 | Sort Multi / Sort Script / Source Filter / Highlight Advanced / Collapse |
| 💡 **联想 Suggest** | 3 | Completion / Term Suggest / Phrase Suggest |
| 🛠️ **排错与高级** | 7 | Profile / Explain / Function Score / Count / Validate / Inner Hits / Script Score |

<EsDslRecipes />

## 🎯 使用建议

### 何时使用哪种查询？

| 场景 | 推荐 |
|---|---|
| 全文搜索 | 🍃 Match / Match Phrase |
| 精确匹配（keyword、数值、状态） | 🍃 Term / Terms |
| 复合条件 | 🎯 Bool（must + filter + should） |
| 数值/日期筛选 | 📏 Range |
| 嵌套数组内筛选 | 🔗 Nested |
| 父查子 | 🔗 Has Child |
| 分类计数、平均值 | 📊 Aggregations |
| 性能剖析 | 🛠️ Profile |

### 性能最佳实践

1. **filter 上下文优于 query**：filter 不参与评分且可缓存
2. **避免高基数字段的 prefix/wildcard**：会展开为大量 term，拖慢搜索
3. **bool/should 单独使用**：默认 `minimum_should_match: 1`，有 must/filter 时默认 0
4. **nested 慢**：每条 nested doc 独立索引，按需使用

## 🔗 关联工具

- **[🚀 调试器](/05-tools/curl-client)** — 一键预填 DSL 并实际发送
- **[☕ Java SDK 速查](/05-tools/java)** — 对应的 Java API 调用
- **[📊 集群仪表板](/05-tools/dashboard)** — 实时观察慢查询对集群的影响

## 🔗 关联文档

- [Query DSL 总览](/02-query/query-dsl)
- [Match Query](/02-query/match)
- [Term Query](/02-query/term)
- [Bool Query](/02-query/bool)
- [Range Query](/02-query/range)
- [聚合 Aggregation](/02-query/aggregation)
- [Query Profile](/02-query/profile)
