---
title: Longhorn
---

# Longhorn — 轻量级 K8s 块存储

> <span class="kg-badge kg-badge--cloud-native">云原生</span>
> 微服务架构 · 增量快照 · 简单好用

Longhorn 是 Rancher 出品的 K8s 块存储系统。它**专为 K8s 设计**：

- 100% 微服务化（每个卷一个 Pod）
- 增量快照 / 备份
- 内置 Dashboard
- 比 Ceph 简单 90%，比 OpenEBS cStor 性能好

## 1. Longhorn 核心设计

每个卷是一个独立的微服务：

```
┌──────────────────────────────────────────────┐
│  K8s Cluster                                 │
│  - longhorn-manager (DaemonSet)              │
│  - longhorn-driver (Deployment)              │
│  - longhorn-ui (Deployment)                  │
└────────────────┬─────────────────────────────┘
                 │ gRPC + CSI
┌────────────────▼─────────────────────────────┐
│  每个卷 = 1 个 Pod                            │
│  - replica 1: 数据副本                       │
│  - replica 2: 数据副本                       │
│  - replica 3: 数据副本                       │
└────────────────┬─────────────────────────────┘
                 │ 
┌────────────────▼─────────────────────────────┐
│  节点本地盘（ext4 / xfs）                    │
└──────────────────────────────────────────────┘
```

## 2. Longhorn vs 其他

| 维度 | Longhorn | Rook-Ceph | OpenEBS |
|------|----------|-----------|---------|
| 架构 | **微服务（每卷一个 Pod）** | 单体 | 微服务 |
| 部署复杂度 | **低** | 高 | 中 |
| 副本数 | 1~3 | 3 | 1~3 |
| 快照 | 增量 | 全量/增量 | 增量 |
| 备份 | S3 / NFS | S3 / CephFS | S3 |
| 块设备 | ✅ | ✅ | ✅ |
| 共享文件系统 | ❌ | ✅ (CephFS) | ❌ |
| 性能 | **中** | 中 | 中 |
| 适合规模 | 中小（< 100 节点） | 大 | 小 |

## 3. 部署实战

### 3.1 安装

```bash
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.7.0/deploy/longhorn.yaml
```

### 3.2 命名空间

```bash
kubectl get pods -n longhorn-system
```

应该看到：

```
longhorn-manager-xxxxx    # 每个节点一个
longhorn-driver-deployer  # 1 副本
longhorn-ui-xxxxxx        # 1 副本
```

### 3.3 访问 UI

```bash
kubectl -n longhorn-system port-forward svc/longhorn-frontend 8080:80
# 打开 http://localhost:8080
```

## 4. StorageClass

Longhorn 默认创建 `longhorn` StorageClass：

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: longhorn
provisioner: driver.longhorn.io
parameters:
  numberOfReplicas: "3"
  staleReplicaTimeout: "2880"      # 30 天
  fromBackup: ""
  fsType: ext4
  dataLocality: disabled           # 或 best-effort
  recurringJobs: '[
    {"name":"snap", "task":"snapshot", "cron":"0 0 * * *", "retention":3},
    {"name":"backup", "task":"backup", "cron":"0 2 * * *", "retention":7}
  ]'
allowVolumeExpansion: true
reclaimPolicy: Delete
volumeBindingMode: Immediate
```

## 5. PVC 实战

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-data
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: longhorn
  resources:
    requests:
      storage: 50Gi
```

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  replicas: 1
  serviceName: mysql
  selector: { matchLabels: { app: mysql } }
  template:
    metadata: { labels: { app: mysql } }
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        volumeMounts:
        - name: data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata: { name: data }
    spec:
      accessModes: [ReadWriteOnce]
      storageClassName: longhorn
      resources:
        requests:
          storage: 50Gi
```

## 6. 快照与备份

### 6.1 手动快照

```bash
kubectl apply -f - <<EOF
apiVersion: longhorn.io/v1beta2
kind: Snapshot
metadata:
  name: mysql-snap-20260101
  namespace: longhorn-system
spec:
  volume: pvc-xxx
EOF
```

### 6.2 定期快照

在 StorageClass 的 `recurringJobs` 配置：

```json
{
  "name": "snap",
  "task": "snapshot",
  "cron": "0 * * * *",
  "retention": 24
}
```

### 6.3 备份到 S3

```bash
# 1. 配 S3 backup target
kubectl apply -f - <<EOF
apiVersion: longhorn.io/v1beta2
kind: BackupTarget
metadata:
  name: default
  namespace: longhorn-system
spec:
  backupTargetURL: s3://backup-bucket@us-east-1/
  credentialSecret: s3-cred
EOF
```

```bash
kubectl create secret generic s3-cred -n longhorn-system \
    --from-literal=AWS_ACCESS_KEY_ID=xxx \
    --from-literal=AWS_SECRET_ACCESS_KEY=xxx
```

```yaml
# 2. 创建 backup
apiVersion: longhorn.io/v1beta2
kind: Backup
metadata:
  name: mysql-backup-20260101
  namespace: longhorn-system
spec:
  snapshot: pvc-xxx-snap-xxx
  backupTargetName: default
```

## 7. 恢复（Restore）

### 7.1 从快照恢复

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-restored
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: longhorn
  dataSource:
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
    name: mysql-snap-20260101
  resources:
    requests:
      storage: 50Gi
```

### 7.2 从备份恢复

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-from-backup
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: longhorn
  dataSourceRef:
    kind: VolumeBackup
    apiGroup: longhorn.io
    name: mysql-backup-20260101
  resources:
    requests:
      storage: 50Gi
```

## 8. 节点与磁盘

```bash
kubectl -n longhorn-system get nodes.longhorn.io
kubectl -n longhorn-system describe node.longhorn.io worker-1
```

节点配置：

```yaml
apiVersion: longhorn.io/v1beta2
kind: Node
metadata:
  name: worker-1
  namespace: longhorn-system
spec:
  disks:
    - name: disk1
      path: /var/lib/longhorn
      storageReserved: 30Gi
      tags: ["ssd"]
    - name: disk2
      path: /mnt/hdd
      storageReserved: 100Gi
      tags: ["hdd"]
```

## 9. 调优

```yaml
# StorageClass 参数
parameters:
  numberOfReplicas: "3"        # 副本数
  dataLocality: best-effort    # 或 strict（强本地化）
  nodeSelector: "ssd"          # 只用 ssd 标签的盘
  diskSelector: "ssd"
  recurringJobs: '[...]'
  engineUpgradeImage: longhornio/longhorn-engine:v1.7.0
```

## 10. 故障排查

```bash
# 看 manager 日志
kubectl -n longhorn-system logs -l app=longhorn-manager --tail=100

# 看某个卷的状态
kubectl -n longhorn-system describe engines.longhorn.io pvc-xxx
kubectl -n longhorn-system describe replicas.longhorn.io pvc-xxx-r-1

# 看节点磁盘使用
kubectl -n longhorn-system describe node.longhorn.io worker-1

# 常见问题
# - "No available disk": 节点磁盘已满，调大 storageReserved
# - "Replica scheduling failed": 副本数 > 节点数
# - "Volume detach issue": kubelet 没收到 attach 信号
```

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 每卷一 Pod = 微服务 | "卷=Pod" |
| 100% 简单好用 | "Longhorn=易上手" |
| 副本 = 节点 × 节点数 | "副本=横向" |
| S3 备份原生 | "备份走 S3" |
| 数据本地化 | "locality 优化延迟" |

## 参考

- Longhorn 官方文档：<https://longhorn.io/docs/
- 实战案例
- longhorn-examples（GitHub）