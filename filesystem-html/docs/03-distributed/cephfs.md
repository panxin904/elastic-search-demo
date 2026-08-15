---
title: CephFS 统一存储
---

# CephFS 统一存储

<span class="kg-badge kg-badge-distributed">分布式</span>

Ceph 的 POSIX 文件系统——统一块/对象/文件三种接口的存储平台。

## Ceph 架构

Ceph 提供三种存储接口：

```
                ┌── RBD（块设备）
                │
Ceph Storage ──┼── RGW（对象存储，S3 兼容）
   Cluster     │
                └── CephFS（POSIX 文件系统）
```

**核心**：所有接口共享底层 **RADOS**（可靠自主分布式对象存储）。

```
Clients (RBD/RGW/CephFS)
  ↓
LIBRADOS / librgw / libcephfs
  ↓
RADOS（CRUSH 算法 + OSD 集群）
  ↓
OSD（Object Storage Daemon） = 磁盘
```

## CephFS 组件

```
MDS（Metadata Server）       ← 管理 FS 元数据
  ↓
ceph-fuse / kernel client   ← 客户端挂载
  ↓
MDS Cluster（多 MDS 高可用）
```

- **MDS**：把元数据树切分（dirfrag）分给不同 MDS
- **客户端**：直接和 OSD 通信读写数据（数据路径不经过 MDS）
- **快照**：依赖 RADOS 的快照能力

## CRUSH 算法

CRUSH = **Controlled Replication Under Scalable Hashing**。

```
文件 → hash(filename) → PG（Placement Group）→ OSD 列表

PG = 存储池的逻辑分片（默认 128 PG / pool）
OSD = 一块物理磁盘
```

**特点**：
- 无中心查找表（vs HDFS NameNode）
- 计算分布 → 任意节点可独立计算
- 故障域权重（rack / room / dc）

```bash
# CRUSH map 示例
rule replicated_ruleset {
    ruleset 0
    type replicated
    min_size 1
    max_size 10
    step take default
    step chooseleaf firstn 0 type host
    step emit
}
```

## 实战：部署 CephFS

```bash
# 假设已部署 Ceph 集群（至少 3 节点）

# 1. 创建元数据池
ceph osd pool create cephfs_metadata 32 32
# 32 = PG 数（建议 pg_num = 128 * (OSD数 / 副本数)）

# 2. 创建数据池
ceph osd pool create cephfs_data 128 128

# 3. 创建 FS
ceph fs new mycephfs cephfs_metadata cephfs_data

# 4. 启动 MDS（每个 FS 一个 MDS 守护进程）
ceph-deploy mds create node1

# 5. 客户端挂载
mount -t ceph node1:6789:/ /mnt/cephfs -o name=admin,secret=AQB...
# 或用 ceph-fuse（用户态，更易调试）
ceph-fuse /mnt/cephfs
```

## CephFS 的能力

### 快照

```bash
# 创建目录快照
mkdir /mnt/cephfs/dir
# 写入数据
echo "data" > /mnt/cephfs/dir/file.txt
# 快照（隐藏目录）
mkdir /mnt/cephfs/dir/.snap/snap1
# 看快照
ls /mnt/cephfs/dir/.snap/snap1/
```

### 配额

```bash
# 给子树设配额
ceph-fuse /mnt/cephfs --client-quota
setfattr -n ceph.quota.max_bytes -v 1000000000 /mnt/cephfs/dir
# 1 GB 配额
```

### 客户端能力

```bash
# 在 cephx 中给客户端精细授权
ceph auth add client.alice \
    mon 'allow r' \
    osd 'allow rw pool=cephfs_data' \
    mds 'allow rw path=/home/alice'
```

## CephFS 与 HDFS 对比

| 维度 | HDFS | CephFS |
|------|------|--------|
| 元数据 | NameNode（单/HA） | MDS（多节点分片） |
| 扩展性 | 受 NameNode 内存限 | MDS 可横向扩展 |
| 数据访问 | 顺序写为主 | 随机读写都支持 |
| POSIX 兼容 | ❌ | ✅ |
| 多接口 | ❌ | ✅（块/对象/文件）|
| 协议 | HDFS RPC | libcephfs / kernel / FUSE |
| 部署 | Hadoop 集群 | 通用存储 |

## 性能特征

```bash
# 顺序写（4MB 块）
# ~500 MB/s / OSD
# 100 OSD 集群 = 50 GB/s

# 4KB 随机读 IOPS
# ~5K-10K / OSD（受限于网络和 Journal）
```

**调优要点**：
- 用 NVMe 做 WAL/DB（BlueStore）
- 调整 PG 数（太大浪费内存，太小热点）
- 网络分离（cluster + public）
- Jumbo frames（MTU 9000）

## 数据保护

### 副本模式（replicated）

```bash
ceph osd pool set cephfs_data size 3   # 3 副本
# 数据 = 3 倍磁盘占用
# 容忍任意 2 盘故障
```

### 纠删码模式（EC）

```bash
# 创建 EC 池
ceph osd pool create ec_data 64 64 erasure
ceph osd pool set ec_data crush_roots my-root

# EC profile：k + m（数据块 + 校验块）
# erasure-code-profile set ec-profile k=4 m=2
# 4 数据 + 2 校验 = 1.5 倍空间
# 容忍任意 2 盘故障
```

EC vs 副本：
- 副本：性能好，空间浪费
- EC：空间省，写性能差（小写）

## 配额与回收站

```bash
# 配额（基于目录）
ceph.quota.max_bytes  # 字节限制
ceph.quota.max_files  # 文件数限制

# 回收站
ceph fs dump  # 看 FS 配置
# CephFS 默认不开回收站，需要手动管理
```

## CephFS 实战：Kubernetes PV

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: cephfs-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteMany
  cephfs:
    monitors:
      - "10.0.0.1:6789"
      - "10.0.0.2:6789"
      - "10.0.0.3:6789"
    path: /volumes/kubernetes/pv
    user: kube
    secretRef:
      name: ceph-secret
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
```

## Ceph 演进

- **Luminous (12.x)**：BlueStore 默认，简化部署
- **Nautilus (14.x)**：iSCSI gateway、CephFS 快照改进
- **Octopus (15.x)**：镜像、RBD 改进
- **Pacific (16.x)**：cephadm 一键部署、容器化
- **Quincy (17.x)**：CephFS 多活 MDS、改进 EC

## 关键 takeaway

| 优势 | 劣势 |
|------|------|
| 统一存储（块/对象/文件） | 部署运维复杂 |
| 无单点（CRUSH + MDS 分片） | 小文件性能中等 |
| POSIX 兼容 | 监控调优需要专业知识 |
| 自带 RGW（S3 兼容） | 与 Kubernetes 集成需手动配置 |
| 横向扩展强 | 历史版本升级坑多 |