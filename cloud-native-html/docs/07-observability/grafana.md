---
title: Grafana 仪表板
date: 2026-08-15  # date-auto-injected
---

# Grafana - 可视化

> Grafana = 指标 / 日志 / Trace 可视化的事实标准。

## 🤔 为什么需要 Grafana

```
Prometheus 只能查数字（PromQL）
Grafana = 把数字画成图表 + 拼成仪表板 + 多数据源
```

## 🧬 架构

```
┌─────────────┐
│   Grafana   │
└──────┬──────┘
       │ 数据源
   ┌───┴────┬─────────┬──────────┐
   ▼        ▼         ▼          ▼
Prometheus  MySQL    Loki      Jaeger
(指标)     (业务)   (日志)     (trace)
```

支持几十种数据源（Prometheus / Loki / InfluxDB / ES / CloudWatch ...）。

## 🚀 装

### 已经在 prometheus-stack 里有

```bash
helm install kube-prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

kubectl -n monitoring get pods
# grafana 在 kube-prometheus-stack-grafana
```

### 独立装

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm install grafana grafana/grafana -n monitoring --create-namespace
```

## 🔧 访问

```bash
# 端口转发
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3000:80
# 浏览器
# 默认用户 admin / 密码 prom-operator
# （或查 secret）
kubectl -n monitoring get secret kube-prometheus-stack-grafana -o jsonpath='{.data.admin-password}' | base64 -d
```

## 🎨 仪表板

### 导入

- 左 sidebar → "+" → Import
- 输入 dashboard ID（如 6417 是经典 k8s 集群）
- 或上传 JSON

### 经典仪表板

| ID | 名称 |
|----|------|
| 6417 | Kubernetes Cluster (Prometheus) |
| 315 | Node Exporter Full |
| 1860 | Node Exporter Server Stats |

### 自建面板

```yaml
# 选 PromQL 数据源
sum(rate(http_requests_total{app="myapp"}[5m]))
# 选 visualization：graph / stat / gauge / table
# 加变量：$instance / $namespace
```

## 🪜 变量

Variables → 顶部下拉框（多维过滤）

```yaml
# query 类型变量
Data source: Prometheus
Query: label_values(up{job="myapp"}, instance)

# 静态下拉
Type: Custom
Values: dev, staging, prod

# 文本框
Type: Text box
```

## 🔐 数据源

```yaml
# Prometheus
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus-operated.monitoring.svc:9090
    isDefault: true

  - name: Loki
    type: loki
    url: http://loki.monitoring.svc:3100

  - name: MySQL
    type: mysql
    url: mysql.example.com:3306
    user: grafana
    database: myapp
```

## 🚨 告警（unified alerting）

Grafana 8+ 推荐用 "unified alerting"：

```yaml
# 告警规则
apiVersion: grafana.alerting.alertmanager/v1alpha1
kind: AlertRuleGroup
metadata:
  name: myapp
spec:
  folder: myapp
  interval: 1m
  rules:
  - uid: high-error
    title: HighErrorRate
    condition: A
    data:
      - refId: A
        relativeTimeRange: { from: 300, to: 0 }
        queryType: ''
        datasourceUid: prometheus
        model:
          expr: 'sum(rate(http_requests_total{app="myapp",status=~"5.."}[5m])) / sum(rate(http_requests_total{app="myapp"}[5m]))'
          intervalMs: 1000
          maxDataPoints: 43200
    noDataState: NoData
    execErrState: Alerting
    for: 5m
    labels: { severity: critical }
    annotations:
      summary: "Error rate above 5%"
```

## 🪛 实战

### 1. 选 / 改 dashboard

```json
{
  "title": "MyApp 概览",
  "panels": [
    {
      "title": "QPS",
      "type": "timeseries",
      "targets": [
        {
          "expr": "sum(rate(http_requests_total{app=\"myapp\"}[1m]))"
        }
      ]
    },
    {
      "title": "错误率",
      "type": "stat",
      "targets": [
        {
          "expr": "sum(rate(http_requests_total{app=\"myapp\",status=~\"5..\"}[5m])) / sum(rate(http_requests_total{app=\"myapp\"}[5m]))"
        }
      ],
      "fieldConfig": {
        "defaults": {
          "unit": "percentunit",
          "thresholds": {
            "mode": "absolute",
            "steps": [
              { "color": "green", "value": 0 },
              { "color": "yellow", "value": 0.01 },
              { "color": "red", "value": 0.05 }
            ]
          }
        }
      }
    }
  ]
}
```

### 2. 用 provisioning 自动加 dashboard

```yaml
# dashboards 资源
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-dashboard
  labels:
    grafana_dashboard: "1"
data:
  myapp.json: |
    { ... }
```

## 🔐 鉴权

```yaml
# 装 LDAP / OAuth / SAML
[auth.ldap]
enabled = true
host = ldap.example.com
bind_dn = "cn=grafana,dc=example,dc=com"

# OAuth
[auth.github]
enabled = true
client_id = xxx
client_secret = xxx
allow_sign_up = true
```

## 🔗 下一步

- [Prometheus](/07-observability/prometheus)
- [Loki 日志聚合](/07-observability/loki)
- [Alertmanager](/07-observability/alertmanager)