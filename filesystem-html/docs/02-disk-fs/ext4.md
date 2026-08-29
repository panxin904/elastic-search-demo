---
title: ext4 经典之选
date: 2026-08-15  # date-auto-injected
---

# ext4 经典之选

<span class="kg-badge kg-badge-disk-fs">本地盘</span>

Linux 的默认文件系统——ext2/3/4 家族的集大成者。

## 历史

- **ext2** (1993)：最早的可扩展 FS，无日志
- **ext3** (2001)：加日志，兼容 ext2
- **ext4** (2008)：extent、B+ tree、延迟分配、大文件支持

## 核心特性

### 1. Extent（盘区）

ext3 用**直接/间接块指针**管理数据块，大文件元数据爆炸。
ext4 改用 **extent**（盘区）：连续块 = 一个 extent。

```
ext3: 一百万块的 1GB 文件 → 25 万个指针（4 级间接）
ext4: 同样文件 → 1000 个 extent（每个 4MB）
```

**效果**：大文件元数据减小 ~100 倍，性能显著提升。

### 2. B+ tree 索引

```bash
# ext4 用 Htree（特殊 B+ tree）做目录索引
# 1 万文件的目录：传统线性查找 O(n) → Htree O(log n)
```

```bash
tune2fs -l /dev/sda1 | grep "Filesystem features"
# dir_index    ← Htree 启用
```

### 3. 延迟分配（Delayed Allocation）

```c
write(fd, buf, n)
  → 数据先到 Page Cache，**不立即分配磁盘块**
  → 文件真正落盘时（writeback/fsync）才分配 extent
  → 一次性分配连续 extent（而非零散小块）
```

**效果**：减少碎片，提高顺序写性能。

### 4. 多块分配

```bash
# ext4 同时分配多个块给一个文件
# 默认 stripe 是 0（自适应），可手动调
mke2fs -E stride=128,stripe-width=128 /dev/sdb1
# stride = RAID chunk size / block size
```

### 5. Journal Checksum

ext4 的 journal 头部带 checksum，防止"日志本身损坏"导致 fsck 误操作。

## 实战：创建与调优

```bash
# 创建
mkfs.ext4 /dev/sdb1
mkfs.ext4 -L "DataDisk" /dev/sdb1    # label

# 高级选项
mkfs.ext4 -b 4096 -J size=256 -i 8192 /dev/sdb1
#   -b 4096        块大小
#   -J size=256    journal 大小 256MB
#   -i 8192        bytes-per-inode（每个 inode 代表多少字节）

# 挂载优化
mount -o noatime,nodiratime,data=ordered /dev/sdb1 /mnt/data

# 在线调整（resize）
resize2fs /dev/sdb1 5G      # 缩到 5G
resize2fs /dev/sdb1         # 扩到整盘（先扩 LVM 或 fdisk）
```

## ext4 的限制

| 限制 | 值 |
|------|-----|
| 单文件最大 | 16 TiB（4KB 块） |
| 单 FS 最大 | 1 EiB |
| 文件名最大 | 255 字节 |
| 路径最大 | 4096 字节 |

## 调试工具

```bash
# 查看 FS 信息
tune2fs -l /dev/sda1
# 输出：blocks count、inode count、journal size 等

# 检查与修复
fsck.ext4 -n /dev/sda1          # 只读检查
fsck.ext4 -y /dev/sda1          # 自动修复（先备份！）

# 调试文件系统
debugfs -R "ls /" /dev/sda1     # 列出根目录
debugfs -R "stat <12345>" /dev/sda1  # 看 inode 12345
debugfs -R "dump_extents <12345> /tmp/out" /dev/sda1  # 导出文件内容

# 看性能统计
cat /proc/fs/ext4/sda1/stats
# 看各种错误、alloc、sync 计数
```

## ext4 与 SSD

ext4 的 discard/TRIM 支持：

```bash
# 挂载时启用 discard
mount -o discard /dev/sdb1 /mnt/data

# 或定期手动 trim
fstrim -v /mnt/data

# 查看 trim 状态
cat /sys/block/sda/queue/discard_max_bytes
```

## 与其他 FS 的关键差异

| 特性 | ext4 | XFS | Btrfs | ZFS |
|------|------|-----|-------|-----|
| COW | ❌ | ❌ | ✅ | ✅ |
| 内置快照 | ❌ | ❌ | ✅ | ✅ |
| 校验和 | ❌ | ✅（元数据） | ✅ | ✅ |
| 在线 defrag | ✅ | ✅ | ❌ | ❌ |
| 最大单文件 | 16 TiB | 8 EiB | 16 EiB | 16 EiB |
| 适用 | 通用 | 大文件 | 快照需求 | 终极可靠 |

## 生产场景建议

- **Web 服务器 / 数据库**：ext4 默认 + noatime
- **大文件（视频/日志）**：XFS 更优
- **需要快照/子卷**：Btrfs 或 ZFS
- **极致数据安全**：ZFS

## 关键 takeaway

| 优势 | 劣势 |
|------|------|
| 成熟稳定 | 无 COW，无法高效快照 |
| 工具齐全 | 元数据无校验和（ext4 现在有了 metadata_csum） |
| 广泛支持 | 单盘性能不及 XFS |
| 兼容性好 | 不能跨盘管理（无 volume manager 概念） |


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

<!-- svg-injected:do-not-edit -->

## 图示：ext4 块组 + Journal + Extent

![ext4 块组 + Journal + Extent](/ext4-layout.svg)
