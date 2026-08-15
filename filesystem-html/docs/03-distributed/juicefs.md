---
title: JuiceFS
---

# JuiceFS — 元数据 / 数据分离的云原生分布式文件系统

> <span class="kg-badge kg-badge--distributed">分布式 FS</span>
> 元数据上 Redis/TiKV · 数据走对象存储 · POSIX 兼容

JuiceFS 是国内团队开源的云原生分布式文件系统，把"元数据"和"数据"分别放到两套独立的系统里：

- **元数据** → Redis / TiKV / MySQL（任意 KV/关系库）
- **数据** → S3 / OSS / COS / MinIO（任意对象存储）

客户端通过 FUSE 暴露成 POSIX 文件系统。它本质是一个**分布式 KV + 对象存储之上的格式引擎**。

## 1. 为什么需要元数据 / 数据分离

传统分布式 FS（HDFS、Ceph）把数据块和元数据都放在"自己"管理的服务器里：

- 集群规模和硬件绑定强
- 运维复杂（多副本、rebalance）
- 难以复用云上的对象存储

JuiceFS 的取舍：

| 维度 | 传统 FS | JuiceFS |
|------|--------|---------|
| 数据落点 | 自管 chunk server | 任意 S3 兼容对象存储 |
| 元数据 | 自管 NameNode/MDS | Redis / TiKV / 数据库 |
| 副本 | 自己副本 → 多机开销 | 对象存储自带 EC / 多 AZ |
| 集群边界 | 强 | **几乎无**（客户端 + 远端） |
| 一致性 | 强 | **强**（通过元数据事务） |

## 2. 核心架构

```
┌────────────────────────────────────────┐
│         POSIX App / Hadoop / K8s       │
└────────────────┬───────────────────────┘
                 │  FUSE
┌────────────────▼───────────────────────┐
│     JuiceFS Client（juicefs mount）    │
└─┬──────────────────┬───────────────────┘
  │ 元数据            │ 数据块 (chunk)
┌─▼────────────┐    ┌▼──────────────┐
│ Redis/TiKV   │    │ S3 / OSS / COS│
│ (KV store)   │    │ (object store)│
└──────────────┘    └───────────────┘
```

- **Chunk**：默认 64 MiB 的逻辑切片
- **Object**：一个 chunk 被切分成若干 4 MiB 对象，顺序写
- **Metadata**：每个文件 = {inode attr, [chunks...]}, chunks 存 `{id, size, [block keys]}`

## 3. 部署形态

### 3.1 自建 Redis / 自有 S3

```bash
# 安装客户端
curl -L https://github.com/juicedata/juicefs/releases/download/v4.9.2/juicefs-4.9.2-linux-amd64.tar.gz \
    | tar -xz -C /usr/local/bin

# 格式化（创建元数据 + 生成配置）
juicefs format \
    --storage s3 \
    --bucket https://s3.amazonaws.com/mybucket \
    --access-key XXX --secret-key YYY \
    redis://1.2.3.4:6379/1 \
    myjfs

# 挂载
juicefs mount -d redis://1.2.3.4:6379/1 /mnt/jfs
```

### 3.2 托管服务（JuiceFS Cloud / OSS + 自建 Redis）

元数据走 JuiceFS 官方的元数据服务，数据走自管 OSS，省运维。

### 3.3 K8s CSI

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: jfs-pv
spec:
  storageClassName: juicefs
  capacity: { storage: 100Gi }
  accessModes: [ReadWriteMany]
  csi:
    driver: csi.juicefs.com
    volumeHandle: myjfs-pv-1
    nodePublishSecretRef:
      name: juicefs-secret
      namespace: default
```

支持 **ReadWriteMany**（多 Pod 同时读写），这是它在 K8s 的最大杀手锏。

## 4. 数据读写路径

**写流程**：

1. Client 拿到 inode → 决定写哪个 chunk（顺序追加）
2. 把 chunk 切成 4 MiB block，对象存储多 part upload
3. 写完后 atomic 更新元数据："新增 block key"

**读流程**：

1. Client 查元数据：`{inode → chunks → block keys}`
2. 并发从 S3 拉 block
3. 拼回 chunk 返回给应用

**强一致保证**：元数据写入走 Redis Lua / TiKV 事务，确保 `{chunks → block keys}` 这条"指针链"原子。

## 5. 性能特性与取舍

| 维度 | JuiceFS 表现 | 备注 |
|------|--------------|------|
| 吞吐 | 受限于对象存储带宽 | 4 MiB block → S3 可线性扩 |
| 延迟 | 较本地盘高（多一跳对象存储） | 配合 Redis 元数据做缓存 |
| 小文件 | **强**（元数据扁平） | 比 HDFS/CephFS 强 10×+ |
| 大文件 | 中（写靠顺序追加） | 改写 = 重写 block |
| 元数据 QPS | 受 Redis / TiKV 容量 | 10w+ QPS 没问题 |
| 跨可用区 | **天然** | 数据在对象存储 AZ |
| 加密 | 客户端 AES/SM4 | 数据离开 client 前加密 |

**关键坑**：写是顺序追加 → **改文件末段之外的位置** = 重写对应 block。这是为元数据事务 + 写吞吐做的取舍。

## 6. 实战命令

```bash
# 看挂载情况
juicefs status /mnt/jfs

# 看统计 / 性能
juicefs profile /mnt/jfs

# 预热（把热数据预取到本地）
juicefs warmup /mnt/jfs/data --threads 32

# 压测
juicefs bench /mnt/jfs

# 卸载
juicefs umount /mnt/jfs
```

## 7. 与 HDFS / CephFS / S3FS 对比

| 维度 | JuiceFS | HDFS | CephFS | S3FS |
|------|---------|------|--------|------|
| 元数据 | 外部 KV | NameNode | MDS | 无（对象键扁平） |
| POSIX 兼容 | **完整** | 完整 | 完整 | **不完整**（无原子 rename 等） |
| 多 Pod 共享 | **支持** | 不支持 | 支持 | 支持 |
| 写延迟 | 中 | 低 | 低 | 高 |
| 适合场景 | 通用 / K8s / AI | Hadoop 离线 | 全场景 | 备份归档 |
| 学习曲线 | **低** | 中 | 高 | 极低 |
| 跨云迁移 | **容易**（换对象存储即可） | 难 | 难 | 容易 |

## 8. 典型落地场景

1. **Kubernetes 共享存储**：多 Pod ReadWriteMany，stateful workload
2. **AI 训练数据集**：HuggingFace / ImageNet 挂在 JuiceFS → 多 worker 并行
3. **数据湖查询加速**：Presto / Hive 直接读 JuiceFS 当作 HDFS 替代
4. **跨云灾备**：对象存储 + 元数据可独立迁移

## 9. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 元数据走 Redis / 数据走 S3 | "元上 KV、底到 S3" |
| 强一致靠元数据事务 | "事务即一致" |
| 写 = 顺序追加 | "只追加、不改写" |
| K8s 杀手锏是 RWX | "RWX 共享救世主" |
| 跨云靠对象存储可拔插 | "换桶即可搬家" |

## 参考

- JuiceFS 官方文档：<https://juicefs.com/docs/>
- 论文：JuiceFS — A Distributed POSIX File System (2021)
- GitHub：<https://github.com/juicedata/juicefs>