---
title: 重试与退避
date: 2026-08-15  # date-auto-injected
---

# 重试与退避

## 重试三要素

**1. 重试条件**：

- 重试：网络错误 / 超时 / 5xx / 特定业务码
- 不重试：4xx（业务错误 / 权限 / 参数错误）

**2. 退避策略**：

- **指数退避（Exponential Backoff）**：`delay = base * 2^attempt`
  - 示例：1s, 2s, 4s, 8s, 16s
- **指数退避 + 抖动（Jitter）**：`delay = base * 2^attempt * (1 + random(0, 0.5))`
  - 避免「thundering herd」（多个客户端同时重试）
- **固定退避**：固定 1s（不推荐，易雪崩）

**3. 重试上限**：

- 最大次数：3-5 次（避免无限重试）
- 最大时长：30 秒（总耗时上限）

## Resilience4j 实现（Java）

```java
RetryConfig config = RetryConfig.custom()
    .maxAttempts(3)
    .intervalFunction(IntervalFunction.ofExponentialRandomBackoff(
        Duration.ofMillis(500),  // initialInterval
        2.0,                     // multiplier
        0.5                      // randomizationFactor
    ))
    .retryExceptions(IOException.class, TimeoutException.class)
    .build();

Retry retry = Retry.of("paymentService", config);

CheckedSupplier<String> supplier = Retry.decorateCheckedSupplier(retry,
    () -> paymentClient.charge(orderId, amount));

try {
    return supplier.get();
} catch (Throwable t) {
    return "fallback";
}
```

## Go 实现（cenkalti/backoff）

```go
func chargeWithRetry(ctx context.Context, orderID string, amount int) error {
    backoff := backoff.NewExponentialBackOff()
    backoff.InitialInterval = 500 * time.Millisecond
    backoff.MaxInterval = 30 * time.Second
    backoff.MaxElapsedTime = 2 * time.Minute

    operation := func() error {
        _, err := paymentClient.Charge(ctx, orderID, amount)
        return err
    }
    return backoff.RetryNotify(operation, backoff.WithContext(ctx), onError)
}
```

**参数调优**：

- `InitialInterval`：初始延迟（500ms - 1s）
- `MaxInterval`：最大延迟（30s - 1min）
- `MaxElapsedTime`：总耗时上限（1min - 5min）
- `Multiplier`：指数倍数（2.0 - 3.0）

## 幂等性要求

**重试必须保证「多次调用效果一致」**。

**支付场景**：

```http
POST /payments HTTP/1.1
Host: api.example.com
Authorization: Bearer xxx
Idempotency-Key: ord_12345_pay_v1  # 关键
Content-Type: application/json

{"orderId": "12345", "amount": 1000}
```

服务端处理：

```python
def charge_with_idempotency(order_id, amount, idempotency_key):
    # 检查 Idempotency-Key 是否已处理
    cached = redis.get(f"idempotency:{idempotency_key}")
    if cached:
        return cached

    # 实际扣款
    result = payment_client.charge(order_id, amount)

    # 缓存结果（24 小时）
    redis.setex(f"idempotency:{idempotency_key}", 86400, result)
    return result
```

**数据库乐观锁**：

```sql
UPDATE accounts
SET balance = balance - 100
WHERE account_id = 12345
  AND version = 1  -- 乐观锁
  AND balance >= 100;
-- 如果影响行数 = 0 → 重试
```

## 与其他站点关系

- **chaos/05-resilience-patterns/circuit-breaker**：重试 + 熔断组合
- **design-pattern/05-architectural-patterns**：重试模式
- **system-design/08-availability**：可用性原则


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
