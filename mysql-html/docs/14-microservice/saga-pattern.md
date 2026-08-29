---
title: Saga 模式详解
date: 2026-08-15  # date-auto-injected
---

# 🌀 Saga 模式详解

> Saga 是处理**跨服务长事务**的经典模式。在微服务架构下，没有分布式事务也能保证最终一致性。

## 🎯 Saga 是什么？

```
传统分布式事务（2PC/3PC）：
- 同步阻塞
- 性能差
- 不适合微服务

Saga 模式：
- 异步执行
- 高性能
- 最终一致
- 通过补偿事务回滚
```

**核心思想：**
- 把长事务拆成多个**本地子事务**
- 每个子事务都有对应的**补偿操作**
- 如果某个子事务失败，按相反顺序执行补偿

## 📊 两种 Saga 编排方式

### 1. 协调式（Orchestration）

```
┌──────────────────────────────────┐
│  协调器（OrderService）           │
│  - 知道整个流程                   │
│  - 依次调用各服务                 │
│  - 失败时调用补偿                 │
└──────────────────────────────────┘
              │
   ┌──────────┼──────────┐
   ▼          ▼          ▼
┌──────┐  ┌──────┐  ┌──────┐
│ 订单  │  │ 库存  │  │ 账户  │
└──────┘  └──────┘  └──────┘
```

### 2. 编排式（Choreography）⭐⭐⭐

```
无中心协调器
服务之间通过事件通信
┌──────┐  事件   ┌──────┐  事件   ┌──────┐
│ 订单  │ ────→ │ 库存  │ ────→ │ 账户  │
└──────┘  ←──── └──────┘  ←──── └──────┘
       失败事件              完成事件
```

**对比：**

| 维度 | 协调式 | 编排式 |
|---|---|---|
| 业务代码 | 集中在协调器 | 分散在每个服务 |
| 服务耦合 | 高（知道所有服务） | 低（只关心自己） |
| 调试 | 容易（看协调器） | 难（事件流分散） |
| 适合 | 流程复杂 | 微服务（推荐） |

## 🚀 实现 1：协调式 Saga（手写）

```java
@Service
@Slf4j
public class OrderSagaOrchestrator {
    
    @Autowired
    private OrderService orderService;
    
    @Autowired
    private InventoryClient inventoryClient;
    
    @Autowired
    private AccountClient accountClient;
    
    // 整个下单流程
    public void createOrderSaga(OrderDTO dto) {
        // 记录 saga 状态（用于恢复）
        String sagaId = UUID.randomUUID().toString();
        sagaStateStore.save(sagaId, "createOrder", dto);
        
        try {
            // 步骤 1：创建订单
            orderService.create(dto);
            sagaStateStore.markCompleted(sagaId, "createOrder");
            
            // 步骤 2：扣减库存
            inventoryClient.tryDecrease(dto);
            sagaStateStore.markCompleted(sagaId, "decreaseInventory");
            
            // 步骤 3：扣款
            accountClient.tryDebit(dto);
            sagaStateStore.markCompleted(sagaId, "debitAccount");
            
            // ✅ 全部成功
            sagaStateStore.markSagaCompleted(sagaId);
            
        } catch (Exception e) {
            // ❌ 失败：反向补偿
            log.error("Saga failed, compensating: {}", sagaId, e);
            compensate(sagaId, dto, e);
        }
    }
    
    // 补偿（反向执行已完成的步骤）
    private void compensate(String sagaId, OrderDTO dto, Exception cause) {
        if (sagaStateStore.isCompleted(sagaId, "debitAccount")) {
            try {
                accountClient.rollbackDebit(dto);
            } catch (Exception e) {
                log.error("补偿扣款失败，需人工介入", e);
            }
        }
        if (sagaStateStore.isCompleted(sagaId, "decreaseInventory")) {
            try {
                inventoryClient.rollbackDecrease(dto);
            } catch (Exception e) {
                log.error("补偿库存失败，需人工介入", e);
            }
        }
        if (sagaStateStore.isCompleted(sagaId, "createOrder")) {
            try {
                orderService.cancel(dto);
            } catch (Exception e) {
                log.error("补偿订单失败，需人工介入", e);
            }
        }
    }
}
```

**问题：**
- ❌ 业务代码和补偿代码混在一起
- ❌ 每次新增步骤都要改 Saga
- ❌ 测试困难

## 🚀 实现 2：编排式 Saga（推荐）⭐⭐⭐

### 案例：电商下单完整 Saga

```java
// ============ 1. 订单服务：发布事件 ============
@Service
public class OrderService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    public Order createOrder(OrderDTO dto) {
        // 1. 写订单（本地事务）
        orderMapper.insert(dto);
        
        // 2. 发布订单创建事件
        OrderCreatedEvent event = new OrderCreatedEvent(dto);
        event.setOrderNo(dto.getOrderNo());
        kafkaTemplate.send("order.created", JSON.toJSONString(event));
        
        return dto;
    }
    
    // 补偿：监听支付/库存失败，取消订单
    @KafkaListener(topics = {"order.cancel.required"})
    public void onCancelRequired(String message) {
        OrderDTO dto = JSON.parseObject(message, OrderDTO.class);
        orderMapper.cancelByOrderNo(dto.getOrderNo());
        // 发布订单已取消事件
        kafkaTemplate.send("order.cancelled", JSON.toJSONString(dto));
    }
}

// ============ 2. 库存服务：订阅事件 ============
@Service
@Slf4j
public class InventorySaga {
    
    @Autowired
    private InventoryMapper inventoryMapper;
    
    @Autowired
    private KafkaTemplate kafka;
    
    // 监听订单创建 → 扣减库存
    @KafkaListener(topics = "order.created")
    @Transactional
    public void onOrderCreated(String message) {
        OrderCreatedEvent event = JSON.parseObject(message, OrderCreatedEvent.class);
        OrderDTO dto = event.getOrder();
        
        // ✅ 幂等性
        if (inventoryMapper.existsByOrderNo(dto.getOrderNo())) return;
        
        try {
            int affected = inventoryMapper.decreaseAtomic(
                dto.getProductId(), dto.getQuantity()
            );
            if (affected == 0) {
                // 库存不足，发布失败事件
                kafka.send("inventory.failed", JSON.toJSONString(dto));
                return;
            }
            // 成功，发布下一步事件
            kafka.send("account.debit", JSON.toJSONString(dto));
        } catch (Exception e) {
            log.error("库存扣减失败", e);
            kafka.send("inventory.failed", JSON.toJSONString(dto));
        }
    }
    
    // 补偿：监听订单取消，恢复库存
    @KafkaListener(topics = "order.cancelled")
    public void onOrderCancelled(String message) {
        OrderDTO dto = JSON.parseObject(message, OrderDTO.class);
        inventoryMapper.increase(dto.getProductId(), dto.getQuantity());
    }
}

// ============ 3. 账户服务：扣款 ============
@Service
@Slf4j
public class AccountSaga {
    
    @Autowired
    private AccountMapper accountMapper;
    
    @KafkaListener(topics = "account.debit")
    public void onDebit(String message) {
        OrderDTO dto = JSON.parseObject(message, OrderDTO.class);
        
        // 幂等性
        if (accountMapper.existsByOrderNo(dto.getOrderNo())) return;
        
        try {
            accountMapper.debit(dto.getUserId(), dto.getAmount());
            // 成功，发布支付完成
            kafka.send("payment.completed", JSON.toJSONString(dto));
        } catch (Exception e) {
            log.error("扣款失败", e);
            // 发布扣款失败，触发补偿
            kafka.send("payment.failed", JSON.toJSONString(dto));
        }
    }
}

// ============ 4. 支付失败监听器（统一补偿）============
@Component
@Slf4j
public class PaymentFailedListener {
    
    @Autowired
    private KafkaTemplate kafka;
    
    @KafkaListener(topics = "payment.failed")
    public void onPaymentFailed(String message) {
        OrderDTO dto = JSON.parseObject(message, OrderDTO.class);
        log.warn("支付失败，触发 Saga 补偿: {}", dto.getOrderNo());
        
        // 触发整个 Saga 补偿
        kafka.send("order.cancel.required", JSON.toJSONString(dto));
    }
}
```

## 🚀 Seata Saga 模式

### Seata 三种 Saga

```
Seata 提供三种 Saga 模式：
1. State Machine Engine（状态机引擎）
2. Annotation-based（基于注解）
3. Spring Bean 编排
```

### 1. 注解式 Saga

```java
// 引入 Seata Saga
<dependency>
    <groupId>io.seata</groupId>
    <artifactId>seata-spring-boot-starter</artifactId>
    <version>1.7.0</version>
</dependency>
```

```java
@Service
public class OrderSagaService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    @Autowired
    private InventoryClient inventoryClient;
    
    @Autowired
    private AccountClient accountClient;
    
    // 定义 Saga
    @GlobalTransactional(name = "create-order-saga")
    public boolean createOrder(OrderDTO dto) {
        // 1. 创建订单
        orderMapper.insert(dto);
        
        // 2. 远程调用库存
        inventoryClient.decrease(dto);
        
        // 3. 远程调用账户
        accountClient.debit(dto);
        
        return true;
        // ✅ Seata 自动协调：失败自动回滚
    }
}
```

### 2. 状态机 Saga（高级）

```java
// 状态机定义
@Component
public class OrderStateMachine {
    
    public static class States {
        public static final String ORDER_CREATED = "ORDER_CREATED";
        public static final String INVENTORY_DECREASED = "INVENTORY_DECREASED";
        public static final String ACCOUNT_DEBITED = "ACCOUNT_DEBITED";
        public static final String ORDER_COMPLETED = "ORDER_COMPLETED";
        public static final String ORDER_FAILED = "ORDER_FAILED";
    }
    
    // 状态机定义（DSL）
    @Bean
    public StateMachine<OrderState, OrderEvent> orderStateMachine() {
        StateMachineBuilder<OrderState, OrderEvent> builder = 
            StateMachineBuilder.create();
        
        // 状态机配置
        return builder.configure()
            .withConfiguration()
                .autoStartup(true)
                .listener(new OrderStateListener())
                .and()
            .withStates()
                .initial(States.ORDER_CREATED)
                .state(States.INVENTORY_DECREASED)
                .state(States.ACCOUNT_DEBITED)
                .end(States.ORDER_COMPLETED)
                .end(States.ORDER_FAILED)
                .and()
            // 转换
            .withTransitions()
                .from(States.ORDER_CREATED).to(States.INVENTORY_DECREASED)
                .on(OrderEvent.INVENTORY_OK)
                .from(States.INVENTORY_DECREASED).to(States.ACCOUNT_DEBITED)
                .on(OrderEvent.ACCOUNT_OK)
                .from(States.ACCOUNT_DEBITED).to(States.ORDER_COMPLETED)
                .on(OrderEvent.PAYMENT_OK)
                .from(States.ORDER_CREATED).to(States.ORDER_FAILED)
                .on(OrderEvent.INVENTORY_FAIL)
                .and()
            .build();
    }
}
```

## 📊 实战：Saga 选型

| 业务场景 | 推荐方案 | 理由 |
|---|---|---|
| 简单流程（3-4 步） | Seata Saga AT | 零侵入 |
| 复杂流程（5+ 步） | 编排式 Saga（事件驱动） | 易扩展 |
| 需要可视化流程 | 状态机 Saga | 易调试 |
| 不想引入中间件 | 本地消息表 | 简单 |

## 🛠️ Saga 模式实战注意事项

### 1. 幂等性（必须！）

```java
// ✅ 每个消费者都要幂等
@KafkaListener(topics = "inventory.decrease")
public void onMessage(String message) {
    OrderDTO dto = JSON.parseObject(message, OrderDTO.class);
    
    // 业务单号去重
    if (inventoryMapper.existsByOrderNo(dto.getOrderNo())) {
        return;
    }
    
    // 业务处理
    inventoryMapper.decrease(...);
}
```

### 2. 补偿顺序

```
正向：订单创建 → 库存扣减 → 账户扣款
补偿：账户退款 → 库存恢复 → 订单取消

⚠️ 补偿顺序：反着补偿（先补偿后面的）
```

### 3. 幂等补偿

```java
// 补偿也要幂等
public void rollbackDebit(OrderDTO dto) {
    // 防止重复补偿
    if (accountMapper.isRefunded(dto.getOrderNo())) {
        return;
    }
    accountMapper.refund(dto.getUserId(), dto.getAmount());
}
```

### 4. 失败处理（人工介入）

```java
// 多次重试失败 → 人工介入
public void compensate(String sagaId, OrderDTO dto) {
    int retry = 0;
    while (retry < 3) {
        try {
            accountClient.rollbackDebit(dto);
            return;
        } catch (Exception e) {
            retry++;
            Thread.sleep(1000 * retry);
        }
    }
    // 多次失败，发告警
    alertService.send("Saga 补偿失败，需人工介入", sagaId);
    // 写入人工处理表
    manualHandleService.save(sagaId, dto, e);
}
```

## 🆚 Saga vs Seata AT

| 维度 | Saga | Seata AT |
|---|---|---|
| 性能 | 高（异步） | 中（同步） |
| 一致性 | 最终 | 强 |
| 业务侵入 | 需写补偿 | 零侵入 |
| 调试 | 较难 | 易 |
| 适用 | 长流程 | 短流程 |
| 风险 | 补偿失败需人工 | 锁等待 |

## 🎯 总结

**Saga 模式核心：**
- ✅ 长事务拆成多个**本地子事务**
- ✅ 每个子事务有**补偿操作**
- ✅ 失败时**反序补偿**
- ✅ 配合**幂等性**保证安全
- ✅ **最终一致性**（不是强一致）

**两种编排方式：**
- ✅ **协调式**：中心化（适合简单流程）
- ✅ **编排式**：去中心化（**推荐**，微服务友好）

**实战选型：**
- ✅ 简单流程：Seata AT
- ✅ 复杂流程：编排式 Saga
- ✅ 状态机：可视化要求高时
- ✅ 不引入中间件：本地消息表

**关键原则：**
- ✅ 幂等性（必做）
- ✅ 补偿顺序（反序）
- ✅ 失败重试（指数退避）
- ✅ 人工介入（多次失败后）
- ✅ 监控告警

**下一步：** [☕ 微服务数据库模式](/14-microservice/db-pattern) — 每个服务一个数据库的实践

## 📚 跨站参考：📊 监控告警

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **observability** 站（[https://java-px.bot.cd/observability/](https://java-px.bot.cd/observability/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [mysql](https://java-px.bot.cd/mysql/) / [video](https://java-px.bot.cd/video/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。
