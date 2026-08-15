---
title: 集群重启
category: ops
graphNodeId: restart
---

<span class="kg-badge kg-badge-ops">运维层</span>

# 集群重启 Restart

## 📌 两种重启方式

| 方式 | 适用 | 风险 |
|---|---|---|
| **滚动重启** (Rolling) | 升级、配置变更 | 低（服务不中断） |
| **全量重启** (Full) | 灾难恢复 | 高（服务中断） |

## 🔧 滚动重启流程（推荐）

### Step 1: 关闭分片分配

```http
PUT /_cluster/settings
{
  "persistent": {
    "cluster.routing.allocation.enable": "primaries"
  }
}
```

> 阻止主分片在重启时迁移（避免不必要的复制流量）

### Step 2: 逐节点执行 sync + restart

```bash
# 每个节点
./bin/elasticsearch -s sync    # 同步 translog 到磁盘
sudo systemctl restart elasticsearch
```

### Step 3: 等待节点恢复

```bash
curl -s http://es01:9200/_cluster/health?wait_for_status=green&timeout=60s
```

### Step 4: 重新启用分配

```http
PUT /_cluster/settings
{
  "persistent": {
    "cluster.routing.allocation.enable": null
  }
}
```

### Step 5: 重复其他节点

> ⚠️ **不要**同时重启所有节点（特别是 master 节点同时宕机会导致脑裂）

## 📋 滚动升级 (跨版本)

```bash
# 关闭分片分配
PUT /_cluster/settings { "cluster.routing.allocation.enable": "primaries" }

# 停止非 master 节点
# 升级 tar 包 / rpm
# 启动节点

# 升级 master 节点（最后）

# 启用分片分配
PUT /_cluster/settings { "cluster.routing.allocation.enable": null }
```

## ⚠️ 升级兼容性

| 源版本 → 目标版本 | 是否需要重启 |
|---|---|
| 7.17.10 → 7.17.11 | 滚动升级 |
| 7.x → 7.y (minor) | 滚动升级 |
| 7.x → 8.x | **全量重启** + reindex |

## 🆘 全量重启（紧急情况）

```bash
# 1. 停止所有节点
for h in es01 es02 es03; do ssh $h "systemctl stop elasticsearch"; done

# 2. 维护操作

# 3. 启动所有节点
for h in es01 es02 es03; do ssh $h "systemctl start elasticsearch"; done

# 4. 等待 yellow/green
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="restart" :height="400" />

## 📚 延伸阅读
- [集群健康](/04-ops/cluster-health)
- [Snapshot 备份](/04-ops/snapshot)
- [JVM 调优](/04-ops/jvm-tuning)
