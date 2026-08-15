---
title: 限流熔断
---

# 限流熔断

限流控制流量入口，熔断保护下游服务，是系统稳定性的最后防线。

## 限流

### Sentinel（推荐）

```java
// 注解方式
@SentinelResource(value = "createOrder", blockHandler = "blockHandler")
@PostMapping("/orders")
public Result create(@RequestBody OrderDTO dto) {
    return Result.success(orderService.create(dto));
}

// 限流后的降级方法
public Result blockHandler(OrderDTO dto, BlockException e) {
    return Result.error(2006, "系统繁忙，请稍后重试");
}
```

### Guava RateLimiter（单机）

```java
@Component
public class RateLimiterConfig {
    private final RateLimiter rateLimiter = RateLimiter.create(100.0);  // 100 QPS

    public boolean tryAcquire() {
        return rateLimiter.tryAcquire(100, TimeUnit.MILLISECONDS);
    }
}
```

## 熔断

当某个服务持续失败，熔断器打开，直接返回降级结果而不是继续调用。

```
状态转换:
    CLOSED ──(失败次数达标)──> OPEN
    OPEN ──(冷却时间到)──> HALF_OPEN
    HALF_OPEN ──(尝试成功)──> CLOSED
    HALF_OPEN ──(尝试失败)──> OPEN
```

### Sentinel 熔断规则

```java
@Bean
public DegradeRule degradeRule() {
    DegradeRule rule = new DegradeRule("payService")
        .setGrade(RuleConstant.DEGRADE_GRADE_RT)  // 慢调用比例
        .setCount(1000)       // RT > 1000ms 视为慢调用
        .setTimeWindow(10)    // 熔断 10 秒
        .setMinRequestAmount(5);
    return rule;
}
```

## 降级策略

| 策略 | 说明 | 示例 |
|---|---|---|
| 返回默认值 | 返回兜底数据 | 推荐列表返回热门商品 |
| 返回缓存 | 用缓存数据 | 商品详情返回缓存 |
| 功能降级 | 关闭非核心功能 | 关闭推荐模块 |
| 排队等待 | 提示用户稍后再试 | 12306 排队系统 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="rate-limiting" :height="400" />
