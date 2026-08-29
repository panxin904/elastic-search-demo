---
title: Zipkin 链路追踪
date: 2026-08-15  # date-auto-injected
description: Twitter 2012 开源 / 分布式 tracing 鼻祖
---

# Zipkin 链路追踪

> **TL;DR**：Zipkin = **Twitter 2012 开源的分布式追踪系统（受 Google Dapper 启发）**。**Jaeger 的"前辈"**，**目前是 CNCF 退役项目**。**架构：Client → Collector → Storage（ES/Cassandra/MySQL）→ Query UI**。**新项目首选 Jaeger / Tempo，Zipkin 用于已有项目维护**。

## 一句话定义

```
Zipkin = Twitter 2012 开源 tracing
      = Google Dapper 论文的工业实现
      = 受 OpenTracing 标准影响（被 OpenTelemetry 取代）
      = 现状：CNCF 退役项目（archived），不建议新项目采用
      = 已有项目兼容：OTel SDK 支持 Zipkin 协议输出
```

## 与 Jaeger / Tempo 对比

| 维度 | Zipkin | Jaeger | Tempo |
|---|---|---|---|
| 出品 | Twitter | Uber | Grafana Labs |
| 状态 | CNCF 退役 | CNCF 毕业 | 活跃 |
| 存储 | ES / Cassandra / MySQL | ES / Cassandra / Kafka | S3 / GCS |
| 协议 | Zipkin | OTLP / Jaeger | OTLP / Jaeger / Zipkin |
| UI | 自带 | 自带 | 依赖 Grafana |
| 客户端库 | Brave (Java) | jaeger-client | 任意 OTel SDK |
| 适用 | 老项目维护 | 大型生产 | 已有 Grafana |

## 架构

```
┌─────────────┐  HTTP/JSON  ┌─────────────┐  store   ┌──────────┐
│ Zipkin      │ ───────────▶│ Collector   │ ────────▶│ Storage  │
│ client      │  Thrift     │             │          │ ES/Cass  │
│ (Brave)     │             │             │          └──────────┘
└─────────────┘             └──────┬──────┘                 │
                                  │ query                   ▼
                                  ▼                  ┌──────────┐
                            ┌─────────────┐          │ Query UI │
                            │ Zipkin UI   │          └──────────┘
                            └─────────────┘
```

## 部署

```bash
# Docker 启动
docker run -d --name zipkin   -p 9411:9411   -e STORAGE_TYPE=elasticsearch   -e ES_HOSTS=elasticsearch:9200   openzipkin/zipkin:latest
```

```yaml
# docker-compose
services:
  zipkin:
    image: openzipkin/zipkin:latest
    environment:
      - STORAGE_TYPE=elasticsearch
      - ES_HOSTS=elasticsearch:9200
      - ES_USERNAME=zipkin
      - ES_PASSWORD=xxx
    ports:
      - "9411:9411"
```

## Java 客户端（Brave）

```xml
<!-- Maven 依赖 -->
<dependency>
    <groupId>io.zipkin.brave</groupId>
    <artifactId>brave</artifactId>
</dependency>
<dependency>
    <groupId>io.zipkin.brave</groupId>
    <artifactId>brave-context-slf4j</artifactId>
</dependency>
<dependency>
    <groupId>io.zipkin.reporter2</groupId>
    <artifactId>zipkin-reporter-brave</artifactId>
</dependency>
```

```java
// 配置 Brave
Tracing.newBuilder()
    .localServiceName("order-service")
    .currentTraceContext(ThreadLocalCurrentTraceContext.newInstance())
    .spanReporter(AsyncZipkinSpanReporter.create(
        URLConnectionClient.create(new URL("http://zipkin:9411/api/v2/spans"))
    ))
    .build();

// 业务代码
Tracer tracer = tracing.tracer();
Span span = tracer.newTrace().name("processOrder").start();
try {
    // 业务
} finally {
    span.finish();
}
```

## OpenTelemetry 桥接

```bash
# OTel → Zipkin（推荐新项目用 OTel，输出 Zipkin 协议）
java -javaagent:./opentelemetry-javaagent.jar      -Dotel.service.name=order-service      -Dotel.exporter.zipkin.endpoint=http://zipkin:9411/api/v2/spans      -jar order-service.jar
```

```yaml
# Collector 配置：OTLP → Zipkin
exporters:
  zipkin:
    endpoint: http://zipkin:9411/api/v2/spans

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [zipkin]
```

## Zipkin UI 核心功能

```
1. Search 搜索
   - service / span name / annotations / minDuration / maxDuration
   - 时间范围 + Lookback

2. Trace 详情
   - Span 列表（瀑布图）
   - Span 标签 + Annotations

3. Dependencies
   - 服务依赖图（自动生成）

4. Compare
   - 对比多条 trace 的耗时分布
```

## 一句话总结

> **Zipkin = tracing 鼻祖 / 现已 CNCF 退役**。**老项目维护用 Zipkin，新项目直接用 OpenTelemetry → Jaeger/Tempo**。

---

## 关联章节

- [Jaeger](../06-tracing/jaeger.md)
- [Tempo](../06-tracing/tempo.md)
- [Tracing 基础](../06-tracing/concepts.md)
- [协议对比](../06-tracing/protocol-compare.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
