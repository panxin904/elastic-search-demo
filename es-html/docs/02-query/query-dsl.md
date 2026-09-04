---
title: Query DSL
date: 2026-08-15  # date-auto-injected
category: query
graphNodeId: query-dsl
---

<span class="kg-badge kg-badge-query">查询层</span>

# Query DSL

![Es Query Fetch Coord](/es-query-fetch-coord.svg)

## 📌 一句话定义
Query DSL 是 ES 的**基于 JSON 的结构化查询语言**，是所有查询/过滤的表达基础。

## 🧱 DSL 结构层次

```
SearchRequest
├── query       → 决定哪些文档被返回
│   ├── match
│   ├── term
│   ├── bool
│   │   ├── must
│   │   ├── filter
│   │   ├── should
│   │   └── must_not
│   └── ...
├── aggs        → 聚合分析
├── sort        → 排序
├── from / size → 分页
├── highlight   → 高亮
└── _source     → 字段过滤
```

## 🔍 完整示例

```http
POST /products/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "name": "机械键盘" } }
      ],
      "filter": [
        { "term":  { "category": "电脑外设" } },
        { "range": { "price": { "lte": 1000 } } }
      ]
    }
  },
  "sort": [
    { "price": "asc" }
  ],
  "from": 0,
  "size": 10,
  "highlight": {
    "fields": { "name": {} }
  }
}
```

## 📚 Query 上下文 vs Filter 上下文

| 维度 | Query Context | Filter Context |
|---|---|---|
| 目的 | 找匹配 + **计算评分** | 只判断**是否匹配** |
| 性能 | 较慢 | **快**（可缓存） |
| 使用 | `must` / `should` | `filter` / `must_not` |

> 💡 最佳实践：能 filter 就 filter，**过滤不需要评分的条件**。

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="query-dsl" :height="400" />

## 📚 延伸阅读
- [Match Query](/02-query/match)
- [Term Query](/02-query/term)
- [Bool Query](/02-query/bool)
- [Range Query](/02-query/range)
