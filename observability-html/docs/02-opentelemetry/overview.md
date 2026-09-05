---
title: OpenTelemetry 概览
date: 2026-08-15  # date-auto-injected
description: OTel 是什么 / 与 OpenTracing/OpenCensus 关系
---

# OpenTelemetry 全景

> **TL;DR**：OpenTelemetry（OTel）是 CNCF 顶级项目，**统一了 Metrics / Logs / Traces 三类信号的采集与传输**。它不是单一工具，而是一套**规范 + SDK + 协议 + Collector** 的完整生态。**2026 年新项目，OTel 已是默认起点**。

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">OpenTelemetry 数据管道</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">Instrumentation → SDK → Collector → Backend</text>

  <!-- Apps (源) -->
  <rect class="at-hover-card" x="30" y="100" width="100" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="80" y="123" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">App A</text>
  <text x="80" y="140" text-anchor="middle" font-size="9" fill="#475569">SDK + Agent</text>

  <rect class="at-hover-card" x="30" y="160" width="100" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="80" y="183" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">App B</text>
  <text x="80" y="200" text-anchor="middle" font-size="9" fill="#475569">Auto-Instr</text>

  <rect class="at-hover-card" x="30" y="220" width="100" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="80" y="243" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">App C</text>
  <text x="80" y="260" text-anchor="middle" font-size="9" fill="#475569">Sidecar eBPF</text>

  <!-- OTLP -->
  <rect class="at-hover-card" x="170" y="120" width="120" height="120" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="230" y="143" text-anchor="middle" font-size="12" font-weight="700" fill="#92400e">OTLP</text>
  <text x="230" y="161" text-anchor="middle" font-size="10" fill="#475569">gRPC / HTTP</text>
  <text x="230" y="183" text-anchor="middle" font-size="10" fill="#475569">Trace + Metric</text>
  <text x="230" y="200" text-anchor="middle" font-size="10" fill="#475569">+ Log</text>
  <text x="230" y="222" text-anchor="middle" font-size="9" fill="#92400e" font-style="italic">protobuf / JSON</text>

  <!-- Collector -->
  <rect class="at-hover-card" x="320" y="100" width="120" height="160" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="2"/>
  <text x="380" y="123" text-anchor="middle" font-size="13" font-weight="700" fill="#047857">Collector</text>
  <text x="380" y="145" text-anchor="middle" font-size="10" fill="#475569">Receivers</text>
  <text x="380" y="163" text-anchor="middle" font-size="10" fill="#475569">Processors</text>
  <text x="380" y="181" text-anchor="middle" font-size="10" fill="#475569">Exporters</text>
  <text x="380" y="205" text-anchor="middle" font-size="9" fill="#475569" font-style="italic">批处理 / 采样</text>
  <text x="380" y="223" text-anchor="middle" font-size="9" fill="#475569" font-style="italic">路由 / 转换</text>
  <text x="380" y="248" text-anchor="middle" font-size="9" fill="#10b981" font-weight="700">FAN-OUT</text>

  <!-- Backends -->
  <rect class="at-hover-card" x="470" y="100" width="100" height="40" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="520" y="118" text-anchor="middle" font-size="10" font-weight="700" fill="#5b21b6">Jaeger</text>
  <text x="520" y="133" text-anchor="middle" font-size="9" fill="#475569">Trace</text>

  <rect class="at-hover-card" x="470" y="150" width="100" height="40" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="520" y="168" text-anchor="middle" font-size="10" font-weight="700" fill="#5b21b6">Prometheus</text>
  <text x="520" y="183" text-anchor="middle" font-size="9" fill="#475569">Metric</text>

  <rect class="at-hover-card" x="470" y="200" width="100" height="40" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="520" y="218" text-anchor="middle" font-size="10" font-weight="700" fill="#5b21b6">Loki / ES</text>
  <text x="520" y="233" text-anchor="middle" font-size="9" fill="#475569">Log</text>

  <rect class="at-hover-card" x="470" y="250" width="100" height="40" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="520" y="268" text-anchor="middle" font-size="10" font-weight="700" fill="#5b21b6">Tempo / S3</text>
  <text x="520" y="283" text-anchor="middle" font-size="9" fill="#475569">Trace 归档</text>

  <!-- 箭头 -->
  <line x1="130" y1="125" x2="170" y2="160" stroke="#3b82f6" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="130" y1="185" x2="170" y2="180" stroke="#3b82f6" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="130" y1="245" x2="170" y2="200" stroke="#3b82f6" stroke-width="1.5" marker-end="url(#arr)"/>

  <line x1="290" y1="180" x2="320" y2="180" stroke="#f59e0b" stroke-width="2" marker-end="url(#arr)"/>

  <line x1="440" y1="140" x2="470" y2="120" stroke="#10b981" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="440" y1="170" x2="470" y2="170" stroke="#10b981" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="440" y1="200" x2="470" y2="220" stroke="#10b981" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="440" y1="230" x2="470" y2="270" stroke="#10b981" stroke-width="1.5" marker-end="url(#arr)"/>

  <!-- 关键点 -->
  <rect x="30" y="295" width="540" height="170" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="300" y="318" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">关键设计点</text>

  <text x="50" y="343" font-size="11" font-weight="600" fill="#1e293b">① 三种信号统一</text>
  <text x="50" y="361" font-size="10" fill="#475569">· Trace / Metric / Log 通过 OTLP 同协议</text>
  <text x="50" y="376" font-size="10" fill="#475569">· Context Propagation（W3C TraceContext）</text>

  <text x="320" y="343" font-size="11" font-weight="600" fill="#1e293b">② Collector 角色</text>
  <text x="320" y="361" font-size="10" fill="#475569">· Agent（每节点）vs Gateway（中心）</text>
  <text x="320" y="376" font-size="10" fill="#475569">· 采样、过滤、协议转换、缓冲重试</text>

  <text x="50" y="400" font-size="11" font-weight="600" fill="#1e293b">③ 部署模式</text>
  <text x="50" y="418" font-size="10" fill="#475569">· 直接上报后端（简单）</text>
  <text x="50" y="433" font-size="10" fill="#475569">· 经 Collector 中转（推荐）</text>

  <text x="320" y="400" font-size="11" font-weight="600" fill="#1e293b">④ 与厂商解耦</text>
  <text x="320" y="418" font-size="10" fill="#475569">· 后端可换：Jaeger → Tempo / SigNoz</text>
  <text x="320" y="433" font-size="10" fill="#475569">· 数据模型与协议标准化，避免锁定</text>
</svg>

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
