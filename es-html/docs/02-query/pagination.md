---
title: 分页
category: query
graphNodeId: pagination
---

<span class="kg-badge kg-badge-query">查询层</span>

# 分页 Pagination

ES 提供 **三种分页方式**，适用不同场景。

## 1️⃣ from / size (浅分页)

```http
POST /products/_search
{
  "from": 0,
  "size": 10
}
```

| 维度 | 说明 |
|---|---|
| 原理 | 每个分片返回 `from + size` 条，**协调节点聚合后丢弃**前 `from` 条 |
| 性能 | 随 from 增大而**线性下降** |
| 适用 | from + size < 10000 |

> ⚠️ `index.max_result_window` 默认 10000，超出会报错。

## 2️⃣ search_after (无状态深度分页)

```http
POST /products/_search
{
  "size": 10,
  "query": { "match_all": {} },
  "sort": [
    { "price": "asc" },
    { "_id":   "asc" }
  ]
}
```

第一次返回：
```json
{ "hits": { "hits": [...], "sort": [599, "p001"] } }
```

下一次：
```http
{
  "size": 10,
  "search_after": [599, "p001"],
  "sort": [
    { "price": "asc" },
    { "_id":   "asc" }
  ]
}
```

| 维度 | 说明 |
|---|---|
| 状态 | **无状态**（不依赖 scroll context） |
| 性能 | 与翻页深度**无关**，稳定 |
| 局限 | **不可跳页**，只能向后/向前逐页 |

## 3️⃣ scroll (已废弃，推荐 PIT + search_after)

```http
POST /products/_search?scroll=1m
{ "size": 1000, "query": { "match_all": {} } }
```

```http
POST /_search/scroll
{
  "scroll": "1m",
  "scroll_id": "..."
}
```

| 维度 | 说明 |
|---|---|
| 用途 | 一次性大批量导出（reindex） |
| 缺点 | 维护 scroll context 占内存，**不可实时** |

> ES 7.10+ 引入 **PIT (Point In Time)** 配合 `search_after` 作为 scroll 的现代替代。

## 📊 选型建议

| 场景 | 推荐方式 |
|---|---|
| 常规前端分页 | `from/size` |
| 滚动加载 / 无限下拉 | `search_after` |
| 全量数据导出 | `PIT + search_after` 或 reindex API |

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="pagination" :height="400" />

## 📚 延伸阅读
- [Search After](/02-query/search-after)
- [排序 Sort](/02-query/sort)
