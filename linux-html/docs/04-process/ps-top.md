---
title: ps / top / htop
date: 2026-08-15  # date-auto-injected
---

# ps / top / htop

> 看进程是 Linux 排查第一步。

## 📜 ps - 进程快照

```bash
ps                         # 当前 shell 启动的进程
ps -e                       # 系统中所有进程
ps -ef                      # 完整列表
ps aux                      # BSD 风格，更详细
ps -ef | grep nginx         # 找 nginx 进程
ps -ef --forest             # 树形结构
ps -u alice                 # alice 的进程
ps -L -p <pid>              # 该进程的所有线程

# 按资源排序
ps aux --sort=-%cpu         # CPU 占用降序
ps aux --sort=-%mem         # 内存占用降序
ps aux --sort=-rss          # RSS 降序

# 自定义输出列
ps -eo pid,ppid,user,%cpu,%mem,cmd --sort=-%cpu | head
```

### ps aux 输出字段

```
USER  PID  %CPU %MEM  VSZ    RSS   TTY  STAT  START  TIME  COMMAND
alice 1234  5.0  1.2 123456 12345 pts/0  S    10:00  0:01  node app.js
│     │    │    │    │      │     │     │    │      │      │
│     │    │    │    │      │     │     │    │      │      └─ 命令
│     │    │    │    │      │     │     │    │      └─ CPU 时间
│     │    │    │    │      │     │     │    └─ 启动时间
│     │    │    │    │      │     │     └─ 状态 (S/R/Z/D/T)
│     │    │    │    │      │     └─ 终端
│     │    │    │    │      └─ RSS（实际内存）
│     │    │    │    └─ VSZ（虚拟内存）
│     │    │    └─ 内存 %
│     │    └─ CPU %
│     └─ PID
└─ 用户
```

### 进程状态

| 状态 | 含义 |
|------|------|
| `R` | Running |
| `S` | Sleeping（可中断） |
| `D` | Uninterruptible sleep（不可中断，通常 IO） |
| `Z` | Zombie（已死未收尸） |
| `T` | Stopped |
| `I` | Idle kernel thread |

## 📈 top - 实时

```bash
top                          # 默认 3 秒刷新
top -p <pid>                 # 只看某 PID
top -u alice                 # 只看 alice
top -b -n 1                  # 批处理模式（适合脚本）

# 交互命令（top 内）
1                            # 看每个 CPU 核心
m                            # 切换内存显示
t                            # 切换 CPU 显示
P                            # 按 CPU 排序
M                            # 按内存排序
c                            # 切换命令显示（完整 / 仅命令名）
z                            # 切换颜色
k                            # kill 一个进程（输入 PID）
r                            # renice
```

## 🌳 htop - top 的升级版

```bash
# 安装
sudo apt install htop        # Debian/Ubuntu
sudo yum install htop        # RHEL/CentOS

# 使用
htop                         # 直接启动
htop -d 5                     # 5 秒刷新
htop -u alice                # 只看 alice

# 交互
↑ ↓                         # 选进程
F2 / <                       # 设置
F3 / >                       # 搜索
F4 / \                       # 过滤
F5 / t                       # 树形
F6 / ]                       # 排序
F7 / F8                      # nice - / nice +
F9 / k                       # 杀进程（选信号）
Space                        # tag
u                            # 按用户过滤
```

## 🆚 ps vs top vs htop

| | ps | top | htop |
|--|-----|------|------|
| 形态 | 一次性快照 | 实时交互 | 实时交互 + 彩色 |
| 易用 | 脚本友好 | 数字密集 | 鼠标支持 + 树形 |
| 功能 | 看历史 | 看实时 | 看实时 + tree |

## 🔧 实战

```bash
# 找僵尸进程
ps -eo stat,ppid,pid,cmd | grep -w Z

# 看某进程打开的文件
lsof -p <pid>
ls -la /proc/<pid>/fd/

# 看进程的工作目录
ls -l /proc/<pid>/cwd

# 看进程的启动命令
cat /proc/<pid>/cmdline | tr '\0' ' '

# 看进程的环境变量
cat /proc/<pid>/environ | tr '\0' '\n'

# 看进程占用的端口
ss -tulnp | grep <pid>
```

## 🎯 load average

```
top 输出右上角: load average: 1.20, 0.85, 0.40
              /  \   /  \  /  \
             1min  5min  15min
```

- 单核 CPU：load < 1 健康，> 1 有任务排队
- N 核 CPU：load < N 健康
- > 5min 持续高 = 真实瓶颈
- IO 密集型 load 可能偏高但 CPU 使用率不高

## 🔗 下一步

- [信号 (kill)](/04-process/signals)
- [systemd](/04-process/systemd)
- [iostat / iotop](/10-perf/iostat)