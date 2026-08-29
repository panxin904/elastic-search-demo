---
title: Boost 相关度
date: 2026-08-15  # date-auto-injected
category: query
graphNodeId: boost
---

<span class="kg-badge kg-badge-query">查询层</span>

# Boost 相关度

## 📌 一句话定义
Boost 调整某个查询子句的**评分权重**，从而**影响结果排序**。

## 🔧 字段级 boost

```http
POST /products/_search
{
  "query": {
    "multi_match": {
      "query": "机械键盘",
      "fields": ["name^3", "description^1", "tags^2"]
    }
  }
}
```

`name^3` 表示 `name` 字段命中权重是 `description` 的 **3 倍**。

## 🔧 子句级 boost

```http
POST /products/_search
{
  "query": {
    "bool": {
      "should": [
        { "term": { "is_promoted": { "value": true, "boost": 5.0 } } },
        { "match": { "name": "机械键盘" } }
      ]
    }
  }
}
```

## ⚠️ Boost 不是过滤器

Boost **只影响评分**，**不决定文档是否匹配**。要让某条件必须满足，用 `must`/`filter`；想提升权重用 `should` + boost。

## 🎯 使用场景

| 场景 | Boost 策略 |
|---|---|
| 标题比正文重要 | `title^3, content^1` |
| 标签命中加分 | `tags^2` |
| 新品加权 | `created_at` 衰减函数 |
| 促销商品加权 | `is_promoted: boost: 5` |

## 🔗 替代方案：function_score

更复杂的权重逻辑（按时间衰减、按销量加权等）使用 [`function_score` 查询](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/query-dsl-function-score-query.html)。

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="boost" :height="400" />

## 📚 延伸阅读
- [Match Query](/02-query/match)
- [Bool Query](/02-query/bool)
- [BM25 相关度](/03-analysis/bm25)
