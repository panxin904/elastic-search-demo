---
title: 事件风暴
date: 2026-08-15  # date-auto-injected
---
# 事件风暴（Event Storming）

## 1. 是什么

Alberto Brandolini 2013 提出，**DDD 战术设计**的核心实践。

**核心**：通过**领域事件**为线索，把业务完整地"铺"在工作墙上。

**为什么有效**：
- 技术 + 业务 + 测试 + 设计师同处一室
- 不画 UML 类图，**只贴便签**（事件 + 命令 + 聚合 + 边界）
- 一张图能装下整个业务

## 2. 颜色约定

```
🟡 黄色：领域事件（Domain Event）
   OrderPlaced, PaymentCompleted, InventoryReduced
   用过去时：已经发生

🟠 橙色：命令 / 操作（Command）
   PlaceOrder, CancelOrder
   触发事件

🔴 红色：外部系统（External System）
   PaymentGateway, EmailService, SMSProvider
   边界

🔵 蓝色：聚合（Aggregate）
   Order, Customer, Inventory
   边界 / 一致性单元

🟢 浅绿色：读模型（Read Model / Projection）
   OrderListView, OrderReport
   事件触发更新

🟣 紫色：策略（Policy）
   "VIP 客户可优先发货"
   写在命令旁的便签

🩷 粉色：外部系统触发的事件
   TimeElapsed, SystemOutage
```

## 3. 实战流程（4-6 小时）

### Step 1: 领域事件（90 分钟）

```
材料：黄色便签 + 马克笔
全员轮流贴：
  - "我做了什么" → 过去时 → 黄色便签
  - 例：用户下单了（OrderPlaced）
  - 例：订单已支付（OrderPaid）
  - 例：库存减少了（InventoryReduced）
```

事件贴在时间轴上（从左到右）。

### Step 2: 命令（60 分钟）

```
材料：橙色便签
对每个事件问 "是什么触发了它？"
  OrderPlaced ← 用户点了"提交订单"（PlaceOrder，橙色便签）
  OrderPaid ← 用户完成支付（CompletePayment）
```

**关键**：每个命令贴在触发的事件**之前**。

### Step 3: 聚合（60 分钟）

```
材料：蓝色便签
对每个事件 / 命令问 "谁负责？"
  OrderPlaced → Order 聚合（蓝色便签）
  PaymentCompleted → Payment 聚合
  InventoryReduced → Inventory 聚合
```

**关键**：同一聚合的多个事件 / 命令画在一个椭圆里。

### Step 4: 限界上下文（60 分钟）

```
材料：虚线 / 大方框
  - 把相邻的聚合画成同一个限界上下文
  - 上下文间画依赖关系
  - 找 ACL（防腐层）
  - 标出"共享内核"
```

**结果**：每个虚线方框 = 一个限界上下文 = 一个微服务。

### Step 5: 补充（30 分钟）

- 红色便签：外部系统
- 紫色便签：业务规则（策略）
- 粉色便签：系统自动触发
- 🟢 浅绿：读模型（CQRS）

## 4. 实战例子：电商下单

```
[PlaceOrder (橙)] ─→ [OrderPlaced (黄)] ─→ [InventoryFrozen (黄)]
                                              ↓
[CompletePayment (橙)] ─→ [PaymentCompleted (黄)]
                                              ↓
                                       [OrderConfirmed (黄)]
                                              ↓
[ScheduleDelivery (橙)] ─→ [DeliveryScheduled (黄)]
```

椭圆（聚合）：Order / Payment / Inventory / Delivery
虚线（限界上下文）：OrderContext / PaymentContext / InventoryContext / LogisticsContext

## 5. 输出物

**一张图** + **一个清单**：

```
# 限界上下文
- OrderContext (核心域)
  - 聚合: Order, OrderItem
  - 实体: Order, OrderItem
  - 值对象: OrderId, Money, Address
  - 事件: OrderPlaced, OrderCancelled, OrderPaid
  - 命令: PlaceOrder, CancelOrder, PayOrder
  - API: POST /api/orders, GET /api/orders/{id}
  
- InventoryContext (核心域)
- PaymentContext (支撑域)
- UserContext (通用域)
```

## 6. 实战技巧

### 避免陷阱

- ❌ 先画类图 → 回到事件
- ❌ 一次 5 天 → 4 小时一节
- ❌ 只有技术人员 → 业务 + 设计师 + 测试 + 运维
- ❌ 试图一次画完 → 1-2 个核心流程先画

### 成功要点

- ✅ **业务专家主导**，技术辅助
- ✅ **大量黄色便签**（事件先于聚合）
- ✅ **问"为什么"**（5 个为什么）
- ✅ **持续时间 ≤ 4 小时**（疲劳后质量下降）

## 7. 事件风暴 → 代码

```
领域事件 OrderPlaced
  → 限界上下文 OrderContext
  → 聚合 Order
  → 实体 Order
  → 事件总线 Kafka topic=order-events
  → 消费者 PaymentContext, InventoryContext
```

事件风暴 = 业务 → 限界上下文 → 聚合 → 实体 → 代码。

## 8. 现代变体

- **远程事件风暴**：Miro / Mural + 视频会议
- **异步事件风暴**：12 人分 4 组，每组 90 分钟
- **微事件风暴**：单限界上下文，30-60 分钟

## 9. 与其他方法对比

| | 事件风暴 | Domain Storytelling | BPMN |
|------|----------|---------------------|------|
| 抽象度 | 中 | 高 | 高 |
| 速度 | 4 小时 | 4-8 hour | 1-2 day |
| 重点 | 事件 | 业务流程 | 流程图 |
| 团队规模 | 8-15 人 | 4-8 人 | 1-3 人 |

## 10. 实战 checklist

- [ ] 业务专家主导
- [ ] 1-2 个核心流程（不要贪多）
- [ ] 大量黄色便签（事件先于聚合）
- [ ] 标出限界上下文边界
- [ ] 输出：事件清单 + 限界上下文图
- [ ] 直接转化为代码骨架

## 🔗 下一步
- [聚合 / 实体 / 值对象](/11-ddd/basics)
- [限界上下文](/11-ddd/bounded-context)
