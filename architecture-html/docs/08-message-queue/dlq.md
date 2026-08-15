---
title: 死信队列 / 重试策略
---
# 死信队列与重试策略

## 1. 为什么需要 DLQ

```
消费者处理消息失败：
  - 重试：可能继续失败（永久错误）
  - 阻塞队列：消息卡住，后续都受影响
  - 丢弃：数据丢失

DLQ：失败消息进"死信队列"，独立处理
  - 不影响主流程
  - 人工排查
  - 重放 / 修复 / 丢弃
```

## 2. DLQ 实战：RabbitMQ

```java
// 1. 声明 DLQ
@Bean
public DirectExchange deadLetterExchange() { return new DirectExchange("dlx"); }

@Bean
public Queue mainQueue() {
  return QueueBuilder.durable("orders")
    .withArgument("x-dead-letter-exchange", "dlx")
    .withArgument("x-dead-letter-routing-key", "dlq.orders")
    .build();
}

@Bean
public Queue dlq() { return QueueBuilder.durable("dlq.orders").build(); }

// 2. 消费失败 → 拒收
@RabbitListener(queues = "orders")
public void onOrder(OrderEvent e) {
  try { process(e); }
  catch (Exception ex) {
    throw new AmqpRejectAndDontRequeueException("retry fail → DLQ");
  }
}
```

## 3. Kafka DLQ 实战

```yaml
# 1. 创建 DLQ topic
kafka-topics --create --topic orders-dlq --partitions 3 --replication-factor 3

# 2. 消费时捕获错误
@KafkaListener(topics = "orders")
public void onOrder(OrderEvent e) {
  try {
    process(e);
  } catch (Exception ex) {
    kafkaTemplate.send("orders-dlq", e);
    ack(e);  // 立即 ack，不再重试
  }
}
```

**或用 Spring Kafka 的 DefaultErrorHandler**：

```java
@Bean
public DefaultErrorHandler errorHandler(KafkaTemplate<String, String> template) {
  var recoverer = new DeadLetterPublishingRecoverer(template, "orders-dlq");
  return new DefaultErrorHandler(recoverer, new FixedBackOff(1000L, 3));
  // 重试 3 次，每次间隔 1s，失败进 DLQ
}
```

## 4. 重试策略

### 立即重试 vs 延迟重试

```java
// 1. 立即重试（同步 / 幂等操作）
// 2. 延迟重试（指数退避，IO 类）
new ExponentialBackOff(1000L, 2.0)
// 第 1 次：1s
// 第 2 次：2s
// 第 3 次：4s
// 第 4 次：8s
// 上限：60s

// 3. 多次重试 + DLQ（混合）
RetryTemplate.builder()
  .maxAttempts(3)
  .exponentialBackoff(1000, 2.0)
  .retryOn(IOException.class)
  .recoverer(new DeadLetterRecoverer("dlq-topic"))
  .build()
```

### 重试 vs 幂等

```
重试 = 再次执行同一操作
幂等 = 重试 N 次 = 重试 1 次
  ↓
必须先设计幂等，才能安全重试
```

## 5. 实战：库存扣减

```java
@KafkaListener(topics = "order.created")
public void onOrder(OrderEvent e) {
  // 1. 幂等：检查已扣过没
  if (inventoryRepo.frozen(e.sku)) return;

  // 2. 试扣（乐观锁）
  int affected = jdbcTemplate.update(
    "UPDATE inventory SET stock = stock - ? WHERE sku = ? AND stock >= ?",
    e.qty, e.sku, e.qty
  );
  if (affected == 0) throw new RuntimeException("库存不足");

  // 3. 发 frozen 事件
  kafkaTemplate.send("inventory.frozen", e);
}
```

**重试 5 次都不会出错**：幂等保护 + 乐观锁 + 库存检查。

## 6. 实战：支付回调

```java
@KafkaListener(topics = "payment.callback")
public void onPayment(PaymentCallbackEvent e) {
  // 幂等：用 orderId 唯一索引
  if (orderRepo.isPaid(e.orderId)) return;

  // 试更新状态
  int affected = orderRepo.markPaid(e.orderId, e.transactionId);
  if (affected == 0) {
    // 重复消息 / 状态错乱
    log.warn("order {} already paid", e.orderId);
    return;
  }
}
```

## 7. 死信处理流程

```
主流程 → 失败 → DLQ
              ↓
         人工排查
              ↓
   ┌─────┼─────┐
   ↓     ↓     ↓
 重放  修复  丢弃
```

**重放**：修复后重发到主队列
**修复**：手动修改业务数据
**丢弃**：确认是无效消息（如重复）

## 8. 重试 vs DLQ 决策

| 场景 | 重试 | DLQ |
|------|------|-----|
| 瞬态故障（网络抖动） | ✅ | |
| 业务校验失败 | | ✅ |
| 数据已存在 | | ✅ |
| 系统 bug | | ✅（先修复） |
| 永久错误 | | ✅ |

**原则**：可恢复的 → 重试；不可恢复的 → DLQ。

## 9. Spring Kafka 实战

```yaml
spring:
  kafka:
    consumer:
      auto-offset-reset: earliest
      enable-auto-commit: false
    producer:
      acks: all
      retries: 3
    listener:
      ack-mode: manual
```

```java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory(
    ConsumerFactory<String, String> cf
) {
  var factory = new ConcurrentKafkaListenerContainerFactory<>();
  factory.setConsumerFactory(cf);
  factory.setCommonErrorHandler(errorHandler);  // DLQ 重试
  return factory;
}
```

## 10. 实战选型

| 场景 | 方案 |
|------|------|
| 瞬态故障 | 指数退避重试 3 次 |
| 业务校验 | DLQ + 人工 |
| 重复消息 | 业务幂等 + 唯一索引 |
| 资金 | 强一致 + 幂等 + 监控告警 |
| 死信回收 | 监控 → 告警 → 人工 / 自动重放 |

## 🔗 下一步
- [Kafka vs RabbitMQ](/08-message-queue/compare)
- [顺序 / 幂等](/08-message-queue/idempotency)
- [幂等性设计](/03-ha-theory/idempotency)
