---
title: PV / PVC
---

# PV / PVC - 持久化存储

> Pod 是短命的，数据要"长"在 Pod 之外。PersistentVolume（PV）+ PersistentVolumeClaim（PVC）= k8s 的存储抽象。

## 🤔 为什么需要 PV / PVC

```
裸 Pod + hostPath：
  - Pod 重建 → 数据可能在不同 Node → 数据丢
  - 集群扩缩 + 跨节点调度 → 数据没跟着

PV / PVC：
  - Pod 调度到哪 → 存储跟着去
  - 抽象存储细节（用户只说"我要 10G"，不说底层是 EBS / NFS / Ceph）
```

## 🧬 核心概念

```
┌──────────┐  请求       ┌──────┐
│   Pod    │ ←──────→  │ PVC  │  "我需要 10G readWriteOnce"
└──────────┘            └──────┘
                            ↓ 静态 / 动态供给
                       ┌──────────┐
                       │   PV     │  实际存储（EBS 卷 / NFS / ceph）
                       └──────────┘
```

| 资源 | 谁创建 | 含义 |
|------|--------|------|
| **PV** | 管理员（手动）/ 动态 provisioner | 一段实际存储 |
| **PVC** | 用户（应用） | "我需要多少空间 + 访问模式" |
| **StorageClass** | 管理员 | "什么类型的存储 + 动态 provisioner" |

## 📜 静态 PV

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-nfs-1
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce            # 只能被一个 Node 挂为读写
    # - ReadOnlyMany
    # - ReadWriteMany          # 多个 Node 可读写
  persistentVolumeReclaimPolicy: Retain    # 删 PVC 后保留数据
  storageClassName: nfs
  nfs:
    server: 192.168.1.100
    path: /exports/data
```

| accessModes | 含义 |
|-------------|------|
| ReadWriteOnce (RWO) | 单 Node 读写 |
| ReadOnlyMany (ROX) | 多 Node 只读 |
| ReadWriteMany (RWX) | 多 Node 读写（NFS / ceph 可） |

## 📜 静态 PVC

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data-claim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: nfs        # 不指定会用默认
  volumeName: pv-nfs-1        # 显式绑定到某 PV
```

PVC 创建后，k8s 自动找匹配的 PV 绑定（按 size + accessModes + class）。

## 📜 在 Pod 里用

```yaml
spec:
  containers:
  - name: app
    image: myapp:1.0
    volumeMounts:
    - name: data
      mountPath: /var/lib/app
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: data-claim
```

## 🔄 StorageClass 动态供给

**生产推荐**：动态创建 PV，不用管理员手动。

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3
  provisioner: ebs.csi.aws.com    # AWS EBS CSI
  parameters:
    type: gp3
    fsType: ext4
  reclaimPolicy: Delete
  volumeBindingMode: WaitForFirstConsumer
  allowVolumeExpansion: true
```

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data
spec:
  storageClassName: gp3
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 20Gi
```

PVC 创建 → StorageClass 自动 provisioner → 自动建 PV → 绑定。

## 📚 主流 CSI provisioner

| 云 / 存储 | provisioner |
|----------|-------------|
| AWS EBS | ebs.csi.aws.com |
| GCP PD | pd.csi.storage.gke.io |
| Azure Disk | disk.csi.azure.com |
| Azure File | file.csi.azure.com |
| NFS | nfs.csi.k8s.io |
| Ceph | rook-ceph.rbd.csi.ceph.com |
| Longhorn | driver.longhorn.io |
| OpenEBS | openebs.io/local |

## 🔧 常用命令

```bash
# 看
kubectl get pv
kubectl get pvc
kubectl get storageclass    # 简写 kubectl get sc

# 详细
kubectl describe pvc data-claim
kubectl describe pv pv-nfs-1

# 删（注意：policy = Retain 时 PV 还在）
kubectl delete pvc data-claim

# 扩（需 StorageClass.allowVolumeExpansion）
kubectl edit pvc data-claim
# 改 spec.resources.requests.storage
```

## 🔄 StatefulSet 自动 PVC

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: db
spec:
  serviceName: db
  replicas: 3
  template:
    spec:
      containers:
      - name: db
        image: postgres:15
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:        # 关键！
  - metadata:
      name: data
    spec:
      accessModes: [ReadWriteOnce]
      storageClassName: gp3
      resources: { requests: { storage: 10Gi } }
```

自动建 PVC：`data-db-0` / `data-db-1` / `data-db-2`，绑定到 db-0/1/2 Pod。

## 🩹 故障

```bash
# PVC Pending
kubectl describe pvc data-claim
# Events: no persistent volumes available for this claim
# - 没有匹配 PV（size / class / accessModes）
# - StorageClass provisioner 失败

# Pod 卡在 ContainerCreating
kubectl describe pod <name>
# Events: MountVolume.SetUp failed
# 通常：PV / PVC 未 bound

# 数据恢复
kubectl delete pod <pod>    # StatefulSet 重建
# PVC 数据仍在（没被删）
```

## 🛠 实战

```bash
# 1. 装 AWS EBS CSI Driver（生产）
# EKS 默认已装 / 自建用 helm
helm repo add aws-ebs-csi-driver https://kubernetes-sigs.github.io/aws-ebs-csi-driver
helm install aws-ebs-csi-driver aws-ebs-csi-driver/aws-ebs-csi-driver \
  --namespace kube-system

# 2. 默认 StorageClass
kubectl get sc

# 3. 申请 PVC
kubectl apply -f pvc.yaml

# 4. 看自动 PV
kubectl get pv

# 5. 装到 Pod
# (见上面 Pod manifest)
```

## 🔗 下一步

- [StorageClass / CSI](/05-k8s-storage/storageclass)
- [ConfigMap / Secret](/05-k8s-storage/configmap-secret)
- [StatefulSet](/03-k8s-workload/statefulset)