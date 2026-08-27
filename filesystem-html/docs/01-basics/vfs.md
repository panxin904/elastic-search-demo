---
title: VFS 虚拟文件系统
---

# VFS 虚拟文件系统

<span class="kg-badge kg-badge-basics">基础</span>

Linux 的"万能适配器"——同一套系统调用接口支持 ext4 / NTFS / NFS / procfs / sysfs ...

## VFS 是什么

**VFS**（Virtual File System）是 Linux 内核中的一层抽象，让上层应用看到的是"统一的文件操作接口"，下层可以接入任何具体文件系统。

```
应用层   →  read() / write() / open()  (POSIX 系统调用)
                ↓
VFS 层   →  通用文件操作框架（super_operations / inode_operations / file_operations）
                ↓
具体 FS  →  ext4 / xfs / btrfs / nfs / procfs / sysfs / ...
                ↓
块设备   →  磁盘 / SSD / 网络存储
```

**为什么需要 VFS**：
- 同一个 `open("/a/b")` 能打开本地文件、NFS 远程文件、甚至 `/proc/cpuinfo`
- FS 可以即插即用（模块化）
- 同一个进程可以同时挂载多个 FS

## VFS 的四大核心对象

```c
// 1. super_block - 代表一个挂载的文件系统实例
struct super_block {
    struct list_head s_list;       // 所有 super_block 链表
    dev_t s_dev;                   // 设备标识
    struct file_system_type *s_type;  // FS 类型
    const struct super_operations *s_op;  // FS 操作函数表
    struct dentry *s_root;         // 根目录
    // ...
};

// 2. inode - 代表一个文件
struct inode {
    const struct inode_operations *i_op;  // inode 操作
    struct super_block *i_sb;             // 所属 FS
    // ...
};

// 3. dentry - 代表一个目录项（路径解析单元）
struct dentry {
    struct inode *d_inode;
    struct dentry *d_parent;
    const struct dentry_operations *d_op;
    // ...
};

// 4. file - 代表一个打开的文件（fd 背后的实体）
struct file {
    const struct file_operations *f_op;
    struct inode *f_inode;
    struct path f_path;
    // ...
};
```

## 三大操作表

每个 FS 必须实现这 3 个函数表：

### super_operations
```c
struct super_operations {
    int (*write_inode)(struct inode *, int);  // 写回 inode
    void (*put_super)(struct super_block *);   // 卸载 FS
    int (*remount_fs)(struct super_block *, int *, char *);
    void (*sync_fs)(struct super_block *, int);
    // ...
};
```

### inode_operations
```c
struct inode_operations {
    int (*create)(struct inode *, struct dentry *, umode_t, bool);
    struct dentry *(*lookup)(struct inode *, struct dentry *, unsigned int);
    int (*link)(struct dentry *, struct inode *, struct dentry *);
    int (*unlink)(struct inode *, struct dentry *);
    int (*mkdir)(struct inode *, struct dentry *, umode_t);
    // ...
};
```

### file_operations
```c
struct file_operations {
    ssize_t (*read)(struct file *, char __user *, size_t, loff_t *);
    ssize_t (*write)(struct file *, const char __user *, size_t, loff_t *);
    int (*open)(struct inode *, struct file *);
    int (*release)(struct inode *, struct file *);
    loff_t (*llseek)(struct file *, loff_t, int);
    // ...
};
```

## 实战：查看 VFS 状态

```bash
# 当前挂载的所有 FS
mount | column -t

# 当前内核支持的 FS 类型
cat /proc/filesystems

# dentry 缓存状态
cat /proc/sys/fs/dentry-state

# inode 缓存
cat /proc/sys/fs/inode-state

# 看某个进程打开了哪些文件
ls -la /proc/PID/fd/

# 看某个文件属于哪个 FS
stat -f /etc/passwd
# Type: ext4/devtmpfs
```

## 案例：两个 FS 的文件可以混用

```bash
# 假设 /a 是 ext4，/b 是 ntfs-3g 挂载的 NTFS 分区
cp /a/data.txt /b/  # 这条 cp 跨了两个 FS
# 但用户视角是：把一个文件复制到另一个目录
# VFS 在底层自动处理了 FS 差异：
#   - 源 ext4 的 read() 调用 ext4_file_read
#   - 目标 NTFS 的 write() 调用 ntfs_file_write
#   - 中间是内核 page cache 缓冲
```

## 案例：/proc 和 /sys

```proc
/proc/cpuinfo   # 由 procfs（内存 FS，无磁盘）提供
/sys/block/     # 由 sysfs（内核对象 FS）提供
/dev/sda1       # 由 devtmpfs（设备 FS）提供
/tmp            # 通常是 tmpfs（内存盘 FS）
```

这些都不是磁盘上的"真"文件系统，但通过 VFS 提供相同接口——这就是 VFS 抽象的力量。

## mount：FS 接入点

```c
// mount 一个 FS 的简化流程
do_mount()
  → 分配 super_block
  → 调用 FS 的 mount()（如 ext4_fill_super）
  → 读取 FS 超级块（磁盘前 1KB）
  → 关联到挂载点的 dentry
```

mount 把 FS 的根 dentry 接到 VFS 树的某个目录，从此该 FS 的文件可通过该路径访问。

## 关键 takeaway

| 特性 | 说明 |
|------|------|
| 统一接口 | 应用看到的 API 完全相同 |
| 可插拔 | 任何实现 3 个 ops 的 FS 都能接入 |
| 缓存友好 | dentry/inode cache 跨 FS 共享 |
| 多态 | 同一个进程可同时挂载 N 个 FS |


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

## 图示：VFS 四大对象与具体文件系统

![VFS 四大对象与具体文件系统](/linux-vfs.svg)
