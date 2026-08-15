#!/usr/bin/env python3
"""
Generate observability stubs → substantial via CONTENT dictionary.
Reuses the pattern from scripts/gen-pg-stubs.py.

Usage:
    /Users/a1111/.workbuddy/binaries/python/versions/3.13.12/bin/python3 scripts/gen-obs-stubs.py
"""
import os
import sys

DOCS_ROOT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "observability-html", "docs",
)

CONTENT = {
    # =====================================================================
    # 02-opentelemetry
    # =====================================================================
    "02-opentelemetry/sdk.md": """---
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
java -javaagent:opentelemetry-javaagent.jar \
     -Dotel.service.name=order-service \
     -Dotel.exporter.otlp.endpoint=http://otel-collector:4317 \
     -jar app.jar
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
""",

    "02-opentelemetry/otlp.md": """---
title: OTLP 协议
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

## 一句话总结

> **OTLP = OTel 协议标准**。**两种传输：gRPC（4317，推荐）/ HTTP（4318）**。**数据模型：Resource + Scope + Signal**。**所有 OTel 生态都通过 OTLP 互通**。

---

## 关联章节

- [SDK](../02-opentelemetry/sdk.md)
- [Collector](../02-opentelemetry/collector.md)
- [OpenTelemetry 概览](../02-opentelemetry/overview.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "02-opentelemetry/auto-instrumentation.md": """---
title: 自动埋点
description: Java agent / eBPF / 零代码埋点
---

# 自动埋点

> **TL;DR**：**自动埋点 = 不改业务代码，靠 SDK agent / eBPF 自动捕获 span/metric**。**Java：opentelemetry-javaagent.jar 一行命令搞定**。**eBPF：Parca / Pixie / Cilium Tetragon 不需要 SDK 也能自动捕获系统调用**。**新项目首选自动埋点 + 关键路径手动埋点**。

## 一句话定义

```
自动埋点 = 无侵入捕获调用栈
        = 三种实现：字节码注入（JVM）/ 运行时 hook（Node.js）/ eBPF（内核）
        = 优点：覆盖广 / 零代码 / 部署即生效
        = 缺点：捕获全但业务语义弱（需手动埋点补充）
```

## Java 自动埋点

```bash
# 1. 下载 opentelemetry-javaagent.jar
curl -L -o opentelemetry-javaagent.jar \
  https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/latest/download/opentelemetry-javaagent.jar

# 2. 启动 jar 时附加
java -javaagent:./opentelemetry-javaagent.jar \
     -Dotel.service.name=order-service \
     -Dotel.exporter.otlp.endpoint=http://otel-collector:4317 \
     -jar order-service.jar

# 自动埋点覆盖（2024）：
# - HTTP server: Tomcat, Jetty, Netty, Spring Web
# - HTTP client: Apache HttpClient, OkHttp, RestTemplate
# - Database: JDBC, HikariCP, R2DBC
# - Messaging: Kafka, RabbitMQ, JMS
# - RPC: gRPC, Dubbo
# - Cache: Redis (Jedis, Lettuce)
# - 框架: Spring Boot, Spring Data
```

## Node.js 自动埋点

```bash
# 1. 安装
npm install @opentelemetry/auto-instrumentations-node \
            @opentelemetry/sdk-node \
            @opentelemetry/exporter-trace-otlp-http

# 2. 启动命令前加载
node --require ./tracing.js server.js
```

```javascript
// tracing.js
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({ url: 'http://otel-collector:4318/v1/traces' }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

// 自动埋点：http, express, koa, mongodb, mysql, redis, kafka
```

## Python 自动埋点

```bash
pip install opentelemetry-distro[otlp]
opentelemetry-bootstrap -a install   # 自动安装所有 instrumentation
opentelemetry-instrument python app.py
```

## eBPF 自动埋点（K8s）

```
代表项目：
  - Pixie（New Relic 开源）：eBPF 自动捕获应用 trace + metrics
  - Parca：CPU/内存剖析（Profiling）
  - Cilium Tetragon：安全 + 网络可观测
  - bpftrace：自定义 eBPF 脚本

Pixie 示例：
  - 自动捕获 HTTP 请求（无需 SDK）
  - 自动生成火焰图
  - 自动捕获 SQL 查询 + DB 耗时
  - 限制：语言运行时细节缺失（如 Java 方法名）
```

## 选择决策

| 场景 | 推荐方案 |
|---|---|
| 新 JVM 项目 | Java agent 自动 + 关键路径手动 |
| 新 Node.js 项目 | auto-instrumentations + 手动埋点 |
| Go 项目 | 必须手动埋点（无运行时 hook） |
| K8s 容器化项目 | 配 Java agent + Pixie（eBPF）做兜底 |
| 旧系统接入 | eBPF / sidecar 方式无侵入接入 |
| 性能敏感 | 不开 auto，CPU 影响 2-5% |

## 一句话总结

> **自动埋点 = 零代码接入**。**Java 用 javaagent，Node.js 用 auto-instrumentations，K8s 用 eBPF**。**Go 必须手动**。**auto + 关键路径手动 = 最佳组合**。

---

## 关联章节

- [SDK](../02-opentelemetry/sdk.md) — 自动 + 手动的 SDK
- [OTLP](../02-opentelemetry/otlp.md) — 自动埋点的数据输出
- [Collector](../02-opentelemetry/collector.md) — 数据汇聚点

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    # =====================================================================
    # 03-prometheus
    # =====================================================================
    "03-prometheus/data-model.md": """---
title: Prometheus 数据模型
description: Metric + Label + Sample
---

# Prometheus 数据模型

> **TL;DR**：Prometheus 数据模型 = **Metric（指标名）+ Label（标签键值对）+ Sample（时间戳 + 值）**。**所有数据都是时间序列**：`<metric>{<labels>} <value> @ <timestamp>`。**Label 是 Prometheus 维度切片的灵魂，**慎用高基数标签**。

## 一句话定义

```
时间序列（Time Series）= metric + labels + samples
                        = 同一 metric + label 组合的一个时间序列
                        = 例：http_requests_total{service="order",status="200"} 1423

Metric（指标名）= 描述测量什么（用 snake_case）
Label（标签）= 维度切片键值对
Sample（样本）= (timestamp, value) 数据点
```

## Metric 类型

### 1. Counter（计数器）

```
只能递增的指标（重启时可重置为 0）
用途：请求总数 / 错误总数 / 任务完成数

# 例：HTTP 请求总数
http_requests_total{service="order",method="POST",status="200"} 1423456

# PromQL 计算速率
rate(http_requests_total[5m])   # 每秒请求数
```

### 2. Gauge（仪表盘）

```
可增可减的指标
用途：当前温度 / 队列长度 / CPU 使用率

# 例：当前活跃连接数
db_connections_active 142

# PromQL
delta(db_connections_active[5m])  # 5 分钟变化量
```

### 3. Histogram（直方图）

```
分桶统计（bucket）= 延迟 / 大小 等分布数据
用途：延迟 / 响应大小

# 例：HTTP 请求延迟（buckets: 0.005s, 0.01s, ..., 10s）
http_request_duration_seconds_bucket{le="0.005"} 23456
http_request_duration_seconds_bucket{le="0.01"} 25678
http_request_duration_seconds_bucket{le="+Inf"} 50000
http_request_duration_seconds_sum 1234.56
http_request_duration_seconds_count 50000

# PromQL 计算分位数
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
```

### 4. Summary（摘要）

```
类似 Histogram，但服务端预计算分位数
缺点：不可聚合（分位数不能跨实例求平均）

# 例：客户端报告 P99 延迟
http_request_duration_seconds{quantile="0.99"} 1.234

# 实战：Histogram 优于 Summary（可聚合）
```

## Label 命名规范

```yaml
# 良好实践：
- service: "order-api"
- env: "prod"
- region: "cn-north-1"
- status: "200"

# 禁用（高基数，会导致时序爆炸）：
- user_id: "12345"          # 100w 用户 = 100w 时序
- email: "[email protected]"
- order_id: "ORD-001"
- request_id: "abc-def"
- timestamp: "..."          # 完全禁忌
```

## 时序存储

```
Prometheus TSDB 内部结构：
  - Block = 一段时间（如 2 小时）的所有时序
  - 每个时序按 (metric, labels) 哈希
  - 压缩算法：Gorilla (Facebook 2015)，平均 1.3 字节/样本
  - 块文件：head (内存) + persisted (磁盘)

存储路径：
  /prometheus-data/
    01GBM0AC4N0WJZ37H8Z7G8KX1V  # block 1
    01GBM2R8NQ3WXCV9Q4SFXJ8XCP  # block 2
    chunks_head/                # head block

远程存储：
  - remote_write: Prometheus → Thanos / Cortex / InfluxDB / Mimir
  - remote_read: 从远程读
```

## 实战案例：自定义 Counter / Histogram

```go
// Go (prometheus client_golang)
import "github.com/prometheus/client_golang/prometheus"

var (
    requestCounter = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total HTTP requests",
        },
        []string{"service", "method", "status"},
    )

    requestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "http_request_duration_seconds",
            Help:    "HTTP request duration",
            Buckets: []float64{0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10},
        },
        []string{"service", "endpoint"},
    )
)

func init() {
    prometheus.MustRegister(requestCounter, requestDuration)
}
```

## 一句话总结

> **Prometheus 数据 = Metric + Label + Sample**。**四种类型：Counter / Gauge / Histogram / Summary**。**Label 设计决定查询能力**。**禁止高基数标签（user_id / order_id）**。

---

## 关联章节

- [Prometheus 概览](../03-prometheus/overview.md) — 架构
- [PromQL](../03-prometheus/promql.md) — 查询语言
- [Exporter](../03-prometheus/exporter.md) — 暴露指标的工具

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "03-prometheus/exporter.md": """---
title: Prometheus Exporter
description: node_exporter / 黑盒 / 自定义 exporter
---

# Prometheus Exporter

> **TL;DR**：Exporter = **把第三方系统指标转换为 Prometheus 格式的工具**。**白盒（exporter 程序暴露指标）+ 黑盒（prober 主动探测）**。**官方维护：node_exporter（主机）/ blackbox_exporter（HTTP/TCP/ICMP）/ mysqld_exporter / redis_exporter / kafka_exporter**。

## 一句话定义

```
Exporter = 第三方指标的"翻译器"
        = 把 MySQL / Redis / Kafka / 主机 等系统的内部指标
        = 转换为 Prometheus 可抓取的格式（HTTP /metrics 端点）
        = 部署方式：sidecar / daemonset / 独立进程
```

## node_exporter（主机指标）

```yaml
# DaemonSet 部署（每台机器 / 每个 K8s 节点）
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: node-exporter
spec:
  template:
    spec:
      hostPID: true
      hostNetwork: true
      containers:
        - name: node-exporter
          image: prom/node-exporter:v1.7.0
          args:
            - "--path.rootfs=/host"
            - "--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)"
          volumeMounts:
            - name: root
              mountPath: /host
          ports:
            - containerPort: 9100
```

```
暴露指标（常用）：
  - node_cpu_seconds_total{mode="idle|user|system|iowait"}
  - node_memory_MemTotal_bytes / MemAvailable_bytes
  - node_filesystem_avail_bytes{mountpoint="/"}
  - node_network_receive_bytes_total / transmit_bytes_total
  - node_disk_io_now / disk_io_seconds_total
  - node_load1 / load5 / load15
```

## blackbox_exporter（黑盒探测）

```yaml
# 主动探测：HTTP / TCP / ICMP / DNS
apiVersion: v1
kind: ConfigMap
metadata:
  name: blackbox-exporter-config
data:
  blackbox.yml: |
    modules:
      http_2xx:
        prober: http
        timeout: 5s
        http:
          valid_http_versions: ["HTTP/1.1", "HTTP/2.0"]
          valid_status_codes: [200]
          method: GET
      tcp_connect:
        prober: tcp
        timeout: 5s
      icmp_ping:
        prober: icmp
        timeout: 5s
```

```yaml
# Prometheus scrape 配置
scrape_configs:
  - job_name: blackbox-http
    metrics_path: /probe
    params:
      module: [http_2xx]
    static_configs:
      - targets:
          - https://example.com
          - https://api.example.com/health
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - source_labels: [__param_target]
        target_label: instance
      - target_label: __address__
        replacement: blackbox-exporter:9115
```

## 主流 Exporter 一览

| Exporter | 用途 | 端口 |
|---|---|---|
| node_exporter | 主机（CPU/内存/磁盘/网络） | 9100 |
| blackbox_exporter | HTTP/TCP/ICMP 探测 | 9115 |
| mysqld_exporter | MySQL 内部指标 | 9104 |
| postgres_exporter | PostgreSQL 指标 | 9187 |
| redis_exporter | Redis 指标 | 9121 |
| kafka_exporter | Kafka broker 指标 | 9308 |
| nginx-prometheus-exporter | nginx stub_status / VTS | 9113 |
| elasticsearch_exporter | ES 集群指标 | 9114 |
| kube-state-metrics | K8s 对象指标 | 8080 |
| cadvisor | 容器指标 | 8080 |
| jmx_exporter | Java JMX 指标（任意） | 8080 |

## 自定义 Exporter（Python）

```python
# 1. 使用 prometheus_client
from prometheus_client import start_http_server, Gauge, Counter
import time

REQUEST_COUNT = Counter('app_requests_total', 'Total requests', ['endpoint'])
REQUEST_LATENCY = Gauge('app_request_duration_seconds', 'Request latency', ['endpoint'])

def handler(endpoint):
    start = time.time()
    # 业务逻辑
    duration = time.time() - start
    REQUEST_COUNT.labels(endpoint=endpoint).inc()
    REQUEST_LATENCY.labels(endpoint=endpoint).set(duration)

# 2. 暴露 :9100/metrics
start_http_server(9100)

# 业务循环...
while True:
    handler('/api/orders')
    time.sleep(1)
```

## 一句话总结

> **Exporter = 第三方指标翻译器**。**主机：node_exporter / 黑盒：blackbox_exporter / 数据库：mysqld_exporter**。**K8s 标配：node-exporter DaemonSet + kube-state-metrics + cadvisor**。

---

## 关联章节

- [Prometheus 概览](../03-prometheus/overview.md)
- [数据模型](../03-prometheus/data-model.md)
- [PromQL](../03-prometheus/promql.md)
- [K8s 监控](../11-scenarios/k8s-monitor.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    # =====================================================================
    # 04-grafana
    # =====================================================================
    "04-grafana/overview.md": """---
title: Grafana 概览
description: 数据源 / Dashboard / 告警
---

# Grafana 概览

> **TL;DR**：Grafana = **业界标准的可视化平台**，**支持 30+ 数据源**（Prometheus / Loki / Elasticsearch / InfluxDB / MySQL / PostgreSQL / Tempo / Jaeger）。**核心功能：Dashboard（看板）+ Explore（临时查询）+ Alerting（告警）+ Unified Alerting**。**新项目标配：Grafana + Prometheus + Loki + Tempo = 全栈可观测**。

## 一句话定义

```
Grafana = 开源可视化 + 分析平台
       = 2014 Torkel Ödegaard 创立
       = Grafana Labs 维护（Grafana / Loki / Tempo / Mimir / Pyroscope）
       = 核心：数据源抽象 + Dashboard 模板化 + 多租户
```

## 核心组件

### 1. 数据源（Data Source）

```
支持的 30+ 数据源（部分）：
  - Prometheus / Loki / Tempo（原生三件套）
  - Elasticsearch（ELK）
  - InfluxDB / TimescaleDB（时序数据库）
  - MySQL / PostgreSQL / MSSQL（关系数据库）
  - CloudWatch / Azure Monitor / GCP Monitoring（云厂商）
  - Jaeger / Zipkin（tracing）
  - Pyroscope（profiling）

每种数据源有独立的 query editor：
  - Prometheus: PromQL 编辑器 + 自动补全
  - Loki: LogQL 编辑器 + 标签选择
  - Elasticsearch: KQL / Lucene
```

### 2. Dashboard

```
Dashboard = 多个 Panel 的组合（JSON 格式）
         = 支持变量（Variables）做联动
         = 支持 drilldown（点击 panel 跳到 detail）
         = 支持时间范围（全局 + 每 panel 覆盖）

最佳实践：
  - 一个服务一个 dashboard
  - 用 input controls 联动
  - dashboard JSON 可 git 版本控制
  - 用 templating 做复用
```

### 3. Explore

```
Explore = 临时查询模式
       = 不需要保存 dashboard
       = 适合临时调试 / ad-hoc 查询
       = 支持 split view（同时查多个数据源）

用法：Explore → 选数据源 → 写 PromQL/LogQL → Run
```

### 4. Unified Alerting

```
Grafana 8+ 内置告警引擎：
  - Alert rules：基于查询的告警规则
  - Contact points：Slack / Email / PagerDuty / Webhook
  - Notification policies：路由 / 抑制 / 静默
  - Silences：手动静默告警

优势：
  - 一个 UI 管理所有数据源告警
  - 不依赖 Alertmanager
  - 支持多租户
```

## 安装与配置

```bash
# Docker 单机启动
docker run -d --name grafana \
  -p 3000:3000 \
  -v grafana-data:/var/lib/grafana \
  grafana/grafana:latest
```

```yaml
# docker-compose（生产）
version: '3'
services:
  grafana:
    image: grafana/grafana:10.4.0
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
      - ./grafana.ini:/etc/grafana/grafana.ini
      - ./provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GF_PASSWORD}
      - GF_USERS_ALLOW_SIGN_UP=false
```

```ini
# grafana.ini（关键配置）
[server]
http_port = 3000
domain = grafana.example.com
root_url = https://grafana.example.com

[security]
admin_user = admin
admin_password = ${GF_PASSWORD}

[users]
allow_sign_up = false

[auth.anonymous]
enabled = false

[smtp]
enabled = true
host = smtp.example.com:587
user = [email protected]
password = ${SMTP_PASSWORD}
```

## 实战案例：Grafana + Prometheus + Loki

```yaml
# Grafana provisioning 自动配数据源
# /etc/grafana/provisioning/datasources/datasources.yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true

  - name: Loki
    type: loki
    url: http://loki:3100

  - name: Tempo
    type: tempo
    url: http://tempo:3200
```

## 权限与多租户

```
Grafana 多租户模型：
  - Org 组织（顶层隔离单位）
  - Team 团队（组织内）
  - Folder 文件夹（dashboard 分组）
  - Role 角色（Admin / Editor / Viewer）
  - Permission 权限（Edit / View）

最佳实践：
  - 团队 dashboard 放在 team folder
  - 全公司 dashboard 放 General folder
  - 生产环境数据源用 Viewer 角色
```

## 一句话总结

> **Grafana = 数据源无关的可视化平台**。**支持 30+ 数据源**。**核心：Dashboard / Explore / Unified Alerting**。**新项目标配：Grafana + Prometheus + Loki + Tempo = 全栈可观测**。

---

## 关联章节

- [Dashboard 设计](../04-grafana/dashboard.md)
- [变量](../04-grafana/variables.md)
- [Grafana 告警](../04-grafana/alerting.md)
- [Annotation 注释](../04-grafana/annotation.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "04-grafana/variables.md": """---
title: Grafana 变量
description: Variables / Templating / Dropdown
---

# Grafana 变量

> **TL;DR**：**Grafana Variables = Dashboard 上的下拉筛选器**。**联动所有 panel 的查询**。**核心类型：Query（数据源查询）/ Custom（静态列表）/ Datasource（数据源切换）/ Interval（时间步长）**。**最佳实践：用 variables 做多服务 / 多环境 / 多 region 的统一看板**。

## 一句话定义

```
Variable（变量）= Dashboard 上的交互式参数
              = 在 dashboard 顶部显示为下拉框
              = 联动所有 panel 的查询
              = 模板化 dashboard 的关键
```

## 变量类型

| 类型 | 数据来源 | 典型用途 |
|---|---|---|
| Query | 数据源查询 | 服务列表、环境列表 |
| Custom | 静态自定义 | 固定选项（如 P0/P1/P2） |
| Datasource | 数据源切换 | 多 Prometheus 实例 |
| Interval | 时间步长 | rate / histogram bucket |
| Text box | 自由输入 | 临时查询 |
| Constant | 常量 | 业务常量 |
| Hidden | 隐藏变量 | URL 传参 |

## Query 变量（最常用）

```yaml
# 1. 从 Prometheus 查询所有服务名
type: query
name: service
label: 服务
query: label_values(http_requests_total, service)

# 2. 多选
multi: true
include_all: true   # 自动加 "All" 选项

# 3. 依赖其他变量
type: query
name: instance
query: label_values(http_requests_total{service="$service"}, instance)

# 4. 正则过滤
regex: /.*-prod/
```

## 在 Panel 中使用变量

```promql
# 1. 直接插值
sum(rate(http_requests_total{service="$service"}[5m]))

# 2. 多选变量 → 用 =~
service=~"$service"   # 选多个 → service=~"a|b|c"

# 3. 用 ${var} 还是 $var
# 推荐 ${var}（更明确，避免与字符混淆）

# 4. 变量默认转义
# 文本变量自动 quote，label 变量自动处理
```

## 实战案例：多服务 SLO 看板

```yaml
# 变量配置
variables:
  - name: service
    type: query
    query: label_values(http_requests_total, service)
    multi: true
    include_all: true
    default: "All"

  - name: env
    type: custom
    options:
      - prod
      - staging
      - dev
    default: prod

  - name: percentile
    type: custom
    options:
      - { text: "P50", value: "0.5" }
      - { text: "P95", value: "0.95" }
      - { text: "P99", value: "0.99" }
    default: P95

  - name: interval
    type: interval
    options:
      - 1m
      - 5m
      - 15m
    default: 5m

# Panel 查询
panels:
  - title: ${service} ${env} Rate
    targets:
      - expr: sum(rate(http_requests_total{service=~"$service", env="$env"}[$interval]))

  - title: ${service} ${env} P${percentile}
    targets:
      - expr: |
        histogram_quantile($percentile,
          sum by (le) (rate(http_request_duration_seconds_bucket{service=~"$service", env="$env"}[$interval]))
        )
```

## 嵌套变量

```yaml
# 复杂场景：选择 region → 选择 service → 选择 instance
variables:
  - name: region
    type: custom
    options: [cn-north, cn-east, us-west]

  - name: service
    type: query
    query: label_values(http_requests_total{region="$region"}, service)
    refresh: on_time_change  # 父变量变时自动 refresh

  - name: instance
    type: query
    query: label_values(http_requests_total{region="$region", service="$service"}, instance)
```

## URL 参数传变量

```
Dashboard URL 可带变量值：
  https://grafana/d/order-slo?var-service=order-api&var-env=prod&from=now-1h

应用：
  - 告警通知附 URL（直接定位到 dashboard）
  - 第三方系统集成（如 status page）
```

## 一句话总结

> **Variables = Dashboard 的下拉筛选器**。**Query 变量最常用**。**支持嵌套（service → instance）**。**一个 dashboard 服务所有服务所有环境**。

---

## 关联章节

- [Dashboard 设计](../04-grafana/dashboard.md)
- [Grafana 概览](../04-grafana/overview.md)
- [Grafana 告警](../04-grafana/alerting.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "04-grafana/annotation.md": """---
title: Grafana Annotation
description: 时间轴标记 / 部署事件 / 告警叠加
---

# Grafana Annotation

> **TL;DR**：Annotation = **Dashboard 时间轴上的事件标记**（如部署 / 告警 / 提交）。**两层叠加：内建（来自数据源告警）+ 自定义（来自 Grafana API / Prometheus deploy webhook）**。**实战：在 trace 上看部署时间点，定位"是不是这次上线出的问题"**。

## 一句话定义

```
Annotation = Dashboard 上时间轴的"事件标记"
           = 竖线 + 标签，标记关键时刻
           = 内建：来自 Grafana Alerting / 数据源告警
           = 自定义：来自外部 webhook / API
```

## 内建 Annotation

```
Grafana 自动从以下来源获取 annotations：
  1. Alerting：触发 / 解决的告警
  2. Dashboard URL：手动添加（按住 Ctrl 拖动）
  3. 数据源查询（query 类型）

每种类型用不同颜色区分
```

## 自定义 Annotation（最常用）

### 1. 通过 Grafana HTTP API

```bash
# 添加 deployment annotation
curl -X POST http://admin:[email protected]/api/annotations \
  -H "Content-Type: application/json" \
  -d '{
    "dashboardId": 1,
    "panelId": 1,
    "time": 1723219200000,
    "tags": ["deploy", "prod"],
    "text": "v2.3.1 deployed (PR #1234)"
  }'
```

### 2. 部署时自动添加（CI/CD 集成）

```yaml
# GitHub Actions 示例
- name: Add deploy annotation
  run: |
    curl -X POST "$GRAFANA_URL/api/annotations" \
      -H "Authorization: Bearer $GRAFANA_TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "dashboardId": 1,
        "time": $(date +%s)000,
        "tags": ["deploy", "${{ github.event.repository.name }}"],
        "text": "Deploy ${{ github.sha }} by ${{ github.actor }}"
      }'
```

### 3. 从 Prometheus 拉取（query 类型）

```yaml
# Grafana Dashboard JSON
annotations:
  list:
    - name: deploys
      datasource: Prometheus
      iconColor: blue
      enable: true
      query:
        - 'ALERTS{alertstate="firing",severity="critical"}'
      tagKeys: "alertname,severity"
      titleFormat: "{{alertname}}"
```

## 实战案例：trace + deploy 联动

```
场景：15:00 发现错误率突增，需要判断是否与 14:55 的部署相关

步骤：
  1. 打开 Grafana Dashboard（订单服务）
  2. 时间窗口：14:30 ~ 15:30
  3. 在 dashboard 上看到 14:55 有一条 annotation（v2.3.1 部署）
  4. 错误率从 14:58 开始飙升 → 时间相关
  5. 结论：v2.3.1 引入的 bug，触发回滚

没有 annotation：
  - 需要手动 grep 部署日志
  - 需要问运维 / 同事
  - 排查时间长 5-10 分钟
```

## Annotation Tags 最佳实践

```
常用标签：
  - deploy: 部署事件
  - config-change: 配置变更
  - alert: 告警
  - incident: 故障
  - release: 版本发布
  - maintenance: 维护窗口

颜色编码（iconColor）：
  - red: 严重事件
  - orange: 警告
  - yellow: 注意
  - green: 成功
  - blue: 信息
```

## 一句话总结

> **Annotation = 时间轴事件标记**。**部署时通过 API 自动添加**。**Trace / 错误率 / 告警叠加 = 故障定位 1 步到位**。

---

## 关联章节

- [Dashboard 设计](../04-grafana/dashboard.md)
- [Grafana 概览](../04-grafana/overview.md)
- [Alertmanager](../08-alerting/alertmanager.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "04-grafana/alerting.md": """---
title: Grafana 告警
description: Unified Alerting / Contact Points / Notification Policies
---

# Grafana 告警

> **TL;DR**：**Grafana 8+ Unified Alerting = 内置告警引擎**（替代依赖 Alertmanager）。**核心：Alert Rules + Contact Points + Notification Policies + Silences**。**优势：单 UI 管理所有数据源告警**。**实战：Prometheus + Loki 告警都在 Grafana 配置**。

## 一句话定义

```
Grafana Unified Alerting = Grafana 8+ 内置告警引擎
                        = 一个 UI 管所有数据源告警
                        = 替代 Alertmanager（但 Alertmanager 仍可用）
                        = 适合：中小团队 / 不希望维护 Alertmanager
```

## 核心组件

### 1. Alert Rules（告警规则）

```yaml
# Grafana Alert Rule 关键字段：
- query: PromQL / LogQL / 数据源查询
- condition: 触发条件（reduce + math）
- for: 持续时间
- labels: severity / team
- annotations: summary / description
- no_data_state: NoData / OK / Alerting
- exec_err_state: Error / Alerting
```

### 2. Contact Points（联系点）

```yaml
# 支持的 contact type：
- Slack
- Email
- PagerDuty
- OpsGenie
- VictorOps
- Webhook
- Microsoft Teams
- DingTalk / 飞书 / 钉钉（国内）

# 配置示例（Slack）
apiVersion: 1
contactPoints:
  - orgId: 1
    name: slack-ops
    receivers:
      - uid: slack-ops-1
        type: slack
        settings:
          url: https://hooks.slack.com/services/T00/B00/xxx
          channel: '#ops-alerts'
          title: '{{ template "slack.default.title" . }}'
          text: '{{ template "slack.default.text" . }}'
```

### 3. Notification Policies（路由策略）

```
树状结构，按 label 匹配层层下钻：
  Root (default → email-default)
    └─ match: team=payments (→ pagerduty-payments)
    └─ match: severity=critical (→ pagerduty-critical)
        └─ match: region=cn (→ pagerduty-cn)
```

### 4. Silences（静默）

```
手动 / 定时屏蔽特定告警：
  - 创建 silence（matcher + 时间窗口）
  - 维护窗口 / 已知问题
  - 到期自动解除
```

## 实战案例：Prometheus 告警迁移

```yaml
# 1. Alert Rule（YAML provisioning）
apiVersion: 1
groups:
  - orgId: 1
    name: prometheus-alerts
    folder: Production
    interval: 1m
    rules:
      - uid: high-error-rate
        title: HighErrorRate
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: |
                sum(rate(http_requests_total{status=~"5.."}[5m]))
                /
                sum(rate(http_requests_total[5m]))
          - refId: B
            datasourceUid: __expr__
            model:
              type: threshold
              conditions:
                - evaluator:
                    type: gt
                    params: [0.05]   # 5%
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "错误率超过 5%"
          description: "当前错误率: {{ $value }}"
```

## Grafana Alerting vs Alertmanager

| 维度 | Grafana Alerting | Alertmanager |
|---|---|---|
| 部署 | 集成在 Grafana | 独立组件 |
| UI | Grafana 统一 UI | 独立 Web UI |
| 数据源 | 任意（Grafana 支持的） | 仅 Prometheus |
| 路由 | Notification Policies | route tree |
| 集群 | Grafana HA | Gossip 协议 |
| 适用 | 中小团队 / 多数据源 | 大型 Prometheus 部署 |

## 一句话总结

> **Grafana Unified Alerting = 单 UI 管所有告警**。**支持 PromQL / LogQL / 任意数据源**。**中小团队首选 Grafana Alerting，大型仍可保留 Alertmanager**。

---

## 关联章节

- [Dashboard 设计](../04-grafana/dashboard.md)
- [变量](../04-grafana/variables.md)
- [Alertmanager](../08-alerting/alertmanager.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    # =====================================================================
    # 05-loki
    # =====================================================================
    "05-loki/overview.md": """---
title: Loki 概览
description: Grafana Labs 的日志聚合系统
---

# Loki 概览

> **TL;DR**：Loki = **Grafana Labs 2018 开源的日志聚合系统**，**设计哲学：只索引标签，不索引内容**。**类似 Prometheus 但 for logs**。**架构：Promtail（采集）+ Loki（存储 + 查询）+ Grafana（可视化）**。**优势：成本极低（vs ES 索引全文）+ 与 Prometheus 标签对齐**。

## 一句话定义

```
Loki = Grafana Labs 开源日志聚合系统
     = 设计灵感来自 Prometheus
     = 只索引 labels（标签），不索引 content（日志原文）
     = 通过 LogQL 查询（类似 PromQL）
     = 存储：chunk + object store（S3 / GCS / MinIO / 本地磁盘）
```

## 与 ELK 对比

| 维度 | Loki | ELK（Elasticsearch） |
|---|---|---|
| 出品 | Grafana Labs | Elastic |
| 索引 | 只索引 labels | 全文倒排索引 |
| 存储成本 | 极低（不索引原文） | 高（每条日志都建索引） |
| 查询能力 | LogQL（标签 + 行过滤） | Lucene KQL（全文检索强） |
| 全文检索 | 弱（要扫 chunk） | 强 |
| 聚合能力 | 中（受限于扫描量） | 强 |
| 适用 | 监控日志 / 结构化日志 | 全文检索 / 复杂查询 |
| 部署 | 单二进制 / 微服务 | ES 集群 |

## 架构

```
┌──────────┐  push   ┌──────────────────────────────────────┐
│ Promtail │ ──────▶ │  Loki                                │
│  (agent) │         │  ┌──────────┐ ┌──────────┐ ┌─────┐  │
└──────────┘         │  │ Distributor│ │ Ingester│ │Querier│ │
                     │  └──────┬───┘ └──────┬───┘ └──┬──┘  │
┌──────────┐  push   │         │             │        │     │
│  Docker  │ ──────▶ │         ▼             ▼        ▼     │
│  driver  │         │  ┌──────────────────────────────────┐ │
└──────────┘         │  │  Storage (chunks + index)        │ │
                     │  │  - Local FS / S3 / GCS / MinIO   │ │
┌──────────┐  push   │  │  - Index: BoltDB / TSDB          │ │
│  Syslog  │ ──────▶ │  └──────────────────────────────────┘ │
└──────────┘         └──────────┬───────────────────────────┘
                               │ query (LogQL)
                               ▼
                          ┌──────────┐
                          │ Grafana  │
                          └──────────┘
```

## 核心组件

### 1. Distributor

```
接收客户端 push 的日志流
  - 验证 / 限流
  - 按 tenant 分流
  - 转发到 Ingester
```

### 2. Ingester

```
把日志流写入 chunk（默认 24h 一个 chunk）
  - 流式压缩（gzip）
  - 内存 → 定期 flush 到对象存储
  - 同一 label 流的日志聚合到同一 chunk
```

### 3. Querier

```
处理 LogQL 查询
  - 扫描匹配的 chunk
  - 应用 LogQL 过滤
  - 合并 / 排序
```

### 4. Storage

```
Chunk 存储：S3 / GCS / MinIO / 本地磁盘
Index 存储：BoltDB（单实例）/ TSDB（多副本）
```

## 部署模式

### 单二进制模式（开发）

```bash
# 一行启动
loki -config.file=/etc/loki/local-config.yaml
```

### 微服务模式（生产）

```yaml
# docker-compose
services:
  loki:
    image: grafana/loki:2.9.0
    command: -config.file=/etc/loki/config.yaml
  promtail:
    image: grafana/promtail:2.9.0
    command: -config.file=/etc/promtail/config.yaml
  minio:
    image: minio/minio
    command: server /data
```

## 标签设计（核心）

```
Loki 的标签 = 唯一可索引字段
           = 决定查询效率
           = 设计原则：低基数 + 业务维度

良好标签：
  - job: "order-api"
  - env: "prod"
  - service: "order"
  - level: "error|warn|info"

禁用标签：
  - user_id: 高基数
  - request_id: 高基数
  - timestamp: 完全禁忌
  - message: 全文，应该过滤而非标签
```

## 实战案例：Loki 部署 + Promtail

```yaml
# loki config
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

limits_config:
  retention_period: 744h   # 31 天
  ingestion_rate_mb: 10
  ingestion_burst_size_mb: 20

ruler:
  storage:
    type: local
    local:
      directory: /loki/rules
```

## 一句话总结

> **Loki = Prometheus 式的日志系统**。**只索引 labels，不索引 content**。**优势：成本低 + 与 Prometheus 标签对齐**。**适用：监控日志 / 结构化日志**。

---

## 关联章节

- [LogQL 查询](../05-loki/logql.md)
- [Pipeline 处理](../05-loki/pipeline.md)
- [Loki 最佳实践](../05-loki/best-practice.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "05-loki/pipeline.md": """---
title: Loki Pipeline 处理
description: Promtail pipeline stages / 字段提取 / 转换
---

# Loki Pipeline 处理

> **TL;DR**：**Pipeline = Promtail 把原始日志解析成结构化字段的规则链**。**核心 stage：regex / json / logfmt / timestamp / label / template / drop / limit**。**类比 Logstash filter，但更轻量**。**实战：把 nginx 默认日志解析成结构化字段，便于 LogQL 查询**。

## 一句话定义

```
Pipeline = Promtail 的日志处理规则链
         = 顺序应用多个 stage（解析 / 转换 / 丢弃）
         = 类似 Logstash filter / Fluentd filter
         = 输出：提取的字段 + 标签（可加入 Loki 索引）
```

## Pipeline Stage 一览

| Stage | 功能 |
|---|---|
| `regex` | 正则提取字段 |
| `json` | JSON 解析 |
| `logfmt` | logfmt 解析 |
| `timestamp` | 提取/转换时间戳 |
| `label` | 提取字段作为标签 |
| `template` | 模板字符串 |
| `drop` | 丢弃匹配行 |
| `limit` | 限制速率 |
| `replace` | 字符串替换 |
| `match` | 条件分支 |
| `merge` | 多行合并 |

## 实战案例：nginx access log

```yaml
# Promtail 配置
scrape_configs:
  - job_name: nginx
    static_configs:
      - targets: [localhost]
        labels:
          job: nginx
          __path__: /var/log/nginx/*.log
    pipeline_stages:
      # 1. 正则提取字段
      - regex:
          expression: '^(?P<remote_addr>\S+) - \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d+) (?P<bytes>\d+) (?P<req_time>\S+)'

      # 2. 提取字段作为标签（labels，影响 Loki 索引）
      - labels:
          method:
          status:

      # 3. 转换时间戳
      - timestamp:
          source: time
          format: '02/Jan/2006:15:04:05 -0700'

      # 4. 丢弃 favicon 请求
      - match:
          selector: '{job="nginx"}'
          stages:
            - drop:
                expression: ".*favicon\\.ico.*"
                older_than: 1h
```

## 实战案例：JSON 日志

```yaml
pipeline_stages:
  # 1. 解析 JSON 到 root
  - json:
      expressions:
        level: level
        msg: message
        trace_id: trace_id
      # 把 JSON 字段也作为 Loki 标签
      # 注意：高基数字段不要作为标签

  # 2. 应用格式
  - template:
      source: msg
      template: '{{ .msg }}'

  # 3. 提取 status_code
  - label:
      level:
```

## 实战案例：Java 应用日志

```bash
# 输入日志：
# 2026-08-09 14:23:45.123 ERROR [http-nio-8080-exec-3] com.example.Service - NullPointerException at UserService.java:42
```

```yaml
pipeline_stages:
  - regex:
      expression: '^(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) (?P<level>\S+) \[[^\]]+\] (?P<logger>\S+) - (?P<msg>.*)'
      # 提取：time / level / logger / msg

  - labels:
      level:    # level 作为标签（低基数）
      logger:   # logger 名作为标签

  - timestamp:
      source: time
      format: '2006-01-02 15:04:05.000'

  # 提取异常类型到 msg 字段
  - regex:
      expression: '(?P<exception>\w+Exception)'
      # 配合第一个 regex 的 msg
```

## 高级技巧

### 1. 条件分支

```yaml
pipeline_stages:
  - match:
      selector: '{job="nginx", status="5.."}'
      stages:
        - regex:
            expression: '...'
        # 只对 5xx 应用额外处理
```

### 2. 多行合并（Java stack trace）

```yaml
pipeline_stages:
  # 检测：以 "	at " 开头的行是上一行的延续
  - match:
      selector: '{job="java"}'
      stages:
        - regex:
            # 匹配 stack trace 起始行（含 "Exception"）
            expression: '.*(?P<exception>\w+Exception)'
        - template:
            source: msg
            template: '{{ .msg }}'
```

## 性能优化

```
- regex 顺序：先简单后复杂
- 提取的字段越少越好（labels 尤其）
- 避免高基数字段作为标签
- drop stage 减少写入量
- limit stage 限制单文件速率（防爆）
```

## 一句话总结

> **Pipeline = Promtail 日志解析链**。**核心 stage：regex / json / logfmt / timestamp / labels / drop**。**先解析后打标，性能可控**。

---

## 关联章节

- [Loki 概览](../05-loki/overview.md)
- [LogQL 查询](../05-loki/logql.md)
- [Loki 最佳实践](../05-loki/best-practice.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "05-loki/best-practice.md": """---
title: Loki 最佳实践
description: 标签设计 / 存储优化 / 性能调优
---

# Loki 最佳实践

> **TL;DR**：**Loki 最佳实践 = 标签设计（低基数）+ 存储分层（hot/warm/cold）+ 写入优化（batch）+ 查询优化（缩小时间窗）**。**核心原则：标签决定成本，原文不索引**。**实战：单集群可承载日均 1TB 日志**。

## 一句话定义

```
Loki 最佳实践 = 标签设计 + 存储优化 + 写入优化 + 查询优化
             = 核心：让标签有意义但不爆量
             = 让 chunk 压缩率高
             = 让查询扫描范围小
```

## 标签设计（最重要）

### 良好实践

```yaml
labels:
  # 业务维度（必加）
  job: "order-api"           # 服务名
  env: "prod"                # 环境
  cluster: "prod-cn-north"   # 集群
  namespace: "ecommerce"     # K8s namespace

  # 关键状态（必加）
  level: "error|warn|info"   # 日志级别（低基数）
  service: "order"           # 业务服务

  # 来源（必加）
  source: "app|nginx|system"

  # 不要的：
  # ❌ user_id, request_id, order_id (高基数)
  # ❌ ip（除非 NAT 后唯一）
  # ❌ timestamp, datetime
  # ❌ message（应该 LogQL filter）
```

### 标签数量控制

```
每个日志流的标签建议 5-10 个
每条日志流的标签基数总和 < 10000
例：job × env × level = 20 × 3 × 3 = 180 个时间序列，可接受
```

## 存储优化

### 1. 存储分层

```yaml
# 短期：本地磁盘（hot）
# 长期：S3/GCS/MinIO（warm/cold）

common:
  storage:
    s3:
      s3: s3://cn-north-1/loki-chunks
      s3forcepathstyle: true
      access_key_id: xxx
      secret_access_key: xxx

schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: s3
      schema: v13
      index:
        prefix: index_
        period: 24h
```

### 2. 压缩

```yaml
# Chunk 默认 gzip 压缩（80%+ 压缩率）
# 进一步启用 LZ4（更快压缩）

limits_config:
  ingestion_rate_mb: 10      # 限制每租户速率
  ingestion_burst_size_mb: 20
  reject_old_samples: true
  reject_old_samples_max_age: 168h
```

### 3. Retention（保留期）

```yaml
limits_config:
  retention_period: 744h   # 31 天
  # 超期自动删除

compactor:
  working_directory: /loki/compactor
  compaction_interval: 10m
  retention_enabled: true
  retention_delete_delay: 2h
  delete_request_store: filesystem
```

## 写入优化

### 1. Promtail batch

```yaml
# promtail 配置
clients:
  - url: http://loki:3100/loki/api/v1/push
    batchwait: 1s          # 等待新日志的最长时间
    batchsize: 1048576     # 1MB 触发 batch
    backoff_config:
      min_period: 500ms
      max_period: 5m
```

### 2. 多租户

```yaml
# Loki 多租户隔离（auth_enabled: true）
# 每个应用/团队一个 tenant
# 限流独立（防止一个团队打爆）

auth_enabled: true

# tenant 通过 X-Scope-OrgID header 传递
```

## 查询优化

### 1. 缩小时间窗口

```logql
# 错误：查询全量
{job="nginx"} |= "error"

# 正确：限定时间窗
{job="nginx"} |= "error" [5m]
```

### 2. 利用标签

```logql
# 错误：扫描所有日志流
{job=~".+"} |= "500"

# 正确：用标签缩小范围
{job="nginx", level="error"} |= "500"
```

### 3. 控制返回行数

```logql
# LogQL 加 limit
{job="nginx"} |= "500" | limit 100
```

### 4. Metric query 用 rate

```logql
# 错误：count 然后 rate（无法计算）
count_over_time({job="nginx"} |= "500" [5m])

# 正确：用 rate
sum(rate({job="nginx"} |= "500" [5m]))
```

## 监控 Loki 自身

```promql
# Loki 写入速率
loki_distributor_lines_received_total

# Loki 摄入速率
loki_ingester_chunk_bytes_received_total

# Loki 查询延迟
loki_request_duration_seconds_bucket{path="/loki/api/v1/query"}

# 当前租户活跃 series 数
loki_ingester_active_series
```

## 一句话总结

> **Loki 最佳实践 = 标签低基数 + 存储分层 + 写入 batch + 查询窄范围**。**标签设计决定成本**。**新项目首选 Loki（监控日志）/ ES（全文检索）**。

---

## 关联章节

- [Loki 概览](../05-loki/overview.md)
- [LogQL 查询](../05-loki/logql.md)
- [Pipeline 处理](../05-loki/pipeline.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    # =====================================================================
    # 06-tracing
    # =====================================================================
    "06-tracing/tempo.md": """---
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
""",

    "06-tracing/zipkin.md": """---
title: Zipkin 链路追踪
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
docker run -d --name zipkin \
  -p 9411:9411 \
  -e STORAGE_TYPE=elasticsearch \
  -e ES_HOSTS=elasticsearch:9200 \
  openzipkin/zipkin:latest
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
java -javaagent:./opentelemetry-javaagent.jar \
     -Dotel.service.name=order-service \
     -Dotel.exporter.zipkin.endpoint=http://zipkin:9411/api/v2/spans \
     -jar order-service.jar
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
""",

    "06-tracing/protocol-compare.md": """---
title: Tracing 协议对比
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
""",

    # =====================================================================
    # 07-elk-efk
    # =====================================================================
    "07-elk-efk/fluentd.md": """---
title: Fluentd 日志采集
description: CNCF 毕业的统一日志层
---

# Fluentd 日志采集

> **TL;DR**：Fluentd = **CNCF 毕业的统一日志采集层**（2019）**。**类比 Logstash，但更轻量（Ruby 写）**。**核心架构：Input → Filter → Output（pipeline plugin）**。**生态丰富：1000+ 插件（源 + 过滤 + 输出）**。**K8s 场景：Fluent Bit（轻量版，Go 写）**。

## 一句话定义

```
Fluentd = CNCF 毕业的统一日志采集器
       = Ruby 写（C 扩展加速），基于 jemalloc
       = 设计：Input → Filter → Output pipeline
       = 插件架构：1000+ 插件（Source / Filter / Output）
       = 轻量版：Fluent Bit（Go 写，CNCF 子项目）
```

## 与 Filebeat / Logstash 对比

| 维度 | Fluentd | Fluent Bit | Filebeat | Logstash |
|---|---|---|---|---|
| 语言 | Ruby + C | Go + C | Go | JRuby |
| 内存 | 40-60MB | 5-10MB | 30-50MB | 200-500MB |
| 插件 | 1000+ | 70+ | 30+ | 200+ |
| 解析能力 | 强（filter DSL） | 中 | 弱 | 极强（grok） |
| 路由能力 | 极强（match + rewrite） | 中 | 弱 | 强 |
| 适用 | 复杂路由 | K8s sidecar / DaemonSet | 简单日志采集 | ELK 重度处理 |

## 架构

```
Input Plugin → Buffer → Filter Plugin → Buffer → Output Plugin
   (tail)       chunk    (parse/regex)    chunk    (ES/S3/HTTP)
                          (geoip enrich)
                          (record_transform)
```

## 配置示例

```ruby
# /etc/fluent/fluent.conf
<source>
  @type tail
  path /var/log/app/*.log
  pos_file /var/log/fluentd.pos
  tag app.logs
  <parse>
    @type json
    time_key timestamp
    time_format %Y-%m-%dT%H:%M:%S.%LZ
  </parse>
</source>

<filter app.logs>
  @type record_transformer
  enable_ruby true
  <record>
    hostname ${hostname}
    env "prod"
  </record>
</filter>

<filter app.logs>
  @type grep
  <regexp>
    key level
    pattern /^(error|warn|info)$/
  </regexp>
</filter>

<match app.logs>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name app-logs-${tag[1]}-%Y.%m.%d
  flush_interval 10s
  buffer_type file
  buffer_path /var/log/fluentd/buffer
  retry_max_times 5
</match>
```

## K8s 部署（Fluent Bit）

```yaml
# DaemonSet：每个 K8s 节点一份
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluent-bit
spec:
  template:
    spec:
      containers:
        - name: fluent-bit
          image: fluent/fluent-bit:2.2
          volumeMounts:
            - name: varlog
              mountPath: /var/log
            - name: varlibdockercontainers
              mountPath: /var/lib/docker/containers
              readOnly: true
            - name: fluent-bit-config
              mountPath: /fluent-bit/etc/
      volumes:
        - name: varlog
          hostPath: { path: /var/log }
        - name: varlibdockercontainers
          hostPath: { path: /var/lib/docker/containers }
        - name: fluent-bit-config
          configMap:
            name: fluent-bit-config
```

```ini
# fluent-bit ConfigMap
[INPUT]
    Name              tail
    Path              /var/log/containers/*.log
    Parser            docker
    Tag               kube.*
    Refresh_Interval  5

[FILTER]
    Name              kubernetes
    Match             kube.*
    Kube_URL          https://kubernetes.default.svc:443
    Kube_CA_File      /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    Kube_Token_File   /var/run/secrets/kubernetes.io/serviceaccount/token
    Merge_Log         On
    Merge_Log_Key     log_processed

[OUTPUT]
    Name              loki
    Match             *
    Host              loki
    Port              3100
    Labels            job=fluent-bit,k8s_namespace_name=$kubernetes['namespace_name']
```

## 一句话总结

> **Fluentd = CNCF 统一日志层**。**Fluent Bit（Go 轻量版）= K8s sidecar / DaemonSet 首选**。**复杂场景用 Fluentd（强大 filter DSL）**。

---

## 关联章节

- [ES 日志存储](./elasticsearch-logs.md)
- [Kibana](./kibana.md)
- [Filebeat](./filebeat.md)
- [K8s 监控](../11-scenarios/k8s-monitor.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "07-elk-efk/filebeat.md": """---
title: Filebeat 轻量日志采集
description: Elastic 官方的轻量采集器
---

# Filebeat 轻量日志采集

> **TL;DR**：Filebeat = **Elastic 官方的轻量日志采集器（Go 写，Go 替代了 Logstash shipper）**。**功能：tail 日志 → 解析 → 发送到 Elasticsearch / Logstash / Kafka**。**内置模块：system / nginx / mysql / kafka 等开箱即用**。**K8s 场景：DaemonSet 部署 + 自动发现容器日志**。

## 一句话定义

```
Filebeat = Elastic 官方轻量日志采集器
        = Go 写，资源占用低（< 50MB 内存）
        = 设计：Prospector（发现日志文件）+ Harvester（采集行）+ Spooler（缓冲）
        = 替代 Logstash 做 shipper（Logstash 退居 filter/aggregation）
```

## 架构

```
┌──────────────────────────────────────┐
│  Filebeat                            │
│  ┌────────────────┐  ┌────────────┐  │
│  │ Prospector     │→ │ Harvester  │  │
│  │  监控目录       │  │ 读新行      │  │
│  └────────────────┘  └─────┬──────┘  │
│                            │         │
│                     ┌──────▼──────┐  │
│                     │ Spooler     │  │
│                     │ (缓冲)      │  │
│                     └──────┬──────┘  │
│                            │         │
│                     ┌──────▼──────┐  │
│                     │ Output      │  │
│                     │ (ES/Logstash│  │
│                     └─────────────┘  │
└──────────────────────────────────────┘
```

## 配置示例

```yaml
# filebeat.yml
filebeat.inputs:
  # 1. 通用日志输入
  - type: log
    enabled: true
    paths:
      - /var/log/app/*.log
    parsers:
      - ndjson:
          target: ""
          overwrite_keys: true
          add_error_key: true
    fields:
      env: prod
      service: order-api
    fields_under_root: true

  # 2. 容器日志（K8s 场景）
  - type: container
    enabled: true
    paths:
      - /var/log/containers/*.log
    json.keys_under_root: true
    json.add_error_key: true
    json.message_key: log

filebeat.config.modules:
  path: ${path.config}/modules.d/*.yml
  reload.enabled: true

processors:
  - add_host_metadata: ~
  - add_cloud_metadata: ~
  - add_kubernetes_metadata: ~   # K8s 元数据

output.elasticsearch:
  hosts: ["https://elasticsearch:9200"]
  username: "filebeat_writer"
  password: "${ES_PASSWORD}"
  index: "app-logs-%{+yyyy.MM.dd}"
  ssl.certificate_authorities: ["/etc/ca.crt"]
  pipeline: "app-logs-pipeline"

setup.template.name: "app-logs"
setup.template.pattern: "app-logs-*"
setup.ilm.enabled: true
setup.ilm.policy: "logs-lifecycle"

logging.level: info
```

## 内置模块（开箱即用）

```bash
# 启用模块
filebeat modules enable system nginx mysql redis kafka

# 模块目录：/etc/filebeat/modules.d/
# - system.yml: 系统日志（syslog / auth.log）
# - nginx.yml: nginx access / error log
# - mysql.yml: mysql slow log / error log
# - redis.yml: redis slowlog
# - kafka.yml: kafka server log
# - elasticsearch.yml: ES server log
```

## K8s 部署

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: filebeat
  namespace: kube-system
spec:
  template:
    spec:
      serviceAccountName: filebeat
      containers:
        - name: filebeat
          image: docker.elastic.co/beats/filebeat:8.13.0
          args:
            - "-c"
            - "/etc/filebeat.yml"
            - "-e"
          env:
            - name: ES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: elastic-credentials
                  key: password
          volumeMounts:
            - name: config
              mountPath: /etc/filebeat.yml
              subPath: filebeat.yml
            - name: data
              mountPath: /var/lib/filebeat-data
            - name: varlog
              mountPath: /var/log
            - name: varlibdockercontainers
              mountPath: /var/lib/docker/containers
              readOnly: true
      volumes:
        - name: config
          configMap:
            name: filebeat-config
        - name: data
          hostPath: { path: /var/lib/filebeat-data, type: DirectoryOrCreate }
        - name: varlog
          hostPath: { path: /var/log }
        - name: varlibdockercontainers
          hostPath: { path: /var/lib/docker/containers }
```

## Filebeat vs Fluent Bit

| 维度 | Filebeat | Fluent Bit |
|---|---|---|
| 内存 | 30-50MB | 5-10MB |
| 插件 | 30+（少） | 70+ |
| 模板化 | 内置模块丰富 | 需要自定义 |
| K8s 集成 | 完善（官方支持） | 完善 |
| 学习曲线 | 低 | 中 |

## 一句话总结

> **Filebeat = Elastic 官方轻量采集器**。**内置模块开箱即用**。**K8s DaemonSet 部署 + 自动发现容器日志**。

---

## 关联章节

- [ES 日志存储](./elasticsearch-logs.md)
- [Kibana](./kibana.md)
- [Fluentd](./fluentd.md)
- [K8s 监控](../11-scenarios/k8s-monitor.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    # =====================================================================
    # 08-alerting
    # =====================================================================
    "08-alerting/severity.md": """---
title: 告警分级
description: P0/P1/P2/P3 与响应 SLO
---

# 告警分级

> **TL;DR**：**告警分级 = 给每条告警打上 P0 / P1 / P2 / P3**，**对应不同的响应时间 + 通知渠道**。**P0：电话立即响应（5min）/ P1：Slack + Slack 提及（15min）/ P2：Slack 普通消息（4h）/ P3：工单（24h）**。**Google SRE 推荐：P0 月均 ≤ 5 次/人**。

## 一句话定义

```
告警分级 = 严重度等级 + 响应 SLO + 通知渠道
       = 让 on-call 知道该多紧急
       = P0/P1/P2/P3 是工业标准
       = 配套：响应时间 / 升级链 / 复盘要求
```

## P0 - 严重（Critical）

```
定义：影响核心业务 / 用户感知严重 / 资金损失
例：
  - 核心交易全挂（订单 / 支付）
  - 数据丢失 / 数据损坏
  - 安全事故（数据泄露 / 入侵）
  - SLO breach 严重（错误率 > 25%）

响应 SLO：
  - 5 分钟内 ack
  - 30 分钟内止血（恢复 / 回滚 / 限流）
  - 24 小时内复盘

通知渠道：
  - PagerDuty / OpsGenie（电话 + SMS + Slack）
  - 升级链：on-call → 主管 → VP → CTO（5min 一级）
  - 应急频道：#incident-{date}
```

## P1 - 高（High）

```
定义：服务降级但可用 / 影响部分用户
例：
  - 单一服务错误率高（5%-25%）
  - 核心接口 P99 > 5s
  - 数据延迟（非丢失）
  - 容量预警（资源 80%+）

响应 SLO：
  - 15 分钟内 ack
  - 4 小时内解决
  - 48 小时内复盘

通知渠道：
  - Slack 频道 @here
  - 升级链：on-call → 主管（30min）
```

## P2 - 中（Medium）

```
定义：可观察但不影响用户 / 待办事项
例：
  - 资源使用率高（70-80%）
  - 批处理任务失败
  - 报表延迟
  - 非核心接口异常

响应 SLO：
  - 4 小时内 ack
  - 下个工作日解决
  - 不强制复盘

通知渠道：
  - Slack 普通消息
  - 不打电话
```

## P3 - 低（Low）

```
定义：信息性 / 不需要立即处理
例：
  - 性能优化建议
  - 容量趋势预警（3 个月后耗尽）
  - 安全补丁
  - 日志清理

响应 SLO：
  - 下个工作日 ack
  - 1 周内解决
  - 工单跟踪

通知渠道：
  - 工单系统（Jira / Linear）
  - 周报汇总
```

## Prometheus Alert 实战分级

```yaml
groups:
  - name: severity-tiers
    rules:
      # === P0 ===
      - alert: PaymentServiceDown
        expr: up{job="payment-service"} == 0
        for: 1m
        labels:
          severity: critical    # → P0
          pager: true
        annotations:
          runbook: https://wiki/runbooks/payment-down

      - alert: OrderErrorRateCritical
        expr: |
          sum(rate(http_requests_total{service="order", status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total{service="order"}[5m]))
          > 0.25
        for: 2m
        labels:
          severity: critical

      # === P1 ===
      - alert: HighLatencyP99
        expr: |
          histogram_quantile(0.99,
            sum by (le, service) (rate(http_request_duration_seconds_bucket[5m]))
          ) > 5
        for: 10m
        labels:
          severity: warning      # → P1

      - alert: ErrorRateWarning
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum(rate(http_requests_total[5m]))
          > 0.05
        for: 5m
        labels:
          severity: warning

      # === P2 ===
      - alert: DiskSpaceWarning
        expr: |
          (1 - node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"}
          / node_filesystem_size_bytes) > 0.8
        for: 30m
        labels:
          severity: info         # → P2

      # === P3 ===
      - alert: CertificateExpiresSoon
        expr: probe_ssl_earliest_cert_expiry - time() < 86400 * 30
        for: 1h
        labels:
          severity: low          # → P3
```

## Alertmanager 路由配置

```yaml
route:
  receiver: 'default'
  group_by: [alertname, severity]
  routes:
    # P0 → 电话 + SMS
    - matchers: [{name="severity", value="critical"}]
      receiver: 'pagerduty-p0'
      group_wait: 10s
      group_interval: 1m
      repeat_interval: 15m

    # P1 → Slack @here
    - matchers: [{name="severity", value="warning"}]
      receiver: 'slack-warning'
      group_wait: 1m
      repeat_interval: 4h

    # P2 → Slack 普通
    - matchers: [{name="severity", value="info"}]
      receiver: 'slack-info'
      group_wait: 5m
      repeat_interval: 24h

    # P3 → Jira 工单
    - matchers: [{name="severity", value="low"}]
      receiver: 'jira-ticket'
      group_wait: 1h
      repeat_interval: 168h   # 一周
```

## 月均告警指标

```
Google SRE 推荐：
  - P0: ≤ 5 次/人/月
  - P1: ≤ 10 次/人/月
  - P2 + P3: ≤ 30 次/人/月
  - 总告警：≤ 50 次/人/月

超过指标 → 重新审视告警分级
告警疲劳 → on-call 倦怠 → 重要告警被忽略
```

## 一句话总结

> **告警分级 = P0/P1/P2/P3**。**响应时间：5min/15min/4h/24h**。**通知渠道：电话+SMS / Slack @here / Slack / 工单**。**P0 ≤ 5 次/人/月，否则就是分级有问题**。

---

## 关联章节

- [Alertmanager](./alertmanager.md) — 告警如何路由
- [静默规则](./silence.md) — 已知问题屏蔽
- [On-call](./oncall.md) — 值班文化
- [SLI/SLO](../01-foundations/sli-slo.md) — SLO breach 对应 P0/P1

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "08-alerting/silence.md": """---
title: 告警静默
description: Silence / 维护窗口 / 已知问题屏蔽
---

# 告警静默

> **TL;DR**：**Silence = 临时屏蔽特定告警**（维护窗口 / 已知问题 / 演练）。**Alertmanager + Grafana 都支持**。**关键：必须有到期时间 + matcher + 创建人**，**避免"永不过期"的 silence**。

## 一句话定义

```
Silence = 临时屏蔽告警规则匹配
       = 不会触发，不会通知
       = 但 PromQL 仍正常评估（只是不进 Alertmanager）
       = 用途：维护窗口 / 已知问题 / 故障演练 / 升级演练
```

## Alertmanager 静默（amtool）

```bash
# 1. 创建 silence（4 小时屏蔽，匹配 service=order, severity=warning）
amtool silence add \
  --alertmanager.url=http://alertmanager:9093 \
  --comment "DB 升级维护窗口" \
  --start="2026-08-09 14:00:00" \
  --end="2026-08-09 18:00:00" \
  --matcher service=order \
  --matcher severity=warning

# 2. 查询 silence
amtool silence query \
  --alertmanager.url=http://alertmanager:9093

# 3. 提前结束 silence
amtool silence expire \
  --alertmanager.url=http://alertmanager:9093 \
  <silence-id>
```

## Alertmanager UI 创建

```
1. 打开 http://alertmanager:9093/#/silences
2. 点击 "New Silence"
3. 设置 matcher（如 service=order, severity=critical）
4. 设置 start / end 时间
5. 填 comment / 创建人
6. Submit

UI 会显示所有 active / pending / expired silences
```

## Grafana 静默

```bash
# 通过 API 创建 silence
curl -X POST http://admin:[email protected]/api/v1/provisioning/alert/rules \
  -H "Content-Type: application/json" \
  -d '{
    "matchers": [
      {"name": "service", "value": "order"},
      {"name": "severity", "value": "warning"}
    ],
    "startsAt": "2026-08-09T14:00:00Z",
    "endsAt": "2026-08-09T18:00:00Z",
    "comment": "DB 升级",
    "createdBy": "ops-team"
  }'
```

## 实战场景

### 1. 计划维护窗口

```yaml
# 数据库迁移维护：周六 02:00 - 06:00
# 提前 1 周创建 silence
silence:
  matchers:
    - name: service
      value: db-migration
    - name: severity
      value: ~"warning|critical"   # 正则匹配
  time:
    start: "2026-08-15 02:00:00"
    end: "2026-08-15 06:00:00"
  comment: "DB 迁移维护（PRG-1234）"
  created_by: "alice"
```

### 2. 已知问题（带工单）

```yaml
silence:
  matchers:
    - name: alertname
      value: "HighMemoryUsage"
    - name: instance
      value: "web-3"
  time:
    start: "now"
    end: "now + 7d"     # 最多 7 天
  comment: "已知内存泄漏，JIRA-1234 处理中"
  created_by: "bob"
```

### 3. 演练

```yaml
silence:
  matchers:
    - name: severity
      value: "warning"
  time:
    start: "now"
    end: "now + 2h"
  comment: "2026 春季故障演练，warning 级别暂屏蔽"
  created_by: "sre-team"
```

## Silence 与 Inhibit 的区别

| 维度 | Silence | Inhibit |
|---|---|---|
| 触发 | 手动 / 定时 | 自动（更高 severity 触发） |
| 范围 | 任意 matcher | 关联告警（如 cluster 全挂 → 抑制该 cluster 其他） |
| 时间 | 有 end time | 实时 |
| 用途 | 维护 / 演练 / 已知问题 | 告警噪音减少（避免告警风暴） |
| 管理 | amtool / UI | alertmanager.yml |

## 一句话总结

> **Silence = 临时屏蔽告警**。**必须有 end time + matcher + 创建人 + comment**。**Alertmanager + Grafana 都支持**。

---

## 关联章节

- [Alertmanager](./alertmanager.md) — 告警如何路由
- [告警分级](./severity.md) — P0/P1/P2/P3
- [On-call](./oncall.md) — 值班文化

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    # =====================================================================
    # 09-app-instrumentation
    # =====================================================================
    "09-app-instrumentation/jvm-metrics.md": """---
title: JVM 指标采集
description: JMX / Micrometer / async-profiler
---

# JVM 指标采集

> **TL;DR**：**JVM 指标采集 = JMX → Prometheus 格式**。**主流方案：Micrometer + Prometheus Registry + JMX Exporter**。**关键指标：堆内存 / GC / 线程 / 类加载 / JIT**。**生产必备：堆内存 + GC 暂停时间 + 线程数 + JIT 编译**。

## 一句话定义

```
JVM 指标 = Java 应用的内部状态
        = 通过 JMX 暴露
        = 转换为 Prometheus 格式后抓取
        = 工具：Micrometer / JMX Exporter / async-profiler
```

## Micrometer + Prometheus（推荐）

```xml
<!-- Maven 依赖 -->
<dependency>
  <groupId>io.micrometer</groupId>
  <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

```java
// Spring Boot 自动配置（application.yml）
management:
  endpoints:
    web:
      exposure:
        include: health, info, metrics, prometheus
  metrics:
    tags:
      application: order-service
    distribution:
      percentiles-histogram:
        http.server.requests: true
      percentiles:
        http.server.requests: 0.5, 0.95, 0.99
```

```java
// 手动埋点
@RestController
public class OrderController {
    private final Counter orderCounter;
    private final Timer orderTimer;

    public OrderController(MeterRegistry registry) {
        this.orderCounter = Counter.builder("orders.processed")
            .tag("status", "success")
            .register(registry);
        this.orderTimer = Timer.builder("orders.duration")
            .publishPercentiles(0.5, 0.95, 0.99)
            .register(registry);
    }

    @PostMapping("/orders")
    public Order create() {
        return orderTimer.record(() -> {
            // 业务
            orderCounter.increment();
            return newOrder;
        });
    }
}
```

## JMX Exporter（独立 Java agent）

```bash
# 1. 下载 jmx_prometheus_javaagent
curl -L -o jmx_prometheus_javaagent.jar \
  https://github.com/prometheus/jmx_exporter/releases/latest/download/jmx_prometheus_javaagent.jar

# 2. 创建 config.yml
cat > config.yml << 'EOF'
---
lowercaseOutputName: true
lowercaseOutputLabelNames: true
rules:
  - pattern: 'java.lang<type=Memory><HeapMemoryUsage>(\w+):'
    name: jvm_memory_heap_bytes
    type: GAUGE
    attrNameSnakeCase: true
    labels:
      area: heap
  - pattern: 'java.lang<type=Memory><NonHeapMemoryUsage>(\w+):'
    name: jvm_memory_nonheap_bytes
    type: GAUGE
    labels:
      area: nonheap
  - pattern: 'java.lang<type=GarbageCollector, name=(\w+)><CollectionCount>'
    name: jvm_gc_collection_seconds_count
    type: COUNTER
    labels:
      gc: $1
  - pattern: 'java.lang<type=GarbageCollector, name=(\w+)><CollectionTime>'
    name: jvm_gc_collection_seconds_sum
    type: COUNTER
    labels:
      gc: $1
  - pattern: 'java.lang<type=Threading><(.*)>'
    name: jvm_threads_$2
    type: GAUGE
EOF

# 3. 启动 jar
java -javaagent:./jmx_prometheus_javaagent.jar=8080:config.yml \
     -jar order-service.jar
```

## 关键 JVM 指标

```promql
# 1. 堆内存使用
jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} * 100

# 2. GC 暂停时间（最关键）
rate(jvm_gc_collection_seconds_sum[5m])
/ rate(jvm_gc_collection_seconds_count[5m])
# G1 通常 5-50ms，ZGC/Shenandoah < 1ms

# 3. GC 频率
rate(jvm_gc_collection_seconds_count[5m])

# 4. 活跃线程
jvm_threads_current

# 5. 守护线程
jvm_threads_daemon

# 6. 类加载
jvm_classes_loaded

# 7. JIT 编译（OpenJ9 才有，HotSpot 不暴露）

# 8. JVM CPU
process_cpu_seconds_total
```

## 实战告警

```yaml
# Prometheus rules
- alert: JVMHeapHigh
  expr: jvm_memory_used_bytes{area="heap"} / jvm_memory_max_bytes{area="heap"} > 0.85
  for: 5m
  labels: {severity: warning}
  annotations:
    summary: "堆内存使用率 > 85%"

- alert: JVMLongGCPause
  expr: |
    rate(jvm_gc_collection_seconds_sum[5m])
    / rate(jvm_gc_collection_seconds_count[5m])
    > 0.1   # 100ms
  for: 5m
  labels: {severity: warning}
  annotations:
    summary: "平均 GC 暂停 > 100ms（考虑 G1 → ZGC）"

- alert: JVMThreadLeak
  expr: |
    jvm_threads_current
    >
    jvm_threads_current offset 1h * 1.5   # 1 小时增长 50%
  for: 10m
  labels: {severity: critical}
  annotations:
    summary: "线程数 1h 内增长 50%（可能是线程泄漏）"
```

## GC 选择对比

| GC | 暂停时间 | 适用 |
|---|---|---|
| G1 | 50-200ms | 默认 / 通用 |
| ZGC | < 1ms | 大堆（>32G）/ 低延迟 |
| Shenandoah | < 1ms | 低延迟（同 ZGC） |
| Parallel | 100ms+ | 高吞吐 / 批处理 |
| CMS | 已废弃 | 不要再用 |

## 一句话总结

> **JVM 指标 = Micrometer + JMX Exporter**。**关键指标：堆 / GC / 线程 / 类加载**。**GC 暂停 < 100ms 是健康值**。**大堆 + 低延迟选 ZGC / Shenandoah**。

---

## 关联章节

- [RED 方法](./red-method.md) — 服务级指标
- [USE 方法](./use-method.md) — JVM 即资源
- [业务指标](./business-metrics.md) — 业务维度
- [持续剖析](../10-profiling/continuous-profiling.md) — 更深定位

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "09-app-instrumentation/k8s-metrics.md": """---
title: K8s 指标采集
description: kube-state-metrics / cAdvisor / Prometheus Operator
---

# K8s 指标采集

> **TL;DR**：**K8s 指标采集 = kube-state-metrics（K8s 对象）+ cAdvisor（容器）+ node-exporter（主机）+ Prometheus Operator（部署）**。**生产标配：kube-prometheus-stack Helm Chart（一键全套）**。**指标涵盖：Pod / Deployment / Node / PVC / Service / Ingress**。

## 一句话定义

```
K8s 指标采集 = 4 类 exporter 配合
             = node-exporter（主机）
             = cAdvisor（容器，kubelet 内置）
             = kube-state-metrics（K8s 对象状态）
             = Prometheus Operator（自动化）

完整可观测：
  Prometheus + Alertmanager + Grafana + node-exporter + kube-state-metrics
```

## kube-prometheus-stack（一键部署）

```bash
# Helm 安装
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

```
自动部署：
  - prometheus-operator
  - prometheus（StatefulSet）
  - alertmanager（StatefulSet）
  - grafana（Deployment）
  - node-exporter（DaemonSet）
  - kube-state-metrics（Deployment）
  - 预置 ServiceMonitor / PrometheusRule / Grafana Dashboard
```

## kube-state-metrics 关键指标

```promql
# 1. Pod 状态
kube_pod_status_phase{phase="Running"}        # 运行中的 pod
kube_pod_container_status_ready                # 容器就绪
kube_pod_container_status_restart_total       # 重启次数

# 2. Deployment 状态
kube_deployment_status_replicas_available      # 可用副本数
kube_deployment_spec_replicas                  # 期望副本数

# 3. Node 状态
kube_node_status_condition{condition="Ready",status="true"}

# 4. PVC / PV
kube_persistentvolumeclaim_status_phase{phase="Bound"}

# 5. 资源请求 / 限制（用于容量规划）
kube_pod_container_resource_requests{resource="cpu"}
kube_pod_container_resource_limits{resource="memory"}
```

## cAdvisor / kubelet 指标

```promql
# 1. 容器 CPU 使用
rate(container_cpu_usage_seconds_total{name!="", name!="POD"}[5m])

# 2. 容器内存使用
container_memory_usage_bytes{name!="", name!="POD"}

# 3. 容器网络 IO
rate(container_network_receive_bytes_total[5m])
rate(container_network_transmit_bytes_total[5m])

# 4. 容器文件系统
container_fs_usage_bytes

# 5. OOM 事件（重启原因）
kube_pod_container_status_last_terminated_reason{reason="OOMKilled"}
```

## 实战告警

```yaml
groups:
  - name: k8s-alerts
    rules:
      # Pod 频繁重启
      - alert: PodCrashLooping
        expr: |
          rate(kube_pod_container_status_restart_total[10m]) > 0
        for: 5m
        labels: {severity: warning}

      # 容器 OOMKilled
      - alert: ContainerOOMKilled
        expr: |
          kube_pod_container_status_last_terminated_reason{reason="OOMKilled"} == 1
        for: 0m
        labels: {severity: critical}

      # Pod Pending 超过 5 分钟
      - alert: PodPendingLong
        expr: kube_pod_status_phase{phase="Pending"} == 1
        for: 5m
        labels: {severity: warning}

      # 节点 NotReady
      - alert: NodeNotReady
        expr: |
          kube_node_status_condition{condition="Ready",status="true"} == 0
        for: 2m
        labels: {severity: critical}

      # PVC Pending（存储问题）
      - alert: PVCPending
        expr: |
          kube_persistentvolumeclaim_status_phase{phase="Pending"} == 1
        for: 5m
        labels: {severity: warning}

      # 节点磁盘即将耗尽
      - alert: NodeDiskPressure
        expr: |
          (1 - node_filesystem_avail_bytes{mountpoint="/"}
          / node_filesystem_size_bytes{mountpoint="/"}) > 0.85
        for: 10m
        labels: {severity: warning}

      # Deployment 副本不足
      - alert: DeploymentReplicasMismatch
        expr: |
          kube_deployment_status_replicas_available
          != kube_deployment_spec_replicas
        for: 5m
        labels: {severity: critical}
```

## Prometheus Operator 优势

```
1. ServiceMonitor：自动发现 + 抓取配置（CRD）
2. PrometheusRule：告警规则 CRD
3. AlertmanagerConfig：Alertmanager 路由 CRD
4. Grafana Dashboard 自动导入

# ServiceMonitor 示例（自动抓取 ingress-nginx）
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: ingress-nginx
  labels:
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: ingress-nginx
  endpoints:
    - port: metrics
      interval: 30s
```

## 一句话总结

> **K8s 监控 = kube-prometheus-stack（Helm 一键）+ 4 类指标**。**关键告警：Pod 重启 / OOMKilled / Node NotReady / PVC Pending**。**生产必备**。

---

## 关联章节

- [K8s 监控](../11-scenarios/k8s-monitor.md)
- [Exporter](../03-prometheus/exporter.md)
- [Prometheus 告警](../03-prometheus/alert.md)
- [PromQL](../03-prometheus/promql.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    # =====================================================================
    # 10-profiling
    # =====================================================================
    "10-profiling/pprof.md": """---
title: Go pprof 剖析
description: Go 内置的性能剖析工具
---

# Go pprof 剖析

> **TL;DR**：**Go pprof = Go 内置的 profiler**（runtime/pprof 包 + net/http/pprof）。**支持 5 类 profile：CPU / Heap / Goroutine / Block / Mutex**。**可视化：go tool pprof + 火焰图（brendangregg/FlameGraph）**。**生产标配：开启 pprof HTTP 端口 + 持续收集 + 自动化分析**。

## 一句话定义

```
Go pprof = Go runtime 内置的性能剖析工具
         = 5 类 profile：
           - CPU（CPU 时间）
           - Heap（堆内存分配）
           - Goroutine（协程栈）
           - Block（阻塞事件）
           - Mutex（锁竞争）
         = 可视化：火焰图 / 树状图 / 调用图
```

## 启用 pprof

```go
// 1. 在 main 函数中开启（生产环境）
import (
    "net/http"
    _ "net/http/pprof"   // 自动注册 /debug/pprof 路由
)

func main() {
    go func() {
        http.ListenAndServe("localhost:6060", nil)
    }()
    // 业务代码
}
```

```bash
# 2. 抓取 profile
# CPU profile（30 秒）
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Heap profile（堆内存）
go tool pprof http://localhost:6060/debug/pprof/heap

# Goroutine（当前所有 goroutine 栈）
go tool pprof http://localhost:6060/debug/pprof/goroutine

# Block（阻塞事件）
go tool pprof http://localhost:6060/debug/pprof/block

# Mutex（锁竞争）
go tool pprof http://localhost:6060/debug/pprof/mutex
```

## 火焰图生成

```bash
# 1. 安装 FlameGraph 脚本
git clone https://github.com/brendangregg/FlameGraph.git
export PATH=$PATH:./FlameGraph

# 2. CPU profile → 火焰图
go tool pprof -raw -output=cpu.raw http://localhost:6060/debug/pprof/profile?seconds=30
go tool pprof -top cpu.raw

# 或生成火焰图 SVG
go tool pprof -svg cpu.raw > cpu.svg

# 3. 直接可视化
go tool pprof -http=:8080 http://localhost:6060/debug/pprof/profile?seconds=30
# 浏览器打开 http://localhost:8080
```

## Heap 分析

```bash
# 1. 当前内存使用
go tool pprof -inuse_space http://localhost:6060/debug/pprof/heap

# 2. 累计分配字节（找内存泄漏点）
go tool pprof -alloc_space http://localhost:6060/debug/pprof/heap

# 3. 累计分配对象数
go tool pprof -alloc_objects http://localhost:6060/debug/pprof/heap

# 4. 找泄漏 goroutine
curl http://localhost:6060/debug/pprof/goroutine?debug=2 > goroutine.txt
# 看 goroutine 数量 + 阻塞在哪个 channel/lock
```

## 持续剖析（Pyroscope 集成）

```go
// 用 Pyroscope + pprof 自动采集
import "github.com/grafana/pyroscope-go"

func main() {
    pyroscope.Start(pyroscope.Config{
        ApplicationName: "my-service",
        ServerAddress:   "http://pyroscope:4040",
        Tags: map[string]string{
            "env":     "prod",
            "version": "1.0.0",
        },
        ProfileTypes: []pyroscope.ProfileType{
            pyroscope.ProfileCPU,
            pyroscope.ProfileAllocObjects,
            pyroscope.ProfileAllocSpace,
            pyroscope.ProfileInuseObjects,
            pyroscope.ProfileInuseSpace,
            pyroscope.ProfileGoroutines,
        },
    })
    // 业务代码
}
```

## 实战案例：定位内存泄漏

```bash
# 1. 抓两次 heap（间隔 5 分钟）
curl -o heap1.pb.gz http://localhost:6060/debug/pprof/heap
sleep 300
curl -o heap2.pb.gz http://localhost:6060/debug/pprof/heap

# 2. 对比两次内存增长
go tool pprof -base heap1.pb.gz heap2.pb.gz
# (pprof) top
# Showing nodes accounting for 1500MB, 95% of 1580MB total
#       flat  flat%   sum%        cum   cum%
#    1200MB 75.9% 75.9%   1200MB 75.9%  bytes.makeSlice
#     200MB 12.7% 88.6%    300MB 19.0%  cache.(*LRU).Add

# 3. 火焰图看调用链
go tool pprof -http=:8080 -base heap1.pb.gz heap2.pb.gz
```

## 实战案例：定位 goroutine 泄漏

```bash
# 1. 看 goroutine 数量
curl http://localhost:6060/debug/pprof/goroutine?debug=1 | head -20

# 2. dump 所有 goroutine
curl http://localhost:6060/debug/pprof/goroutine?debug=2 > goroutines.txt
grep -A 20 "goroutine profile:" goroutines.txt | head -30
# 看哪些 goroutine 数量异常（应该 ≤ CPU 数 * 2）
```

## 实战案例：定位锁竞争

```go
// 1. 在 main 中启用 mutex profile
runtime.SetMutexProfileFraction(5)   // 5% 采样
```

```bash
# 2. 抓 mutex profile
go tool pprof http://localhost:6060/debug/pprof/mutex

# (pprof) top
# Showing nodes accounting for 800ms, 90% of 888ms total
#       flat  flat%   sum%        cum   cum%
#      500ms 56.3% 56.3%    500ms 56.3%  sync.(*Mutex).Lock
#      300ms 33.8% 89.9%    800ms 90.1%  mypkg.(*Cache).Get
```

## 一句话总结

> **Go pprof = Go 内置 profiler**。**5 类 profile：CPU / Heap / Goroutine / Block / Mutex**。**生产标配：pprof HTTP 端口 + Pyroscope 持续剖析**。

---

## 关联章节

- [持续剖析](./continuous-profiling.md) — Continuous Profiling
- [Pyroscope](./pyroscope.md) — 多语言持续剖析
- [Java async-profiler](./async-profiler.md) — Java 等价工具

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "10-profiling/async-profiler.md": """---
title: Java async-profiler
description: Java 生产级低开销 profiler
---

# Java async-profiler

> **TL;DR**：**async-profiler = Java 生产级低开销 profiler（基于 asyncGetCallTrace）**。**比 perf + HotSpot 调试更稳定**，**支持 CPU / Wall clock / Allocation / Lock**。**输出 HTML / Flame Graph + JFR 格式**。**生产标配：JVM 启动参数 + 定时收集 + 告警驱动**。

## 一句话定义

```
async-profiler = async-profiler 项目（JVM 内部 profiler）
              = 2016 起源，基于 HotSpot asyncGetCallTrace API
              = 低开销（< 1% CPU）
              = 支持 4 种事件：cpu / wall / alloc / lock
              = 输出火焰图 / JFR / 文本
```

## 安装与启动

```bash
# 1. 下载 async-profiler
curl -L -o async-profiler.jar \
  https://github.com/async-profiler/async-profiler/releases/latest/download/async-profiler.jar
# 同时下载 native lib（async-profiler-2.9-linux-x64.tar.gz）
tar xzf async-profiler-2.9-linux-x64.tar.gz

# 2. 启动 JVM 时 attach
java -jar app.jar &
APP_PID=$!

# 3. 启动 profiling（30 秒 CPU profile）
./profiler.sh -e cpu -d 30 -f /tmp/cpu.html $APP_PID
# 也可以启动时 attach：java -agentpath:./libasyncProfiler.so=start,event=cpu,flamegraph -jar app.jar
```

## 常用命令

```bash
# 1. CPU 火焰图（30 秒）
./profiler.sh -e cpu -d 30 -f /tmp/cpu.html <pid>

# 2. Wall clock（包含 IO 等待）
./profiler.sh -e wall -d 30 -f /tmp/wall.html <pid>

# 3. 内存分配字节
./profiler.sh -e alloc -d 30 -f /tmp/alloc.html <pid>

# 4. 内存分配对象数
./profiler.sh -e alloc -d 30 -o jfr -f /tmp/alloc.jfr <pid>

# 5. 锁竞争
./profiler.sh -e lock -d 30 -f /tmp/lock.html <pid>

# 6. JFR 格式（导入 JDK Mission Control 分析）
./profiler.sh -e cpu -d 30 -o jfr -f /tmp/cpu.jfr <pid>

# 7. 采样频率
./profiler.sh -e cpu -i 5ms -d 30 -f /tmp/cpu.html <pid>
# 5ms = 200Hz
```

## JVM 启动时附加

```bash
# 启动时注入 async-profiler agent（推荐生产）
java -agentpath:./libasyncProfiler.so=start,event=cpu,flamegraph,interval=10ms,log=./profiler.log \
     -jar app.jar

# 同时采集多种事件
java -agentpath:./libasyncProfiler.so=start,event=cpu,alloc,lock,flamegraph \
     -jar app.jar

# 启动后远程控制（通过 HTTP / JMX）
java -agentpath:./libasyncProfiler.so=start,event=cpu,flamegraph,server=8086 \
     -jar app.jar
# 然后通过 HTTP API 控制：
curl http://localhost:8086/start?event=alloc
curl http://localhost:8086/stop
curl http://localhost:8086/threaddump
```

## 输出格式

```bash
# 1. HTML（内嵌 SVG 火焰图）
./profiler.sh -e cpu -d 30 -f cpu.html <pid>
# 浏览器打开 cpu.html

# 2. JFR（Java Flight Recorder）
./profiler.sh -e cpu -d 30 -o jfr -f cpu.jfr <pid>
# 用 JDK Mission Control / JMC Analyzer 打开

# 3. Tree 模式（文本）
./profiler.sh -e cpu -d 30 -o tree -f cpu.txt <pid>

# 4. Collapsed 模式（用于 FlameGraph 脚本）
./profiler.sh -e cpu -d 30 -o collapsed -f cpu.collapsed <pid>
./FlameGraph/flamegraph.pl --title "CPU Flame Graph" cpu.collapsed > cpu.svg
```

## 实战案例：定位 GC 频繁

```bash
# 1. 采集 alloc 事件（30 秒）
./profiler.sh -e alloc -d 30 -f alloc.html <pid>

# 2. 看火焰图
# 找最大块：通常是某个 byte[] / char[] 反复分配

# 3. 找具体代码
./profiler.sh -e alloc -d 30 -o tree -f alloc.txt <pid>
grep "allocate" alloc.txt | head -20
```

## 实战案例：定位锁竞争

```bash
# 1. 采集 lock 事件
./profiler.sh -e lock -d 30 -f lock.html <pid>

# 2. 看火焰图顶部
# 如果某个 Object.wait 或 synchronized 占大头 → 锁竞争严重

# 3. 实战解决：
#    - 用 ConcurrentHashMap 代替 Collections.synchronizedMap
#    - 用 ReentrantLock 代替 synchronized（更细粒度控制）
#    - 用 LongAdder 代替 AtomicLong（高并发写）
```

## 与 JFR 对比

| 维度 | async-profiler | JFR（Java Flight Recorder） |
|---|---|---|
| 开销 | 极低（< 1%） | 低（2-3%） |
| 火焰图 | ✓ 原生 | 需要转换 |
| JFR 格式 | ✓ | ✓ |
| 远程采集 | ✓ HTTP API | ✓ JMX |
| CPU event | ✓ | ✓ |
| Wall clock | ✓ | ✓ |
| Allocation | ✓ | ✓ |
| Lock | ✓ | ✓ |
| 推荐 | 生产首选 | JDK 自带 / JDK 17+ 已内置 |

## 一句话总结

> **async-profiler = Java 生产级 profiler**。**比 perf 稳定，比 JFR 灵活**。**火焰图一键生成**。**生产标配：JVM 启动 attach + 告警驱动 + 持续剖析**。

---

## 关联章节

- [持续剖析](./continuous-profiling.md) — Continuous Profiling
- [Pyroscope](./pyroscope.md) — 多语言平台
- [Go pprof](./pprof.md) — Go 等价工具
- [JVM 指标](../09-app-instrumentation/jvm-metrics.md) — JVM 运行时

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    # =====================================================================
    # 11-scenarios
    # =====================================================================
    "11-scenarios/database-monitor.md": """---
title: 数据库可观测性
description: MySQL / PostgreSQL / Redis 监控实践
---

# 数据库可观测性

> **TL;DR**：**数据库监控 = 连接池 + 慢查询 + 复制延迟 + 锁等待 + 缓存命中率**。**MySQL：mysqld_exporter + performance_schema**。**PostgreSQL：postgres_exporter + pg_stat_statements**。**Redis：redis_exporter + INFO 命令**。**SRE 三件套：Exporter + 慢查询日志 + EXPLAIN 分析**。

## 一句话定义

```
数据库可观测性 = 4 个维度
             = 1. 资源（CPU/内存/磁盘/连接池）
             = 2. 查询（QPS / 慢查询 / 锁）
             = 3. 复制（主从延迟 / binlog）
             = 4. 缓存（命中率 / 淘汰率）
```

## MySQL 监控

```yaml
# Prometheus mysqld_exporter
scrape_configs:
  - job_name: mysql
    static_configs:
      - targets: [mysql-exporter:9104]
    metrics_path: /metrics
```

```promql
# 1. 连接池使用率
mysql_global_status_threads_connected / mysql_global_variables_max_connections

# 2. QPS / TPS
rate(mysql_global_status_questions[5m])     # QPS
rate(mysql_global_status_com_insert[5m])    # INSERT/s
rate(mysql_global_status_com_update[5m])    # UPDATE/s

# 3. 慢查询
rate(mysql_global_status_slow_queries[5m])

# 4. InnoDB 缓冲池命中率
1 - rate(mysql_global_status_innodb_buffer_pool_reads[5m])
  / rate(mysql_global_status_innodb_buffer_pool_read_requests[5m])

# 5. 主从延迟
mysql_slave_status_seconds_behind_master

# 6. 表锁等待
mysql_global_status_table_locks_waited
```

```sql
-- 启用慢查询日志
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- 1 秒
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';

-- 查询最慢的 SQL（performance_schema）
SELECT * FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC LIMIT 10;
```

## PostgreSQL 监控

```yaml
# Prometheus postgres_exporter
scrape_configs:
  - job_name: postgres
    static_configs:
      - targets: [postgres-exporter:9187]
```

```promql
# 1. 连接池使用率
pg_stat_activity_count / pg_settings_max_connections

# 2. QPS
rate(pg_stat_database_tup_fetched[5m])    # 读
rate(pg_stat_database_tup_inserted[5m])   # 写

# 3. 慢查询（pg_stat_statements）
# 需要先 CREATE EXTENSION pg_stat_statements
# 然后用 postgres_exporter 暴露

# 4. 锁等待
pg_locks_count{mode="waiting"}

# 5. 复制延迟
pg_replication_lag_seconds

# 6. 缓存命中率
pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)
```

```sql
-- 启用 pg_stat_statements
-- postgresql.conf
shared_preload_libraries = 'pg_stat_statements'

-- CREATE EXTENSION
CREATE EXTENSION pg_stat_statements;

-- 查询最慢的 SQL
SELECT round((100 * total_time / sum(total_time) over ())::numeric, 2) AS percent,
       calls, round(total_time::numeric, 2) AS total_ms,
       round(mean_time::numeric, 2) AS mean_ms,
       substring(query, 1, 80)
FROM pg_stat_statements
ORDER BY total_time DESC LIMIT 10;
```

## Redis 监控

```yaml
# Prometheus redis_exporter
scrape_configs:
  - job_name: redis
    static_configs:
      - targets: [redis-exporter:9121]
```

```promql
# 1. QPS
rate(redis_commands_processed_total[5m])

# 2. 命中率
1 - rate(redis_keyspace_misses_total[5m])
  / rate(redis_keyspace_hits_total[5m])

# 3. 连接数
redis_connected_clients

# 4. 内存使用
redis_memory_used_bytes / redis_memory_max_bytes

# 5. 淘汰率（重要：频繁淘汰 = 容量不足）
rate(redis_evicted_keys_total[5m])

# 6. 主从延迟（master_repl_offset vs slave offset）
# redis_exporter 自动暴露
```

## 数据库告警

```yaml
# Prometheus rules
groups:
  - name: db-alerts
    rules:
      # MySQL 连接池即将耗尽
      - alert: MySQLConnectionsHigh
        expr: |
          mysql_global_status_threads_connected
          / mysql_global_variables_max_connections > 0.8
        for: 5m
        labels: {severity: warning}

      # PostgreSQL 复制延迟
      - alert: PostgresReplicationLag
        expr: pg_replication_lag_seconds > 30
        for: 2m
        labels: {severity: critical}

      # Redis 命中率低
      - alert: RedisHitRateLow
        expr: |
          1 - rate(redis_keyspace_misses_total[5m])
          / rate(redis_keyspace_hits_total[5m])
          < 0.8   # 命中率 < 80%
        for: 10m
        labels: {severity: warning}

      # Redis 频繁淘汰
      - alert: RedisEvictionRate
        expr: rate(redis_evicted_keys_total[5m]) > 100
        for: 5m
        labels: {severity: warning}
        annotations:
          summary: "Redis 频繁淘汰 key（容量不足）"

      # 慢查询 spike
      - alert: MySQLSlowQuerySpike
        expr: |
          rate(mysql_global_status_slow_queries[5m])
          > rate(mysql_global_status_slow_queries[1h] offset 1d) * 3
        for: 10m
        labels: {severity: warning}
```

## 慢查询分析流程

```
1. 触发慢查询告警
   ↓
2. 拉 slow query log
   mysqldumpslow -s t /var/log/mysql/slow.log | head
   ↓
3. 找到慢 SQL → 拿 schema
   ↓
4. EXPLAIN ANALYZE 看执行计划
   - 看是否走索引（全表扫描 = 缺索引）
   - 看 join 顺序
   - 看 rows 估算
   ↓
5. 优化：
   - 加索引
   - 改写 SQL（避免 SELECT * / 避免子查询）
   - 拆表 / 分区
   ↓
6. 验证：slow query 指标下降
```

## 一句话总结

> **DB 监控 = Exporter + 慢查询 + EXPLAIN**。**MySQL / PG / Redis 都有官方 exporter**。**关键指标：连接池 / 慢查询 / 复制延迟 / 命中率 / 淘汰率**。

---

## 关联章节

- [Exporter](../03-prometheus/exporter.md)
- [K8s 监控](./k8s-monitor.md)
- [RED 方法](../09-app-instrumentation/red-method.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "11-scenarios/microservice-trace.md": """---
title: 微服务全链路追踪
description: 跨服务 trace + 服务地图 + 依赖分析
---

# 微服务全链路追踪

> **TL;DR**：**微服务全链路追踪 = Trace 串联所有服务 + Service Map 自动生成依赖图 + SpanMetrics 生成调用指标**。**核心：W3C Trace Context（traceparent header）+ OpenTelemetry SDK 自动注入 + OTel Collector SpanMetrics 转换**。**实战：一次 HTTP 请求从 LB 到 gateway 到 5 个微服务再到 DB 的完整路径**。

## 一句话定义

```
微服务全链路追踪 = 跨服务 trace 串联
                = W3C Trace Context 标准
                = 自动生成服务地图（service map）
                = 自动生成调用关系指标（SpanMetrics）
                = 工具：OpenTelemetry SDK + Collector + Jaeger/Tempo
```

## 完整架构

```
                 ┌──────┐
   Client ──────▶│  LB  │ (envoy/nginx)
                 └──────┘
                     │ traceparent: 00-aaaa-bbbb-01
                     ▼
              ┌──────────────┐
              │   Gateway    │ (Spring Cloud Gateway)
              │  span: http  │
              └──────┬───────┘
                     │ traceparent
        ┌────────────┼────────────┐
        ▼            ▼            ▼
  ┌──────────┐ ┌──────────┐ ┌──────────┐
  │ order-   │ │ payment- │ │ user-    │
  │ service  │ │ service  │ │ service  │
  │ span:    │ │ span:    │ │ span:    │
  │ grpc     │ │ http     │ │ db       │
  └────┬─────┘ └────┬─────┘ └────┬─────┘
       │            │            │
       ▼            ▼            ▼
   ┌────────┐  ┌────────┐   ┌────────┐
   │  MySQL │  │  Redis │   │  MySQL │
   │ span:  │  │ span:  │   │        │
   │ jdbc   │  │ redis  │   │        │
   └────────┘  └────────┘   └────────┘
```

## OpenTelemetry SDK 自动注入

```bash
# Java：所有服务统一一行 javaagent
java -javaagent:./opentelemetry-javaagent.jar \
     -Dotel.service.name=order-service \
     -Dotel.exporter.otlp.endpoint=http://otel-collector:4317 \
     -jar order-service.jar

# 关键环境变量：
-Dotel.service.name=order-service           # 服务名（ServiceMap 节点）
-Dotel.propagators=tracecontext,baggage     # 跨进程传播（W3C）
-Dotel.traces.exporter=otlp                # 导出器
-Dotel.metrics.exporter=otlp
```

## W3C Trace Context 协议

```http
# HTTP 请求自动注入 traceparent header
GET /api/orders HTTP/1.1
Host: api.example.com
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: congo=t61rcWkgMzE

# 格式：
# 00 - version
# 4bf92f3577b34da6a3ce929d0e0e4736 - trace_id (32 hex chars)
# 00f067aa0ba902b7 - span_id (16 hex chars)
# 01 - flags (sampled)
```

## OTel Collector SpanMetrics

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc: { endpoint: 0.0.0.0:4317 }

processors:
  # 关键：从 span 生成 RED 指标
  spanmetrics:
    metrics_expiration: 5m
    metrics_flush_interval: 15s
    histogram: explicit
    dimensions:
      - name: http.method
        default: GET
      - name: http.status_code

exporters:
  prometheus:
    endpoint: 0.0.0.0:8889
  otlp/tempo:
    endpoint: tempo:4317
    tls: { insecure: true }

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [spanmetrics, batch]
      exporters: [otlp/tempo]

    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
```

```
SpanMetrics 自动生成指标：
  - traces.spanmetrics.calls.total{service, span_name, status_code}
  - traces.spanmetrics.duration.sum{service, span_name}
  - traces.spanmetrics.duration.bucket{service, span_name, le}
```

## Service Map 自动生成

```yaml
# Tempo / Jaeger 自动从 trace 生成依赖图
# 圆圈 = 服务，连线 = 调用关系
# 圆圈大小 = 请求量，连线粗细 = 调用次数

# 实战：在 Grafana 看 Tempo Service Map
# Explore → Tempo → Service Map 标签页
```

## 实战案例：定位慢请求

```
场景：用户反馈下单慢（10s+）

排查步骤：
  1. 打开 Grafana → APM（vía Tempo / Jaeger UI）
  2. service = order-api, lookback = 1h, minDuration = 10s
  3. 找到慢 trace → 点开
  4. 瀑布图看到 payment-service span 占 9s
  5. payment-service 内部：grpc.client 占 8s
  6. 跳到 payment-service trace → 看 bank-api 调用占 8s
  7. 结论：bank-api 通道慢
  8. 行动：切换备用通道 + 给 bank-api 反馈

无 trace 时：
  - 用户说慢 → 看指标 → 看日志 → 抓包 → 3 小时
有 trace 时：
  - 1 分钟定位到具体 span
```

## 异步上下文传播

```
陷阱：线程池 / MQ / 异步回调容易丢 trace

线程池：
  // 错误
  executor.submit(() -> {
      // 这里 trace context 丢失
      processOrder();
  });

  // 正确（Java）
  executor.submit(() -> {
      try (Scope scope = Context.current().makeCurrent()) {
          processOrder();
      }
  });

Kafka：
  // Producer 端：自动注入 traceparent 到 header
  kafkaTemplate.send(...);

  // Consumer 端：自动提取
  @KafkaListener(topics = "orders")
  public void onMessage(ConsumerRecord<String, Order> record) {
      // trace context 自动恢复
  }
```

## 一句话总结

> **微服务 trace = W3C Trace Context + OTel SDK + Collector SpanMetrics**。**一次 HTTP 请求 = 完整 trace 串联所有 span**。**自动生成 Service Map + 调用指标**。

---

## 关联章节

- [Tracing 基础](../06-tracing/concepts.md)
- [Jaeger](../06-tracing/jaeger.md)
- [Tempo](../06-tracing/tempo.md)
- [K8s 监控](./k8s-monitor.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "11-scenarios/cost-optimization.md": """---
title: 可观测成本优化
description: 存储成本 / 采样 / 保留期 / 标签基数
---

# 可观测成本优化

> **TL;DR**：**可观测成本 = 三大开销（Metrics / Logs / Traces）**。**优化策略：Metrics 降采样 + Logs 保留期分层 + Traces tail-based sampling**。**典型节省：50-80% 成本（vs 默认配置）**。**核心原则：保留有价值的，丢弃可重算的**。

## 一句话定义

```
可观测成本 = Metrics 存储（~30%）+ Logs 存储（~50%）+ Traces 存储（~20%）
         = 取决于：保留期 × 标签基数 × 采样率
         = 优化核心：丢弃不需要的，保留有用的
```

## Metrics 成本优化

### 1. 标签基数治理

```yaml
# 杀手：高基数标签
- service: order-api                  # 10 个服务 = 10
- env: prod                          # 3 个环境 = 30
- user_id: "12345"                   # 100w 用户 = 100w × 30 = 3000w 时序
                                      # 一天 100w 时序 × 30 bytes = 30GB/天
                                      # 30 天 = 900GB → 成本爆炸

# 解决：
- user_id → 移到 log / trace，不放 metric label
- bucket histogram → 用 log / quantile，不放全量时序
```

### 2. 降采样 + 长期保留

```yaml
# Prometheus remote_write + downsampling
remote_write:
  - url: http://thanos-receive:19291/api/v1/receive
    write_relabel_configs:
      - source_labels: [__name__]
        regex: 'go_.*|process_.*|node_.*'
        action: drop                  # 删掉 go runtime 指标（高基数）

# Thanos / Cortex 自动降采样
# raw → 5min → 1h 三层
# raw 保留 7d（高分辨率）
# 5min 保留 30d
# 1h 保留 1y
```

### 3. Mimir 块存储压缩

```
Mimir vs Prometheus 本地存储：
  - Mimir：对象存储（S3/GCS），压缩 + 分块，~0.1 美元/GB·月
  - Prometheus 本地：磁盘，~0.5 美元/GB·月
  - 节省：80%
```

## Logs 成本优化

### 1. 保留期分层（ILM）

```yaml
# ES ILM（详细见 elasticsearch-logs.md）
hot: 7d, 50GB shard    # 高频查询
warm: 30d              # 偶尔查询
cold: 90d, freeze      # 几乎不查
delete: 365d

# 成本估算：
# 日均 100GB × 7 天 hot = 700GB（SSD ~0.23/GB·月 = $161）
# 日均 100GB × 30 天 warm = 3000GB（HDD ~0.05/GB·月 = $150）
# 日均 100GB × 90 天 cold = 9000GB（OSS ~0.02/GB·月 = $180）
# 总计 ~$491/月
```

### 2. 采样 + 过滤

```yaml
# Promtail / Vector 端做过滤
pipeline_stages:
  - match:
      selector: '{job="nginx"}'
      stages:
        # 丢弃健康检查日志
        - drop:
            expression: ".*healthcheck.*"
        # 丢弃 2xx 成功请求（保留 4xx/5xx）
        - match:
            selector: '{status="2.."}'
            stages:
              - sampling:
                  rate: 0.01   # 只采样 1%
```

### 3. Loki 替代 ES（成本骤降）

```
ES（默认）：全文索引，每条日志都建倒排索引
  → 100GB/天 × 30天 = 3TB
  → 存储成本 $300-700/月

Loki：只索引标签，不索引内容
  → 100GB/天 × 30天 = 3TB（chunk 高度压缩）
  → 存储成本 $50-150/月
  → 节省 70%

权衡：Loki 全文检索弱（要扫 chunk），但 90% 场景够用
```

## Traces 成本优化

### 1. 采样策略

```yaml
# Head-based sampling（SDK 端决策）
processors:
  probabilistic_sampler:
    sampling_percentage: 10   # 10% 采样

# Tail-based sampling（Collector 端决策，更智能）
processors:
  tail_sampling:
    decision_wait: 10s
    num_traces: 100000
    policies:
      # 错误 100% 保留
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      # 慢请求 100% 保留
      - name: slow
        type: latency
        latency: { threshold_ms: 1000 }
      # 健康请求 5% 采样
      - name: default
        type: probabilistic
        probabilistic: { sampling_percentage: 5 }
```

### 2. 存储分层

```
Tempo / Jaeger:
  - hot: 7d，OSS + 高频查询
  - cold: 30d，对象存储 + 低频查询
  - archive: 1y，对象存储（极冷） + 不查

成本：
  - 100% 采样：100GB/天 × 30天 = 3TB × $0.02 = $60/月
  - 10% 采样：10GB/天 × 30天 = 300GB × $0.02 = $6/月
  - tail-based 5%：~5GB/天 × 30天 = 150GB × $0.02 = $3/月
  - 节省 95%
```

### 3. 协议选择

```
Zipkin → OTLP：
  - OTLP 用 protobuf（更紧凑）
  - HTTP/2 多路复用（更高效）
  - 节省带宽 30-50%
```

## 成本估算（典型 100 服务企业）

```
场景：
  - 100 微服务
  - 日均 QPS 100w
  - 日志 500GB/天
  - Trace 100% 采样 = 200GB/天

默认配置成本：
  - Prometheus: 10 节点 × 1TB × $0.5/GB·月 = $5000/月
  - ES 日志: 15TB × $0.05 = $750/月
  - Jaeger: 6TB × $0.5 = $3000/月
  - 总计: ~$9000/月

优化后：
  - Mimir（标签治理 + 降采样）: ~$500/月
  - Loki（替代 ES + 过滤 90%）: ~$150/月
  - Tempo（tail-based 5% 采样）: ~$30/月
  - 总计: ~$700/月

节省：92%
```

## 一句话总结

> **可观测成本优化 = 标签治理 + 保留分层 + 智能采样**。**90% 节省不牺牲质量**。**生产标配：Mimir + Loki + Tempo + tail-based sampling**。

---

## 关联章节

- [K8s 监控](./k8s-monitor.md)
- [Tracing 基础](../06-tracing/concepts.md)
- [Database 监控](./database-monitor.md)
- [Alertmanager](../08-alerting/alertmanager.md) — 告警也耗资源

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",
}


def main():
    """Write each CONTENT entry to its corresponding md file."""
    print(f"Total pages to generate: {len(CONTENT)}")
    written = 0
    failed = []
    for rel_path, content in CONTENT.items():
        full_path = os.path.join(DOCS_ROOT, rel_path)
        try:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
            written += 1
            size = os.path.getsize(full_path)
            print(f"  {rel_path:<55} {size:>6} bytes")
        except Exception as e:
            failed.append((rel_path, str(e)))
            print(f"  {rel_path:<55} FAILED: {e}")

    print(f"\nGenerated: {written}/{len(CONTENT)}")
    if failed:
        print(f"Failed: {len(failed)}")
        for path, err in failed:
            print(f"  {path}: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()