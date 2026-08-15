---
title: 查询层 总览
---

# 查询层 Query

查询层是 ES 的"用户界面"，涉及**如何向 ES 表达需求、获取结果、控制相关性**。

## 🔍 查询结构

```json
{
  "query":    { ... },   // 过滤与评分
  "sort":     [ ... ],   // 排序
  "from/size": 0, 10,    // 分页
  "_source":  [ ... ],   // 字段过滤
  "aggs":     { ... },   // 聚合分析
  "highlight":{ ... }    // 高亮
}
```

## 🎯 Query 子句类型

| 子句 | 作用 | 是否评分 |
|---|---|---|
| [Match](/02-query/match) | 分词后匹配 | ✅ |
| [Term](/02-query/term) | 精确匹配 | ✅ |
| [Bool](/02-query/bool) | 组合多个子句 | 取决于子句 |
| [Range](/02-query/range) | 范围匹配 | ✅ |
| Match All / Match None | 全匹配/无匹配 | - |

## 🛠️ 结果控制

| 能力 | 说明 |
|---|---|
| [Boost](/02-query/boost) | 提升相关性 |
| [Sort](/02-query/sort) | 自定义排序 |
| [Pagination](/02-query/pagination) | from/size + search_after |
| [Highlight](/02-query/highlight) | 高亮关键字 |
| [Aggregation](/02-query/aggregation) | 聚合分析 |

## 🔬 性能与调试

| 工具 | 用途 |
|---|---|
| [Script Query](/02-query/script) | Painless 脚本 |
| [Multi Search](/02-query/multi-search) | 批量查询 |
| [Search After](/02-query/search-after) | 深度分页 |
| [Query Rewrite](/02-query/rewrite) | 查询重写阶段 |
| [Query Profile](/02-query/profile) | 查询剖析 |

## 🗺️ 本层在图谱中的位置

<KnowledgeGraph mode="full" :height="500" />

## 🔗 关联项目源码

本项目 [`ElasticsearchService#searchProductsByName`](https://github.com/your-repo) 使用了 `match` 查询：

```java
SearchRequest.of(s -> s
    .index(indexName)
    .query(q -> q.match(m -> m.field("name").query(nameQuery)))
);
```
