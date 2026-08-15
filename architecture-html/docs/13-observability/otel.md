---
title: OpenTelemetry
---
# OpenTelemetry（OTel）

## 1. 是什么

**OTel = OpenTracing + OpenCensus**（2021 合并），CNCF 项目。
**统一的可观测性标准**：
- 一次 instrumentation
- 多语言 SDK（Java/Go/Node/Python/Rust/...）
- 多个后端导出（Jaeger / Prometheus / Tempo / Zipkin / Datadog / NewRelic / 商用）
- 统一数据模型（Trace / Span / Metric / Log）

## 2. 三大支柱

| | OTel API | 后端 |
|--|----------|------|
| **Tracing** | OpenTelemetry API | Jaeger / Tempo / Zipkin |
| **Metrics** | OpenTelemetry SDK | Prometheus / Datadog / NewRelic |
| **Logs** | OpenTelemetry Logs | Loki / ES / Splunk |

**统一**：同一份 Span 里同时携带 traceId / metric / log = 完美关联。

## 3. 实战：Spring Boot 集成

```xml
<dependency>
  <groupId>io.opentelemetry.instrumentation</groupId>
  <artifactId>opentelemetry-spring-boot-starter</artifactId>
</dependency>
```

```yaml
# application.yml
otel:
  service:
    name: myapp
  traces:
    exporter: otlp
  metrics:
    exporter: otlp
  logs:
    exporter: otlp
  exporter:
    otlp:
      endpoint: http://otel-collector:4317
```

**零代码**：自动注入 Trace + Metric + Log 采集。

## 4. 手动埋点

```java
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;

@Service
public class OrderService {
  private final Tracer tracer = OpenTelemetry.getGlobalTracer("order-service");

  public void placeOrder(OrderDTO dto) {
    Span span = tracer.spanBuilder("placeOrder")
      .setAttribute("order.amount", dto.getAmount())
      .setSpanKind(SpanKind.INTERNAL)
      .startSpan();
    try (Scope scope = span.makeCurrent()) {
      orderRepo.create(dto);
      span.addEvent("order.created");
    } catch (Exception e) {
      span.recordException(e);
      throw e;
    } finally {
      span.end();
    }
  }
}
```

## 5. OpenTelemetry Collector

**OTel 后端统一代理**：
```
App SDK → OTLP (4317/4318) → OTel Collector → 多种后端
                                  ├→ Jaeger (Trace)
                                  ├→ Prometheus (Metric)
                                  ├→ Loki (Log)
                                  └→ Datadog (All)
```

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols: { grpc: { endpoint: 0.0.0.0:4317 } }
processors:
  batch: { timeout: 10s }
exporters:
  prometheus:
    endpoint: 0.0.0.0:8889
  otlp/jaeger:
    endpoint: jaeger:4317
service:
  pipelines:
    traces: { receivers: [otlp], processors: [batch], exporters: [otlp/jaeger] }
    metrics: { receivers: [otlp], processors: [batch], exporters: [prometheus] }
```

```bash
docker run -d --name otel-collector   -p 4317:4317 -p 8889:8889   -v $PWD/otel-collector-config.yaml:/etc/otelcol/config.yaml   otel/opentelemetry-collector-contrib
```

## 6. TraceContext 跨服务传播

```
服务 A                           服务 B
span_id=span-A   trace_id=tid  span_id=span-B
      ↓ HTTP Header                ↑
   traceparent: 00-{tid}-{span-A}-01
   tracestate: myapp=value
```

**OTel 自动注入 `traceparent` header**，下游服务提取 → 完整 trace。

## 7. Baggage（跨服务传值）

```java
// 服务 A
Span.current().setBaggage("userId", "12345");

// 服务 B（通过 HTTP header 自动传递）
Baggage.current().getEntryValue("userId");
```

应用层传"用户 ID"等元数据，无需改业务代码。

## 8. 实战：OpenTelemetry Collector 部署

```bash
# 部署到 k8s
kubectl apply -f https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.91.0/manifests/collector-metrics-service.yaml

# 或 DaemonSet（每 Node 一个）
kubectl apply -f https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.91.0/manifests/collector-daemonset.yaml
```

## 9. OpenTelemetry vs 商业方案

| | OTel | Datadog | NewRelic | Dynatrace |
|--|------|---------|---------|-----------|
| 开源 | ✅ | ❌ | ❌ | ❌ |
| 自托管 | ✅ | ❌ | ❌ | 部分 |
| 厂商绑定 | ❌ | ✅ | ✅ | ✅ |
| 自动 instrumentation | ✅（APM） | ✅ | ✅ | ✅ |
| 成本 | 低 | 高 | 高 | 高 |

**建议**：中小项目用 OTel + Grafana + Prometheus + Tempo + Loki（开源栈）；大企业可考虑 Datadog。

## 10. 实战选型

| 场景 | 选 |
|------|-----|
| 多语言 + 不想绑定 | OTel + 开源后端 |
| Java Spring 生态 | Micrometer + Spring Actuator |
| Go / Rust 性能敏感 | OTel native SDK |
| 大规模（万级 Pod） | OTel Collector + Jaeger / Tempo + Prometheus + Grafana |
| 简单 / 单语言 | SLF4J + Loki / ELK |

## 11. 关键实践

1. **统一 traceId**：每条日志带 traceId（自动）
2. **SLO 驱动告警**：不是"磁盘满了才告警"
3. **Sampling**：高吞吐场景采样（1-10%）
4. **RED + USE**：必加指标
5. **避免过度采集**：每条 metric 都有 storage 成本

## 🔗 下一步
- [Metrics/Tracing/Logging](/13-observability/three-pillars)
- [Saga / Bulkhead](/12-microservice-patterns/saga)
