---
title: 消息幂等性
---

# 🔁 消息幂等性

> **消息幂等性**是 Kafka 生产环境的核心问题。即使有 Producer 幂等性和事务，业务端仍需**幂等消费**。

## 🎯 什么是消息幂等性？

```
幂等性 = 多次重复执行同一个操作，结果与执行一次相同

Kafka 场景：
  - 消息可能被重复消费（At Least Once）
  - 必须保证业务只处理一次
```

### 为什么会重复消费？

```
Producer 端：
  - 重试导致重复（即使有幂等性也有限制）

Consumer 端：
  - At Least Once 提交后崩溃 → 重新消费
  - Rebalance 时未提交 Offset → 重新消费

业务端：
  - 多次发送相同业务消息
  - 网络重试
```

## 🔧 幂等性方案

### 方案 1：数据库唯一索引

```java
// 最简单、最可靠的方案

@Entity
@Table(name = "orders")
public class Order {
    @Id
    private String orderId;  // 主键（消息中的 orderId）
    private BigDecimal amount;
    private String status;
    // ...
}

@Service
public class OrderProcessor {
    
    @Transactional
    public void process(OrderEvent event) {
        try {
            // 保存订单（主键冲突时抛异常）
            Order order = new Order();
            order.setOrderId(event.getOrderId());
            order.setAmount(event.getAmount());
            orderRepository.save(order);
        } catch (DuplicateKeyException e) {
            // 主键冲突，说明已处理过
            log.info("Order {} already processed, skip", event.getOrderId());
        }
    }
}
```

**优点**：
- ✅ 简单可靠
- ✅ 数据库保证
- ✅ 性能高

**缺点**：
- ❌ 仅适合有唯一标识的场景
- ❌ 业务表耦合

### 方案 2：Redis SETNX

```java
@Service
public class IdempotentProcessor {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    public boolean process(OrderEvent event) {
        String key = "order:processed:" + event.getOrderId();
        
        // SETNX：只在不存在时设置（原子操作）
        Boolean firstTime = redisTemplate.opsForValue()
            .setIfAbsent(key, "1", 24, TimeUnit.HOURS);
        
        if (Boolean.TRUE.equals(firstTime)) {
            // 第一次处理
            try {
                processOrder(event);
                return true;
            } catch (Exception e) {
                // 处理失败，删除 key 让下次重试
                redisTemplate.delete(key);
                throw e;
            }
        } else {
            log.info("Order {} already processed", event.getOrderId());
            return false;  // 已处理过
        }
    }
}
```

**优点**：
- ✅ 性能高（Redis 内存操作）
- ✅ 跨数据库
- ✅ TTL 自动过期

**缺点**：
- ❌ 依赖 Redis
- ❌ Redis 故障时降级

### 方案 3：数据库唯一约束表

```java
// 独立的幂等性表

@Entity
@Table(name = "processed_messages")
public class ProcessedMessage {
    @Id
    private String messageId;  // 唯一标识
    @Column(nullable = false)
    private LocalDateTime processedAt;
}

@Service
@Transactional
public class IdempotentProcessor {
    
    @Autowired
    private ProcessedMessageRepository repository;
    
    public void process(OrderEvent event) {
        // 1. 检查 + 插入幂等表
        if (!repository.existsById(event.getMessageId())) {
            try {
                repository.save(new ProcessedMessage(
                    event.getMessageId(), 
                    LocalDateTime.now()
                ));
            } catch (DuplicateKeyException e) {
                // 重复消息，跳过
                log.info("Duplicate message: {}", event.getMessageId());
                return;
            }
            
            // 2. 处理业务
            orderService.process(event);
        }
    }
}
```

**优点**：
- ✅ 业务与幂等解耦
- ✅ 通用方案

**缺点**：
- ❌ 多一次数据库写
- ❌ 需要清理历史数据（按业务保留）

### 方案 4：乐观锁（版本号）

```java
@Entity
public class Inventory {
    @Id
    private Long productId;
    private Integer stock;
    @Version
    private Long version;  // 乐观锁
}

@Service
public class InventoryProcessor {
    
    @Transactional
    public void deductStock(OrderEvent event) {
        Inventory inventory = inventoryRepository.findById(event.getProductId());
        
        // 乐观锁：version 不匹配则更新失败
        inventory.setStock(inventory.getStock() - event.getQuantity());
        try {
            inventoryRepository.save(inventory);
        } catch (OptimisticLockingFailureException e) {
            // 乐观锁冲突，可能已被其他消息处理
            log.info("Inventory already deducted: {}", event.getProductId());
        }
    }
}
```

**适用场景**：
- 状态更新（如扣库存）
- 版本号控制

### 方案 5：业务状态机

```java
public enum OrderStatus {
    CREATED, PAID, SHIPPED, COMPLETED, CANCELLED
}

@Service
public class OrderProcessor {
    
    public void processStatusChange(OrderEvent event) {
        Order order = orderRepository.findById(event.getOrderId());
        
        // 状态机校验：只能顺序流转
        if (canTransition(order.getStatus(), event.getNewStatus())) {
            order.setStatus(event.getNewStatus());
            orderRepository.save(order);
        } else {
            log.info("Invalid status transition: {} -> {}", 
                order.getStatus(), event.getNewStatus());
        }
    }
    
    private boolean canTransition(OrderStatus from, OrderStatus to) {
        Map<OrderStatus, Set<OrderStatus>> transitions = Map.of(
            CREATED, Set.of(PAID, CANCELLED),
            PAID, Set.of(SHIPPED, REFUNDED),
            SHIPPED, Set.of(COMPLETED)
        );
        return transitions.getOrDefault(from, Set.of()).contains(to);
    }
}
```

**适用场景**：
- 状态变更（如订单状态）
- 业务流引擎

## 🔧 实战：完整的幂等消费

```java
@Service
public class IdempotentOrderProcessor {
    
    @Autowired
    private RedisTemplate<String, String> redisTemplate;
    @Autowired
    private OrderRepository orderRepository;
    @Autowired
    private OutboxRepository outboxRepository;
    
    // 多重幂等保障
    public void process(OrderEvent event) {
        String key = "order:processed:" + event.getOrderId();
        
        // 1. Redis SETNX（性能优先）
        Boolean firstTime = redisTemplate.opsForValue()
            .setIfAbsent(key, "1", 24, TimeUnit.HOURS);
        
        if (!Boolean.TRUE.equals(firstTime)) {
            log.info("Duplicate order (Redis): {}", event.getOrderId());
            return;
        }
        
        try {
            // 2. 处理业务（数据库唯一约束兜底）
            processOrderWithDBLock(event);
            
        } catch (DuplicateKeyException e) {
            // 兜底：数据库主键冲突
            log.info("Duplicate order (DB): {}", event.getOrderId());
        } catch (Exception e) {
            // 处理失败，删除 Redis key 让下次重试
            redisTemplate.delete(key);
            throw e;
        }
    }
    
    @Transactional
    public void processOrderWithDBLock(OrderEvent event) {
        // 唯一索引保证幂等
        Order order = new Order();
        order.setOrderId(event.getOrderId());
        order.setUserId(event.getUserId());
        order.setAmount(event.getAmount());
        order.setStatus("CREATED");
        orderRepository.save(order);  // 主键冲突会抛异常
        
        // 写入 Outbox
        outboxRepository.save(new OutboxEvent(...));
    }
}
```

## 🔧 选择幂等方案

### 决策树

```
是否有唯一业务标识？
  ├─ 是 → 数据库唯一索引（推荐）
  └─ 否 ↓

是否有状态机？
  ├─ 是 → 业务状态机
  └─ 否 ↓

是否可以增加幂等字段？
  ├─ 是 → 数据库唯一约束表
  └─ 否 → Redis SETNX
```

### 方案对比

| 方案 | 可靠性 | 性能 | 复杂度 | 适用场景 |
|------|--------|------|--------|---------|
| 数据库唯一索引 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 低 | 有唯一 ID 的业务 |
| Redis SETNX | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 中 | 高并发、跨业务 |
| 数据库唯一约束表 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 中 | 通用方案 |
| 乐观锁 | ⭐⭐⭐⭐ | ⭐⭐⭐ | 中 | 状态更新 |
| 业务状态机 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 中 | 状态变更 |

## 🔧 实战：通用幂等框架

```java
// 通用幂等注解
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface Idempotent {
    String key();        // 幂等 Key（SpEL）
    String prefix() default "idem";  // Key 前缀
    long expireSeconds() default 86400;  // 过期时间
}

// AOP 切面
@Aspect
@Component
public class IdempotentAspect {
    
    @Autowired
    private RedisTemplate<String, String> redisTemplate;
    
    @Around("@annotation(idempotent)")
    public Object around(ProceedingJoinPoint pjp, Idempotent idempotent) throws Throwable {
        // 1. 生成 Key
        String key = idempotent.prefix() + ":" + 
            SpEL.parse(idempotent.key(), pjp);
        
        // 2. SETNX
        Boolean firstTime = redisTemplate.opsForValue()
            .setIfAbsent(key, "1", idempotent.expireSeconds(), TimeUnit.SECONDS);
        
        if (!Boolean.TRUE.equals(firstTime)) {
            log.info("Duplicate request: {}", key);
            return null;  // 已处理
        }
        
        try {
            return pjp.proceed();
        } catch (Exception e) {
            redisTemplate.delete(key);  // 处理失败允许重试
            throw e;
        }
    }
}

// 使用
@Service
public class OrderService {
    
    @Idempotent(key = "'order:' + #event.orderId", expireSeconds = 3600)
    public Order createOrder(OrderEvent event) {
        // 业务处理
        // ...
    }
}
```

## 🔧 分布式幂等

### 挑战

```
单 JVM 幂等：
  - Redis SETNX 即可

多 JVM 幂等：
  - 需要分布式锁（Redis / ZK）
  - 或数据库唯一约束（强一致）
```

### 实战：分布式幂等

```java
public class DistributedIdempotent {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    public boolean tryProcess(String businessId, long timeout, TimeUnit unit) {
        String key = "distributed-idem:" + businessId;
        
        // SETNX + EX（原子）
        Boolean success = redisTemplate.opsForValue()
            .setIfAbsent(key, "1", timeout, unit);
        
        return Boolean.TRUE.equals(success);
    }
    
    public void processOrder(OrderEvent event) {
        if (tryProcess(event.getOrderId(), 30, TimeUnit.SECONDS)) {
            try {
                // 业务处理
                orderService.process(event);
            } catch (Exception e) {
                // 处理失败释放锁
                redisTemplate.delete("distributed-idem:" + event.getOrderId());
                throw e;
            }
        } else {
            log.info("Order already processed: {}", event.getOrderId());
        }
    }
}
```

## ⚠️ 常见问题

### 问题 1：处理失败但 Redis 锁未释放

```
解决：
  1. 业务代码用 try-catch 释放
  2. Redis 设置合理 TTL（兜底）
  3. 监控 Redis 异常 key
```

### 问题 2：Redis 故障导致无法去重

```
解决：
  1. Redis 故障降级（直接处理）
  2. 数据库兜底（唯一约束）
```

### 问题 3：幂等字段选择不当

```
场景：用 userId 作幂等字段，但同用户多个订单
解决：选择真正唯一的业务字段（如 orderId、messageId）
```

## 🎯 总结

**消息幂等性核心要点**：
- ✅ Kafka 至少一次语义需要业务幂等
- ✅ 数据库唯一索引最可靠
- ✅ Redis SETNX 性能最佳
- ✅ 多重幂等保障（Redis + DB）
- ✅ 通用幂等框架（AOP）
- ⚠️ 处理失败需释放 Redis key
- ⚠️ Redis 故障需降级方案

**下一步：** [📊 顺序消费](/08-enterprise/order-consume) — 顺序保证实战
