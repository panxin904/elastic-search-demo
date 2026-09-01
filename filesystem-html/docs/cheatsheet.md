---
title: 速记卡
date: 2026-08-15  # date-auto-injected
---

# 速记卡

一页速查 — 关键概念、命令、对比表。

## 🎯 核心概念速查

### inode 三件套
- **inode** = 文件元数据（权限/大小/时间戳/数据块指针）
- **dentry** = 目录项缓存（文件名 → inode 映射）
- **file** = 进程打开后的"打开文件表"项

### 文件读流程
```
read(fd, buf, n)
  → sys_read → vfs_read
  → 检查 Page Cache
    → 命中 → copy_to_user 返回
    → 未命中 → 触发缺页 → 磁盘读 → 填 Page Cache → 返回
```

### 文件写流程
```
write(fd, buf, n)
  → sys_write → vfs_write
  → 写入 Page Cache（标记 dirty）
  → 立即返回（write back 由内核后台完成）
  → fsync(fd) 强制刷盘
```

## 📊 选型速查表

| 场景 | 推荐 | 原因 |
|------|------|------|
| Linux 默认 | ext4 | 稳定/广泛支持 |
| 大文件顺序写 | XFS | 高吞吐 |
| 快照 / COW | Btrfs / ZFS | 内置快照 |
| 数据湖 | HDFS / JuiceFS | 海量 + 大文件 |
| 自建对象存储 | MinIO | S3 兼容 |
| K8s 块存储 | Longhorn / Rook | CSI |
| K8s 共享存储 | CephFS / NFS | ReadWriteMany |
| 跨云备份 | restic + S3 | 加密增量 |

## 🔧 常用命令

### 磁盘与空间
```bash
df -h                       # 各挂载点使用情况
du -sh /path                # 目录大小
du -h --max-depth=1 /var    # 一级子目录
ncdu /var                   # 交互式扫描
lsof +L1                    # 已删除但仍被占用的文件
fuser -v /path              # 谁在用这个文件
```

### 文件查找
```bash
find / -name "*.log"        # 按名
find / -size +100M          # 按大小
find / -mtime -7            # 7 天内修改
fd "*.log" /var             # fd 更快
```

### 文件系统工具
```bash
mkfs.ext4 /dev/sdb1         # 格式化
tune2fs -l /dev/sda1        # 查看 ext4 参数
xfs_info /dev/sda1          # 查看 XFS
btrfs filesystem show       # 查看 Btrfs
zpool status                # 查看 ZFS
fsck.ext4 -n /dev/sda1      # 检查（只读）
mount | column -t           # 当前挂载
```

### 监控与调试
```bash
iostat -xz 1                # IO 统计
iotop                       # 按进程 IO 排序
strace -p PID -e read,write # 跟踪文件 IO
perf top                    # 性能热点
inotifywait -m /path        # 文件事件监控
```

### 同步与备份
```bash
rsync -avz src/ dst/        # 本地/远程同步
rsync -avz --delete src/ dst/  # 镜像
borg init /backup/repo      # Borg 备份
restic -r /backup init      # restic 备份
```

## 🗂️ 关键路径速查

| 路径 | 内容 |
|------|------|
| `/proc/mounts` | 当前挂载 |
| `/proc/filesystems` | 支持的 FS 类型 |
| `/proc/diskstats` | 磁盘统计 |
| `/proc/sys/vm/dirty_*` | Page Cache 调优 |
| `/etc/fstab` | 开机自动挂载 |
| `/proc/self/fd/` | 当前进程 fd 链接 |
| `/sys/block/*/queue/scheduler` | IO 调度器 |

## ⚠️ 常见坑

| 坑 | 原因 | 修复 |
|----|------|------|
| `No space left on device` 但 `df` 看还有空间 | inode 用尽（小文件太多） | `df -i` 查看 |
| `rm` 后空间未释放 | fd 还开着 | `lsof +L1` 找进程 kill |
| `cp` 慢 | 大文件 + 默认 Page Cache 抖动 | 用 `dd bs=1M` 或 direct I/O |
| NFS 客户端卡死 | NFS server 挂了，sync 等超时 | 用 `soft` / `intr` 或切 SMB |
| 容器启动慢 | 镜像层太多 / 复制慢 | 合并 RUN 指令 / 用 BuildKit |
| `git pull` 慢 | inode 满 / fsck 卡住 | 检查 inode + fsck |
| `mv` 跨盘变慢 | 不同 FS 需要复制+删除 | 同盘 mv 才是 rename |

## 📈 性能关键数字

| 操作 | 延迟 |
|------|------|
| L1 cache | 1 ns |
| L2 cache | 4 ns |
| RAM 访问 | 100 ns |
| SSD 读 | 100 μs |
| HDD 寻道 | 10 ms |
| 跨数据中心 | 50-100 ms |
| NFS round-trip | 0.5-5 ms |
| S3 GET | 30-200 ms |

> **核心规律**：Page Cache 命中 = RAM 速度（100 ns），未命中 = 磁盘速度（μs-ms 差 1000 倍）。所有性能调优本质都是提高 Page Cache 命中率。


## 📱 手机扫码继续阅读

<ClientOnly>
  <QrShare />
</ClientOnly>
