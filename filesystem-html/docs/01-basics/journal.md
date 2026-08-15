# 日志与一致性

<span class="kg-badge kg-badge-basics">基础</span>

突然断电，文件系统会不会坏？日志（journal）就是答案。

## 什么是日志（Journaling）

**Journal**（也叫 write-ahead log）是 FS 在正式写数据之前，先把"我要做什么改动"记到日志区的技术。断电后通过 replay 日志保证一致性。

## 没有日志会怎样？

假设执行 `write /a/file`：
1. 写 inode
2. 写数据块
3. 更新目录项

如果在步骤 1 和 2 之间断电：
- inode 显示"新数据"（大小变了）
- 实际数据是旧的（或部分写入的）
- 文件系统**不一致**

下次启动 fsck 会扫整个 FS 找孤立 inode，修得很慢（小时级）。

## 有日志怎样工作？

写 `file` 之前：
1. **JBD**: 在 journal 写入 "打算改 inode X，data block Y"
2. **commit**: journal 打 commit 标记
3. **checkpoint**: 实际写 inode 和 data block
4. **释放 journal**: journal 可以被复用

断电后：
- 如果 journal 有 commit → replay 写操作（应用层日志）
- 如果 journal 无 commit → 直接丢弃 journal（什么都没做）

> **保证**：要么完全做了，要么没做。永远不会是"半完成"。

## ext4 的日志模式

```bash
# 查看当前日志模式
tune2fs -l /dev/sda1 | grep "Filesystem features"
# has_journal, ext_attr, ...

# 修改日志模式
tune2fs -o journal_data /dev/sda1
tune2fs -o journal_data_ordered /dev/sda1  # 默认
tune2fs -o journal_data_writeback /dev/sda1
```

| 模式 | 写数据 | 写元数据 | 性能 | 一致性 |
|------|--------|----------|------|--------|
| `journal` | 先写日志 | 先写日志 | 慢 | 强 |
| `ordered`（默认） | 写数据后写元数据日志 | 先写日志 | 中 | 元数据 + 数据顺序 |
| `writeback` | 仅元数据写日志 | 先写日志 | 快 | 仅元数据 |

**生产推荐**：`ordered` 是最佳平衡。

## 其他 FS 的等效机制

### XFS：自己的日志

```bash
xfs_info /dev/sda1
# log size=... （默认 32 MB）
# 不能关闭日志（XFS 必须日志化）
```

### Btrfs：COW + 检查和

Btrfs 不依赖传统 journal，用 **copy-on-write**：
- 写新数据到新位置
- 写元数据指针更新
- 旧版本仍存在（变成快照）
- 全程用 checksum 验证一致性

```bash
btrfs scrub start /mnt/btrfs  # 在线校验
btrfs balance start /mnt/btrfs  # 重新平衡
```

### ZFS：类似 COW + 端到端校验

```bash
zpool scrub tank    # 校验整个 pool
```

## COW vs Journal

```
Journal (ext4):
  写元数据前先记录"打算写什么"
  断电后 replay journal
  优点：兼容性好，性能可控
  缺点：日志是固定开销，双倍写

COW (Btrfs/ZFS):
  写新数据到新位置，原子切换指针
  断电后旧版本仍然完整（指针未更新）
  优点：天然支持快照，写入放大可控
  缺点：实现复杂，碎片问题
```

## 日志大小与位置

```bash
# ext4 日志大小
dumpe2fs /dev/sda1 | grep -i journal
# Journal size:           128M
# Journal backup:         inode blocks

# 日志通常和 FS 在同一磁盘
# 也可以放到独立设备（极端性能场景）
mke2fs -O journal_dev /dev/sdc1  # 单独日志设备
mount -o journal_dev=/dev/sdc1 /dev/sdb1 /mnt  # 用它
```

## 实战：观察日志

```bash
# 查看 ext4 journal 操作统计（需要 debugfs）
debugfs -R "stats" /dev/sda1 | grep -i journal

# 监控 dirty page 写回（journal 触发）
iostat -dx 1
# 看到 w/s 大幅波动就是 writeback 在工作

# 强制 replay（恢复后挂载）
mount -o ro,norecovery /dev/sda1 /mnt/recover  # 不 replay
mount /dev/sda1 /mnt  # 自动 replay
```

## 经典案例：断电后挂载失败

```
mount: wrong fs type, bad option, bad superblock on /dev/sdb1
       or too many mounted file systems
```

**排查**：
```bash
# 1. 看 superblock 状态
dumpe2fs /dev/sdb1 | head -20

# 2. 尝试用备份 superblock 挂载
mkfs.ext4 -n /dev/sdb1  # 看备份位置
mount -o sb=131072 /dev/sdb1 /mnt/recover

# 3. fsck 修复（先备份 image）
dd if=/dev/sdb1 of=/backup/sdb1.img
fsck.ext4 -y /dev/sdb1
```

## 关键 takeaway

| FS | 一致性机制 | 关键命令 |
|----|-----------|---------|
| ext4 | journal | `tune2fs -o journal_data_ordered` |
| XFS | journal（强制） | `xfs_repair` |
| Btrfs | COW + checksum | `btrfs scrub` |
| ZFS | COW + checksum | `zpool scrub` |
| NTFS | journal ($LogFile) | `chkdsk /f` |
| APFS | COW + clones | `diskutil repairVolume` |