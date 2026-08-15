---
title: 顺序保证 / 幂等消费
---
# 顺序保证 / 幂等消费

## 1. 两个核心问题

```
问题 1：消息乱序
  场景：order.created 在 payment.completed 之前到了
  → 业务状态错乱

问题 2：消息重复
  场景：at-least-once 重投 → 同一订单扣两次
  → 业务错误
```

## 2. 顺序保证

### Kafka 的顺序保证

**仅分区内有序，跨分区无序**。

```
Topic "order" (3 个 partition)
  Part 0: msg1, msg2, msg3  ← 同 key 必同 partition
  Part 1: msg4, msg5
  Part 2: msg6
```

**保持顺序的关键**：相同业务 key 路由到相同 partition。

```java
// Kafka producer
kafkaTemplate.send(new ProducerRecord<>(
  "order",
  String.valueOf(order.getUserId()),  // partition key = userId
  order
));
// 同一 userId → 同 partition → 严格顺序
```

**消费端**：单 partition 单 consumer 可保证顺序。**多 consumer 同 group**：每个分区只被一个 consumer 消费。

### 顺序被破坏的场景

```
场景：下单 → 支付 → 库存
  1. 生产发 order.created（partition 0）
  2. 库存服务发 inventory.frozen（partition 1）
  3. 支付服务发 payment.completed（partition 0）

如果消费顺序为 2 → 1 → 3：
  看到 frozen → created → completed 顺序错乱
```

**解决**：
- 全部消息同 partition（同 key）
- 或消费端按业务 ID 排序

## 3. 幂等消费

### 为什么要幂等

MQ 默认 **at-least-once**：消息可能重发（网络超时 / consumer 崩）。

```
消费者处理 msg 成功 → 但响应前崩
  → broker 没收到 ack
  → 重投 msg
  → 重复处理！
```

**结论**：消费者必须幂等（同一消息处理 N 次 = 处理 1 次）。

### 三大幂等实现

**1. 唯一键 + 唯一索引**

```sql
CREATE TABLE processed_messages (
  msg_id VARCHAR(64) PRIMARY KEY,
  processed_at TIMESTAMP
);

-- 处理前
INSERT INTO processed_messages (msg_id) VALUES (?);
-- 重复主键冲突 → 跳过
```

```java
@Transactional
public void onMessage(Message msg) {
  if (processedMsgRepo.exists(msg.getId())) {
    log.info("duplicate msg: {}", msg.getId());
    return;
  }
  processOrder(msg);
  processedMsgRepo.save(msg.getId());
}
```

**2. 业务 ID（去重表）**

```
order.created event 含 bizId (orderId)
consumer: SELECT * FROM payments WHERE order_id = ? AND status = 'PAID'
  已存在 → 跳过
  不存在 → 扣款 + 写支付
```

**3. 状态机（CAS）**

```
UPDATE order SET status = 'PAID' WHERE id = ? AND status = 'CREATED'
affected = rowsAffected
if affected == 0: 已支付，幂等
```

## 4. 业务幂等设计

### 支付场景

```
1. 收到 msg(order_id=123, amount=100)
2. SELECT * FROM payments WHERE order_id = 123 AND status = 'PAID'
   → 不存在：处理
   → 存在：跳过
3. INSERT INTO payments (id, order_id, amount, status='PAID')
   → 主键冲突：重复消息，跳过
4. 发支付成功事件
```

### 库存场景

```
1. 收到 msg(sku='S001', qty=10)
2. SELECT stock FROM inventory WHERE sku='S001' FOR UPDATE
3. UPDATE inventory SET stock = stock - 10 WHERE sku = 'S001' AND stock >= 10
   affected = rowsAffected
   affected = 0 → 库存不足
   affected = 1 → 扣减成功
```

## 5. Kafka exactly-once 语义

Kafka 0.11+ 引入**事务 API**：

```java
// 生产
kafkaTemplate.executeInTransaction(t -> {
  t.send("order.created", order);
  t.send("payment.required", payment);
  t.commitTransaction();
});
// 原子：全成功 或 全失败

// 消费（read_committed 隔离）
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
```

**事务 + 幂等消费者 + 流处理** = 真 exactly-once。

## 6. 实战：消息重投 5 次失败

```java
@KafkaListener(topics = "order.created")
public void onOrderCreated(OrderCreatedEvent e) {
  try {
    orderService.create(e);
  } catch (Exception ex) {
    // 失败 → 5 次重试
    throw new RuntimeException(ex);
    // 5 次后 → DLQ（看 broker 配置）
  }
}
```

**关键**：重试间加退避（1s, 2s, 4s, 8s...），避免雪崩。

## 7. 顺序 + 幂等的权衡

| 场景 | 顺序方案 | 幂等方案 |
|------|---------|---------|
| 订单创建 + 支付 | 同 userId partition | 业务唯一索引 |
| 库存扣减 | 同 sku partition | 乐观锁 / CAS |
| 物流预约 | 同 orderId partition | 业务状态机 |
| 跨服务同步 | 同 bizId partition | 去重表 |

**原则**：partition key = 业务唯一标识。

## 8. 实战选型

| 场景 | 方案 |
|------|------|
| 强顺序 + 强一致 | Kafka + exactly-once + 业务幂等 |
| 弱顺序 + 最终一致 | Kafka + at-least-once + 幂等 |
| 复杂路由 + DLQ | RabbitMQ + 手动 ack + 重试 |
| 高吞吐日志 | Kafka + 分区有序 |
| RPC | RabbitMQ + correlation ID |

## 🔗 下一步
- [Kafka vs RabbitMQ](/08-message-queue/compare)
- [死信 / 重试](/08-message-queue/dlq)
- [幂等性设计](/03-ha-theory/idempotency)
