---
title: 爆炸半径
---

# 爆炸半径

## 爆炸半径分级

爆炸半径（Blast Radius）是「实验失败时的最大影响范围」。分级管理：

| 级别 | 流量 | 实例 | 区域 | 时长 | 适用 |
|---|---|---|---|---|---|
| L1 · 单测 | 0% | 1 Pod | 单 AZ | 5s | 首次实验 |
| L2 · 金丝雀 | 1% | 10% Pods | 单 AZ | 30s | 灰度验证 |
| L3 · 灰度 | 10% | 50% Pods | 单 Region | 5min | 回归测试 |
| L4 · 全量 | 100% | 100% Pods | 多 Region | 30min | 持续运行 |

**L1（单测）**：1 个 Pod，无真实流量（仅探活），单 AZ，5 秒。适用于首次实验，验证工具链 + 流程。

**L2（金丝雀）**：10% 真实流量，10% Pods，单 AZ，30 秒。验证核心假设（如 Pod kill 时流量转移）。

**L3（灰度）**：10-50% 流量，半数 Pods，单 Region，5 分钟。验证依赖链路（如支付失败是否影响订单）。

**L4（全量）**：100% 流量，所有 Pods，多 Region，30 分钟。生产环境持续运行（每周 / 每月）。

## 爆炸半径控制四要素

**1. 流量比例**：

- 金丝雀 1% → 灰度 10% → 全量 100%
- 实现：Service Mesh（Istio VirtualService）或 API Gateway

```yaml
# Istio VirtualService（流量切分）
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: order-service
spec:
  hosts: [order-service]
  http:
  - route:
    - destination:
        host: order-service
        subset: v1
      weight: 90
    - destination:
        host: order-service
        subset: v2
      weight: 10  # 灰度 10% 到 v2
```

**2. 实例比例**：

- 1 个 Pod → 10% Pods → 50% Pods → 100% Pods
- 实现：PodChaos `mode` 字段

```yaml
spec:
  mode: fixed-percent
  value: "10"  # 10% Pods
```

**3. 区域比例**：

- 单 AZ → 同城双活 → 跨 Region
- 实现：chaos-mesh `nodeSelectors`

```yaml
selector:
  nodeSelectors:
    topology.kubernetes.io/zone: us-east-1a
```

**4. 时长控制**：

- 实验时长 ≤ 影响传播时间
- 实现：`duration` 字段（自动恢复）

```yaml
spec:
  duration: "30s"  # 30 秒后自动恢复
```

**回滚预案（必备）**：

- 自动化：SLO breach → 自动 kill chaos
- 手动化：「红色按钮」一键 kill
- 退出条件：业务影响超阈值

## 退出条件设计

**退出条件三要素**：

1. **业务退出条件**：业务指标跌至阈值
2. **时间退出条件**：实验超过最大时长
3. **错误退出条件**：实验连续失败 N 次

**示例**：

```yaml
# chaos-experiment.yaml
spec:
  duration: "5m"
  auto_termination:
    - condition: "order_success_rate < 95"
      action: "kill_chaos"
      notification: "pagerduty:high"
    - condition: "p99_latency > 3000ms"
      action: "kill_chaos"
      notification: "slack:#chaos-game-day"
    - condition: "duration > 10m"
      action: "kill_chaos"
      notification: "slack:oncall"
```

**退出条件最佳实践**：

1. **必有**：实验无退出条件 = 灾难
2. **可量化**：用 SLO 指标，不用「感觉慢」
3. **可测试**：先在测试环境验证退出条件
4. **可追溯**：每次退出都有原因记录（用于改进）

## 与其他站点关系

- **chaos/02-chaos-mesh**：Chaos Mesh 的爆炸半径配置
- **system-design/08-availability**：可用性分级
- **devops/06-best-practices**：灰度发布流程


<!-- auto-enrich:do-not-edit -->

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
