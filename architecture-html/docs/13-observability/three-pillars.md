---
title: 三大支柱 Metrics/Tracing/Logging
---
# 可观测性三大支柱

## 1. 三大支柱

| 支柱 | 回答什么问题 | 典型工具 | 数据形式 |
|------|-------------|----------|---------|
| **Metrics** | 系统在做什么 | Prometheus / Grafana | 数值 / 时序 |
| **Tracing** | 请求经过哪些服务 | Jaeger / Zipkin / Tempo | span / trace |
| **Logging** | 发生了什么 | ELK / Loki | 文本 / 结构化 |

## 2. Metrics

### Prometheus 核心

```yaml
# 指标类型
- Counter（计数器）：只增不减（请求数）
- Gauge（仪表）：可增可减（CPU 使用率）
- Histogram（直方图）：分布（请求延迟）
- Summary：分位数（99th percentile）
```

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
scrape_configs:
- job_name: myapp
  static_configs:
  - targets: ['myapp:8080']
```

```java
// Micrometer + Prometheus
Counter.builder("orders_total")
  .tag("status", "ok")
  .register(registry)
  .increment();
```

## 3. Tracing

### 三大支柱中的"因果"

请求经过多个服务，**Tracing 把分散的日志串成完整故事**。

```
User → API → Service A → Service B → DB
       ↓ span_id  ↓ span_id  ↓ span_id
       trace_id=abc123, parent=root, child=span-A
       trace_id=abc123, child-of=span-A
       trace_id=abc123, child-of=span-A
```

**组成**：
- Trace：完整请求链路（树）
- Span：单个服务调用（节点）

### 实战

```java
// OpenTelemetry SDK
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.api.trace.Span;

@Service
public class OrderService {
  private final Tracer tracer;

  public Order createOrder(OrderDTO dto) {
    Span span = tracer.spanBuilder("createOrder").startSpan();
    try (var scope = span.makeCurrent()) {
      span.setAttribute("order.amount", dto.amount);
      // ... 业务逻辑
      return order;
    } finally {
      span.end();
    }
  }
}
```

## 4. Logging

### 结构化日志

```json
{"timestamp":"2024-01-15T10:30:00Z","level":"INFO","traceId":"abc123","spanId":"def","service":"order","msg":"createOrder done","orderId":"12345","amount":99.9,"duration":12}
```

```java
// SLF4J + Logback JSON
log.info("createOrder done",
  kv("orderId", dto.id),
  kv("amount", dto.amount),
  kv("duration", elapsed));
```

### 日志聚合

```
App → Filebeat/Fluentd → Kafka → ES/Loki → Grafana
```

## 5. 三大支柱的关联

```
请求失败
  ↓ Metrics（成功率 50%，异常）
  → Grafana 告警
  ↓
  → Tracing（看具体哪个服务慢）
  → Jaeger UI
  ↓
  → Logging（看错误堆栈）
  → Kibana / Loki
```

**自上而下**：Metrics 报警 → Tracing 定位 → Logging 看详情。

## 6. OpenTelemetry（标准）

CNCF 项目，**统一 SDK / 协议 / 后端**，替代 OpenTracing + OpenCensus。

```java
// OTel SDK（统一 API）
OpenTelemetrySdk sdk = OpenTelemetrySdk.builder()
  .addSpanProcessor(BatchSpanProcessor.builder().build())
  .build();
```

**优势**：一套 SDK export 到多个后端（Jaeger / Tempo / Zipkin / 商用）。

## 7. RED / USE 方法

### RED 指标

```
Rate：每秒请求数（QPS）
Errors：失败率
Duration：响应时间
```

### USE 指标

```
Utilization：资源使用率（CPU / Mem / IO）
Saturation：饱和度（队列长度）
Errors：硬件/系统错误
```

## 8. 实战：Spring Boot 集成

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
<dependency>
  <groupId>io.micrometer</groupId>
  <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
<dependency>
  <groupId>io.opentelemetry</groupId>
  <artifactId>opentelemetry-spring-boot-starter</artifactId>
</dependency>
```

```yaml
# application.yml
management:
  endpoints.web.exposure.include: health,info,metrics,prometheus
  tracing:
    sampling.probability: 0.1
```

自动：Actuator / Micrometer（Prometheus 格式）/ OpenTelemetry。

## 9. 实战：trace_id 关联

```java
// 关键：让日志带 trace_id，方便 Kibana / Grafana 关联
log.info("OrderPlaced",
  kv("traceId", Span.current().getSpanContext().getTraceId()),
  kv("orderId", order.getId()));
```

Grafana / Kibana 中可按 traceId 查询完整请求链路。

## 10. 实战选型

| 场景 | 选 |
|------|-----|
| 中小规模 | Grafana + Prometheus + Loki + Tempo（一套） |
| 大规模 | OpenTelemetry + Jaeger / Tempo + Prometheus + ELK |
| 多语言 | OpenTelemetry SDK（统一） |
| 阿里系 | ARMS / 日志服务（SLS） |
| 国内云 | 阿里云 ARMS / 华为云 APM |

## 11. SLO / SLA / SLI

- **SLI**（Service Level Indicator）：衡量指标（如可用性 = 成功请求 / 总请求）
- **SLO**（Service Level Objective）：目标（如 99.9% 可用性）
- **SLA**（Service Level Agreement）：合同（如未达成赔钱）

```promql
# SLO 评估
sum(rate(http_requests_total{status!~"5.."}[30d]))
/
sum(rate(http_requests_total[30d]))
# ≥ 0.999 (99.9% availability)
```

## 12. 实战 checklist

- [ ] 三支柱齐全（Metrics + Trace + Logs）
- [ ] 统一 traceId 关联
- [ ] 关键告警（SLI 错误 / 延迟 P99 / 资源饱和度）
- [ ] 仪表盘按服务划分
- [ ] OnCall 流程 + Runbook

## 🔗 下一步
- [OpenTelemetry](/13-observability/otel)
- [熔断器三态](/05-circuit-breaker/states)
