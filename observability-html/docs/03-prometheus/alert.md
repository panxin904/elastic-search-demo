---
title: Prometheus 告警规则
description: PromQL alert + 多窗口 burn rate
---

# Prometheus 告警规则

> **TL;DR**：Prometheus 告警 = **PromQL 表达式 + for 持续时间 + labels + annotations**。**SRE 推荐多窗口 burn rate 告警**（2%/1h + 5%/6h 组合），**能在用户感知前发现 SLO breach**。**典型文件：`prometheus.rules.yml`**。

## 一句话定义

```
Prometheus alert = 评估 PromQL 表达式
                 + 持续 for 时间（如 for: 5m）
                 + 触发后 push 到 Alertmanager
                 + labels/annotations 携带上下文
```

## 基础语法

```yaml
# prometheus.rules.yml
groups:
  - name: example
    interval: 30s          # 评估频率（独立于 scrape interval）
    rules:
      - alert: HighRequestLatency
        expr: |
          job:request_latency_seconds:p99{job="myapp"} > 1
        for: 5m            # 持续 5 分钟才触发
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "P99 延迟过高 ({{ $value }}s)"
          description: "{{ $labels.instance }} P99 延迟超过 1s 持续 5 分钟"
          runbook_url: "https://wiki/runbooks/high-latency"
          dashboard: "https://grafana/d/myapp"
```

## 关键字段

```
- alert: 告警名称（业务唯一）
- expr:  PromQL 表达式（产生非空结果 = 触发）
- for:   持续时间（默认 0）
- keep_firing_for: 告警解决后保持 firing 时长（防抖）
- labels: 附加 labels（路由 / 抑制的关键）
- annotations: 人类可读信息（summary / description / runbook_url）
```

## SRE 多窗口 Burn Rate 告警（推荐）

```
核心思想：SLO 99.9%（月）= 允许每月 43.2 分钟错误时间
         单窗口评估不能区分"小问题"vs"大故障"
         多窗口组合 = 灵敏 + 稳定

Google SRE 推荐 4 个窗口组合：
  - 2% burn rate / 1h  短窗灵敏（1h 内误差率 2% 即告警）
  - 5% burn rate / 6h  中窗
  - 10% burn rate / 3d 长窗（避免长期缓慢劣化被掩盖）

举例 SLO 99.9%：
  允许错误率 0.1%（每月 43.2 min）
  burn rate 2% = 错误率 0.1% × 2 = 0.2%（约 8.6 小时/月）
  burn rate 5% = 错误率 0.5%
```

```yaml
# 多窗口 burn rate 告警（Google SRE Workbook）
- name: SLO-ErrorBudget-BurnRate
  rules:
    # Page: 短窗快速 + 长窗确认（2% 错误预算 / 1h 但 5% / 6h 确认）
    - alert: ErrorBudgetBurnFastPage
      expr: |
        (
          slo:sli_error:ratio_rate5m{sloth_service="checkout"} > (14.4 * 0.001)
          and
          slo:sli_error:ratio_rate30m{sloth_service="checkout"} > (14.4 * 0.001)
        ) or (
          slo:sli_error:ratio_rate2h{sloth_service="checkout"} > (6 * 0.001)
          and
          slo:sli_error:ratio_rate6h{sloth_service="checkout"} > (6 * 0.001)
        )
      labels:
        severity: critical
        slo: checkout
      annotations:
        summary: "Checkout 错误预算高速消耗（burn rate > 14.4x）"
        runbook: "https://wiki/runbooks/checkout-burn"

    # Ticket: 长窗（5% / 24h 但 5% / 3d 确认）→ 不打电话，发 ticket
    - alert: ErrorBudgetBurnSlowTicket
      expr: |
        (
          slo:sli_error:ratio_rate24h{sloth_service="checkout"} > (3 * 0.001)
          and
          slo:sli_error:ratio_rate3d{sloth_service="checkout"} > (3 * 0.001)
        )
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "Checkout 错误预算中速消耗（burn rate > 3x）"
```

## 实战案例：电商订单服务告警集

```yaml
groups:
  # === 业务级（影响收入） ===
  - name: business
    rules:
      - alert: OrderConversionDropped
        expr: |
          sum(rate(orders_succeeded_total[5m]))
          / sum(rate(orders_attempted_total[5m])) < 0.85
        for: 10m
        labels: {severity: critical, team: payments}
        annotations:
          summary: "订单转化率 < 85% 持续 10 分钟"
          action: "立刻检查支付通道 + 限流开关"

      - alert: CartAbandonmentSpike
        expr: |
          rate(cart_abandonment_total[10m])
          / rate(cart_started_total[10m]) > 0.7
        for: 30m
        labels: {severity: warning, team: product}

  # === 应用级（SLI） ===
  - name: golden-signals
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels: {severity: critical}

      - alert: HighLatencyP99
        expr: |
          histogram_quantile(0.99, sum by (le, service) (rate(http_request_duration_seconds_bucket[5m]))) > 2
        for: 10m
        labels: {severity: warning}

      - alert: TrafficDropped
        expr: |
          sum(rate(http_requests_total[5m])) < sum(rate(http_requests_total[1h] offset 1d)) * 0.5
        for: 15m
        labels: {severity: warning}
        annotations:
          summary: "流量同比昨日下降 50%"

  # === 资源级 ===
  - name: resources
    rules:
      - alert: HostHighCpuLoad
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 10m
        labels: {severity: warning}

      - alert: HostOutOfMemory
        expr: (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 < 10
        for: 5m
        labels: {severity: critical}
```

## Alertmanager 集成

```yaml
# prometheus.yml
rule_files:
  - "prometheus.rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager-1:9093
            - alertmanager-2:9093
            - alertmanager-3:9093
```

## 验证 & 调试

```bash
# 1. 规则语法
promtool check rules prometheus.rules.yml

# 2. 测试规则：用 --debug 启动 Prometheus 控制台
curl -G http://prometheus:9090/api/v1/query \
  --data-urlencode 'query=up{job="prometheus"}'

# 3. 当前活跃告警
curl http://prometheus:9090/api/v1/alerts

# 4. 单元测试（推荐）
# promtool test rules alert_test.yml
```

## 一句话总结

> **Prometheus 告警 = PromQL + for + labels + annotations**。**SRE 多窗口 burn rate 4 组合**（2%/1h + 5%/6h + 5%/24h + 5%/3d）是工业最佳实践。**告警要 actionable**：每条告警必须配 runbook_url + dashboard。

---

## 关联章节

- [Prometheus 概览](../03-prometheus/overview.md) — TSDB / 拉取模型
- [PromQL](../03-prometheus/promql.md) — 告警表达式的查询语言
- [SLI/SLO](../01-foundations/sli-slo.md) — 错误预算与 burn rate
- [Alertmanager](../08-alerting/alertmanager.md) — 告警路由与抑制
- [告警分级](../08-alerting/severity.md) — P0/P1/P2/P3 划分

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
