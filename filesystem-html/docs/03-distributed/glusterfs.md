---
title: GlusterFS
date: 2026-08-15  # date-auto-injected
---

# GlusterFS — 用户态分布式文件系统

> <span class="kg-badge kg-badge--distributed">分布式 FS</span>
> 无元数据节点 · 弹性哈希 · 用户态 FUSE

GlusterFS（现属 Red Hat / Gluster.org）是一款**完全运行在用户态**的横向扩展文件系统。它不依赖独立的元数据服务器，靠 **弹性哈希（DHT）** 把目录映射到具体 brick，是"轻量、好上手"的代表。

## 1. 为什么 GlusterFS 没有元数据服务

很多分布式 FS（HDFS、CephFS）都有专门的"主控"节点（NameNode / MDS），存放"文件 → 位置"的映射。这会带来两个痛点：

1. **元数据热点**：百万级文件时，元数据节点先成为瓶颈
2. **扩展困难**：提升元数据吞吐往往意味着重新分片

GlusterFS 的解法：

| 维度 | 思路 | 代价 |
|------|------|------|
| 数据定位 | 用文件名 hash → 直接定位 brick | 改名/重命名需要遍历 |
| 一致性 | 最终一致 + 自愈 | 强一致场景不适用 |
| 协议 | 全用户态（FUSE + gfapi） | 内核态性能略差 |

## 2. 核心架构

```
┌──────────────────────────────────────────┐
│         Application / NFS / SMB          │
└─────────────────┬────────────────────────┘
                  │
┌─────────────────▼────────────────────────┐
│      FUSE / libgfapi / gluster client    │
└─────────────────┬────────────────────────┘
                  │
┌─────────────────▼────────────────────────┐
│     Translator Stack（卷模式插件）        │
│  DHT → AFR → Stripe → Posix              │
└─────────────────┬────────────────────────┘
                  │
┌─────────────────▼────────────────────────┐
│       glusterd（管理平面）               │
└──────────────────────────────────────────┘
```

- **Brick**：一个 trusted storage pool 里的一个导出目录，通常就是一块 XFS 文件系统的子目录
- **Volume**：若干 brick 的逻辑组合（distributed / replicated / striped / dispersed）
- **Translator**：模块化的"中间件"，组合方式决定卷行为

## 3. 四种基本卷类型

| 类型 | 类比 | 用途 | 最低 brick 数 |
|------|------|------|--------------|
| **Distributed** | JBOD | 扩容 | 1 |
| **Replicated** | RAID-1 | 副本冗余 | 2（推荐 3） |
| **Striped** | RAID-0 | 大文件聚合带宽 | 2 |
| **Dispersed** | RAID-6/erasure coding | 容量 + 冗余 | k + m |

实战最常见的是 **Distributed-Replicated**（如 4 brick = 2×2，先分布再副本）。

## 4. 实战部署（3 节点）

```bash
# 1. 准备存储后端（每个节点）
mkfs.xfs -i size=512 /dev/sdb
mkdir -p /bricks/brick1
mount /dev/sdb /bricks/brick1

# 2. 安装
yum install -y centos-release-gluster  # 或 glusterfs-server
systemctl start glusterd

# 3. 建立 trusted pool
gluster peer probe node2
gluster peer probe node3
gluster peer status

# 4. 创建 distributed-replicated 卷
gluster volume create gv0 replica 2 \
    node1:/bricks/brick1/gv0 \
    node2:/bricks/brick1/gv0 \
    node3:/bricks/brick1/gv0 \
    node4:/bricks/brick1/gv0 force

# 5. 启动并验证
gluster volume start gv0
gluster volume info gv0
gluster volume status gv0

# 6. 客户端挂载
mount -t glusterfs node1:/gv0 /mnt/gv0
```

## 5. 关键调优参数

```bash
gluster volume set gv0 performance.cache-size 1GB        # 读缓存
gluster volume set gv0 performance.write-behind off      # 写后合并（关掉=强一致）
gluster volume set gv0 network.ping-timeout 30          # 网络抖动判超时
gluster volume set gv0 cluster.self-heal-daemon enable   # 自愈
gluster volume set gv0 features.inode-quota on           # 配额
```

**`write-behind` 取舍**：开启 = 性能↑，宕机丢数据↑；金融/数据库关掉它。

## 6. 自愈（Self-Heal）机制

当某 brick 离线 → 重启后，对应文件被标记 `heal-needed`，后台 `glusterfsd` 触发复制：

```bash
gluster volume heal gv0 info            # 看哪些待修复
gluster volume heal gv0 info summary    # 汇总
gluster volume heal gv0 full            # 强制全量修复
```

**坑**：自愈会消耗网络带宽，建议给 `self-heal-daemon` 单独打 tag 限速（10MB/s），避免影响业务。

## 7. Geo-Replication（异地复制）

把一个 GlusterFS 卷异步复制到远端（一般是另一个 GlusterFS 卷或本地目录）：

```bash
gluster volume geo-replication gv0 \
    ssh://backup-node:/bricks/backup/gv0 \
    geoaccount create push-pem

gluster volume geo-replication gv0 \
    ssh://backup-node:/bricks/backup/gv0 \
    geoaccount config rsync-options "--bwlimit=50M"

gluster volume geo-replication gv0 \
    ssh://backup-node:/bricks/backup/gv0 \
    geoaccount start
```

## 8. 与 HDFS / CephFS 的取舍

| 维度 | GlusterFS | HDFS | CephFS |
|------|-----------|------|--------|
| 元数据 | **无（哈希）** | NameNode（中心） | MDS（可分布） |
| 扩展粒度 | 单 brick | 节点 | 节点 + OSD |
| 一致性 | 最终一致 | 强一致（写成功） | 强一致 |
| 大文件吞吐 | 中 | **极高**（流式批） | 高 |
| 小文件性能 | **优**（无元数据瓶颈） | 差 | 中 |
| 学习曲线 | **低** | 中 | 高 |
| Kubernetes | CSI 第三方 | 无原生 | Rook 原生 |

**典型选型**：

- 备份归档、小文件为主 → **GlusterFS**
- 大数据离线分析（Hadoop） → **HDFS**
- 云原生全场景 → **CephFS**
- 极简 + 改造存量 Linux → **GlusterFS**

## 9. 监控与排障

```bash
gluster volume profile gv0 start   # 开启采样
gluster volume profile gv0 info cumulative | head -50

# 看 brick 级 IO
gluster volume top gv0 read-perf   # 读带宽 Top 文件
gluster volume top gv0 brick-read-perf
gluster volume top gv0 list
```

日志路径：

- 服务端：`/var/log/glusterfs/bricks/gv0-*.log`
- 客户端：`/var/log/glusterfs/mnt-gv0.log`
- 关键错误关键词：`Transport endpoint is not connected`（brick 断链）、`Self-heal`（自愈日志）

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 无元数据 → 弹性哈希 | "Gluster 不背" |
| 副本靠 AFR translator | "AFR=双写保险" |
| 改文件名代价高 | "改名=扫盘" |
| 自愈需要限速 | "heal 必限流" |
| 用户态性能 → 跑 FUSE 调度 | "fuse 调度=内核 cache 命门" |

## 参考

- Gluster Docs: <https://docs.gluster.org/>
- Red Hat Gluster Storage Administration Guide
- 弹性哈希论文：原 Gluster 团队 2005 年早期论文

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 文件系统
- [observability](https://java-px.bot.cd/observability/):存储监控
- [postgresql](https://java-px.bot.cd/postgresql/):PG 存储引擎
