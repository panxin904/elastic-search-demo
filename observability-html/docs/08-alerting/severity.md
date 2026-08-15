---
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
