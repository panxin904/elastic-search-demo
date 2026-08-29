---
title: PV 与 PVC
date: 2026-08-15  # date-auto-injected
---

# PersistentVolume 与 PersistentVolumeClaim — K8s 存储的声明式模型

> <span class="kg-badge kg-badge--cloud-native">云原生</span>
> PV 资源池 · PVC 申请单 · StorageClass 动态分配

K8s 把存储分成**供应者（PV）**和**消费者（PVC）**两个抽象：

- **PV（PersistentVolume）**：集群里的"一块存储"
- **PVC（PersistentVolumeClaim）**：用户对存储的"申请"
- **StorageClass**：存储的"模板"，决定如何动态创建 PV

## 1. 三大资源关系

```
┌──────────────────┐
│  StorageClass    │   ← 模板（kind=gold, kind=fast, kind=backup）
└────────┬─────────┘
         │ 创建
┌────────▼─────────┐
│  PersistentVolume│   ← 集群里的实际存储
└────────┬─────────┘
         │ 绑定 (1:1)
┌────────▼─────────┐
│  PVC             │   ← 用户/Pod 的申请
└────────┬─────────┘
         │ mount
┌────────▼─────────┐
│  Pod             │
└──────────────────┘
```

## 2. 静态 PV 实战

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-static-1
spec:
  capacity:
    storage: 10Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /data/pv1
  mountOptions:
    - hard
    - nfsvers=4.1
```

PVC 申请：

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-static-1
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: manual    # 必须匹配 PV 的 class
  volumeName: pv-static-1     # 显式绑定到具体 PV
```

## 3. 动态 PV 实战（最常用）

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-gp3
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iopsPerGB: "3000"
  throughput: "125"
  encrypted: "true"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
reclaimPolicy: Delete
```

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-dynamic
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: ebs-gp3
  resources:
    requests:
      storage: 20Gi
```

K8s 自动：调 CSI Driver → AWS 创建 EBS → 创建 PV → 绑定 PVC。

## 4. accessModes 三种

| Mode | 缩写 | 含义 |
|------|------|------|
| ReadWriteOnce | RWO | 单节点读写 |
| ReadOnlyMany | ROX | 多节点只读 |
| ReadWriteMany | RWX | 多节点读写（最稀有） |
| ReadWriteOncePod | RWOP | 单 Pod 读写（K8s 1.22+，比 RWO 更严格） |

**常见支持矩阵**：

| 存储 | RWO | ROX | RWX |
|------|-----|-----|-----|
| AWS EBS | ✅ | ✅ | ❌ |
| Azure Disk | ✅ | ✅ | ❌ |
| GCE PD | ✅ | ✅ | ❌ |
| CephFS | ✅ | ✅ | ✅ |
| NFS | ✅ | ✅ | ✅ |
| Longhorn | ✅ | ✅ | ✅ |
| JuiceFS | ✅ | ✅ | ✅ |
| GlusterFS | ✅ | ✅ | ✅ |

## 5. 关键字段

### 5.1 reclaimPolicy

| 值 | 含义 | 何时用 |
|----|------|--------|
| Retain | 删 PVC → PV 保留（数据留着） | **数据库 / 生产数据** |
| Recycle | 删 PVC → PV 回收（rm -rf 内容） | 测试 |
| Delete | 删 PVC → 后端存储也删 | **开发 / 临时** |

**强烈建议**：生产用 **Retain**，手动清理 PV。

### 5.2 volumeBindingMode

| 值 | 含义 |
|----|------|
| Immediate | PVC 创建就立即创建 PV（绑定存储） |
| WaitForFirstConsumer | 等 Pod 调度 → 按节点拓扑创建 PV |

**拓扑敏感存储（EBS / PD）必须用 WaitForFirstConsumer**——否则 Pod 调度到与卷不同的 AZ 会 mount 失败。

### 5.3 allowVolumeExpansion

是否允许在线扩：

```yaml
allowVolumeExpansion: true   # 允许
```

扩的方式：

```bash
kubectl edit pvc my-pvc
# 把 storage: 10Gi 改成 storage: 20Gi
```

CSI Driver 必须支持 `ControllerExpandVolume` + `NodeExpandVolume`。

### 5.4 mountOptions

```yaml
mountOptions:
  - hard
  - nfsvers=4.1
  - noatime
  - _netdev
```

传给 mount 命令的参数。

## 6. PV 生命周期

```
Available ─→ Bound ─→ Released
                 │
                 └──→ (Retain：Available)
```

- **Available**：未被绑定
- **Bound**：已绑定到 PVC
- **Released**：PVC 已删，PV 待处理（按 reclaimPolicy）

## 7. StorageClass 的 provisioner

```yaml
provisioner: <driver-name>
```

| Driver | 写法 |
|--------|------|
| AWS EBS | ebs.csi.aws.com |
| GCE PD | pd.csi.storage.gke.io |
| Ceph RBD | rbd.csi.ceph.com |
| CephFS | cephfs.csi.ceph.com |
| NFS | nfs.csi.k8s.io |
| JuiceFS | csi.juicefs.com |
| Longhorn | driver.longhorn.io |

## 8. 实战：StatefulSet 自动 PVC

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres
  replicas: 3
  selector:
    matchLabels: { app: postgres }
  template:
    metadata:
      labels: { app: postgres }
    spec:
      containers:
      - name: postgres
        image: postgres:15
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ReadWriteOnce]
      storageClassName: ebs-gp3
      resources:
        requests:
          storage: 100Gi
```

K8s 自动给每个 Pod（postgres-0, postgres-1, postgres-2）创建独立的 PVC（data-postgres-0, data-postgres-1, data-postgres-2）。

## 9. 常见问题

### 9.1 PVC Pending

```bash
kubectl describe pvc my-pvc
```

常见原因：

- StorageClass 不存在
- provisioner 没装
- volumeBindingMode 等待 Pod 调度
- 拓扑不匹配（EBS 在 us-east-1a，但 Pod 调度到 us-east-1b）
- 配额（`pods/persistentvolumeclaims` 超限）

### 9.2 Pod 无法 mount

- CSI Driver Node Plugin 未运行
- 卷已经被其他 Pod 占用（RWO）
- 文件系统不兼容

### 9.3 删 PVC 数据没清

- reclaimPolicy=Retain（这正是设计）
- 要 Delete 才删后端存储

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| PVC = 申请单 | "PVC=用户单" |
| PV = 实际存储 | "PV=资源池" |
| StorageClass = 模板 | "SC=动态工厂" |
| 生产用 Retain | "Retain=数据安全" |
| WaitForFirstConsumer = 拓扑 | "等调度=防 AZ" |

## 参考

- K8s Storage 文档：<https://kubernetes.io/docs/concepts/storage/>
- PersistentVolume 详解
- CSI 规范文档

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 文件系统
- [observability](https://java-px.bot.cd/observability/):存储监控
- [postgresql](https://java-px.bot.cd/postgresql/):PG 存储引擎
