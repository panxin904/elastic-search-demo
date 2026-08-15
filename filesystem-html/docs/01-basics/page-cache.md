# Page Cache 页缓存

<span class="kg-badge kg-badge-basics">基础</span>

Linux I/O 性能的核心——所有"第二次变快"的秘密。

## 什么是 Page Cache

**Page Cache** 是内核管理的磁盘文件页缓存，以 4KB 为单位缓存磁盘内容到内存。

```c
struct page {
    unsigned long flags;            // PG_locked, PG_dirty, PG_uptodate ...
    struct address_space *mapping;  // 关联的 inode（address_space）
    void *virtual;                  // 内存地址
    pgoff_t index;                  // 文件内的页号
    // ...
};
```

每个被缓存的文件页对应一个 `struct page`，所有页通过 LRU 链表管理。

## 读流程

```c
read(fd, buf, n)
  → sys_read → vfs_read → file->f_op->read
  → 触发缺页异常（如果 Page Cache 没有）
  → 调用具体 FS 的 readpage（如 ext4_readpage）
  → 提交 bio 到块设备层
  → 块设备驱动发起磁盘 IO
  → 中断处理拷贝数据到 page
  → 标记 page uptodate
  → copy_to_user 把 page 内容复制到用户 buf
  → 返回
```

**关键**：第二次 read 同样的内容 → 直接从内存 copy，**零磁盘 IO**。

## 写流程

```c
write(fd, buf, n)
  → sys_write → vfs_write
  → 把数据写入 Page Cache（page 标记 dirty）
  → 立即返回（write-back 由内核后台完成）
  → 后台 writeback 线程把 dirty page 写回磁盘
```

**write 不阻塞磁盘**——这是 Page Cache 的核心收益，也是新手最容易踩坑的地方（"我明明 write 了，数据却没持久化"）。

## 性能数字

| 层级 | 延迟 | 吞吐 |
|------|------|------|
| L1 cache | 1 ns | - |
| L2 cache | 4 ns | - |
| RAM（Page Cache 命中） | 100 ns | ~10 GB/s |
| SSD 随机读 | 50-100 μs | ~100K IOPS |
| HDD 寻道 | 10 ms | ~100 IOPS |
| 网络存储 | 1-50 ms | 受网络限制 |

> **Page Cache 命中 = 比 SSD 快 1000 倍**。所有性能调优的核心目标就是提高命中率。

## 调优参数

```bash
# 查看当前值
sysctl vm.dirty_ratio            # 5-20，脏页占内存 % 上限
sysctl vm.dirty_background_ratio # 1-10，后台 writeback 触发点
sysctl vm.dirty_expire_centisecs # 3000，脏页最长存活 30s
sysctl vm.dirty_writeback_centisecs # 500，每 5s 检查一次

# 生产推荐（数据库场景）
vm.dirty_ratio = 5
vm.dirty_background_ratio = 1
vm.dirty_expire_centisecs = 1500
```

## sync / fsync / fdatasync

```c
sync()      // 把所有文件的 dirty page 写回（全局）
fsync(fd)   // 把指定 fd 的脏数据 + 元数据刷盘（阻塞到完成）
fdatasync(fd) // 只刷数据，不刷元数据（更快）

// 性能差距（典型 NVMe）
fsync    ~ 1 ms
fdatasync ~ 0.5 ms
```

## direct I/O

```c
int fd = open(path, O_RDONLY | O_DIRECT);
// 绕过 Page Cache，直接 IO 到磁盘/用户 buf
```

**适用场景**：
- 数据库（自己的缓存管理，避免双重缓存）
- 大文件顺序 IO（Page Cache 是 page-sized，对超大文件无用）

**代价**：
- 不享受 Page Cache 的预读
- 必须用户自己管理对齐（512/4K 边界）
- IO 性能变差（小 IO 场景）

## 实战：观察 Page Cache 效果

```bash
# 测试两次读取的差异
dd if=/var/log/syslog of=/dev/null bs=1M count=100
# 第一次：从磁盘读，慢
# 第二次：Page Cache 命中，几乎瞬时

# 查看 Page Cache 占用
free -h
# 输出：
#               total    used    free   shared  buff/cache  available
# Mem:           16Gi    3.2Gi    8.1Gi    0.5Gi    4.7Gi        12Gi
#                                          ↑
#                                      Page Cache 在这

# 精确查看
cat /proc/meminfo | grep -E "Cached|Buffers|Dirty"

# 主动清空（紧急情况）
sync && echo 3 > /proc/sys/vm/drop_caches
# 1 = page cache
# 2 = dentry + inode
# 3 = 全部
```

## 案例：MySQL 的 InnoDB

InnoDB 有自己的 buffer pool（典型 70-80% 内存），所以：
- 关闭 Page Cache 对查询性能**几乎无影响**（数据在 buffer pool）
- 但对 fsync 的开销**影响巨大**
- 生产 MySQL 通常用 O_DIRECT 打开数据文件，让 Page Cache 给文件系统元数据用

## 关键 takeaway

| 现象 | 原因 |
|------|------|
| 第二次读快 1000 倍 | Page Cache 命中 |
| write 后立即读能读到 | 仍在内存，未写盘 |
| 突然断电丢数据 | dirty page 没刷盘 |
| `fsync` 慢 | 强制刷盘，触发磁盘 IO |
| 磁盘 IO 监控看不到大 IO | Page Cache 屏蔽了大部分读 |