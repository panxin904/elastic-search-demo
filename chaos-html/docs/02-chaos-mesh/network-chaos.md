---
title: NetworkChaos 实验
---

# NetworkChaos 实验

## NetworkChaos action 类型

NetworkChaos 支持六种网络故障动作：

**1. delay（延迟）**：

```yaml
spec:
  action: delay
  delay:
    latency: "200ms"
    correlation: "75"  # 75% 流量同步延迟
    jitter: "50ms"     # 抖动
  direction: to
```

**2. loss（丢包）**：

```yaml
spec:
  action: loss
  loss:
    loss: "1.0"  # 1% 丢包率
    correlation: "75"
```

**3. duplicate（重复）**：

```yaml
spec:
  action: duplicate
  duplicate:
    duplicate: "0.5"  # 0.5% 重复率
    correlation: "75"
```

**4. corrupt（损坏）**：

```yaml
spec:
  action: corrupt
  corrupt:
    corrupt: "0.1"  # 0.1% 损坏率
    correlation: "75"
```

**5. partition（分区）**：

```yaml
spec:
  action: partition
  direction: both
  target:
    selector:
      namespaces: [default]
    mode: all
```

**6. bandwidth（带宽限制）**：

```yaml
spec:
  action: bandwidth
  bandwidth:
    rate: "1mbps"
    buffer: 10000
```

## 实战案例：跨 AZ 延迟

**场景**：验证 checkout-service 在跨 AZ 网络延迟 200ms 时的可用性。

**实验 YAML**：

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: checkout-az-delay
  namespace: chaos-mesh
spec:
  action: delay
  mode: all
  selector:
    namespaces: [checkout]
    labelSelectors:
      app: checkout-service
  delay:
    latency: "200ms"
    correlation: "75"
    jitter: "50ms"
  direction: to
  duration: "60s"
```

**观察指标**：

```promql
# P99 延迟（期望 + 200ms 但 < 1.5s）
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{app="checkout-service"}[5m])) by (le))

# 错误率（期望 < 1%）
sum(rate(http_requests_total{status=~"5..",app="checkout-service"}[5m]))
/ sum(rate(http_requests_total{app="checkout-service"}[5m]))

# TCP 重传率（关键信号）
rate(node_netstat_tcp_retransmits[5m])
```

**预期结果**：

- 延迟增加 ~200ms
- 错误率 < 1%（circuit breaker 保护）
- 服务降级生效（fallback 到 cached data）

## 实战案例：网络分区

**场景**：payment-service 与 order-service 之间网络完全断开。

**实验 YAML**：

```yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: NetworkChaos
metadata:
  name: payment-partition
  namespace: chaos-mesh
spec:
  action: partition
  mode: all
  selector:
    namespaces: [payment]
    labelSelectors:
      app: payment-service
  target:
    selector:
      namespaces: [order]
      labelSelectors:
        app: order-service
    mode: all
  direction: both
  duration: "30s"
```

**观察指标**：

```promql
# payment-service 的成功调用率（期望快速下降）
sum(rate(payment_success_total[1m]))
/ sum(rate(payment_total[1m]))

# order-service 的支付相关错误（期望快速上升）
sum(rate(http_requests_total{status=~"5..",app="order-service",endpoint="/pay"}[1m]))
```

**预期结果**：

- order-service 在 5 秒内检测到 payment 不可用
- 熔断器 OPEN（circuit breaker）
- order-service 返回降级结果（fallback）
- 支付流程暂停（不报错，用户友好提示）
- 30 秒后自动恢复

## 与其他站点关系

- **observability/03-prometheus**：网络指标采集
- **chaos/03-litmus**：pod-network-latency 对应
- **design-pattern/05-architectural-patterns**：Circuit Breaker 验证
- **system-design/08-availability**：多活架构验证


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
