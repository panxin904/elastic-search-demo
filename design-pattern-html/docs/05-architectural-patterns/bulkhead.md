---
title: Bulkhead 舱壁隔离模式
description: 资源隔离防雪崩 + Resilience4j 线程池 + K8s resource limit + 连接池隔离
---

# Bulkhead 舱壁隔离模式

## 核心问题

当多个下游服务共享同一个资源池（线程池 / 连接池）时，一个慢服务会占满所有资源，拖垮所有其他服务调用。

**举例**：
- 共享 100 个线程：90 个被慢 payment 调用占满，剩下 10 个给 inventory / order / 用户请求
- 共享 100 个数据库连接：90 个被慢查询占满，所有其他数据库操作排队
- 共享 1000 个并发：100 个慢请求把所有带宽占满

## 核心思想

把资源按业务 / 服务**隔离**成多个独立池，每个池有自己的容量上限。一个池被打满不会影响其他池。

**两种隔离方式**：

| 方式 | 适用 | 案例 |
|---|---|---|
| **线程池隔离** | 不同下游服务 | Resilience4j Bulkhead |
| **信号量隔离** | 同一进程内 | Resilience4j SemaphoreBulkhead |
| **连接池隔离** | 数据库 / HTTP 客户端 | HikariCP / OkHttp |
| **进程隔离** | K8s Pod | K8s resource limit |

## Resilience4j 舱壁实战

```java
@Service
public class OrderService {
    // 舱壁 1：支付服务（独立线程池）
    @Bulkhead(name = "payment", type = Bulkhead.Type.THREADPOOL, fallbackMethod = "paymentFallback")
    public PaymentResult pay(PaymentRequest req) {
        return paymentClient.charge(req);
    }

    // 舱壁 2：库存服务（独立线程池）
    @Bulkhead(name = "inventory", type = Bulkhead.Type.THREADPOOL, fallbackMethod = "inventoryFallback")
    public ReserveResult reserve(List<OrderItem> items) {
        return inventoryClient.reserve(items);
    }

    // 舱壁 3：HTTP 客户端（信号量隔离）
    @Bulkhead(name = "http", type = Bulkhead.Type.SEMAPHORE)
    public List<Product> searchProducts(String query) {
        return httpClient.search(query);
    }
}

resilience4j:
  bulkhead:
    instances:
      payment:
        maxThreadPoolSize: 20           # 支付服务最多 20 线程
        maxWaitDuration: 100ms           # 排队最多等 100ms

      inventory:
        maxThreadPoolSize: 15
        maxWaitDuration: 50ms

      http:
        maxConcurrentCalls: 100          # 信号量：最多 100 并发
        maxWaitDuration: 0              # 不等待
```

即使 payment 服务慢导致 20 个线程全占满，inventory 仍有自己的 15 个线程可用。

## Spring Cloud Hystrix 舱壁

```java
@HystrixCommand(
    groupKey = "paymentService",
    threadPoolKey = "paymentPool",
    threadPoolProperties = {
        @HystrixProperty(name = "coreSize", value = "20"),
        @HystrixProperty(name = "maxQueueSize", value = "50")
    },
    fallbackMethod = "paymentFallback"
)
public PaymentResult pay(PaymentRequest req) {
    return paymentClient.charge(req);
}

@HystrixCommand(
    groupKey = "inventoryService",
    threadPoolKey = "inventoryPool",
    threadPoolProperties = {
        @HystrixProperty(name = "coreSize", value = "15")
    }
)
public ReserveResult reserve(List<OrderItem> items) {
    return inventoryClient.reserve(items);
}
```

## 连接池隔离

```typescript
// TypeScript：每个下游服务独立 axios 实例（独立连接池）
const httpClients = {
    payment: axios.create({
        baseURL: 'https://payment.example.com',
        maxSockets: 10,           // 最多 10 个并发连接
        timeout: 5000,
    }),
    inventory: axios.create({
        baseURL: 'https://inventory.example.com',
        maxSockets: 15,
        timeout: 3000,
    }),
    analytics: axios.create({
        baseURL: 'https://analytics.example.com',
        maxSockets: 5,
        timeout: 10000,
    }),
};

// 即使 payment 服务挂掉，inventory 仍有自己的 15 个连接可用
```

## HikariCP 数据库连接池隔离

```yaml
spring:
  datasource:
    primary:
      url: jdbc:mysql://primary-db/mydb
      hikari:
        maximum-pool-size: 20       # 主库连接池
        pool-name: PrimaryPool
    analytics:
      url: jdbc:mysql://analytics-db/mydb
      hikari:
        maximum-pool-size: 5        # 分析库连接池（独立）
        pool-name: AnalyticsPool

// 主库慢查询占满 primary 池，analytics 池不受影响
```

## Kubernetes 进程隔离

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  template:
    spec:
      containers:
        - name: order-service
          image: order-service:1.0
          resources:
            requests:
              cpu: 100m      # 至少 0.1 核
              memory: 128Mi  # 至少 128 MB
            limits:
              cpu: 500m      # 最多 0.5 核
              memory: 512Mi  # 最多 512 MB
```

K8s 是终极舱壁：
- 每个 Pod 有自己的 CPU / 内存上限
- 一个 Pod 内存爆掉 → OOM Kill → 不影响其他 Pod
- Namespace 进一步隔离（资源配额 `ResourceQuota`）

## 实战案例：Hystrix Dashboard

Hystrix Dashboard 可视化各舱壁状态：

```
Thread Pools:
┌────────────┬──────┬───────┬────────┬──────────┐
│ Name       │ Active│ Queue│ PoolSize│ MaxSize  │
├────────────┼──────┼───────┼────────┼──────────┤
│ payment    │   2  │   0   │   18   │   20     │
│ inventory  │   1  │   0   │   14   │   15     │
│ analytics  │   0  │   0   │    3   │    5     │
└────────────┴──────┴───────┴────────┴──────────┘
```

监控每个舱壁的：
- 活跃线程数（接近 maxSize 告警）
- 队列长度（堆积告警）
- 拒绝率（达到上限拒绝）

## 适用边界

✅ **使用场景**：
- 调用多个下游服务（避免相互影响）
- 关键路径与非关键路径隔离
- 不同业务有不同 SLA
- K8s 多租户（避免 noisy neighbor）

❌ **避免场景**：
- 调用单一服务（不需要隔离）
- 资源极有限（隔离会浪费）
- 业务极简（直接调即可）

🔄 **与 Circuit Breaker 区别**：
- **Bulkhead**：资源隔离（防雪崩）
- **Circuit Breaker**：快速失败（防拖延）

💼 **组合使用**：
```yaml
# 同时配置 Bulkhead + Circuit Breaker + Timeout + Retry
# 这四个是分布式 resilience 的「四大金刚」
resilience4j:
  bulkhead:
    instances:
      payment: { maxThreadPoolSize: 20 }
  circuitbreaker:
    instances:
      payment: { failureRateThreshold: 50 }
  timelimiter:
    instances:
      payment: { timeoutDuration: 2s }
  retry:
    instances:
      payment: { maxAttempts: 3 }
```

💡 **最佳实践**：
- 线程池大小 = QPS × 平均响应时间 + buffer
- 监控舱壁活跃度（接近 maxSize 告警）
- 与 Circuit Breaker 组合使用
- 优先 K8s 进程隔离（最彻底）
