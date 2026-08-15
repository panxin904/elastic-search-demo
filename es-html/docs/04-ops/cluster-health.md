---
title: 集群健康
category: ops
graphNodeId: cluster-health
---

<span class="kg-badge kg-badge-ops">运维层</span>

# 集群健康 Cluster Health

## 🔧 查看集群状态

```bash
GET /_cluster/health
```

返回：
```json
{
  "cluster_name": "es-prod",
  "status": "green",
  "timed_out": false,
  "number_of_nodes": 3,
  "number_of_data_nodes": 3,
  "active_primary_shards": 30,
  "active_shards": 60,
  "unassigned_shards": 0,
  "initializing_shards": 0,
  "relocating_shards": 0
}
```

## 🟢🟡🔴 状态判定

| 状态 | 含义 | 行动 |
|---|---|---|
| 🟢 **green** | 所有分片（含副本）正常分配 | 正常 |
| 🟡 **yellow** | 主分片正常，**副本缺失** | 单节点集群正常；多节点需查 |
| 🔴 **red** | 至少 1 个主分片**未分配** | 立即处理 |

## 🔍 yellow 状态排查

```bash
# 看哪些分片未分配
GET /_cluster/allocation/explain
```

```json
{
  "index": "products",
  "shard": 2,
  "primary": false,
  "current_state": "unassigned",
  "unassigned_info": { "reason": "NODE_LEFT" },
  "can_allocate": "no",
  "allocate_explanation": "cannot allocate because allocation is not permitted to any of the nodes"
}
```

## 📊 关键指标

| 指标 | 含义 | 警戒 |
|---|---|---|
| `unassigned_shards` | 未分配分片数 | > 0 异常 |
| `initializing_shards` | 初始化中 | 持续 > 0 = 集群问题 |
| `relocating_shards` | 迁移中 | 持续 > 0 = 平衡失败 |
| `active_shards_percent_as_number` | 活跃分片百分比 | < 100% 异常 |

## 🔧 详细健康查询

```bash
# 指定索引
GET /products/_cluster/health

# 等待状态变化
GET /_cluster/health?wait_for_status=green&timeout=30s
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="cluster-health" :height="400" />

## 📚 延伸阅读
- [集群 Cluster](/01-storage/cluster)
- [分片分配](/04-ops/shard-allocation)
- [_cat API](/04-ops/cat-api)
