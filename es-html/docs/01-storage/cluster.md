---
title: 集群 Cluster
date: 2026-08-15  # date-auto-injected
category: storage
graphNodeId: cluster
---

<span class="kg-badge kg-badge-storage">存储层</span>

# 集群 Cluster

![Elasticsearch Cluster 状态机](/es-cluster-state-machine.svg)

## 📌 一句话定义
ES 集群是由**一个或多个节点**组成的、能对外提供统一搜索服务的分布式系统。

## 🎯 为什么需要集群？
- **水平扩展**：突破单机容量与吞吐上限
- **高可用**：节点故障时副本接管
- **并行处理**：查询与索引在多节点并行执行

## 🔧 集群状态

```bash
GET /_cluster/health
```

返回：
```json
{
  "cluster_name": "es-demo",
  "status": "green",   // green / yellow / red
  "number_of_nodes": 3,
  "active_primary_shards": 5,
  "active_shards": 10
}
```

| 状态 | 含义 |
|---|---|
| 🟢 green | 所有分片（含副本）正常分配 |
| 🟡 yellow | 主分片正常，**副本缺失**（常见于单节点） |
| 🔴 red | 至少一个主分片未分配，**有数据丢失风险** |

## 🔗 节点角色

| 角色 | 职责 |
|---|---|
| `master` | 集群状态管理、节点加入/离开 |
| `data` | 存储数据、执行 CRUD/搜索 |
| `ingest` | 预处理管道（ingest pipeline） |
| `coordinating` | 请求路由与结果聚合（每个节点默认都有） |

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="cluster" :height="400" />

## 📚 延伸阅读
- [节点 Node](/01-storage/node)
- [集群健康](/04-ops/cluster-health)
- [分片分配](/04-ops/shard-allocation)

<!-- svg-injected:do-not-edit -->

![elasticsearch cluster](/elasticsearch-cluster.svg)
