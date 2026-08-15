---
title: OpenTelemetry SDK
description: 编程语言 SDK / 上下文传播 / 资源属性
---

# OpenTelemetry SDK

> **TL;DR**：OpenTelemetry SDK = 各语言的**埋点库**。**核心 API：Tracer / Meter / Logger**。**关键能力：上下文传播（W3C Trace Context）+ 自动埋点 + 导出器（OTLP）**。**选语言对应 SDK：Java / Go / Python / Node.js / Rust / .NET**。

## 一句话定义

```
OpenTelemetry SDK = 各语言的官方埋点库
                 = API（接口）+ SDK（实现）+ Instrumentation（埋点）
                 = 三大信号：Trace / Metric / Log
                 = 数据通过 OTLP 协议导出
```

## API 三件套

```java
// 1. Tracer：分布式追踪
Tracer tracer = openTelemetry.getTracer("my-service");
Span span = tracer.spanBuilder("processOrder").startSpan();
try (Scope scope = span.makeCurrent()) {
    // 业务逻辑
    span.setAttribute("order.id", "ORD-001");
} finally {
    span.end();
}

// 2. Meter：指标
Meter meter = openTelemetry.getMeter("my-service");
Counter<Long> counter = meter.counterBuilder("orders.processed").build();
counter.add(1, Attributes.of(AttributeKey.stringKey("status"), "success"));

// 3. Logger：日志
Logger logger = openTelemetry.getLogsBridge().get("my-service");
logger.log("Order processed", Attributes.of(...));
```

## 自动埋点

```bash
# Java：一行 jvm 参数搞定
java -javaagent:opentelemetry-javaagent.jar      -Dotel.service.name=order-service      -Dotel.exporter.otlp.endpoint=http://otel-collector:4317      -jar app.jar
# 自动埋点：HTTP server/client、JDBC、Kafka、Redis、gRPC、JMS
```

## 资源属性（Resource）

```bash
# 资源 = 服务的"身份证"
# 所有 span/metric/log 都自动带上这些属性

otel.service.name=order-service
otel.service.version=2.3.0
otel.deployment.environment=prod
otel.resource.attributes=service.namespace=ecommerce,team=backend
```

## 上下文传播

```
HTTP W3C Trace Context：
  Headers: traceparent / tracestate
  traceparent: 00-<trace-id>-<parent-span-id>-<flags>
  
跨进程：HTTP client → 提取 traceparent → 注入到 outbound 请求
跨线程：Span.current().makeCurrent() 后子线程继承
跨队列：Kafka header / RabbitMQ properties / Redis 序列化
```

## 多语言 SDK 选型

| 语言 | 包名 | 自动埋点 | 性能开销 |
|------|------|---------|---------|
| Java | `opentelemetry-java` + `opentelemetry-javaagent` | ⭐⭐⭐⭐⭐ | 3-8% |
| Go | `go.opentelemetry.io/otel` | ⭐⭐⭐ | 1-3% |
| Python | `opentelemetry-python` + `opentelemetry-instrumentation` | ⭐⭐⭐ | 5-15% |
| Node.js | `@opentelemetry/sdk-node` + `@opentelemetry/auto-instrumentations-node` | ⭐⭐⭐ | 3-8% |
| .NET | `OpenTelemetry.Extensions.Hosting` + `OpenTelemetry.AutoInstrumentation` | ⭐⭐⭐⭐ | 3-6% |
| Rust | `opentelemetry-rust` | ⭐⭐ | 1-2% |

> **Java / .NET 自动埋点最成熟**（javaagent / dotnet tool 模式）；**Go / Rust 偏手动埋点**（零开销，但需要写代码）；**Python / Node 自动埋点丰富但开销较大**。

## 实战：电商订单服务 SDK 初始化

```java
// 1. pom.xml 加依赖
// <dependency>
//   <groupId>io.opentelemetry</groupId>
//   <artifactId>opentelemetry-api</artifactId>
//   <version>1.42.0</version>
// </dependency>

// 2. 启动类初始化 SDK（Spring Boot 启动钩子）
@Configuration
public class OtelConfig {
    @Bean
    public OpenTelemetry openTelemetry() {
        Resource resource = Resource.getDefault().merge(
            Resource.create(Attributes.builder()
                .put(ServiceAttributes.SERVICE_NAME, "order-service")
                .put(ServiceAttributes.SERVICE_VERSION, "2.3.0")
                .put(stringKey("deployment.environment"), "prod")
                .build()));

        SdkTracerProvider tracerProvider = SdkTracerProvider.builder()
            .addSpanProcessor(BatchSpanProcessor.builder(
                OtlpGrpcSpanExporter.builder()
                    .setEndpoint("http://otel-collector:4317")
                    .build())
                .setScheduleDelay(Duration.ofSeconds(2))
                .build())
            .setResource(resource)
            .build();

        return OpenTelemetrySdk.builder()
            .setTracerProvider(tracerProvider)
            .setPropagators(ContextPropagators.create(
                W3CTraceContextPropagator.getInstance()))
            .buildAndRegisterGlobal();
    }
}
```

## 一句话总结

> **OTel SDK = Tracer + Meter + Logger 三件套**。**Java goauto-instrumentation 用 javaagent 一行命令搞定**。**上下文传播靠 W3C Trace Context header**。

---

## 关联章节

- [OpenTelemetry 概览](../02-opentelemetry/overview.md)
- [OTLP 协议](../02-opentelemetry/otlp.md)
- [自动埋点](../02-opentelemetry/auto-instrumentation.md)
- [Collector](../02-opentelemetry/collector.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
