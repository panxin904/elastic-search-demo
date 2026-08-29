---
title: 稳态假设
date: 2026-08-15  # date-auto-injected
---

# 稳态假设

## 什么是稳态

稳态（Steady State）是系统在正常情况下的可度量行为模式。它是混沌实验的「对照组」—— 没有稳态，实验结果无法解读。

**稳态三要素**：

1. **可度量的指标（Measurable）**：CPU 使用率、订单成功率、P99 延迟、错误率等
2. **基线值（Baseline）**：过去 7 天 / 30 天的 P50 / P95 / P99
3. **区间范围（Range）**：不是单点值，而是「区间 + 时间窗口」

**稳态示例**：

- 订单成功率：99.5% - 99.9%，持续 5 分钟
- P99 延迟：700ms - 900ms，持续 10 分钟
- 错误率：0.01% - 0.1%，持续 15 分钟
- 队列积压：< 1000 条消息，持续 5 分钟

**为什么稳态是「区间」而不是「单点」**？

- 单点值波动大（每秒成功率可能波动 0.5%）
- 区间 + 窗口更稳定（5 分钟聚合窗口）

**稳态计算（滑动窗口）**：

```promql
# 订单成功率（5 分钟窗口）
sum(rate(order_success_total[5m]))
/ sum(rate(order_total[5m]))
```

**稳态基线建立流程**：

1. 收集 7-30 天数据
2. 计算 P5 / P95（剔除异常值）
3. 定义区间 = [P5, P95]
4. 加上窗口期（如 5 分钟）
5. 写入 runbook

## 稳态验证方法

**1. 阈值法**：

```yaml
# 稳态判定（Prometheus alert）
alert: SteadyStateViolation
expr: |
  abs(
    sum(rate(order_success_total[5m]))
    / sum(rate(order_total[5m]))
    - 0.997
  ) > 0.005
for: 5m
```

**2. 同比/环比法**：

```promql
# 与上周同时段对比
sum(rate(order_success_total[5m]))
/ sum(rate(order_total[5m]))
> on() (0.997 - 0.005)
```

**3. 3-sigma 法**：

```python
import numpy as np

def steady_state_check(observed, history):
    mean = np.mean(history)
    std = np.std(history)
    return abs(observed - mean) < 3 * std
```

**4. 机器学习（Prophet / LSTM）**：

```python
from prophet import Prophet

model = Prophet()
model.fit(history_df)

future = model.make_future_dataframe(periods=300, freq='1min')
forecast = model.predict(future)

# 检测观测值是否在预测区间外
is_anomaly = observed < forecast.yhat_lower or observed > forecast.yhat_upper
```

**5. CUSUM（累积和算法）**：

```python
def cusum_check(observed, baseline, threshold):
    cumulative = 0
    for value in observed:
        cumulative = max(0, cumulative + (baseline - value))
        if cumulative > threshold:
            return True  # 异常
    return False
```

## 稳态常见误区

**误区 1：用 CPU 使用率做稳态**

- CPU 使用率高 ≠ 系统故障（可能正常负载）
- 关注**用户感知**指标（订单成功率 / 延迟）

**误区 2：用瞬时值**

- 每秒成功率波动 0.5% 是正常的
- 用滑动窗口聚合（如 5 分钟）

**误区 3：单一指标**

- 订单成功率 99.5% 但 P99 延迟 5 秒 → 用户体验差
- 多维度（成功率 + 延迟 + 错误率）

**误区 4：忽略季节性**

- 大促期间订单量翻倍，指标波动大
- 用同比/环比对比同时段

**误区 5：稳态不变**

- 系统升级 / 流量增长后，稳态基线需要重新建立
- 每月 / 每季度重新计算

## 与其他站点关系

- **observability/03-prometheus**：Prometheus 采集稳态指标
- **observability/08-alerting**：稳态偏离告警
- **system-design/08-availability**：SLO 与稳态关系


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
