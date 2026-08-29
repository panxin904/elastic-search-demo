---
title: Prometheus
---

# Prometheus - 指标采集

> Prometheus = CNCF 毕业项目，**云原生事实标准**的指标采集与监控系统。

## 🤔 为什么需要 Prometheus

```
传统监控（Zabbix / Nagios）：
  ❌ 推模式（agent 主动推）
  ❌ 集中存储（关系数据库）
  ❌ 难应对微服务瞬时扩缩

Prometheus：
  ✅ 拉模式（自服务发现）
  ✅ 时序数据库（专为指标）
  ✅ 与 k8s / Service Mesh 深度集成
  ✅ PromQL 强大查询
```

## 🏗️ 架构

```
[App / Node]  ────  /metrics  ────►  [Prometheus]
                                       │
                                  (scrape)
                                       │
                                ┌──────▼──────┐
                                │  Time-Series│
                                │  Database   │
                                └──────┬──────┘
                                       │
                            ┌──────────┼──────────┐
                            ▼          ▼          ▼
                       [Grafana] [Alertmanager] [API client]
```

| 组件 | 作用 |
|------|------|
| **Prometheus server** | 抓取 / 存储 / 查询 |
| **Pushgateway** | 短任务推数据 |
| **Alertmanager** | 告警分发 |
| **Exporters** | 各种数据源适配（node_exporter / blackbox_exporter） |
| **Grafana** | 可视化 |

## 📜 部署

### Helm 装

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 装 kube-prometheus-stack（含 Prom + Grafana + Alertmanager）
kubectl create namespace monitoring

helm install kube-prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi
```

组件：
- `prometheus-operator`
- `prometheus` (StatefulSet)
- `alertmanager` (StatefulSet)
- `grafana` (Deployment)
- `node-exporter` (DaemonSet)
- `kube-state-metrics` (Deployment)

## 🔍 ServiceMonitor（推荐）

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: myapp
  namespace: monitoring
  labels:
    release: kube-prometheus      # 让 prometheus-operator 抓取
spec:
  selector:
    matchLabels:
      app: myapp
  endpoints:
  - port: http
    interval: 30s
    path: /metrics
```

**自动发现**：Prometheus Operator 看到 ServiceMonitor → 自动配 scrape。

## 📊 关键概念

### Metric 类型

| 类型 | 含义 |
|------|------|
| Counter | 累计值（只增）— 请求数、错误数 |
| Gauge | 当前值（可增可减）— CPU、内存、温度 |
| Histogram | 分布统计 — 响应时间分布 |
| Summary | 分布统计（聚合后）— 分位数 |

### 标签（labels）

```
http_requests_total{method="GET", path="/api/users", status="200"} 1234
```

标签用于分组 / 过滤（**高基数标签会爆炸**）。

### 暴露 /metrics

```python
# Python prometheus_client
from prometheus_client import Counter, Histogram

REQUESTS = Counter('http_requests_total', 'Total HTTP requests', ['method', 'path'])
LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

@app.route('/api/users')
def handler():
    REQUESTS.labels(method='GET', path='/api/users').inc()
    with LATENCY.time():
        return get_users()
```

## 🪜 PromQL 速查

```promql
# CPU 使用率（最近 5 分钟平均）
100 - (avg by(instance)(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用
node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes

# 99 分位响应时间
histogram_quantile(0.99, sum by(le)(rate(http_request_duration_seconds_bucket[5m])))

# 错误率
sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))

# 过去 1 小时 pod 重启次数
increase(kube_pod_container_status_restarts_total[1h])

# 看 top 5 高 CPU pod
topk(5, sum by(pod)(rate(container_cpu_usage_seconds_total[5m])))
```

## 🚨 告警规则

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: myapp-alerts
  namespace: monitoring
  labels:
    release: kube-prometheus
spec:
  groups:
  - name: myapp
    interval: 30s
    rules:
    - alert: HighErrorRate
      expr: |
        sum(rate(http_requests_total{app="myapp",status=~"5.."}[5m]))
        /
        sum(rate(http_requests_total{app="myapp"}[5m])) > 0.05
      for: 5m
      labels:
        severity: critical
      annotations:
        summary: "Error rate above 5%"
        description: "{{ $value | humanizePercentage }} errors in last 5m"
```

## 🔧 排查

```bash
# 看 Prometheus 状态
kubectl -n monitoring get pods
kubectl -n monitoring logs -l app.kubernetes.io/name=prometheus

# 端口转发
kubectl -n monitoring port-forward svc/kube-prometheus-stack-prometheus 9090

# 浏览器打开
http://localhost:9090
# 试：up{job="myapp"} 或 query browser
```

## 🛠 实战

```bash
# 1. 装
helm install kube-prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# 2. 暴露 Grafana
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3000:80
# 浏览器 admin / prom-operator

# 3. 暴露 Prometheus
kubectl -n monitoring port-forward svc/kube-prometheus-stack-prometheus 9090:80

# 4. 给应用加 ServiceMonitor
kubectl apply -f servicemonitor.yaml
```

## 🔗 下一步

- [Grafana 仪表板](/07-observability/grafana)
- [Loki 日志聚合](/07-observability/loki)
- [Alertmanager](/07-observability/alertmanager)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud](https://java-px.bot.cd/cloud/):Spring Cloud 微服务
- [linux](https://java-px.bot.cd/linux/):Linux 内核基础
- [devops](https://java-px.bot.cd/devops/):DevOps 流程
