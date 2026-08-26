---
title: 横向对比与选型
---

# 横向对比与选型

<span class="kg-badge kg-badge-disk-fs">本地盘</span>

7 种主流本地文件系统——一张表选型。

## 总览

| FS | 平台 | 一致性 | 快照 | 校验和 | 加密 | 默认 |
|----|------|--------|------|--------|------|------|
| **ext4** | Linux | journal | ❌ | ⚠️（metadata_csum） | ⚠️（LUKS 层） | Ubuntu/Debian |
| **XFS** | Linux | journal | ❌ | ✅（元数据） | ⚠️（LUKS） | RHEL 7+ |
| **Btrfs** | Linux | COW | ✅ | ✅ | ⚠️ | openSUSE |
| **ZFS** | Linux/FreeBSD/macOS | COW | ✅ | ✅（端到端）| ✅（原生） | FreeBSD/Solaris |
| **NTFS** | Windows | journal | ❌（VSS）| ⚠️ | ✅（EFS） | Windows |
| **exFAT** | 全平台 | ❌ | ❌ | ❌ | ❌ | U盘 |
| **APFS** | Apple | COW | ✅ | ✅ | ✅（原生） | macOS 10.13+ |

## 详细对比

### 容量

| FS | 单卷最大 | 单文件最大 |
|----|---------|----------|
| ext4 | 1 EiB | 16 TiB |
| XFS | 8 EiB | 8 EiB |
| Btrfs | 16 EiB | 16 EiB |
| ZFS | 256 ZiB | 16 EiB |
| NTFS | 256 TB | 16 TB |
| exFAT | 128 PiB | 16 EiB |
| APFS | 8 EiB | 8 EiB |

### 性能特征

| FS | 顺序写 | 随机 IO | 大目录 | 小文件 |
|----|--------|---------|--------|--------|
| ext4 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| XFS | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Btrfs | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| ZFS | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| NTFS | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 功能矩阵

| 功能 | ext4 | XFS | Btrfs | ZFS | NTFS | APFS |
|------|------|-----|-------|-----|------|------|
| COW | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ |
| 内置快照 | ❌ | ❌ | ✅ | ✅ | ❌（VSS 外部） | ✅ |
| 内置 RAID | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |
| 透明压缩 | ❌ | ❌ | ✅ | ✅ | ✅（LZNT1）| ✅ |
| 透明加密 | ❌ | ❌ | ⚠️（实验） | ✅ | ✅（EFS）| ✅ |
| 去重 | ❌ | ❌ | ⚠️ | ⚠️（耗内存） | ❌ | ❌ |
| 在线扩容 | ✅ | ✅ | ✅ | ✅ | ✅（部分）| ✅ |
| 缩小 FS | ✅ | ❌ | ✅ | ❌ | ✅ | ⚠️ |
| 子卷 | ❌ | ❌ | ✅ | ✅（dataset）| ❌ | ✅ |
| 配额 | ✅ | ✅（项目） | ✅ | ✅ | ✅ | ⚠️ |

## 选型决策树

### 场景 1：Linux 服务器系统盘

```
需要稳定性 + 通用？
└── ✅ ext4（首选）

大文件顺序 IO（视频/日志/数据库）？
└── ✅ XFS（RHEL 默认）

需要频繁快照（如开发/测试环境）？
├── 接受 ZFS 学习曲线 → ZFS
└── 想要轻量 → Btrfs
```

### 场景 2：NAS / 家用存储

```
数据安全最重要（校验 + 自愈）？
├── ✅ ZFS（业界 20 年验证）
└── ⚠️ Btrfs（RAID5/6 历史问题，慎用）

要 macOS 客户端兼容？
└── ✅ ZFS 或 APFS（如果都用 Mac）
```

### 场景 3：数据库

```
MySQL / PostgreSQL？
└── ext4 + noatime（稳定）或 XFS（大数据）

Oracle？
└── 专用 FS（OCFS2）或直接裸设备

MongoDB？
└── XFS 或 ext4
```

### 场景 4：U 盘 / 外接存储

```
跨平台 + 大文件？
└── ✅ exFAT（兼容性最好）

只 Windows？
└── NTFS

只 Mac？
└── APFS（macOS）或 exFAT
```

### 场景 5：容器存储

```
Docker / containerd 数据目录？
└── ext4 / XFS（标准）

需要 overlay2 性能？
└── ext4 + 大量 inode
```

## 性能基准（典型 NVMe）

**顺序写 1GB 文件**：
- XFS:    ~3.0 GB/s
- ext4:   ~2.8 GB/s
- Btrfs:  ~2.5 GB/s
- ZFS:    ~2.4 GB/s（无 dedup + lz4）

**4KB 随机写 IOPS**：
- ext4:   ~150K
- XFS:    ~140K
- ZFS:    ~100K
- Btrfs:  ~80K（COW 开销）

**创建 100 万个小文件**：
- ext4:   28s
- XFS:    35s
- Btrfs:  90s（COW 慢）

> ⚠️ 实际性能**强烈依赖**内核版本、硬件、配置。以上仅参考。

## 迁移路径

### Linux: ext4 → XFS

```bash
# 不能在线转换，需要：
1. 备份数据
2. mkfs.xfs 新分区
3. restore 数据
```

### Linux: ext4 → Btrfs

```bash
# btrfs-convert 可以"在线"转换（但有风险）
umount /mnt/data
btrfs-convert /dev/sdb1
mount /dev/sdb1 /mnt/data
# 转换后可以 btrfs balance 整理
```

### Windows: NTFS → ReFS

```cmd
# ReFS（Resilient File System）是 Microsoft 的 ZFS 替代品
# 用于 Storage Spaces Direct 和某些服务器场景
# 不通用，慎用
```

## 决策矩阵（最常见 5 场景）

| 你的角色 | 推荐 |
|---------|------|
| **个人 Linux 桌面** | ext4（默认，无忧） |
| **Linux 服务器运维** | XFS（大数据） + ext4（系统盘）|
| **架构师 / 平台** | ZFS（关键数据）+ ext4（普通）|
| **DevOps / K8s** | ext4 / XFS（按场景）|
| **NAS / 家用** | ZFS（首选）或 Btrfs |
| **数据库 DBA** | ext4 / XFS（看 DB 类型） |
| **Windows 用户** | NTFS（系统）+ exFAT（U 盘）|
| **Mac 用户** | APFS（系统）+ exFAT（跨平台）|

## 关键 takeaway

> **没有"最好"的 FS，只有"最适合"的 FS**。
>
> 90% 的 Linux 场景用 ext4 就对了。需要高级特性（快照/校验/RAID）才考虑 ZFS / Btrfs。
>
> **不要**为了"用 ZFS 而用 ZFS"——学习曲线和维护成本不低。


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
