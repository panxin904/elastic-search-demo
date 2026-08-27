---
title: Saga / Bulkhead
---
# Saga 与 Bulkhead 模式

## 1. Saga 模式

详见 [Saga 模式](/07-distributed-tx/saga)。在微服务模式下：

```
订餐 Saga：
  1. 创建订单（OrderService）
  2. 扣库存（InventoryService）
  3. 扣款（PaymentService）
  4. 发通知（NotificationService）

任一失败 → 补偿：
  1. 取消订单
  2. 恢复库存
  3. 退款
  4. 发补偿通知
```

## 2. Saga 模式 vs Microservices

| | Saga | 同步 RPC |
|--|------|----------|
| 失败处理 | 自动补偿 | 需手动 try-catch |
| 数据一致性 | 最终一致 | 强一致（锁） |
| 性能 | 异步（快） | 同步（慢） |
| 复杂度 | 中 | 低 |

**实践**：用 Saga + 幂等 + 状态机。

## 3. Bulkhead（舱壁模式）

**防止一个故障拖垮整个系统**——船舱隔水。

```
❌ 共享线程池：
  服务 A 慢 → 线程池满 → 服务 B 也慢

✅ Bulkhead 隔离：
  服务 A 一个池
  服务 B 一个池
  A 慢了只影响 A
```

## 4. Bulkhead 实战

```java
// Resilience4j Bulkhead
@Bulkhead(name = "order-service", type = Bulkhead.Type.SEMAPHORE,
          maxConcurrentCalls = 100, maxWaitDuration = 100)
public CompletableFuture<Order> placeOrder(OrderDTO dto) {
  // 100 并发上限，超出排队 100ms
}
```

## 5. 舱壁 vs 熔断 vs 限流

| | 舱壁 | 熔断 | 限流 |
|--|------|------|------|
| 目的 | 资源隔离 | 失败隔离 | 速率控制 |
| 触发 | 并发数超阈值 | 失败率超阈值 | 速率超阈值 |
| 副作用 | 拒绝（排队/拒绝） | 快速失败 | 拒绝 |

**组合**：舱壁（隔离）+ 熔断（防雪崩）+ 限流（防过载）= 完整防护。

## 6. 舱壁的 4 种实现

| 类型 | 描述 |
|------|------|
| **线程池** | 不同服务不同池（Tomcat thread pool） |
| **信号量（Semaphore）** | 限制并发数（ReentrantLock + Semaphore） |
| **进程隔离** | 不同服务不同进程 |
| **集群隔离** | 不同服务不同集群 / K8s namespace |

## 7. 实战：舱壁 + 限流 + 熔断组合

```java
@Service
public class OrderService {
  @Bulkhead(name = "order", maxConcurrentCalls = 100)
  @CircuitBreaker(name = "order", fallbackMethod = "fallback")
  @RateLimiter(name = "order")
  public Order createOrder(OrderDTO dto) {
    return remoteCall(dto);
  }
}
```

**Resilience4j 注解组合**：同时启用 3 个保护。

## 8. Saga 模式 in Microservices

详见 [Saga 模式](/07-distributed-tx/saga) - 微服务版用事件驱动 Saga：

```
Order 聚合：orderRepo.create()
   → 发 OrderCreated 事件
Inventory 聚合：@EventListener onOrderCreated() { deduct() }
   → 发 InventoryFrozen 事件
Payment 聚合：@EventListener onInventoryFrozen() { charge() }
   → 发 PaymentCompleted 事件
Order 聚合：@EventListener onPaymentCompleted() { confirm() }
```

## 9. 微服务常用模式汇总

| 模式 | 目的 | 库 / 工具 |
|------|------|----------|
| 服务发现 | 找到服务实例 | Nacos / Consul / Eureka |
| API 网关 | 外部流量入口 | Kong / APISIX / Spring Cloud Gateway |
| 熔断 | 防雪崩 | Sentinel / Hystrix / Resilience4j |
| 限流 | 防过载 | Sentinel / Guava RateLimiter |
| 舱壁 | 资源隔离 | Resilience4j Bulkhead |
| 分布式配置 | 配置管理 | Nacos / Apollo / Spring Cloud Config |
| 分布式事务 | 强一致 | Seata TCC / Saga |
| 服务网格 | 网络层抽象 | Istio / Linkerd |
| Saga | 长事务 | Seata Saga / Temporal / Camunda |
| CQRS | 读写分离 | Axon / 自研 |
| Event Sourcing | 事件溯源 | Axon / 自研 |
| Outbox | 可靠发消息 | Debezium / 自研 |

## 10. 实战选型

| 场景 | 选 |
|------|-----|
| 微服务新项目 | Nacos + Sentinel + Seata |
| 多语言 + 强可观测 | Service Mesh（Istio）+ Nacos |
| 简单 + 少服务 | Spring Cloud 全家桶 |
| 高并发 | 限流 + 舱壁 + 消息队列 |

## 🔗 下一步
- [Service Mesh](/12-microservice-patterns/service-mesh)
- [Sidecar 模式](/12-microservice-patterns/sidecar)
- [Saga 模式](/07-distributed-tx/saga)

<!-- svg-injected:do-not-edit -->

![cqrs flow](/cqrs-flow.svg)
