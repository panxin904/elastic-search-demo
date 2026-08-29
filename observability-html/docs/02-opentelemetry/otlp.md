---
title: OTLP 协议
date: 2026-08-15  # date-auto-injected
description: OpenTelemetry Line Protocol / gRPC + HTTP
---

# OTLP 协议

> **TL;DR**：OTLP（OpenTelemetry Line Protocol）= **OpenTelemetry 的标准数据传输协议**。**两种传输：gRPC（推荐，高吞吐）+ HTTP/Protobuf（兼容 HTTP）**。**数据模型：Resource + Scope + Signal（Span/Metric/Log）**。**所有 OTel 生态（Collector / Jaeger / Tempo）都通过 OTLP 互通**。

## 一句话定义

```
OTLP = OpenTelemetry Protocol
     = 三大信号（Trace / Metric / Log）的统一传输协议
     = 基于 Protocol Buffers（v1）
     = 两种传输：gRPC（4317）/ HTTP（4318）
     = 数据模型：Resource + InstrumentationScope + Signal
```

## 数据模型

```protobuf
message ExportTraceServiceRequest {
  repeated ResourceSpans resource_spans = 1;
}

message ResourceSpans {
  Resource resource = 1;                      // 服务标识
  repeated ScopeSpans scope_spans = 2;        // instrumentation scope
  string schema_url = 3;
}

message ScopeSpans {
  InstrumentationScope scope = 1;
  repeated Span spans = 2;
  string schema_url = 3;
}

message Span {
  bytes trace_id = 1;
  bytes span_id = 2;
  string name = 3;
  uint32 kind = 4;
  fixed64 start_time_unix_nano = 5;
  fixed64 end_time_unix_nano = 6;
  map<string, KeyValue> attributes = 7;
  // ... events, links, status
}
```

## gRPC 传输

```yaml
# OpenTelemetry Collector receiver
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
        max_recv_msg_size_mib: 16
        max_concurrent_streams: 100
        tls:                       # 可选 TLS
          cert_file: /etc/tls/cert.pem
          key_file: /etc/tls/key.pem
```

## HTTP/Protobuf 传输

```yaml
receivers:
  otlp:
    protocols:
      http:
        endpoint: 0.0.0.0:4318
        max_request_size: 16mb
        # 不需要 TLS 也能用（Nginx 加 TLS 即可）
```

## 客户端配置

```bash
# Java Agent
-Dotel.exporter.otlp.protocol=grpc              # 默认 grpc
-Dotel.exporter.otlp.protocol=http/protobuf     # 改 HTTP
-Dotel.exporter.otlp.endpoint=http://collector:4317
-Dotel.exporter.otlp.headers=api-key=xxx

# Go
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317

# Python
os.environ["OTEL_EXPORTER_OTLP_PROTOCOL"] = "grpc"
```

## 数据压缩

```yaml
# gRPC 默认带压缩，可指定
receivers:
  otlp:
    protocols:
      grpc:
        compression: gzip
```

## gRPC vs HTTP 选型

| 维度 | gRPC | HTTP/Protobuf |
|------|------|---------------|
| 端口 | 4317 | 4318 |
| 吞吐 | 高（HTTP/2 多路复用 + 二进制） | 中（HTTP/1.1 串行） |
| 延迟 | 低（连接复用） | 较高 |
| 穿透防火墙 | 需放行非 443/80 | 易（看似普通 HTTP） |
| 浏览器支持 | ❌ 不支持 | ✅ 支持（fetch / beacon） |
| TLS | 可选 | 推荐（走标准 HTTPS） |
| 适用场景 | 服务端 → 服务端 | 浏览器 → 服务端 |

## 实战：gRPC 路由到 Tempo / Jaeger

```yaml
# OpenTelemetry Collector 配置
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
        max_recv_msg_size_mib: 16   # 大 span 调大到 64

processors:
  batch:
    timeout: 5s
    send_batch_size: 1024

exporters:
  # Trace → Tempo（OTLP）
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true

  # Trace → Jaeger（OTLP gRPC，Jaeger 1.35+ 支持）
  otlp/jaeger:
    endpoint: jaeger-collector:4317

  # Metric → Prometheus
  prometheus:
    endpoint: 0.0.0.0:8889

  # Log → Loki
  loki:
    endpoint: http://loki:3100/loki/api/v1/push

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/tempo, otlp/jaeger]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [loki]
```

## 故障排查

| 症状 | 排查 |
|------|------|
| Collector 收不到数据 | 检查防火墙 / 网络：gRPC 需要 4317；HTTP 需要 4318 |
| Span 数据乱码 | 检查 Protobuf 版本兼容性（v1 vs v0） |
| Metric 时间戳为 0 | 客户端时钟漂移，开启 NTP |
| 内存暴涨 | `max_recv_msg_size_mib` 调小 + batch timeout 调短 |

## 一句话总结

> **OTLP = OTel 协议标准**。**两种传输：gRPC（4317，推荐）/ HTTP（4318）**。**数据模型：Resource + Scope + Signal**。**所有 OTel 生态都通过 OTLP 互通**。

---

## 关联章节

- [SDK](../02-opentelemetry/sdk.md)
- [Collector](../02-opentelemetry/collector.md)
- [OpenTelemetry 概览](../02-opentelemetry/overview.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
