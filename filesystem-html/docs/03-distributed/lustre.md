---
title: Lustre
date: 2026-08-15  # date-auto-injected
---

# Lustre — HPC 领域的高性能并行文件系统

> <span class="kg-badge kg-badge--distributed">分布式 FS</span>
> MDS + OSS · RDMA · HPC 专属

Lustre 名字源自 "Linux + Cluster"，专为 **HPC（高性能计算）** 设计：在 Top 500 超算里，70%+ 的系统曾使用 Lustre 作为主存储。它是**吞吐量之王**，但前提是"专为大文件流式 I/O 准备"。

## 1. Lustre 为什么出现在 HPC

HPC 场景的特征：

- 几十到几万台计算节点
- 单次作业 = 数百节点同时读写同一数据集
- 数据量 PB 级，单文件 TB 级
- 延迟不敏感，**带宽决定生死**

传统 NFS 单服务端扛不住；HDFS NameNode 中心化在大规模下抖动明显。Lustre 走"分而治之"：

| 设计 | 理由 |
|------|------|
| 多 MDS 分担 | 元数据是瓶颈 → 拆分多台 |
| 多 OSS 并行 | 数据分散在 N 个对象存储 |
| RDMA 高速网络 | InfiniBand / RoCE 直接绕过内核 TCP |
| 大条带（stripe） | 一个文件横跨多个 OST |
| 客户端缓存 | 计算节点上有 Page Cache |

## 2. 核心组件

```
┌────────────────────────────────────────┐
│  Lustre Client（kernel module）         │
│  - 计算节点 / 登录节点                  │
└────────────────┬───────────────────────┘
                 │  LNet
┌────────────────▼───────────────────────┐
│  MDS（Metadata Server）                │
│  - 元数据 + DLM（分布式锁）            │
└────────────────┬───────────────────────┘
                 │  LNet
┌────────────────▼───────────────────────┐
│  OSS（Object Storage Server） × N      │
│  - OST（Object Storage Target）        │
│  - 单文件横跨多个 OST                 │
└────────────────────────────────────────┘
```

- **MDS**：1 个（或 HA 主备），维护文件名 → MDT（Metadata Target）对象
- **MDT**：存储元数据，挂在 MDS 上
- **OSS**：多个，每个 OSS 管 1+ OST
- **OST**：底层是普通文件系统（ldiskfs / ZFS），存实际数据条带
- **LNet**：Lustre 的网络层，支持 TCP、InfiniBand、RoCE

## 3. 文件布局：Stripe 是核心

Lustre 把一个文件**横向切条带**（stripe），分布到多个 OST：

```
file size = N (stripe_count) × stripe_size

stripe_count: 文件由几块 OST 组成
stripe_size:  每块 OST 上 stripe 的字节数
```

例如 `stripe_count=4, stripe_size=1MB`，一个 100MB 文件 → 4 个 OST，每个存 25MB（按 1MB 切片循环写）。

```bash
lfs setstripe -c 4 -s 1M /mnt/lustre/job1234/output.dat
lfs getstripe /mnt/lustre/job1234/output.dat
```

**小文件陷阱**：默认 stripe_count=1 → 大量小文件全堆在一个 OST 上，造成热点 → 性能雪崩。

## 4. 部署实战（小型配置）

> **注意**：生产环境必须用专用的 Lustre Installer + RDMA 网卡。小型测试可用 TCP 模式。

### 4.1 系统准备

```bash
# 内核版本对齐（CentOS 8 + Lustre 2.15）
# RHEL 8 系列：kernel ≥ 4.18 匹配
yum install -y kernel-4.18.0-513.5.1.el8_lustre.x86_64

# zfs / ldiskfs 后端
yum install -y lustre-dkms lustre-osd-ldiskfs-mount lustre-osd-zfs-mount
```

### 4.2 配置 MGS/MDS

```bash
# MGS（Management Server）与 MDS 同机
mkfs.lustre --mdt --mgs --fsname=lfs /dev/sda
mount -t lustre /dev/sda /mnt/mdt

# 启动服务
systemctl start lnet
systemctl start ldgssd  # 用于 OSN 鉴权
```

### 4.3 配置 OSS

```bash
# 每个 OSS 至少 1 个 OST
mkfs.lustre --ost --fsname=lfs --mgsnode=mds@tcp0 /dev/sdb
mount -t lustre /dev/sdb /mnt/ost0

# 启动 lnet
lnetctl net add --net tcp0 --if eth0
lctl network up
```

### 4.4 客户端挂载

```bash
lnetctl lnet configure --all
mount -t lustre mds@tcp0:/lfs /mnt/lustre
```

## 5. 性能调优

### 5.1 Stripe 策略

```bash
# 大文件作业：宽条带
lfs setstripe -c 16 -s 16M /scratch/jobA/

# 小文件作业：单条带（避免热点）
lfs setstripe -c 1 -s 4M /scratch/jobB/

# 默认策略（目录级）
lfs setstripe -d -c 8 -s 4M /scratch/jobC/
```

### 5.2 网络与 RPC

```ini
# /etc/modprobe.d/lustre.conf
options lnet networks="tcp0(eth0),o2ib0(ib0)"
options ost oss_io_threads=32
```

### 5.3 客户端缓存

```bash
# 调整 Page Cache 最大占用
lctl set_param llite.*.max_read_ahead_mb=64
lctl set_param llite.*.max_write_ahead_mb=32

# 预读（数据采集场景）
lctl set_param llite.*.read_ahead=2048
```

## 6. 关键管理命令

```bash
# 拓扑信息
lctl dl                    # 设备列表
lctl list_nids             # 本机网络地址

# 配额
lfs quota -u alice /mnt/lustre
lfs quota -u alice -b 100G /mnt/lustre

# 文件状态
lfs getstripe /mnt/lustre/data.bin

# 调试
lctl debug_kernel           # 打开 debug 日志（注意开销）
lctl set_param osc.*.max_rpcs_in_flight=32
```

## 7. 故障模式与运维

| 故障 | 表现 | 处置 |
|------|------|------|
| OSS 宕机 | 该 OST 上的文件 IO 报错 | 客户端自动重路由其他 OST（受副本策略影响） |
| MDS 宕机 | 整个 FS 只读 / 报错 | 切换 HA（主备 MDS） |
| 网卡抖动 | RPC 大量 retry | 排查 IB/RNIC 健康 |
| OST 满 | 写入失败 | 监控 `OST.total` vs `OST.free` |
| MGS 配置漂移 | 多节点不信 | 用同一个 MGS，禁本地 hack |

**重要**：Lustre 没有内置 EC，要在 OST 层用 RAID 或 ZFS RAID-Z 补强。

## 8. 与 HDFS / GPFS / BeeGFS 对比

| 维度 | Lustre | HDFS | GPFS (IBM Spectrum Scale) | BeeGFS |
|------|--------|------|---------------------------|--------|
| 主场景 | HPC 科研 | 大数据 Hadoop | HPC + 企业 | HPC 中小集群 |
| 元数据 | MDS（可 HA） | NameNode | Token Manager | Mgmt（独立） |
| 数据 | OST（横条带） | Block | 数据块 | Storage Server |
| POSIX 兼容 | **完整** | 半 | **完整** | **完整** |
| RDMA | **原生** | 不支持 | 原生 | 原生 |
| 学习曲线 | **陡** | 中 | 陡 | 中 |
| 商业支持 | DDN/华为 | Cloudera/HW | IBM | ThinkParQ |

## 9. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 条带是灵魂 | "Stripe 决定吞吐" |
| 小文件必调 stripe=1 | "小文件防热点" |
| 客户端内核态 | "Lustre 不走 FUSE" |
| 网络是 LNet | "LNet=内部 TCP/IB" |
| HPC 是它的家 | "别拿它跑 Web" |

## 参考

- 官方文档：<https://wiki.lustre.org/>
- Intel Lustre 用户指南（OpenSFS 镜像）
- DDN EXAScaler（商业版）

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 文件系统
- [observability](https://java-px.bot.cd/observability/):存储监控
- [postgresql](https://java-px.bot.cd/postgresql/):PG 存储引擎
