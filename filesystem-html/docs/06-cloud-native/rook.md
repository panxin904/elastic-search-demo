---
title: Rook
---

# Rook — Kubernetes 上的存储编排器

> <span class="kg-badge kg-badge--cloud-native">云原生</span>
> Operator 模式 · Ceph / NFS / Cassandra · 云原生存储管家

Rook 把**分布式存储系统**变成 Kubernetes 上的"原生"服务。它通过 Operator 模式，把 Ceph、NFS、Cassandra、MinIO、EdgeFS 等部署成 K8s 工作负载，并由 K8s 调度管理。

## 1. Rook 是什么

Rook = **Operator + 存储后端**

- **Operator**：K8s 自定义资源（CRD）+ Controller，把存储系统的运维操作变成 K8s API
- **后端**：Ceph / NFS / Cassandra / MinIO（可插拔）

最常用的后端是 **Ceph**——Ceph 通过 Rook 部署，就像数据库 Operator 部署 MySQL/PostgreSQL。

## 2. Rook + Ceph 架构

```
┌──────────────────────────────────────────┐
│  K8s Cluster                             │
│  - rook-ceph-operator                    │
│  - rook-ceph-tools (CLI)                 │
│  - cephcluster CRD                       │
└────────────────┬─────────────────────────┘
                 │ 创建/管理
┌────────────────▼─────────────────────────┐
│  Ceph Cluster                            │
│  - MON (3 pods, Quorum)                  │
│  - MGR (2 pods, active/standby)          │
│  - OSD (1 pod per disk)                  │
│  - MDS (for CephFS)                      │
│  - RGW (for S3)                          │
└────────────────┬─────────────────────────┘
                 │ CSI gRPC
┌────────────────▼─────────────────────────┐
│  CSI Driver                             │
│  - csi-rbdplugin (DaemonSet)             │
│  - csi-cephfsplugin (DaemonSet)          │
│  - csi-rbd / csi-cephfs provisioner      │
└──────────────────────────────────────────┘
```

## 3. 部署实战（最小 3 节点）

### 3.1 准备

每个节点至少 1 块空闲盘：

```bash
lsblk
# sdb       8:16   0  100G  0 disk   ← 这块给 Ceph
```

### 3.2 部署 Rook

```bash
git clone --depth 1 --single-branch --branch release-1.16 \
    https://github.com/rook/rook.git
cd rook/deploy/examples

# 装 operator
kubectl apply -f crds.yaml
kubectl apply -f common.yaml
kubectl apply -f operator.yaml
```

### 3.3 创建 CephCluster

```yaml
apiVersion: ceph.rook.io/v1
kind: CephCluster
metadata:
  name: rook-ceph
  namespace: rook-ceph
spec:
  dataDirHostPath: /var/lib/rook
  cephVersion:
    image: quay.io/ceph/ceph:v18.2.0
  mon:
    count: 3
    allowPerHostAffinities: false
  mgr:
    count: 2
  storage:
    useAllNodes: true
    useAllDevices: true   # 自动用所有空闲盘
  dashboard:
    enabled: true
```

```bash
kubectl apply -f cluster.yaml
kubectl -n rook-ceph get cephcluster
# 等待 HEALTH_OK
```

### 3.4 创建存储池 + StorageClass

```yaml
apiVersion: ceph.rook.io/v1
kind: CephBlockPool
metadata:
  name: replicapool
  namespace: rook-ceph
spec:
  replicated:
    size: 3
    requireSafeReplicaSize: true
---
apiVersion: v1
kind: Secret
metadata:
  name: rook-csi-rbd-provisioner
  namespace: rook-ceph
type: Opaque
stringData:
  userID: provisioner
  userKey: <从 toolbox 获取>
---
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-ceph-block
provisioner: rbd.csi.ceph.com
parameters:
  clusterID: rook-ceph
  pool: replicapool
  imageFormat: "2"
  imageFeatures: layering
  csi.storage.k8s.io/provisioner-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/nodeplugin-secret-name: rook-csi-rbd-provisioner
  reclaimPolicy: Delete
  allowVolumeExpansion: true
```

## 4. 创建 CephFS（共享文件系统）

```yaml
apiVersion: ceph.rook.io/v1
kind: CephFilesystem
metadata:
  name: myfs
  namespace: rook-ceph
spec:
  metadataPool:
    replicated:
      size: 3
  dataPools:
    - replicated:
        size: 3
  metadataServer:
    activeCount: 2
```

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-cephfs
provisioner: cephfs.csi.ceph.com
parameters:
  clusterID: rook-ceph
  fsName: myfs
  pool: myfs-data0
  csi.storage.k8s.io/provisioner-secret-name: rook-csi-cephfs-provisioner
  csi.storage.k8s.io/nodeplugin-secret-name: rook-csi-cephfs-provisioner
reclaimPolicy: Delete
```

## 5. 创建 S3 (RGW)

```yaml
apiVersion: ceph.rook.io/v1
kind: CephObjectStore
metadata:
  name: my-store
  namespace: rook-ceph
spec:
  dataPool:
    failureDomain: host
    replicated:
      size: 3
  metadataPool:
    replicated:
      size: 3
  preservePoolsOnDelete: false
  gateway:
    type: s3
    sslCertificateRef: ""
    port: 80
    securePort: 443
  hosting:
    endpoint: s3.example.com
    dnsNames:
      - s3.example.com
```

```bash
kubectl apply -f object-store.yaml

# 创建用户
kubectl -n rook-ceph exec deploy/rook-ceph-tools -- radosgw-admin user create \
    --uid=alice --display-name="Alice" --access-key=alice --secret-key=secret123
```

## 6. 实战：StatefulSet 用 Rook Ceph

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  replicas: 3
  serviceName: postgres
  selector: { matchLabels: { app: postgres } }
  template:
    metadata: { labels: { app: postgres } }
    spec:
      containers:
      - name: postgres
        image: postgres:15
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata: { name: data }
    spec:
      accessModes: [ReadWriteOnce]
      storageClassName: rook-ceph-block
      resources:
        requests:
          storage: 100Gi
```

## 7. 运维工具

```bash
# Toolbox
kubectl apply -f toolbox.yaml
kubectl -n rook-ceph exec deploy/rook-ceph-tools -- ceph -s
kubectl -n rook-ceph exec deploy/rook-ceph-tools -- ceph osd tree
kubectl -n rook-ceph exec deploy/rook-ceph-tools -- ceph df

# Dashboard
kubectl -n rook-ceph get svc | grep dashboard
# 改 svc 为 NodePort / Ingress

# 扩 OSD（加新盘 / 新节点）
# 在 cluster.yaml 加 nodes / devices，重启 Operator
kubectl -n rook-ceph exec deploy/rook-ceph-tools -- ceph osd pool set replicapool pg_num 256
```

## 8. 监控

```bash
# Prometheus 抓取规则
kubectl apply -f deploy/examples/monitoring/

# ServiceMonitor 自动发现
```

**关键指标**：

| 指标 | 含义 |
|------|------|
| `ceph_health_status` | 集群健康 |
| `ceph_osd_up` | OSD 在线数 |
| `ceph_pool_bytes_used` | 池用量 |
| `ceph_pg_state` | PG 状态 |
| `ceph_mon_quorum_status` | MON 法定人数 |

## 9. 故障恢复

| 故障 | 处置 |
|------|------|
| MON 挂了 1 个 | 自动选新 leader |
| OSD 挂了 | CRUSH 自动迁移数据 |
| 节点整体挂了 | 数据还在 → 把 OSD Pod 调度到其他节点 |
| 整个集群挂 | 从备份恢复 + bootstrap |

**关键**：Rook 把 Ceph 的运维"运维化"——通过 K8s 控制器自动化恢复。

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| Operator = K8s 化 Ceph | "Rook=Operator+Ceph" |
| 3 节点是最低门槛 | "3 节点 = MON 法定" |
| RBD=块 / CephFS=共享 / RGW=S3 | "三态 Ceph" |
| Toolbox 是必备工具 | "Toolbox=金手铐" |
| 让 K8s 帮你恢复 | "自愈=Operator" |

## 参考

- Rook 文档：<https://rook.io/docs/rook/latest/
- Ceph 官方文档
- rook-examples（GitHub）


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 文件系统
- [observability](https://java-px.bot.cd/observability/):存储监控
- [postgresql](https://java-px.bot.cd/postgresql/):PG 存储引擎
