---
title: NTFS / FAT / exFAT
date: 2026-08-15  # date-auto-injected
---

# NTFS / FAT / exFAT

<span class="kg-badge kg-badge-disk-fs">本地盘</span>

Windows 世界的文件系统——从软盘到现代 SSD。

## 历史时间线

```
FAT12 (1980)        软盘
  ↓
FAT16 (1984)        早期硬盘
  ↓
FAT32 (1996)        Win95 OSR2+
  ↓
NTFS 1.0 (1993)     Windows NT 3.1
  ↓
NTFS 3.1 / v5 (2000) Windows 2000+ （NTFS 5.0）
  ↓
NTFS 3.1 + 改进     Windows 10/11 （当前）
  ↓
exFAT (2006)        闪存/U盘
```

## FAT32

**File Allocation Table 32**——最简单的 FS 之一。

### 结构

```
保留区 | FAT 表（两份） | 数据区
```

- 簇（cluster）：最小分配单位
- FAT 表：每个簇一个 entry，记录"下一个簇号"或"EOF"

### 限制

| 限制 | 值 |
|------|-----|
| 单文件最大 | 4 GB - 1 字节 |
| 单卷最大 | 2 TB（实际 Windows 格式化 32 GB） |
| 文件名最大 | 8.3（短名）或 255（VFAT 长名） |
| 文件数 | 根目录固定 512 项 |

### 仍在使用的原因

- U盘 / SD 卡（兼容性最好）
- 路由器、相机等嵌入式设备
- BIOS 启动分区（UEFI 仍需 FAT32）

### Linux 访问

```bash
# 内核支持
mount -t vfat /dev/sdb1 /mnt/usb

# 修复
fsck.vfat /dev/sdb1

# 创建
mkfs.vfat -F 32 /dev/sdb1
```

## exFAT

**Extended FAT**——为闪存优化的现代 FAT。

### 改进

- 单文件 > 4GB ✅
- 单卷 > 32GB ✅
- 时间戳精度到 10ms
- 支持 ACL
- 文件名 UTF-16

### 限制

- 单卷最大 128 PiB（实际无意义）
- 单文件最大 16 EiB
- 没有日志（断电可能损坏）

### Linux 支持

```bash
# 内核 5.4+ 默认包含 exFAT
mount -t exfat /dev/sdb1 /mnt/usb

# 旧内核需要 exfat-fuse
apt install exfat-fuse

# 创建
mkfs.exfat /dev/sdb1
mkfs.exfat -L "MyDrive" /dev/sdb1
```

## NTFS

**New Technology File System**——Windows 的现代主力。

### 核心特性

#### 1. MFT（Master File Table）

NTFS 用 MFT 存储所有元数据。每个文件至少一个 MFT entry（1024 字节）。

```
MFT Entry 0:  $MFT          # MFT 自身
MFT Entry 1:  $MFTMirr       # MFT 镜像
MFT Entry 2:  $LogFile       # 日志
MFT Entry 3:  $Volume        # 卷信息
MFT Entry 4:  $AttrDef       # 属性定义
MFT Entry 5:  .              # 根目录
MFT Entry 6+: 用户文件
```

**关键**：小文件可以直接存在 MFT entry 中（resident data）。

#### 2. 日志（$LogFile）

NTFS 日志化，类似 ext4 journal：

```
NTFS 写流程：
1. 把改动写入 $LogFile
2. 提交（commit）
3. 实际修改 MFT/data
```

断电后通过日志恢复。

#### 3. USN Journal（Update Sequence Number Journal）

记录所有文件改动，给备份软件、索引服务使用：

```cmd
fsutil usn queryjournal C:
```

#### 4. Alternate Data Streams（ADS）

NTFS 独有特性——一个文件可以有多个"数据流"：

```cmd
echo "秘密" > file.txt:hidden
# file.txt 是正常文件
# file.txt:hidden 是隐藏流
# dir 看不到，但可以读写
```

Linux 访问：
```bash
mount -t ntfs-3g /dev/sdb1 /mnt
ls /mnt/file.txt
# 默认看不到 ADS

# 需要 getfattr -h
getfattr -h -n system.ntfs_attrib_be /mnt/file.txt
```

#### 5. 权限与 ACL

NTFS ACL 比 POSIX rwx 更细：

- 所有者、子用户、组、Everyone 四类
- 每类有 14 种权限（完全控制、修改、读取、写入、读取执行...）
- 继承规则（parent → child）

```cmd
icacls C:\Users
# 显示详细 ACL
```

#### 6. 压缩与加密

```cmd
# 压缩
compact /c C:\path\file.txt
# NTFS 压缩（LZNT1 算法）

# 加密（EFS）
cipher /e C:\Users\Alice\Documents
# 透明加密
```

#### 7. 配额（Quota）

```cmd
fsutil quota modify C: 104857600 DOMAIN\User
# 设置 100GB 配额
```

### NTFS 限制

| 限制 | 值 |
|------|-----|
| 单卷最大 | 256 TB（理论），实际受 Windows 版本限制 |
| 单文件最大 | 16 TB（理论），受实际卷大小限制 |
| 文件名最大 | 255 字符（UTF-16） |
| 时间戳精度 | 100ns |
| 簇大小 | 512B - 64KB |

### Linux 访问

```bash
# 传统 ntfs-3g（用户态，FUSE）
apt install ntfs-3g
mount -t ntfs-3g /dev/sdb1 /mnt

# 现代 ntfs3（内核态，性能更好，kernel 5.15+）
mount -t ntfs3 /dev/sdb1 /mnt

# 写入 NTFS（需要用户映射）
mount -t ntfs-3g -o uid=1000,gid=1000 /dev/sdb1 /mnt

# 修复
ntfsfix /dev/sdb1

# 看信息
ntfsinfo -m /dev/sdb1
```

## 各 FS 对比

| 特性 | FAT32 | exFAT | NTFS |
|------|-------|-------|------|
| 单文件上限 | 4 GB | 16 EiB | 16 TB |
| 单卷上限 | 32 GB（实际）| 128 PiB | 256 TB |
| 日志 | ❌ | ❌ | ✅ |
| 权限 | ❌ | ❌ | ✅ |
| 加密 | ❌ | ❌ | ✅（EFS） |
| 压缩 | ❌ | ❌ | ✅（LZNT1） |
| ADS | ❌ | ❌ | ✅ |
| U盘兼容 | ✅✅ | ✅ | ⚠️ |
| 大文件（>4GB）| ❌ | ✅ | ✅ |
| Linux 原生读 | ✅ | ✅（5.4+）| ✅（ntfs3）|
| Linux 原生写 | ✅ | ✅ | ⚠️（ntfs-3g / ntfs3）|

## 选型决策

```
要 Windows + Linux 共享？
├── U盘/小文件 → exFAT
├── 大文件 + 兼容性优先 → exFAT
└── 仅 Windows + 需要权限/加密 → NTFS

仅 Windows 系统盘？
└── NTFS（必须）

仅 Linux 系统盘？
└── ext4 / XFS / Btrfs

跨平台最大兼容性（USB 设备）？
└── exFAT（FAT32 因 4GB 限制已被淘汰）
```

## 实战：双系统共享盘

```bash
# Linux 创建 NTFS 分区
mkfs.ntfs -L "Shared" /dev/sdb1
# 或
mkntfs -F -L "Shared" /dev/sdb1

# Linux 自动挂载
# /etc/fstab
/dev/sdb1 /mnt/shared ntfs-3g defaults,uid=1000,gid=1000,umask=022 0 0

# Windows 访问（自动识别）
```

## 关键 takeaway

| FS | 何时用 |
|----|--------|
| **FAT32** | 几乎不用了（4GB 限制） |
| **exFAT** | U盘、SD 卡、跨平台 |
| **NTFS** | Windows 系统盘、大文件、ACL 需求 |