---
title: USE 方法
description: Utilization / Saturation / Errors
---

# USE 方法

> **TL;DR**：USE 方法 = **资源级别的黄金三指标**。**Utilization（利用率）+ Saturation（饱和度）+ Errors（错误）**。**Brendan Gregg 2012 提出**。**RED 看服务对外表现，USE 看资源（CPU / 内存 / 磁盘 / 网络 / IO）是否即将耗尽**。**每个资源都必须问这三个问题**。

## 一句话定义

```
USE 方法 = 资源（Resource）的三大黄金指标
        = Utilization（资源利用率）
        = Saturation（资源饱和度，等待队列长度）
        = Errors（资源错误事件数）
        = Brendan Gregg 2012 提出（Netflix/Concolidated)
        = 适用：CPU / 内存 / 磁盘 / 网络 / IO / 线程池 / 连接池
```

## 三大指标详解

### 1. Utilization（利用率）

```
定义：资源忙于工作的时间百分比
      例：CPU 在 1 分钟内有 45 秒在执行指令 → 利用率 75%

关键：单核 100% ≠ 多核 100%
      16 核 CPU 中 1 核 100% = 总利用率 6.25%
      必须按核分开看，不能只看平均

Prometheus 查询：
node_cpu_seconds_total{mode!="idle"}   # 非 idle 时间
1 - avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m]))  # 利用率
```

### 2. Saturation（饱和度）

```
定义：资源无法服务的额外工作量
      通常表现为等待队列长度 / 排队时间
      例：CPU run queue 长度 / IO 队列深度 / 线程池活跃数

CPU 饱和度：load average / run queue
  node_load5 > cores * 0.7  → 饱和预警

IO 饱和度：IO 等待时间占比
  100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

线程池饱和度：活跃线程数 / 最大线程数
  thread_pool_active / thread_pool_max  > 0.8

连接池饱和度：活跃连接 / 最大连接
  db_connections_active / db_connections_max  > 0.8
```

### 3. Errors（错误）

```
定义：资源错误事件计数
      例：网卡丢包数 / 磁盘 IO 错误 / 内存分配失败

网络丢包：
node_network_receive_drop_total

磁盘 IO 错误：
node_disk_io_now   # 当前 IO 数
node_disk_errors_total   # 累积错误数

内存分配失败（OOM）：
node_vmstat_pgpgin  # 页换入（间接指标）
container_oom_events_total   # K8s OOM 事件
```

## 资源 USE 检查清单

| 资源 | Utilization | Saturation | Errors |
|---|---|---|---|
| **CPU** | `node_cpu_seconds_total{mode!="idle"}` | `node_load5` / run queue | `node_cpu_seconds_total{mode="steal"}` |
| **内存** | `(1 - node_memory_MemAvailable/node_memory_MemTotal)` | `node_memory_SwapFree` 减少 / page faults | `node_vmstat_pgmajfault` |
| **磁盘** | `node_disk_io_now` / `iostat -x %util` | `node_disk_io_time_seconds_total` | `node_disk_io_errors` |
| **网络** | `node_network_receive_bytes_total / bandwidth` | `node_network_transmit_queue` / drops | `node_network_receive_drop_total` |
| **线程池** | `thread_pool_active / thread_pool_max` | `thread_pool_queue_size` | `thread_pool_rejected_total` |
| **连接池** | `db_pool_active / db_pool_max` | `db_pool_waiting_threads` | `db_pool_connection_errors_total` |
| **文件描述符** | `process_open_fds / process_max_fds` | N/A | `process_fds_open_failed` |

## 完整示例：CPU USE 看板

```promql
# 1. Utilization：CPU 各模式时间
sum by (mode) (rate(node_cpu_seconds_total{mode!="idle", instance=~".+"}[5m]))

# 2. Saturation：Load Average
node_load5 / count by (instance) (node_cpu_seconds_total{mode="system"}) > 0.7

# 3. Errors：CPU steal time（虚拟化被抢占）
rate(node_cpu_seconds_total{mode="steal"}[5m])

# 4. 综合告警（USE → SLO）
- alert: CPUSaturation
  expr: |
    node_load5
    /
    count by (instance) (node_cpu_seconds_total{mode="system"})
    > 1.5  # load > 核数 1.5 倍
  for: 10m
  labels: {severity: warning}
```

## 完整示例：JVM USE 看板

```promql
# 1. CPU 利用率（Java 进程 CPU）
rate(process_cpu_seconds_total{job="java-app"}[5m]) * 100

# 2. 内存：堆内存使用
jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} * 100

# 3. 线程池饱和度：Tomcat 活跃线程 / 最大线程
tomcat_threads_busy / tomcat_threads_config_max > 0.8

# 4. GC 暂停时间（属于 Saturation）
rate(jvm_gc_pause_seconds_sum[5m]) / rate(jvm_gc_pause_seconds_count[5m])

# 5. OOM 错误
jvm_memory_used_bytes{area="heap"} > jvm_memory_max_bytes{area="heap"}
```

## 实战案例：数据库连接池 USE

```promql
# HikariCP 连接池指标
# U: 连接使用率
hikaricp_connections_active / hikaricp_connections_max * 100

# S: 等待连接的线程数（队列长度）
hikaricp_connections_pending

# E: 获取连接超时次数
rate(hikaricp_connection_timeout_total[5m])

# 告警阈值：
# - U > 80% 持续 5min → warning（即将耗尽）
# - S > 50 → critical（队列堆积）
# - E > 0 → critical（超时，连接不够用）
```

## USE × 不同角色

```
DevOps / SRE 视角：
  - 全部资源 USE 监控
  - 重点：磁盘 / 内存 / 网络（物理资源）
  - 工具：node_exporter / Prometheus / Grafana

后端开发视角：
  - JVM 内部 USE：堆 / GC / 线程池 / 类加载
  - 工具：Micrometer + Prometheus + JFR（Java Flight Recorder）

DBA 视角：
  - 数据库连接池 / 锁等待 / 缓存命中率 / 主从延迟
  - 工具：pg_stat / MySQL performance_schema / Prometheus DB exporter
```

## USE vs RED 何时用？

```
场景 1：服务出问题但找不到原因
  → 先看 USE（资源是不是快挂了）
  → 再看 RED（服务对外表现）
  → 最后看 trace（哪个 span 慢）

场景 2：服务器告警 CPU 高
  → USE 视角：CPU Utilization 90%
  → 进一步看：哪个进程（top）+ 哪个线程
  → 看进程内：JVM GC / 业务循环 / 死循环

场景 3：服务 P99 突增
  → RED 视角：Duration ↑
  → 看 trace：哪个 span 慢
  → 看 USE：依赖的下游服务 / 数据库 / Redis 是否饱和
  → 看日志：异常堆栈

最佳实践：
  - 告警面板：RED 看 SLO（用户视角）
  - 容量面板：USE 看资源（运维视角）
  - 故障排查：RED → USE → Trace → Log 四层下钻
```

## 一句话总结

> **USE = 资源三件套：Utilization + Saturation + Errors**。**每类资源（CPU/内存/磁盘/网络/线程池/连接池）都问这三个问题**。**RED 看服务，USE 看资源，两者是互补的**。

---

## 关联章节

- [RED 方法](./red-method.md) — 服务级黄金指标
- [JVM 指标](./jvm-metrics.md) — Java 应用 USE 实践
- [K8s 指标](./k8s-metrics.md) — 容器资源 USE
- [业务指标设计](./business-metrics.md) — 业务维度 USE

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>