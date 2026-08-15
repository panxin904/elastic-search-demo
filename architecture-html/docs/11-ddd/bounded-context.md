---
title: 限界上下文
---
# 限界上下文（Bounded Context）

## 1. 为什么需要限界上下文

```
单体 / 大服务：
  - 一个模型（User）满足所有场景
  - 矛盾属性堆在一个类（买家 / 卖家 / 客服 / 风控）
  - 改了 User → 影响所有

限界上下文：
  - 同一概念在不同上下文有不同含义
  - 每个上下文一个模型
  - 上下文间通过显式边界通信
```

## 2. 经典例子：User 的多面性

| 上下文 | User 含义 | 关键属性 |
|--------|----------|---------|
| 销售 | 客户 | 邮箱 / 偏好 / 购买力 |
| 客服 | 工单创建者 | 联系方式 / 历史工单 |
| 风控 | 风控对象 | 设备指纹 / 风险评分 |
| 认证 | 凭据主体 | 账号 / 密码 / Token |

**错误**：把 4 个 User 合在一个表 / 一个实体 → 改一处影响所有。
**正确**：4 个 User（4 个限界上下文，每个有自己模型），通过上下文映射通信。

## 3. 上下文映射（Context Map）

| 关系 | 描述 | 例子 |
|------|------|------|
| **共享内核** | 两上下文共享部分代码 | 通用类型（Money, Address） |
| **客户-供应商** | 上游提供 API，下游消费 | 订单服务 → 支付服务 |
| **发布-订阅** | 异步事件 | 订单事件 → 库存订阅 |
| **防腐层（ACL）** | 翻译老系统 API | 新系统 ↔ 遗留系统 |
| **开放主机** | 提供公开 API | 支付网关的 API |
| **独立** | 无关系 | 互不依赖的两个业务 |
| **共享内核** | 共用一部分模型 | 共用枚举（如 OrderStatus） |

## 4. 限界上下文的边界识别

### 事件风暴（Event Storming）

```
1. 召集业务 + 技术 + 测试
2. 黄色便签：领域事件（"OrderPlaced"）
3. 橙色便签：触发事件的命令（"PlaceOrder"）
4. 红色便签：外部系统（"支付系统"）
5. 蓝色便签：聚合（"Order"）
6. 粉红色便签：外部事件
7. 找出聚合边界 = 限界上下文
```

详见 [事件风暴](/11-ddd/event-storming)。

## 5. 限界上下文的代码映射

```
Java 工程结构：
myapp/
├── order-context/           ← Order Bounded Context
│   ├── domain/              ← Entity, ValueObject, DomainEvent
│   │   ├── Order.java
│   │   ├── OrderId.java
│   │   ├── Money.java
│   │   └── event/
│   │       └── OrderPlacedEvent.java
│   ├── application/         ← UseCase, Command, Query
│   │   └── PlaceOrderService.java
│   ├── infrastructure/      ← Repository, Adapter
│   │   ├── OrderRepository.java
│   │   └── OrderEntity.java
│   └── interfaces/          ← DTO, REST/Event adapter
│       └── OrderController.java
├── inventory-context/      ← 独立 Bounded Context
└── payment-context/        ← 独立 Bounded Context
```

## 6. 跨上下文通信

### 6.1 同步调用（REST / gRPC）

```java
// Order Context 调用 Payment Context
@Service
public class PlaceOrderService {
  @Autowired PaymentClient paymentClient;  // Feign / gRPC stub

  public void placeOrder(OrderDTO dto) {
    orderRepo.create(dto);
    paymentClient.charge(dto.userId, dto.amount);  // 同步远程调用
  }
}
```

**问题**：Payment 挂了 → Order 也挂。**用 Saga / 事件** 替代。

### 6.2 异步事件

```java
// Order Context 发布事件
@Service
public class PlaceOrderService {
  @Autowired DomainEventPublisher events;

  public void placeOrder(OrderDTO dto) {
    orderRepo.create(dto);
    events.publish(new OrderPlacedEvent(dto.orderId, dto.amount));
  }
}

// Payment Context 订阅事件
@EventListener("OrderPlaced")
public void onOrderPlaced(OrderPlacedEvent e) {
  paymentService.charge(e.userId, e.amount);
}
```

**优**：松耦合，Payment 挂了 Order 不挂。

## 7. 上下文边界 vs 服务边界

```
DDD 限界上下文 ≈ 微服务
  一个上下文 = 一个微服务
  （团队规模、复杂度足够时）

但不必 1:1
  - 多个上下文 = 1 微服务（monolith 微服务）
  - 1 上下文 = 多微服务（复杂业务拆）
```

**原则**：团队边界 = 服务边界（康威定律）。

## 8. 实战选型

| 场景 | 策略 |
|------|------|
| 全新项目 | 1 上下文 = 1 微服务 |
| 老单体 | 事件风暴 → 识别上下文 → 绞杀者迁移 |
| 多团队 | 按 Bounded Context 拆 |
| 性能敏感 | 同步调用（按 SLA） |
| 解耦优先 | 异步事件 |

## 9. 限界上下文落地 checklist

- [ ] 业务语言清晰（领域专家能讲）
- [ ] 每个上下文有清晰的接口（API 或事件）
- [ ] 上下文间不共享数据库
- [ ] 团队结构和上下文对齐
- [ ] 事件命名是业务语言（OrderPlaced，不是 Event1）

## 10. 实战：事件风暴

详见 [事件风暴](/11-ddd/event-storming)。

## 🔗 下一步
- [聚合 / 实体 / 值对象](/11-ddd/basics)
- [事件风暴](/11-ddd/event-storming)
- [服务拆分原则](/06-microservice/split)
