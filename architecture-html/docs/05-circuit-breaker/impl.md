---
title: Sentinel / Hystrix / Resilience4j
---
# 熔断器实现

## 1. Hystrix（已停止维护）

Netflix 2012 出品，2018 宣布停止主动开发。**设计思想仍是标准**。

```
HystrixCommand<User> getUser = (HystrixCommand<User>) HystrixCommands
  .newBuilder(HystrixCommand.Setter.withGroupKey("user-service"))
  .andCommandKey("getUser")
  .andThreadPoolKey("user-service")
  .andCommandPropertiesDefaults(HystrixCommandProperties.defaultSetter()
    .withCircuitBreakerRequestVolumeThreshold(20)
    .withCircuitBreakerSleepWindowInMilliseconds(10000)
    .withCircuitBreakerErrorThresholdPercentage(50))
  .andCommandKeyDefaults(...);
```

**关键概念**：Command 模式 + 滑动窗口统计 + 隔离（线程池 / 信号量）+ Fallback。

## 2. Resilience4j（推荐）

Java 8+ 函数式风格，轻量（无线程池隔离），模块化：

```xml
<dependency>
  <groupId>io.github.resilience4j</groupId>
  <artifactId>resilience4j-spring-boot3</artifactId>
  <version>2.2.0</version>
</dependency>
```

```java
@Service
public class UserService {
  @CircuitBreaker(name = "user-service", fallbackMethod = "fallback")
  public User getUser(Long id) {
    return remoteCall(id);
  }
  private User fallback(Long id, Throwable t) {
    return User.defaultUser();
  }
}
```

**模块**：
- CircuitBreaker（熔断）
- Retry（重试）
- RateLimiter（限流）
- BulkHead（舱壁隔离）
- TimeLimiter（超时）
- Retry（重试，组合熔断）

## 3. Sentinel（阿里出品，国内最常用）

```xml
<dependency>
  <groupId>com.alibaba.csp</groupId>
  <artifactId>sentinel-core</artifactId>
  <version>1.8.6</version>
</dependency>
```

```java
// 限流
FlowRule rule = new FlowRule("user-service")
  .setGrade(RuleConstant.FLOW_GRADE_QPS)
  .setCount(20);  // QPS 上限 20
FlowRuleManager.loadRules(Collections.singletonList(rule));

// 熔断
DegradeRule degradeRule = new DegradeRule("user-service")
  .setGrade(CircuitBreakerStrategy.ERROR_COUNT)
  .setCount(10)
  .setMinRequestAmount(20)
  .setSlowRatioThreshold(0.5);
DegradeRuleManager.loadRules(Collections.singletonList(degradeRule));

// 包装调用
try (Entry entry = SphU.entry("user-service")) {
  return remoteCall();
} catch (BlockException e) {
  return fallback();
}
```

**Sentinel 优势**：规则动态加载（Dashboard 动态调整）、实时监控、应用广泛（阿里系、Spring Cloud Alibaba）。

## 4. 三者对比

| 特性 | Hystrix | Resilience4j | Sentinel |
|------|---------|---------------|----------|
| 状态 | 维护停止 | 活跃 | 活跃 |
| 线程隔离 | 有（线程池） | 无（信号量） | 有（信号量） |
| Dashboard | 少 | 中 | **强**（独立控制台） |
| 性能 | 较重 | 轻 | 轻 |
| 国内使用 | 少 | 中 | **多** |
| 推荐场景 | 老项目 | 新项目（Spring Boot） | 国内微服务 |

## 5. Spring Cloud Circuit Breaker

Spring Cloud 抽象统一的 API：

```yaml
resilience4j:
  circuitbreaker:
    instances:
      user-service:
        slidingWindowType: TIME_BASED
        slidingWindowSize: 10
        minimumNumberOfCalls: 10
        failureRateThreshold: 50
        waitDurationInOpenState: 30s
        permittedNumberOfCallsInHalfOpenState: 3
```

自动接入 `@CircuitBreaker(name = "user-service", fallbackMethod = "fallback")`。

## 6. 服务网格中的熔断（Service Mesh）

```
应用 → Sidecar (Envoy) → 远端服务
         ↑
         熔断在 Sidecar 层（不修改应用）
```

**优势**：跨语言一致、应用零侵入、自动注入。

详见 [Service Mesh](/12-microservice-patterns/service-mesh)。

## 7. 实战选型

```
新项目 + Spring Boot    → Resilience4j（Spring Cloud 生态）
阿里系 / 国内微服务     → Sentinel（Dashboard 强）
Java 8- 旧项目          → Hystrix（维护模式，仍可用）
多语言微服务            → Service Mesh（应用无侵入）
```

## 8. 实战：组合使用

```java
// 完整的高可用：限流 + 熔断 + 重试 + Fallback
@Service
public class OrderService {
  @RateLimiter(name = "order", fallbackMethod = "limiterFallback")
  @Retry(name = "order", fallbackMethod = "retryFallback")
  @CircuitBreaker(name = "order", fallbackMethod = "circuitFallback")
  @Bulkhead(name = "order")
  public Order createOrder(OrderRequest req) {
    return orderClient.createOrder(req);
  }
  // 三种 fallback 分别处理限流/重试/熔断场景
}
```

## 🔗 下一步
- [熔断器三态](/05-circuit-breaker/states)
- [Fallback 设计](/05-circuit-breaker/fallback)
- [限流](/04-rate-limit/token-bucket)
