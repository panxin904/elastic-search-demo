---
title: 顺序保证
---

# 📊 顺序保证

> Kafka 保证**单 Partition 内消息有序**，但**跨 Partition 无序**。理解顺序保证是很多业务场景的前提。

## 🎯 Kafka 的顺序保证级别

```
1. 全局有序：❌ 不支持
   - 多个 Partition 之间并行处理，无法全局排序

2. 单 Partition 内有序：✅ 默认保证
   - Producer 按顺序发送，Broker 按顺序追加
   - Consumer 按 offset 顺序消费

3. 单 Key 有序：✅ 通过 Key 保证
   - 同 Key 进入同 Partition（hash 一致）
   - 单 Partition 内顺序保证

4. 业务维度有序：✅ 业务设计保证
   - 如订单按 userId 分区，订单状态变更有序
```

## 📊 消息顺序的重要性

```
场景 1：订单状态变更
  订单创建 → 支付 → 发货 → 完成
  ❌ 如果乱序：发货 → 完成 → 支付（状态错乱）

场景 2：数据库变更同步（CDC）
  INSERT → UPDATE → DELETE
  ❌ 如果乱序：DELETE → UPDATE → INSERT（数据错误）

场景 3：金融交易
  下单 → 风控 → 扣款
  ❌ 如果乱序：扣款 → 风控 → 下单（资金错误）
```

## 🔧 默认顺序保证机制

### Producer 端：单 Partition 顺序

```
前提：
  1. max.in.flight.requests.per.connection = 1（默认 5）
  2. retries > 0
  3. acks=all

保证：
  - 单 Producer 发送到单 Partition 的消息严格有序
  - 即使重试，消息顺序也不变
```

```java
// ❌ 默认配置下不保证顺序（max.in.flight > 1）
Properties props = new Properties();
props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);  // 可能乱序

// ✅ 强顺序保证
props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 1);  // 严格顺序
props.put(ProducerConfig.ACKS_CONFIG, "all");
props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);
```

### Producer 端：单 Key 顺序

```
✅ 同一 Key 一定进入同一 Partition
   → 同 Key 消息严格有序
```

```java
// ✅ 同 Key 进入同 Partition
for (int i = 0; i < 100; i++) {
    String orderId = "order-" + (i % 10);  // 10 个订单
    producer.send(new ProducerRecord<>("orders", orderId, "msg-" + i));
    // 同一 orderId 的消息会进入同一 Partition
    // 保证同订单的消息有序
}
```

### Producer 端：幂等性顺序保证

```
启用幂等性后：
  - max.in.flight.requests.per.connection ≤ 5
  - 重试时不会乱序
  - 同 Partition 内消息严格有序
```

```
⚠️ 即使 max.in.flight = 5，幂等性也能保证顺序：
  - Broker 检测 seq 重复
  - 重试时 seq 不变
  - 后续消息等重试完成才发送
```

## 🔧 Consumer 端顺序消费

### 单 Partition 顺序消费

```
✅ 单 Partition 内消息严格有序
   - Consumer 按 offset 顺序拉取
   - 不会跳过、乱序

⚠️ 多 Partition 顺序消费复杂
   - 不同 Partition 的消息并行处理
   - 可能跨 Partition 乱序
```

### Consumer 顺序保证配置

```java
Properties props = new Properties();
props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 1);  // 每次只拉 1 条
// 单线程顺序处理

// 或
props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 100);
// 单线程批量处理（仍是顺序）
```

### 顺序消费的代价

```
顺序消费 vs 并行消费：

顺序消费（单线程）：
  ✅ 严格有序
  ❌ 吞吐低（受限于单 Consumer 处理速度）

并行消费（多线程）：
  ✅ 高吞吐
  ❌ 跨 Partition 乱序

折中方案：
  按 Key 分发到不同 Consumer（Hash 分发）
  - 同 Key 进入同一 Consumer
  - 跨 Key 可并行
```

## 🔧 实战：保证业务顺序

### 场景 1：订单状态变更

```java
@Service
public class OrderStatusProducer {
    
    @Autowired
    private KafkaProducer<String, OrderEvent> producer;
    
    public void updateStatus(String orderId, OrderStatus newStatus) {
        OrderEvent event = new OrderEvent(orderId, newStatus);
        // ✅ key 用 orderId，保证同订单事件进入同一 Partition
        producer.send(new ProducerRecord<>("order-events", orderId, event));
    }
}

@Service
public class OrderStatusConsumer {
    
    // 单线程消费（保证顺序）
    @KafkaListener(topics = "order-events", concurrency = "1")
    public void consume(OrderEvent event) {
        // ✅ 单线程处理，同 orderId 的事件按顺序到达
        processOrderStatus(event);
    }
}
```

### 场景 2：数据库变更同步（CDC）

```java
@Service
public class CDCProducer {
    
    @Autowired
    private KafkaProducer<String, CDCEvent> producer;
    
    public void publishChange(String tableName, String primaryKey, CDCEvent event) {
        // ✅ key = tableName + ":" + primaryKey
        // 同表同主键的事件进入同一 Partition，保证顺序
        String key = tableName + ":" + primaryKey;
        producer.send(new ProducerRecord<>("cdc-events", key, event));
    }
}
```

### 场景 3：限流（顺序触发）

```java
@Service
public class RateLimitProducer {
    
    @Autowired
    private KafkaProducer<String, RateLimitEvent> producer;
    
    public void publishLimit(String userId, RateLimitEvent event) {
        // ✅ 同 userId 顺序处理限流事件
        producer.send(new ProducerRecord<>("rate-limit-events", userId, event));
    }
}
```

## 🔧 处理顺序问题的设计模式

### 模式 1：单一 Partition

```java
// 只创建 1 个 Partition（牺牲并行性换全局有序）
kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 1 \
    --replication-factor 3

// 优点：全局有序
// 缺点：吞吐受限（单 Partition 上限 ~10MB/s）
```

### 模式 2：按 Key 路由（推荐）

```java
// 多 Partition，按 Key 路由
kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 12 \
    --replication-factor 3

// 同一 orderId 的消息进入同一 Partition
// 不同 orderId 跨 Partition 并行
// 业务幂等保证跨 Partition 顺序
```

### 模式 3：业务端排序

```java
// 业务端收到所有 Partition 消息后排序
@Service
public class SortingConsumer {
    
    @KafkaListener(topics = "events")
    public void consume(Event event) {
        // 按时间戳排序（窗口内排序）
        pendingEvents.put(event.getKey(), event);
        
        // 定期 flush 按顺序处理
        if (shouldFlush()) {
            List<Event> sorted = pendingEvents.values().stream()
                .sorted(Comparator.comparing(Event::getTimestamp))
                .collect(Collectors.toList());
            
            for (Event e : sorted) {
                process(e);
            }
            pendingEvents.clear();
        }
    }
}
```

## 📊 顺序保证与性能权衡

| 方案 | 顺序保证 | 性能 | 复杂度 |
|------|---------|------|--------|
| **单 Partition** | 全局有序 | ❌ 低（单 Partition 上限） | 低 |
| **按 Key 路由 + 多 Partition** | 单 Key 有序 | ✅ 高 | 中 |
| **多 Partition + 业务排序** | 全局有序（窗口内） | ✅ 高 | 高 |
| **单线程顺序消费** | 单 Partition 有序 | ❌ 低 | 低 |
| **多线程并行消费 + 业务幂等** | 单 Key 有序 | ✅ 高 | 中 |

## ⚠️ 常见顺序问题

### 问题 1：Consumer 重平衡导致乱序

```
场景：Consumer Group 再平衡时，新 Consumer 可能从其他 Partition 拉取消息

影响：
  - 单 Partition 内仍有序
  - 跨 Partition 处理顺序不可控

解决：
  1. 业务端幂等设计
  2. 按 Key 路由（避免跨 Partition）
  3. 窗口排序（容忍窗口内乱序）
```

### 问题 2：重试导致顺序

```
场景：Producer 重试 msg-2 时，msg-3 已经发送成功

问题：msg-3 比 msg-2 先到达 Broker
（虽然后到达，但 Broker 拒绝接收，因为 seq 不连续）

解决：
  1. 启用幂等性（启用后自动保证顺序）
  2. max.in.flight.requests.per.connection = 1
```

### 问题 3：跨 Topic 顺序

```
场景：业务需要在 topic-a 和 topic-b 写入消息

问题：Kafka 不保证跨 Topic 顺序

解决：
  1. 启用事务
  2. 业务端排序
```

## 🛠️ 完整实战：保证业务顺序

```java
@Configuration
public class OrderedProducerConfig {
    
    @Bean
    public ProducerFactory<String, OrderEvent> orderedProducerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
        
        // ✅ 强顺序保证配置
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);
        // max.in.flight=5 + 幂等性 也能保证顺序（推荐）
        // 严格要求顺序用 max.in.flight=1（吞吐降低）
        
        return new DefaultKafkaProducerFactory<>(props);
    }
}

@Service
public class OrderEventProducer {
    
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    public void publishEvent(OrderEvent event) {
        // ✅ key 用 orderId，同订单事件进入同一 Partition
        CompletableFuture<SendResult<String, OrderEvent>> future = 
            kafkaTemplate.send("order-events", event.getOrderId(), event);
        
        future.whenComplete((result, ex) -> {
            if (ex == null) {
                log.info("Sent: topic={}, partition={}, offset={}",
                    result.getRecordMetadata().topic(),
                    result.getRecordMetadata().partition(),
                    result.getRecordMetadata().offset());
            } else {
                log.error("Send failed", ex);
            }
        });
    }
}

@Service
public class OrderEventConsumer {
    
    // ✅ 单线程消费（顺序处理）
    @KafkaListener(topics = "order-events", concurrency = "1")
    public void consume(ConsumerRecord<String, OrderEvent> record) {
        // 同 orderId 顺序到达
        processEvent(record.value());
    }
}
```

## 🎯 总结

**顺序保证核心要点**：
- ✅ 单 Partition 内消息严格有序
- ✅ 同 Key 进入同一 Partition（单 Key 有序）
- ✅ 幂等性保证重试不乱序
- ✅ max.in.flight.requests.per.connection ≤ 5 时仍保证顺序（需启用幂等性）
- ⚠️ 全局有序需要单 Partition（牺牲性能）
- ⚠️ 跨 Partition / Topic 无序（需事务或业务端排序）

**下一步：** [⚡ 性能调优](/04-producer/tuning) — Producer 性能优化实战
