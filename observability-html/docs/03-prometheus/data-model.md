---
title: Prometheus 数据模型
description: Metric + Label + Sample
---

# Prometheus 数据模型

> **TL;DR**：Prometheus 数据模型 = **Metric（指标名）+ Label（标签键值对）+ Sample（时间戳 + 值）**。**所有数据都是时间序列**：`<metric>{<labels>} <value> @ <timestamp>`。**Label 是 Prometheus 维度切片的灵魂，**慎用高基数标签**。

## 一句话定义

```
时间序列（Time Series）= metric + labels + samples
                        = 同一 metric + label 组合的一个时间序列
                        = 例：http_requests_total{service="order",status="200"} 1423

Metric（指标名）= 描述测量什么（用 snake_case）
Label（标签）= 维度切片键值对
Sample（样本）= (timestamp, value) 数据点
```

## Metric 类型

### 1. Counter（计数器）

```
只能递增的指标（重启时可重置为 0）
用途：请求总数 / 错误总数 / 任务完成数

# 例：HTTP 请求总数
http_requests_total{service="order",method="POST",status="200"} 1423456

# PromQL 计算速率
rate(http_requests_total[5m])   # 每秒请求数
```

### 2. Gauge（仪表盘）

```
可增可减的指标
用途：当前温度 / 队列长度 / CPU 使用率

# 例：当前活跃连接数
db_connections_active 142

# PromQL
delta(db_connections_active[5m])  # 5 分钟变化量
```

### 3. Histogram（直方图）

```
分桶统计（bucket）= 延迟 / 大小 等分布数据
用途：延迟 / 响应大小

# 例：HTTP 请求延迟（buckets: 0.005s, 0.01s, ..., 10s）
http_request_duration_seconds_bucket{le="0.005"} 23456
http_request_duration_seconds_bucket{le="0.01"} 25678
http_request_duration_seconds_bucket{le="+Inf"} 50000
http_request_duration_seconds_sum 1234.56
http_request_duration_seconds_count 50000

# PromQL 计算分位数
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
```

### 4. Summary（摘要）

```
类似 Histogram，但服务端预计算分位数
缺点：不可聚合（分位数不能跨实例求平均）

# 例：客户端报告 P99 延迟
http_request_duration_seconds{quantile="0.99"} 1.234

# 实战：Histogram 优于 Summary（可聚合）
```

## Label 命名规范

```yaml
# 良好实践：
- service: "order-api"
- env: "prod"
- region: "cn-north-1"
- status: "200"

# 禁用（高基数，会导致时序爆炸）：
- user_id: "12345"          # 100w 用户 = 100w 时序
- email: "[email protected]"
- order_id: "ORD-001"
- request_id: "abc-def"
- timestamp: "..."          # 完全禁忌
```

## 时序存储

```
Prometheus TSDB 内部结构：
  - Block = 一段时间（如 2 小时）的所有时序
  - 每个时序按 (metric, labels) 哈希
  - 压缩算法：Gorilla (Facebook 2015)，平均 1.3 字节/样本
  - 块文件：head (内存) + persisted (磁盘)

存储路径：
  /prometheus-data/
    01GBM0AC4N0WJZ37H8Z7G8KX1V  # block 1
    01GBM2R8NQ3WXCV9Q4SFXJ8XCP  # block 2
    chunks_head/                # head block

远程存储：
  - remote_write: Prometheus → Thanos / Cortex / InfluxDB / Mimir
  - remote_read: 从远程读
```

## 实战案例：自定义 Counter / Histogram

```go
// Go (prometheus client_golang)
import "github.com/prometheus/client_golang/prometheus"

var (
    requestCounter = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total HTTP requests",
        },
        []string{"service", "method", "status"},
    )

    requestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request duration",
            Buckets: []float64{0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10},
        },
        []string{"service", "endpoint"},
    )
)

func init() {
    prometheus.MustRegister(requestCounter, requestDuration)
}
```

## 一句话总结

> **Prometheus 数据 = Metric + Label + Sample**。**四种类型：Counter / Gauge / Histogram / Summary**。**Label 设计决定查询能力**。**禁止高基数标签（user_id / order_id）**。

---

## 关联章节

- [Prometheus 概览](../03-prometheus/overview.md) — 架构
- [PromQL](../03-prometheus/promql.md) — 查询语言
- [Exporter](../03-prometheus/exporter.md) — 暴露指标的工具

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
