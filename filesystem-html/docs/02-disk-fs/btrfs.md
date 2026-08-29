---
title: Btrfs COW与快照
date: 2026-08-15  # date-auto-injected
---

# Btrfs COW 与快照

<span class="kg-badge kg-badge-disk-fs">本地盘</span>

B-tree FS——为快照、校验、子卷而生的现代 FS。

## 核心设计

Btrfs 全称 **B-tree File System**，核心思想：
- 所有元数据用 B-tree
- **写时复制（COW）**：写新位置，原子切指针
- 内置快照 / 子卷 / 校验和

## COW（Copy-on-Write）

```c
write("/file", data)
  → 写到新位置（不是覆盖旧块）
  → 写新元数据指针
  → commit 后指针切换
  → 旧版本仍存在（成"快照"）
```

**优势**：
- 写过程 crash-safe（旧版本完整）
- 天然支持快照
- 减少 fsck 需要

**代价**：
- 写放大（一次写产生多份元数据更新）
- SSD 上需要配合 TRIM

## 子卷（Subvolume）

子卷是 Btrfs 的"逻辑卷"，类似独立的 FS 树：

```bash
# 创建子卷
mkfs.btrfs /dev/sdb1
mount /dev/sdb1 /mnt
btrfs subvolume create /mnt/@root
btrfs subvolume create /mnt/@home
btrfs subvolume create /mnt/@snapshots

# 子卷是独立挂载点
mount -o subvol=@root /dev/sdb1 /
mount -o subvol=@home /dev/sdb1 /home
```

**优势**：
- 一个磁盘上的多个 FS（共享空闲空间池）
- 子卷快照几乎瞬时（COW）
- 比 LVM 轻量

## 快照（Snapshot）

```bash
# 创建快照（几乎瞬时）
btrfs subvolume snapshot /mnt/@home /mnt/@snapshots/home-2026-08-08

# 读写快照
mount -o subvol=@snapshots/home-2026-08-08 /dev/sdb1 /mnt/snap

# 删除快照
btrfs subvolume delete /mnt/@snapshots/home-2026-08-08

# 独立快照（不与原卷同步删除）
btrfs subvolume snapshot -r /mnt/@home /mnt/@backup
# -r 表示只读
```

## RAID 与多设备

Btrfs 内置软件 RAID（不依赖 mdadm）：

```bash
# RAID1（mirror）
mkfs.btrfs /dev/sdb1 /dev/sdc1
mount /dev/sdb1 /mnt

# RAID0（stripe）
mkfs.btrfs -m raid0 -d raid0 /dev/sdb1 /dev/sdc1
# -m 元数据 RAID 级别
# -d 数据 RAID 级别

# 添加设备
btrfs device add /dev/sdd1 /mnt
btrfs balance start /mnt   # 数据重平衡

# 替换设备（模拟 RAID 重build）
btrfs replace start /dev/sdb1 /dev/sdb-new /mnt
```

## 校验和（Checksum）

```bash
# 在线校验
btrfs scrub start /mnt
btrfs scrub status /mnt
# scrub = 读所有数据，验证 checksum

# 看 checksum 算法
btrfs inspect-internal checksum /mnt
```

**重要性**：检测"bit rot"（磁盘静默数据损坏）。ZFS 是鼻祖，Btrfs 跟进。

## 压缩

```bash
# 透明压缩（zstd 推荐）
mount -o compress=zstd:3 /dev/sdb1 /mnt
# 等级 1-15，3 是常用默认
# 显著节省空间，对 IO 影响很小

# 多种压缩算法
# zstd：压缩率 + 速度平衡
# lzo：快，压缩率低
# zlib：高压缩率，慢
```

## 发送/接收（Send/Receive）

```bash
# 完整快照导出
btrfs send /mnt/@snapshots/home-2026-08-08 > /backup/snap.btrfs

# 接收
btrfs receive /mnt/restored < /backup/snap.btrfs

# 增量发送（基于父快照）
btrfs send -p /mnt/@snapshots/home-old /mnt/@snapshots/home-new > /backup/incr.btrfs
# 极大节省备份带宽
```

## 配额（Quota）

```bash
# 启用配额
btrfs quota enable /mnt

# 给子卷设限制
btrfs qgroup limit 100G /mnt/@home

# 看配额
btrfs qgroup show /mnt
```

## 实战：openSUSE 风格的 root FS

```bash
# 经典的 Btrfs root 布局（openSUSE Tumbleweed）
mkfs.btrfs /dev/sda2
mount /dev/sda2 /mnt
btrfs subvolume create /mnt/@          # 根
btrfs subvolume create /mnt/@home      # 用户
btrfs subvolume create /mnt/@snapshots # 快照

# 卸载，挂载子卷
umount /mnt
mount -o subvol=@,compress=zstd /dev/sda2 /mnt
mkdir -p /mnt/{home,.snapshots}
mount -o subvol=@home /dev/sda2 /mnt/home
mount -o subvol=@snapshots /dev/sda2 /mnt/.snapshots

# snapper 自动快照管理
zypper install snapper
snapper -c root create-config /
snapper create -d "before update"
```

## Btrfs 的争议与现状

**优点**：
- 快照、子卷、COW、压缩、校验、内置 RAID
- 比 ZFS 轻量（Linux 内核原生）

**缺点**：
- 历史上有稳定性问题（2014-2018）
- RAID5/6 实现曾被认为不稳定（已修复但被批评过晚）
- 碎片问题（COW FS 通病）
- 大 FS 性能不如 ext4/XFS（某些场景）

**现状**：
- openSUSE 默认 FS
- Fedora / RHEL 支持但不默认
- SUSE 投入最多开发资源

## 与 ZFS 对比

| 特性 | Btrfs | ZFS |
|------|-------|-----|
| 校验和 | ✅ | ✅ |
| COW | ✅ | ✅ |
| 快照 | ✅ | ✅ |
| 内置 RAID | ✅（RAID 0/1/10/5/6） | ✅（RAID-Z1/2/3） |
| 压缩 | ✅（zstd/lzo） | ✅（lz4/zstd） |
| 最大单卷 | 16 EiB | 256 ZiB |
| ARC 缓存 | ❌ | ✅（自适应内存缓存） |
| 跨平台 | Linux only | Linux/FreeBSD/macOS |
| 许可证 | GPL | CDDL（与 GPL 不兼容）|
| 默认生产 | openSUSE | FreeBSD / Solaris / NAS |

## 关键 takeaway

| 适合 | 不适合 |
|------|--------|
| 需要频繁快照 | 极致写入性能（数据库 raw device） |
| 子卷管理 | 大型 HPC（XFS 更稳） |
| NAS / 家用服务器 | ZFS 已有场景（CDDL 偏好） |
| 校验和检测静默损坏 | RAID5/6 生产（除非最新版）|


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
