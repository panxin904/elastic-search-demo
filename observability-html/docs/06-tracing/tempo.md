---
title: Tempo 链路追踪
description: Grafana Labs 的轻量级 tracing 后端
---

# Tempo 链路追踪

> **TL;DR**：Tempo = **Grafana Labs 2020 开源的 tracing 后端**。**最大特点：依赖对象存储（S3/GCS/本地），不依赖 ES/Cassandra**。**与 Grafana / Loki / Prometheus 天然集成**。**Jaeger / Zipkin / OTLP 协议都支持**。**已有 Grafana 栈首选 Tempo**。

## 一句话定义

```
Tempo = Grafana Labs 开源 tracing 后端
     = 设计：极简单（只存 trace）+ 廉价存储（S3/GCS）
     = 协议：OTLP / Jaeger / Zipkin
     = 查询：依赖 Grafana（无自带 UI）
     = 与 Loki 联动：通过 traceID 跳转日志
```

## 与 Jaeger 对比

| 维度 | Tempo | Jaeger |
|---|---|---|
| 出品 | Grafana Labs | Uber |
| 存储 | S3/GCS/本地 | ES/Cassandra/Kafka |
| UI | 依赖 Grafana | 自带 UI |
| 集成 | Grafana / Loki / Prometheus 天然 | 独立 |
| 成本 | 极低（对象存储） | 中（ES 集群） |
| 协议 | OTLP / Jaeger / Zipkin | OTLP / Jaeger |
| 适用 | 已有 Grafana 栈 | 独立 tracing 系统 |

## 架构

```
┌────────────┐  OTLP    ┌────────────┐  ingest   ┌──────────┐
│ App + OTel │ ───────▶ │   Tempo    │ ────────▶ │  Storage │
│  SDK       │  gRPC    │  Distributor│          │  S3/GCS  │
└────────────┘          │  Ingester  │          └──────────┘
                        │  Querier   │
┌────────────┐  Jaeger  │  Compactor │  query    ┌──────────┐
│ App + Jaeger│ ──────▶ │            │ ────────▶ │ Grafana  │
│  client     │  gRPC    └────────────┘           │ Tempo UI │
└────────────┘                                   └──────────┘
```

## 部署

```yaml
# tempo.yaml
server:
  http_listen_port: 3200

distributor:
  receivers:
    otlp:
      protocols:
        grpc:
          endpoint: 0.0.0.0:4317
    jaeger:
      protocols:
        grpc:
          endpoint: 0.0.0.0:14250
        thrift_http:
          endpoint: 0.0.0.0:14268

ingester:
  trace_idle_period: 10s
  max_block_duration: 5m

compactor:
  compaction:
    block_retention: 48h  # 保留期

storage:
  trace:
    backend: s3
    s3:
      bucket: tempo-traces
      endpoint: minio.storage:9000
      access_key: admin
      secret_key: password
    wal:
      path: /var/tempo/wal
```

```yaml
# docker-compose（开发）
services:
  tempo:
    image: grafana/tempo:latest
    command: ["-config.file=/etc/tempo.yaml"]
    volumes:
      - ./tempo.yaml:/etc/tempo.yaml
      - tempo-data:/var/tempo
    ports:
      - "4317:4317"   # OTLP gRPC
      - "3200:3200"   # HTTP

  minio:
    image: minio/minio
    command: server /data
```

## Grafana 集成

```yaml
# Grafana 数据源
apiVersion: 1
datasources:
  - name: Tempo
    type: tempo
    url: http://tempo:3200
    jsonData:
      httpMethod: GET
      tracesToLogsV2:
        datasourceUid: loki
        tags: ['job', 'service']
        mappedTags: [{ key: 'service.name', value: 'service' }]
        mapTagNamesEnabled: true
      serviceMap:
        datasourceUid: prometheus
```

## 与 Loki / Prometheus 联动

```
Trace ID → 跳转：
  1. Grafana Explore → Tempo → 输入 traceID
  2. 自动跳转到 Loki 查同一 traceID 的所有日志
  3. 自动跳转到 Prometheus 看 trace 期间的指标

Service Map：
  - 自动生成服务依赖图（基于 trace span）
  - 数据源：Prometheus（SpanMetrics processor）

配置 SpanMetrics：
  receivers:
    otlp:
      protocols: { grpc: { endpoint: 0.0.0.0:4317 } }
  processors:
    spanmetrics:
      metrics_expiration: 5m
      metrics_flush_interval: 15s
      histogram: explicit
  exporters:
    prometheus:
      endpoint: 0.0.0.0:8889
```

## 一句话总结

> **Tempo = 轻量 tracing + 对象存储**。**已有 Grafana 栈首选**。**Trace + Loki + Prometheus 联动 = 全栈可观测**。

---

## 关联章节

- [Jaeger](../06-tracing/jaeger.md)
- [Zipkin](../06-tracing/zipkin.md)
- [Tracing 基础](../06-tracing/concepts.md)
- [协议对比](../06-tracing/protocol-compare.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
