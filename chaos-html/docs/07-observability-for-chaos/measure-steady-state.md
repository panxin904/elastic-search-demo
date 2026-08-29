---
title: 稳态假设度量
date: 2026-08-15  # date-auto-injected
---

# 稳态假设度量

## 稳态度量五要素

**1. 业务指标（KBI）**：

- 电商：订单成功率 / 支付成功率
- 视频：缓冲率 / 卡顿率 / 首帧时间
- 金融：交易成功率 / 清算时效

**2. 系统指标（SLI）**：

- 可用性：成功率 = 成功请求 / 总请求
- 延迟：P50 / P95 / P99
- 吞吐：QPS / TPS
- 错误：错误率 / 5xx 比例

**3. 资源指标**：

- CPU / 内存 / 磁盘 / 网络
- K8s：Pod 重启 / OOM / 节点状态

**4. 滑动窗口**：

- 不是「瞬时值」，而是「窗口期聚合」
- 常见窗口：1 分钟 / 5 分钟 / 15 分钟

**5. 稳态区间**：

- 不是「单点值」，而是「区间 + 时间窗口」
- 示例：订单成功率稳态 = [99.5%, 99.9%]，持续 5 分钟

## Prometheus 查询示例

```promql
# 订单成功率（5 分钟窗口）
sum(rate(order_success_total[5m]))
/ sum(rate(order_total[5m]))

# P99 延迟
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{app="order-service"}[5m])) by (le))

# 错误率（5xx）
sum(rate(http_requests_total{status=~"5..",app="order-service"}[5m]))
/ sum(rate(http_requests_total{app="order-service"}[5m]))

# Pod 重启次数（异常信号）
increase(kube_pod_container_status_restarts_total[5m])
```

## 异常检测算法

**1. 阈值法**：

```yaml
alert: SteadyStateViolation
expr: |
  abs(
    sum(rate(order_success_total[5m]))
    / sum(rate(order_total[5m]))
    - 0.997
  ) > 0.005
for: 5m
```

**2. 同比/环比**：

```promql
# 与上周同时段对比
sum(rate(order_success_total[5m]))
/ sum(rate(order_total[5m]))
> on() (0.997 - 0.005)
```

**3. 3-sigma**：

```python
def steady_state_check(observed, history):
    mean = np.mean(history)
    std = np.std(history)
    return abs(observed - mean) < 3 * std
```

**4. CUSUM**：

```python
def cusum_check(observed, baseline, threshold):
    cumulative = 0
    for value in observed:
        cumulative = max(0, cumulative + (baseline - value))
        if cumulative > threshold:
            return True
    return False
```

## 稳态对比 Dashboard

**Grafana Dashboard 示例**：

```
┌─────────────────────────────┐
│  实验前稳态 (过去 7 天)        │
│  - 订单成功率: 99.72% ± 0.05% │
│  - P99 延迟: 800ms ± 50ms    │
│  - 错误率: 0.05% ± 0.01%     │
└─────────────────────────────┘

┌─────────────────────────────┐
│  实验中（实时）                │
│  - 订单成功率: 99.45% ↓       │
│  - P99 延迟: 1200ms ↑         │
│  - 错误率: 0.42% ↑            │
│  判定: 偏离稳态（但仍可接受）   │
└─────────────────────────────┘

┌─────────────────────────────┐
│  实验后（恢复期）              │
│  - 订单成功率: 99.71% (恢复)   │
│  - P99 延迟: 850ms (恢复)     │
│  - 错误率: 0.06% (恢复)       │
│  恢复时间: 35 秒              │
└─────────────────────────────┘
```

## 与其他站点关系

- **chaos/01-foundations/steady-state**：稳态定义
- **observability/03-prometheus**：Prometheus 集成
- **system-design/08-availability**：SLO 体系


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

- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 混沌
- [observability](https://java-px.bot.cd/observability/):故障注入监控
- [system-design](https://java-px.bot.cd/system-design/):系统韧性
