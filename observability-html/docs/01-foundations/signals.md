---
title: 信号类型
description: Counter / Gauge / Histogram / Summary 的本质与选型
---

# 可观测性信号类型

> **TL;DR**：信号类型不是 Prometheus 独有的概念，而是**所有时序数据库的通用模型**。Counter / Gauge / Histogram / Summary 各有适用场景，**选错类型 = 算不出正确的数**。

## 四种核心类型

| 类型 | 特点 | 典型用例 | 计算方式 |
|---|---|---|---|
| **Counter** | 单调递增，只增不减 | 请求总数、错误总数、字节传输总数 | rate() / increase() |
| **Gauge** | 可增可减，瞬时值 | CPU 使用率、内存占用、队列长度 | 直接取值 / delta() |
| **Histogram** | 样本分布（桶） | 延迟分布、响应大小 | histogram_quantile() |
| **Summary** | 客户端预聚合的分位数 | 客户端计算的 p99 | 直接读 quantile |

## Counter · 单调递增计数器

**定义**：只能增加（或被 reset 清零）的累计值。

**典型例子**：

```
http_requests_total{service="order", status="200"} = 12345678
http_requests_total{service="order", status="500"} = 234
```

**核心 PromQL**：

```promql
# 最近 5 分钟的请求速率（每秒）
rate(http_requests_total[5m])

# 最近 1 小时的总增量
increase(http_requests_total[1h])

# 错误率（错误请求 / 总请求）
sum(rate(http_requests_total{status="500"}[5m]))
/
sum(rate(http_requests_total[5m]))
```

**注意事项**：

```promql
# ❌ 错误：Counter 是累计值，不能直接当瞬时值用
http_requests_total  # = 12345678，无意义

# ✅ 正确：必须 rate() 或 increase() 处理
rate(http_requests_total[5m])  # = 234/s

# ❌ 错误：rate 不能用于时间窗口 < 采集间隔
rate(http_requests_total[10s])  # 噪声极大

# ✅ 正确：rate 时间窗口 ≥ 4 倍采集间隔（采集间隔 15s，rate 窗口至少 1m）
rate(http_requests_total[1m])
```

> **Prometheus 官方建议**：rate 窗口是采集间隔的 4-5 倍。例如 15s 采集，rate 用 [1m] 或 [5m]。

## Gauge · 瞬时值

**定义**：可增可减的数值，反映某个时刻的状态。

**典型例子**：

```
cpu_usage_percent{instance="web-01"} = 67.3
memory_used_bytes{instance="web-01"} = 4.2e9
queue_length{queue="order-process"} = 1234
active_connections{service="db"} = 89
```

**核心 PromQL**：

```promql
# 直接取值
cpu_usage_percent

# 5 分钟内的平均 CPU 使用率
avg_over_time(cpu_usage_percent[5m])

# 队列长度的变化趋势
delta(queue_length[5m])

# 预测何时队列会满
predict_linear(queue_length[1h], 4 * 3600) > 10000

# 与历史同期对比
cpu_usage_percent > on(instance) cpu_usage_percent offset 1d
```

**注意事项**：

```promql
# ❌ Gauge 不能用 rate()（rate 假设 Counter 单调）
rate(memory_used_bytes[5m])  # 可能为负值，无意义

# ❌ Gauge 不能 increase()（increase 也假设单调）
increase(queue_length[5m])  # 无意义

# ✅ Gauge 应该直接读、avg_over_time、max_over_time
```

> **判断类型**：在 Grafana 上画图，**Counter 趋势线只升不降**（除 reset），**Gauge 趋势线起伏**。

## Histogram · 分布桶

**定义**：把样本值分到一组桶里，每个桶记录落入次数。

**典型例子**（HTTP 请求延迟分布）：

```
http_request_duration_seconds_bucket{le="0.005"} 10245
http_request_duration_seconds_bucket{le="0.01"}  15890
http_request_duration_seconds_bucket{le="0.025"} 28390
http_request_duration_seconds_bucket{le="0.05"}  42011
http_request_duration_seconds_bucket{le="0.1"}   56890
http_request_duration_seconds_bucket{le="0.25"}  78901
http_request_duration_seconds_bucket{le="0.5"}   89340
http_request_duration_seconds_bucket{le="1"}     92013
http_request_duration_seconds_bucket{le="2.5"}   93456
http_request_duration_seconds_bucket{le="5"}     93601
http_request_duration_seconds_bucket{le="10"}    93612
http_request_duration_seconds_bucket{le="+Inf"}  93612
http_request_duration_seconds_sum              1234.56  # 所有样本延迟之和
http_request_duration_seconds_count            93612   # 样本总数
```

**核心 PromQL**：

```promql
# p99 延迟（最常用！）
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
)

# p95 延迟
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

# p50（中位数）
histogram_quantile(0.50,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

# 平均延迟
rate(http_request_duration_seconds_sum[5m])
/
rate(http_request_duration_seconds_count[5m])
```

**Histogram vs Summary**：

| 维度 | Histogram | Summary |
|---|---|---|
| 计算位置 | 服务端（Prometheus 算分位数） | 客户端（应用算好分位数） |
| 可聚合 | ✅ 任意维度聚合 | ❌ 客户端预聚合，无法跨实例聚合 |
| 精度 | 取决于桶设计 | 取决于客户端 quantile 配置 |
| 适用场景 | 大多数场景 | 单实例精细化监控 |

> **99% 场景用 Histogram**。Summary 的"无法跨实例聚合"是致命缺陷。

## Summary · 客户端分位数

**定义**：客户端预计算的分位数，每个 quantile 是一个时序。

**典型例子**：

```
rpc_duration_seconds{service="order", quantile="0.5"}  0.023
rpc_duration_seconds{service="order", quantile="0.9"}  0.089
rpc_duration_seconds{service="order", quantile="0.99"} 0.245
rpc_duration_seconds_sum                              1234.56
rpc_duration_seconds_count                            93612
```

**核心 PromQL**：

```promql
# 直接读 quantile（不能聚合！）
rpc_duration_seconds{quantile="0.99"}

# ❌ 错误：quantile 是客户端预聚合的，不能跨实例求平均
avg(rpc_duration_seconds{quantile="0.99"})  # 无意义
```

**何时用 Summary**：
- 单实例监控（不关心聚合）
- 想节省服务端计算（客户端已算好）
- 应用有自定义分位数需求（如 p99.9）

## 类型选型决策

```
要测的是"一段时间内发生多少次"？
├─ 是 → Counter
│   ├─ 请求数、错误数、字节数
│   └─ 用 rate() / increase() 计算
│
└─ 否 → Gauge
    ├─ 瞬时状态：CPU、内存、队列长度
    └─ 直接读 / avg_over_time / max_over_time

要测的是"分布"（如延迟、响应大小）？
├─ 是 + 需要跨实例聚合 → Histogram
│   └─ 用 histogram_quantile() 计算分位数
│
└─ 是 + 单实例 / 不需聚合 → Summary
    └─ 直接读 quantile
```

## 实战例子：HTTP 服务指标设计

```yaml
# Counter：累计计数
http_requests_total{service, method, status, code}    # 请求总数
http_request_errors_total{service, method, status}    # 错误总数

# Gauge：瞬时状态
http_active_connections{service}                       # 当前活跃连接数
http_inflight_requests{service}                        # 处理中请求数

# Histogram：分布
http_request_duration_seconds{service, method}         # 延迟分布
http_response_size_bytes{service, method}              # 响应大小分布
```

**最常见错误**：

```promql
# ❌ Counter 当 Gauge 用
http_requests_total  # 累计值，无业务含义

# ❌ Histogram 不带 _bucket 用 rate
rate(http_request_duration_seconds[5m])  # 用错了

# ❌ Summary 跨实例聚合
avg(rpc_duration_seconds{quantile="0.99"})  # 数学上不合法

# ❌ Histogram 不带 le 标签聚合
sum(http_request_duration_seconds_bucket)  # 漏了 by (le)
```

## 一句话总结

> **选错类型 = 算不出正确的数，埋了再多指标也是废数据**。
> Counter = 累计，rate() 才有意义；Gauge = 瞬时，直接读；Histogram = 分布，histogram_quantile() 算分位数。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

<!-- svg-injected:do-not-edit -->

![observability stack](/observability-stack.svg)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
