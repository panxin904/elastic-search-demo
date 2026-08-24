---
title: 排序
category: query
graphNodeId: sort
---

<span class="kg-badge kg-badge-query">查询层</span>

# 排序 Sort

ES 默认按 **`_score` 降序**排序，可自定义。

## 🔧 字段排序

```http
POST /products/_search
{
  "query": { "match_all": {} },
  "sort": [
    { "price": "asc" },
    { "created_at": "desc" }
  ]
}
```

> 💡 排序会**禁用评分计算**（除非显式保留 `_score`）。

## 🎯 多字段 + tiebreaker

```json
{
  "sort": [
    { "price":   { "order": "asc" } },
    { "_id":     { "order": "asc" } }    // 唯一 tiebreaker
  ]
}
```

`search_after` 必须有**唯一性 tiebreaker**（推荐 `_id` 或带 doc_value 的字段）。

## 🔧 按数组字段排序 (mode)

```json
{
  "sort": [
    { "ratings": { "order": "desc", "mode": "avg" } }
  ]
}
```

| mode | 行为 |
|---|---|
| `min` / `max` | 取最小/最大 |
| `sum` / `avg` | 求和/平均 |
| `median` | 中位数 |

## 🔧 缺失值处理 (missing)

```json
{
  "sort": [
    { "discount": { "order": "asc", "missing": "_last" } }
  ]
}
```

| missing | 行为 |
|---|---|
| `_last`（默认） | 缺失值排最后 |
| `_first` | 排最前 |
| 具体值 | 用该值替代 |

## 📊 按 _score 排序

```json
{
  "sort": [
    "_score",
    { "created_at": "desc" }
  ]
}
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="sort" :height="400" />

## 📚 延伸阅读
- [分页](/02-query/pagination)
- [Search After](/02-query/search-after)
## 🎯 实战建议

- `_score` 排排序 + relevance 时考虑 tie_breaker（多字段综合评分）
- 字符串排序用 `keyword` 字段（`text` 字段无法直接排序）
- 大结果集排序用 search_after（游标分页，比 from/size 深翻页性能好）
- 多字段排序用 `_score` + 业务字段组合，确保稳定性
