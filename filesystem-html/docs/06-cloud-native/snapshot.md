---
title: VolumeSnapshot
date: 2026-08-15  # date-auto-injected
---

# VolumeSnapshot — K8s 存储快照标准

> <span class="kg-badge kg-badge--cloud-native">云原生</span>
> CSI 原生快照 · 备份与恢复 · 数据保护

K8s 通过 `VolumeSnapshot` API 把"卷快照"做成标准资源。它是数据保护、灾备、克隆的核心机制。

## 1. 三种资源

| 资源 | API | 作用 |
|------|-----|------|
| VolumeSnapshot | snapshot.storage.k8s.io/v1 | 一次快照的实例 |
| VolumeSnapshotContent | snapshot.storage.k8s.io/v1 | 实际的快照（PV 视角） |
| VolumeSnapshotClass | snapshot.storage.k8s.io/v1 | 快照模板 |

类比：

- Snapshot = "快照的申请单"
- SnapshotContent = "快照的实际数据"
- SnapshotClass = "快照的模板"（用什么 driver）

## 2. 创建快照类

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-snapclass
driver: ebs.csi.aws.com          # CSI driver 名
deletionPolicy: Delete            # Delete 或 Retain
parameters:                       # 可选：传给 driver
  tagSpecification: "true"
  encrypted: "true"
```

| 删除策略 | 含义 |
|----------|------|
| Delete | 删 Snapshot → 自动删底层快照 |
| Retain | 删 Snapshot → 保留底层快照 |

## 3. 创建快照

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: db-snap-20260101
  namespace: production
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: db-data
```

```bash
kubectl get volumesnapshot -A
kubectl describe volumesnapshot db-snap-20260101
```

**关键字段** `status`：

```yaml
status:
  readyToUse: true
  snapshotHandle: snap-0a1b2c3d...
  creationTime: "2026-01-01T10:00:00Z"
  restoreSize: "100Gi"
```

## 4. 从快照恢复 / 克隆

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-restored
  namespace: production
spec:
  storageClassName: ebs-gp3
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 100Gi
  dataSource:
    name: db-snap-20260101
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
```

CSI Driver 会从快照恢复出**新 PVC**。适合：

- 灾备恢复
- 测试环境（复制生产数据）
- 数据迁移

## 5. 实战：MySQL 定时快照

```bash
# 用 Velero（K8s 备份神器）
velero install --provider aws --bucket my-backup-bucket \
    --secret-file ./credentials-velero \
    --use-restic          # 用 restic 做文件级备份

# 自动备份
velero schedule create daily-snapshot \
    --schedule="0 2 * * *" \
    --include-namespaces production
```

Velero 配合 K8s VolumeSnapshot → 自动把 PVC 备份到 S3。

## 6. 实战：Longhorn 快照

Longhorn 自带快照与备份：

```yaml
# 1. Longhorn 快照
apiVersion: longhorn.io/v1beta2
kind: Snapshot
metadata:
  name: mysql-snap-20260101
  namespace: longhorn-system
spec:
  volume: pvc-xxx
```

UI 里能看到 snapshot 树（增量链）：

```
mysql-snap-20260101 (增量)
  ↑
mysql-snap-20260101-mid (增量)
  ↑
mysql-snap-20260101-base (全量)
```

## 7. 实战：备份到 S3

### Longhorn

```yaml
apiVersion: longhorn.io/v1beta2
kind: BackupTarget
metadata:
  name: s3-backup
  namespace: longhorn-system
spec:
  backupTargetURL: s3://my-backup@us-east-1/
  credentialSecret: longhorn-s3
```

### Rook-Ceph

```yaml
apiVersion: ceph.rook.io/v1
kind: CephBlockPool
metadata:
  name: replicapool
spec:
  replicated: { size: 3 }
---
# 配合 k8s-snapshot + 配置 S3 backup target
```

### OpenEBS

```yaml
apiVersion: openebs.io/v1alpha1
kind: Backup
metadata:
  name: my-backup
spec:
  volumeName: pvc-xxx
  backupName: my-backup-20260101
  s3:
    endpoint: s3.amazonaws.com
    bucket: my-backup
    accessKeyID: ...
    secretAccessKey: ...
```

## 8. 实战：Stork（OpenEBS 高级数据保护）

Stork 是 OpenEBS 的 K8s 数据保护工具：

```bash
# 1. 安装
helm install stork openebs/stork --namespace openebs

# 2. 克隆 PVC
kubectl apply -f - <<EOF
apiVersion: stork.libopenebs.io/v1alpha1
kind: GroupSnapshot
metadata:
  name: clone-group
spec:
  pvcSelector:
    matchLabels:
      app: mysql
EOF
```

Stork 能一次性克隆多个 PVC（用于整套应用迁移）。

## 9. 快照与备份的差异

| 概念 | 快照 | 备份 |
|------|------|------|
| 存哪 | 卷所在存储 | 独立存储（S3 / NFS） |
| 恢复速度 | **快** | 慢（要下载） |
| 空间 | 增量（便宜） | 全量（贵） |
| 跨集群恢复 | ❌ | ✅ |
| 长期保留 | ❌（同存储） | ✅ |
| 频率 | 高（每分钟） | 低（每天） |

**经验**：快照是"近场保护"，备份是"异地保护"。两者都要有。

## 10. RTO / RPO 设计

| 策略 | RPO（数据丢失） | RTO（恢复时间） |
|------|----------------|----------------|
| 无任何保护 | 数小时 | 数小时 |
| 每天备份 | 24 小时 | 1~4 小时 |
| 每小时快照 | 1 小时 | 分钟 |
| 实时同步副本 | ~0 | 分钟 |
| 多 AZ 同步副本 | ~0 | 秒 |

**快照频率与备份频率 = 业务允许的 RPO**。

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| VolumeSnapshot 是 K8s 标准 | "Snapshot=K8s API" |
| Delete vs Retain | "Delete=自动清，Retain=留着" |
| 快照 = 同存储快速恢复 | "快照=近场" |
| 备份 = 异地长期保留 | "备份=异地" |
| 两者结合才完整 | "近 + 远 = 全" |

## 参考

- K8s VolumeSnapshot 文档
- Velero 备份框架
- Longhorn 快照原理（White Paper）