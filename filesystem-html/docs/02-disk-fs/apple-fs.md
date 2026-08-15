# APFS / HFS+

<span class="kg-badge kg-badge-disk-fs">本地盘</span>

Apple 设备的文件系统演进——从 HFS+ 到 APFS。

## HFS+（Hierarchical File System Plus）

1985 年发布的 Mac OS 经典 FS，1998 年随 Mac OS 8.1 引入 HFS+。

### 特性

- B-tree 目录索引
- Catalog（文件元数据）
- Extents overflow file
- 区分大小写（可选）
- Unicode 文件名

### 限制

- 单文件最大 8 EiB（理论）
- 无 COW（克隆需要复制）
- 无原生快照（依赖 Time Machine 的硬链接技巧）
- 时间戳精度 1 秒

### Time Machine 的黑科技

HFS+ 没有原生快照，但 Time Machine 用**硬链接 + 目录 inode**模拟：

```
/Volumes/Backup/
├── 2026-08-01/      ← 第一次备份
│   └── Users/Alice/Documents/foo.txt
├── 2026-08-02/      ← 第二次备份（使用硬链接共享未变文件）
│   └── Users/Alice/Documents/foo.txt (硬链接 → 同一个 inode)
├── 2026-08-08/
│   └── Users/Alice/Documents/foo.txt (新版本，独立 inode)
└── ...
```

未变的文件复用 inode（不占空间），变化的文件创建新 inode。看起来像快照，原理是硬链接 + inode 引用计数。

### macOS 用到什么时候

- macOS Sierra (10.12) 及更早默认 HFS+
- macOS High Sierra (10.13) 默认 APFS
- Time Machine 备份盘仍可使用 HFS+

## APFS（Apple File System）

2017 年发布，专为 SSD 和现代存储设计。Apple File System。

### 设计目标

- SSD 优化（TRIM、零拷贝）
- 内置快照和克隆
- 加密原生
- 空间共享（Space Sharing）
- 多设备容器

### 核心特性

#### 1. 空间共享（Space Sharing）

传统 FS：每个卷独立固定大小
APFS：容器内所有卷共享同一空间池

```
Container (物理磁盘)
  ├── Volume 1 (macOS)         ← 不需要预分配大小
  ├── Volume 2 (Data)
  └── Volume 3 (Backup)
所有 Volume 共享 Container 的容量
```

**优势**：不需要预先规划各卷大小，动态按需分配。

#### 2. 克隆（Clone）

```bash
# APFS clone = 写时复制，几乎瞬时，零额外空间
cp -c file.txt file-backup.txt
# 实际上两者共享 inode，直到其中一个修改
```

**实现**：APFS 文件 = 树状结构，多个"文件"可以共享子树。

#### 3. 快照（Snapshot）

```bash
# APFS 原生快照
tmutil snapshot /Volumes/Macintosh\ HD
# 或
diskutil apfs addSnapshot /dev/disk1s1 -name "before-update"

# 列出快照
diskutil apfs listSnapshots /dev/disk1s1

# 回滚（macOS Recovery）
```

#### 4. 加密

APFS 原生支持：
- **FileVault**：全盘加密
- **单文件加密**：不同文件可不同密钥
- 性能影响 < 5%（现代 CPU AES 指令）

#### 5. TRIM 与 SSD 优化

```bash
# APFS 自动向 SSD 发送 TRIM
# 不需要手动管理

# 看 TRIM 状态
system_profiler SPNVMeDataType
```

### APFS 限制

| 限制 | 值 |
|------|-----|
| 单卷最大 | 8 EiB（理论）|
| 单文件最大 | 8 EiB（理论）|
| 时间戳精度 | 1 纳秒 |
| 文件名 | UTF-8 最多 255 字节 |

### 实战：APFS 命令

```bash
# 看分区布局
diskutil list
diskutil apfs list

# 创建 APFS 容器
diskutil apfs createContainer /dev/disk0s2

# 加卷
diskutil apfs addVolume /dev/disk0s2 APFS Data

# 加密
diskutil apfs encryptVolume /dev/disk0s2

# 快照
diskutil apfs addSnapshot disk0s2 -name "before-update"
diskutil apfs revert disk0s2 -snapshot "before-update"
```

## APFS vs HFS+

| 特性 | HFS+ | APFS |
|------|------|------|
| 首次发布 | 1998 | 2017 |
| 写时复制 | ❌ | ✅ |
| 克隆 | ❌ | ✅（瞬时）|
| 快照 | ⚠️（TM hack）| ✅（原生）|
| SSD 优化 | ❌ | ✅ |
| 空间共享 | ❌ | ✅ |
| 加密 | ⚠️（CoreStorage）| ✅（原生）|
| 时间戳精度 | 1 s | 1 ns |
| 默认 | 10.12 及更早 | 10.13+ |
| iOS | ❌ | ✅（10.3+） |

## iOS / iPadOS 的 APFS

iOS 10.3+ 默认 APFS，但用户看不到命令行管理。系统自动使用：
- 快照（系统更新前自动备份）
- 克隆（App 数据高效共享）
- 加密（默认全设备加密）

## 跨平台访问

```bash
# Linux 读 APFS（实验性）
git clone https://github.com/yanburman/apfs-fuse.git
cd apfs-fuse
make
./apfs-fuse /dev/sdb1 /mnt

# ⚠️ 只读，且不稳定

# macOS 共享给 Linux：推荐 exFAT
diskutil eraseVolume ExFAT Shared /dev/disk1s1
```

## 实战：Time Machine 的 APFS 进化

```bash
# macOS Big Sur+ 的 Time Machine 用 APFS 原生快照
# 不再需要"稀疏捆绑"黑科技

# 配置 TM 目标
tmutil setdestination /Volumes/Backup

# 立即备份
tmutil startbackup

# 列出备份快照
tmutil listbackups
tmutil destinationinfo /Volumes/Backup

# 删除旧备份
tmutil delete /Volumes/Backup/2026-06-01-123456
```

## 关键 takeaway

| 选 HFS+ 何时 | 选 APFS 何时 |
|--------------|--------------|
| 旧 macOS（< 10.13） | 现代 Mac |
| Time Machine 老备份盘 | 任何新部署 |
| 兼容老软件 | 需要快照/克隆 |
| 几乎不再推荐 | **默认选 APFS** |