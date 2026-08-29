---
title: iostat / iotop
date: 2026-08-15  # date-auto-injected
---

# iostat / iotop - 磁盘 IO 排查

> 找到"磁盘慢"的真凶。

## 📊 iostat - 设备级 IO 统计

```bash
sudo apt install sysstat
iostat                       # 默认快照
iostat -x                    # 扩展（最重要的输出）
iostat -x 1 5                # 每 1 秒 × 5 次
iostat -d /dev/sda 1 5       # 单盘监控
iostat -p /dev/sda 1 5       # 看分区
```

### 输出解读

```
Linux 5.15.0-...  _x86_64_

Device  r/s     w/s   rkB/s    wkB/s  rrqm/s  wrqm/s  %rrqm  %wrqm  r_await  w_await  aqu-sz  rareq-sz  wareq-sz  svctm  %util
sda     1.20    3.40  12.80    45.20    0.00    1.00    0.0%   22.7%    0.50     1.20     0.05     10.7      13.3   0.40   4.40
```

| 列 | 含义 |
|----|------|
| `r/s` `w/s` | 每秒读 / 写次数（IOPS） |
| `rkB/s` `wkB/s` | 每秒读 / 写 字节（吞吐） |
| `rrqm/s` `wrqm/s` | 每秒合并的请求（队列合并） |
| `r_await` `w_await` | 单个 IO 平均等待（ms） |
| `aqu-sz` | 平均队列长度 |
| `rareq-sz` `wareq-sz` | 平均 IO 大小（KB） |
| `%util` | 设备繁忙比（接近 100% = 满） |

### ⚠️ %util 的误解

`%util` 只表示"设备至少有一个 IO 在进行的时间百分比"。

- 现代设备（NVMe）并行度高：`%util=100%` 不一定饱和
- 真正看 IO 能力：看 `aqu-sz`（队列）和 `await`（延迟）
- SSD / NVMe 重点看：IOPS 和延迟（`await`）

```bash
# NVMe 满载指标
iostat -x 1 3
# r/s + w/s = 设备 IOPS 上限
# await > 1ms（机械盘）/> 0.1ms（SSD） = 有问题
```

## 🚀 iotop - 进程级 IO

```bash
sudo apt install iotop
sudo iotop                    # 实时（类似 top）
sudo iotop -ao                # 仅显示有 IO 的进程
sudo iotop -b -n 3            # 批模式 ×3
sudo iotop -P                 # 仅显示进程（不显示线程）
```

### 输出

```
Total DISK READ:       0.00 B/s | Total DISK WRITE:    15.34 K/s
Actual DISK READ:      0.00 B/s | Actual DISK WRITE:    12.45 K/s

  PID  PRIO  USER     DISK READ  DISK WRITE  SWAPIN      IO    COMMAND
 1234 be/4 alice        0.00 B/s     3.45 K/s  0.00 %  0.05 %  node app.js
 5678 be/4 root         0.00 B/s    12.34 K/s  0.00 %  0.12 %  python3 backup.py
```

- `DISK READ / WRITE`：当前 IO 速率
- `SWAPIN / IO`：占用 IO / swap 比例
- 用 O_DIRECT 绕过 cache 的进程：`Actual` 和 `DISK` 数字不同

## 📊 实战排查

### 场景 1：数据库慢

```bash
iostat -x 1 5
# 看：
# - %util 是否 100%（NVMe 看 await）
# - await 是否高（> 1ms 机械盘 / > 0.1ms SSD）
# - aqu-sz 队列

# 看谁在大量 IO
sudo iotop -ao
```

### 场景 2：日志写入慢

```bash
iostat -x -d /dev/sda 1 5
# 看 wkB/s（写吞吐）
# wkB/s 接近设备上限（机械盘 ~200MB/s，SSD ~500MB/s，NVMe 1-3GB/s）→ 瓶颈
```

### 场景 3：磁盘慢 + CPU 高

```bash
# 找 IO 密集的进程
iotop -P

# 找耗时 syscall
perf trace -e syscalls:sys_enter_read, syscalls:sys_enter_write -a -s 50
```

## 🧰 进阶工具

### biolatency / iosnoop (bcc)

```bash
sudo apt install bpfcc-tools

sudo biolatency                 # 块设备延迟直方图
sudo iosnoop -d                 # 看进程级 IO 请求
sudo biolatency -Q             # 队列延迟
```

类似 Brendan Gregg 的 DTrace 工具，能看 IO 延迟分布（不止平均值）。

### perf

```bash
# 看 IO 在等什么
sudo perf trace -e block:* -a
sudo perf stat -e 'syscalls:sys_enter_read' cmd
```

详见 [perf / strace](/10-perf/perf-strace)。

## ⚙️ 调优

### I/O Scheduler

```bash
# 看当前
cat /sys/block/sda/queue/scheduler

# 改（机械盘：deadline / bfq；SSD / NVMe：none）
echo none | sudo tee /sys/block/sda/queue/scheduler

# NVMe 推荐 none（避免内核调度器干扰设备自带调度）
```

### 调 readahead

```bash
# 看
sudo blockdev --getra /dev/sda        # 通常 256 = 128KB

# 改（顺序读大文件可加大，SSD 可关）
sudo blockdev --setra 2048 /dev/sda
echo 2048 | sudo tee /sys/block/sda/queue/read_ahead_kb
```

### dirty ratio

```bash
sysctl vm.dirty_ratio          # 默认 20%
sysctl vm.dirty_background_ratio  # 默认 10%
# 数据库 / 写密集型：调低避免 IO 抖动
sudo sysctl -w vm.dirty_ratio=5
sudo sysctl -w vm.dirty_background_ratio=1
```

### I/O 调度优先级

```bash
# /etc/fstab 加 prio= 字段
/dev/sda1 /data ext4 defaults,prio=0 0 2

# 或 ionice（按进程）
ionice -c 1 -n 4 nice -n 19 backup.sh
# class 1 (realtime), class 2 (best-effort), class 3 (idle)
```

## 🩺 排查 checklist

```bash
# 1. 整盘是否满
iostat -x 1 3 | grep -E 'sda|nvme'

# 2. 谁在写
sudo iotop -ao -n 3 -d 2

# 3. 看特定进程的 IO
iotop -p <pid>

# 4. 持续监控
iostat -dx /dev/sda 5 12 > /tmp/iostat.log
# 等事故发生时回头分析

# 5. 看 log（日志系统可能在打爆 IO）
sudo lsof -p <pid> | grep -E '\.log|REG'

# 6. swap 是否在 IO 抖
vmstat 1 5  # 看 si / so
```

## 🔗 下一步

- [top / htop](/10-perf/top-htop)
- [vmstat / mpstat](/10-perf/vmstat)
- [perf / strace](/10-perf/perf-strace)