---
title: Saga 模式
---

# Saga 模式

> 把长事务拆成多个短事务，通过补偿操作保证最终一致。

## 1. 什么是 Saga？

```
传统分布式事务（2PC）：
  - 一个大事务跨多个服务
  - 同步阻塞
  - 性能差

Saga 思路：
  - 把大事务拆成 N 个本地子事务
  - 每个子事务有对应的补偿操作
  - 部分失败时按相反顺序执行补偿
  → 最终一致，无锁定
```

## 2. 直觉

```
例：下单流程（4 个子事务）
  T1: 创建订单
  T2: 扣库存
  T3: 扣款
  T4: 发货

如果 T3 失败：
  - 补偿 C3：退款
  - 补偿 C2：补回库存
  - 补偿 C1：取消订单
  → 全程无锁定
```

## 3. Saga 的两种实现

### 3.1 编排（Choreography）

```
没有中心协调者
每个服务监听其他服务的事件，自主决定下一步

事件流：
  OrderService 发 OrderCreated 事件
    ↓
  InventoryService 监听 → 扣库存 → 发 InventoryReserved
    ↓
  PaymentService 监听 → 扣款 → 发 PaymentCompleted
    ↓
  ShippingService 监听 → 发货

失败时反向：
  PaymentService 发 PaymentFailed
    ↓
  InventoryService 监听 → 补库存
    ↓
  OrderService 监听 → 取消订单

📌 优点：简单无中心
📌 缺点：流程散落，难以追踪
```

### 3.2 编制（Orchestration）

```
有一个 Saga 协调器（Orchestrator）
  - 知道整个流程
  - 告诉每个服务该做什么
  - 处理失败补偿

协调器伪代码：
  saga = new Saga()
  saga.addStep(InventoryService.reserve)
  saga.addStep(PaymentService.charge)
  saga.addStep(OrderService.confirm)
  
  try {
    saga.execute()
  } catch (e) {
    saga.compensate()  // 逆序补偿
  }

📌 优点：流程清晰，易于追踪
📌 缺点：协调器是中心点，需要高可用
```

## 4. 补偿操作的设计

### 4.1 什么是补偿？

```
补偿 = 撤销之前操作的影响

例：
  T1: 创建订单（订单状态 = 已创建）
  C1: 取消订单（订单状态 = 已取消）

  T2: 扣库存 -1
  C2: 加回库存 +1

  T3: 扣款 -100
  C3: 退款 +100
```

### 4.2 补偿的挑战

```
1. 等价性：
   C 是否真的"撤销"了 T？
   例：发货后无法"撤销发货"，只能退货

2. 幂等性：
   C 多次执行结果一致？
   例：退款一次和退款两次应该一样

3. 顺序：
   C 必须按 T 的相反顺序执行
   例：先退款后补库存（避免重复扣款）

4. 异步：
   C 可能要异步执行（不能立刻撤回）
   例：已发货商品需要召回流程
```

## 5. Saga vs 2PC

```
┌──────────────┬──────────────────┬──────────────────┐
│              │ 2PC              │ Saga             │
├──────────────┼──────────────────┼──────────────────┤
│ 一致性       │ 强一致           │ 最终一致         │
│ 性能         │ 低               │ 高               │
│ 复杂度       │ 中（协议）       │ 高（业务）       │
│ 适用事务     │ 短               │ 长               │
│ 锁           │ 全程             │ 无               │
│ 回滚         │ 自动             │ 业务补偿         │
│ 隔离性       │ 强               │ 弱               │
└──────────────┴──────────────────�──────────────────┘
```

## 6. 隔离性问题

### 6.1 Saga 的弱隔离

```
2PC：所有子事务都锁定 → 其他事务看不到中间状态
Saga：逐步提交 → 其他事务可能看到中间状态

例：
  Saga 进行中：
    T1 已提交（订单已创建）
    T2 还没执行（库存还没扣）
  此时用户 B 也下单买同商品：
    - 看到 T1 已提交（订单已创建）
    - 看到 T2 还没执行（库存还是原值）
    - 也下单
  → 库存可能超卖

📌 Saga 不保证事务隔离
```

### 6.2 隔离性增强

```
方案 1：业务层语义锁
  - Saga 内"伪锁定"对外不可见
  - 通过状态字段标记
  例：订单状态 = "锁定中"，不允许其他操作

方案 2：重新排序
  - 把冲突的事务排序
  - 让它们串行执行

方案 3：版本号 / 业务时间戳
  - 检测冲突
  - 失败时重试

方案 4：补偿性 Saga
  - 提前发现冲突
  - 用补偿回滚
```

## 7. Saga 框架

### 7.1 Apache ServiceComb Saga

```
华为开源：
  - Java 实现
  - Spring Cloud 集成
  - 提供 Saga 协调器
  - 支持编排模式
```

### 7.2 Seata Saga

```
阿里 Seata：
  - Java 实现
  - 三种模式：AT / TCC / Saga
  - Saga 模式支持编排 + 编制
  - 与 Spring Cloud / Dubbo 集成
```

### 7.3 Eventuate Tram Saga

```
事件驱动 Saga：
  - 基于 Eventuate 事件总线
  - Java 实现
  - 支持编排和编制
```

### 7.4 Temporal / Cadence

```
工作流引擎：
  - 不限于 Saga，但适合
  - Go / Java SDK
  - 强大的错误处理 + 重试
```

## 8. 实战案例

### 8.1 电商下单

```
子事务：
  1. 创建订单（order_db）
  2. 扣库存（inventory_db）
  3. 扣款（payment_db）
  4. 发优惠券（coupon_db）
  5. 通知商家（notification）

补偿：
  C1: 取消订单
  C2: 补回库存
  C3: 退款
  C4: 退还优惠券
  C5: 取消通知

📌 实际实现：
   - 状态机 + 数据库
   - 失败重试 + 告警
   - 人工介入流程（超时不回滚）
```

### 8.2 旅行预订

```
子事务：
  1. 预订机票
  2. 预订酒店
  3. 预订租车
  4. 扣款

如果酒店预订失败：
  - 取消机票预订
  - 取消租车预订
  - 不扣款

📌 编排模式适合：
   - 第三方服务（航空公司 API）
   - 状态不可控
   - 长延迟
```

## 9. Saga 设计原则

```
1. 每个子事务必须有补偿
2. 补偿也要幂等
3. 失败时按逆序补偿
4. 补偿失败要重试
5. 超时要告警（不能无限重试）
6. 状态可追踪（日志/数据库）
7. 隔离性问题业务层解决
```

## 10. 与其他方案对比

### 10.1 Saga vs TCC

```
TCC：
  - Try 阶段预留资源
  - 性能好（无长事务）
  - 实现复杂（每个操作要写 Try/Confirm/Cancel）

Saga：
  - 无 Try 阶段
  - 直接执行子事务
  - 实现稍简单（只需子事务 + 补偿）
  - 隔离性差
```

### 10.2 Saga vs 异步消息

```
异步消息：
  - 完全解耦
  - 业务上下游依赖消息
  - 复杂业务链路不清晰

Saga：
  - 链路明确
  - 失败可追踪
  - 适合中等复杂度
```

## 11. 一句话总结

```
📌 Saga = 长事务拆分 + 补偿操作 + 最终一致
📌 两种实现：编排（事件驱动，无中心）vs 编制（有协调器）
📌 优点：无锁定、高性能、适合长事务
📌 缺点：弱隔离、业务复杂、补偿设计难
📌 隔离性问题靠业务层解决：语义锁、重排序、版本号
📌 工业级实现：Seata Saga / Apache ServiceComb Saga / Temporal
📌 现代微服务架构的事实标准之一
```

## 12. 参考资料

- SAGAS (Garcia-Molina & Salem, 1987) —— 原论文
- Applying Sagas Pattern (Microsoft, 2020)
- Seata Saga 模式文档
- Microservices Patterns (Chris Richardson, 2018) —— Saga 章节
- Apache ServiceComb Saga 文档


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

<!-- svg-injected:do-not-edit -->

## 图示：Saga 编排式补偿流程与 Orchestrator

![Saga 编排式补偿流程与 Orchestrator](/saga-compensation-flow.svg)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [architecture](https://java-px.bot.cd/architecture/):企业架构
- [java](https://java-px.bot.cd/java-web-manual/):Java 实现
- [kafka](https://java-px.bot.cd/kafka/):消息
