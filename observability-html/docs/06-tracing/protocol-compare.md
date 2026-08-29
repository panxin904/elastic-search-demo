---
title: Tracing 协议对比
date: 2026-08-15  # date-auto-injected
description: OTLP / Jaeger / Zipkin / OpenTracing
---

# Tracing 协议对比

> **TL;DR**：**OpenTelemetry Protocol (OTLP) 是行业标准**，**Jaeger 原生协议 / Zipkin v2 是历史遗留**。**实战：OTel SDK → OTLP → Collector → 后端（Jaeger/Tempo/Zipkin 都支持 OTLP）**。**新项目一律用 OTLP**。

## 一句话定义

```
Tracing 协议 = 跨进程传递 trace 数据的格式
            = 客户端 SDK → 后端存储
            = 三种主流：OTLP / Jaeger / Zipkin
            = OTLP 统一所有协议（OpenTelemetry 标准）
```

## 协议矩阵

| 协议 | 出品 | 数据格式 | 端口（gRPC） | 现状 |
|---|---|---|---|---|
| **OTLP** | OpenTelemetry | Protobuf | 4317 | 行业标准（2024+） |
| **Jaeger** | Uber | Thrift / Protobuf | 14250 | 历史主流，逐步迁移 OTLP |
| **Zipkin v2** | Twitter | JSON / Thrift | 9411 | 老项目，CNCF 退役 |
| **OpenTracing** | CNCF | （不是协议，是 API 标准）| - | 已被 OTel 取代 |

## OTLP（OpenTelemetry Protocol）

```protobuf
// OTLP 标准格式（v1）
message Span {
  bytes trace_id = 1;            // 16 bytes
  bytes span_id = 2;             // 8 bytes
  bytes parent_span_id = 4;
  string name = 3;
  fixed64 start_time_unix_nano = 5;
  fixed64 end_time_unix_nano = 6;
  map<string, KeyValue> attributes = 7;
  repeated Event events = 8;
  repeated Link links = 9;
  Status status = 15;
}
```

## Jaeger Thrift 协议

```thrift
// Jaeger 原生协议（Thrift IDL）
struct Span {
  1: required string operationName
  2: required list<SpanRef> references
  3: required i64 startTime
  4: required i64 duration
  5: required list<Log> logs
  6: required list<KeyValue> tags
  7: required SpanContext spanContext
}

struct SpanContext {
  1: required i64 trace_id
  2: required i64 span_id
  3: required i64 parent_id
  4: required i32 flags
}
```

## Zipkin v2 JSON

```json
[
  {
    "id": "span_id",
    "traceId": "trace_id_hex",
    "parentId": "parent_span_id",
    "name": "operation_name",
    "timestamp": 1723219200000,
    "duration": 12345,
    "kind": "CLIENT",
    "tags": {
      "http.method": "GET",
      "http.status_code": "200"
    },
    "annotations": [
      { "timestamp": 1723219200000, "value": "annotation_text" }
    ]
  }
]
```

## 协议互通

```yaml
# OpenTelemetry Collector：协议转换的"瑞士军刀"
receivers:
  otlp:           # 接收 OTLP
    protocols: { grpc: { endpoint: 0.0.0.0:4317 } }
  jaeger:         # 接收 Jaeger
    protocols: { grpc: { endpoint: 0.0.0.0:14250 } }
  zipkin:         # 接收 Zipkin
    protocols: { endpoint: 0.0.0.0:9411 }   # HTTP

exporters:
  otlp/jaeger:    # 导出 OTLP（到 Jaeger / Tempo）
    endpoint: jaeger:4317
  zipkin:         # 导出 Zipkin v2
    endpoint: http://zipkin:9411/api/v2/spans

service:
  pipelines:
    traces:
      receivers: [otlp, jaeger, zipkin]   # 都接收
      processors: [batch]
      exporters: [otlp/jaeger]            # 统一导出
```

## 一句话总结

> **OTLP 是行业标准**。**新项目一律用 OTLP**。**老项目用 Collector 转换协议**。**已退役的 OpenTracing / Zipkin 不再新用**。

---

## 关联章节

- [OTel 概览](../02-opentelemetry/overview.md)
- [OTLP 协议](../02-opentelemetry/otlp.md)
- [Jaeger](../06-tracing/jaeger.md)
- [Tempo](../06-tracing/tempo.md)
- [Zipkin](../06-tracing/zipkin.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
