---
title: 映射 Mapping
category: storage
graphNodeId: mapping
---

<span class="kg-badge kg-badge-storage">存储层</span>

# 映射 Mapping

## 📌 一句话定义
Mapping 定义了**索引中文档的字段类型与结构**，是 ES 的"schema"。

## 🔧 显式 Mapping

```http
PUT /products
{
  "mappings": {
    "properties": {
      "name":        { "type": "text",    "analyzer": "ik_max_word" },
      "category":    { "type": "keyword" },
      "price":       { "type": "double" },
      "created_at":  { "type": "date" },
      "tags":        { "type": "keyword" },
      "location":    { "type": "geo_point" }
    }
  }
}
```

## 🔄 动态 Mapping

未预先定义的字段写入时 ES 自动推断类型：

```bash
# 关闭动态 mapping（严格模式）
PUT /products
{
  "mappings": {
    "dynamic": "strict"
  }
}
```

| `dynamic` 值 | 行为 |
|---|---|
| `true`（默认） | 自动添加字段 |
| `false` | 存储字段但**不索引**（不可搜） |
| `strict` | 未知字段写入**报错** |

## 📌 常用 Mapping 参数

| 参数 | 作用 |
|---|---|
| `index` | true（默认）/ false（仅存储不索引） |
| `analyzer` | 指定分词器 |
| `format` | 日期格式，如 `yyyy-MM-dd HH:mm:ss` |
| `fields` | multi-field，同字段不同类型索引 |

### Multi-field 示例

```json
{
  "name": {
    "type": "text",
    "fields": {
      "keyword": { "type": "keyword", "ignore_above": 256 }
    }
  }
}
```

这样 `name` 既可全文搜索也可精确聚合（`name.keyword`）。

## 🔍 查看已有 Mapping

```http
GET /products/_mapping
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="mapping" :height="400" />

## 📚 延伸阅读
- [字段类型](/01-storage/field-types)
- [Analyzer 分析器](/03-analysis/analyzer)
- [索引模板](/04-ops/index-template)
