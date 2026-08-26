---
title: XFS 高性能日志
---

# XFS 高性能日志

<span class="kg-badge kg-badge-disk-fs">本地盘</span>

SGI 血统，分配组 + B+ tree，为大文件和大容量而生。

## 历史

SGI 在 1990 年代为 IRIX 开发 XFS，2001 年开源，2002 年并入 Linux 2.5。RHEL/CentOS 7+ 默认 XFS。

## 核心架构

### 分配组（Allocation Group）

XFS 把磁盘分成多个独立管理的 AG（默认几百个），每个 AG 有自己的：
- inode 池
- 空闲空间管理
- B+ tree 索引

```
Disk:
  AG0: inodes + space + btree
  AG1: inodes + space + btree
  AG2: ...
```

**效果**：
- 多核并行分配（不同 AG 互不阻塞）
- 单 AG 损坏不波及其他
- 大 FS 性能不衰减

### B+ tree 元数据

所有元数据（空闲空间、inode、目录、反向查找）都用 B+ tree：

```
空间管理: B+ tree of free extent ranges
inode 索引: B+ tree of inode chunks
目录索引: B+ tree of (hash, inode) pairs
```

**效果**：目录查找、空间分配都是 O(log n)。

### 分配策略

- **Extent-based allocation**（类似 ext4）
- **延迟分配**：与 ext4 相同的优化
- **多 extent 文件**：单文件可跨多个 extent
- **实时子卷**（RT subvolume）：预留空间给实时任务

### 日志

XFS **强制日志化**，且日志与数据分离：

```bash
xfs_info /dev/sda1
# log size=52428800  # 50 MB
# log = internal log （在数据盘内）
# 或 external log（独立设备）
```

**journal 在 XFS 中更复杂**：支持逻辑日志、并行事务。

## 优势场景

| 场景 | XFS 表现 |
|------|----------|
| 大文件顺序写（视频、日志） | ⭐⭐⭐⭐⭐ |
| 大目录（百万文件） | ⭐⭐⭐⭐⭐ |
| 多线程并行 IO | ⭐⭐⭐⭐⭐ |
| 在线扩容 | ⭐⭐⭐⭐⭐（原生支持） |
| 小文件随机 IO | ⭐⭐⭐（不如 ext4） |
| 缩小 FS | ❌（不支持，只可扩大） |
| 快照 | ❌（需 LVM 或外部工具） |

## 实战

```bash
# 创建
mkfs.xfs /dev/sdb1
mkfs.xfs -L DataDisk -d agcount=8 -l size=128m /dev/sdb1
# -d agcount=8        强制 8 个 AG（默认自适应）
# -l size=128m        journal 128MB

# 挂载优化
mount -o noatime,allocsize=64m,logbufs=8 /dev/sdb1 /mnt/data
# allocsize=64m      预分配 hint（视频/数据库）
# logbufs=8          journal buffers 数（写密集场景调高）

# 在线扩容（XFS 强项）
xfs_growfs /mnt/data     # FS 已扩展到新容量
# 前提是底层设备已扩大（LVM / 4Kn 磁盘 / 虚拟化层）

# 检查（只能在线 check，不能脱机 repair）
xfs_repair -n /dev/sdb1  # 只读检查
# XFS 设计为"挂载就自愈"，通常不需要 repair
```

## XFS 的高级特性

### 项目配额（Project Quota）

```bash
# 限制某个目录树的容量
mount -o prjquota /dev/sdb1 /mnt/data
xfs_quota -x -c 'project -s myproj' /mnt/data
xfs_quota -x -c 'limit -p bsoft=100g bhard=110g myproj' /mnt/data
```

### 在线碎片整理

```bash
# XFS 文件碎片整理
xfs_fsr /dev/sdb1
# 或对单个文件
xfs_fsr -t 3600 /mnt/data/bigfile
# 每 3600 秒整理一次
```

### 实时子卷

```bash
# 预留独立空间给实时进程（避免被普通 IO 饿死）
mkfs.xfs -r rtdev=/dev/sdc1 /dev/sdb1
# /dev/sdb1 是数据
# /dev/sdc1 是实时
```

## 与 ext4 对比（典型差异）

| 特性 | ext4 | XFS |
|------|------|-----|
| 单 FS 最大 | 1 EiB | 8 EiB |
| 单文件最大 | 16 TiB | 8 EiB |
| AG 概念 | ❌ | ✅（核心） |
| 多块分配 | ✅ | ✅ |
| 延迟分配 | ✅ | ✅ |
| 在线扩容 | ✅（resize2fs） | ✅（xfs_growfs） |
| 缩小 FS | ✅ | ❌ |
| 快照 | 外部 | 外部 |
| 默认 RHEL | 6 | 7+ |
| 最大 inode | 受限 | 动态分配（更灵活） |
| metadata 校验 | ✅（新版本） | ✅ |

## 性能调优

```bash
# /etc/fstab 推荐配置
/dev/sdb1 /data xfs defaults,noatime,allocsize=64m,inode64 0 0

# inode64: 跨 AG 分布 inode（大 FS 性能更好）
# allocsize: 预分配 hint

# 监控
xfs_io -x -c "stat /mnt/data/file" /dev/sdb1   # 看 FS 内部状态
xfs_io -x -c "bulkstat" /dev/sdb1              # dump 所有 inode
```

## 关键 takeaway

| 优势 | 劣势 |
|------|------|
| 大文件 / 大容量 / 多核 | 不能缩小 |
| 并行性能强 | 小文件 IO 不如 ext4 |
| 扩容方便 | 没有原生快照 |
| RHEL 默认 | 学习曲线略陡 |

> **选 XFS 的理由**：单 FS > 50TB 或大文件顺序写场景。


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
