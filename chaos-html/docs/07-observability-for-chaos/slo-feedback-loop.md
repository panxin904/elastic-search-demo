---
title: SLO 反馈环
---

# SLO 反馈环

## SLO 三要素

**SLI（Service Level Indicator）**：可度量的指标

- 例：订单成功率、P99 延迟

**SLO（Service Level Objective）**：目标值

- 例：99.5% 成功率、P99 < 1.5s

**Error Budget**：可消耗的错误预算

- 例：每月 0.5% 错误预算

## 反馈环流程

```
SLO 定义 → 稳态采集 → 混沌实验 → SLO 对比 → 持续验证
   │          │          │           │            │
   ↓          ↓          ↓           ↓            ↓
业务承诺    实时指标    注入故障     偏离判定     累计统计
                                                   │
                                                   ↓
                                            触发改进
```

## Error Budget 与混沌实验

**每月 Error Budget 计算**：

```python
monthly_budget = (1 - slo_objective) * monthly_request_count
```

例：SLO 99.5% × 月请求量 100M → Budget = 0.5M 错误请求

**混沌实验消耗**：

- 每次混沌实验消耗多少？**取决于实验影响**
- 例：Pod kill 实验影响 0.1% 错误率 / 1 分钟 → 消耗 ~0.0007% 预算
- 每周 1 次 × 4 周 = 0.003% 预算

**混沌日（Chaos Day）**：

- 季度 / 半年：消耗 0.1% 预算做大型实验
- 大促窗口：冻结实验（保护预算）

## Sloth SLO 定义

**Sloth 自动生成 Prometheus rules**：

```yaml
service: order-service
slos:
  - name: availability
    objective: 99.5
    description: "订单成功率 SLO"
    sli:
      events:
        error_query: sum(rate(http_requests_total{status=~"5..",app="order-service"}[5m]))
        total_query: sum(rate(http_requests_total{app="order-service"}[5m]))
    alerting:
      page_alert:
        burnrate: 14.4
        for: 2m
      ticket_alert:
        burnrate: 1
        for: 1h
```

**多窗口 Burn Rate 报警**：

- 5 分钟 × 14.4 倍率：短期爆发（page alert）
- 30 分钟 × 6 倍率：中期泄漏（page alert）
- 1 小时 × 3 倍率：缓慢泄漏（ticket alert）
- 6 小时 × 1 倍率：长期泄漏（ticket alert）

## 与其他站点关系

- **observability/03-prometheus**：Prometheus 集成
- **system-design/08-availability**：SLO 设计
- **chaos/01-foundations/steady-state**：稳态定义


## ## 实战案例

**Netflix SLO 文化**：Netflix 内部把 SLO 叫做 **RED (Rate / Error / Duration)** + **USE (Utilization / Saturation / Errors)** 双重体系，每个微服务必须定义 3-5 个核心 SLO，并用 Sloth + Prometheus 自动化。

**Uber 错误预算治理**：Uber 引入 **burn rate gating** — PR 合并前必须满足过去 7 天 SLO 预算消耗 < 80%，否则阻断发布。CI 集成 OPA 策略，强制 SLA 守护。

**字节跳动 Chaos Day**：每两周一次大型 Chaos Day，提前 1 周申请 0.5% 错误预算，结果直接写入稳定性季度报告。


## ## 故障排查清单

1. SLO 数据缺失 → 检查 Sloth rules 是否同步到 Prometheus
2. 误差巨大 → 检查 burn rate 公式（multi-window 多窗口）
3. 报警疲劳 → 调整 for / burnrate 阈值，结合业务时段
4. 预算耗尽 → 冻结新功能上线，专人值班恢复
5. 实验未触发 → 确认 chaos platform 注入是否真正执行


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
