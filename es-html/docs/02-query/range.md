---
title: Range Query
category: query
graphNodeId: range
---

<span class="kg-badge kg-badge-query">查询层</span>

# Range Query

## 📌 一句话定义
Range Query 对**数值 / 日期 / 字符串**字段做范围匹配。

## 🔧 基本用法

```http
POST /products/_search
{
  "query": {
    "range": {
      "price": {
        "gte": 100,
        "lte": 1000
      }
    }
  }
}
```

## 📐 操作符

| 操作符 | 含义 |
|---|---|
| `gt`  | > |
| `gte` | ≥ |
| `lt`  | < |
| `lte` | ≤ |

## 📅 日期范围

```json
{
  "range": {
    "created_at": {
      "gte": "now-7d",
      "lte": "now"
    }
  }
}
```

支持的日期数学表达式：
- `now` / `now+1d` / `now-1h`
- `2026-01-01` / `2026-01-01||+1M` (加 1 月)

## 📊 范围查询的内部实现

- 数值：使用 BKD 树
- 日期：使用 BKD 树
- keyword：使用倒排索引 + 范围扩展（range query 会展开为 term set）

## 🎯 多条件组合

```json
{
  "range": {
    "price": { "gt": 100, "lt": 1000 }
  }
}
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="range" :height="400" />

## 📚 延伸阅读
- [Term Query](/02-query/term)
- [Bool Query](/02-query/bool)
