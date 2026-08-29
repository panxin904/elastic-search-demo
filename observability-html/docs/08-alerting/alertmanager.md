---
title: Alertmanager 架构与配置
description: 去重 / 分组 / 路由 / 抑制
---

# Alertmanager 架构与配置

> **TL;DR**：Alertmanager 是 **Prometheus 生态的告警中枢**。接收 Prometheus server 推送的 alerts → **去重（inhibit）/ 分组（group）/ 路由（route）/ 静默（silence）** → 推到 **PagerDuty / Slack / Email / Webhook**。**正确的 Alertmanager 配置可以把"凌晨 3 点叫醒你"的告警降到月均 < 3 次**。

## 一句话定义

```
Alertmanager = Prometheus alerts 的"路由器 + 过滤器"
            = 接收多个 Prometheus 推送的告警
            = 按 group_by / route / receivers 分发
            = 去重 + 抑制 + 静默三件套
```

## 架构总览

```
┌──────────────┐  push alerts    ┌────────────────────┐  fan-out  ┌──────────┐
│ Prometheus   │ ──────────────▶ │   Alertmanager     │ ────────▶ │ PagerDuty│
│ (rule eval)  │                 │ ┌──────────────┐   │          └──────────┘
└──────────────┘                 │ │  1. inhibit  │   │          ┌──────────┐
                                 │ │  2. silence  │   │ ────────▶│ Slack    │
┌──────────────┐  push alerts    │ │  3. group_by │   │          └──────────┘
│ Prometheus   │ ──────────────▶ │ │  4. route     │   │          ┌──────────┐
│ (HA 副本)    │                 │ │  5. receiver  │   │ ────────▶│ Email    │
└──────────────┘                 │ └──────────────┘   │          └──────────┘
                                 └────────────────────┘
```

## 核心概念

### 1. Group（分组）

```
同一时间窗口 + 同一标签集合的 alerts 合并成一条通知
避免：1000 个 pod 触发同一告警 → 1000 条 Slack 消息
配置：group_by: [cluster, alertname] / group_wait: 30s / group_interval: 5m
```

### 2. Route（路由）

```
路由树 = 按 label 匹配层层下钻
       = 每个叶子节点指向一个 receiver
       = 支持 continue: true（子路由继续匹配）

route:
  receiver: 'default'
  group_by: [alertname, cluster]
  routes:
    - matchers:
        - severity="critical"
      receiver: 'pagerduty-critical'
      group_wait: 10s
    - matchers:
        - severity="warning"
      receiver: 'slack-warning'
      group_wait: 5m
```

### 3. Inhibit（抑制）

```
当更高严重度的告警触发时，自动静默相关低级别告警
例：cluster=prod 全挂 → 抑制所有该 cluster 的 warning
规则：
  inhibit_rules:
    - source_matchers: [severity="critical"]
      target_matchers: [severity="warning"]
      equal: [cluster, alertname]
```

### 4. Silence（静默）

```
手动 / 定时屏蔽特定告警（维护窗口、已知问题）
通过 amtool silence add 或 Alertmanager UI 创建
过期时间：24h / 1w / forever
```

## 完整配置示例

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alertmanager@example.com'
  smtp_auth_username: 'alertmanager@example.com'
  smtp_auth_password: '<password>'

templates:
  - '/etc/alertmanager/templates/*.tmpl'

route:
  receiver: 'default-receiver'
  group_by: ['alertname', 'cluster', 'service']
  group_wait: 30s        # 同组新告警等待 30s 一起发
  group_interval: 5m     # 同组再次发间隔
  repeat_interval: 4h    # 未恢复告警重复通知间隔
  routes:
    # P0：核心交易 / 资金 / 数据丢失
    - matchers:
        - severity="critical"
        - team="payments"
      receiver: 'pagerduty-p0'
      group_wait: 10s
      repeat_interval: 1h

    # P1：服务降级但可用
    - matchers:
        - severity="warning"
      receiver: 'slack-ops'
      group_wait: 5m
      repeat_interval: 12h

    # K8s 基础设施
    - matchers:
        - source="kubernetes"
      receiver: 'slack-k8s'

inhibit_rules:
  # 全集群挂 → 抑制所有 warning
  - source_matchers: [alertname="ClusterDown"]
    target_matchers: [severity="warning"]
    equal: [cluster]

  # 节点挂 → 抑制该节点上的 pod 告警
  - source_matchers: [alertname="NodeDown"]
    target_matchers: [severity="warning"]
    equal: [node]

receivers:
  - name: 'default-receiver'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/T00/B00/xxx'
        channel: '#alerts'
        title: '{{ .GroupLabels.alertname }} ({{ .GroupLabels.cluster }})'
        text: '{{ range .Alerts }}{{ .Annotations.description }}\n{{ end }}'

  - name: 'pagerduty-p0'
    pagerduty_configs:
      - service_key: '<pagerduty-key>'
        description: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'

  - name: 'slack-ops'
    slack_configs:
      - api_url: '<slack-webhook>'
        channel: '#ops-alerts'

  - name: 'slack-k8s'
    slack_configs:
      - api_url: '<slack-webhook>'
        channel: '#k8s-alerts'
```

## 实战案例：电商大促告警分级

```yaml
# 场景：双 11 大促，告警分级不能错过任何 P0，也不能让 P3 淹没 P0
route:
  receiver: 'default'
  routes:
    # 资金 / 库存 / 订单 → 必须 P0 + 电话
    - matchers: [{name="service", value=~"order|payment|inventory"}]
      matchers: [{name="severity", value="critical"}]
      receiver: 'pagerduty-p0-phone'
      group_wait: 0s          # 大促期间立即通知
      repeat_interval: 15m    # 15 分钟未恢复重复叫

    # 推荐 / 搜索 → P1，5 分钟内响应即可
    - matchers: [{name="service", value=~"recommend|search"}]
      receiver: 'slack-p1'

    # 离线任务 / 报表 → P2，只发 Slack 不打电话
    - matchers: [{name="category", value="batch"}]
      receiver: 'slack-p2'
      group_wait: 30m
      repeat_interval: 24h

inhibit_rules:
  # 大促期间全站挂 → 抑制所有非 critical
  - source_matchers: [{name="alertname", value="TotalRequestFailureRateHigh"}]
    target_matchers: [{name="severity", value=~"warning|info"}]
    equal: [cluster]
```

## HA 部署

```
Alertmanager 必须 HA 部署（Gossip 协议同步状态）
最小集群：3 节点，避免脑裂

docker run -d --name am-1 \
  -p 9093:9093 \
  -v $(pwd)/alertmanager.yml:/etc/alertmanager/alertmanager.yml \
  prom/alertmanager:v0.27.0 \
  --cluster.listen-address=''
  
# 节点 2/3 用 --cluster.peer=am-1:9094 加入集群
```

## 故障排查

```bash
# 1. 启动失败：配置语法错
amtool check-config alertmanager.yml

# 2. 告警没收到：Prometheus → Alertmanager 连通性
curl -X POST http://alertmanager:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[{"labels":{"alertname":"test"}}]'

# 3. UI 查看活跃告警
http://alertmanager:9093/#/alerts

# 4. 路由没匹配
http://alertmanager:9093/#/routes  # 调试路由树
```

## 一句话总结

> **Alertmanager = 告警路由器**：**group 去重 / route 分发 / inhibit 抑制 / silence 静默**。**配置正确 = 月均告警 < 3 次**；**配置错误 = 告警疲劳 + 重要告警被淹没**。

---

## 关联章节

- [Prometheus 告警规则](../03-prometheus/alert.md) — 写 alert rules 配合 Alertmanager
- [告警分级](../08-alerting/severity.md) — P0/P1/P2/P3 划分标准
- [静默规则](../08-alerting/silence.md) — silence 命令与最佳实践
- [On-call 文化](../08-alerting/oncall.md) — 值班轮转与告警升级

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
