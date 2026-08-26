---
title: readahead
---

# readahead — 提前读，让磁盘预取为你加速

> <span class="kg-badge kg-badge--perf">性能调优</span>
> 内核预读 · 用户态预读 · 实战取舍

readahead（预读）是 OS 提前把后续数据从磁盘读到 Page Cache 的机制。对**顺序读**场景（视频、备份、大数据查询），合理 readahead 能把 IO 性能提升 5-50 倍。

## 1. 内核 readahead 原理

```
进程读 page 100
   │
   ▼
内核发现这是顺序读 → 启动异步 readahead
   │
   ▼
把 page 100 ~ 100+N 提前读入 Page Cache
   │
   ▼
进程继续读 page 101 → 直接命中 Page Cache
```

**核心算法**：

- 连续顺序读 → 加大 readahead 窗口（最大 128MB）
- 随机读 → 减小窗口（最小 0）
- 切换时调整（"切换历史"窗口）

## 2. 系统级参数

```bash
# /sys/block/<dev>/queue/read_ahead_kb
cat /sys/block/sda/queue/read_ahead_kb
# 默认 128 KB

# 调大（顺序读）
echo 8192 | sudo tee /sys/block/sda/queue/read_ahead_kb

# 调小（随机读 / 数据库）
echo 128 | sudo tee /sys/block/sda/queue/read_ahead_kb
```

## 3. 文件级 readahead

```bash
# 看某个文件的当前 readahead
blockdev --getra /dev/sda

# 用 posix_fadvise 设置
posix_fadvise(fd, 0, size, POSIX_FADV_SEQUENTIAL);
posix_fadvise(fd, 0, size, POSIX_FADV_RANDOM);   # 关闭 readahead
```

## 4. 实战：大文件顺序读

```bash
# 默认 128KB → 顺序读 10GB 文件需 80k 次 IO
echo 4096 | sudo tee /sys/block/sda/queue/read_ahead_kb
# 现在只需 2560 次 IO
```

**验证**：

```bash
# 1. 清理缓存
sync && echo 3 > /proc/sys/vm/drop_caches

# 2. 调大 readahead
echo 4096 | sudo tee /sys/block/sda/queue/read_ahead_kb

# 3. 读文件
dd if=/var/lib/data/big.bin of=/dev/null bs=1M

# 看 iostat
iostat -x 1
# r/s    rMB/s  await
# 5      200    1.0     ← 之前可能是 50MB/s（128KB readahead）
```

## 5. 实战：数据库

```bash
# 关系数据库 = 随机读，关 readahead
echo 256 | sudo tee /sys/block/sdb/queue/read_ahead_kb

# 启用大页缓存预热
mysql> SET GLOBAL innodb_buffer_pool_size = 4G;
```

**PostgreSQL**：

```ini
# postgresql.conf
effective_io_concurrency = 200    # SSD 高并发
random_page_cost = 1.1            # 几乎和顺序读等价
```

## 6. 应用层预读

### 6.1 madvise / posix_fadvise

```c
#include <sys/mman.h>
#include <fcntl.h>

// 告诉内核：这块区域要顺序读
madvise(addr, len, MADV_SEQUENTIAL);

// 取消最近预读
madvise(addr, len, MADV_DONTNEED);

// 预读特定区域
posix_fadvise(fd, offset, len, POSIX_FADV_WILLNEED);
```

### 6.2 readahead 命令

```bash
readahead /var/lib/data/big.bin
# 把文件加载到 Page Cache
```

## 7. 用户态异步预读库

```python
# linux_aio（libaio）
# or async io_uring
# 在 Python / Go 应用里异步 prefetch
```

## 8. 容器场景

```bash
# 容器内 readahead 受 host sysfs 控制
# /sys/devices/.../queue/read_ahead_kb 是全局的
# 不能从容器直接改

# 但可以用 posix_fadvise（从容器内进程）
```

## 9. 监控 readahead 效果

```bash
# 看 cache hit rate
sar -B 1
# majflt/s   pgmajfault/s
# 0.5                ← 如果高 = 预读没起效

# perf trace 看 readahead 调用
perf trace -e 'fs:*' -p <PID>
# 输出：
# fs/read(0xfd, ...) ... readahead=4096KB

# 跟踪实际 IO 模式
btrace /dev/sda | grep "R"
```

## 10. 常见误区

| 误区 | 真相 |
|------|------|
| 越大越好 | 太大 → 浪费内存，挤掉有用的 cache |
| 数据库默认越大越好 | 数据库是**随机读**！调小 |
| 设了 readahead 就稳了 | 还要看 posix_fadvise 是否触发 |
| NVMe 不需要 readahead | NVMe 仍能从预读获益（节省延迟） |

## 11. 实战：依据场景调整

```bash
# 备份服务器（顺序大文件）
echo 16384 | sudo tee /sys/block/sdb/queue/read_ahead_kb

# 数据库服务器（随机 IO）
echo 128 | sudo tee /sys/block/sdb/queue/read_ahead_kb

# 文件服务器（混合）
echo 4096 | sudo tee /sys/block/sdb/queue/read_ahead_kb

# NVMe SSD 数据库
echo 16 | sudo tee /sys/block/nvme0n1/queue/read_ahead_kb
```

## 12. 与内核其他优化配合

| 优化 | 顺序读 | 随机读 |
|------|--------|--------|
| readahead 大 | ✅ | ❌ |
| 调度器 mq-deadline | ✅ | ✅ |
| Page Cache 大 | ✅ | ✅ |
| O_DIRECT | ❌（绕过） | ✅（数据库） |
| NVMe SSD | ✅ | ✅ |

## 13. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| 顺序读 = readahead 大 | "顺序=预读多" |
| 随机读 = readahead 小 | "随机=预读少" |
| 数据库关 readahead | "DB=小" |
| 备份设大 readahead | "备份=大" |
| 用 posix_fadvise 控制 | "fadvise=细控" |

## 参考

- Linux 内核 mm/readahead.c 注释
- posix_fadvise(2) man 手册
- 《Systems Performance》 Brendan Gregg


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
