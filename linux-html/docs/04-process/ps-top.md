---
title: ps / top / htop
date: 2026-08-15  # date-auto-injected
---

# ps / top / htop
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Linux 进程生命周期</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">创建 → 就绪 → 运行 → 阻塞 → 终止 · task_struct 描述</text>

  <!-- 5 态转换 -->
  <g>
    <text x="50" y="90" font-size="13" font-weight="700" fill="#1e293b">① Linux 进程 5 大状态</text>

    <rect class="at-hover-card" x="40" y="105" width="105" height="65" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="92" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">R Running</text>
    <text x="92" y="146" text-anchor="middle" font-size="9" fill="#475569">运行中</text>
    <text x="92" y="160" text-anchor="middle" font-size="9" fill="#3b82f6">占用 CPU</text>

    <rect class="at-hover-card" x="170" y="105" width="105" height="65" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="222" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">S Sleeping</text>
    <text x="222" y="146" text-anchor="middle" font-size="9" fill="#475569">可中断睡眠</text>
    <text x="222" y="160" text-anchor="middle" font-size="9" fill="#10b981">等待事件</text>

    <rect class="at-hover-card" x="300" y="105" width="105" height="65" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="352" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">D Disk Sleep</text>
    <text x="352" y="146" text-anchor="middle" font-size="9" fill="#475569">不可中断</text>
    <text x="352" y="160" text-anchor="middle" font-size="9" fill="#f59e0b">等待 IO</text>

    <rect class="at-hover-card" x="430" y="105" width="130" height="65" rx="6" fill="#e9d5ff" stroke="#8b5cf6" stroke-width="1.5"/>
    <text x="495" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#5b21b6">T/Z Stopped/Zombie</text>
    <text x="495" y="146" text-anchor="middle" font-size="9" fill="#475569">停止/僵尸</text>
    <text x="495" y="160" text-anchor="middle" font-size="9" fill="#8b5cf6">信号控制</text>

    <rect class="at-hover-card" x="40" y="195" width="105" height="65" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
    <text x="92" y="218" text-anchor="middle" font-size="11" font-weight="700" fill="#991b1b">X Dead</text>
    <text x="92" y="236" text-anchor="middle" font-size="9" fill="#475569">死亡</text>
    <text x="92" y="250" text-anchor="middle" font-size="9" fill="#dc2626">资源回收</text>

    <rect class="at-hover-card" x="170" y="195" width="105" height="65" rx="6" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
    <text x="222" y="218" text-anchor="middle" font-size="11" font-weight="700" fill="#475569">I Idle</text>
    <text x="222" y="236" text-anchor="middle" font-size="9" fill="#475569">空闲内核线程</text>

    <rect class="at-hover-card" x="300" y="195" width="260" height="65" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="430" y="218" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">ps STAT 列含义</text>
    <text x="315" y="236" font-size="9" fill="#475569">R 运行 / S 可中断 / D 不可中断</text>
    <text x="315" y="250" font-size="9" fill="#475569">T 停止 / Z 僵尸 / X 死亡 / I 空闲</text>
  </g>

  <!-- task_struct -->
  <g>
    <text x="50" y="285" font-size="13" font-weight="700" fill="#1e293b">② task_struct 关键字段（进程描述符）</text>

    <rect class="at-hover-card" x="40" y="295" width="520" height="50" rx="6" fill="#1e293b" stroke="#1e293b" stroke-width="1"/>
    <text x="55" y="318" font-size="11" font-weight="700" fill="#10b981">struct task_struct {</text>
    <text x="75" y="335" font-size="10" fill="#e2e8f0" font-family="monospace">pid · state · mm (内存) · files (fd表) · signal · cred · sched_entity</text>

    <path d="M300,345 L300,365" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="40" y="365" width="520" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="55" y="388" font-size="10" font-weight="700" fill="#1e40af">🧠 mm_struct</text>
    <text x="135" y="388" font-size="9" fill="#475569">虚拟地址空间 → 页表</text>
    <text x="315" y="388" font-size="10" font-weight="700" fill="#1e40af">📁 files_struct</text>
    <text x="425" y="388" font-size="9" fill="#475569">fd 数组 → file*</text>
    <text x="55" y="405" font-size="10" font-weight="700" fill="#1e40af">🔐 cred</text>
    <text x="115" y="405" font-size="9" fill="#475569">uid/gid</text>
    <text x="200" y="405" font-size="10" font-weight="700" fill="#1e40af">📊 sched_entity</text>
    <text x="320" y="405" font-size="9" fill="#475569">CFS 调度实体</text>
  </g>

  <!-- 进程创建 -->
  <g>
    <text x="50" y="435" font-size="13" font-weight="700" fill="#1e293b">③ 进程创建（fork/exec/wait）</text>

    <rect class="at-hover-card" x="40" y="445" width="510" height="20" rx="4" fill="#dcfce7" stroke="#10b981"/>
    <text x="300" y="459" text-anchor="middle" font-size="10" font-weight="700" fill="#047857">fork() 复制 task_struct · exec() 替换代码 · wait() 回收僵尸</text>
  </g>
</svg>


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

<ClientOnly>
  <GiscusComment />
</ClientOnly>

<!-- giscus-injected:do-not-edit -->
