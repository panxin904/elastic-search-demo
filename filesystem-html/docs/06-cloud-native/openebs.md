---
title: OpenEBS
---

# OpenEBS — K8s 原生存储利器

> <span class="kg-badge kg-badge--cloud-native">云原生</span>
> cStor / Jiva / Mayastor · 三种引擎可选

OpenEBS 是 MayaData 出品的开源 K8s 存储系统。它把卷拆成**微服务**（与 Longhorn 类似），但提供**三种引擎**：

- **Jiva**：基于 Linux LVM 的用户态复制
- **cStor**：基于 ZFS 的池化存储
- **Mayastor**：NVMe-oF + SPDK 高性能（v3+）

## 1. 三种引擎对比

| 引擎 | 后端 | 性能 | 复杂度 | 状态 |
|------|------|------|--------|------|
| Jiva | LVM / hostpath | 低 | **极低** | 维护中 |
| cStor | ZFS | 中 | 中 | 维护中 |
| Mayastor | NVMe-oF + SPDK | **高** | 高 | 推荐（新） |

## 2. Jiva 架构（最简单）

```
┌──────────────────────────────────────┐
│  Jiva Volume = 1 Pod                 │
│  - jiva-target (主)                  │
│  - jiva-replica × N (副本)           │
└──────────────────────────────────────┘
```

适合：开发 / 测试 / 中小规模。

## 3. cStor 架构

```
┌──────────────────────────────────────────────┐
│  cStor Pool = 1 Pool Pod                     │
│  - 用 1+ 节点上的空闲盘                       │
│  - 每个卷 = 1 个 Volume Pod                   │
│    - target (主)                              │
│    - replica × N                              │
└──────────────────────────────────────────────┘
```

## 4. Mayastor 架构（最新）

```
┌──────────────────────────────────────────────┐
│  Mayastor Pool = 多个节点上的 disk             │
│  - SPDK 用户态 NVMe 驱动                      │
│  - 每个卷横跨多个节点（replica or EC）         │
│  - iSCSI / NVMe-oF 给 K8s                    │
└──────────────────────────────────────────────┘
```

Mayastor 是性能最高的开源 K8s 块存储，定位对标 Rook-Ceph。

## 5. 部署 Jiva（最简单实战）

```bash
helm repo add openebs https://openebs.github.io/charts
helm install openebs openebs/openebs \
    --namespace openebs \
    --create-namespace \
    --set jiva.enabled=true \
    --set cstor.enabled=false \
    --set mayastor.enabled=false
```

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: openebs-jiva
provisioner: openebs.io/provisioner-iscsi
parameters:
  poolType: jiva
  replicaCount: "3"
  volumeType: "Jiva"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-data
spec:
  accessModes: [ReadWriteOnce]
  storageClassName: openebs-jiva
  resources:
    requests:
      storage: 10Gi
```

## 6. 部署 Mayastor

```bash
# 1. 先在每个节点装 SPDK / NVMe 依赖
# 2. 用 lvm 创建 physical volume
pvcreate /dev/sdb
vgcreate mayastor-pool /dev/sdb

# 3. 安装 Mayastor
helm install mayastor openebs/openebs \
    --namespace mayastor \
    --create-namespace \
    --set jiva.enabled=false \
    --set cstor.enabled=false \
    --set mayastor.enabled=true
```

```bash
# 4. 创建磁盘池
kubectl mayastor create disk-pool node1.dev --pool-name pool1 /dev/sdb
```

```yaml
# 5. StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: mayastor
provisioner: io.openebs.csi-mayastor
parameters:
  ioTimeout: "60"
  protocol: "nvmf"
  repl: "3"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

## 7. 快照与备份

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: my-snap
spec:
  volumeSnapshotClassName: openebs-snapclass
  source:
    persistentVolumeClaimName: my-data
---
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: openebs-snapclass
driver: openebs.io/provisioner-iscsi
deletionPolicy: Delete
```

## 8. cStor 实战（推荐中等规模）

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: openebs-cstor
provisioner: cstor.csi.openebs.io
parameters:
  replicaCount: "3"
  cstorPoolName: cstor-pool
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

## 9. 监控

```bash
# 安装 Prometheus + Grafana
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
    --namespace monitoring

# OpenEBS 提供 ServiceMonitor
kubectl apply -f https://openebs.github.io/openebs/v3.0.0/monitoring/prometheus/
```

## 10. Longhorn vs OpenEBS 选型

| 需求 | 推荐 |
|------|------|
| 简单好用 | **Longhorn** |
| Mayastor 高性能 | **OpenEBS Mayastor** |
| cStor 复杂池化 | OpenEBS cStor |
| Jiva 极简单 | OpenEBS Jiva |
| 增量备份 | **Longhorn** 更细 |
| 完整文档 | **Longhorn** 更清晰 |

**实战经验**：先试 **Longhorn**（上手快）；需要更高性能就 **OpenEBS Mayastor** 或 **Rook-Ceph**。

## 11. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 三引擎选 Jiva/cStor/Mayastor | "三引擎=三选一" |
| 每卷一 Pod | "卷=Pod" |
| Mayastor 最强 | "Mayastor=顶配" |
| Jiva 最简 | "Jiva=开发友好" |
| 默认 3 副本 | "副本 3 默认" |

## 参考

- OpenEBS 文档：<https://openebs.io/docs
- Mayastor 设计论文
- OpenEBS GitHub


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
