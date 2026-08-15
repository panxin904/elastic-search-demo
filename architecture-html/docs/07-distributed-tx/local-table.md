---
title: 本地消息表
---
# 本地消息表（Outbox 模式）

## 1. 核心思想

**业务表和消息表写同一个本地事务** → 一定能发出去。

```
START TRANSACTION
  INSERT INTO orders (...)    -- 业务数据
  INSERT INTO outbox (...)    -- 消息表（同一 DB 同一事务）
COMMIT
↓
轮询 outbox 表 → 发到 MQ → 标记已发
```

**保证**：业务成功 → 消息一定能被发出去（at-least-once 消息 + 业务强一致）。

## 2. 三个关键表

```sql
CREATE TABLE orders (
  id BIGINT PRIMARY KEY,
  user_id BIGINT,
  amount DECIMAL,
  status VARCHAR(20),
  created_at TIMESTAMP
);

CREATE TABLE outbox (
  id BIGINT PRIMARY KEY,
  topic VARCHAR(100),        -- 'order.created'
  payload JSON,
  status VARCHAR(20),        -- 'pending' | 'sent' | 'failed'
  retry_count INT DEFAULT 0,
  created_at TIMESTAMP,
  sent_at TIMESTAMP NULL
);
```

## 3. 业务 + 轮询

```java
@Service
public class OrderService {
  @Transactional
  public void placeOrder(OrderDTO dto) {
    orderRepo.create(dto);                    // 业务写入
    outboxRepo.create("order.created", dto);  // 消息写入（同一事务）
  }
}

@Scheduled(fixedDelay = 100)
public void pollOutbox() {
  List<Outbox> pending = outboxRepo.findPending(limit=100);
  for (var msg : pending) {
    kafkaTemplate.send(msg.topic, msg.payload).get(5, TimeUnit.SECONDS);
    outboxRepo.markSent(msg.id);
  }
}
```

## 4. 优缺点

✅ **优点**：
- **不丢消息**：业务和消息同事务
- **无 2PC**：纯本地事务，性能好
- **易实现**：一张表 + 一个定时器

❌ **缺点**：
- **轮询延迟**：秒级（可优化为 CDC / logtail）
- **消息表膨胀**：需定期清理
- **顺序**：发到 MQ 后仍可能乱序（消费者要按 ID 排序）

## 5. 优化：CDC（Change Data Capture）

不用轮询，直接订阅数据库 binlog：

```
业务表写 → MySQL binlog → Debezium → Kafka
```

**优势**：实时（亚秒级），无轮询压力。
**代表**：Debezium、Canal、Maxwell。

## 6. 实战：Debezium + Outbox

```java
// 不用轮询，直接订阅 outbox 表的 binlog
@DebeziumListener(table = "outbox")
public void onOutboxChange(ChangeRecord<Outbox> change) {
  if (change.isInsert()) {
    Outbox msg = change.getRecord().getValue();
    kafkaTemplate.send(msg.getTopic(), msg.getPayload());
  }
}
```

**优势**：低延迟 + 无应用层轮询 + 强一致（事务保证）。

## 7. 实战：完整下单流程

```
用户下单 → OrderService (本地事务)
  ├─ INSERT INTO orders
  ├─ INSERT INTO outbox (topic='order.created', payload={...})
  └─ COMMIT

↓
轮询 / CDC → Kafka topic=order.created

↓
PaymentService (consumer)
  ├─ 支付
  ├─ 写支付表
  └─ 发 PaymentCompleted 事件

↓
InventoryService (consumer of payment.completed)
  ├─ 扣库存
  └─ 发 InventoryUpdated 事件

↓
LogisticsService (consumer of inventory.updated)
  └─ 创建物流单
```

**任何环节失败 → 发回滚事件 → 各服务补偿**。

## 8. 实战优化

### 消息表清理

```sql
-- 定期清理已发送消息
DELETE FROM outbox WHERE status = 'sent' AND sent_at < NOW() - INTERVAL '7 days';
```

```java
@Scheduled(cron = "0 0 * * * *")
public void cleanupOutbox() {
  outboxRepo.deleteOld(7);
}
```

### 批量发送

```java
@Scheduled(fixedDelay = 100)
public void pollAndSend() {
  List<Outbox> batch = outboxRepo.findPending(100);
  kafkaTemplate.sendBatch(batch);  // 批量
  outboxRepo.markSent(batch);
}
```

## 9. 变体

| 变体 | 差异 |
|------|------|
| **Outbox** | 业务 + 消息同表，轮询发 |
| **CDC** | 订阅 binlog 实时发 |
| **Transactional Inbox** | 消费者侧，存已收消息去重 |
| **Listen to Yourself** | 业务写完 + 发本地事件，事务 |

## 10. 选型

| 场景 | 选 |
|------|-----|
| 简单 + 强一致 | Outbox（轮询） |
| 高吞吐 + 实时 | CDC（Debezium） |
| 已经用 Kafka | Outbox + CDC + Kafka |
| 多服务 / 跨语言 | Outbox + MQ（通用） |

## 🔗 下一步
- [2PC / 3PC](/07-distributed-tx/2pc)
- [TCC 模式](/07-distributed-tx/tcc)
- [Saga 模式](/07-distributed-tx/saga)
- [幂等性设计](/03-ha-theory/idempotency)
