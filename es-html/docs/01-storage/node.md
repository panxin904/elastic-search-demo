---
title: 节点 Node
date: 2026-08-15  # date-auto-injected
category: storage
graphNodeId: node
---

<span class="kg-badge kg-badge-storage">存储层</span>

# 节点 Node

## 📌 一句话定义
节点是运行一个 ES 进程（`org.elasticsearch.bootstrap.Elasticsearch`）的 JVM 实例。

## 🎯 节点分类

| 角色 | 配置 | 职责 |
|---|---|---|
| Master-eligible | `node.master: true` | 参与主节点选举 |
| Data node | `node.data: true` | 存储分片数据 |
| Ingest node | `node.ingest: true` | 执行 ingest pipeline |
| Coordinating only | `node.master/data/ingest: false` | 仅做请求路由 |

> **生产建议**：Master 与 Data 节点**分离部署**，避免主节点因 GC/IO 抖动影响集群稳定性。

## 🔧 节点配置示例

```yaml
# elasticsearch.yml
node.name: ${HOSTNAME}
node.master: true
node.data: true
node.ingest: false
```

## ⚙️ 节点发现 (Zen Discovery)

```yaml
discovery.zen.ping.unicast.hosts:
  - es-node-1
  - es-node-2
  - es-node-3
```

ES 7.x 默认使用**单播发现**，节点启动时互相 ping 组成集群。

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="node" :height="400" />

## 📚 延伸阅读
- [集群 Cluster](/01-storage/cluster)
- [JVM 调优](/04-ops/jvm-tuning)
- [分片分配](/04-ops/shard-allocation)
