---
title: 熔断器
---

# 熔断器

## 三态状态机

熔断器三态：

```
       成功 / 错误率低于阈值
CLOSED ─────────────────────────► CLOSED (继续请求)
  │                                    ▲
  │ 错误率超阈值                        │
  ▼                                    │
OPEN ──── 经过 sleepWindow ────► HALF_OPEN
  │                                    │
  │ 直接拒绝                            │
  ▼                                    │
直接失败 (Fallback)                  探测请求
                                  成功→CLOSED
                                  失败→OPEN
```

**CLOSED（关闭）**：正常状态，请求正常通过。

**OPEN（开启）**：错误率超阈值，所有请求直接失败（不调用下游）。

**HALF_OPEN（半开）**：经过 sleepWindow 后，允许少量探测请求。成功 → CLOSED，失败 → OPEN。

## Resilience4j 实现

```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)
    .slowCallRateThreshold(80)
    .slowCallDurationThreshold(Duration.ofSeconds(2))
    .slidingWindowSize(100)
    .minimumNumberOfCalls(20)
    .waitDurationInOpenState(Duration.ofSeconds(30))
    .build();

CircuitBreaker breaker = CircuitBreaker.of("paymentService", config);

CheckedSupplier<String> supplier = CircuitBreaker.decorateCheckedSupplier(breaker,
    () -> paymentClient.charge(orderId, amount));

try {
    return supplier.get();
} catch (CallNotPermittedException e) {
    return "fallback";
}
```

**关键参数**：

- `failureRateThreshold`：错误率阈值（默认 50%）
- `slidingWindowSize`：统计窗口（默认 100 请求）
- `permittedNumberOfCallsInHalfOpenState`：半开探测请求数（默认 10）
- `waitDurationInOpenState`：OPEN 状态持续时间（默认 60s）
- `slowCallDurationThreshold`：慢调用阈值（默认 2s）
- `slowCallRateThreshold`：慢调用率阈值（默认 100%）

## gobreaker（Go）实现

```go
settings := gobreaker.Settings{
    Name:        "paymentService",
    MaxRequests: 5,            // HALF_OPEN 最大探测
    Interval:    60 * time.Second,
    Timeout:     30 * time.Second,
    ReadyToTrip: func(counts gobreaker.Counts) bool {
        failureRatio := float64(counts.TotalFailures) / float64(counts.Requests)
        return counts.Requests >= 10 && failureRatio >= 0.5
    },
}
cb := gobreaker.NewCircuitBreaker(settings)
result, err := cb.Execute(func() (interface{}, error) {
    return paymentClient.Charge(ctx, orderID, amount)
})
```

## 熔断器与重试组合

**调用链**：

```
调用方 → Retry → CircuitBreaker → 实际下游
```

**原则**：

- Retry 在 CircuitBreaker 外层
- 避免熔断状态变化干扰重试逻辑
- Retry + CircuitBreaker 都失败 → 触发 Fallback

**陷阱**：重试次数过多会「穿透」熔断器（破坏熔断效果）。例：每次重试 3 次 → 实际请求 9 次。

**Resilience4j 组合**：

```java
// 顺序：Retry → CircuitBreaker → Bulkhead → 实际调用
Supplier<String> decorated = Decorators.ofSupplier(() -> paymentClient.charge(orderId, amount))
    .withRetry(retry)
    .withCircuitBreaker(breaker)
    .withBulkhead(bulkhead)
    .withFallback(Arrays.asList(CallNotPermittedException.class, BulkheadFullException.class),
                  e -> "fallback")
    .decorate();
```

## 与其他站点关系

- **chaos/05-resilience-patterns/retry-backoff**：重试 + 熔断
- **design-pattern/05-architectural-patterns**：Circuit Breaker 模式
- **system-design/08-availability**：可用性原则
