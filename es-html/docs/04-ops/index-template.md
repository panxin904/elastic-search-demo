---
title: 索引模板
date: 2026-08-15  # date-auto-injected
category: ops
graphNodeId: index-template
---

<span class="kg-badge kg-badge-ops">运维层</span>

# 索引模板 Index Template

## 📌 一句话定义
索引模板在**新索引创建时**自动套用预设的 settings、mappings、aliases，避免重复配置。

## 🔧 组件模板 (Component Template) - 7.8+

```http
PUT /_component_template/products_settings
{
  "template": {
    "settings": {
      "number_of_shards":   3,
      "number_of_replicas": 1
    }
  }
}

PUT /_component_template/products_mappings
{
  "template": {
    "mappings": {
      "properties": {
        "name":     { "type": "text" },
        "category": { "type": "keyword" },
        "price":    { "type": "double" }
      }
    }
  }
}
```

## 🔧 索引模板 (Index Template)

```http
PUT /_index_template/products_template
{
  "index_patterns": ["products-*"],
  "priority": 100,
  "composed_of": ["products_settings", "products_mappings"],
  "template": {
    "aliases": {
      "products": {}
    }
  }
}
```

之后创建 `products-2026-07-13` 会**自动应用**上述配置。

## 🎯 模板优先级

| 字段 | 说明 |
|---|---|
| `priority` | 数字越大越优先 |
| `composed_of` | 多个组件模板组合 |
| 合并规则 | 后定义覆盖先定义 |

```bash
# 查看匹配的模板
GET /products-2026/_index_template
```

## 🔧 旧版模板 (legacy templates)

ES 7.x 仍支持两种旧模板：
- `PUT /_template/<name>` （模板）
- `PUT /_index_template/<name>` （索引模板）

> 💡 **新项目推荐使用 Composable Index Template**（上面示例）

## 📌 模板版本管理

```http
PUT /_index_template/products_template
{
  "index_patterns": ["products-*"],
  "version": 2,        // 显式版本号
  "_meta": {
    "description": "Products index template v2"
  },
  ...
}
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="index-template" :height="400" />

## 📚 延伸阅读
- [别名 Alias](/04-ops/alias)
- [ILM 生命周期](/04-ops/ilm)
- [映射 Mapping](/01-storage/mapping)
