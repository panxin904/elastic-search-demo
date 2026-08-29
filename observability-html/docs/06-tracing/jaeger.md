---
title: Jaeger 链路追踪
date: 2026-08-15  # date-auto-injected
description: Uber 开源的 CNCF 毕业 tracing 系统
---

# Jaeger 链路追踪

> **TL;DR**：Jaeger = **Uber 开源 + CNCF 毕业**的分布式追踪系统。**架构：Client SDK → Agent（sidecar/daemonset）→ Collector → Storage（ES/Cassandra/Kafka）→ Query UI**。**对比 Zipkin：Jaeger 后端更现代、Cassandra/ES 存储、CQL/ES 查询**，**现代项目首选 Jaeger**。

## 一句话定义

```
Jaeger = Uber 2016 开源的分布式追踪系统
      = CNCF 第三个毕业项目（K8s / Prometheus 之后）
      = 完整链路：Client → Agent → Collector → Storage → Query
      = 支持 OpenTelemetry / Zipkin 协议
```

## 架构图

```
┌────────────┐  UDP    ┌──────────┐  gRPC    ┌────────────┐  Kafka/  ┌──────────┐
│ App SDK    │ ──────▶ │  Agent   │ ───────▶ │  Collector │ ───────▶ │  Storage │
│ (jaeger /  │         │ (local)  │          │ (ingest +  │          │  ES /    │
│  otel)     │         │          │          │  validate) │          │  Cassandra│
└────────────┘         └──────────┘          └────────────┘          └──────────┘
                                                                           │
                                                              ┌────────────▼────────────┐
                                                              │  Query / jaeger-ui      │
                                                              │  查 trace / span / tags  │
                                                              └─────────────────────────┘
```

## 核心概念

| 概念 | 定义 |
|---|---|
| **Trace** | 一次完整请求的调用链（tree of spans） |
| **Span** | 一次具体操作（含 start time / duration / tags / logs） |
| **Root Span** | 调用入口（HTTP 服务端 / MQ 消费者 / 定时任务） |
| **SpanContext** | traceID + spanID + baggage（跨服务传递） |
| **Agent** | 客户端 sidecar，UDP 接收 + 批量转发 |
| **Collector** | 无状态服务，校验 + 索引 + 写存储 |

## OpenTelemetry 集成（推荐）

```bash
# 1. 安装 OpenTelemetry SDK（以 Java 为例）
# otel-javaagent.jar 是自动注入埋点
java -javaagent:./opentelemetry-javaagent.jar \
     -Dotel.service.name=my-service \
     -Dotel.exporter.otlp.endpoint=http://otel-collector:4317 \
     -jar myapp.jar
```

```yaml
# 2. OpenTelemetry Collector 配置（导出到 Jaeger）
# otel-collector-config.yaml
exporters:
  jaeger:
    endpoint: jaeger-collector:14250
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [jaeger]
```

## Kubernetes 部署

```yaml
# jaeger-all-in-one（开发测试用）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jaeger
spec:
  replicas: 1
  template:
    spec:
      containers:
        - name: jaeger
          image: jaegertracing/all-in-one:1.55
          ports:
            - containerPort: 16686  # UI
            - containerPort: 14250  # gRPC
            - containerPort: 14268  # HTTP
          env:
            - name: COLLECTOR_OTLP_ENABLED
              value: "true"  # 接收 OTLP 协议
```

```yaml
# 生产级：Collector + Storage + Query 分开
# 1. Collector（无状态，可水平扩）
# 2. Storage：Elasticsearch（推荐）或 Cassandra
# 3. Query：jaeger-query 服务
# 4. Ingester：可选，用于从 Kafka 读 spans
```

## 采样策略

```yaml
# jaeger-collector 配置
# 1. 概率采样（恒定比例）
sampling:
  default_strategy:
    type: probabilistic
    param: 0.1  # 10% 采样

# 2. 速率限制采样（每秒 N 个 trace）
sampling:
  default_strategy:
    type: ratelimiting
    param: 100

# 3. 远程采样（adaptive，根据上游决定）
sampling:
  default_strategy:
    type: remote
    param:
      endpoint: http://jaeger-collector:14250/api/sampling

# 4. 自适应：error 100% 采样，正常流量 1% 采样
# 用 OpenTelemetry 的 tail-based sampling processor
processors:
  tail_sampling:
    decision_wait: 10s
    num_traces: 100000
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow
        type: latency
        latency: { threshold_ms: 2000 }
      - name: default
        type: probabilistic
        probabilistic: { sampling_percentage: 1 }
```

## Jaeger UI 核心功能

```
1. Search 搜索
   - service / operation / tags / minDuration / maxDuration
   - 例：service=checkout, http.status_code=500, lookback=1h

2. Trace 详情
   - Span 列表 + 时间轴（瀑布图）
   - Tags / Process / Logs 标签页
   - 关键路径分析：找出最慢 span

3. System Architecture（依赖图）
   - 自动绘制服务依赖关系
   - 圆圈大小 = 请求量，连线 = 调用关系

4. Compare 两条 trace
   - 对比正常 vs 异常 trace 的耗时分布
```

## 实战案例：电商订单链路

```
用户下单 → [nginx] → [gateway] → [order-service] → [payment-service]
                                              ↘ [inventory-service]
                                              ↘ [coupon-service] → [coupon-db]

每条 span 包含：
  service.name: order-service
  operation: POST /api/orders
  tags: http.method=POST, http.status_code=200, user.id=12345
  duration: 850ms

故障排查：
  1. 登录 jaeger-ui:16686
  2. service=order-service, minDuration=2s, lookback=1h
  3. 找到慢 trace → 看瀑布图 → 发现 payment-service span 占 1.8s
  4. 点 payment-service span → 看 tags（payment.channel=stripe）
  5. 结论：stripe 通道慢，切换到备用通道
```

## Jaeger vs Zipkin vs Tempo

| 维度 | Jaeger | Zipkin | Tempo |
|---|---|---|---|
| 出品 | Uber（CNCF 毕业） | Twitter（CNCF 退役）| Grafana Labs |
| 存储 | ES / Cassandra / Kafka | ES / Cassandra / MySQL | S3 / GCS（廉价） |
| 协议 | OTLP / Zipkin / Jaeger native | Zipkin | OTLP / Jaeger / Zipkin |
| 采样 | 多种策略 | 概率采样 | 依赖 collector |
| 查询 | 自带 UI | 自带 UI | 依赖 Grafana |
| 适用 | 大规模生产 | 中小规模 / 旧项目 | 已有 Grafana 栈 |

## 一句话总结

> **Jaeger = Uber 出品 + CNCF 毕业 + 协议兼容 OTLP**。**架构四层：Client → Agent → Collector → Storage**。**采样策略：概率 / 速率限制 / 远程 / tail-based**。**新项目首选 Jaeger + OpenTelemetry，老项目兼容 Zipkin**。

---

## 关联章节

- [Tracing 基础](../06-tracing/concepts.md) — Trace/Span/Context
- [OpenTelemetry](../02-opentelemetry/overview.md) — 现代 tracing 标准
- [Tempo](../06-tracing/tempo.md) — Grafana 生态的轻量 tracing
- [Zipkin](../06-tracing/zipkin.md) — 旧项目兼容
- [微服务全链路追踪](../11-scenarios/microservice-trace.md) — 实战架构

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
