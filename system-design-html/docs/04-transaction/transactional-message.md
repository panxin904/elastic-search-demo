---
title: 事务消息
---

# 事务消息

> MQ 自己实现"业务 + 消息"的两阶段提交，简化分布式事务。**RocketMQ 首创，工业级标准**。

## 1. 什么是事务消息？

```
定义：
  - MQ 提供的事务性消息投递
  - 保证"本地事务"和"消息发送"原子性
  - 业务只需写本地事务 + 消息，MQ 帮你保证一致

📌 区别于普通消息：
   普通消息：业务 commit → 发消息（可能发不出去）
   事务消息：业务 commit → MQ 二次确认 → 才投递
```

## 2. 为什么需要事务消息？

```
场景：下单 + 扣库存
  1. 写订单（业务库）
  2. 发消息（MQ）
  
  问题：
    - 订单成功 + 消息失败 → 库存没扣
    - 订单失败 + 消息成功 → 库存扣了但订单没生成
    - 顺序问题导致不一致

事务消息：
  - 把订单和消息"绑定"成原子操作
  - MQ 帮你回查（如果消息状态未知）
```

## 3. RocketMQ 事务消息

### 3.1 三状态

```
消息生命周期：
  ┌─────────┐
  │ 准备    │  发送半消息（对消费者不可见）
  └────┬────┘
       ↓
  ┌─────────┐
  │ 提交    │  本地事务成功，消息对消费者可见
  └────┬────┘
       ↓
  ┌─────────┐
  │ 回滚    │  本地事务失败，消息删除
  └─────────┘

中间状态：
  - 半消息（half message）：已发到 broker 但对消费者不可见
  - 未决状态：需要本地事务回查
```

### 3.2 流程

```
┌──────────┐                  ┌──────────┐                  ┌──────────┐
│ Producer │                  │  Broker  │                  │ Consumer │
└────┬─────┘                  └────┬─────┘                  └────┬─────┘
     │  1. 发送半消息              │                                │
     │ ──────────────────────→   │                                │
     │                            │ 存为半消息                     │
     │  2. ACK（半消息成功）       │                                │
     │ ←──────────────────────   │                                │
     │                            │                                │
     │  3. 执行业务本地事务        │                                │
     │  （写订单、写库）          │                                │
     │                            │                                │
     │  4. 发送 commit / rollback │                                │
     │ ──────────────────────→   │                                │
     │                            │  5. commit → 投递消息          │
     │                            │ ────────────────────────────→ │
     │                            │                                │
     │  (如果超时)                │                                │
     │  6. 主动回查本地事务状态    │                                │
     │ ←──────────────────────   │                                │
     │  7. 返回 commit/rollback   │                                │
     │ ──────────────────────→   │                                │
     └──────────┘                  └──────────┘                  └──────────┘
```

### 3.3 代码实现

```java
// 1. 事务监听器
public class OrderTransactionListener implements TransactionListener {
    
    // 本地事务执行
    @Override
    public LocalTransactionState executeLocalTransaction(Message msg, Object arg) {
        try {
            // 执行业务（如写订单库）
            orderService.createOrder(arg);
            return LocalTransactionState.COMMIT_MESSAGE;
        } catch (Exception e) {
            return LocalTransactionState.ROLLBACK_MESSAGE;
        }
    }

    // 回查（MQ 反查本地事务状态）
    @Override
    public LocalTransactionState checkLocalTransaction(MessageExt msg) {
        // 查订单表
        Order order = orderDao.findById(msg.getKeys());
        if (order != null) {
            return LocalTransactionState.COMMIT_MESSAGE;
        } else {
            return LocalTransactionState.ROLLBACK_MESSAGE;
        }
    }
}

// 2. 发送
TransactionMQProducer producer = new TransactionMQProducer("order_group");
producer.setTransactionListener(new OrderTransactionListener());
producer.start();

Message msg = new Message("OrderTopic", "order.created",
                          order.getId().toString(),  // keys
                          JSON.toJSONBytes(order));
SendResult result = producer.sendMessageInTransaction(msg, order);
```

## 4. Kafka 事务消息

### 4.1 模型

```
Kafka 事务（KIP-98）：
  - 引入 Transaction Coordinator
  - Producer 启动事务 → 写多 topic/partition
  - Consumer 设置 isolation.level=read_committed

📌 Kafka 事务是"消息→消息"的事务
   不是"业务 DB → 消息"的事务
   适合 Kafka Streams / 跨 topic 写
```

### 4.2 代码示例

```java
// 1. Producer
Properties props = new Properties();
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "my-tx-id");
KafkaProducer<String, String> producer = new KafkaProducer<>(props);
producer.initTransactions();

try {
    producer.beginTransaction();
    producer.send(new ProducerRecord<>("topic-a", "key1", "value1"));
    producer.send(new ProducerRecord<>("topic-b", "key2", "value2"));
    producer.commitTransaction();
} catch (Exception e) {
    producer.abortTransaction();
}

// 2. Consumer
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
```

### 4.3 Kafka 事务 vs RocketMQ 事务

| 维度 | RocketMQ | Kafka |
|---|---|---|
| 业务事务 | 支持（executeLocalTransaction）| 不直接支持 |
| 范围 | 跨服务事务 | Kafka 内事务 |
| 回查 | 自动 | 手动 |
| 性能 | 中 | 高 |

## 5. 关键设计

### 5.1 半消息

```
半消息：
  - 已发到 broker，对消费者不可见
  - 等 commit / rollback
  - 超时未决 → MQ 主动回查

📌 半消息是事务消息的核心
   broker 必须有"未决"状态
```

### 5.2 消息回查

```
为什么需要回查？
  - Producer commit/rollback 因网络问题没到 broker
  - broker 不知道这条消息该不该投
  - 必须主动问 producer

回查限制：
  - 默认 5 次（可配置）
  - 间隔递增
  - 都失败 → 消息丢弃（不投递）

📌 回查的核心是幂等
   查业务表判断事务状态
```

### 5.3 防重复消费

```
事务消息也可能重复：
  - commit 发出去 → broker 没收到 ACK → 重新发 commit
  - 消息可能被投递多次

解决：
  - 消费方幂等（同本地消息表）
  - msg_id / keys 唯一索引
  - 业务幂等（订单状态机）
```

## 6. 事务消息 vs 本地消息表

| 维度 | 事务消息 | 本地消息表 |
|---|---|---|
| 实现方 | MQ 提供 | 业务自己写 |
| 复杂度 | 业务少 | 业务多 |
| 消息表 | 不需要 | 需要 |
| 实时性 | 较高（毫秒） | 较低（秒） |
| 强依赖 MQ | 是 | 否 |
| 适用 | MQ 是核心 | 业务简单 |

## 7. 经典案例

### 7.1 电商下单

```
业务：
  - 订单服务写订单
  - 库存服务扣库存
  - 营销服务发券

用事务消息：
  1. 订单服务发半消息（topic=order.created）
  2. 写订单（本地事务）
  3. 订单成功 → commit 消息
  4. 库存 / 营销服务消费
```

### 7.2 跨行转账

```
A 行 → B 行：
  1. A 行发半消息（topic=transfer.created）
  2. A 行扣款
  3. 扣款成功 → commit
  4. 消息投递到 B 行
  5. B 行消费 → 加款

📌 跨行场景下，B 行回滚难
   走 Saga 或人工对账
```

## 8. 注意事项

### 8.1 反查幂等

```
反查必须是幂等的：
  - 不能因为反查而执行两次业务
  - 检查业务表状态，再返回结果

实现：
  LocalTransactionState checkLocalTransaction(MessageExt msg) {
      Order order = orderDao.findById(msg.getKeys());
      // 不管查多少次，结果一致
      return order != null ? COMMIT : ROLLBACK;
  }
```

### 8.2 长事务

```
问题：
  - 本地事务执行 30s
  - 半消息卡在 broker 30s
  - broker 频繁反查

解决：
  - 业务尽量短
  - 异步处理（业务写库 → 立即返回 → 后台慢慢处理）
  - 调整反查参数
```

### 8.3 死信处理

```
反查都失败：
  - 消息进入"已死信"状态
  - 不会投递
  - 人工处理（补偿、对账）

📌 死信不可怕
   重要的是有"对账"机制兜底
```

## 9. 何时用事务消息？

```
✅ 适合：
  - 业务能拆出"主业务 + 多个分支业务"
  - 主业务用本地事务，分支业务用 MQ 异步
  - MQ 是核心基础设施
  - 想少写代码（用框架能力）

❌ 不适合：
  - 强一致（用 TCC）
  - MQ 不可用（退化成本地消息表）
  - 简单业务（用本地事务 + 同步调用）
```

## 10. 一句话总结

```
📌 事务消息 = 半消息 + 本地事务 + 消息回查，由 MQ 保证一致
📌 RocketMQ：原生支持（executeLocalTransaction + checkLocalTransaction）
📌 Kafka：消息内事务（KIP-98），不直接支持业务 DB 事务
📌 核心：半消息对消费者不可见，等本地事务确认后才投递
📌 回查：MQ 主动问 producer 事务状态，必须幂等
📌 vs 本地消息表：事务消息代码少、强依赖 MQ；本地消息表自己写轮询、可降级
📌 适合：电商下单、跨服务数据同步、MQ 强依赖场景
📌 反查失败 → 死信 + 人工对账兜底
```

## 11. 参考资料

- RocketMQ 事务消息设计文档
- "Transactional Messaging" (Pat Helland, 2005)
- Kafka KIP-98 设计
- "In-Doubt Transactions" (Microsoft Research)
- Apache RocketMQ 官方文档
- Apache Kafka Exactly-Once Semantics
