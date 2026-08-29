---
title: OpenTelemetry 概览
description: OTel 是什么 / 与 OpenTracing/OpenCensus 关系
---

# OpenTelemetry 全景

> **TL;DR**：OpenTelemetry（OTel）是 CNCF 顶级项目，**统一了 Metrics / Logs / Traces 三类信号的采集与传输**。它不是单一工具，而是一套**规范 + SDK + 协议 + Collector** 的完整生态。**2026 年新项目，OTel 已是默认起点**。

## 一句话定义

```
OpenTelemetry = 供应商中立的可观测性数据采集规范与工具集
```

## 三大前身：为什么 OTel 存在

```
2010-2015：百花齐放
  ├─ Zipkin（Twitter）
  ├─ Jaeger（Uber）
  ├─ Pinpoint（Naver）
  ├─ LightStep Tracing
  └─ AppDynamics / Dynatrace（商业）

2015-2019：两大阵营成立
  ├─ OpenTracing（CNCF，Uber 主导）  → 仅 Traces
  └─ OpenCensus（Google 主导）        → Metrics + Traces

2019：合并
  └─ OpenTelemetry（CNCF，OpenTracing + OpenCensus 合并）
       目标：统一三大信号，不绑定任何后端

2021：OTel 1.0 发布（Traces）
2022：OTel 1.0 Metrics 稳定
2023-2026：Logs 稳定 + 协议 OTLP 成为事实标准
```

> **为什么合并？** 因为 Traces / Metrics / Logs 各自一套规范不互通，应用要装多个 agent。OTel 把它们统一，**一次埋点，三类信号都采集**。

## OTel 的四层架构

```
┌──────────────────────────────────────────┐
│  1. API（应用代码接口）                   │
│     - 业务代码调用 OTel API              │
│     - 与后端解耦（可换 Jaeger/Tempo）     │
├──────────────────────────────────────────┤
│  2. SDK（语言实现）                       │
│     - Java/Go/Python/Node/Rust/.NET/... │
│     - 负责采样、上下文传播、批处理        │
├──────────────────────────────────────────┤
│  3. OTLP（OpenTelemetry Protocol）        │
│     - 数据序列化（gRPC + HTTP/protobuf）  │
│     - 应用 → Collector / 应用 → 后端     │
├──────────────────────────────────────────┤
│  4. Collector（数据管道）                 │
│     - 接收 / 处理 / 转换 / 导出          │
│     - 部署模式：agent / gateway / 自托管  │
└──────────────────────────────────────────┘
```

## OTel 能做什么

| 信号 | OTel 状态 | 说明 |
|---|---|---|
| **Traces** | 1.0 稳定 | Distributed tracing 标准 |
| **Metrics** | 1.0 稳定 | Counter / Gauge / Histogram 完整 |
| **Logs** | 1.0 稳定（2023） | 但生态成熟度不如前两者 |
| **Profiles** | 实验中 | eBPF profiling 实验 |

## OTel 与 OpenTracing / OpenCensus 的对比

| 维度 | OpenTracing | OpenCensus | OpenTelemetry |
|---|---|---|---|
| 时代 | 2016-2019 | 2017-2020 | 2019-至今 |
| 信号范围 | 仅 Traces | Metrics + Traces | Metrics + Logs + Traces |
| 语言支持 | 6 | 4 | 11+ |
| 维护者 | Uber | Google | 50+ 公司社区 |
| 现状 | **已归档**，并入 OTel | **已归档**，并入 OTel | 活跃 |

> **新项目 100% 选 OTel**，不要选 OpenTracing / OpenCensus。

## OTel 与各种后端的关系

```
OTel SDK/Collector ──OTLP──→ 后端
                              ├─ Jaeger（原生支持）
                              ├─ Tempo（原生支持）
                              ├─ Prometheus（通过 otlp2prometheus converter）
                              ├─ Loki（通过 otlp2loki 或直接 gELF）
                              ├─ Datadog（商业）
                              ├─ Honeycomb（商业）
                              └─ 任何自建存储
```

> **OTel 不绑定后端**。换后端只需要改 Collector 的 exporter，应用代码不变。

## 部署模式

### 模式 1：应用直连后端（简单场景）

```
App → OTel SDK → OTLP → Jaeger
```

**优点**：架构简单
**缺点**：应用重启数据丢，水平扩展时连接管理复杂

### 模式 2：应用 → Collector Agent → 后端（推荐）

```
App1 ─┐
App2 ─┤→ OTel Agent (sidecar) ─→ OTel Gateway ─→ Jaeger/Tempo
App3 ─┘
```

**优点**：应用无状态，Collector 处理重试 / 采样 / 批处理
**缺点**：多一层运维

### 模式 3：Gateway 模式（生产环境）

```
App Pod (OTel Agent) → OTel Gateway (集群级) → 后端集群
```

**优点**：集中采样、过滤、配额管理
**缺点**：Gateway 是单点（要做 HA）

## OTel Collector 详解

```
Receivers  →  Processors  →  Exporters
   ↓             ↓              ↓
接收数据     处理/转换        发送到后端
```

**典型配置**：

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 5s
    send_batch_size: 1000

  # 尾部采样：保留错误请求和慢请求
  tail_sampling:
    decision_wait: 10s
    num_traces: 100000
    expected_new_traces_per_sec: 1000
    policies:
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow
        type: latency
        latency: { threshold_ms: 200 }

exporters:
  otlp/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true

  prometheus:
    endpoint: 0.0.0.0:8889

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [tail_sampling, batch]
      exporters: [otlp/jaeger]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
```

## 语义约定（Semantic Conventions）

OTel 标准化了**指标名 / Span 名 / 属性键**的命名规则：

```yaml
# HTTP 服务自动埋点产生的 span
name: "GET /api/orders/{id}"
attributes:
  http.request.method: "GET"
  http.route: "/api/orders/{id}"
  http.response.status_code: 200
  url.path: "/api/orders/12345"
  server.address: "order-service"

# 数据库 span
name: "SELECT orders"
attributes:
  db.system: "postgresql"
  db.statement: "SELECT * FROM orders WHERE id = $1"
  db.name: "shop"
```

> **好处**：不用每个公司自己命名规范，跨语言 / 跨工具通用。

## 实战代码示例（Java）

```java
// 1. 加依赖
// pom.xml: io.opentelemetry:opentelemetry-sdk:1.40.0

// 2. 初始化 OTel
OpenTelemetrySdk sdk = OpenTelemetrySdk.builder()
    .setTracerProvider(
        SdkTracerProvider.builder()
            .addSpanProcessor(SimpleSpanProcessor.create(
                OtlpGrpcSpanExporter.builder()
                    .setEndpoint("http://otel-collector:4317")
                    .build()))
            .setResource(Resource.getDefault().toBuilder()
                .put(SERVICE_NAME, "order-service")
                .build())
            .build())
    .setPropagators(TextMapPropagator.composite(
        W3CTraceContextPropagator.getInstance(),
        BaggagePropagator.getInstance()))
    .buildAndRegisterGlobal();

// 3. 业务代码埋点
Tracer tracer = sdk.getTracer("order-service");
Span span = tracer.spanBuilder("process-order")
    .setAttribute("order.id", "12345")
    .setAttribute("user.id", "u_456")
    .startSpan();
try (Scope scope = span.makeCurrent()) {
    // 业务逻辑
    processOrder();
} catch (Exception e) {
    span.recordException(e);
    span.setStatus(StatusCode.ERROR);
    throw e;
} finally {
    span.end();
}
```

## OTel 生态现状（2026）

### 已成事实标准的部分

- ✅ OTLP 协议（gRPC + HTTP）
- ✅ Traces SDK（Java/Go/Python/Node/...）
- ✅ Metrics SDK
- ✅ Logs SDK
- ✅ W3C Trace Context（context propagation）
- ✅ Semantic Conventions（语义约定）

### 仍在演进的领域

- 🔄 eBPF profiling 集成
- 🔄 Auto-instrumentation 覆盖率（Java 已较全，Node 中等，Python 较弱）
- 🔄 Logs 与 Traces 的关联（OTel Logs v1 已稳定但工具支持还在完善）

## 选型决策

```
新项目？  → 直接用 OTel，不要考虑其他
老项目用 OpenTracing？ → 迁移到 OTel（OpenTracing 已归档）
老项目用 OpenCensus？   → 迁移到 OTel
老项目用 Zipkin/Jaeger SDK 直连？ → 加一层 OTel SDK + Collector，未来换后端容易
```

## 常见误区

### 误区 1：OTel 是 Prometheus 替代品

```
❌ OTel 取代 Prometheus
✅ OTel 是采集层，Prometheus 是存储 + 查询层。两者配合：OTel → OTLP → Prometheus
```

### 误区 2：OTel = 后端

```
❌ OTel 包含存储 / 可视化
✅ OTel 只管采集。存储用 Jaeger/Tempo/Loki/Prometheus，可视化用 Grafana
```

### 误区 3：OTel 部署很简单

```
✅ 简单场景确实简单（agent 模式）
❌ 大规模生产环境 OTel Collector 的资源调优、采样策略、配额管理都不简单
```

### 误区 4：所有语言 OTel 支持一样

```
❌ Java/Go/Python/Node 支持都一样
✅ Java 生态最成熟，Go 次之，Python/Node/.NET 中等，Rust/Elixir/C++ 还在补齐
```

## 一句话总结

> **OpenTelemetry 是 2026 年可观测性的"必选起点"**。
> 新项目直接用 OTel SDK + OTLP + Collector + 后端（J/T/L/P/G）的组合，**别再用各家的私有 SDK 了**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
