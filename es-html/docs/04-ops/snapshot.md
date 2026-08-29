---
title: Snapshot 备份
date: 2026-08-15  # date-auto-injected
category: ops
graphNodeId: snapshot
---

<span class="kg-badge kg-badge-ops">运维层</span>

# Snapshot 备份

## 📌 一句话定义
Snapshot 是 ES 内置的**集群级备份机制**，基于**增量**原理，支持 S3/HDFS/共享文件系统等多种 repository。

## 🔧 注册 Repository

### 共享文件系统

```bash
PUT /_snapshot/my_backup
{
  "type": "fs",
  "settings": {
    "location": "/mnt/es-backup",
    "compress": true
  }
}
```

### S3

```bash
PUT /_snapshot/my_s3_repo
{
  "type": "s3",
  "settings": {
    "bucket": "my-es-backup",
    "region": "us-east-1"
  }
}
```

## 📦 创建快照

```bash
# 备份所有索引
PUT /_snapshot/my_backup/snapshot_2026_07_13
{
  "include_global_state": true,
  "indices": "*",
  "ignore_unavailable": true
}
```

```bash
# 备份指定索引
PUT /_snapshot/my_backup/products_2026_07_13
{
  "indices": "products,orders",
  "ignore_unavailable": true,
  "include_global_state": false
}
```

## 🔄 恢复

```bash
# 关闭索引（必须）
POST /products/_close

# 恢复
POST /_snapshot/my_backup/snapshot_2026_07_13/_restore
{
  "indices": "products",
  "rename_pattern": "products(.+)",
  "rename_replacement": "restored_products$1"
}

# 打开
POST /products/_open
```

## 📊 快照管理

| 操作 | API |
|---|---|
| 列出快照 | `GET /_snapshot/my_backup/_all` |
| 快照状态 | `GET /_snapshot/my_backup/snapshot_2026_07_13/_status` |
| 删除快照 | `DELETE /_snapshot/my_backup/snapshot_2026_07_13` |
| 列出 repo | `GET /_snapshot` |
| 删除 repo | `DELETE /_snapshot/my_backup` |

## ⚠️ 关键注意事项

1. **必须先 close 索引**才能 restore 到已有索引名
2. **共享文件系统**需要在所有节点的同路径可访问
3. **S3/GCS** 需要对应 plugin + 凭证
4. 跨集群恢复**要求版本兼容**（目标集群版本 ≥ 源集群 -1）

## 🗓️ 自动化建议

```bash
# SLM (Snapshot Lifecycle Management)
PUT /_slm/policy/daily-snapshot
{
  "schedule": "0 30 1 * * ?",
  "name": "<daily-{now/d}>",
  "repository": "my_backup",
  "config": {
    "indices": ["products", "orders"],
    "include_global_state": false
  },
  "retention": {
    "expire_after": "30d",
    "min_count": 5,
    "max_count": 50
  }
}
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="snapshot" :height="400" />

## 📚 延伸阅读
- [ILM 生命周期](/04-ops/ilm)
- [集群重启](/04-ops/restart)
