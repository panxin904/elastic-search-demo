---
title: ZFS 企业级
---

# ZFS 企业级

<span class="kg-badge kg-badge-disk-fs">本地盘</span>

终极文件系统的代表——128-bit 地址空间、内置 RAID-Z、自愈校验、ARC 缓存。

## 历史

ZFS 由 Sun Microsystems 在 2005 年发布，因 CDDL 许可证与 GPL 不兼容，未能并入 Linux 内核。Linux 上通过 **OpenZFS** 项目独立提供（作为内核模块）。

## 核心理念

> "ZFS 终极目标：消灭所有文件系统问题。"

设计原则：
- **集成卷管理 + FS**：不再需要 LVM
- **端到端校验**：每块数据都有 checksum
- **自愈**：检测到错误自动从副本修复
- **简单命令**：一个 `zfs` 管所有

## 架构层次

```
ZFS Pool（zpool）              ← 等同于 LVM VG
├── vdev（虚拟设备）           ← 可以是单盘 / mirror / raidz
│   ├── /dev/sdb1
│   ├── /dev/sdc1
│   └── /dev/sdd1
└── Dataset（数据集）           ← 等同于 LV + FS
    ├── tank/home              ← mount 到 /home
    ├── tank/data              ← mount 到 /data
    └── tank/snapshots/...
```

**关键**：ZFS pool 自己管理设备，不需要传统 fdisk/mkfs/LV 步骤。

## 创建与基本操作

```bash
# 创建 pool
zpool create tank /dev/sdb1
# 自动 mount 到 /tank

# 创建 dataset
zfs create tank/home
zfs create tank/data

# 设挂载点
zfs set mountpoint=/home tank/home

# 看 pool 状态
zpool status tank
# 输出池结构、vdev、健康状态

# 看 dataset
zfs list
```

## RAID-Z（ZFS 的软 RAID）

```bash
# RAID-Z1（单校验，类似 RAID5）
zpool create tank raidz1 /dev/sdb1 /dev/sdc1 /dev/sdd1
# 允许 1 盘故障

# RAID-Z2（双校验，类似 RAID6）
zpool create tank raidz2 /dev/sdb1 /dev/sdc1 /dev/sdd1 /dev/sde1
# 允许 2 盘同时故障

# RAID-Z3（三校验）
zpool create tank raidz3 /dev/sdb1 ... /dev/sdg1
# 允许 3 盘同时故障
```

**vs 硬件 RAID**：
- ✅ 知道 FS 结构 → 不一致时能自我修复
- ✅ 校验和 vs RAID 5 的"silent corruption"
- ❌ 性能略差（软件实现）
- ❌ 不能用硬件 RAID 卡的 BBU 缓存

## 快照与克隆

```bash
# 快照（瞬时）
zfs snapshot tank/home@2026-08-08

# 列出快照
zfs list -t snapshot

# 访问快照
ls /home/.zfs/snapshot/2026-08-08/

# 回滚
zfs rollback tank/home@2026-08-08

# 克隆（可写副本）
zfs clone tank/home@2026-08-08 tank/home-test
# 修改克隆不影响原快照

# 销毁快照
zfs destroy tank/home@2026-08-08
```

## 发送/接收

```bash
# 全量发送
zfs send tank/home@2026-08-08 > /backup/snap.zfs

# 接收
zfs receive backup/home < /backup/snap.zfs

# 增量发送
zfs send -i tank/home@2026-08-01 tank/home@2026-08-08 > /backup/incr.zfs
```

## 压缩与去重

```bash
# 启用 zstd 压缩（推荐）
zfs set compression=zstd tank/data
# 对大部分数据几乎无性能影响

# 启用去重（慎用！）
zfs set dedup=on tank/data
# 内存需求极大（每 1TB 数据需 ~5GB 内存存 dedup table）
# 生产中通常不开
```

## ARC 缓存

ZFS 自适应替换缓存（ARC）使用**空闲 RAM** 作为读缓存：

```bash
# 查看 ARC 状态
arc_summary
# 输出：
# ARC summary: (HEALTHY)
# Memory Throttle Count: 0
# ARC Size: 87.5%  14.01 GiB
# Target Size: (Adaptive) 100.00%
# ...

# 调整 ARC 最大值
echo "options zfs zfs_arc_max=8589934592" > /etc/modprobe.d/zfs.conf
# 限制 8 GB（避免吃光 RAM）
```

**L2ARC**：用 SSD 做二级 ARC 缓存（冷数据 → SSD → HDD）。

**ZIL**：独立日志设备，写加速（通常用 NVMe）。

## 自愈（Self-Healing）

```bash
# 触发 scrub（在线校验）
zpool scrub tank

# 看进度
zpool status -v tank

# 模拟磁盘损坏
mdadm --fail /dev/sdc1    # 如果硬件 RAID 不行
# 实际：直接拔线 / 写错误块

# ZFS 会：
# 1. 检测到错误（checksum 不匹配）
# 2. 从其他 vdev 副本读取正确数据
# 3. 自动写入正确数据修复
# 4. 在 zpool status 中报告修复事件
```

## 实战：家用 NAS 配置

```bash
# 4 盘位，2 盘故障容忍
zpool create nas-pool raidz2 /dev/sda /dev/sdb /dev/sdc /dev/sdd

# 启用压缩
zfs set compression=zstd-3 nas-pool

# 数据集
zfs create nas-pool/photos
zfs create nas-pool/videos
zfs create nas-pool/backups

# 配额
zfs set quota=2T nas-pool/backups

# 每周自动 scrub
echo "0 3 * * 0 zpool scrub nas-pool" | crontab -

# 快照策略（zfs-auto-snapshot）
apt install zfs-auto-snapshot
systemctl enable zfs-auto-snapshot-hourly.timer
```

## ARC vs Page Cache

两个独立的缓存机制：
- **ARC**（ZFS 内）：直接管理，精确统计
- **Page Cache**（Linux 内核）：通用缓存

ZFS 不使用 Linux Page Cache（用 ARC 代替）。这是双刃剑：
- ✅ ARC 更智能（知道哪些是 L2ARC 候选）
- ❌ 内存压力下 ARC 可能挤占其他进程

## ZFS 的限制

| 限制 | 值 |
|------|-----|
| 单 vdev 最大 | 2^64 bytes |
| 单 pool 最大 | 2^78 bytes |
| 单 dataset 最大 | 2^78 bytes |
| 文件名最大 | 255 字节 |
| 单文件最大 | 16 EiB |
| 实际部署上限 | 几 EB（取决于内存） |

## 性能调优

```bash
# 内存调整
zfs_arc_max                # ARC 上限
zfs_prefetch_disable       # 关预取（数据库）
zfs_txg_timeout            # 事务组提交间隔（默认 5s）

# 数据库场景：关预取
echo "options zfs zfs_prefetch_disable=1" > /etc/modprobe.d/zfs.conf

# NFS 性能
zfs set sync=standard tank/nfs  # 默认
zfs set sync=always tank/nfs    # 强制同步（最慢）
zfs set sync=disabled tank/nfs  # 关 fsync（最快，最不安全）
```

## 实战：ZFS + LXC/KVM

```bash
# 给 VM 提供 ZFS 卷（zvol）
zfs create -V 100G tank/vm-disk
# 创建 100G 块设备

# 作为 KVM 磁盘
<disk type='block' device='disk'>
  <source dev='/dev/zvol/tank/vm-disk'/>
  <target dev='vda' bus='virtio'/>
</disk>

# 性能优化
zfs set primarycache=metadata tank/vm-disk
zfs set secondarycache=metadata tank/vm-disk
# 只缓存元数据，数据由 VM 自己缓存
```

## 关键 takeaway

| 优势 | 劣势 |
|------|------|
| 端到端校验 + 自愈 | CDDL 与 GPL 不兼容（不出现在 Linux 内核） |
| 内置 RAID-Z | 学习曲线陡 |
| ARC 智能缓存 | dedup 内存需求恐怖 |
| 快照 / 克隆原生 | 大内存依赖（< 8GB RAM 不推荐） |
| 业界 20+ 年验证 | 比硬件 RAID 性能略低 |

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [linux](https://java-px.bot.cd/linux/):Linux 文件系统
- [observability](https://java-px.bot.cd/observability/):存储监控
- [postgresql](https://java-px.bot.cd/postgresql/):PG 存储引擎
