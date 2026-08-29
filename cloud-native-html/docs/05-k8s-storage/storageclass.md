---
title: StorageClass / CSI
---

# StorageClass / CSI - 动态存储

> StorageClass = 存储的"模板" + provisioner。CSI = Container Storage Interface（标准接口）。

## 🤔 为什么需要 StorageClass

```
手动 PV：
  - 管理员手写 PV → 慢、错
  - 几十个 PVC → 几十个 PV → 难维护

StorageClass：
  - 管理员写一个"类"（sc.yaml）
  - 用户写 PVC（选 sc）
  - 动态 provisioner 自动建 PV
```

## 📜 StorageClass manifest

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3                    # 类名（用户在 PVC 中引用）
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"   # 标记默认
provisioner: ebs.csi.aws.com  # 哪个 provisioner
parameters:                   # 透传给 provisioner
  type: gp3
  fsType: ext4
  iopsPerGB: "10"
reclaimPolicy: Delete         # 删 PVC 后 PV 行为
volumeBindingMode: WaitForFirstConsumer   # 等 Pod 调度再决定（推荐）
allowVolumeExpansion: true    # 允许扩
mountOptions:                 # 挂载选项
  - debug
```

## 🎛 关键字段

| 字段 | 选项 / 说明 |
|------|------------|
| `provisioner` | 哪个 driver 负责（CSI 名） |
| `reclaimPolicy` | `Retain`（保留数据）/ `Delete`（自动删） |
| `volumeBindingMode` | `Immediate`（立即建 PV）/ `WaitForFirstConsumer`（等 Pod 调度） |
| `allowVolumeExpansion` | true / false |
| `mountOptions` | mount 命令的额外参数 |

## 🪜 主流 StorageClass 模板

### AWS EBS（gp3 SSD）

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: gp3
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  fsType: ext4
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

### NFS（ReadWriteMany）

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs
provisioner: nfs.csi.k8s.io
parameters:
  server: nfs.example.com
  share: /exports/data
reclaimPolicy: Delete
volumeBindingMode: Immediate
mountOptions:
  - nfsvers=4.1
```

### Local Path（开发 / 单节点）

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-path
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: rancher.io/local-path
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete
```

```bash
# 装 driver
kubectl apply -f https://raw.githubusercontent.com/rancher/local-path-provisioner/master/deploy/local-path-storage.yaml
```

## 🧠 CSI 架构

```
                ┌─────────────────┐
                │     k8s          │
                │  (kubelet)      │
                └────────┬────────┘
                         │ gRPC (CSI)
                ┌────────▼────────┐
                │  CSI Driver     │   跑在 Pod / DaemonSet
                │  (sidecar)      │
                └────────┬────────┘
                         │ 厂商 API
                ┌────────▼────────┐
                │  存储后端        │
                │  (EBS / ceph)  │
                └─────────────────┘
```

CSI 三个 gRPC 接口：
- **Identity**（能力声明）
- **Controller**（创建 / 删除 / 扩 PV）
- **Node**（mount / unmount）

## 📜 PVC 引用 StorageClass

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: data
spec:
  storageClassName: gp3        # 引用 StorageClass
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 20Gi
```

PVC 创建 → SC provisioner 自动建 PV → 自动绑定。

## 🔧 常用命令

```bash
# 看所有 SC
kubectl get sc

# 默认 SC（被自动选）
kubectl get sc -o jsonpath='{.items[?(@.metadata.annotations.storageclass\.kubernetes\.io/is-default-class=="true")].metadata.name}'

# 看 PVC
kubectl get pvc
kubectl get pvc -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,SC:.spec.storageClassName,SIZE:.spec.resources.requests.storage

# 描述（看 PV / StorageClass / 事件）
kubectl describe pvc data
```

## 🔄 扩容

```bash
# StorageClass 需 allowVolumeExpansion: true
kubectl edit pvc data
# 改 spec.resources.requests.storage
# 改 10Gi → 50Gi，存储自动扩
```

## 🛠 实战

### 1. 装 AWS EBS CSI

```bash
# 装（EKS 默认 / 自建用 helm）
kubectl apply -k "github.com/kubernetes-sigs/aws-ebs-csi-driver/deploy/kubernetes/overlays/stable/?ref=release-1.27"
```

### 2. 创建 SC + PVC + Pod

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iopsPerGB: "50"
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
  storageClassName: fast-ssd
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 100Gi
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: db
spec:
  containers:
  - name: postgres
    image: postgres:15
    volumeMounts:
    - name: data
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: data
```

## 🩹 故障

```bash
# PVC Pending
kubectl describe pvc data
# Events:
# - ProvisioningFailed: no valid plugin for ...
# - aws-auth: no EC2 IMDS credentials available (EKS IAM Role 错)

# 解决：
# 1. SC provisioner 装了吗？kubectl -n kube-system get pods
# 2. 装对了参数？（type / fsType）
# 3. IAM 权限？（云）
# 4. StorageClass 默认吗？（PVC 不指定 scName 会用默认）

# 扩容失败
kubectl describe pvc data
# Events: VolumeModificationFailed
# 通常：底层不支持在线扩容（某些实例类型）
```

## 🔗 下一步

- [PV / PVC](/05-k8s-storage/pv-pvc)
- [ConfigMap / Secret](/05-k8s-storage/configmap-secret)
- [StatefulSet](/03-k8s-workload/statefulset)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud](https://java-px.bot.cd/cloud/):Spring Cloud 微服务
- [linux](https://java-px.bot.cd/linux/):Linux 内核基础
- [devops](https://java-px.bot.cd/devops/):DevOps 流程
