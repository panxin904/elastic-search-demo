---
title: Alertmanager
date: 2026-08-15  # date-auto-injected
---

# Alertmanager - 告警分发

> Alertmanager = Prometheus 的"邮件 / Slack / 钉钉"中转站。

## 🤔 为什么需要 Alertmanager

```
Prometheus 触发告警 → ?
  - 太多规则，重复发
  - 告警风暴（同一问题 100 个实例）
  - 不同时段处理方式不同
  - 重复告警要去重

Alertmanager：
  ✅ 分组（同一 service 聚合一条）
  ✅ 抑制（down 的时候不重复告警 host）
  ✅ 静默（维护时禁告警）
  ✅ 路由（critical 走 PagerDuty，warning 走 Slack）
```

## 🏗️ 架构

```
Prometheus ── alert ──► Alertmanager
                          │
                ┌─────────┼─────────┐
                ▼         ▼         ▼
              Email   Slack    Webhook
                                        │
                                   (PagerDuty / 钉钉 / 飞书 / 企业微信)
```

## 🚀 部署

`kube-prometheus-stack` 已经默认装好 Alertmanager。

```bash
kubectl -n monitoring get pods
# alertmanager-kube-prometheus-stack-alertmanager-0

# 端口转发
kubectl -n monitoring port-forward alertmanager-kube-prometheus-stack-alertmanager-0 9093:9093
```

## 📜 配置

```yaml
# alertmanager-config.yaml
apiVersion: monitoring.coreos.com/v1alpha1
kind: AlertmanagerConfig
metadata:
  name: main
  namespace: monitoring
spec:
  route:
    receiver: 'default'
    groupBy: ['alertname', 'namespace']
    groupWait: 30s
    groupInterval: 5m
    repeatInterval: 4h
    routes:
    - matchers:
      - severity = "critical"
      receiver: 'pagerduty'
    - matchers:
      - severity = "warning"
      receiver: 'slack'
  receivers:
  - name: 'default'
    webhookConfigs:
    - url: 'https://hooks.example.com/alert'
      sendResolved: true
  - name: 'pagerduty'
    pagerdutyConfigs:
    - routingKey: 'xxx'
      sendResolved: true
  - name: 'slack'
    slackConfigs:
    - apiURL: 'https://hooks.slack.com/services/xxx'
      channel: '#alerts'
      sendResolved: true
```

## 🔧 抑制（Inhibit）

```yaml
# 集群 down 时不告警每个节点
inhibit_rules:
- source_matchers:
  - alertname = "ClusterDown"
  target_matchers:
  - alertname = "NodeDown"
  equal: ['cluster']
```

## 🔇 静默（Silence）

```bash
# 临时禁告警（维护时）
amtool silence add --alertmanager=http://localhost:9093 \
  --comment "Database maintenance" \
  --duration 2h \
  --matcher severity=~"warning|critical" \
  --matcher service="db"
```

```bash
# 用 API
curl -X POST http://alertmanager:9093/api/v1/silences \
  -d '{
    "matchers": [{"name": "alertname", "value": "HighErrorRate", "isRegex": false}],
    "startsAt": "2024-01-15T00:00:00Z",
    "endsAt": "2024-01-15T02:00:00Z",
    "comment": "Investigation"
  }'
```

## 📊 模板（Go template）

```yaml
receivers:
- name: 'slack'
  slackConfigs:
  - apiURL: 'https://hooks.slack.com/services/xxx'
    channel: '#alerts'
    title: '🔥 {{ .CommonLabels.alertname }}'
    text: |
      *Severity*: {{ .CommonLabels.severity }}
      *Summary*: {{ .CommonAnnotations.summary }}
      *Description*: {{ .CommonAnnotations.description }}
      *Status*: {{ .Status }}
    sendResolved: true
```

| 变量 | 含义 |
|------|------|
| `.Alerts` | 当前告警组 |
| `.CommonLabels` | 公共标签 |
| `.CommonAnnotations` | 公共注释 |
| `.Status` | firing / resolved |
| `.ExternalURL` | Alertmanager URL |

## 🪜 主流接收方

| 接收方 | 用途 |
|--------|------|
| Email | 传统 |
| Slack / Teams | 团队协作 |
| PagerDuty / Opsgenie | 值班 / 升级 |
| 钉钉 / 飞书 / 企业微信 | 中国团队 |
| Webhook | 集成其他系统 |
| WeChat | 个人 |
| Telegram | 跨平台 |

```yaml
# 钉钉（webhook）
- name: 'dingtalk'
  webhookConfigs:
  - url: 'https://oapi.dingtalk.com/robot/send?access_token=xxx'
    sendResolved: true

# 飞书（webhook）
- name: 'feishu'
  webhookConfigs:
  - url: 'https://open.feishu.cn/open-apis/bot/v2/hook/xxx'
    sendResolved: true
```

## 🔧 常用命令

```bash
# 用 amtool
amtool alert query                          # 看当前 firing
amtool silence add -c "maintenance" -d 1h    # 加静默
amtool silence list
amtool silence expire <id>
amtool silence expire all

# 看状态
curl http://alertmanager:9093/-/ready
curl http://alertmanager:9093/api/v2/status
```

## 🛠 实战

### 静默管理（避免维护时告警风暴）

```bash
#!/bin/bash
# 部署前 5 分钟
amtool silence add -c "Deploy $(date +%s)" -d 30m \
  --matcher service="myapp" --matcher severity=~"warning|critical"
```

### 抑制：节点 down 时不告警其上 Pod

```yaml
inhibit_rules:
- source_matchers:
  - alertname = "NodeDown"
  target_matchers:
  - alertname = "PodNotReady"
  equal: ['node']
```

## 🩹 故障

```bash
# 告警没发出
# 1. Prometheus 规则触发了吗？
# Prometheus → Alerts 页面

# 2. Prometheus 推到 Alertmanager 了吗？
curl http://prometheus:9090/api/v1/alertmanagers

# 3. Alertmanager 收到但没发？
amtool alert query
# 看 status / inhibited / silenced

# 4. 接收方 webhook 失败
amtool alert query --output=json
# alertmanager 日志
```

## 🔗 下一步

- [Prometheus](/07-observability/prometheus)
- [Grafana 仪表板](/07-observability/grafana)
- [Loki 日志聚合](/07-observability/loki)