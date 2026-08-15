---
title: 副本 Replica
category: storage
graphNodeId: replica
---

<span class="kg-badge kg-badge-storage">存储层</span>

# 副本 Replica

## 📌 一句话定义
副本是主分片的**完整拷贝**，提供**高可用**与**读吞吐扩展**。

## 🎯 副本的两大作用

| 作用 | 说明 |
|---|---|
| **高可用** | 主分片所在节点宕机时，副本提升为新主分片 |
| **读扩展** | 搜索请求可在主+副本分片并行执行（默认轮询） |

## 🔧 动态调整副本数

```http
PUT /products/_settings
{
  "number_of_replicas": 2
}
```

副本数**可动态调整**，不影响写入（副本由主分片异步同步）。

## 📊 主-副本同步机制

```
写入流程：
  Client → Primary Shard → Translog → Memory Buffer
  Primary → Replica (异步同步) → Translog → Memory Buffer
  Refresh → Segment (可搜索)
```

## ⚠️ 副本相关注意事项

::: warning
- 副本数 = 0：节点故障时**数据丢失**
- 副本数 ≥ 数据节点数：会有副本**无法分配**，集群 yellow
- 副本提升需要几秒到几十秒，期间搜索仍可用（读旧副本）
:::

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="replica" :height="400" />

## 📚 延伸阅读
- [分片 Shard](/01-storage/shard)
- [段 Segment](/01-storage/segment)
- [Translog](/01-storage/translog)
