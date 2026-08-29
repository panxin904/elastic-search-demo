---
title: K8s 全栈监控实战
date: 2026-08-15  # date-auto-injected
description: ServiceMonitor + PrometheusRule + Grafana 完整 yaml
---

# K8s 全栈监控实战

> **TL;DR**：K8s 监控不是装个 Prometheus 就完事。需要 Prometheus Operator 管理 CRD、ServiceMonitor 自动发现、PrometheusRule 管理告警、Grafana 配 Dashboard。**本文给出可直接复用的 yaml 配置**。

## 一句话定义

```
K8s 全栈监控 = kube-prometheus-stack（Helm chart）
                = Prometheus + Alertmanager + Grafana + node-exporter + kube-state-metrics
                + 一堆预定义 dashboard / alert
```

## 部署：Helm 一键安装

```bash
# 1. 添加 repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# 2. 创建 namespace
kubectl create namespace monitoring

# 3. 安装 kube-prometheus-stack
helm install kube-prometheus-stack \
  prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi \
  --set grafana.adminPassword=admin123 \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.podMonitorSelectorNilUsesHelmValues=false \
  --set prometheus.prometheusSpec.ruleSelectorNilUsesHelmValues=false

# 4. 暴露 Grafana
kubectl port-forward svc/kube-prometheus-stack-grafana 8080:80 -n monitoring
# 浏览器访问 http://localhost:8080，admin / admin123
```

> **存储**：生产环境必须配 PVC（PersistentVolumeClaim），否则 Prometheus 重启数据丢失。`storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi` 起。

## ServiceMonitor：自动发现应用指标

**问题**：新部署的应用怎么让 Prometheus 自动抓取？

**答案**：在应用 namespace 里创建 ServiceMonitor CRD。

### 应用侧的 Service YAML

```yaml
# app-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: order-service
  labels:
    app: order-service
spec:
  ports:
  - name: http
    port: 8080
    targetPort: 8080
  selector:
    app: order-service
```

### ServiceMonitor CRD

```yaml
# service-monitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: order-service
  namespace: monitoring   # ServiceMonitor 所在 ns
  labels:
    release: kube-prometheus-stack  # 被 prometheus-operator 选择
spec:
  selector:
    matchLabels:
      app: order-service  # 选择上面那个 Service
  namespaceSelector:
    matchNames:
    - default  # Service 所在 ns（可跨 ns）
  endpoints:
  - port: http
    path: /actuator/prometheus
    interval: 15s
    scrapeTimeout: 10s
    honorLabels: true  # 保留原始 label，避免被覆盖
```

**生效流程**：

```
应用暴露 /actuator/prometheus → Service 暴露 8080
                                ↓
                    ServiceMonitor 选择这个 Service
                                ↓
                Prometheus Operator 监听到 CRD 变化
                                ↓
                  自动重载 Prometheus 配置
                                ↓
                        开始抓取指标
```

## PodMonitor：Pod 级别抓取

**适用场景**：Pod 有 IP 但没 Service（如 Job、DaemonSet）。

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: filebeat-pods
  namespace: monitoring
  labels:
    release: kube-prometheus-stack
spec:
  selector:
    matchLabels:
      app: filebeat
  namespaceSelector:
    matchNames:
    - logging
  podMetricsEndpoints:
  - port: metrics
    path: /metrics
    interval: 30s
```

## PrometheusRule：告警规则管理

**问题**：告警规则散落在 prometheus.yml 里，难管理。

**答案**：用 PrometheusRule CRD 把规则管理起来。

### 业务告警：订单服务错误率

```yaml
# prometheus-rule-order.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: order-service-alerts
  namespace: monitoring
  labels:
    release: kube-prometheus-stack
spec:
  groups:
  - name: order-service.slo
    interval: 30s
    rules:
    # P0 - 立刻 page
    - alert: OrderServiceErrorBudgetBurn1h
      expr: |
        (
          sum(rate(http_requests_total{service="order-service", status=~"5.."}[1h]))
          /
          sum(rate(http_requests_total{service="order-service"}[1h]))
        ) > (14.4 * 0.001)
      for: 2m
      labels:
        severity: page
        team: order
      annotations:
        summary: "订单服务 1h 燃烧率 14.4x, SLO 即将破线"
        description: "当前错误率 {{ $value | humanizePercentage }}, 阈值 1.44%"
        runbook: "https://wiki/runbooks/order-error-budget"

    # P1 - 6h 燃烧率
    - alert: OrderServiceErrorBudgetBurn6h
      expr: |
        (
          sum(rate(http_requests_total{service="order-service", status=~"5.."}[6h]))
          /
          sum(rate(http_requests_total{service="order-service"}[6h]))
        ) > (6 * 0.001)
      for: 5m
      labels:
        severity: page
        team: order
      annotations:
        summary: "订单服务 6h 燃烧率 6x"

    # P2 - 24h 趋势
    - alert: OrderServiceErrorBudgetBurn24h
      expr: |
        (
          sum(rate(http_requests_total{service="order-service", status=~"5.."}[24h]))
          /
          sum(rate(http_requests_total{service="order-service"}[24h]))
        ) > (3 * 0.001)
      for: 10m
      labels:
        severity: ticket
        team: order
      annotations:
        summary: "订单服务 24h 燃烧率 3x, ticket 处理"
```

### 基础设施告警：节点

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: infrastructure-alerts
  namespace: monitoring
  labels:
    release: kube-prometheus-stack
spec:
  groups:
  - name: node.rules
    rules:
    - alert: NodeCPUHigh
      expr: |
        100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "节点 {{ $labels.instance }} CPU > 80%"

    - alert: NodeMemoryHigh
      expr: |
        (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 85
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "节点 {{ $labels.instance }} 内存 > 85%"

    - alert: NodeDiskWillFillIn4Hours
      expr: |
        predict_linear(node_filesystem_avail_bytes{fstype!~"tmpfs"}[6h], 4 * 3600) < 0
      for: 10m
      labels:
        severity: page
      annotations:
        summary: "节点 {{ $labels.instance }} 磁盘将在 4h 内写满"

    - alert: KubernetesNodeNotReady
      expr: kube_node_status_condition{condition="Ready",status="true"} == 0
      for: 5m
      labels:
        severity: page
      annotations:
        summary: "节点 {{ $labels.node }} 失联"
```

## 应用埋点：Spring Boot + Micrometer

### 加依赖

```xml
<!-- pom.xml -->
<dependency>
    <groupId>io.micrometer</groupId>
    <artifactId>micrometer-registry-prometheus</artifactId>
</dependency>
```

### application.yml

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
  metrics:
    tags:
      application: ${spring.application.name}
    distribution:
      percentiles-histogram:
        http.server.requests: true
      percentiles:
        http.server.requests: 0.5, 0.95, 0.99
      slo:
        http.server.requests: 10ms, 50ms, 100ms, 200ms, 500ms, 1s
```

### 业务埋点

```java
@Service
public class OrderService {
    private final MeterRegistry registry;
    private final Counter orderCreatedCounter;
    private final Timer orderProcessTimer;

    public OrderService(MeterRegistry registry) {
        this.registry = registry;
        this.orderCreatedCounter = Counter.builder("order_created_total")
            .description("订单创建总数")
            .tag("type", "online")
            .register(registry);
        this.orderProcessTimer = Timer.builder("order_process_duration")
            .description("订单处理耗时")
            .publishPercentileHistogram()
            .register(registry);
    }

    public Order createOrder(OrderRequest req) {
        return orderProcessTimer.record(() -> {
            Order order = orderRepository.save(new Order(req));
            orderCreatedCounter.increment();
            return order;
        });
    }
}
```

## 自定义 Grafana Dashboard（ConfigMap）

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: order-service-dashboard
  namespace: monitoring
  labels:
    grafana_dashboard: "1"  # 让 Grafana sidecar 自动加载
data:
  order-service.json: |
    {
      "title": "Order Service · SRE Dashboard",
      "panels": [
        {
          "title": "QPS",
          "type": "timeseries",
          "targets": [{
            "expr": "sum(rate(http_server_requests_seconds_count{service=\"order-service\"}[5m]))"
          }]
        }
      ]
    }
```

**Grafana 自动加载**：通过 Grafana 的 sidecar 自动发现 ConfigMap：

```yaml
# values.yaml
grafana:
  sidecar:
    dashboards:
      enabled: true
      label: grafana_dashboard
```

## 全栈可观测性（Metrics + Logs + Traces）

```yaml
# 1. Loki（logs）
helm install loki grafana/loki-stack \
  --namespace logging --create-namespace \
  --set promtail.enabled=true

# 2. Tempo（traces）
helm install tempo grafana/tempo \
  --namespace tracing --create-namespace

# 3. OpenTelemetry Collector（统一采集）
helm install otel-collector open-telemetry/opentelemetry-collector \
  --namespace observability --create-namespace \
  --set mode=deployment
```

**OTel Collector 配置（采集所有信号）**：

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317

  # 从 K8s 服务发现 metrics
  prometheus:
    config:
      scrape_configs:
      - job_name: kubernetes-pods
        kubernetes_sd_configs:
        - role: pod

processors:
  batch:
    timeout: 10s

exporters:
  prometheus:
    endpoint: 0.0.0.0:8889
  loki:
    endpoint: http://loki.logging.svc:3100/loki/api/v1/push
  otlp/tempo:
    endpoint: tempo.tracing.svc:4317
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/tempo]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [loki]
```

## 一句话总结

> **K8s 全栈监控 = Prometheus Operator（CRD 管理）+ ServiceMonitor（自动发现）+ PrometheusRule（告警规则）+ Grafana（可视化）+ OTel（统一采集）**。
> Helm 一键安装 + yaml 可复用，本文给的配置 80% 场景够用。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
