---
title: CSI
---

# Container Storage Interface (CSI) — K8s 存储的通用接口

> <span class="kg-badge kg-badge--cloud-native">云原生</span>
> 标准驱动接口 · 跨存储系统 · 解耦供应商

CSI（Container Storage Interface）是 Kubernetes 在 1.13 后 GA 的存储驱动标准。它把"卷的提供 / 挂载 / 快照 / 扩"做成统一的 gRPC 接口，任何厂商按这个接口实现 driver，就能在 K8s 里被使用。

## 1. CSI 解决了什么问题

CSI 之前：

- 卷插件写死在 `kubelet` / `kube-controller-manager` 里
- 新存储产品 → 要修改 K8s 上游代码，发布周期长
- 安全 / 升级都受 K8s 版本绑定

CSI 之后：

- Driver 是**独立的 Pod / DaemonSet**
- K8s 通过 gRPC 与 Driver 通信
- 第三方 Driver 可独立发布、独立升级

## 2. CSI 架构

```
┌──────────────────────────────────────────────┐
│  Kubernetes Control Plane                    │
│  - kube-controller-manager                   │
│  - kubelet                                   │
└──────────────┬───────────────────────────────┘
               │ gRPC (Identity / Controller / Node)
┌──────────────▼───────────────────────────────┐
│  CSI Driver Pods                             │
│  - controller (deployment)                   │
│  - node plugin (daemonset)                   │
│  - sidecar (external-provisioner, etc.)      │
└──────────────┬───────────────────────────────┘
               │ 厂商协议（iSCSI / NFS / 自家）
┌──────────────▼───────────────────────────────┐
│  存储后端（Ceph / MinIO / AWS EBS / Longhorn）│
└──────────────────────────────────────────────┘
```

### 三种 CSI 组件

| 组件 | 角色 | 部署形态 |
|------|------|----------|
| Controller | 卷生命周期（create / delete / attach / detach） | Deployment（一般 2 副本） |
| Node Plugin | 在 Node 上把卷挂到容器里（mount / unmount） | DaemonSet（每个节点） |
| Identity | 服务身份 | 集成在以上两者中 |

### Sidecar 容器

K8s 提供一组官方 sidecar 简化 Driver 开发：

| Sidecar | 功能 |
|---------|------|
| external-provisioner | 自动 Provision PVC |
| external-attacher | 自动 attach 卷到节点 |
| external-snapshotter | 创建/删除快照 |
| external-resizer | 扩容 |
| external-health-monitor | 健康检查 |
| livenessprobe | 探活 |

## 3. CSI RPC 接口

CSI Driver 必须实现以下 gRPC 服务：

```protobuf
service Identity {
  rpc GetPluginInfo(GetPluginInfoRequest) returns (GetPluginInfoResponse);
  rpc GetPluginCapabilities(GetPluginCapabilitiesRequest) returns (...);
  rpc Probe(ProbeRequest) returns (ProbeResponse);
}

service Controller {
  rpc CreateVolume(CreateVolumeRequest) returns (CreateVolumeResponse);
  rpc DeleteVolume(DeleteVolumeRequest) returns (DeleteVolumeResponse);
  rpc ControllerPublishVolume(...) returns (...);  // attach
  rpc ControllerUnpublishVolume(...) returns (...); // detach
  rpc ListVolumes(...);
  rpc CreateSnapshot(...);
  rpc DeleteSnapshot(...);
}

service Node {
  rpc NodeStageVolume(NodeStageVolumeRequest) returns (...);  // mount 到全局
  rpc NodeUnstageVolume(...);
  rpc NodePublishVolume(...);  // bind mount 到容器
  rpc NodeUnpublishVolume(...);
  rpc NodeGetCapabilities(...);
}
```

## 4. CSI 实战部署（以 NFS 为例）

```bash
helm repo add csi-driver-nfs https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/charts
helm install csi-driver-nfs csi-driver-nfs/csi-driver-nfs \
    --namespace kube-system
```

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-csi
provisioner: nfs.csi.k8s.io
parameters:
  server: nfs.example.com
  path: /data/shared
  csi.storage.k8s.io/provisioner-secret-name: nfs-creds
  csi.storage.k8s.io/provisioner-secret-namespace: default
reclaimPolicy: Delete
volumeBindingMode: Immediate
mountOptions:
  - hard
  - nfsvers=4.1
```

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-nfs-pvc
spec:
  accessModes: [ReadWriteMany]
  storageClassName: nfs-csi
  resources:
    requests:
      storage: 10Gi
```

## 5. 关键 CSI 概念

### 5.1 Topology

CSI 支持**拓扑感知**：卷能感知节点位于哪个 region / zone。

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ebs-topology
provisioner: ebs.csi.aws.com
volumeBindingMode: WaitForFirstConsumer   # 等 pod 调度后才创建
allowedTopologies:
  - matchLabelExpressions:
      - key: topology.kubernetes.io/zone
        values:
          - us-east-1a
```

### 5.2 Volume Snapshots

CSI 标准化快照：

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-snapclass
driver: ebs.csi.aws.com
deletionPolicy: Delete
parameters:
  encrypted: "true"
---
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: my-snap
spec:
  volumeSnapshotClassName: csi-snapclass
  source:
    persistentVolumeClaimName: my-pvc
```

### 5.3 Volume Expansion

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: expand-sc
provisioner: ebs.csi.aws.com
allowVolumeExpansion: true
```

```bash
# 在线扩
kubectl edit pvc my-pvc
# 修改 spec.resources.requests.storage: 20Gi
```

### 5.4 Raw Block

CSI 支持块设备（不格式化）：

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: raw-pvc
spec:
  accessModes: [ReadWriteOnce]
  volumeMode: Block
  storageClassName: ebs-sc
  resources:
    requests:
      storage: 10Gi
```

数据库场景用 Block。

## 6. 主流 CSI Driver 一览

| Driver | 维护者 | 适合 |
|--------|--------|------|
| aws-ebs-csi-driver | AWS | AWS EBS |
| azure-disk-csi-driver | Azure | Azure Disk |
| gcp-pd-csi-driver | GCP | GCP PD |
| ceph-csi | Ceph | Ceph RBD / CephFS |
| csi-driver-nfs | K8s | NFS |
| csi-driver-smb | K8s | SMB / CIFS |
| csi-host-path | K8s | 测试用 |
| juicefs-csi | JuiceFS | JuiceFS |
| minio-csi | 社区 | MinIO |
| longhorn | Rancher | 块存储 |

## 7. 实战排查

```bash
# 看 CSI driver 是否健康
kubectl get pods -n kube-system -l app=csi-driver-nfs
kubectl logs -n kube-system -l app=csi-driver-nfs -c csi-driver

# 看 PVC 状态
kubectl describe pvc my-pvc
kubectl get events --sort-by=.lastTimestamp | grep -i csi

# 看卷在节点上的挂载
mount | grep /var/lib/kubelet/pods
```

常见错误：

| 错误 | 原因 |
|------|------|
| `FailedMount` `MountDevice Failed` | 节点上 Node Plugin 失败 |
| `ProvisioningFailed` | Controller 端无权限或参数错 |
| `InvalidArgument` | StorageClass parameters 错 |
| `Volume stuck Pending` | 拓扑问题或 driver bug |

## 8. 自己写一个 CSI 最小 Driver

```go
// 推荐用 csi-spec + Go
// 1. 实现 Identity / Controller / Node 三个 gRPC 服务
// 2. 注册到 gRPC server（unix socket）
// 3. 部署 sidecar（external-provisioner / external-attacher / ...）

// 入门模板：csi-driver-host-path（参考实现）
// https://github.com/kubernetes-csi/csi-driver-host-path
```

## 9. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| gRPC 三件套 | "Identity + Controller + Node" |
| sidecar 自动运维 | "sidecar=内置" |
| 拓扑靠 WaitForFirstConsumer | "等调度再创建" |
| 块 vs 文件 mode | "DB=Block，其他=FS" |
| 故障看 events | "events=真相" |

## 参考

- CSI Spec：<https://github.com/container-storage-interface/spec>
- Kubernetes CSI 文档
- kubernetes-csi 组织下的官方 driver