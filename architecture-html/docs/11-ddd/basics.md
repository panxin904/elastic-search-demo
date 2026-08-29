---
title: DDD 聚合 / 实体 / 值对象
date: 2026-08-15  # date-auto-injected
---
# DDD 核心概念

## 1. 为什么需要 DDD

```
传统开发：
  - 看需求 → 建表 → CRUD
  - 业务复杂时表 join 爆炸
  - 业务逻辑散落在 Service / Util
  - 改了字段 → 改 N 个文件

DDD（领域驱动设计）：
  - 围绕业务概念建模
  - 业务逻辑封装在领域对象
  - 边界清晰（限界上下文）
  - 战略 + 战术两层
```

## 2. 战略设计：限界上下文（Bounded Context）

**一个业务领域 = 多个限界上下文**。每个上下文有：
- 自己的通用语言
- 自己的领域模型
- 自己的团队
- 自己的代码库

```
电商领域
├─ 商品上下文 (Catalog Context)
│   ├─ Product, SKU, Category
│   └─ 服务：商品服务、搜索服务
├─ 订单上下文 (Order Context)
│   ├─ Order, OrderItem, Payment
│   └─ 服务：订单服务、支付服务
├─ 库存上下文 (Inventory Context)
│   ├─ Inventory, Stock, Warehouse
│   └─ 服务：库存服务
└─ 用户上下文 (Identity Context)
    ├─ User, Account
    └─ 服务：用户服务、认证服务
```

**关键**：**跨上下文通过 API / 事件**，**不共享数据库**。

## 3. 战术设计：三大核心概念

### 实体（Entity）

有唯一标识的对象，**生命周期可变状态**。

```java
@Entity
public class Order {
  @Id private OrderId id;        // 唯一标识
  private Money totalAmount;
  private List<OrderItem> items;
  private OrderStatus status;
  private CustomerId customerId;

  // 业务行为（不是 setter）
  public void pay(Money amount, PaymentId paymentId) {
    if (this.status != OrderStatus.PENDING) throw new IllegalStateException();
    this.status = OrderStatus.PAID;
    this.paidAt = Instant.now();
    registerEvent(new OrderPaidEvent(id, paymentId));
  }
}
```

**关键**：业务逻辑在实体上（不是贫血模型）。Getter 少，setter 几乎不用。

### 值对象（Value Object）

无唯一标识的对象，**只描述特征**。不可变。

```java
public record Money(BigDecimal amount, Currency currency) {
  public Money {
    if (amount == null || amount.signum() < 0) throw new IllegalArgumentException();
  }
  public Money add(Money other) {
    if (this.currency != other.currency) throw new IllegalArgumentException();
    return new Money(this.amount.add(other.amount), this.currency);
  }
}

Address addr1 = new Address("北京", "海淀", "100080");
Address addr2 = new Address("北京", "海淀", "100080");
addr1.equals(addr2);  // true（值相等）
```

**关键**：值对象应该**不可变**（record / final 字段 / 无 setter）。

### 聚合（Aggregate）

实体 + 值对象的**一致性边界**。一个聚合 = 一个根实体 + 若干从属对象。

```
Order 聚合
  ├─ Order (根实体，唯一 ID)
  ├─ OrderItem[] (从属实体，唯一于 Order)
  └─ ShippingAddress (值对象)
```

**不变量**：一个事务只改一个聚合。跨聚合 = 分布式事务 / Saga。

```java
// 错误的：跨聚合写
orderRepo.save(order);
inventoryRepo.save(inventory);  // 不在同一个事务

// 正确的：通过聚合根
order.confirmPayment();  // 内部触发 payment 事件
eventBus.publish(new OrderPaidEvent(order.id));
// 其他聚合订阅后处理
```

## 4. 聚合根 vs 实体

| | 聚合根 | 实体 |
|--|--------|------|
| 全局唯一标识 | ✅ 必须 | 可选 |
| 业务入口 | ✅ 外部只能调根 | ❌ |
| 维护不变量 | ✅ 一致性边界 | ❌ |
| 持久化 | 一个根一条记录 | 聚合根下的从属实体 |

## 5. 限界上下文的关系

```
下单（Order Context）       →  Payment Context
    发布 OrderCreated 事件      订阅事件
        → 支付处理
        → 支付完成事件
        → 回到 Order 更新状态
```

**关系类型**：
- 共享内核（Shared Kernel）：两上下文共享一部分代码
- 客户/供应商（Customer/Supplier）：上游提供 API
- 发布/订阅（Pub-Sub）：事件驱动
- 防腐层（Anti-Corruption Layer, ACL）：翻译老系统
- 独立（Separate Ways）：互不依赖

## 6. 领域服务（Domain Service）

不属于任何实体的业务逻辑：

```java
@Service
public class TransferService {
  public void transfer(AccountId from, AccountId to, Money amount) {
    // 跨聚合的逻辑
  }
}
```

## 7. 实体 vs 值对象

| | 实体 | 值对象 |
|--|------|----------|
| 唯一标识 | ✅ 必须 | ❌ |
| 可变 | ✅（带业务规则） | ❌ 不可变 |
| 持久化 | ✅ 一条记录 | ❌ 嵌入式 |
| 例子 | Order, User | Money, Address |
| 判等 | ID 相等 | 值相等 |

## 8. 实战：DDD 在 Spring

```java
// 实体
@Entity @Table(name = "orders")
public class Order {
  @EmbeddedId private OrderId id;
  private OrderStatus status;
  // ...
  public void cancel(String reason) {
    if (status == OrderStatus.SHIPPED) throw new IllegalStateException("已发货");
    this.status = OrderStatus.CANCELLED;
    this.cancelledAt = Instant.now();
    this.cancelReason = reason;
    // 发领域事件
    DomainEventPublisher.publish(new OrderCancelled(this.id, reason));
  }
}

// 值对象
public record OrderId(String value) {
  public OrderId { if (value == null || value.isBlank()) throw new IllegalArgumentException(); }
}
```

## 9. DDD 误区

- **贫血模型**：实体只有 getter/setter，没业务逻辑 → DDD 没入门
- **过大聚合**：聚合根管太多东西 → 重新拆分
- **直接 CRUD**：忽视聚合根 → 业务一致性破坏
- **跨库 join**：把上下文糅在一起 → 失去 DDD 价值

## 🔗 下一步
- [限界上下文](/11-ddd/bounded-context)
- [事件风暴](/11-ddd/event-storming)
- [服务拆分原则](/06-microservice/split)
