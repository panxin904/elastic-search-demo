---
title: mount / umount
date: 2026-08-15  # date-auto-injected
---

# mount / umount

> Linux 文件系统挂载是"装在"根目录树上的能力。

## 🧠 概念

```
设备 /dev/sdb1
       │
       ▼  挂载（mount）
   /mnt/data
       │
       └── /mnt/data/file.txt   ← 访问文件前，先经过 /dev/sdb1
```

挂载点（mount point）是文件系统在目录树上的"接入位置"。

## 🔍 df / du - 看挂载 / 用量

```bash
df -h                       # 所有挂载点（人类可读）
df -h /                     # 看某路径所在的文件系统
df -i                       # inode 使用情况
df -T                       # 显示文件系统类型

du -sh dir                  # 目录总大小
du -h --max-depth=1 /      # 1 层
du -h -d 0 /var | sort -h   # 排个序
```

## 📦 手动挂载

```bash
# 看所有块设备
lsblk
lsblk -f                    # 含文件系统类型
fdisk -l

# 格式化（已分区但未格式化的设备）
sudo mkfs.ext4 /dev/sdb1
sudo mkfs.xfs /dev/sdb1
sudo mkfs.btrfs /dev/sdb1

# 挂载
sudo mount /dev/sdb1 /mnt/data
sudo mount -t ext4 /dev/sdb1 /mnt/data     # 指定类型
sudo mount -o ro /dev/sdb1 /mnt/iso       # 只读
sudo mount -o noatime /dev/sdb1 /var/data # 不更新访问时间

# 看挂载的选项
mount | grep sdb
findmnt /mnt/data           # 看某挂载点的详情
```

## 🔓 umount - 卸载

```bash
sudo umount /mnt/data
sudo umount /dev/sdb1
# 或
umount -l /mnt/data         # lazy（先脱离再实际卸载，处理"busy"）
```

⚠️ **不能卸载被占用的挂载点**：

```bash
# "device is busy"
fuser -mv /mnt/data         # 看谁在用
lsof +D /mnt/data           # 看打开了哪些文件

# 找进程
fuser -m /mnt/data
# 结束它们，或 cd 到别处再 umount
```

## 📝 /etc/fstab - 自动挂载

```
# <file system>          <mount point>  <type>  <options>          <dump> <pass>
/dev/sda1                /              ext4    defaults           0       1
/dev/sdb1                /data          xfs     noatime,nofail     0       2
UUID=abc-123             /backup        ext4    defaults,noauto   0       0
tmpfs                    /tmp           tmpfs   defaults,size=512M 0       0
//server/share           /mnt/nfs       cifs    credentials=/etc/samba.cred 0 0
```

| 列 | 含义 |
|----|------|
| `<file system>` | 设备 / UUID / label / 网络路径 |
| `<mount point>` | 挂载点（swap 是 none） |
| `<type>` | ext4 / xfs / btrfs / nfs / cifs / tmpfs |
| `<options>` | 逗号分隔：defaults / noatime / ro / nofail |
| `<dump>` | 备份（dump 工具用，0 几乎不用） |
| `<pass>` | fsck 顺序：1 root、2 其他、0 不检查 |

### 常用选项

| 选项 | 含义 |
|------|------|
| `defaults` | rw, suid, dev, exec, auto, nouser, async |
| `noatime` | 不更新文件访问时间（性能） |
| `nodiratime` | 不更新目录访问时间 |
| `ro` | 只读 |
| `rw` | 读写 |
| `nofail` | 设备缺失时不启动失败 |
| `noexec` | 不允许执行二进制 |
| `nosuid` | 忽略 SUID |
| `nodev` | 忽略设备文件 |
| `discard` | SSD TRIM |
| `_netdev` | 需要网络（避免开机 mount 卡住） |

```bash
# 测试 fstab（不真的挂载）
sudo mount -a               # 模拟挂载所有

# 改完 fstab 后应用
sudo systemctl daemon-reload
```

## 🆔 用 UUID 而非 /dev/sdX

```bash
# 设备名可能漂移（BIOS 顺序、磁盘顺序），UUID 不会
lsblk -f                    # 看 UUID
blkid /dev/sdb1

# fstab 推荐
UUID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx  /data  ext4  defaults  0  2
```

## 🗂️ 临时挂载（运行时生效）

```bash
# bind mount：把已有目录再挂一遍（不同位置访问）
sudo mount --bind /data /var/data

# tmpfs：内存文件系统
sudo mount -t tmpfs -o size=512M tmpfs /tmp/cache

# overlay（容器用）
sudo mount -t overlay overlay -o lowerdir=/low,upperdir=/up,workdir=/work /merged

# loop mount（ISO 镜像）
sudo mount -o loop image.iso /mnt/iso
```

## 🩺 排查

```bash
# "fstab 写了不生效"
sudo mount -a                    # 模拟挂载看错误
sudo journalctl -b -u local-fs.target

# "挂载后访问慢"
mount -o remount,noatime /data   # 重新挂载

# "swap 没生效"
swapon --show
mkswap /dev/sdc1
swapon /dev/sdc1
```

## 🧰 实战

### 自动挂载新数据盘

```bash
# 1. 找设备
lsblk
# sdb    8:16   0   100G  0 disk

# 2. 分区
sudo fdisk /dev/sdb
# n (new), p (primary), 1, 回车, 回车, w

# 3. 格式化
sudo mkfs.xfs /dev/sdb1

# 4. 挂载
sudo mkdir /data
sudo mount /dev/sdb1 /data

# 5. fstab 永久
UUID=$(blkid -s UUID -o value /dev/sdb1)
echo "UUID=$UUID /data xfs defaults,nofail 0 2" | sudo tee -a /etc/fstab

# 6. 验证
sudo mount -a
df -h /data
```

### 挂载 CIFS / NFS

```bash
# NFS
sudo mount -t nfs server:/share /mnt/nfs
# 或 fstab
server:/share /mnt/nfs nfs defaults,_netdev 0 0

# CIFS / Samba
sudo mount -t cifs //server/share /mnt/cifs -o username=alice,password=xxx
# 或 fstab
//server/share /mnt/cifs cifs credentials=/etc/samba.cred,uid=1000 0 0
```

### 光盘 / USB 自动挂载

```bash
# 现代 systemd 自动挂到 /media/...
lsblk
# sdc1 → 自动到 /media/alice/USBDRIVE

# 手动
sudo mount /dev/sdc1 /mnt/usb -o uid=1000,gid=1000
```

## 🔗 下一步

- [fstab 自动挂载](/09-storage/fstab)
- [LVM 逻辑卷](/09-storage/lvm)
- [ext4 / xfs / btrfs](/09-storage/fs-types)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 自动化
- [cloud-native](https://java-px.bot.cd/cloud-native/):云原生
- [network](https://java-px.bot.cd/network/):Linux 网络
