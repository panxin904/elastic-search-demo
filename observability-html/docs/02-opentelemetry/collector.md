---
title: OTel Collector 详解
date: 2026-08-15  # date-auto-injected
description: OpenTelemetry Collector 部署模式与配置实战
---

# OTel Collector 详解

> **TL;DR**：OTel Collector 是**可观测性数据的"瑞士军刀"**——接收、处理、转换、导出。生产环境的可观测性架构里，**Collector 是必不可少的一环**。

## 一句话定义

```
OTel Collector = vendor-neutral 的可观测性数据管道（receivers → processors → exporters）
```

## 三种部署模式

### 1. Agent 模式（每节点一个）

```
App Pod (with OTel Collector as sidecar)
  ├─ App container
  └─ otel-collector-agent container
        ↓
   otel-collector-gateway (集群级)
        ↓
     后端
```

**适用**：Kubernetes 环境，每个 Pod 一个 Collector sidecar。

### 2. Gateway 模式（集中式）

```
App1 ─┐
App2 ─┤─→ otel-collector-gateway ──→ 后端
App3 ─┘
```

**适用**：传统 VM / 物理机部署，所有应用指向一个 Collector。

### 3. 混合模式

```
App1 ──→ otel-collector-agent ─┐
App2 ──→ otel-collector-agent ─┤─→ otel-collector-gateway ──→ 后端
App3 (collector 直接) ─────────┘
```

## Collector 架构

```
┌─────────────────────────────────────────────────────┐
│                  OTel Collector                     │
│                                                     │
│  Receivers   →   Processors   →   Exporters         │
│  ┌─────────┐    ┌──────────┐    ┌──────────┐       │
│  │ OTLP    │    │ batch    │    │ OTLP     │       │
│  │ Jaeger  │    │ tail_sam │    │ Jaeger   │       │
│  │ Zipkin  │    │ resource │    │ Prometheus│       │
│  │ Prometheus│  │ filter   │    │ Loki     │       │
│  │ Kafka   │    │          │    │ Kafka    │       │
│  └─────────┘    └──────────┘    └──────────┘       │
│                                                     │
│  Extensions:  health_check, pprof, zpages          │
└─────────────────────────────────────────────────────┘
```

## Receivers（接收器）

**OTel Collector 支持的 receivers**（部分）：

| Receiver | 用途 |
|---|---|
| `otlp` | 接收 OTLP 协议（gRPC 4317 / HTTP 4318） |
| `jaeger` | 接收 Jaeger 协议（gRPC 14250 / HTTP 14268） |
| `zipkin` | 接收 Zipkin 协议 |
| `prometheus` | 拉取 Prometheus exporter（兼容 scrape config） |
| `kafka` | 从 Kafka 消费数据（解耦 producer / consumer） |
| `filelog` | 读取本地日志文件 |
| `hostmetrics` | 收集主机指标（CPU / 内存） |
| `dockerstats` | 收集 Docker 容器指标 |
| `k8scluster` | 收集 K8s 集群指标 |

## Processors（处理器）

**关键 processors**：

| Processor | 用途 |
|---|---|
| `batch` | 批量发送（默认） |
| `memory_limiter` | 内存限制（防 OOM） |
| `tail_sampling` | 尾部采样（保留错误和慢请求） |
| `resource` | 给所有数据添加 resource attributes（如 cluster、env） |
| `attributes` | 修改 / 删除属性 |
| `filter` | 过滤数据（不想要的丢弃） |
| `transform` | 数据转换（高级） |
| `probabilistic_sampler` | 概率采样 |
| `loadbalancing` | 负载均衡（exporter 端） |
| `routing` | 按属性路由到不同 exporter |

## Exporters（导出器）

| Exporter | 目标 |
|---|---|
| `otlp` | 发送 OTLP 到后端 |
| `otlphttp` | 发送 OTLP/HTTP 到后端 |
| `jaeger` | 发送到 Jaeger |
| `zipkin` | 发送到 Zipkin |
| `prometheus` | 暴露为 Prometheus scrape endpoint |
| `loki` | 发送到 Loki |
| `kafka` | 发送到 Kafka（链路解耦） |
| `file` | 写入文件（debug 用） |
| `logging` | 打印到日志（debug 用） |

## 实战配置：生产环境

```yaml
# otel-collector-config.yaml
receivers:
  # 接收应用 OTLP
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
        max_recv_msg_size_mib: 16
      http:
        endpoint: 0.0.0.0:4318

  # 接收主机指标
  hostmetrics:
    collection_interval: 30s
    scrapers:
      cpu:
      memory:
      disk:
      network:
      filesystem:
      load:

  # 接收 K8s 容器指标
  k8scluster:
    auth_type: serviceAccount
    collection_interval: 30s

  # 接收 K8s Pod 指标（Prometheus scrape）
  prometheus:
    config:
      scrape_configs:
      - job_name: kubernetes-pods
        kubernetes_sd_configs:
        - role: pod
        relabel_configs:
        - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
          action: keep
          regex: true

processors:
  # 内存限制
  memory_limiter:
    check_interval: 1s
    limit_percentage: 80
    spike_limit_percentage: 20

  # 资源属性注入
  resource:
    attributes:
    - key: deployment.environment
      value: production
      action: upsert
    - key: cluster.name
      value: prod-us-east-1
      action: upsert

  # 尾部采样（保留错误和慢请求）
  tail_sampling:
    decision_wait: 10s
    num_traces: 100000
    expected_new_traces_per_sec: 1000
    policies:
      # 错误请求 100% 保留
      - name: errors
        type: status_code
        status_code:
          status_codes: [ERROR]
      # 慢请求 100% 保留
      - name: slow-traces
        type: latency
        latency:
          threshold_ms: 200
      # 健康请求 5% 采样
      - name: probabilistic
        type: probabilistic
        probabilistic:
          sampling_percentage: 5

  # 批量发送
  batch:
    timeout: 5s
    send_batch_size: 10000
    send_batch_max_size: 15000

exporters:
  # traces 发送到 Jaeger
  otlp/jaeger:
    endpoint: jaeger-collector.observability.svc:4317
    tls:
      insecure: true
    sending_queue:
      enabled: true
      num_consumers: 10
      queue_size: 5000
    retry_on_failure:
      enabled: true
      initial_interval: 5s
      max_interval: 30s
      max_elapsed_time: 300s

  # metrics 暴露为 Prometheus
  prometheus:
    endpoint: 0.0.0.0:8889
    resource_to_telemetry_conversion:
      enabled: true

  # logs 发送到 Loki
  loki:
    endpoint: http://loki.logging.svc:3100/loki/api/v1/push

  # debug 用
  debug:
    verbosity: detailed
    sampling_initial: 5
    sampling_thereafter: 200

extensions:
  health_check:
    endpoint: 0.0.0.0:13133
  pprof:
    endpoint: 0.0.0.0:1777
  zpages:
    endpoint: 0.0.0.0:55679
  memory_ballast:
    size_mib: 512

service:
  telemetry:
    metrics:
      address: 0.0.0.0:8888
    logs:
      level: info

  extensions: [health_check, pprof, zpages, memory_ballast]

  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, tail_sampling, resource, batch]
      exporters: [otlp/jaeger]

    metrics:
      receivers: [otlp, hostmetrics, k8scluster, prometheus]
      processors: [memory_limiter, resource, batch]
      exporters: [prometheus]

    logs:
      receivers: [otlp]
      processors: [memory_limiter, resource, batch]
      exporters: [loki]
```

## Kubernetes 部署

```yaml
# otel-collector-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: otel-collector
  namespace: observability
spec:
  replicas: 3
  selector:
    matchLabels:
      app: otel-collector
  template:
    metadata:
      labels:
        app: otel-collector
    spec:
      containers:
      - name: otel-collector
        image: otel/opentelemetry-collector-contrib:0.108.0
        args:
        - --config=/etc/otelcol/config.yaml
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 1Gi
        ports:
        - name: otlp-grpc
          containerPort: 4317
        - name: otlp-http
          containerPort: 4318
        - name: metrics
          containerPort: 8888
        - name: health
          containerPort: 13133
        volumeMounts:
        - name: config
          mountPath: /etc/otelcol
      volumes:
      - name: config
        configMap:
          name: otel-collector-config
---
apiVersion: v1
kind: Service
metadata:
  name: otel-collector
  namespace: observability
spec:
  selector:
    app: otel-collector
  ports:
  - name: otlp-grpc
    port: 4317
    targetPort: 4317
  - name: otlp-http
    port: 4318
    targetPort: 4318
```

## 性能调优

### 1. 内存限制

```yaml
processors:
  memory_limiter:
    # 占用物理内存超过 80% 时拒绝新数据
    limit_percentage: 80
    # 突发到 100% 也允许，但要快速回落
    spike_limit_percentage: 20
    check_interval: 1s
```

### 2. 批量发送

```yaml
processors:
  batch:
    timeout: 5s              # 最长等待 5s
    send_batch_size: 10000   # 满 1 万发送
    send_batch_max_size: 15000
```

> **调优经验**：timeout 越大，吞吐量越高；send_batch_size 越大，单次请求越重。**生产环境 timeout=10s, send_batch_size=8192 是常见起点**。

### 3. 重试

```yaml
exporters:
  otlp/jaeger:
    sending_queue:
      enabled: true
      num_consumers: 10        # 并发消费者
      queue_size: 5000         # 队列最大
      retry_on_failure:
        enabled: true
        initial_interval: 5s
        max_interval: 30s
        max_elapsed_time: 300s  # 5 分钟内重试
```

## 调试技巧

### 1. Debug Exporter

```yaml
exporters:
  debug:
    verbosity: detailed
    sampling_initial: 5
    sampling_thereafter: 200
```

**效果**：每个数据都被打印到 Collector 日志，**看数据格式 + 内容**。

### 2. Health Check

```bash
curl http://collector:13133/
```

### 3. zpages

```
http://collector:55679/debug/tracez      # traces 状态
http://collector:55679/debug/pipelinez   # pipeline 状态
http://collector:55679/debug/servicez    # service 状态
```

### 4. 自监控

```yaml
service:
  telemetry:
    metrics:
      address: 0.0.0.0:8888
```

Collector 自己的 metrics（处理的 span 数、丢弃数等）暴露在 :8888。

## 常见错误

### 错误 1：没用 tail_sampling

```
❌ 100% 采样，存储爆炸
✅ tail_sampling：错误 100% + 慢请求 100% + 健康 5%
```

### 错误 2：queue_size 设太大

```
❌ queue_size: 100000 → 后端故障时内存爆炸
✅ queue_size: 5000 + memory_limiter 兜底
```

### 错误 3：忘了 resource processor

```
❌ 所有数据没打 cluster / env 标签，多集群查询混乱
✅ resource processor 注入 cluster.name / deployment.environment
```

### 错误 4：单实例

```
❌ Collector 单点 → 故障时数据全丢
✅ 至少 2 副本 + sending_queue retry
```

## 一句话总结

> **OTel Collector = 可观测性数据的中转枢纽**。
> 生产环境部署模式：**agent + gateway 混合 + tail_sampling + batch + memory_limiter + 重试**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
