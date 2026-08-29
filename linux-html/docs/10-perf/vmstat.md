---
title: vmstat / mpstat
date: 2026-08-15  # date-auto-injected
---

# vmstat / mpstat - CPU / 内存 / IO

> 计数器式的性能工具：每秒打一行，便于看趋势。

## 📊 vmstat - 整体概况

```bash
vmstat 1                       # 每秒 1 行
vmstat 1 10                    # 1 秒间隔 × 10 次
vmstat -s                      # 一次性 summary（总和）
vmstat -d                      # 磁盘 IO
vmstat -p /dev/sda             # 单盘分区
```

### 输出解读

```
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 2  0      0 123456 12345 234567    0    0     1     5  100  150  5  3 92  0  0
```

#### procs

| 列 | 含义 | 警告 |
|----|------|------|
| `r` | 等待运行的进程数 | > CPU 核心数 → 满载 |
| `b` | 不可中断睡眠（IO） | > 0 → IO 瓶颈 |

#### memory

| 列 | 含义 |
|----|------|
| `swpd` | swap 使用 |
| `free` | 完全空闲内存 |
| `buff` | 块设备 buffer |
| `cache` | 页缓存 |

#### swap

| 列 | 含义 |
|----|------|
| `si` | swap in（从磁盘到内存） |
| `so` | swap out（从内存到磁盘） |

> 0 是好的，> 0 持续 = 内存紧张。

#### io

| 列 | 含义 |
|----|------|
| `bi` | 块设备 in（读，blocks/s） |
| `bo` | 块设备 out（写） |

> 高 = IO 瓶颈，但只是宏观，看 iostat 找具体设备。

#### system

| 列 | 含义 |
|----|------|
| `in` | 中断数 |
| `cs` | 上下文切换 |

> `cs` 极高（> 100k） → 进程切换频繁（太多进程 / 锁竞争）。

#### cpu

| 列 | 含义 |
|----|------|
| `us` | user CPU |
| `sy` | system CPU |
| `id` | idle |
| `wa` | IO wait |
| `st` | steal（虚拟化） |

> `us+sy` 高 → CPU 瓶颈；`wa` 高 → IO 瓶颈。

## 📊 实战：vmstat 排查

```bash
# 看 1 秒 5 次
vmstat 1 5
```

### 场景 1：CPU 瓶颈

```
 r  b  swpd  free  buff  cache  si  so  bi  bo  in   cs   us sy id wa st
 8  0     0  1234  1000  5000   0   0   1   5  200  5000  90 10  0  0  0
```

- `r=8` > 核心数 → CPU 满
- `us=90` → 应用层 CPU 密集
- 解决：看 top 找谁 → 调代码 / 加 CPU

### 场景 2：IO 瓶颈

```
 1  5     0  1234  1000  5000   0   0   0  200  500  800  10  5  0 85  0
```

- `b=5` 多个进程在不可中断睡眠
- `wa=85%` 大量时间等 IO
- 解决：iostat 找慢盘 / 加 SSD / 调应用 IO

### 场景 3：内存压力

```
 2  0 102400  1234  1000  5000  50 100  100 200  500 1000  10  5 80  5  0
```

- `si=50 so=100` → swap 大量进出
- 解决：加内存 / 优化内存使用 / 加 swap

### 场景 4：上下文切换过高

```
100 0   0  1234  1000  5000    0   0   1   5  1000 100000  10  5 85  0  0
```

- `cs=100000` → 太多线程 / 进程切换
- 解决：减少线程数 / 改用 IO 多路复用

## 📈 mpstat - 多核分析

```bash
sudo apt install sysstat
mpstat                       # 全部 CPU 平均
mpstat -P ALL                # 每个核心分开
mpstat -P 0 1 5               # CPU 0，每 1 秒 5 次
```

### 输出

```
Linux 5.15.0-91-generic (...)  _x86_64_
10:23:45  CPU    %usr   %nice    %sys   %iowait    %irq   %soft   %steal   %guest   %gnice   %idle
10:23:46  all    12.3   0.0      3.4    0.5         0.0    0.5     0.0      0.0      0.0      84.3
10:23:46    0    10.1   0.0      2.5    0.3         0.0    0.2     0.0      0.0      0.0      86.9
10:23:46    1    15.5   0.0      4.2    0.8         0.0    0.1     0.0      0.0      0.0      79.4
```

- 看到某 CPU 满载但其他空闲 → 单线程应用 → 多进程/线程优化

## 🆚 vmstat vs mpstat vs top

| | vmstat | mpstat | top |
|--|--------|--------|-----|
| 形式 | 单行计数 | 多列计数 | 进程表 |
| 优势 | 长时间观察 | 多核分析 | 进程级定位 |
| 时延 | 1 秒 | 1 秒 | 3 秒（默认） |
| 适合 | 趋势分析 | 单核问题 | 找具体进程 |

## 🩺 实战流程

```bash
# 1. 整体观察 5 秒
vmstat 1 5

# 2. 看 CPU 各核
mpstat -P ALL 1 3

# 3. 找占资源的进程
top -o %CPU | head

# 4. 如果 CPU 高但 wa 也高 → IO 瓶颈
iostat -x 1 3

# 5. 如果内存高 → 看 cache / swap
free -h
cat /proc/meminfo
```

## 🔗 下一步

- [top / htop](/10-perf/top-htop)
- [iostat / iotop](/10-perf/iostat)
- [sar 持续监控](/10-perf/sar)
- [perf / strace](/10-perf/perf-strace)