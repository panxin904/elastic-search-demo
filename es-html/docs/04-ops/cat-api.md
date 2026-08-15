---
title: _cat API
category: ops
graphNodeId: cat-api
---

<span class="kg-badge kg-badge-ops">运维层</span>

# _cat API

## 📌 一句话定义
`_cat` API 提供**人类可读**的集群状态信息，是运维诊断的瑞士军刀。

## 📚 常用 _cat 命令

| 命令 | 用途 |
|---|---|
| `/_cat/health` | 集群健康 |
| `/_cat/nodes` | 节点列表 |
| `/_cat/indices` | 索引列表 |
| `/_cat/shards` | 分片分布 |
| `/_cat/allocation` | 分片分配 |
| `/_cat/recovery` | 恢复进度 |
| `/_cat/thread_pool` | 线程池 |
| `/_cat/pending_tasks` | 待处理任务 |
| `/_cat/plugins` | 插件列表 |
| `/_cat/master` | master 节点 |

## 🔧 格式化输出

```bash
# 紧凑 + 表头
GET /_cat/nodes?h=ip,name,heap.percent,role&v

# 输出：
ip          name  heap.percent role
10.0.1.10   es01  45           cdfhilmrstw
10.0.1.11   es02  50           cdfhilmrstw
10.0.1.12   es03  42           cdfhilmrstw
```

## 📋 常用列

### 节点 (`_cat/nodes`)

| 列 | 含义 |
|---|---|
| `heap.percent` | 堆使用百分比 |
| `ram.percent` | 内存使用百分比 |
| `cpu` | CPU 使用 |
| `load_1m` | 1分钟负载 |
| `node.role` | m (master) / d (data) / i (ingest) / ... |
| `master` | 是否当前 master |
| `disk.used_percent` | 磁盘使用百分比 |

### 索引 (`_cat/indices`)

```bash
GET /_cat/indices?v&s=store.size:desc
```

| 列 | 含义 |
|---|---|
| `index` | 索引名 |
| `docs.count` | 文档数 |
| `store.size` | 存储大小 |
| `pri` | 主分片数 |
| `rep` | 副本数 |

### 分片 (`_cat/shards`)

```bash
GET /_cat/shards/products?v&h=index,shard,prirep,state,node,unassigned.reason
```

| 列 | 含义 |
|---|---|
| `index,shard` | 索引与分片号 |
| `prirep` | p (primary) / r (replica) |
| `state` | STARTED / UNASSIGNED / INITIALIZING |
| `unassigned.reason` | 未分配原因 |

## 📦 JSON 输出

```bash
GET /_cat/nodes?format=json
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="cat-api" :height="400" />

## 📚 延伸阅读
- [集群健康](/04-ops/cluster-health)
- [监控 Cerebro](/04-ops/monitoring)
