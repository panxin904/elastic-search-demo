---
title: Page Cache 调优
---

# Page Cache 调优 — 让 Linux 内核缓存为你加速

> <span class="kg-badge kg-badge--perf">性能调优</span>
> 内存缓存 · 内核参数 · 性能方法论

Linux 把"未刷盘"的数据缓存在 **Page Cache**（页缓存）。调整 Page Cache 的参数能让普通业务轻松获得 10-100 倍性能提升。

## 1. 什么是 Page Cache

```
Application
    │
    ▼ read()/write()
VFS
    │
    ▼
Page Cache ← 内核维护
    │
    ▼
Block Layer / IO Scheduler
    │
    ▼
Disk
```

**关键**：

- **读**：先查 Page Cache，没命中才读盘
- **写**：先写 Page Cache，**异步**刷盘（由内核脏页策略控制）

Page Cache 命中 = **零 IO**，纯内存操作。

## 2. 查看 Page Cache

```bash
# 总体
free -h
# 输出：
#               total    used    free    shared  buff/cache  available
# Mem:           62Gi   12Gi   40Gi     0Gi      10Gi       49Gi
#                                                   ↑ Page Cache 在 buff/cache 里

# 详细
cat /proc/meminfo | grep -E "Buffers|Cached|SwapCached"
# Buffers: 100 MB
# Cached: 10 GB
# SwapCached: 0

# 某个文件命中状态
cminfo /var/lib/data/big.db
# 或：
fincore --pages=false /var/lib/data/big.db
```

## 3. 关键内核参数

### 3.1 脏页比例

```bash
# /proc/sys/vm/dirty_*
cat /proc/sys/vm/dirty_ratio             # 默认 20（%）
cat /proc/sys/vm/dirty_background_ratio  # 默认 10（%）
cat /proc/sys/vm/dirty_expire_centisecs  # 默认 3000（30s）
cat /proc/sys/vm/dirty_writeback_centisecs # 默认 500（5s）
```

**含义**：

- `dirty_ratio`：进程触发刷盘的内存占比上限
- `dirty_background_ratio`：后台刷盘开始（异步）
- `dirty_expire_centisecs`：脏页多久后必刷
- `dirty_writeback_centisecs`：刷盘周期

### 3.2 优化场景

#### 数据库（数据安全优先）

```bash
# 减小 dirty，让写更及时落盘
sysctl -w vm.dirty_ratio=5
sysctl -w vm.dirty_background_ratio=2
sysctl -w vm.dirty_expire_centisecs=500     # 5 秒
sysctl -w vm.dirty_writeback_centisecs=100  # 1 秒
```

#### 大文件读（吞吐优先）

```bash
# 增大 dirty，缓冲更多写
sysctl -w vm.dirty_ratio=40
sysctl -w vm.dirty_background_ratio=20
```

## 4. 缓存回收参数

```bash
# 内存压力时回收
cat /proc/sys/vm/vfs_cache_pressure    # 默认 100
# 调小（<100）= 优先回收 dentry/inode（不常用的元数据）
# 调大（>100）= 优先回收页缓存

# 数据库场景：保留更多 Page Cache
sysctl -w vm.vfs_cache_pressure=50
```

## 5. swap 行为

```bash
cat /proc/sys/vm/swappiness  # 默认 60
# 调小（=10）：少用 swap
# 调大（=100）：多用 swap
```

**数据库场景**：

```bash
sysctl -w vm.swappiness=10   # 减少 swap IO
```

**大量顺序写场景**：

```bash
sysctl -w vm.swappiness=80   # 让 swap 缓存大量数据
```

## 6. drop_caches（手动释放）

```bash
# 只释放 Page Cache
echo 1 > /proc/sys/vm/drop_caches

# 释放 dentry + inode
echo 2 > /proc/sys/vm/drop_caches

# 全部释放
echo 3 > /proc/sys/vm/drop_caches
```

**实战：做基准测试前清理缓存**

```bash
sync
echo 3 > /proc/sys/vm/drop_caches
# 此时运行 fio 测试冷启动
```

## 7. 实战：让数据进 Page Cache

```bash
# 1. vmtouch（推荐）
vmtouch -t /var/lib/data/big.db    # 把文件 touch 进 cache
vmtouch -l /var/lib/data/big.db    # 锁在 cache 里

# 2. dd（粗糙）
dd if=/var/lib/data/big.db of=/dev/null bs=1M
# 把文件读一遍 → 进 cache

# 3. posix_fadvise（程序内调用）
posix_fadvise(fd, 0, 0, POSIX_FADV_WILLNEED)
```

## 8. 实战：Page Cache 监控

```bash
# 缓存命中率
sar -B 1
# 输出：
# pgpgin/s     pgpgout/s    %vmeff
# 0.00          0.00         99.50     ← 命中率 > 99% 很好

# 实时监控（prometheus）
node_cpu_seconds_total{mode="page"}
node_vmstat_pgpgin

# 命中率公式
# 100 - (pgpgin / (pgpgin + allocstall) * 100)
```

## 9. 缓存穿透 vs 雪崩

| 场景 | 后果 | 解决 |
|------|------|------|
| 缓存穿透 | 重复请求不在缓存的数据 | 加布隆过滤器 |
| 缓存雪崩 | 大面积过期 / 重建 | 分散过期时间 |
| 缓存击穿 | 热点 key 失效 | 加锁 / 永不过期 |

这些不是 FS 问题，但 Page Cache 失效类似。

## 10. 与应用的互动

### 10.1 fsync vs fdatasync

```c
fsync(fd);            // 同步数据 + 元数据
fdatasync(fd);        // 仅同步数据（更快）
```

### 10.2 O_DIRECT 绕过

```c
open(..., O_DIRECT);  // 不进 Page Cache（数据库常用）
```

数据库场景适合：

- 避免 Page Cache 与 DB buffer pool **双重缓存**
- 数据安全敏感（自己控制刷盘）

### 10.3 posix_fadvise

```c
posix_fadvise(fd, 0, 0, POSIX_FADV_DONTNEED);   // 主动释放
posix_fadvise(fd, 0, 0, POSIX_FADV_WILLNEED);   // 提前预热
posix_fadvise(fd, 0, 0, POSIX_FADV_SEQUENTIAL); // 顺序读
posix_fadvise(fd, 0, 0, POSIX_FADV_RANDOM);     // 随机读
```

## 11. 实战：数据库优化清单

```text
[ ] dirty_ratio=5, dirty_background_ratio=2
[ ] dirty_expire_centisecs=500
[ ] dirty_writeback_centisecs=100
[ ] swappiness=10
[ ] vfs_cache_pressure=50
[ ] echo never > /sys/kernel/mm/transparent_hugepage/enabled   # THP 关闭（Oracle）
[ ] IO 调度器 = mq-deadline 或 none（NVMe）
[ ] Page Cache 监控命中率 > 95%
```

## 12. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| Page Cache = 内核内存缓存 | "Cache=内存加速" |
| dirty_ratio 决定刷盘时机 | "dirty=刷盘阈值" |
| vmtouch 主动预热 | "预热=hot" |
| 数据库用 fsync / O_DIRECT | "DB=显式控" |
| swappiness 调小防 swap | "swap=少用" |

## 参考

- Linux Documentation/sysctl/vm.txt
- 《Systems Performance》 Brendan Gregg
- vmtouch：<https://github.com/hoytech/vmtouch