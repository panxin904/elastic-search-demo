---
title: Circuit Breaker 熔断模式
date: 2026-08-15  # date-auto-injected
description: 下游故障快速失败 + Resilience4j / Sentinel / Hystrix + 三种状态
---

# Circuit Breaker 熔断模式

## 核心问题

当下游服务出现故障时（响应慢 / 异常率高 / 完全不可用），上游服务如果继续调用会导致：

1. **线程池耗尽**：上游请求 hang 在等待下游
2. **资源耗尽**：CPU / 内存 / 连接池被占满
3. **雪崩效应**：整个系统级联失败
4. **用户体验差**：超时 30 秒后才返回错误

## 核心思想

当检测到下游故障率超过阈值时，**熔断器打开**，上游直接快速失败（fallback），不调用下游，给下游恢复时间。

**三种状态**：
```
       失败率 < 阈值        失败率 ≥ 阈值
CLOSED ──────────────→ OPEN
   ↑                      │
   │    经过 sleepWindow   │
   └──── HALF_OPEN ←──────┘
            │
            │ 试探请求成功 → CLOSED
            │ 试探失败 → OPEN
```

## Resilience4j 实战

```java
@Service
public class PaymentService {
    @CircuitBreaker(name = "payment", fallbackMethod = "paymentFallback")
    public PaymentResult pay(PaymentRequest req) {
        return paymentClient.charge(req);  // 可能超时 / 抛异常
    }

    // 熔断后的 fallback（必须有相同签名 + Throwable 参数）
    private PaymentResult paymentFallback(PaymentRequest req, Throwable t) {
        log.warn("payment service unavailable: {}", t.getMessage());
        // 1. 排队等待 / 异步重试
        // 2. 返回默认值
        // 3. 抛业务异常
        return PaymentResult.deferred(req.getOrderId());
    }
}

// 配置
resilience4j:
  circuitbreaker:
    instances:
      payment:
        failureRateThreshold: 50        # 失败率 50% 触发熔断
        slowCallRateThreshold: 100      # 慢调用 100% 触发
        slowCallDurationThreshold: 2s   # 2 秒算慢调用
        slidingWindowSize: 100          # 滑动窗口 100 个请求
        minimumNumberOfCalls: 10        # 至少 10 个请求才计算
        waitDurationInOpenState: 10s    # OPEN 状态保持 10 秒
        permittedNumberOfCallsInHalfOpenState: 3  # HALF_OPEN 试 3 次
        recordExceptions:
          - java.io.IOException
          - java.util.concurrent.TimeoutException
        ignoreExceptions:
          - com.example.BusinessException  # 业务异常不计入失败
```

## 编程式使用

```java
CircuitBreaker circuitBreaker = CircuitBreaker.ofDefaults("payment");

CheckedSupplier<PaymentResult> supplier = CircuitBreaker.decorateCheckedSupplier(
    circuitBreaker,
    () -> paymentClient.charge(req)
);

try {
    return Try.of(supplier).getOrElse(this::fallback);
} catch (Throwable e) {
    return fallback(req, e);
}
```

## 阿里 Sentinel

```java
// Sentinel 是阿里开源的熔断限流组件
@SentinelResource(value = "payment", blockHandler = "paymentBlockHandler", fallback = "paymentFallback")
public PaymentResult pay(PaymentRequest req) {
    return paymentClient.charge(req);
}

public PaymentResult paymentBlockHandler(PaymentRequest req, BlockException e) {
    // 流控熔断
    return PaymentResult.rejected(req.getOrderId());
}

public PaymentResult paymentFallback(PaymentRequest req, Throwable e) {
    // 业务异常
    return PaymentResult.deferred(req.getOrderId());
}
```

## Sentinel 控制台

Sentinel Dashboard 提供：
- 实时监控（QPS / 响应时间 / 异常率）
- 规则配置（流控 / 熔断 / 热点）
- 集群限流
- 链路监控

## Hystrix（已停止维护）

```java
// Hystrix 是 Netflix 开源的第一代熔断器，已停止维护
// 但仍有大量遗留代码使用

@HystrixCommand(
    fallbackMethod = "paymentFallback",
    commandProperties = {
        @HystrixProperty(name = "circuitBreaker.errorThresholdPercentage", value = "50"),
        @HystrixProperty(name = "circuitBreaker.requestVolumeThreshold", value = "20"),
        @HystrixProperty(name = "circuitBreaker.sleepWindowInMilliseconds", value = "10000")
    }
)
public PaymentResult pay(PaymentRequest req) {
    return paymentClient.charge(req);
}
```

## Resilience4j vs Sentinel vs Hystrix

| | Resilience4j | Sentinel | Hystrix |
|---|---|---|---|
| 语言 | Java 8+ | Java | Java |
| 设计 | 函数式 | 注解 + 控制台 | 注解 |
| 限流 | ✅ | ✅ | ✅ |
| 熔断 | ✅ | ✅ | ✅ |
| 控制台 | ❌ | ✅（官方 Dashboard）| ✅（Hystrix Dashboard）|
| 维护 | ✅ 活跃 | ✅ 活跃 | ❌ 停止 |

推荐新项目用 **Resilience4j** 或 **Sentinel**。

## 配置参数详解

## 关键参数

| 参数 | 含义 | 推荐值 |
|---|---|---|
| **failureRateThreshold** | 失败率阈值 | 50% |
| **slowCallRateThreshold** | 慢调用率阈值 | 100% |
| **slowCallDurationThreshold** | 慢调用时长阈值 | 2s |
| **slidingWindowSize** | 滑动窗口大小 | 100 |
| **minimumNumberOfCalls** | 计算失败率最小请求数 | 10 |
| **waitDurationInOpenState** | OPEN 状态等待时间 | 10s |
| **permittedNumberOfCallsInHalfOpenState** | HALF_OPEN 试探次数 | 3-5 |
| **recordExceptions** | 计入失败的异常 | IOException, TimeoutException |
| **ignoreExceptions** | 忽略的异常 | BusinessException |

## Fallback 策略

1. **返回默认值**：订单标记「待处理」
2. **排队等待**：写入 Kafka 异步重试
3. **走备用路径**：调用备用服务
4. **抛业务异常**：让上层决定（用户友好提示）

## 适用边界

✅ **使用场景**：
- 调用下游 HTTP / gRPC 服务
- 调用数据库 / Redis / 外部 API
- 关键路径（不能让慢调用拖垮）
- 高并发场景（防止雪崩）

❌ **避免场景**：
- 单体内部调用（不跨网络）
- 性能极敏感（熔断器有开销）
- 业务简单到不会失败（过度设计）

🔄 **配套模式**：
- **Bulkhead**：舱壁隔离（资源池）
- **Retry**：重试（结合熔断使用）
- **Timeout**：超时控制（熔断的前置条件）
- **Fallback**：降级策略（熔断后的行为）

💡 **最佳实践**：
- 必须配 fallback（不配等于没熔断）
- 超时时间要合理（不能太长）
- 区分业务异常（不计入失败率）
- 监控熔断器状态变化（告警）
