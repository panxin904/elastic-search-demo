---
title: 韧性模式总览
---

# 韧性模式总览

## 韧性模式定义

韧性模式（Resilience Patterns）是**系统应对故障的设计模式**，与设计模式（Design Patterns）层级类似，但聚焦「**在故障下保持功能**」而非「解决常见设计问题」。

**与设计模式的关系**：

- 设计模式（design-pattern 站）：OO / 架构 / 分布式模式（Circuit Breaker / Bulkhead 属于这一类）
- 韧性模式（本节）：聚焦「**故障场景的应对策略**」

**核心韧性模式**：

| 模式 | 目标 | 故障场景 |
|---|---|---|
| **重试 + 退避** | 应对瞬时故障 | 网络抖动 / GC 暂停 |
| **超时** | 避免级联等待 | 慢响应 / 死锁 |
| **熔断器** | 避免雪崩 | 下游服务故障 |
| **舱壁** | 资源隔离 | 线程池耗尽 / 数据库连接耗尽 |
| **限流** | 流量整形 | 突发流量 / 攻击 |
| **降级** | 功能降级 | 非核心功能失效 |
| **缓存** | 减少依赖 | 数据库压力大 |
| **幂等性** | 重复请求安全 | 网络重传 |
| **多活** | 区域故障 | Region 不可用 |
| **灾备** | 极端故障 | 自然灾害 / 大范围故障 |

**Netflix 公开分享的「Hystrix 模式」（已 deprecated，演化为 Resilience4j）**：

- 隔离（线程池 / 信号量）
- 熔断（滑动窗口 + 错误率阈值）
- 降级（fallback 方法）
- 监控（事件流 + dashboard）

**Hystrix 2020 停止维护原因**：

- Reactive 编程兴起（Project Reactor / RxJava）
- 服务网格接管（Istio / Linkerd 提供熔断 / 重试 / 限流）
- Resilience4j（Java）+ Polly（.NET）+ Sentinel（阿里）替代

**当前推荐**：

- **Java**：Resilience4j（轻量 / 函数式）
- **Go**：sony/gobreaker + cenkalti/backoff
- **Python**：tenacity（重试）+ circuitbreaker
- **TypeScript**：opossum
- **服务网格**：Istio / Linkerd 统一治理

## 重试 + 退避（Retry + Backoff）

**核心思想**：瞬时故障（网络抖动 / GC / 重启）通过重试可恢复。但盲目重试会放大故障（**retry storm**）。

**重试三要素**：

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

**Resilience4j 实现**：

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

**Go 实现**：

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

**幂等性要求**：

- 重试必须保证「**多次调用效果一致**」
- 支付场景：用 `Idempotency-Key` 头保证唯一性
- 数据库：乐观锁 + 版本号

**实战陷阱**：

- 重试 + 非幂等接口 = 重复扣款
- 重试 + 无超时 = 线程池耗尽
- 重试 + 无降级 = 用户长时间等待

## 熔断器（Circuit Breaker）

**核心思想**：当下游服务故障率超过阈值，**快速失败**而非继续等待，保护调用方资源。

**三态状态机**：

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

**关键参数**：

- **failureRateThreshold**：错误率阈值（默认 50%）
- **slidingWindowSize**：统计窗口（默认 100 请求）
- **permittedNumberOfCallsInHalfOpenState**：半开探测请求数（默认 10）
- **waitDurationInOpenState**：OPEN 状态持续时间（默认 60s）
- **slowCallDurationThreshold**：慢调用阈值（默认 2s）
- **slowCallRateThreshold**：慢调用率阈值（默认 100%）

**Resilience4j 实现**：

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
    // 熔断器 OPEN，直接返回降级结果
    return "fallback";
}
```

**gobreaker（Go）实现**：

```go
settings := gobreaker.Settings{
    Name:        "paymentService",
    MaxRequests: 5,            // HALF_OPEN 最大探测
    Interval:    60 * time.Second,  // 滑动窗口
    Timeout:     30 * time.Second,  // OPEN 持续
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

**熔断器与重试组合**：

```
调用方 → Retry → CircuitBreaker → 实际下游
```

- Retry 在 CircuitBreaker 外层：避免熔断状态变化干扰重试逻辑
- Retry + CircuitBreaker 都失败 → 触发 Fallback
- 注意：重试次数过多会「穿透」熔断器（破坏熔断效果）

## 限流与降级（Rate Limit & Degrade）

**限流（Rate Limiting）**：在**入口处**控制流量，避免突发打垮服务。

**降级（Degrade）**：在**依赖故障**时，关闭非核心功能，保核心功能可用。

**限流算法**：

**1. 令牌桶（Token Bucket）**：

- 桶容量 N，每 R 秒加 1 个令牌
- 请求消耗 1 个令牌，无令牌则拒绝
- 允许突发（桶满时可瞬时 N 个）

**2. 漏桶（Leaky Bucket）**：

- 请求进入桶，桶以固定速率漏水
- 桶满则溢出（拒绝）
- 强制平滑输出

**3. 滑动窗口（Sliding Window）**：

- 滚动时间窗口（1 分钟内最多 N 个请求）
- 比固定窗口更平滑

**4. 计数器（Counter）**：

- 简单：每分钟一个计数器
- 缺点：窗口边界突刺（59 秒 + 1 秒可瞬时 2N）

**Sentinel（阿里）实现**：

```java
// 定义资源
@SentinelResource(value = "orderCreate", blockHandler = "handleBlock")
public Order createOrder(OrderRequest req) {
    return orderService.create(req);
}

// handleBlock
public Order handleBlock(OrderRequest req, BlockException e) {
    throw new RateLimitException("too many requests");
}

// 配置规则（Sentinel Dashboard）
FlowRule rule = new FlowRule("orderCreate")
    .setGrade(RuleConstant.FLOW_GRADE_QPS)
    .setCount(1000);  // QPS 1000
FlowRuleManager.loadRules(Collections.singletonList(rule));
```

**降级策略**：

**1. 功能降级**：

- 大促期间关闭「推荐」「个性化」非核心功能
- 关闭「历史订单查询」→ 只显示最近 7 天
- 关闭「评论 / 评分」

**2. 数据降级**：

- 用 cached data 替代实时查询
- 用 default value（如返回空列表）
- 用上次成功结果（stale-while-error）

**3. 链路降级**：

- 主链路 → 简化版（跳过非关键步骤）
- 同步链路 → 异步链路

**4. 自动 vs 手动降级**：

- 自动：根据 SLO / 错误率自动触发
- 手动：运维手动开关（如「双 11 大促开关」）

## 舱壁与隔离（Bulkhead）

**核心思想**：把共享资源（线程池 / 连接池）按「业务 / 用户 / 租户」隔离，避免一个慢调用拖垮整个系统。

**类比**：船的舱壁（bulkhead）—— 一个舱进水不会导致整船沉没。

**隔离层级**：

**1. 线程池隔离**：

- 每个下游服务一个独立线程池
- payment-service 线程池满 → order-service 不受影响
- 缺点：线程上下文切换开销

**2. 信号量隔离**：

- 轻量（不切换线程）
- 仅限制并发数，不隔离线程
- 适用：纯计算型调用

**3. 进程隔离**：

- 每个下游服务独立进程（Sidecar）
- Istio / Linkerd 默认采用

**4. 集群隔离**：

- 物理集群分组（核心 / 非核心）
- 大促前把核心服务独立集群

**Resilience4j Bulkhead（线程池版）**：

```java
BulkheadConfig config = BulkheadConfig.custom()
    .maxConcurrentCalls(20)
    .maxWaitDuration(Duration.ofMillis(500))
    .build();

Bulkhead bulkhead = Bulkhead.of("paymentService", config);

CheckedSupplier<String> supplier = Bulkhead.decorateCheckedSupplier(bulkhead,
    () -> paymentClient.charge(orderId, amount));
```

**Sidecar 隔离（Istio）**：

每个 Pod 一个 Envoy Sidecar，自动隔离：

- payment-service Pod 的 Envoy 故障 → order-service 不受影响
- Envoy 资源（CPU / 内存）独立管理

**数据库连接池隔离**：

- HikariCP 多实例：order / payment / inventory 各自独立连接池
- 慢查询拖垮 payment 连接池 → 不影响 order

**多租户隔离**：

- SaaS 场景：每个租户独立资源
- 「吵闹邻居」（Noisy Neighbor）问题

**舱壁大小调优**：

- 太小：拒绝率过高
- 太大：失去隔离意义
- 推荐：`maxConcurrentCalls = (QPS * P99延迟) / 1000`
- 例：QPS 1000 / P99 200ms → maxConcurrentCalls = 200

## 多活与灾备（Multi-Region DR）

**多活（Active-Active）**：多个 Region 同时服务流量。

**灾备（Active-Passive / DR）**：主 Region 服务流量，备 Region 待机。

**多活架构层级**：

**1. DNS 层**：

- 智能 DNS（Route 53 / AliDNS）按地理位置解析
- 健康检查 + 故障转移

**2. 全球负载均衡**：

- AWS Global Accelerator / Cloudflare Spectrum
- 任意cast IP（Anycast）

**3. 数据库同步**：

- 同步复制（强一致）：性能损耗
- 异步复制（最终一致）：性能高，但 RPO > 0
- 双向同步（Active-Active）：冲突处理复杂

**灾备 RTO / RPO 矩阵**：

| 级别 | RTO（恢复时间） | RPO（数据丢失） | 成本 |
|---|---|---|---|
| L0（无灾备） | 小时级 | 不保证 | $0 |
| L1（备份恢复） | 24 小时 | 24 小时 | $ |
| L2（同城灾备） | 1 小时 | 几分钟 | $$ |
| L3（异地灾备） | 4 小时 | 几分钟 | $$$ |
| L4（同城多活） | 分钟级 | 秒级 | $$$$ |
| L5（异地多活） | 分钟级 | 秒-分钟 | $$$$$ |

**金融业典型要求**：

- 支付系统：L4（同城多活）
- 银行核心：L5（异地多活）

**Chaos Engineering 验证**：

1. **Region kill 实验**：
   - chaos-mesh AWSChaos：随机停止一个 AZ 的 EC2
   - 验证：流量 100% 自动转移到其他 AZ
   - 验证：RTO < 5 分钟（自动恢复）

2. **数据库主从切换实验**：
   - chaos-mesh + Redis Sentinel：手动 failover
   - 验证：写请求自动路由到新主
   - 验证：RPO < 1 秒（异步复制延迟）

3. **DNS 切换实验**：
   - 注入 DNS 解析失败
   - 验证：客户端 failover 到备用 DNS

**多活架构陷阱**：

- 不考虑数据冲突（同一订单在两个 Region 创建）
- 时钟不同步（订单时间错乱）
- 流量调度策略简单（无权重 / 无健康检查）
- 灾备演练不足（主 Region 真挂了切不动）

**典型多活案例**：

- **阿里淘宝**：3 地 5 中心（同城 + 异地）
- **AWS S3**：11 个 9 的可用性（多区域存储）
- **Netflix**：跨 AWS Region 多活 + Chaos Monkey 持续验证

**混沌工程在多活中的价值**：

- 验证切换流程（不只是架构图上的线）
- 验证数据一致性（冲突处理逻辑）
- 验证恢复时间（RTO / RPO 实际值）
- 持续验证（不是一次性）

## 与其他站点的关系

- **design-pattern**：Circuit Breaker / Bulkhead / Outbox 是「**代码层实现**」 → 引用 design-pattern/05-architectural-patterns
- **system-design**：可用性原则 / 多活架构 → 引用 system-design/08-availability
- **observability**：熔断指标 / 限流指标 → 引用 observability/03-prometheus
- **devops**：韧性验证纳入 CI/CD → 引用 devops/05-cicd-observability
- **architecture**：微服务韧性 / 服务网格 → 引用 architecture/05-microservices

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 混沌
- [observability](https://java-px.bot.cd/observability/):故障注入监控
- [system-design](https://java-px.bot.cd/system-design/):系统韧性
