---
title: 微服务全链路追踪
date: 2026-08-15  # date-auto-injected
description: 跨服务 trace + 服务地图 + 依赖分析
---

# 微服务全链路追踪

> **TL;DR**：**微服务全链路追踪 = Trace 串联所有服务 + Service Map 自动生成依赖图 + SpanMetrics 生成调用指标**。**核心：W3C Trace Context（traceparent header）+ OpenTelemetry SDK 自动注入 + OTel Collector SpanMetrics 转换**。**实战：一次 HTTP 请求从 LB 到 gateway 到 5 个微服务再到 DB 的完整路径**。

## 一句话定义

```
微服务全链路追踪 = 跨服务 trace 串联
                = W3C Trace Context 标准
                = 自动生成服务地图（service map）
                = 自动生成调用关系指标（SpanMetrics）
                = 工具：OpenTelemetry SDK + Collector + Jaeger/Tempo
```

## 完整架构

```
                 ┌──────┐
   Client ──────▶│  LB  │ (envoy/nginx)
                 └──────┘
                     │ traceparent: 00-aaaa-bbbb-01
                     ▼
              ┌──────────────┐
              │   Gateway    │ (Spring Cloud Gateway)
              │  span: http  │
              └──────┬───────┘
                     │ traceparent
        ┌────────────┼────────────┐
        ▼            ▼            ▼
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │ order-   │ │ payment- │ │ user-    │
  │ service  │ │ service  │ │ service  │
  │ span:    │ │ span:    │ │ span:    │
  │ grpc     │ │ http     │ │ db       │
  └────┬─────┘ └────┬─────┘ └────┬─────┘
       │            │            │
       ▼            ▼            ▼
   ┌────────┐  ┌────────┐   ┌────────┐
   │  MySQL │  │  Redis │   │  MySQL │
   │ span:  │  │ span:  │   │        │
   │ jdbc   │  │ redis  │   │        │
   └────────┘  └────────┘   └────────┘
```

## OpenTelemetry SDK 自动注入

```bash
# Java：所有服务统一一行 javaagent
java -javaagent:./opentelemetry-javaagent.jar      -Dotel.service.name=order-service      -Dotel.exporter.otlp.endpoint=http://otel-collector:4317      -jar order-service.jar

# 关键环境变量：
-Dotel.service.name=order-service           # 服务名（ServiceMap 节点）
-Dotel.propagators=tracecontext,baggage     # 跨进程传播（W3C）
-Dotel.traces.exporter=otlp                # 导出器
-Dotel.metrics.exporter=otlp
```

## W3C Trace Context 协议

```http
# HTTP 请求自动注入 traceparent header
GET /api/orders HTTP/1.1
Host: api.example.com
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: congo=t61rcWkgMzE

# 格式：
# 00 - version
# 4bf92f3577b34da6a3ce929d0e0e4736 - trace_id (32 hex chars)
# 00f067aa0ba902b7 - span_id (16 hex chars)
# 01 - flags (sampled)
```

## OTel Collector SpanMetrics

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc: { endpoint: 0.0.0.0:4317 }

processors:
  # 关键：从 span 生成 RED 指标
  spanmetrics:
    metrics_expiration: 5m
    metrics_flush_interval: 15s
    histogram: explicit
    dimensions:
      - name: http.method
        default: GET
      - name: http.status_code

exporters:
  prometheus:
    endpoint: 0.0.0.0:8889
  otlp/tempo:
    endpoint: tempo:4317
    tls: { insecure: true }

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [spanmetrics, batch]
      exporters: [otlp/tempo]

    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
```

```
SpanMetrics 自动生成指标：
  - traces.spanmetrics.calls.total{service, span_name, status_code}
  - traces.spanmetrics.duration.sum{service, span_name}
  - traces.spanmetrics.duration.bucket{service, span_name, le}
```

## Service Map 自动生成

```yaml
# Tempo / Jaeger 自动从 trace 生成依赖图
# 圆圈 = 服务，连线 = 调用关系
# 圆圈大小 = 请求量，连线粗细 = 调用次数

# 实战：在 Grafana 看 Tempo Service Map
# Explore → Tempo → Service Map 标签页
```

## 实战案例：定位慢请求

```
场景：用户反馈下单慢（10s+）

排查步骤：
  1. 打开 Grafana → APM（vía Tempo / Jaeger UI）
  2. service = order-api, lookback = 1h, minDuration = 10s
  3. 找到慢 trace → 点开
  4. 瀑布图看到 payment-service span 占 9s
  5. payment-service 内部：grpc.client 占 8s
  6. 跳到 payment-service trace → 看 bank-api 调用占 8s
  7. 结论：bank-api 通道慢
  8. 行动：切换备用通道 + 给 bank-api 反馈

无 trace 时：
  - 用户说慢 → 看指标 → 看日志 → 抓包 → 3 小时
有 trace 时：
  - 1 分钟定位到具体 span
```

## 异步上下文传播

```
陷阱：线程池 / MQ / 异步回调容易丢 trace

线程池：
  // 错误
  executor.submit(() -> {
      // 这里 trace context 丢失
      processOrder();
  });

  // 正确（Java）
  executor.submit(() -> {
      try (Scope scope = Context.current().makeCurrent()) {
          processOrder();
      }
  });

Kafka：
  // Producer 端：自动注入 traceparent 到 header
  kafkaTemplate.send(...);

  // Consumer 端：自动提取
  @KafkaListener(topics = "orders")
  public void onMessage(ConsumerRecord<String, Order> record) {
      // trace context 自动恢复
  }
```

## 一句话总结

> **微服务 trace = W3C Trace Context + OTel SDK + Collector SpanMetrics**。**一次 HTTP 请求 = 完整 trace 串联所有 span**。**自动生成 Service Map + 调用指标**。

---

## 关联章节

- [Tracing 基础](../06-tracing/concepts.md)
- [Jaeger](../06-tracing/jaeger.md)
- [Tempo](../06-tracing/tempo.md)
- [K8s 监控](./k8s-monitor.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
