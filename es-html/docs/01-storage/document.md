---
title: 文档 Document
date: 2026-08-15  # date-auto-injected
category: storage
graphNodeId: document
---

<span class="kg-badge kg-badge-storage">存储层</span>

# 文档 Document

## 📌 一句话定义
文档是 ES 中可被索引和搜索的**最小数据单元**，本质是一个 **JSON 对象**。

## 📦 文档结构示例

```json
{
  "id": "p001",
  "name": "机械键盘",
  "description": "RGB 背光 红轴",
  "price": 599.0,
  "category": "电脑外设",
  "stock": 120
}
```

## 🔧 文档操作

### 索引（写入）文档

```http
POST /products/_doc/p001
{
  "name": "机械键盘",
  "price": 599.0,
  "category": "电脑外设"
}
```

> 指定 `_doc/p001` 中的 `p001` 即为文档 ID；不指定则 ES 自动生成。

### 获取文档

```http
GET /products/_doc/p001
```

### 更新文档

```http
POST /products/_update/p001
{
  "doc": { "price": 549.0 }
}
```

### 删除文档

```http
DELETE /products/_doc/p001
```

## 🔗 对应源码

本项目 [`ElasticsearchService#indexProduct`](https://github.com/your-repo)：

```java
public String indexProduct(String indexName, Product product) throws IOException {
    IndexRequest<Product> request = IndexRequest.of(i -> i
        .index(indexName)
        .id(product.getId())
        .document(product)
    );
    IndexResponse response = client.index(request);
    return response.id();
}
```

## 📐 文档 vs 关系数据库

| 维度 | RDB 行 | ES 文档 |
|---|---|---|
| 数据格式 | 行列严格 | 嵌套 JSON，可灵活扩展 |
| Schema | 强 Schema | 动态 Mapping |
| 主键 | 主键列 | `_id` 字段 |
| 一致性 | 强一致 | 最终一致（准实时） |

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="document" :height="400" />

## 📚 延伸阅读
- [索引 Index](/01-storage/index)
- [映射 Mapping](/01-storage/mapping)
- [_source 元数据](/01-storage/source)
