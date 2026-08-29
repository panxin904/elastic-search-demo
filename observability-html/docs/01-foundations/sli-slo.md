---
title: SLI / SLO / Error Budget
description: SRE 三件套
---

# SLI / SLO / Error Budget

> **TL;DR**：SLI 是"**测什么**"，SLO 是"**承诺多少**"，Error Budget 是"**可以错多少**"。三者构成 SRE 量化可靠性的核心方法论。**没有 SLO，就谈不上可靠性工程**。

## 一句话定义

| 概念 | 英文 | 含义 |
|---|---|---|
| **SLI** | Service Level Indicator | 服务水平的量化指标（如 p99 延迟） |
| **SLO** | Service Level Objective | 指标的目标值（如 p99 < 200ms） |
| **Error Budget** | 错误预算 | 允许未达 SLO 的"额度"（如每月 1%） |

## 为什么需要 SLO？

### 没有 SLO 的世界

```
PM：服务可靠性怎么样？
Dev：挺好的，最近一周都没出故障。
PM：怎么证明？
Dev：……（没有量化数据）
```

### 有 SLO 的世界

```
PM：服务可靠性怎么样？
Dev：本月 error budget 已消耗 23%，距离 SLO 目标还有富余。
PM：可以加大发布频率吗？
Dev：可以，但要密切关注这个数字。
```

> **SLO 是工程团队和产品团队之间的契约**。没有它，事故定级就是嘴炮。

## SLI 选什么指标

不是所有指标都适合做 SLI。**好的 SLI 满足三个条件**：

1. **从用户视角测**：用户感知的，不是机器内部的
2. **可量化**：有明确数值，不是"还行"、"挺好"
3. **持续可测**：不是偶尔采样

### 推荐 SLI 候选

| 服务类型 | SLI | 计算 |
|---|---|---|
| HTTP API | 可用性 | 成功请求数 / 总请求数 |
| HTTP API | 延迟 | p99 延迟低于阈值 |
| 流式（Kafka） | 投递完整性 | 成功投递数 / 生产总数 |
| 存储（S3/DB） | 可用性 | 成功读写请求 / 总请求 |
| 批处理 | 完成率 | 成功完成数 / 总数 |

### 反例：差的 SLI

```
❌ CPU 使用率 < 80%       → 这是机器视角，不是用户视角
❌ 服务进程数 = 3          → 不是用户关心的
❌ 日志中没有 ERROR        → 漏掉 WARN 级别的问题
❌ 服务器在线数 = 总数      → 在线 ≠ 可用
```

> **黄金法则**：SLI 应该和"用户能不能用"挂钩。CPU、内存、磁盘利用率都是机器视角，只能做辅助指标。

## SLO 怎么定

### 步骤 1：先看历史数据

```promql
# 过去 30 天 API 可用性
sum(rate(http_requests_total{status!~"5.."}[30d]))
/
sum(rate(http_requests_total[30d]))
```

**如果历史是 99.95%**，那定 SLO = 99.9% 是合理目标（有 0.05% 富余）。

### 步骤 2：根据业务重要程度定档

| 业务 | 推荐 SLO | 备注 |
|---|---|---|
| 个人博客 | 99% | 每月可错 432 分钟 |
| 电商普通商品 | 99.9% | 每月可错 43 分钟 |
| 电商支付 | 99.99% | 每月可错 4 分钟 |
| 银行核心 | 99.999% | 每月可错 26 秒 |
| 生命支持 | 99.9999% | "六个 9" |

> **真相**：99.99% 比 99.9% **难 10 倍**，99.999% 比 99.99% **再难 10 倍**。不要盲目追求"五个 9"。

### 步骤 3：SLO 文档化

```yaml
# SLO 文档示例
service: order-service
version: 2026-Q3
owner: order-team@company.com

slos:
  - name: availability
    description: 订单 API 可用性
    sli:
      spec: |
        sum(rate(http_requests_total{service="order", status!~"5.."}[28d]))
        /
        sum(rate(http_requests_total{service="order"}[28d]))
    objective: 99.9%
    window: 28d

  - name: latency
    description: 订单 API 延迟
    sli:
      spec: |
        histogram_quantile(0.99,
          sum(rate(http_request_duration_seconds_bucket{service="order"}[28d])) by (le)
        )
    objective: 99% < 200ms
    window: 28d
```

## Error Budget 怎么算

**公式**：

```
Error Budget = 1 - SLO
```

举例：
- SLO = 99.9% → Error Budget = 0.1% / 月 = 43 分钟
- SLO = 99.99% → Error Budget = 0.01% / 月 = 4.3 分钟
- SLO = 99% → Error Budget = 1% / 月 = 432 分钟

**计算当月已消耗**：

```promql
# 当月已消耗的 error budget（百分比）
1 -
(
  sum(increase(http_requests_total{service="order", status!~"5.."}[30d]))
  /
  sum(increase(http_requests_total{service="order"}[30d]))
)
```

**Grafana 看板**：

```
╔════════════════════════════════════════════╗
║  Order Service Error Budget (Aug 2026)    ║
║                                            ║
║  ████████████████░░░░░░░  73% remaining   ║
║                                            ║
║  Burn rate (1h): 0.3x                    ║
║  Burn rate (6h): 0.5x                    ║
║  Forecast: 17% consumed by month-end      ║
╚════════════════════════════════════════════╝
```

## Burn Rate · 燃烧率

**什么是 burn rate**：error budget 消耗的速度。

```promql
# 1 小时燃烧率
burn_rate_1h = (1 - sli_1h) / error_budget_total
```

**Google SRE 推荐的多窗口 burn rate 告警**：

| 窗口 | 阈值 | 严重度 | 通知速度 |
|---|---|---|---|
| 1h | 14.4x | page | 立即 |
| 6h | 6x | page | 1 小时内 |
| 24h | 3x | ticket | 6 小时内 |
| 3d | 1x | ticket | 24 小时内 |

> **解读**：1h 燃烧率 14.4x 意味着如果按这个速度烧，整个月 error budget 会在 1 小时内烧光。**这种速度必须立刻叫醒工程师**。

## Error Budget 政策

**SRE 文化核心**：Error Budget 用完 = 停止新功能发布。

```
剩余预算 > 50%：正常节奏发布
剩余预算 25%-50%：谨慎发布，避免高风险改动
剩余预算 10%-25%：仅 bug fix，feature freeze
剩余预算 < 10%：全团队停下手头工作，专攻可靠性
剩余预算 0%：停止所有非关键变更，进入"可靠性战时状态"
```

> **为什么这样？** 因为 SLO 是工程团队对业务方的承诺。承诺破 = 信任破产。**比"按时发布"重要**。

## 多窗口告警实战

```yaml
# Prometheus alerting rule 示例
groups:
- name: order-slo
  rules:
  # 1h 14.4x burn rate：一个月内 1h 烧光预算
  - alert: OrderErrorBudgetBurn1h
    expr: |
      (
        sum(rate(http_requests_total{service="order", status=~"5.."}[1h]))
        /
        sum(rate(http_requests_total{service="order"}[1h]))
      ) > (14.4 * 0.001)
    for: 2m
    labels:
      severity: page
    annotations:
      summary: "Order service 1h 燃烧率 14.4x, 立刻调查"

  # 6h 6x burn rate
  - alert: OrderErrorBudgetBurn6h
    expr: |
      (
        sum(rate(http_requests_total{service="order", status=~"5.."}[6h]))
        /
        sum(rate(http_requests_total{service="order"}[6h]))
      ) > (6 * 0.001)
    for: 5m
    labels:
      severity: page
    annotations:
      summary: "Order service 6h 燃烧率 6x"

  # 24h 3x burn rate
  - alert: OrderErrorBudgetBurn24h
    expr: |
      (
        sum(rate(http_requests_total{service="order", status=~"5.."}[24h]))
        /
        sum(rate(http_requests_total{service="order"}[24h]))
      ) > (3 * 0.001)
    for: 10m
    labels:
      severity: ticket
    annotations:
      summary: "Order service 24h 燃烧率 3x, ticket 处理"
```

## 常见误区

### 误区 1：SLO 越高越好

```
❌ 反正 SLO 高一点也没坏处，99.99% 吧
✅ 99.99% 比 99.9% 难 10 倍，成本翻倍。先定合理的，留改进空间。
```

### 误区 2：SLO 是一次性设定

```
❌ 定完就完事了
✅ SLO 至少每季度 review 一次，根据业务和系统能力调整。
```

### 误区 3：业务方不知道 SLO 存在

```
❌ SLO 是技术团队的内部约定
✅ SLO 是工程团队对业务方的契约，必须公开 + 对齐。
```

### 误区 4：Error Budget 是 KPI

```
❌ "本月我们消耗了 23% 的 error budget，KPI 完成良好"
✅ Error Budget 用得越少越好（说明系统越稳定），但又不能太少（说明 SLO 定得过松）
```

## 与可观测性的关系

```
可观测性 → 测量 SLI（p99 延迟、错误率）
    ↓
SLO → 定义目标
    ↓
Error Budget → 计算允许偏差
    ↓
Burn Rate Alert → 实时监控偏差
    ↓
On-call → 偏差过大时介入
    ↓
Postmortem → 偏差归零后复盘
```

> **没有可观测性，SLO 就是纸上谈兵；没有 SLO，可观测性就是数字游戏**。

## 一句话总结

> **SLI 测量 + SLO 目标 + Error Budget 政策 = 量化可靠性的铁三角**。
> 没有它，再多的监控大盘也只是"事后诸葛亮"。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
