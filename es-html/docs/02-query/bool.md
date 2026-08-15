---
title: Bool Query
category: query
graphNodeId: bool
---

<span class="kg-badge kg-badge-query">查询层</span>

# Bool Query

## 📌 一句话定义
Bool Query 用 `must` / `should` / `filter` / `must_not` **组合多个子句**，是 ES 中最核心的查询方式。

## 🧱 四种子句语义

| 子句 | 作用 | 是否评分 | 是否影响匹配 |
|---|---|---|---|
| `must` | 必须满足，**参与评分** | ✅ | ✅ |
| `should` | 应该满足（影响评分） | ✅ | 仅 `should` 时必须满足 |
| `filter` | 必须满足，**不参与评分** | ❌ | ✅（可缓存） |
| `must_not` | **必须不满足** | ❌ | ✅ |

## 🔧 经典示例

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
        { "range": { "price":    { "lte": 1000 } } }
      ],
      "must_not": [
        { "term":  { "status": "discontinued" } }
      ],
      "should": [
        { "term":  { "is_promoted": true } }
      ]
    }
  }
}
```

## 🎯 评分计算规则

```
score = Σ (must 子句评分) + Σ (should 子句评分)
```

`filter` 和 `must_not` **不参与评分**（查询上下文 vs 过滤上下文）。

## 📌 minimum_should_match

```json
{
  "bool": {
    "should": [
      { "match": { "tags": "新品" } },
      { "match": { "tags": "促销" } },
      { "match": { "tags": "推荐" } }
    ],
    "minimum_should_match": 2
  }
}
```

> 当 query 中**只有 should** 子句时，默认 `minimum_should_match: 1`；有 must/filter 时默认 0。

## ⚠️ 性能最佳实践

1. **过滤条件放 filter**：可被 ES 缓存
2. **能确定必选/必排除的不要放 should**
3. **避免过深的 bool 嵌套**（影响优化器）

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="bool" :height="400" />

## 📚 延伸阅读
- [Match Query](/02-query/match)
- [Term Query](/02-query/term)
- [Range Query](/02-query/range)
- [Boost 相关度](/02-query/boost)
