---
title: 索引 Index
date: 2026-08-15  # date-auto-injected
category: storage
graphNodeId: index
---

<span class="kg-badge kg-badge-storage">存储层</span>

# 索引 Index

## 📌 一句话定义
索引是具有**相似特征文档**的集合，是 ES 中读写数据的**最顶层组织单位**。

> 💡 类比关系数据库：**Index ≈ Database**，**Document ≈ Row**，**Mapping ≈ Schema**

## 🔧 创建索引

```http
PUT /products
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "name": { "type": "text" },
      "price": { "type": "double" },
      "category": { "type": "keyword" }
    }
  }
}
```

## 🔗 对应源码

本项目 [ElasticsearchService.java#createIndex](https://github.com/your-repo) 中演示了基础创建逻辑：

```java
public boolean createIndex(String indexName) throws IOException {
    boolean exists = client.indices().exists(...).value();
    if (exists) return false;
    CreateIndexResponse response = client.indices().create(c -> c.index(indexName));
    return response.acknowledged();
}
```

## 📋 索引操作

| 操作 | API | 说明 |
|---|---|---|
| 创建 | `PUT /index` | 显式创建（也可隐式） |
| 删除 | `DELETE /index` | 谨慎使用 |
| 查看 | `GET /index` | 返回 settings + mappings |
| 打开/关闭 | `POST /index/_open` | 关闭后不可读写，但保留数据 |
| 收缩 | `POST /index/_shrink` | 减少主分片数 |

## 🎯 索引命名规范
- 仅小写字母
- 不能包含 `, /, *, ?, ", <, >, |`, 空格
- 不推荐以 `-`、`_`、`+` 开头
- 不能超过 255 字节

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="index" :height="400" />

## 📚 延伸阅读
- [映射 Mapping](/01-storage/mapping)
- [分片 Shard](/01-storage/shard)
- [索引模板](/04-ops/index-template)
- [别名 Alias](/04-ops/alias)
