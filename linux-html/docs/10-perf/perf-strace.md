---
title: perf / strace
---

# perf / strace - 深入内核追踪

> 性能剖析（perf）+ 系统调用跟踪（strace）。**深入**层工具。

## 📜 strace - 系统调用跟踪

```bash
# 基本
strace cmd                       # 跑 cmd 并打印所有 syscall
strace -p <pid>                  # attach 到运行中的进程
strace -e openat cmd             # 只看 openat 调用
strace -e trace=network cmd      # 只看网络相关
strace -c cmd                    # 汇总统计

# 输出到文件
strace -o /tmp/strace.log cmd
strace -e openat -o /tmp/log cmd

# 时间戳
strace -t cmd                    # 加时间（秒）
strace -tt cmd                   # 毫秒
strace -ttt cmd                  # 毫秒 + 相对

# 看子进程
strace -f cmd                    # 跟随 fork
```

### 输出解读

```
openat(AT_FDCWD, "/etc/passwd", O_RDONLY) = 3
fstat(3, {st_mode=S_IFREG|0644, st_size=2845, ...}) = 0
read(3, "root:x:0:0:root:/root:/bin/bash\n...", 4096) = 2845
close(3) = 0
```

格式：`syscall名(参数...) = 返回值`

### 实战

```bash
# 1. 配置文件没读？追 open
strace -e openat -f cmd 2>&1 | grep my.conf

# 2. 网络不通？追 connect / sendto
strace -e trace=network -f cmd 2>&1 | grep -E 'connect|sendto'

# 3. 性能：哪个 syscall 慢
strace -c -e openat,read,write cmd
# % time  seconds  usecs/call  calls  errors  syscall
# 80.0   0.40     200          2     0       openat
# 20.0   0.10     100          1     0       read

# 4. 启动卡在哪
strace -f -e openat cmd 2>&1 | head
# 第一个 open 就是它卡的文件

# 5. 权限问题
strace -e openat cmd 2>&1 | grep EACCES
```

### 常用 syscall 过滤

```bash
strace -e trace=file     # 文件相关：openat, read, write, close, stat
strace -e trace=network  # 网络：socket, bind, listen, connect, accept, send, recv
strace -e trace=process  # 进程：fork, execve, clone, exit
strace -e trace=signal   # 信号
strace -e trace=ipc      # 进程通信：pipe, shmget
strace -e trace=desc     # fd 操作
```

## 📊 perf - 性能剖析

```bash
# 装 perf
sudo apt install linux-tools-common linux-tools-$(uname -r)
```

### perf stat - 综合统计

```bash
perf stat cmd
#  Performance counter stats for 'cmd':
#
#  1,234.56 msec task-clock                # CPU 时间
#       3,456  context-switches             # 上下文切换
#         123  cpu-migrations               # 进程迁移到其他 CPU
#           4  page-faults                   # 缺页
#   2,345,678  cycles                       # CPU 周期
#   1,234,567  instructions                  # 指令数
#     3.45    GHz
#
#  0.5 seconds time elapsed
```

| 字段 | 含义 |
|------|------|
| `task-clock` | 实际使用 CPU 时间 |
| `context-switches` | 上下文切换（多 = 线程/进程切换频繁） |
| `cpu-migrations` | 进程在不同 CPU 间迁移 |
| `page-faults` | 缺页中断（major = 真 IO，minor = 缓存未命中） |
| `cycles` / `instructions` | CPU 周期 / 指令数 |

### perf record + report

```bash
# 采样（默认 99Hz，记录到 perf.data）
perf record cmd
perf report                    # 交互式查看（按 % 排序函数）

# 看热点函数
perf top                        # 实时 top

# 指定进程
perf record -p <pid> -g         # -g 看调用栈
perf report -g                  # 展示 call graph

# 录 60 秒
perf record -F 99 -a cmd &     # 99Hz，采集所有 CPU
sleep 60
kill %1
perf report
```

### perf 火焰图

```bash
# 生成 FlameGraph（需要 git clone FlameGraph）
git clone https://github.com/brendangregg/FlameGraph.git

perf script | ./FlameGraph/stackcollapse-perf.pl | ./FlameGraph/flamegraph.pl > flame.svg
firefox flame.svg
```

直观看到"哪个函数占 CPU 多"。

### perf 高级

```bash
# 看 cache miss
perf stat -e cache-misses,cache-references cmd

# 看分支预测错误
perf stat -e branch-misses,branch-instructions cmd

# 看页错误
perf stat -e page-faults,minor-faults,major-faults cmd

# 看调度延迟
perf stat -e 'sched:sched_stat_runtime,sched:sched_switch' cmd

# 看具体函数（热点）
perf record -e cycles:u -F 99 cmd
perf report --sort=comm,dso,symbol
```

### perf trace（追踪）

```bash
perf trace cmd                # 类似 strace，但用 perf 框架
perf trace -e syscalls:sys_enter_openat cmd
perf trace -p <pid>           # attach

# 火焰图 + 调度
perf trace -e 'sched:sched_switch' -a -s 100
```

## 🔧 实战

### 1. 应用 CPU 高，但不知道是哪里

```bash
# 采样 10 秒
perf record -F 99 -p <pid> -g -- sleep 10
perf report -g

# 或直接 top
perf top -p <pid>
```

### 2. 系统调用慢（IO 慢 / 网络慢）

```bash
strace -c -p <pid>
# % time  seconds  usecs/call  calls  syscall
# 80.00    0.40     200           2     recvfrom  ← 网络读卡
```

### 3. 启动卡在哪

```bash
strace -f -e openat cmd 2>&1 | grep -v ENOENT
# 看卡在哪个文件
```

### 4. 找内存泄漏

```bash
# 简化版：smaps
cat /proc/<pid>/smaps | grep -i 'rss\|swap' | head

# 高级：valgrind / heaptrack
sudo apt install heaptrack
heaptrack cmd
# 输出内存分配调用栈
```

### 5. 系统调用 profile

```bash
perf record -e 'syscalls:sys_enter_*' cmd
perf report
```

## ⚙️ 工具对比

| | strace | perf |
|--|-------|-----|
| 维度 | 系统调用（用户态 ↔ 内核） | CPU 周期 / cache / branch |
| 开销 | 较大（每次 syscall 都截获） | 较小（采样） |
| 适合 | 看 IO / 文件 / 网络 / 进程操作 | 看 CPU 热点 / 性能瓶颈 |
| 实时 | yes | yes |
| 历史回看 | ❌ | ❌ |
| 安全 | 任何用户（自己进程） | 通常需 root |

## 🔧 调试小技巧

```bash
# 在生产安全用 strace
strace -f -e trace=openat -o /tmp/strace.log -p <pid> &
sleep 5
kill %1
# 看 PID 打开的所有文件

# perf 安全采样（无侵入）
perf record -F 99 -p <pid> -o /tmp/perf.data &
sleep 10
kill %1
perf report -i /tmp/perf.data
```

## ⚠️ 注意

- strace 会显著降低程序性能（拦截每个 syscall）
- 生产环境短时使用，别长时间跑
- perf 也类似，但采样模式开销小
- 需要 root 看其他用户的进程

## 🔗 下一步

- [top / htop](/10-perf/top-htop)
- [iostat / iotop](/10-perf/iostat)
- [vmstat / mpstat](/10-perf/vmstat)