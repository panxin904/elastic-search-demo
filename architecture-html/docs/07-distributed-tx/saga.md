---
title: Saga 模式
---
# Saga 分布式事务


![Saga 时序图 — 正向事务 + 补偿回滚](/saga-sequence.svg)

## 1. 核心思想

把分布式事务拆成**多个本地事务**，每个本地事务有对应的**补偿操作**。

```
转账 = Try A(扣款) + Try B(加款)
        ↑
        失败？B 补偿(回退) → A 补偿(回退)
```

## 2. 两种 Saga

### 编排式（Orchestration）

中央协调者（Orchestrator）管理事务流程。

```
Orchestrator
   ↓ 调用
Service A: try → 成功？
              ↓ 失败
            调 A.compensate
            ↓
            调 B.compensate

Service B: try → 成功？
              ↓ 失败
            调 A.compensate
            调 B.compensate
```

**代表**：Apache ServiceComb Saga、Seata Saga 模式、Cadence（Uber）。

### 编舞式（Choreography）

无中心协调者，服务间通过**事件**联动。

```
A 服务：执行本地事务 → 发 OrderCreated 事件
B 服务：收到事件 → 执行本地事务 → 发 OrderCompleted 事件
任一失败：发 OrderCancelled 事件 → 各自补偿
```

**代表**：Apache Eventuate、Saga Pattern（经典论文）。

## 3. 实战：订单 Saga

```
下单 → 库存冻结 → 支付 → 物流预约
        ↓
   任一失败 → 逆向补偿：
        支付撤销 → 库存解冻 → 订单取消
```

```java
// Orchestrator: OrderSaga
public class OrderSaga {
  @Autowired OrderService orderSvc;
  @Autowired InventoryService invSvc;
  @Autowired PaymentService paySvc;

  public void placeOrder(OrderDTO dto) {
    try {
      orderSvc.create(dto);              // 本地事务
      invSvc.freeze(dto.getSku(), dto.getQty());
      paySvc.charge(dto.getUserId(), dto.getAmount());
    } catch (Exception e) {
      // 补偿
      paySvc.refund(dto.getUserId());
      invSvc.unfreeze(dto.getSku(), dto.getQty());
      orderSvc.cancel(dto);
    }
  }
}
```

## 4. Saga vs 2PC / TCC

| | 2PC | TCC | Saga |
|--|-----|-----|------|
| 一致性 | 强 | 强 | 最终 |
| 锁 | 全程 | Try 阶段 | 无 |
| 协调 | 协调者 | Try 接口 | 业务 / 事件 |
| 适用 | 单机多库 | 短事务 | **长事务 / 多服务** |
| 实现难度 | 低 | 高 | 中 |
| 性能 | 差 | 中 | 好 |

**Sagas = BASE 理论的工程实现**。

## 5. Saga 关键挑战

### 补偿设计

每个正向操作必须有对应补偿（要幂等）。

### 隔离性

Saga 没有全局隔离：
- T1 看见 T2 部分提交（中间状态）
- 例：T1 看到库存已扣，但订单还没创建

**解决**：应用层处理（如"订单处理中"中间状态）。

### 长时间运行

Saga 可能跑数小时 / 数天 → 状态需要持久化（DB / 事件存储）。

## 6. 实战：Seata Saga 模式

```xml
<dependency>
  <groupId>io.seata</groupId>
  <artifactId>seata-spring-boot-starter</artifactId>
</dependency>
```

```java
@GlobalTransactional(name = "placeOrder", rollbackFor = Exception.class)
public void placeOrder(OrderDTO dto) {
  orderRepo.create(dto);
  inventoryClient.freeze(dto.getSku(), dto.getQty());
  paymentClient.charge(dto.getUserId(), dto.getAmount());
}
```

Seata 自动管理：try / confirm / cancel + 反向补偿。

## 7. 实战：事件驱动 Saga

```java
// 库存服务
@KafkaListener(topics = "OrderCreated")
@Transactional
public void onOrderCreated(OrderCreatedEvent e) {
  if (localDb.freezeStock(e.sku, e.qty) == 0) {
    throw new RuntimeException("库存不足");
  }
  kafkaTemplate.send("InventoryFrozen", e);
}

// 支付服务
@KafkaListener(topics = "InventoryFrozen")
public void onInventoryFrozen(InventoryFrozenEvent e) {
  paymentClient.charge(e.userId, e.amount);
  kafkaTemplate.send("PaymentCompleted", e);
}
```

**失败**：发 PaymentFailed 事件 → 库存补偿。

## 8. 选型

| 场景 | 选 |
|------|-----|
| 短事务（秒级） | TCC |
| 长事务（分钟/小时）| Saga |
| 高并发 | Saga 异步 + 幂等 |
| 强一致 | TCC（牺牲性能） |
| 弱一致 | Saga / 本地消息表 |

## 🔗 下一步
- [2PC / 3PC](/07-distributed-tx/2pc)
- [TCC 模式](/07-distributed-tx/tcc)
- [本地消息表](/07-distributed-tx/local-table)
- [幂等性设计](/03-ha-theory/idempotency)
