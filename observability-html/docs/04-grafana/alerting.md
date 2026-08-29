---
title: Grafana 告警
date: 2026-08-15  # date-auto-injected
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
