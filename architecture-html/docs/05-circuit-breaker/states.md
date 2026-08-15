---
title: 熔断器三态
---
# 熔断器（Circuit Breaker）

## 1. 解决什么问题

```
服务 A 调用服务 B：
  - B 慢 → A 线程阻塞 → A 资源耗尽 → 雪崩
  - B 故障 → A 持续失败 → 浪费 CPU

熔断器：B 故障率高 → 直接拒绝（fail fast），保护 A
```

Martin Fowler 2014 年提出。

## 2. 三种状态

```
            失败率 < 阈值
    CLOSED ─────────────────► CLOSED
       │                        ▲
       │ 失败率 ≥ 阈值           │ 探测成功
       ▼                        │
      OPEN ─────────────────► HALF_OPEN
       │                        │
       │ 超时（默认 30s）         │ 探测失败
       └────────────────────────┘
```

| 状态 | 行为 |
|------|------|
| **CLOSED**（关闭） | 正常：所有请求通过；统计失败率 |
| **OPEN**（断开） | 拒绝所有请求（fail fast）；超时后转 HALF_OPEN |
| **HALF_OPEN**（半开）| 放少量探测请求；都成功 → CLOSED，有失败 → OPEN |

## 3. 关键参数

```yaml
windowInMillis: 10000     # 滑动窗口大小（10s）
requestVolumeThreshold: 20  # 最小请求数（太少不触发）
errorThresholdPercentage: 50 # 失败率阈值（50%）
sleepWindowInMillis: 30000   # OPEN 状态持续时间
```

## 4. 与线程池 / 信号量的区别

| | 熔断器 | 限流 | 线程池隔离 |
|------|------|------|------|
| 目的 | 防止依赖故障拖垮自己 | 控制请求速率 | 隔离线程池 |
| 触发 | 失败率超阈值 | 速率超阈值 | 队列满 |
| 恢复 | 探测 | 持续 | 自动 |
| 副作用 | 拒绝请求 | 拒绝请求 | 拒绝新任务 |

熔断 + 限流 = 完整的"高可用三件套"。

## 5. 实战：线程池 + 熔断

```java
// 伪代码
public Result callService() {
  if (!circuitBreaker.allow()) {
    return fallback();              // 快速失败
  }
  try (var ignored = circuitBreaker.mark()) {
    return remoteCall();
  } catch (Exception e) {
    circuitBreaker.onError();
    return fallback();
  }
}
```

## 6. 半开态（HALF_OPEN）详解

关键设计：探测请求数 = 1 还是 N？

```
N=1: 1 个成功就关，1 个失败就开（响应快）
N=k%窗口请求:  50% 成功就关（更稳）
```

Sentinel 默认：探测请求数 = 1。

## 7. 实战配置

```java
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
  .failureRateThreshold(50)        // 50% 失败率
  .slowCallRateThreshold(50)
  .slowCallDurationThreshold(Duration.ofSeconds(2))
  .slidingWindowType(SlidingWindowType.TIME_BASED)
  .slidingWindowSize(10)            // 10 秒窗口
  .minimumNumberOfCalls(10)         // 至少 10 个调用才判断
  .permittedNumberOfCallsInHalfOpenState(3)
  .waitDurationInOpenState(Duration.ofSeconds(30))
  .build();
```

## 8. 常见问题

```
Q: 熔断触发后多久恢复？
A: waitDurationInOpenState（默认 30s）→ HALF_OPEN

Q: 熔断器嵌套？
A: 多次调用同一服务 → 共享同一个熔断器（key by 服务名）

Q: 半开态探测失败？
A: 立即重开 → 等待 → 再次探测

Q: 熔断和重试的区别？
A: 重试：希望成功；熔断：放弃（避免拖垮）
```

## 9. 配合 fallback

```java
public Result callWithFallback(Supplier<Result> call) {
  if (!circuitBreaker.allow()) {
    return cache.get() or defaultValue();  // Fallback
  }
  try {
    return call.get();
  } catch (Exception e) {
    return cache.get() or defaultValue();
  }
}
```

## 🔗 下一步
- [Sentinel / Hystrix](/05-circuit-breaker/impl)
- [Fallback 设计](/05-circuit-breaker/fallback)
- [限流](/04-rate-limit/token-bucket)
