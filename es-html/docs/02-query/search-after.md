---
title: Search After
date: 2026-08-15  # date-auto-injected
category: query
graphNodeId: search-after
---

<span class="kg-badge kg-badge-query">查询层</span>

# Search After

![Elasticsearch Query DSL 执行流程](/es-query-dsl-execution.svg)

## 📌 一句话定义
Search After 是**基于排序值的无状态深度分页**，是 `from/size` 深度分页的现代替代。

## 🔧 工作原理

每次返回结果时携带排序值，下次请求用此值作为起点。

```
第 1 页: sort=null, size=10  → 返回 sort=[a, b, c] 末条
第 2 页: search_after=[a, b, c]  → 继续往后
第 3 页: search_after=[d, e, f]  → 继续
...
```

## 🔧 完整示例

```http
POST /products/_search
{
  "size": 2,
  "query": { "match_all": {} },
  "sort": [
    { "price": "asc" },
    { "_id":   "asc" }
  ]
}
```

返回：
```json
{
  "hits": {
    "hits": [
      { "_id": "p001", "sort": [100, "p001"] },
      { "_id": "p002", "sort": [200, "p002"] }
    ]
  }
}
```

下一页：
```http
POST /products/_search
{
  "size": 2,
  "query": { "match_all": {} },
  "sort": [
    { "price": "asc" },
    { "_id":   "asc" }
  ],
  "search_after": [200, "p002"]
}
```

## 📌 必须有唯一性 tiebreaker

否则不同文档可能 sort 值相同，**导致分页漏数据**：

```json
"sort": [
  { "created_at": "desc" },
  { "_id": "asc" }     // ← tiebreaker
]
```

## 🆚 与 scroll 对比

| 维度 | scroll | search_after |
|---|---|---|
| 状态 | 维护 context | 无状态 |
| 实时性 | 一致性快照 | 实时（每次新请求） |
| 适用 | 一次性全量导出 | 前端滚动/无限下拉 |
| 资源 | 占用集群内存 | 几乎无开销 |

## 🔗 PIT (Point In Time) + Search After

ES 7.10+ 推荐用 PIT 保护一致性：

```http
POST /products/_pit?keep_alive=1m
```

返回 `id`，搜索时传入 `pit.id` 替代 `index`。

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="search-after" :height="400" />

## 📚 延伸阅读
- [分页](/02-query/pagination)
- [排序](/02-query/sort)
