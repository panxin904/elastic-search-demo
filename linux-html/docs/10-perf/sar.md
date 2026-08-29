---
title: sar 持续监控
date: 2026-08-15  # date-auto-injected
---

# sar - 系统活动采样

> 长期采样 + 历史回看。系统出问题后回头看"昨天到底怎么了"。

## 📦 sysstat 安装与启用

```bash
sudo apt install sysstat

# 启用数据采集
sudo sed -i 's/ENABLED="false"/ENABLED="true"/' /etc/default/sysstat
sudo systemctl enable --now sysstat
sudo systemctl restart sysstat

# 数据保留在
ls /var/log/sysstat/
# sa01, sa02, ...   每日文件
```

## 📜 高频命令

```bash
# CPU 使用率（默认 1 次）
sar

# 持续 1 秒 × 10 次
sar 1 10

# 看昨天的 CPU（sa01 文件）
sar -f /var/log/sysstat/sa01

# 看特定时间
sar -s 14:00:00 -e 15:00:00

# 看 CPU（all / 单独核）
sar -u                  # 总览
sar -u -P ALL           # 每个核心
sar -P 1                # 仅 CPU 1

# 内存
sar -r
sar -S                  # swap 使用
sar -H                  # 大页（hugepages）

# IO / 块设备
sar -b                  # IO 速率
sar -d                  # 每块设备
sar -d -p sda            # 单盘 + 分区

# 网络
sar -n DEV              # 网卡速率
sar -n TCP               # TCP 指标
sar -n EDEV             # 错误

# 全部
sar -A
```

## 📊 关键输出字段

### CPU（sar -u）

```
Linux 5.15.0 (host)  _x86_64_

10:00:01  CPU  %user  %nice  %system  %iowait  %steal  %idle
10:00:02  all   12.3   0.0     3.4       0.5     0.0    84.3
10:00:03  all   15.1   0.0     4.0       1.0     0.0    80.0
```

| 列 | 含义 |
|----|------|
| `%user` | 用户态 |
| `%system` | 内核态 |
| `%iowait` | 等 IO |
| `%steal` | 虚拟机偷走 |
| `%idle` | 空闲 |

### 内存（sar -r）

```
10:00:01 kbmemfree kbmemused %memused kbbuffers kbcached kbcommit %commit
10:00:02   1234567  12345678   90.0    123456  2345678  8765432    80.0
```

| 列 | 含义 |
|----|------|
| `kbmemfree` / `kbmemused` | 空闲 / 已用 |
| `%memused` | 内存使用百分比 |
| `kbcached` | 页缓存（可回收） |
| `kbcommit` | 已申请总内存（含 swap） |
| `%commit` | commit 占总内存百分比 |

### 块设备（sar -d）

```
10:00:01  DEV  tps  rd_sec/s  wr_sec/s  avgrq-sz  avgqu-sz  await  svctm  %util
10:00:02  sda  5.0    20.0     30.0      8.0      0.10     4.0    2.0    8.0
```

类似 iostat。

### 网络（sar -n DEV）

```
10:00:01  IFACE  rxpck/s  txpck/s  rxkB/s  txkB/s  rxcmp/s  txcmp/s  rxmcst/s
10:00:02  eth0   100.0   200.0    50.0    100.0    0.0      0.0      1.0
```

## 📅 报告模式（过去的数据）

```bash
# 看今天的 CPU
sar -u
# 看某天
sar -u -f /var/log/sysstat/sa15

# 看 CPU 内存 综合
sar -u -r -n DEV

# 导出 CSV（Excel / Grafana）
sar -u -f /var/log/sysstat/sa15 -o > /tmp/sar.csv

# 或直接转 txt
sadf /var/log/sysstat/sa15 -- -u
```

## 🔧 实时监控

```bash
# 每秒 1 次 × 60 = 1 分钟平均
sar 1 60 > /tmp/sar.log
# 头尾看看
head -3 /tmp/sar.log
tail -3 /tmp/sar.log
```

## 🗂️ 历史数据管理

```bash
# 配置文件
cat /etc/cron.d/sysstat

# 历史保留（/etc/sysstat/sysstat）
HISTORY=28          # 保留 28 天
SADC_OPTIONS="-S ALL"

# 修改保留时间
sudo vim /etc/sysstat/sysstat
sudo systemctl restart sysstat
```

## 🛠 实战：事故后回看

```bash
# 凌晨 3 点收到报警，6 点排查

# 1. 看 3 点的 CPU
sar -u -s 03:00:00 -e 03:10:00

# 2. 看 3 点的内存
sar -r -s 03:00:00 -e 03:10:00

# 3. 看 IO
sar -d -s 03:00:00 -e 03:10:00

# 4. 看网络
sar -n DEV -s 03:00:00 -e 03:10:00
```

## 📈 与其他工具关系

| 工具 | 何时 |
|------|------|
| `top / htop` | 实时看某个进程 |
| `vmstat` | 整体观察（短时） |
| `iostat / iotop` | 磁盘 IO 深入 |
| `sar` | **历史回看**（关键） |
| `dstat` | 综合（已不维护） |

## 🔗 下一步

- [top / htop](/10-perf/top-htop)
- [vmstat / mpstat](/10-perf/vmstat)
- [iostat / iotop](/10-perf/iostat)
- [perf / strace](/10-perf/perf-strace)