---
title: RED 方法
description: Rate / Errors / Duration
---

# RED 方法

> **TL;DR**：RED 方法 = **服务级别的黄金三指标**。**Rate（每秒请求数）+ Errors（错误率）+ Duration（延迟分布）**。**Tom Wilkie 2015（Weaveworks）提出**。**每个微服务都必须暴露这三个指标**，**是从 SLO 到告警的最小集合**。

## 一句话定义

```
RED 方法 = 服务（Service）的三大黄金指标
        = Rate（请求速率）
        = Errors（错误率 / 错误数）
        = Duration（延迟，分布而非平均值）
        = Tom Wilkie 2015 提出（Weaveworks）
```

## 三大指标详解

### 1. Rate（速率）

```promql
# 1. 总请求率
sum(rate(http_requests_total[5m]))

# 2. 按服务分组的请求率
sum by (service) (rate(http_requests_total[5m]))

# 3. 按 endpoint 分组
sum by (service, endpoint) (rate(http_requests_total[5m]))

# 4. 成功请求 vs 总请求
sum(rate(http_requests_total{status!~"5.."}[5m]))
/ sum(rate(http_requests_total[5m]))
```

### 2. Errors（错误）

```promql
# 1. 错误率（4xx + 5xx）
sum(rate(http_requests_total{status=~"[45].."}[5m]))
/ sum(rate(http_requests_total[5m]))

# 2. 5xx 错误率（critical）
sum(rate(http_requests_total{status=~"5.."}[5m]))
/ sum(rate(http_requests_total[5m]))

# 3. 绝对错误数
sum(rate(http_requests_total{status=~"5.."}[5m]))

# 4. 业务错误（如支付失败）
sum(rate(business_errors_total{type="payment_failed"}[5m]))
```

### 3. Duration（延迟）

```promql
# 1. P50 延迟
histogram_quantile(0.50,
  sum by (le, service) (rate(http_request_duration_seconds_bucket[5m]))
)

# 2. P99 延迟
histogram_quantile(0.99,
  sum by (le, service) (rate(http_request_duration_seconds_bucket[5m]))
)

# 3. P95/P99/P999 三档
histogram_quantile(0.95, sum by (le) (rate(...[5m])))
histogram_quantile(0.99, sum by (le) (rate(...[5m])))
histogram_quantile(0.999, sum by (le) (rate(...[5m])))

# 4. 平均延迟（不推荐，掩盖 P99 长尾）
rate(http_request_duration_seconds_sum[5m])
/ rate(http_request_duration_seconds_count[5m])
```

## 与 USE 方法对比

| 维度 | RED（服务级） | USE（资源级） |
|---|---|---|
| **关注** | 服务对外表现 | 资源健康度 |
| **指标** | Rate / Errors / Duration | Utilization / Saturation / Errors |
| **对象** | 微服务 / API | CPU / 内存 / 磁盘 / 网络 |
| **谁看** | SRE / 业务开发 | 运维 / SRE |
| **告警** | 影响用户时 | 资源即将耗尽时 |
| **提出** | Tom Wilkie 2015 | Brendan Gregg 2012 |

> **实战组合**：服务层 RED + 资源层 USE = 完整 SLO 监控

## OpenTelemetry 自动埋点（Java）

```java
// 1. 添加依赖
// <dependency>
//   <groupId>io.opentelemetry.instrumentation</groupId>
//   <artifactId>opentelemetry-spring-boot-starter</artifactId>
// </dependency>

// 2. 自动捕获：HTTP server 指标（Tomcat/Jetty/Netty）
// 自动暴露：
//   http.server.request.count      (counter)
//   http.server.request.duration   (histogram)
// 标签：method, status, uri, http.route
```

```yaml
# 3. application.yml 配置 OTLP 导出
otel:
  service:
    name: order-service
  metrics:
    export:
      otlp:
        endpoint: http://otel-collector:4317
  traces:
    export:
      otlp:
        endpoint: http://otel-collector:4317
```

```yaml
# 4. OpenTelemetry Collector 导出到 Prometheus
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

processors:
  batch:

exporters:
  prometheus:
    endpoint: 0.0.0.0:8889

service:
  pipelines:
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
```

## 手动埋点（Go）

```go
// 1. 引入 prometheus client
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    httpRequestsTotal = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total HTTP requests",
        },
        []string{"method", "endpoint", "status"},
    )

    httpRequestDuration = promauto.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request duration",
            Buckets: []float64{0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10},
        },
        []string{"method", "endpoint"},
    )
)

// 2. 在 middleware 中记录
func instrumentMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        // 调用 next.ServeHTTP
        ww := &statusRecorder{ResponseWriter: w, status: 200}
        next.ServeHTTP(ww, r)

        duration := time.Since(start).Seconds()
        endpoint := r.URL.Path
        method := r.Method

        httpRequestsTotal.WithLabelValues(method, endpoint, strconv.Itoa(ww.status)).Inc()
        httpRequestDuration.WithLabelValues(method, endpoint).Observe(duration)
    })
}
```

## 实战案例：电商订单服务 RED 看板

```yaml
# Grafana Dashboard JSON 片段（核心 panel）
panels:
  - title: Rate (req/s)
    type: timeseries
    targets:
      - expr: sum by (endpoint) (rate(http_requests_total{service="order"}[5m]))

  - title: Errors (%)
    type: timeseries
    targets:
      - expr: |
          sum(rate(http_requests_total{service="order", status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total{service="order"}[5m]))
          * 100

  - title: P50 / P95 / P99 Latency
    type: timeseries
    targets:
      - expr: histogram_quantile(0.50, sum by (le) (rate(http_request_duration_seconds_bucket{service="order"}[5m])))
        legendFormat: P50
      - expr: histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{service="order"}[5m])))
        legendFormat: P95
      - expr: histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket{service="order"}[5m])))
        legendFormat: P99
```

## RED 指标 SLO 配置

```yaml
# Prometheus alert rules（基于 RED）
- alert: HighErrorRate
  expr: |
    sum(rate(http_requests_total{service="order", status=~"5.."}[5m]))
    /
    sum(rate(http_requests_total{service="order"}[5m]))
    > 0.01  # 1% 错误率
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "订单服务错误率 > 1%"
    runbook: "https://wiki/runbooks/order-error-rate"

- alert: HighLatencyP99
  expr: |
    histogram_quantile(0.99,
      sum by (le) (rate(http_request_duration_seconds_bucket{service="order"}[5m]))
    ) > 2  # P99 > 2s
  for: 10m
  labels:
    severity: warning
```

## 一句话总结

> **RED = 服务三件套：Rate + Errors + Duration**。**每个微服务必须有这三类指标**。**自动埋点（OTel） > 手动埋点 > 没埋点**。**RED 看服务，USE 看资源，两者结合 = 完整可观测**。

---

## 关联章节

- [USE 方法](./use-method.md) — 资源级黄金指标
- [Prometheus 告警](../03-prometheus/alert.md) — 基于 RED 写告警
- [SLI/SLO](../01-foundations/sli-slo.md) — RED 是 SLI 三大来源
- [OpenTelemetry 自动埋点](../02-opentelemetry/auto-instrumentation.md) — 零代码埋 RED

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
