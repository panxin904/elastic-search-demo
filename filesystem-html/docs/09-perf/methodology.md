---
title: 性能方法论
---

# 性能调优方法论 — USE、RED、负载剖析

> <span class="kg-badge kg-badge--perf">性能调优</span>
> USE 方法 · RED 方法 · 负载剖析 · 性能思维

性能调优不是"调参数碰运气"。**有方法论**才能**系统**地找到瓶颈。本节讲业界三大方法论：

- **USE 方法**（Brendan Gregg）— 用于定位资源问题
- **RED 方法**（Tom Wilkie）— 用于微服务性能
- **负载剖析** — 找到热点

## 1. USE 方法（Utilization / Saturation / Errors）

**核心思想**：对**每一个资源**（CPU / 内存 / 磁盘 / 网络），问四个问题：

| 指标 | 含义 |
|------|------|
| **Utilization**（利用率） | 资源忙的时间比例 |
| **Saturation**（饱和度） | 资源过载排队程度 |
| **Errors**（错误数） | 错误事件计数 |

**对磁盘**：

| 指标 | 怎么查 |
|------|--------|
| Utilization | `iostat -x 1` 看 `%util` |
| Saturation | `avgqu-sz`（队列长度） |
| Errors | `dmesg` 或 `smartctl` |

**对内存**：

| 指标 | 怎么查 |
|------|--------|
| Utilization | `free -h`（used%） |
| Saturation | `psi`（Pressure Stall Information） |
| Errors | OOM killer（dmesg） |

**对 CPU**：

| 指标 | 怎么查 |
|------|--------|
| Utilization | `top` / `mpstat` |
| Saturation | run queue length |
| Errors | 系统异常 |

## 2. RED 方法（Rate / Errors / Duration）

**核心思想**：对**每一个服务**，监控三个指标：

| 指标 | 含义 |
|------|------|
| **Rate**（请求速率） | 每秒请求数 |
| **Errors**（错误率） | 失败请求的速率 / 比例 |
| **Duration**（延迟） | 每个请求耗时 |

适合 HTTP 服务、API 服务、数据库。

```yaml
# Prometheus 抓取
http_requests_total{service="api"}
http_request_duration_seconds_bucket{le="0.5"}
http_requests_total{status="500"}
```

## 3. 负载剖析（Workload Characterization）

**核心思想**：在做优化之前，**先理解负载**：

- **读 vs 写** 比例？
- **大 IO vs 小 IO** ？
- **顺序 vs 随机** ？
- **峰值 vs 平均** ？

```bash
# 看 IO 模式
iostat -x 1
# r/s, w/s, %util, await, svctm

# 看 IO 分布
fio --filename=/dev/sda --direct=1 \
    --rw=randread --bs=4k --size=1G \
    --runtime=60 --time_based
```

## 4. 经典性能分析模型

```
       OS Resources            Workload Characteristics
              │                          │
              ▼                          ▼
       ┌─────────────────────────────────────────┐
       │           软件（应用 / 中间件）           │
       └─────────────────────────────────────────┘
              │                          │
              ▼                          ▼
       Performance Issues ← → Workload Changes
```

**两种思路**：

- 自上而下：从**应用**往下找瓶颈（先看应用代码）
- 自下而上：从**资源**往上找瓶颈（先看 OS 资源）

## 5. 实战：磁盘性能分析

### 5.1 第一步：看资源利用率

```bash
# CPU
top
mpstat -P ALL 1

# 内存
free -h
cat /proc/pressure/memory

# IO
iostat -x 1
# 看 %util < 60%（还有余量）/ > 80%（紧张）

# 网络
sar -n DEV 1
```

### 5.2 第二步：看饱和度

```bash
# IO 队列
iostat -x 1 | grep sda
# avgqu-sz > 1 = 队列拥堵

# CPU runqueue
vmstat 1
# r 列（running）

# PSI（pressure stall）
cat /proc/pressure/cpu
cat /proc/pressure/io
cat /proc/pressure/memory
```

### 5.3 第三步：看错误

```bash
dmesg -T | grep -i "error\|fail"
journalctl -p err -f
smartctl -a /dev/sda
```

### 5.4 第四步：定位具体进程

```bash
# CPU
top -c

# IO
iotop -o

# 内存
ps aux --sort -rss | head

# 综合
pidstat -p <PID> 1
```

### 5.5 第五步：分析 trace

```bash
# strace 看 syscall
strace -p <PID> -c

# perf 分析热点
perf top -p <PID>

# bpftrace 高级分析
bpftrace -e 'kprobe:blk_mq_start_request { @start[tid] = nsecs; }
             kretprobe:blk_mq_start_request /@start[tid]/ {
                 @latency_us = hist((nsecs - @start[tid])/1000);
                 delete(@start[tid]);
             }'
```

## 6. 调优思路（先识别后优化）

**层次模型**：

```
应用层 (App)
   ↑↓ 调
JVM / Runtime
   ↑↓ 调
OS 内核 (FS / Scheduler / Network)
   ↑↓ 调
硬件 (CPU / 内存 / 磁盘 / 网卡)
```

**从下往上**：

1. 先确认**硬件资源**够不够（CPU 不够加 CPU，磁盘慢换 SSD）
2. 再调 **OS 内核**（调度器、Page Cache、readahead）
3. 再调 **应用配置**（数据库 buffer pool、连接池）
4. 最后调 **应用代码**（索引、SQL、算法）

## 7. 调优的反模式

| 反模式 | 后果 |
|--------|------|
| 改参数碰运气 | 治标不治本 |
| 一次改多个 | 出问题不知哪个害的 |
| 不测基准就调 | 不可重复 |
| 线上调参 | 影响用户 |
| 没数据就判断 | 主观错误 |

## 8. 调优的标准流程

```text
1. 设定目标
   "希望把 IO 延迟从 50ms 降到 10ms"
2. 测基准（基准线）
   fio / sysbench / wrk / ab
3. 测现状（找瓶颈）
   USE / RED / 负载剖析
4. 改一个变量
5. 重测
6. 对比新旧数据
7. 保留好的，回滚坏的
8. 记录（ADR）
```

## 9. 调优 checklist

```text
[ ] 系统目标是什么？（延迟 / 吞吐 / RPO / RTO）
[ ] 现在的瓶颈在哪？（USE）
[ ] 现在的服务指标如何？（RED）
[ ] 改哪个变量？
[ ] 怎么测？
[ ] 成功标准？
[ ] 回滚方案？
```

## 10. 关键 Takeaway

| 要点 | 记忆口诀 |
|------|----------|
| USE = 资源 | "USE=资源视角" |
| RED = 服务 | "RED=服务视角" |
| 改一个变量 | "一次=一变" |
| 先测后调 | "测在调先" |
| 记录决策 | "ADR=记录" |

## 参考

- Brendan Gregg《Systems Performance》
- Brendan Gregg《性能之巅》
- USE 方法博客
- RED 方法博客