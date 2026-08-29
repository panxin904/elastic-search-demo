---
title: 别名 Alias
date: 2026-08-15  # date-auto-injected
category: ops
graphNodeId: alias
---

<span class="kg-badge kg-badge-ops">运维层</span>

# 别名 Alias

## 📌 一句话定义
Alias 是**索引的逻辑名**，一个别名可指向一个或多个物理索引，**支持零停机切换**。

## 🔧 创建别名

```http
POST /_aliases
{
  "actions": [
    { "add": { "index": "products-v1", "alias": "products" } }
  ]
}
```

之后**所有读写都通过 `products`**：
- `GET /products/_search`
- `POST /products/_doc/p001`

## 🔄 零停机索引切换

```http
# 1. 创建新索引
PUT /products-v2
{ ... 同 settings/mapping ... }

# 2. reindex 老数据
POST /_reindex
{
  "source": { "index": "products-v1" },
  "dest":   { "index": "products-v2" }
}

# 3. 原子切换别名（应用层无感知）
POST /_aliases
{
  "actions": [
    { "remove": { "index": "products-v1", "alias": "products" } },
    { "add":    { "index": "products-v2", "alias": "products" } }
  ]
}

# 4. 删除老索引
DELETE /products-v1
```

## 📊 多别名多角色

| 别名 | 指向 | 用途 |
|---|---|---|
| `products` | 当前版本 | 读写 |
| `products_read` | 当前版本 | 只读副本 |
| `products_search` | 多个历史版本 | 跨版本搜索 |

## 🔍 别名查询

```bash
GET /_alias/products                # 哪些索引包含此别名
GET /products-v1/_alias             # 此索引的所有别名
```

## 🎯 过滤别名 (Filtered Alias)

```http
POST /_aliases
{
  "actions": [
    {
      "add": {
        "index": "orders",
        "alias": "recent_orders",
        "filter": { "range": { "created_at": { "gte": "now-30d" } } }
      }
    }
  ]
}
```

这样查 `recent_orders` 自动只返回近 30 天数据。

## 📦 写别名 (Write Index)

```http
POST /_aliases
{
  "actions": [
    {
      "add": {
        "index": "products-v2",
        "alias": "products",
        "is_write_index": true
      }
    }
  ]
}
```

> 用于 rollover 场景：所有写入只发到 `is_write_index: true` 的索引，读取可跨多个。

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="alias" :height="400" />

## 📚 延伸阅读
- [索引模板](/04-ops/index-template)
- [ILM 生命周期](/04-ops/ilm)
