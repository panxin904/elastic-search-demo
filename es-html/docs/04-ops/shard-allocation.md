---
title: 分片分配
category: ops
graphNodeId: shard-allocation
---

<span class="kg-badge kg-badge-ops">运维层</span>

# 分片分配 Shard Allocation

ES 通过**分片分配策略**决定分片在哪些节点上分布。

## ⚙️ 核心分配参数

```yaml
# elasticsearch.yml
cluster.routing.allocation.balance.shard:           0.45
cluster.routing.allocation.balance.index:            0.55
cluster.routing.allocation.balance.threshold:        1.0
cluster.routing.allocation.disk.threshold_enabled:   true
cluster.routing.allocation.disk.watermark.low:       85%
cluster.routing.allocation.disk.watermark.high:      90%
cluster.routing.allocation.disk.watermark.flood_stage: 95%
```

## 📊 分配规则类型

| 规则 | 说明 |
|---|---|
| `include` | 白名单 |
| `exclude` | 黑名单 |
| `require` | 必须满足 |

```yaml
# 示例：仅分配到带 box_type=hot 标签的节点
cluster.routing.allocation.require.box_type: hot
```

## 🧱 节点层 (Tier) 与 Awareness

### 分层 (Hot/Warm/Cold)

```yaml
node.attr.box_type: hot    # hot 节点配置
```

```http
PUT /products/_settings
{
  "index.routing.allocation.require.box_type": "hot"
}
```

### Awareness (机架感知)

```yaml
cluster.routing.allocation.awareness.attributes: zone
node.attr.zone: zone-1
```

主分片和副本**强制分布到不同 zone**，单 zone 故障不丢数据。

## 📦 Shard Filtering

```http
POST /products/_cache/clear

# 手动移动分片
POST /_cluster/reroute
{
  "commands": [
    { "move": { "index": "products", "shard": 2, "from_node": "es01", "to_node": "es02" } }
  ]
}
```

## ⚠️ Disk Watermark

| 阈值 | 行为 |
|---|---|
| low (85%) | 新分片不再分配到此节点 |
| high (90%) | **主动 relocate** 分片到其他节点 |
| flood_stage (95%) | 索引强制**只读** |

```bash
# 临时解除只读
PUT /products/_settings { "index.blocks.read_only_allow_delete": null }
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="shard-allocation" :height="400" />

## 📚 延伸阅读
- [分片 Shard](/01-storage/shard)
- [集群健康](/04-ops/cluster-health)
