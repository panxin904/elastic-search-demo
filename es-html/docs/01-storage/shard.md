---
title: 分片 Shard
date: 2026-08-15  # date-auto-injected
category: storage
graphNodeId: shard
---

<span class="kg-badge kg-badge-storage">存储层</span>

# 分片 Shard

![Elasticsearch Query Shard 路由](/es-query-shard-routing.svg)

## 📌 一句话定义
分片是 ES 索引数据的**物理切分单位**，每个分片本质上是一个**独立的 Lucene 索引**。

## 🎯 为什么需要分片？

- **水平扩展**：突破单机容量上限
- **并行处理**：查询/写入分散到多个分片
- **故障隔离**：单分片故障不影响整体

## 🔧 分片配置

```json
PUT /products
{
  "settings": {
    "number_of_shards": 3,        // 主分片数（创建后不可改！）
    "number_of_replicas": 1       // 副本数（可动态调整）
  }
}
```

> ⚠️ `number_of_shards` **创建后不可修改**。如需调整，使用 [`_shrink` API](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/indices-shrink-index.html) 或 reindex 到新索引。

## 📊 分片内部结构

```
Index: products (3 shards)
├── Shard 0 (Primary)
│   ├── Segment 0
│   ├── Segment 1
│   └── Segment 2
├── Shard 1 (Primary)
└── Shard 2 (Primary)
    └── Segment ...
```

## 🧮 分片数估算

**经验公式**：

```
推荐分片大小: 10-50 GB
推荐 JVM 堆: ≤ 32 GB
单分片文档数: < 2亿
```

**生产示例**：1TB 数据 → 约 20-30 个分片

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="shard" :height="400" />

## 📚 延伸阅读
- [副本 Replica](/01-storage/replica)
- [段 Segment](/01-storage/segment)
- [分片分配](/04-ops/shard-allocation)

<!-- svg-injected:do-not-edit -->

## 图示：ES 分片路由公式与副本拓扑

![ES 分片路由公式与副本拓扑](/es-shard-routing-detail.svg)
