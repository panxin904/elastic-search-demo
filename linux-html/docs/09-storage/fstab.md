---
title: fstab 自动挂载
---

# fstab 自动挂载

> 让 Linux 开机自动挂载分区 / 网络盘 / 内存盘。

## 📂 /etc/fstab

```
# <file system>    <mount point>  <type>  <options>          <dump> <pass>
UUID=xxx           /              ext4    defaults           0       1
UUID=yyy           /data          xfs     noatime,nofail     0       2
tmpfs              /tmp           tmpfs   defaults,size=512M 0       0
//server/share     /mnt/cifs      cifs    credentials=...   0       0
server:/share      /mnt/nfs       nfs     defaults,_netdev  0       0
```

## 🆔 字段含义

| 字段 | 含义 |
|------|------|
| 1 - filesystem | 设备（/dev/sda1）、UUID、LABEL、网络路径 |
| 2 - mount point | 挂载点目录 |
| 3 - type | 文件系统类型（ext4 / xfs / btrfs / nfs / cifs / tmpfs） |
| 4 - options | 逗号分隔的选项 |
| 5 - dump | dump 工具用（0 = 不备份） |
| 6 - pass | fsck 检查顺序（1 = root，2 = 其他，0 = 不检查） |

## ⚙️ 常用选项

| 选项 | 作用 |
|------|------|
| `defaults` | rw, suid, dev, exec, auto, nouser, async |
| `noatime` | 不更新访问时间（性能 + 减少 SSD 写） |
| `ro` | 只读 |
| `nofail` | 设备不存在时不启动失败（**重要**） |
| `_netdev` | 网络设备，等网络启动后再挂载 |
| `noexec` | 不允许可执行 |
| `nosuid` | 忽略 SUID |
| `nodev` | 不解释设备文件 |
| `discard` | SSD TRIM |
| `noauto` | 不自动挂载（需手动 mount / 自动 mount -a） |
| `nofail` + `_netdev` | NFS / iSCSI 的推荐组合 |

## 🛠 编辑 fstab

```bash
# ⚠️ 永远先备份
sudo cp /etc/fstab /etc/fstab.bak

# 找 UUID
sudo blkid /dev/sdb1

# 加条目
echo "UUID=$(sudo blkid -s UUID -o value /dev/sdb1) /data xfs defaults,nofail 0 2" | \
  sudo tee -a /etc/fstab

# 测试（不挂载）
sudo mount -a --fake          # 模拟
sudo mount -a                 # 实际挂载

# 验证
df -h /data
```

## 🆔 找 UUID

```bash
lsblk -f                  # 推荐
blkid /dev/sdb1
blkid -s UUID -o value /dev/sdb1

# 按 label 找
blkid -L data             # label = data

# 按 UUID 找设备
blkid -U xxxxxxx
```

## 🌐 网络文件系统

### NFS

```bash
# /etc/fstab
server:/path /mnt/nfs nfs defaults,_netdev,noatime 0 0

# 选项
# _netdev    - 等网络
# vers=4     - NFS v4（推荐）
# sec=sys    - 安全模式
```

### CIFS / Samba

```bash
# /etc/fstab
//server/share /mnt/cifs cifs credentials=/etc/samba.cred,_netdev,uid=1000,gid=1000 0 0

# /etc/samba.cred（必须 600）
username=alice
password=secret
domain=WORKGROUP
```

```bash
sudo chmod 600 /etc/samba.cred
```

## 🛠 swap 分区 / 文件

```bash
# swap 分区
UUID=xxx none swap sw 0 0

# swap 文件
/swapfile none swap sw 0 0
```

```bash
# 创建 2GB swap 文件
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 🧊 tmpfs（内存盘）

```bash
# /etc/fstab
tmpfs /tmp tmpfs defaults,nosuid,nodev,size=1G 0 0
tmpfs /var/cache/nginx tmpfs defaults,size=512M 0 0
```

适合缓存、临时编译产物。

## 🚨 防止启动失败

⚠️ **fstab 写错会导致系统无法启动**。

```bash
# 1. 用 UUID，不用 /dev/sda1（设备名可能漂移）
# 2. 加 nofail（设备缺失不卡启动）
# 3. 加 _netdev（网络设备）
# 4. 修改后用 mount -a 测试

# 万一启动卡住：
# GRUB 编辑 → 在 linux 行加 single 启动单用户模式
# 或 live USB 启动，修改 /etc/fstab
```

## 📋 完整例子

```bash
# /etc/fstab

# 系统
UUID=aaa-bbb-ccc          /               ext4    defaults           0 1
UUID=ddd-eee-fff          /boot           ext4    defaults,noatime  0 2
UUID=ggg-hhh-iii          /home           xfs     defaults,nofail   0 2
UUID=jjj-kkk-lll          swap            swap    sw                 0 0

# 数据
UUID=mmm-nnn-ooo          /data           xfs     defaults,nofail,noatime  0 2
UUID=ppp-qqq-rrr          /backup         ext4    defaults,nofail,noexec 0 2

# 网络
server:/export /mnt/nfs   nfs   defaults,_netdev,noatime 0 0
//files/share /mnt/smb    cifs  credentials=/etc/samba.cred,_netdev,uid=1000 0 0

# 临时
tmpfs /tmp                 tmpfs defaults,nosuid,nodev,size=2G 0 0
```

## 🪛 实战

```bash
# 验证 fstab 全部条目有效（dry-run）
sudo findmnt --verify --target /

# 看哪些自动挂载了
mount | grep -v "tmpfs\|proc\|sysfs\|cgroup"

# 临时挂载 fstab 里某条（用 mount -a 默认会全部）
sudo mount /data
```

## ❓ 排查

```bash
# 启动时 mount 卡住
# 编辑 GRUB cmdline 加 systemd.unit=rescue.target

# "mount: wrong fs type, bad option, bad superblock"
# 文件系统损坏 → fsck
sudo umount /dev/sdb1
sudo fsck -y /dev/sdb1

# "mount: unknown filesystem type 'xfs'"
# 内核没编 XFS 支持 → 装 xfsprogs
sudo apt install xfsprogs
```

## 🔗 下一步

- [mount / umount](/09-storage/mount)
- [LVM 逻辑卷](/09-storage/lvm)
- [ext4 / xfs / btrfs](/09-storage/fs-types)
- [swap 交换分区](/09-storage/swap)