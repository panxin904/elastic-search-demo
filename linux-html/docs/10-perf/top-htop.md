---
title: top / htop
---

# top / htop - 性能排查第一步

> 看 CPU / 内存 / 负载。Linux 性能排查的起点。

## 📊 top 基础

```bash
top                        # 默认 3 秒刷新
top -d 1                   # 1 秒刷新
top -n 1 -b                # 批模式（适合脚本）
top -p <pid>               # 只看某进程
top -u alice               # 只看 alice
top -o %CPU                # 按 CPU 排序
top -o %MEM                # 按内存排序
```

### 关键区域解读

```
top - 10:23:45 up 30 days,  2 users,  load average: 0.52, 0.48, 0.45
Tasks: 234 total,   2 running, 232 sleeping
%Cpu(s): 12.3 us,  3.4 sy,  0.0 ni, 84.3 id,  0.0 wa,  0.0 hi,  0.0 si,  0.0 hi
MiB Mem :  16000 total,   8234 free,   5432 used,   2334 buff/cache
MiB Swap:   2048 total,    2048 free,      0 used.   10567 avail Mem

  PID USER      PR  NI    VIRT    RES   SHR  %CPU  %MEM     TIME+ COMMAND
 1234 alice     20   0 1234567 234567 12345   5.0   1.4   12:34.56 node app.js
```

#### 第一行：系统运行时间

```
load average: 1min, 5min, 15min
```

- 单核 CPU：load < 1 健康，> 1 有任务排队
- N 核 CPU：load < N 健康
- > 5min 持续高 = 真实瓶颈
- load 高但 CPU idle 高 → IO 瓶颈

#### 第二行：任务

```
total, running, sleeping, stopped, zombie
```

- `zombie` > 0 → 父进程没 wait 子进程（杀父进程）

#### 第三行：CPU

| 字段 | 含义 |
|------|------|
| `us` | user（用户态） |
| `sy` | system（内核态） |
| `ni` | nice（低优先级） |
| `id` | idle（空闲） |
| `wa` | wait（IO 等待） ⚠️ |
| `hi` | hardware interrupt |
| `si` | software interrupt |
| `st` | steal（虚拟化偷走） |

排查信号：
- `us` 高 → 应用层 CPU 密集
- `sy` 高 → 内核态瓶颈（IO / 锁）
- `wa` 高 → IO 等待（磁盘 / 网络）
- `st` 高 → 虚拟机被抢占

#### 第四行：内存

| 列 | 含义 |
|----|------|
| total | 总物理内存 |
| free | 完全空闲 |
| used | 已用（不含 buff/cache） |
| buff/cache | 文件缓存（可回收） |

`available` = free + 可回收 buff/cache，是"实际可用内存"。

#### 第五行：swap

`used` > 0 → 内存压力到 swap 层面了。

### 进程列

```
PID   USER  PR  NI  VIRT  RES   SHR  S  %CPU  %MEM  TIME+  COMMAND
1234  alice 20  0  1.2g 234m  12m   R  5.0  1.4   12:34  node
```

| 列 | 含义 |
|----|------|
| PID | 进程 ID |
| VIRT | 虚拟内存（含共享） |
| RES | 常驻物理内存 |
| SHR | 共享内存 |
| S | 状态（R / S / D / Z） |
| %CPU | CPU 使用率（多核可 > 100%） |
| %MEM | 物理内存百分比 |
| TIME+ | 累计 CPU 时间 |

## ⌨️ top 交互命令

| 键 | 作用 |
|----|------|
| `1` | 显示每个 CPU 核心 |
| `m` | 切换内存显示 |
| `t` | 切换 CPU / task 显示 |
| `P` | 按 CPU 排序 |
| `M` | 按内存排序 |
| `c` | 切换命令完整 / 仅命令名 |
| `V` | 树形视图（线程） |
| `H` | 切到线程模式 |
| `k` | 输入 PID + 信号杀进程 |
| `r` | renice |
| `q` | 退出 |
| `W` | 写配置到 ~/.toprc |

## 🌳 htop - top 的升级版

```bash
sudo apt install htop        # Debian/Ubuntu
sudo yum install htop        # RHEL/CentOS
brew install htop            # macOS

htop
```

### htop 交互

| 键 | 作用 |
|----|------|
| `↑ ↓` | 选进程 |
| `Space` | 标记 |
| `F2 / <` | 设置 |
| `F3 / >` | 搜索 |
| `F4 / \` | 过滤 |
| `F5 / t` | 树形视图 |
| `F6 / ]` | 排序 |
| `F7` | nice - |
| `F8` | nice + |
| `F9 / k` | 杀（可选信号） |
| `u` | 按用户过滤 |
| `H` | 显示线程 |
| `p` | 跟踪进程 |

### 树形视图（F5）

```
systemd─┬─nginx─┬─worker 1
        │       ├─worker 2
        │       └─worker 3
        ├─node─┬─app.js
        │      └─helper.js
        └─sshd
```

排查进程父子关系很有用（看哪个父进程在 fork）。

## 📊 实战

```bash
# 1. 哪个进程吃 CPU
top -o %CPU | head -20

# 2. 内存占用 top
top -o %MEM | head -20

# 3. 哪个进程被卡在 IO（D 状态）
top -o %CPU     # 看 S 列 = D 的

# 4. 持续看一段时间（5 秒 1 次）
watch -n 5 'ps aux --sort=-%cpu | head'

# 5. 找特定 PID
top -p 1234,5678

# 6. 输出到文件（监控一段时间后分析）
top -n 30 -b > /tmp/top.log
```

## 🆚 top vs htop

| | top | htop |
|--|-----|------|
| 自带 | ✅ | ❌ |
| 界面 | 文本 | 彩色 + 鼠标 |
| 树形 | ❌ | ✅ |
| 易用 | 数字密集 | 一目了然 |
| 远程 | 可用 | 可用（无鼠标时） |
| 过滤 / 搜索 | 弱 | 强 |

**推荐 htop** 装上用。top 适合脚本批处理。

## 🔗 下一步

- [vmstat / mpstat](/10-perf/vmstat)
- [iostat / iotop](/10-perf/iostat)
- [perf / strace](/10-perf/perf-strace)