---
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
