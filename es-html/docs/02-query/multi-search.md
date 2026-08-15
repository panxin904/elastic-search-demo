---
title: Multi Search
category: query
graphNodeId: multi-search
---

<span class="kg-badge kg-badge-query">查询层</span>

# Multi Search API

## 📌 一句话定义
Multi Search 允许**单次 HTTP 请求**执行**多个搜索**，减少网络开销。

## 🔧 基本用法

```http
POST /_msearch
{"index":"products"}
{"query":{"match":{"name":"键盘"}}, "size": 5}
{"index":"products"}
{"query":{"term":{"category":"电脑外设"}}, "size": 5}
{"index":"products"}
{"query":{"range":{"price":{"gt":500}}}}
```

格式：每两行一组
- 第 1 行: 元数据（可选 index）
- 第 2 行: query body

## 📦 响应

```json
{
  "responses": [
    { "took": 5, "hits": { ... } },
    { "took": 3, "hits": { ... } },
    { "took": 2, "hits": { ... } }
  ]
}
```

每个响应**独立**，某个失败不影响其他。

## 🎯 使用场景

| 场景 | 说明 |
|---|---|
| 仪表盘多面板 | 一次请求返回多个聚合 |
| 同一页面多个搜索 | 减少前端多次请求 |
| 跨索引并行查询 | 减少网络往返 |

## ⚙️ 模板搜索 (Search Template)

```http
POST /_scripts/<template-id>
{
  "script": {
    "lang": "mustache",
    "source": {
      "query": { "match": { "name": "{{q}}" } }
    }
  }
}
```

```http
POST /products/_search/template
{
  "id": "<template-id>",
  "params": { "q": "机械键盘" }
}
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="multi-search" :height="400" />

## 📚 延伸阅读
- [Query DSL](/02-query/query-dsl)
