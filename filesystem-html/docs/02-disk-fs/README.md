# 02 · 本地盘文件系统

<span class="kg-badge kg-badge-disk-fs">本地盘</span>

单块磁盘上的文件系统——从 ext4 到 ZFS，每种 FS 都是一组权衡。

## 章节目录

| 节点 | 一句话 |
|------|--------|
| [ext4 经典之选](/02-disk-fs/ext4) | Linux 默认，稳定可靠，日志型 FS |
| [XFS 高性能日志](/02-disk-fs/xfs) | SGI 血统，分配组 + B+ tree |
| [Btrfs COW 与快照](/02-disk-fs/btrfs) | 写时复制，内置快照与校验 |
| [ZFS 企业级](/02-disk-fs/zfs) | Sun 遗产，终极可靠性 + RAID-Z |
| [NTFS / FAT / exFAT](/02-disk-fs/windows-fs) | Windows 世界的事实标准 |
| [APFS / HFS+](/02-disk-fs/apple-fs) | Apple 设备的 FS 历史 |
| [横向对比与选型](/02-disk-fs/compare) | 7 种 FS 一张表选型 |

## 选型决策树

```
你要在 Linux 上用？
├── 默认 / 数据库 / 通用    → ext4
├── 大文件顺序写（视频/日志） → XFS
├── 需要快照 / 子卷          → Btrfs
├── 终极可靠性 / NAS         → ZFS
└── Windows 兼容             → NTFS / exFAT
```


<!-- auto-enrich:do-not-edit -->

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
