---
title: BASE / 最终一致性
date: 2026-08-15  # date-auto-injected
---
# BASE 理论

## 1. BASE 是什么

Eric Brewer 提出，CAP 的 AP 选择方案：

- **B**asically **A**available（基本可用）
- **S**oft state（软状态，状态可以暂时不一致）
- **E**ventually consistent（最终一致）

**核心思想**：放弃强一致，换可用性 + 最终一致。

## 2. 与 ACID 对比

| ACID（传统数据库） | BASE（分布式） |
|-------------------|------------------|
| Atomicity（原子性）| 单操作可能部分成功 |
| Consistency（强一致）| 最终一致 |
| Isolation（隔离） | 无强隔离 |
| Durability（持久） | 通常持久（异步复制） |

## 3. 最终一致性的 4 个保证级别

1. **因果一致性**（causal）：因在果前可见
2. **读己之写**（read-your-writes）：自己写后能立刻读到
3. **单调读**（monotonic read）：不会读到比之前更旧的值
4. **前缀读**（prefix read）：不会读到乱序的因果链

DynamoDB 提供：默认最终一致 + 强一致读（Quorum）选项。

## 4. 实战：电商下单 + 减库存

```
传统 ACID：下单 + 减库存在同一事务，rollback
  优点：强一致
  缺点：分布式下跨服务难、性能差

BASE 方案：
  1. 订单服务：写订单（本地事务）→ 发"减库存"事件到 MQ
  2. 库存服务：消费 MQ → 异步减库存
  3. 用户看到"下单成功"（不等库存）
  4. 库存服务失败 → 重试 + 对账 + 补偿（退款）
```

## 5. 4 种最终一致性实现

| 实现 | 描述 | 例子 |
|------|------|------|
| **读时修复（read repair）** | 读时发现版本不一致，异步同步 | Cassandra |
| **写时修复（write repair）** | 写时同步副本 | DynamoDB |
| **异步复制** | 写主即返回，后台慢慢同步 | MySQL async replica |
| **后台 compaction** | 周期性合并 | HBase major compaction |

## 6. 实战：消息中间件 + 业务表

```java
// 写订单
@Transactional
public void placeOrder(Order order) {
  orderRepo.save(order);             // 本地事务
  kafkaTemplate.send("order.created", order);  // 发事件
}

// 库存服务：消费事件
@KafkaListener(topics = "order.created")
public void onOrderCreated(Order order) {
  inventoryRepo.deduct(order);        // 异步减库存
}
```

**保证**：库存最终一定减（at-least-once + 幂等），但不保证瞬时一致。

## 7. CAP vs BASE 选择

```
用户态 / 配置：CAP 选 CP
  - 用户登录态 → Redis Cluster / Nacos
  - 配置中心 → etcd
  - 服务发现 → Nacos（默认 AP，可选 CP）

业务态：BASE 选 AP
  - 订单、库存、购物车
  - 推荐、feed、评论

金融态：CAP 强 CP + 业务层 BASE
  - 余额（强 CP）→ 数据库分库
  - 交易记录（BASE）→ 异步复制
```

## 8. 关键反模式

- **盲目 AP**：不区分业务都用最终一致 → 资金风险
- **盲目 CP**：不分区时也用 CP → 性能浪费
- **忽略补偿**：用 BASE 但没补偿机制 → 数据丢失
- **忽略幂等**：MQ 重发消费导致重复操作 → 业务错乱

## 🔗 下一步
- [CAP 定理](/03-ha-theory/cap)
- [Raft 共识](/03-ha-theory/raft)
- [幂等性设计](/03-ha-theory/idempotency)
- [Saga 模式](/07-distributed-tx/saga)
