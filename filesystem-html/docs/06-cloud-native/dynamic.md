---
title: 动态卷供给
---

# 动态卷供给 — StorageClass 自动化全解

> <span class="kg-badge kg-badge--cloud-native">云原生</span>
> 模板化创建 · 按需扩容 · 延迟绑定

动态卷供给（Dynamic Provisioning）是 K8s 存储的最佳实践：用户**只声明需求**（StorageClass + 容量），K8s 通过 CSI Driver **按需创建**实际卷。

## 1. 为什么需要动态供给

静态 PV 的痛点：

- 集群管理员手工建 PV → 几十个用户就要建几十个
- 用户必须知道底层存储细节
- 容量预估难（用户提了 10G 实际需要 100G）
- 拓扑不匹配问题反复出现

动态供给的好处：

- 用户只需声明 storage + accessModes + storageClassName
- K8s 通过 StorageClass 自动创建匹配的 PV
- 卷跟随 Pod 拓扑（WaitForFirstConsumer）

## 2. StorageClass 完整字段

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-gp3
provisioner: ebs.csi.aws.com          # 必填：CSI driver 名称
parameters:                            # 可选：传给 driver 的参数
  type: gp3
  fsType: ext4
  encrypted: "true"
  iopsPerGB: "3000"
reclaimPolicy: Delete                  # Retain / Recycle / Delete
volumeBindingMode: Immediate           # 或 WaitForFirstConsumer
allowVolumeExpansion: true             # 是否允许扩
mountOptions:                          # 挂载选项
  - noatime
allowedTopologies:                     # 限制可调度区域
  - matchLabelExpressions:
    - key: topology.kubernetes.io/zone
      values: [us-east-1a]
```

## 3. 实战：多类型 StorageClass

```yaml
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-fast
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iopsPerGB: "3000"
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true

---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-archive
provisioner: ebs.csi.aws.com
parameters:
  type: st1                              # Throughput Optimized HDD
reclaimPolicy: Retain
volumeBindingMode: WaitForFirstConsumer

---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: local-ssd
provisioner: kubernetes.io/no-provisioner  # 静态
volumeBindingMode: WaitForFirstConsumer
```

## 4. PVC 申请最佳实践

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-data
  namespace: production
  labels:
    app: mysql
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: ebs-fast
  resources:
    requests:
      storage: 100Gi
  # volumeName: 不用（动态创建）
  # selector: 一般不用
  # dataSource: 用于克隆（见下）
```

## 5. 卷克隆（Clone）

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cloned-data
spec:
  storageClassName: ebs-fast
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 100Gi
  dataSource:
    kind: PersistentVolumeClaim
    name: source-data
  dataSourceRef:
    apiGroup: ""
    kind: PersistentVolumeClaim
    name: source-data
```

CSI Driver 必须支持 `CreateVolume` 时带 `volume_content_source`。

## 6. 容量扩容

```bash
# 1. SC 必须 allowVolumeExpansion: true
# 2. CSI Driver 必须支持扩（ControllerExpandVolume + NodeExpandVolume）

# 在线扩
kubectl patch pvc db-data -p '{"spec":{"resources":{"requests":{"storage":"200Gi"}}}}'

# 看事件
kubectl describe pvc db-data | grep -i resize
```

| 存储 | 支持在线扩 |
|------|-----------|
| EBS gp3 | ✅ |
| GCE PD | ✅ |
| Azure Disk | ✅ |
| Ceph RBD | ✅ |
| CephFS | ✅ |
| NFS | ❌（看 driver，有的支持薄卷扩） |
| Longhorn | ✅ |

## 7. WaitForFirstConsumer 的妙用

```yaml
volumeBindingMode: WaitForFirstConsumer
```

流程：

1. 用户创建 PVC → **不立即调 Driver 创建卷**
2. 用户创建 Pod 引用 PVC
3. K8s 调度 Pod → 选择节点
4. 根据节点拓扑（zone / region）调 Driver 在该 zone 创建卷
5. 卷创建完成 → Pod 启动

**好处**：

- EBS / Azure Disk / GCE PD 都在单 zone → 调度到的节点必须在同 zone
- WaitForFirstConsumer 让"卷跟着 Pod 走"，避免 az 不匹配

## 8. 默认 StorageClass

```bash
# 设默认 SC
kubectl patch storageclass ebs-fast -p '{"metadata":{"annotations":{"storageclass.kubernetes.io/is-default-class":"true"}}}'

# 取消默认
kubectl annotate storageclass ebs-fast storageclass.kubernetes.io/is-default-class-
```

PVC 不写 `storageClassName` → 自动用默认 SC。

## 9. 实战：CSI Snapshot 配合动态供给

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-snapclass
driver: ebs.csi.aws.com
deletionPolicy: Delete
parameters:
  tagSpecification: "true"
```

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: db-snap-20260101
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: db-data
```

```yaml
# 从快照恢复
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-restored
spec:
  storageClassName: ebs-fast
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 100Gi
  dataSource:
    kind: VolumeSnapshot
    name: db-snap-20260101
    apiGroup: snapshot.storage.k8s.io
```

## 10. 容量规划与成本

| 存储类 | AWS 类型 | $/GB/月 | 适用 |
|--------|----------|---------|------|
| ebs-fast | gp3 | $0.08 | 数据库 |
| ebs-cold | st1 | $0.045 | 大数据 / 备份 |
| ebs-archive | sc1 | $0.015 | 冷归档 |

配合 `reclaimPolicy: Delete`，PVC 删 → 卷删 → 停止计费。

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| StorageClass = 模板 | "SC=工厂模板" |
| WaitForFirstConsumer = 拓扑 | "等调度=防 AZ 漂移" |
| 扩要 allowVolumeExpansion | "扩=三条件" |
| 默认 SC 免配置 | "default=免写" |
| Snapshot 需 CSI driver | "快照=CSI 原生" |

## 参考

- K8s Dynamic Provisioning 文档
- AWS EBS CSI Driver 文档
- CSI Snapshot 规范