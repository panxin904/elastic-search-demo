---
title: inode 与 dentry
date: 2026-08-15  # date-auto-injected
---

# inode 与 dentry

<span class="kg-badge kg-badge-basics">基础</span>

理解"文件"的本质——文件名只是别名，真正的身份证是 inode。

## inode 是什么

**inode**（index node）是 Linux 文件系统中描述文件元数据的数据结构。它不包含文件名，但包含文件的所有"非名字信息"。

```c
struct inode {
    umode_t  i_mode;       // 权限 + 类型
    uid_t    i_uid;        // 所有者
    gid_t    i_gid;        // 所属组
    unsigned long i_ino;   // inode 号（文件系统内唯一）
    dev_t    i_dev;        // 设备号
    loff_t   i_size;       // 文件大小
    time_t   i_atime;      // 访问时间
    time_t   i_mtime;      // 修改时间
    time_t   i_ctime;      // 元数据变更时间
    blkcnt_t i_blocks;     // 占用的块数
    struct block_device *i_bdev;  // 块设备指针
    // ... 数据块指针（直接/间接/双间接/三间接）
};
```

**关键事实**：
- 文件名 ≠ inode。一个文件可以多个名字（硬链接），但只有一个 inode。
- 删除文件 = 减少链接数 + inode 引用计数归零。
- inode 总数在 mkfs 时固定。`df -i` 查看剩余。

## inode 与文件名分离

```
目录本质：name → inode 的映射表
```

例如 `/data/file.txt`：
- `/data` 是目录，它的 inode 指向一个"目录文件"内容
- "目录文件"内容是若干 `(name, inode)` 对
- `file.txt` → inode 12345
- inode 12345 才是真正存储数据的结构

所以 `mv /a/file /b/file` 只是改了目录项映射，inode 没变 → 极快。

## dentry 是什么

**dentry**（directory entry）是 VFS 的目录项缓存层。它把"路径 → inode"的映射缓存在内存中，避免每次都走磁盘解析路径。

```c
struct dentry {
    unsigned int d_flags;
    struct inode  *d_inode;   // 关联的 inode
    const char    *d_name;    // 文件名
    struct dentry *d_parent;  // 父目录
    struct list_head d_child; // 兄弟节点链表
    struct super_block *d_sb; // 所属超级块
    // ... hash、LRU 链表等
};
```

**为什么需要 dentry**：
- 路径解析 `/a/b/c/d` 需要依次查 4 个目录
- 没有缓存 → 每次都 4 次磁盘 IO
- 有缓存 → 命中后 0 次磁盘 IO

## 三者的关系

```
进程视角              VFS 层              FS 实现
─────────         ──────────         ──────────
fd (file*)         dentry (缓存)      inode (磁盘)
   ↓                  ↓                  ↓
"open file"表      路径 ↔ inode       元数据 + 数据
                    哈希 + LRU
```

## 实战：查看 inode 与 dentry

```bash
# 看 inode 信息
stat /etc/passwd
# 输出包含：Inode: 1234567 Links: 1

# 看 dentry 缓存命中率
cat /proc/sys/fs/dentry-state
# 234567  198765  45  0  0  100  0
#   ↑       ↑     ↑
#   |       |     dentry 命中率（%）
#   |       未使用 dentry
#   已分配 dentry

# 强制回收 dentry（谨慎！会导致性能抖动）
echo 1 > /proc/sys/vm/drop_caches
# 或
echo 2 > /proc/sys/vm/drop_caches  # 只清 dentry + inode
```

## 经典坑：inode 用尽

```
报错：No space left on device
df -h → 还有 50% 空间
df -i → 100% inode 已用
```

**原因**：小文件太多（每个文件至少占 1 个 inode）。

**修复**：
- 删无用文件（找空 inode 目录）
- 重构为更少的大文件
- 重新 mkfs 时调高 bytes-per-inode（牺牲 inode 换容量）

## 调试命令

```bash
# 看某个目录的 inode 占用 Top
find /var -xdev -type f | awk -F/ '{print $1}' | sort | uniq -c | sort -rn | head

# 看具体文件的 inode
ls -i /etc/passwd
# 输出第一列就是 inode 号

# 看具体目录项
getfacl /path
```

## 关键 takeaway

| 概念 | 作用 | 存储位置 |
|------|------|----------|
| **inode** | 文件元数据 | 磁盘 + inode cache（内存） |
| **dentry** | 路径解析缓存 | 仅内存（dentry cache） |
| **file** | 进程打开的文件 | 仅内存（fd table） |

文件名的作用**仅仅**是把路径解析到 inode。理解这一点，所有看似诡异的 FS 现象都迎刃而解。


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
