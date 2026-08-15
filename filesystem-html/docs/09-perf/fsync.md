---
title: fsync 与持久化
---

# fsync 与持久化 — 写盘的最后一道关卡

> <span class="kg-badge kg-badge--perf">性能调优</span>
> 数据安全 · fsync / fdatasync / barrier · 性能取舍

fsync 是"把数据强制刷到磁盘"的系统调用。它是**数据持久化**与**性能**之间最大的取舍点。

## 1. 写盘的完整路径

```
write(2)
   │
   ▼
用户缓冲区 (user-space)
   │
   ▼  ← memcpy
Page Cache (内核)
   │
   ▼  ← 内核异步刷盘
Disk Cache (硬盘缓存)
   │
   ▼  ← disk 自带刷盘机制
物理磁盘
```

**fsync 的作用**：把上述路径**强制同步到底**，保证调用返回时数据已经在物理磁盘上。

## 2. 系统调用族

| 系统调用 | 含义 |
|----------|------|
| `write()` | 写入用户缓冲 + Page Cache |
| `fsync(fd)` | 把 fd 的所有数据和元数据刷盘 |
| `fdatasync(fd)` | 仅刷数据（**不刷元数据**，更快） |
| `sync()` | 把**所有** fd 的脏数据刷盘 |
| `syncfs(fd)` | 把文件系统所有脏数据刷盘 |
| `sync_file_range()` | 更精细的 sync（部分范围） |
| `O_SYNC` 标志 | open 时声明每次 write 自动 fsync |

## 3. fsync 的代价

| 调用 | 延迟 |
|------|------|
| write() | 0.001 ms（写 Page Cache） |
| fsync() | 1-10 ms（真正落盘） |

**关键**：每次 fsync 都是一次**机械或电子延迟**。NVMe SSD 约 1ms，HDD 约 10ms，远程磁盘几秒。

```c
// 反例：每写一条 fsync
for (int i = 0; i < 1000; i++) {
    write(fd, data, len);
    fsync(fd);
}
// 1000 × 10ms = 10 秒

// 优化：批量 + 一次 fsync
for (int i = 0; i < 1000; i++) {
    write(fd, data, len);
}
fsync(fd);
// 10 ms + 10 ms ≈ 20 ms
```

## 4. 数据库的 fsync 模式

### 4.1 强持久化（MySQL innodb_flush_log_at_trx_commit=1）

```ini
[mysqld]
innodb_flush_log_at_trx_commit=1   # 每个事务都 fsync（最安全）
```

- **RPO = 0**：每个 commit 后数据必在盘
- **代价**：每事务 1-2 次 fsync

### 4.2 性能优先（innodb_flush_log_at_trx_commit=0）

```ini
innodb_flush_log_at_trx_commit=0   # 不主动 fsync，靠 OS 每秒刷
```

- **RPO = 1 秒**（OS crash 可能丢 1 秒数据）
- **代价**：10x 性能

### 4.3 折中

```ini
innodb_flush_log_at_trx_commit=2   # 写到 Page Cache，OS 负责刷
```

| 值 | 含义 | RPO |
|----|------|-----|
| 0 | 每秒刷 | 1 秒 |
| 1 | 每事务刷 | 0 |
| 2 | 写 OS cache | ~1 秒 |

## 5. fdatasync 优化

```c
fdatasync(fd);  // 不刷元数据（atime / mtime 等）
fsync(fd);      // 刷数据和元数据
```

**当数据完整写入且 mtime 不重要时**（如 ETL 临时文件），用 fdatasync 省 30%~50% 时间。

## 6. barrier IO

现代文件系统用 barrier 保证写入顺序：

```c
// 内核关键写盘后插入 barrier
write(...)
<barrier>  // 确保 write 真的落盘后，再做下一个操作
write(...)
```

**ext4 默认开启**。XFS / Btrfs 默认开启。

```bash
# 看是否启用
dumpe2fs /dev/sda1 | grep "Default mount options"
mount | grep barrier
```

**生产建议**：**保持开启**。关闭 barrier = 数据可能错乱。

## 7. sync_file_range 高级用法

```c
#include <fcntl.h>

sync_file_range(fd, offset, nbytes, SYNC_FILE_RANGE_WRITE);
sync_file_range(fd, offset, nbytes, SYNC_FILE_RANGE_WAIT_BEFORE |
                                    SYNC_FILE_RANGE_WRITE |
                                    SYNC_FILE_RANGE_WAIT_AFTER);
```

**场景**：

- 大文件顺序写
- 边写边让内核异步刷
- 数据库 group commit（多个 commit 一次刷）

## 8. WAL 与 fsync

PostgreSQL / RocksDB / LevelDB 都用 **Write-Ahead Log**：

```text
1. 写 WAL 到 Page Cache + fsync
2. 修改内存数据结构
3. 周期性 checkpoint 把内存数据刷到数据文件
```

**fsync WAL** → 即使断电也能从 WAL 重做。

## 9. 实战：MongoDB 的 fsync 调优

```yaml
storage:
  journal:
    commitIntervalMs: 100     # 每 100ms fsync 一次
  wiredTiger:
    engineConfig:
      checkpointSize: 64       # checkpoint 触发
```

## 10. 实战：监控 fsync 频率

```bash
# 看 fsync 次数
iostat -x 1

# w/s, w_await 是关键
# w_await > 10ms 通常意味着 fsync 满载

# perf trace 看 fsync 调用
perf trace -e syscalls:sys_enter_fsync -p <PID>

# 业务层监控
mysql> SHOW GLOBAL STATUS LIKE 'Innodb_data_fsyncs';
+--------------------+-------+
| Variable_name      | Value |
+--------------------+-------+
| Innodb_data_fsyncs | 12345 |   ← fsync 总次数
+--------------------+-------+
```

## 11. 关键 takeaway：何时该 fsync

| 业务 | fsync 策略 |
|------|-----------|
| 金融交易 | **每个事务** fsync（不能丢） |
| 通用业务 | 折中：1 秒刷一次 |
| 日志写入 | 批量写 + 1 秒刷一次 |
| 临时文件 | 不刷（断电丢无所谓） |

## 12. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| fsync = 真正落盘 | "fsync=落盘" |
| fdatasync 更快 | "fdatasync=省 meta" |
| barrier = 顺序保证 | "barrier=顺序" |
| 数据库用 group commit | "group commit=提速" |
| 关闭 fsync = 丢数据风险 | "关 fsync=冒险" |

## 参考

- fsync(2) man 手册
- PostgreSQL WAL 实现
- MySQL InnoDB Flush Method 文档