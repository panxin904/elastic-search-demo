---
title: strace / ltrace
---

# strace / ltrace — 系统调用与库函数追踪

> <span class="kg-badge kg-badge--tools">工具集</span>
> syscall 跟踪 · IO 调试 · 性能瓶颈定位

strace 跟踪**系统调用**，ltrace 跟踪**库函数调用**。它们是 IO / FS 调试的"核武器"——能看到程序究竟做了什么 syscall，性能瓶颈在哪。

## 1. strace 基础

```bash
# 跟踪新进程
strace -f -e trace=openat,read,write ls /tmp

# 跟踪已有进程
strace -p <PID>

# 看调用次数与耗时
strace -c -p <PID>
strace -c ls /tmp
```

输出示例：

```text
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY) = 3
read(3, "\177ELF...", 832)            = 832
write(1, "hello\n", 6)                = 6
```

## 2. 关键选项

| 选项 | 含义 |
|------|------|
| `-p` | attach 到已存在 PID |
| `-f` | 跟踪子进程 |
| `-e trace=` | 指定 syscall 名（openat, read, write, close, fsync...） |
| `-e trace=file` | 所有与文件相关的 syscall |
| `-e trace=network` | 网络相关 |
| `-o file` | 输出到文件 |
| `-c` | 计数 / 时间统计 |
| `-T` | 显示每个 syscall 耗时 |
| `-tt` | 微秒级时间戳 |
| `-y` | 显示文件描述符对应的文件名 |
| `-y` | 文件描述符 → 文件名 |
| `-k` | 输出调用栈 |

## 3. 实战：看应用读哪些文件

```bash
strace -f -e openat -p <PID>
# openat(AT_FDCWD, "/var/lib/app/db.sqlite", O_RDONLY) = 5
```

## 4. 实战：看磁盘 IO 模式

```bash
# 看 read / write 系统调用
strace -e trace=read,write,pread64,pwrite64 -T -p <PID>

# 输出：
# read(3, "....", 4096)              = 4096 <0.000123>
# pwrite64(4, "...", 4096, 0)        = 4096 <0.000456>
```

`-T` 显示每次调用的耗时，定位慢操作。

## 5. 实战：性能瓶颈分析

```bash
# 1. 采样 10 秒
strace -c -p <PID> 2>&1 | head -50

# 看：
# % time     seconds  usecs/call     calls    errors syscall
# 73.21     0.012345      1234         10           write
# 14.52     0.002456       245         10           read
```

就知道哪个 syscall 最耗时。

## 6. 实战：追查错误

```bash
# 看 ENOENT / EACCES
strace -e trace=openat -e signal=none -p <PID>

# 输出：
# openat(AT_FDCWD, "/etc/my.conf", O_RDONLY) = -1 ENOENT
```

## 7. ltrace 库函数

```bash
ltrace -e printf,fopen,fread ./myapp
```

```text
fopen("config.json", "r")              = 0x55aabbcc
fread(buf, 1, 4096, 0x55aabbcc)        = 1024
printf("loaded %d bytes\n", 1024)      = 18
```

适合诊断"应用层 IO 模式"。

## 8. perf + strace 综合

```bash
# 同时看 syscall 和栈
perf trace -p <PID>

# IO 性能
perf stat -e syscalls:sys_enter_read,syscalls:sys_enter_write -p <PID> sleep 10
```

## 9. 实战：容器场景

```bash
# 跟踪容器内进程（从主机）
PID=$(docker inspect -f '{{.State.Pid}}' my-container)
strace -f -e trace=openat -p $PID

# 容器内没 strace → nsenter 进容器
nsenter -t $PID -m -p strace -p 1
```

## 10. 常用 syscall（FS 相关）

| Syscall | 含义 |
|---------|------|
| open / openat | 打开文件 |
| read / write | 读写 |
| pread / pwrite | 偏移读写 |
| close | 关闭 |
| fsync / fdatasync | 刷盘 |
| stat / lstat / fstat | 取元数据 |
| mkdir / rmdir | 创建/删目录 |
| rename | 重命名 |
| unlink | 删除文件 |
| link | 硬链接 |
| symlink / readlink | 软链接 |
| chmod / chown | 改权限 |
| mmap | 内存映射 |
| sendfile | 零拷贝传输 |
| splice | 内核缓冲区管道 |
| getdents | 读目录项 |
| io_uring_enter | io_uring 提交 |

## 11. 性能小贴士

```bash
# 1. -c 模式看汇总
strace -c -p <PID>

# 2. -T + -tt 看每次耗时与时间
strace -T -tt -p <PID>

# 3. -k 看调用栈（要带 -f 才有用）
strace -k -f -e read,write ./myapp

# 4. -ff -o 把每个进程输出到独立文件
strace -ff -o /tmp/trace -p <PID>
```

## 12. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| strace = syscall 跟踪 | "strace=syscall" |
| ltrace = 库函数 | "ltrace=lib" |
| -e trace=file 看 IO | "-e file=IO" |
| -c 看耗时统计 | "-c=汇总" |
| -T 看每次耗时 | "-T=耗时" |

## 参考

- strace 官方文档
- ltrace 手册
- Brendan Gregg 性能分析（perf / strace 组合）