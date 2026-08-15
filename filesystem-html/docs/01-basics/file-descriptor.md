---
title: 文件描述符与 open
---

# 文件描述符与 open

<span class="kg-badge kg-badge-basics">基础</span>

`open()` 返回的那个 int 是什么？fd 表如何工作？为什么 `Too many open files`？

## 什么是文件描述符（fd）

文件描述符是进程级的**整数索引**，指向内核中的"打开文件表"项。

```c
int fd = open("/etc/passwd", O_RDONLY);
// fd = 3 （0/1/2 通常被 stdin/stdout/stderr 占用）

ssize_t n = read(fd, buf, sizeof(buf));
write(1, buf, n);  // fd 1 = stdout
```

## 三张表的层次

```
进程（task_struct）
  ↓ 持有
files_struct（fdtable）
  ↓ 数组
fd_array[0..NR_OPEN_DEFAULT-1]
  ↓ 每个元素指向
struct file（打开文件表项）←—— 所有进程共享的 open file table
  ↓ 持有
struct inode（实际文件）
  ↓ 持有
struct path → dentry → super_block
```

**关键**：多个 fd 可以指向同一个 file（比如 `dup()` 后）；多个进程可以指向同一个 file（比如 `fork()` 后）；但 inode 是唯一的。

## 进程级 fd 表

```bash
# 查看当前进程的所有 fd
ls -la /proc/self/fd/
# 输出：
# lrwx------ 1 user user 64 Aug 1 10:00 0 -> /dev/pts/0
# lrwx------ 1 user user 64 Aug 1 10:00 1 -> /dev/pts/0
# lrwx------ 1 user user 64 Aug 1 10:00 2 -> /dev/pts/0
# lrwx------ 1 user user 64 Aug 1 10:00 3 -> /tmp/foo

# 总数
ls /proc/self/fd/ | wc -l

# 限制
ulimit -n
# 默认 1024 或 65535（取决于发行版）
```

## 经典问题：Too many open files

```
错误：Too many open files (errno 24, EMFILE)
```

**定位**：
```bash
# 系统级限制
cat /proc/sys/fs/file-max   # 系统全局
cat /proc/sys/fs/file-nr    # 已分配 / 未使用 / 最大

# 进程级限制
ulimit -n
cat /proc/PID/limits | grep "open files"

# 看哪个进程打开了最多
lsof | awk '{print $2}' | sort | uniq -c | sort -rn | head

# 看某进程具体打开了啥
lsof -p PID | head -50
```

**修复**：
```bash
# 临时
ulimit -n 65535

# 永久（/etc/security/limits.conf）
*    soft    nofile    65535
*    hard    nofile    65535

# 系统级
echo 2097152 > /proc/sys/fs/file-max
# 永久：/etc/sysctl.conf
fs.file-max = 2097152
```

## open 的标志位

```c
int fd = open(path, flags, mode);
// flags 常用值：
O_RDONLY      // 只读
O_WRONLY      // 只写
O_RDWR        // 读写
O_CREAT       // 不存在则创建（需要 mode）
O_EXCL        // 与 O_CREAT 同用，已存在则失败（原子创建）
O_TRUNC       // 截断为 0
O_APPEND      // 追加写
O_NONBLOCK    // 非阻塞
O_CLOEXEC     // exec 时自动关闭（防泄漏到子进程）
O_DIRECT      // 绕过 page cache（数据库场景）
O_SYNC        // write 立即落盘（强同步，性能差）
```

## open vs fopen

```c
// POSIX 系统调用（直接 fd）
int fd = open(path, O_RDONLY);
read(fd, buf, n);
close(fd);

// C 标准库（带缓冲的 FILE*）
FILE *fp = fopen(path, "r");
fread(buf, 1, n, fp);  // 内部会多次 read + 用户态缓冲
fclose(fp);              // 关闭底层 fd
```

**性能**：fopen 对小读取更友好（用户态缓冲减少 syscall）。但 `fread` + `fwrite` 的隐式缓冲可能让"刚 write 的数据没落盘"成为调试噩梦。

## dup / dup2 / fcntl

```c
// 复制 fd（指向同一 file）
int fd2 = dup(fd1);

// 重定向（关闭 newfd，复制 oldfd 到 newfd）
dup2(fd1, STDOUT_FILENO);  // stdout → fd1 的文件

// 高级控制
fcntl(fd, F_SETFL, O_NONBLOCK);  // 设非阻塞
fcntl(fd, F_GETFD);              // 取标志
```

## fork / exec 时的 fd 行为

```c
// fork 后：子进程继承父进程的 fd（共享同一 file）
// exec 后：默认继承，但设置了 O_CLOEXEC 的会被关闭
// 关进程：所有 fd 自动关闭（引用计数归零才真正关闭 file）
```

## 实战：写一个 fd 监控 demo

```c
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>

int main() {
    // 故意打开 100 个 fd
    int fds[100];
    for (int i = 0; i < 100; i++) {
        char path[64];
        snprintf(path, sizeof(path), "/tmp/test_%d", i);
        fds[i] = open(path, O_CREAT | O_RDWR, 0644);
    }
    printf("Opened 100 fds, current pid=%d\n", getpid());
    printf("Check: ls /proc/%d/fd | wc -l\n", getpid());
    getchar();  // 暂停
    
    for (int i = 0; i < 100; i++) close(fds[i]);
    return 0;
}
```

```bash
# 另一个终端
./demo &
ls /proc/PID/fd | wc -l
# 输出 104（100 + 0/1/2 + 监听 fd）
```

## 关键 takeaway

| 概念 | 关键事实 |
|------|---------|
| fd | 进程级整数索引 |
| file | 内核打开文件表项（多 fd / 多进程可共享） |
| inode | 文件本身（唯一） |
| EMFILE | 进程 fd 用尽，调 ulimit -n |
| close | 引用计数 -1，归零才真正释放 |