---
title: Direct I/O
---

# Direct I/O — 绕过 Page Cache 的高性能读写

> <span class="kg-badge kg-badge--perf">性能调优</span>
> O_DIRECT · 双缓冲问题 · 数据库场景

Direct I/O 让应用程序**绕过 Page Cache**，直接读写磁盘。在某些场景下能显著降低延迟、避免双重缓存，但要求应用自己处理对齐、刷盘等细节。

## 1. 传统 vs Direct I/O

```
传统 write/read:
   App Buffer → Page Cache → Disk
            (双缓冲)
            ↑
         浪费内存 / 同步复杂度

Direct I/O:
   App Buffer → Disk
            ↑
         1 次拷贝 / 应用自管
```

## 2. 何时用 Direct I/O

| 场景 | 推荐 |
|------|------|
| MySQL InnoDB | **用 O_DIRECT**（自管 buffer pool） |
| PostgreSQL | **用 O_DIRECT**（自管 shared_buffers） |
| RocksDB / LevelDB | **用 O_DIRECT**（自管） |
| 大文件顺序写（视频、备份） | 不用（Page Cache 已经够好） |
| 通用服务（nginx 等） | 不用 |
| OLAP 数据库（ClickHouse） | **用 O_DIRECT** |

**核心原则**：当应用**自己有一套内存缓冲**，且对数据安全**有特殊控制**时，用 O_DIRECT。

## 3. Linux O_DIRECT 实现

```c
int fd = open("/var/lib/mysql/data.ibd", O_RDWR | O_DIRECT);
```

**硬性要求**：

1. **对齐**：buffer 地址 / 偏移 / size 必须是文件系统块大小（4KB 或 512 字节）的整数倍
2. **不支持 mmap**：Direct I/O + mmap 会 EINVAL
3. **aio 兼容**：支持 libaio / io_uring 的 O_DIRECT

## 4. MySQL 的 O_DIRECT 配置

```ini
[mysqld]
innodb_flush_method = O_DIRECT   # 启用 Direct IO
innodb_buffer_pool_size = 16G    # 自管 buffer pool
```

**效果**：

- 避免 Page Cache 与 InnoDB buffer pool 双重缓冲
- 减少内存占用
- 数据库 cache 命中 = 不走 IO，cache miss = 直接读盘（绕开 Page Cache）

## 5. PostgreSQL 的 O_DIRECT

```ini
# postgresql.conf
shared_buffers = 8GB
wal_level = replica
# Linux 上 PG 默认对 main relations 用 O_DIRECT
# 但 WAL 仍走 Page Cache（安全性）
```

## 6. 实战：Direct I/O 编程

```c
#include <fcntl.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

int main() {
    // 1. 对齐 buffer
    void *buf;
    posix_memalign(&buf, 4096, 4096);  // 4KB 对齐
    
    // 2. 打开 O_DIRECT
    int fd = open("/dev/sdb1", O_WRONLY | O_DIRECT);
    
    // 3. 写
    strcpy(buf, "Hello, Direct IO!");
    pwrite(fd, buf, 4096, 0);  // offset 也必须对齐
    
    // 4. 强制刷盘
    fsync(fd);
    
    close(fd);
    free(buf);
}
```

## 7. alignment 检查

```c
int posix_memalign(void **memptr, size_t alignment, size_t size);
// alignment 必须是 2 的幂

// 或用 aligned_alloc（C11）
void *buf = aligned_alloc(4096, 4096);
```

## 8. O_DIRECT 性能特点

| 维度 | Page Cache | Direct I/O |
|------|-----------|-----------|
| 读延迟（hit） | ns 级（内存） | 几十 μs（磁盘） |
| 读延迟（miss） | 几十 μs（缓存填充后） | 几十 μs（首次） |
| 写延迟 | ns 级（写 Page Cache） | 几十 μs（直写） |
| 内存占用 | 双倍缓冲 | 单倍 |
| 数据安全 | fsync 才安全 | 落盘即安全（自己 fsync） |

## 9. O_DIRECT + AIO / io_uring

```c
#include <libaio.h>

// 提交异步 Direct IO
io_prep_pwrite(&iocb, fd, buf, 4096, 0);
io_submit(ctx, 1, &iocb);

// 或用 io_uring
struct io_uring_sqe *sqe = io_uring_get_sqe(ring);
io_uring_prep_write(sqe, fd, buf, 4096, 0);
sqe->flags |= IOSQE_FIXED_FILE;
io_uring_submit(ring);
```

## 10. 实战：基准测试

```bash
# fio 是测试 IO 的利器
# 测试 O_DIRECT
fio --name=randwrite \
    --ioengine=libaio \
    --direct=1 \
    --filename=/dev/sdb1 \
    --bs=4k \
    --size=10G \
    --rw=randwrite \
    --iodepth=32

# 对比：非 O_DIRECT
fio --name=randwrite \
    --ioengine=libaio \
    --direct=0 \
    --filename=/var/lib/data/test.bin \
    --bs=4k \
    --size=10G \
    --rw=randwrite \
    --iodepth=32
```

## 11. 与 OS 的交互

```bash
# 看哪些进程用 O_DIRECT
lsof -d '0-100' | grep REG | awk '{print $2, $3, $10}'
# 配合 fio 压测看效果

# 看 OS cache 命中率
sar -B 1
# 如果某些应用 O_DIRECT，会让 Page Cache hit 率变高（因为 OS cache 给别的进程用）
```

## 12. 常见错误

### 12.1 EINVAL（参数不对齐）

```text
EINVAL: Invalid argument
```

原因：

- buffer 没用 aligned_alloc
- offset 不是 4KB 对齐
- size 不是 4KB 倍数

### 12.2 O_DIRECT + O_APPEND

不能直接组合：

```c
open(path, O_WRONLY | O_DIRECT | O_APPEND);  // 可能拒绝
```

### 12.3 O_DIRECT + buffered 写入

混合使用可能产生意外结果。建议全 O_DIRECT 或全 Page Cache。

## 13. 何时不该用

- 写后立刻被另一个进程读（绕过 Page Cache = 无缓存 = 性能差）
- 不在意刷盘开销的小 IO（Page Cache 更好）
- 用 mmap 的场景

## 14. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| Direct IO = 绕 Page Cache | "Direct=绕开" |
| 用 O_DIRECT 必须对齐 | "对齐=硬性" |
| 数据库 = Direct I/O | "DB=Direct" |
| 一般服务 = Page Cache | "普通=Cache" |
| fio 是压测工具 | "fio=测试" |

## 参考

- open(2) man O_DIRECT
- MySQL InnoDB Flush Method 文档
- io_uring 文档