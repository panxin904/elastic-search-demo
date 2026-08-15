---
title: _source 元数据
category: storage
graphNodeId: source
---

<span class="kg-badge kg-badge-storage">存储层</span>

# _source 元数据

## 📌 一句话定义
`_source` 字段存储文档的**原始 JSON 原文**，是 ES 返回、更新、reindex 的数据源。

## 🔧 启用与禁用

```http
PUT /products
{
  "mappings": {
    "_source": { "enabled": true }
  }
}
```

| 配置 | 影响 |
|---|---|
| `enabled: true`（默认） | 存储原始 JSON，update/reindex 可用 |
| `enabled: false` | 不存储，**Get/Update 不可用**，仅能通过搜索字段重建 |

## 🎯 _source 部分包含

```http
PUT /products
{
  "mappings": {
    "_source": {
      "includes": [ "name", "price" ],
      "excludes": [ "description" ]
    }
  }
}
```

## 🔍 获取时过滤

```http
GET /products/_doc/p001?_source_includes=name,price&_source_excludes=description
```

## 🔄 更新依赖 _source

```http
POST /products/_update/p001
{
  "doc": {
    "price": 549
  }
}
```

- **有 _source**：增量更新（合并）
- **无 _source**：必须全量替换或 `_update_by_query`

## ⚠️ 关闭 _source 的代价

| 操作 | 关闭后影响 |
|---|---|
| Get by ID | ❌ 不可用 |
| Update by ID | ❌ 不可用 |
| Reindex | ❌ 不可用（除非 reindex API + stored fields） |
| Search | ✅ 仍可用（仅返回 indexed fields） |

> 💡 **建议**：除非磁盘极度紧张，否则保留 `_source`。

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="source" :height="400" />

## 📚 延伸阅读
- [文档 Document](/01-storage/document)
- [映射 Mapping](/01-storage/mapping)
