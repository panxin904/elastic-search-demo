---
title: ext4 / xfs / btrfs
date: 2026-08-15  # date-auto-injected
---

# 文件系统对比：ext4 / xfs / btrfs

> Linux 主流文件系统的选型。

## 🆚 横向对比

| | ext4 | xfs | btrfs | zfs |
|--|------|------|-------|------|
| 出品 | Linux 传统 | SGI / RHEL | Oracle (Linux) | Sun / Oracle / Illumos |
| 最大文件 | 16 TiB | 8 EiB | 16 EiB | 16 EiB |
| 最大卷 | 1 EiB | 8 EiB | 16 EiB | 256 ZiB |
| 快照 | ❌（LVM 提供） | ❌（LVM 提供） | ✅ 内置 | ✅ 内置 |
| 数据校验 | ❌ | ✅（metadata） | ✅ | ✅ |
| 在线扩容 | ✅ | ✅ | ✅ | ✅ |
| 在线缩小 | ✅ | ❌ | ❌ | ❌ |
| CoW | ❌ | ✅（仅部分） | ✅ | ✅ |
| 学习成本 | 低 | 低 | 中 | 中 |
| 适用 | 通用 | 大文件 / 数据库 | 容器 / 桌面 | NAS / 关键数据 |

## 🪟 ext4 - 老牌稳定

```bash
# 创建
sudo mkfs.ext4 /dev/sda1

# 挂载选项（默认就好）
defaults,noatime
```

适合：根分区 / 通用 Linux / 桌面。

### 特性

- journaling（日志）
- extent（连续块）
- 灵活块大小（1K-4K）
- 在线扩缩容（resize2fs）

```bash
# 检查（离线）
sudo e2fsck -f /dev/sda1

# 调优
sudo tune2fs -o journal_data_writeback /dev/sda1
sudo tune2fs -l /dev/sda1            # 看 superblock
```

## 📊 xfs - 大文件 / RHEL 默认

```bash
# 创建
sudo mkfs.xfs /dev/sdb1

# 扩（只能扩）
sudo xfs_growfs /data
```

适合：RHEL/CentOS 默认、数据库、大文件（NFS 导出）。

### 特性

- **只能扩不能缩**（这是与 ext4 最大区别）
- 高效大目录
- 元数据日志（journaling）
- 在线碎片整理

```bash
# 碎片整理
sudo xfs_fsr /data
sudo xfs_db /dev/sdb1           # 看使用率

# 修复
sudo xfs_repair /dev/sdb1
```

## 🌲 btrfs - 现代多功能

```bash
# 创建
sudo mkfs.btrfs /dev/sdc1

# 挂载
mount -o compress=zstd:3 /dev/sdc1 /data
```

适合：容器、桌面、NAS、子卷隔离。

### 特性

- 内置快照 / 子卷
- 内置 RAID 0/1/10/5/6（`btrfs balance`）
- 透明压缩（zstd / lzo / zlib）
- 写时复制（CoW）
- 在线去重 / scrub

```bash
# 子卷
sudo btrfs subvolume create /data/sub1
sudo btrfs subvolume list /data

# 快照（几乎瞬时）
sudo btrfs subvolume snapshot -r /data /data/snap-2024

# 压缩
sudo btrfs filesystem defragment -czstd /data

# 状态
sudo btrfs filesystem show
sudo btrfs device stats /dev/sdc1
```

## 🛢 zfs - 服务器级 NAS

zfs 不在主内核，Ubuntu 通过 `zfsutils-linux` 安装。

```bash
sudo apt install zfsutils-linux

# 创建池
sudo zpool create datapool /dev/sdc /dev/sdd
sudo zpool add datapool /dev/sde     # 加盘

# 文件系统
sudo zfs create datapool/data
sudo zfs set compression=zstd datapool/data

# 快照
sudo zfs snapshot datapool/data@now
sudo zfs rollback datapool/data@now

# 看池状态
sudo zpool status
sudo zpool iostat 2
```

适合：NAS、关键数据、快照密集使用。

## 🎯 怎么选

| 场景 | 推荐 |
|------|------|
| Ubuntu 根分区 | ext4（默认） |
| RHEL 根分区 | xfs（默认） |
| 大数据库（>10TB） | xfs |
| 容器存储 | btrfs（snapper / subvolume） |
| NAS / 文件服务器 | zfs |
| 个人 NAS / 服务器兼用 | btrfs |
| 简单稳定不折腾 | ext4 |

## 🪛 实战

```bash
# 创建 ext4
sudo mkfs.ext4 -L data /dev/sdb1
sudo tune2fs -L data /dev/sdb1    # 改 label

# 创建 xfs（高级选项）
sudo mkfs.xfs -f -L data -d agcount=8 -l size=256m /dev/sdb1

# 创建 btrfs（开启压缩）
sudo mkfs.btrfs -L data /dev/sdb1
sudo mount -o compress=zstd:3,noatime /dev/sdb1 /data
sudo btrfs filesystem defragment -r -czstd /data

# 看 UUID
sudo blkid /dev/sdb1
```

## 🔄 转换 / 迁移

```bash
# 备份 → 格式化 → 恢复（推荐停机后做）
sudo rsync -av /data/ /mnt/backup/
sudo umount /data
sudo mkfs.btrfs /dev/sdb1
sudo mount /dev/sdb1 /data
sudo rsync -av /mnt/backup/ /data/

# btrfs-balance 把 RAID 转 RAID5
sudo btrfs balance start -dconvert=raid5 /data
```

## ❓ 常见问题

```bash
# ext4 提示 "has unsupported feature"
# 旧内核不能挂载新内核创建的 ext4（启用新特性时）
# 用 tune2fs 降级：
sudo tune2fs -O ^metadata_csum_seed /dev/sdb1

# xfs 不能缩
# 备份 → 新建更小 → 恢复

# btrfs "ENOSPC" 但 df 还有空间
# CoW + 元数据双占用，subvolume snapshot 残留
sudo btrfs balance start -dusage=80 /data
```

## 🔗 下一步

- [mount / umount](/09-storage/mount)
- [LVM 逻辑卷](/09-storage/lvm)
- [swap 交换分区](/09-storage/swap)