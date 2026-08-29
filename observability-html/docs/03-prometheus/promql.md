---
title: PromQL 详解
date: 2026-08-15  # date-auto-injected
description: Prometheus 查询语言实战
---

# PromQL 详解

> **TL;DR**：PromQL 是 Prometheus Query Language，类似 SQL 但专为时序数据设计。掌握 PromQL = 掌握 Prometheus 的 80% 价值。**会写 PromQL，就能从指标里挖出任何业务问题**。

## 一句话定义

```
PromQL = 时序数据查询语言，类 SQL，专门为 metrics 设计
```

## 基础概念

### 时序样本（Sample）

```
# Prometheus 中的一个数据点
http_requests_total{service="order", method="POST", status="200"} 12345 1700000000
                                        ↑  标签              ↑ 值   ↑ 时间戳
```

### 即时向量（Instant Vector）

**同一时刻**的一组时序。

```
http_requests_total
# 返回：
# http_requests_total{service="order", status="200"} = 12345
# http_requests_total{service="order", status="500"} = 23
# http_requests_total{service="payment", status="200"} = 67890
# ...
```

### 范围向量（Range Vector）

**一段时间内**的时序。

```
http_requests_total[5m]
# 返回：每个时序在 5 分钟内的所有样本
# {service="order", status="200"}  [(t1, v1), (t2, v2), ..., (t5, v5)]
```

## 数据类型

| 类型 | 含义 | 例子 |
|---|---|---|
| **Instant vector** | 某时刻一组样本 | `http_requests_total` |
| **Range vector** | 一段时间内一组样本 | `http_requests_total[5m]` |
| **Scalar** | 浮点数 | `1.5` |
| **String** | 字符串（少用） | `"hello"` |

## 基础查询

### 1. 选择时序

```promql
# 所有 http_requests_total
http_requests_total

# 按 service 过滤
http_requests_total{service="order"}

# 多标签过滤
http_requests_total{service="order", method="POST"}

# 正则匹配
http_requests_total{service=~"order|payment"}
http_requests_total{method!="GET"}

# 多值正则
http_requests_total{status=~"5.."}
```

### 2. 时间范围

```promql
# 最近 5 分钟
http_requests_total[5m]

# 最近 1 小时
http_requests_total[1h]

# 1 天
http_requests_total[1d]

# 1 周
http_requests_total[1w]
```

## 核心函数（按使用频率排序）

### Counter 函数

#### `rate()` · 速率

```promql
# 最近 5 分钟每秒平均增长率
rate(http_requests_total[5m])

# ⚠️ Counter 必须用 rate()/increase()，直接用无意义
```

**适用场景**：每秒请求数、每秒错误数

#### `increase()` · 增量

```promql
# 最近 1 小时的总增量
increase(http_requests_total[1h])
```

**适用场景**：小时报 / 天报

#### `irate()` · 瞬时速率

```promql
# 最近 2 个点的瞬时速率（更敏感，噪声大）
irate(http_requests_total[2m])
```

> **rate vs irate**：rate 平滑，irate 灵敏。**生产环境 90% 用 rate**，irate 只在低采集间隔 + 需要精确瞬时值时用。

### Gauge 函数

#### `delta()` · 变化量

```promql
# 5 分钟内队列长度变化
delta(queue_length[5m])
```

#### `deriv()` · 导数

```promql
# 5 分钟内队列长度的变化率
deriv(queue_length[5m])
```

#### `predict_linear()` · 线性预测

```promql
# 预测 1 小时后队列长度
predict_linear(queue_length[1h], 3600)
```

### Histogram 函数

#### `histogram_quantile()` · 分位数（最重要的函数！）

```promql
# p99 延迟
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
)

# ⚠️ 必须先 sum by (le, ...) 聚合，否则跨维度算出来是错的
```

#### `histogram_count()` / `histogram_sum()`

```promql
# 最近 5 分钟总样本数
histogram_count(http_request_duration_seconds_bucket)

# 最近 5 分钟总延迟（秒）
histogram_sum(http_request_duration_seconds)
```

### 聚合函数

#### `sum()` · 求和

```promql
# 所有 service 的总请求数
sum(http_requests_total)

# 按 service 求和（去掉 method 维度）
sum(http_requests_total) by (service)

# 按 service + status 求和
sum(http_requests_total) by (service, status)
```

#### `avg()` / `min()` / `max()`

```promql
# 所有实例的平均 CPU
avg(cpu_usage_percent)

# 最大 CPU
max(cpu_usage_percent)
```

#### `topk()` / `bottomk()`

```promql
# 请求数最多的 5 个 service
topk(5, sum(rate(http_requests_total[5m])) by (service))

# 请求数最少的 5 个 service
bottomk(5, sum(rate(http_requests_total[5m])) by (service))
```

#### `count()` · 计数

```promql
# 当前在线实例数
count(up == 1)

# CPU > 80% 的实例数
count(cpu_usage_percent > 80)
```

### 数学函数

```promql
# 错误率
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))

# p99 延迟（毫秒）
histogram_quantile(0.99, ...) * 1000

# 内存使用率
memory_used_bytes / memory_total_bytes * 100

# 绝对值
abs(delta(queue_length[5m]))
```

### 时间函数

```promql
# 当前时间（秒）
timestamp()

# 当前分钟
timestamp() / 60

# 一天的开始
timestamp() - (timestamp() % 86400)
```

## 实战查询（10 个必备）

### 1. 服务可用性（Availability SLI）

```promql
sum(rate(http_requests_total{status!~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

### 2. 错误率（Error Rate）

```promql
sum(rate(http_requests_total{status=~"5.."}[5m]))
/
sum(rate(http_requests_total[5m]))
```

### 3. p99 延迟

```promql
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service)
)
```

### 4. p95 延迟

```promql
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)
```

### 5. QPS（每秒请求数）

```promql
sum(rate(http_requests_total[1m]))
```

### 6. 在线实例数

```promql
count(up == 1)
```

### 7. CPU 使用率最高的前 5 个实例

```promql
topk(5, cpu_usage_percent)
```

### 8. 预测 1 小时后磁盘占满

```promql
predict_linear(disk_usage_bytes[6h], 3600 * 1) > disk_total_bytes
```

### 9. 服务平均响应时间

```promql
rate(http_request_duration_seconds_sum[5m])
/
rate(http_request_duration_seconds_count[5m])
```

### 10. 黄金信号看板（一个查询搞定所有）

```promql
# Latency
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
)

# Traffic
sum(rate(http_requests_total[5m]))

# Errors
sum(rate(http_requests_total{status=~"5.."}[5m]))

# Saturation
count(cpu_usage_percent > 80)
```

## 操作符

### 算术

```promql
# + - * / % ^
http_requests_total / 60  # 每分钟平均
cpu_usage_percent ^ 0.5   # 开方
```

### 比较

```promql
# == != > < >= <=
cpu_usage_percent > 80

# bool 修饰符：返回 0/1 而不是过滤
http_requests_total > bool 1000
```

### 集合操作

```promql
# and：两个向量都有的标签
up and cpu_usage_percent > 80

# or：两个向量的并集
up or cpu_usage_percent

# unless：差集
http_requests_total unless http_requests_total{service="deprecated"}
```

### 匹配（Vector Matching）

```promql
# 一对一匹配（默认）
# on：指定匹配标签
# ignoring：忽略匹配标签
# group_left / group_right：多对一

# 例：计算每个 instance 的 CPU 使用率 vs 该 instance 的请求数比例
rate(http_requests_total[5m]) / on(instance) cpu_usage_percent

# 例：计算每个 service 的总 QPS 与该 service 错误数
sum(rate(http_requests_total{status=~"5.."}[5m])) by (service)
/ on(service) group_left
sum(rate(http_requests_total[5m])) by (service)
```

## Recording Rule（录制规则）

**问题**：复杂的 PromQL 每次查询都重算，性能差。

**解决**：把常用查询预计算成新指标。

```yaml
# prometheus.yml
groups:
- name: order-service-rules
  rules:
  # 录制规则
  - record: order:http_requests:rate5m
    expr: sum(rate(http_requests_total{service="order"}[5m]))

  - record: order:http_request_duration:p99
    expr: |
      histogram_quantile(0.99,
        sum(rate(http_request_duration_seconds_bucket{service="order"}[5m])) by (le)
      )

  # 在告警中使用录制结果
  - alert: HighErrorRate
    expr: order:http_requests:rate5m > 100
    for: 5m
```

> **好处**：录制后查询 = 直接读 metrics，复杂度 O(1) vs 每次 O(N)。

## 常见错误

### 错误 1：Counter 不 rate

```promql
# ❌ 累计值无意义
http_requests_total > 10000

# ✅ rate 后比较
rate(http_requests_total[5m]) > 100
```

### 错误 2：histogram_quantile 不带 by (le)

```promql
# ❌ 漏 le 标签，结果错
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (service))

# ✅ 必须保留 le
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))
```

### 错误 3：rate 窗口太小

```promql
# ❌ 噪声极大
rate(http_requests_total[10s])

# ✅ 至少 4 倍采集间隔（15s 采集 → rate 窗口 1m）
rate(http_requests_total[1m])
```

### 错误 4：avg 误用

```promql
# ❌ Counter 累加后取平均，数学上无意义
avg(http_requests_total)

# ✅ rate 后再 avg
avg(rate(http_requests_total[5m]))
```

### 错误 5：忘记 by 子句

```promql
# ❌ 没分组，le 标签被吃，结果错
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])))

# ✅ 正确
histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket[5m])) by (le))
```

## 调试技巧

### 在 Grafana Explore 中测试

1. 打开 Grafana → Explore
2. 数据源选 Prometheus
3. 输入 PromQL，先看 Instant query 结果
4. 加 `[5m]` 看 Range vector
5. 加 `by (label)` 看聚合效果

### PromLens / PromQL Editor 工具

- [PromLens](https://promlens.com/)：可视化 PromQL 每一层计算过程
- Prometheus 自带 `/graph`：原始查询界面
- Grafana Explore：最常用的临时查询工具

## 一句话总结

> **PromQL 的核心：Counter 用 rate，Histogram 用 histogram_quantile(by le)，Gauge 直接读**。
> 记住这三条规则，再加 10 个实战查询模板，**覆盖 90% 的可观测性场景**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
