---
title: 目录与路径解析
---

# 目录与路径解析

<span class="kg-badge kg-badge-basics">基础</span>

`/a/b/c` 这个路径是怎么解析到 c 的？软链接和硬链接的本质区别是什么？

## 路径分类

```
绝对路径：从根开始  /var/log/syslog
相对路径：从当前 cwd 开始  ./log/syslog
```

Linux 内核只理解绝对路径，相对路径在用户态库（glibc）转换为绝对路径后传给 syscall。

```c
// 简化版 getcwd()
char cwd[PATH_MAX];
getcwd(cwd, sizeof(cwd));

// open 相对路径
int fd = open("./foo.txt", O_RDONLY);
// 内核实际看到的是：open("/current/cwd/foo.txt")
```

## 路径解析流程

```c
open("/a/b/c", O_RDONLY);
  → link_path_walk("/a/b/c", &nd)
    → 逐段解析：
      "/" → 根 dentry（缓存）
      "a" → 在根 inode 中查找 → dentry (a)
      "b" → 在 a inode 中查找 → dentry (b)
      "c" → 在 b inode 中查找 → dentry (c)
    → 返回 c 的 inode
  → do_last → may_open → 文件创建/打开
```

**关键优化**：
- 每一段查找都先看 dentry cache
- 命中 → 直接拿 inode
- 未命中 → 调用 FS 的 lookup（如 ext4_lookup）

## dentry cache 命中率

```bash
# 系统级
cat /proc/sys/fs/dentry-state
# 234567 198765 45 0 0 100 0
#  ↑       ↑     ↑
#  |       |     hit ratio（45% 偏低）
#  |       unused dentries
#  allocated

# 应用级（通过 perf 或 eBPF 监控）
```

**为什么命中率重要**：
- dentry cache 命中 = 纳秒级
- 未命中 = 需要读 FS 元数据 → 微秒级
- 大量未命中 = 路径解析成为性能瓶颈

## 软链接（Symbolic Link）

```bash
ln -s /real/path /link/path
```

**本质**：软链接是一个特殊文件，内容是**目标路径字符串**。

```bash
ls -l /link/path
# lrwxrwxrwx 1 user user 11 Aug 1 10:00 /link/path -> /real/path

# 软链接的属性
stat /link/path
# 它有自己的 inode！大小 = 目标路径字符串长度
```

**特点**：
- 可以跨文件系统
- 可以链接到不存在的目标（dangling link）
- 删除源文件后链接变成"死链"
- **解析开销**：每次访问都要重新解析目标

## 硬链接（Hard Link）

```bash
ln /real/file /hard/link
```

**本质**：多个目录项指向**同一个 inode**。

```bash
ls -li /real/file /hard/link
# 1234567 -rw-r--r-- 2 user user 100 Aug 1 /real/file
# 1234567 -rw-r--r-- 2 user user 100 Aug 1 /hard/link
#   ↑         ↑
#   同一个 inode   link count
```

**特点**：
- 不能跨文件系统（inode 在 FS 内唯一）
- 不能链接目录（避免循环）
- 删除一个名字 = 链接数 -1，归零才真正删除
- 软/硬链接对比：

| 维度 | 软链接 | 硬链接 |
|------|--------|--------|
| 跨 FS | ✅ | ❌ |
| 链接目录 | ✅ | ❌ |
| 源删除后 | 死链 | 仍可访问 |
| inode | 自己的 inode | 共享 inode |
| 性能 | 每次解析目标 | 直接访问 |
| 大小 | 路径字符串 | 0（目录项） |

## 路径长度限制

```bash
# 查看
getconf PATH_MAX /   # 通常 4096
# 单个文件名最大
getconf NAME_MAX /   # ext4 是 255

# 内核还限制路径查找深度（避免栈溢出）
# include/linux/namei.h
#define MAXSYMLINKS 40   # 软链接最大递归次数
```

## 实战：循环软链接

```bash
# 创建循环
ln -s /tmp/loop /tmp/loop

# 访问会报错
ls /tmp/loop
# ls: cannot access '/tmp/loop': Too many levels of symbolic links
# 内核 MAXSYMLINKS 保护
```

## 实战：解析路径性能

```c
// strace 看路径解析的 syscall
strace -e trace=open,openat ls -l /var/log
// openat(AT_FDCWD, "/var/log", O_RDONLY|O_NONBLOCK|O_CLOEXEC|O_DIRECTORY) = 3

// perf 看 lookup 热点
perf record -e 'fs:*' -g ls /var/log
perf report
```

## 实战：使用 openat 避免 race

```c
// ❌ 老式：cwd 切换不安全（多线程）
chdir("/var/log");
int fd = open("app.log", O_RDONLY);  // 假设 chdir 后 cwd 变了

// ✅ 新式：相对目录 fd
int dirfd = open("/var/log", O_RDONLY | O_DIRECTORY);
int fd = openat(dirfd, "app.log", O_RDONLY);
// 不会受其他线程 chdir 影响
```

## 路径组件的特殊字符

```c
// 含空格 / 中文 / 特殊字符
open("/tmp/has space.txt", O_RDONLY);
open("/tmp/中文.log", O_RDONLY);
// 一切都是字节，内核不解释

// 但 shell 需要引号
ls "/tmp/has space.txt"
```

## 路径缓存：path_lookup

```bash
# 内核维护一个 path cache（hash 表）
# key = (parent_inode, name)
# value = dentry

# 命中 = O(1) 查找
# 未命中 = 调用 FS lookup
```

## 关键 takeaway

| 概念 | 关键 |
|------|------|
| 路径解析 | 从根 dentry 逐段查找 |
| dentry cache | 性能关键（命中率应 > 90%） |
| 软链接 | 自己的 inode，跨 FS，可死链 |
| 硬链接 | 共享 inode，限制多 |
| openat | 多线程安全 |


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
