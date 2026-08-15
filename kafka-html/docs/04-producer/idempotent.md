---
title: 幂等性
---

# 🔁 幂等性

> 默认情况下，Producer 可能因为**重试**发送**重复消息**。Kafka 0.11+ 引入**幂等性（Idempotence）**机制，保证消息**精确一次（Exactly Once）**。

## 🎯 什么是消息重复？

```
场景：Producer 发送消息后没有收到 ack，重试导致重复

时间线：
  T0   Producer 发送 msg
  T1   Broker 写入 msg
  T2   Broker 发送 ack
  T3   ack 网络丢失
  T4   Producer 超时未收到 ack
  T5   Producer 重试发送 msg
  T6   Broker 重复写入 msg（offset 不同）

结果：同一条消息写入两次（消息重复）
```

### 重复场景

```
1. 网络抖动（ack 丢失）→ 重试 → 重复
2. Leader 切换 → Producer 重试 → 重复
3. Producer 进程崩溃 → 客户端重试 → 重复
4. ack=all + retries=3 → 重试 3 次 → 最多 3 条重复
```

## 🎯 幂等性原理

### Producer ID + Sequence Number

```
Kafka 为每个 Producer 实例分配唯一 ID：
  - PID（Producer ID）：Producer 启动时由 Broker 分配
  - Sequence Number：每个 (PID, Partition) 单调递增

Broker 端去重：
  - 收到消息时检查 (PID, Partition) 的最大 Sequence Number
  - 如果新消息的 Sequence Number = 最大值 + 1 → 接受
  - 如果新消息的 Sequence Number ≤ 最大值 → 丢弃（重复）
```

```
Producer PID=12345
  ↓
发送 msg-1 (seq=0) → Broker 接受
发送 msg-2 (seq=1) → Broker 接受
发送 msg-3 (seq=2) → Broker 写入但 ack 丢失
  ↓
重试 msg-3 (seq=2) → Broker 检测 seq ≤ max → 丢弃 ✓
```

### 幂等性保证

```
✅ 单 Producer 会话内消息不重复
  - Producer 启动到崩溃为一个会话
  - 会话内 PID 唯一
  - 同一 Partition 内 Sequence Number 单调递增

❌ 不能跨会话去重
  - Producer 重启会重新分配 PID
  - 跨会话的重复消息无法检测

⚠️ 仅保证单 Partition 幂等
  - 不同 Partition 的 Sequence Number 独立
  - 跨 Partition 的去重需要事务
```

## 🔧 启用幂等性

### Java 代码

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

// 启用幂等性（Kafka 3.x 默认 false，建议开启）
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);

// 启用幂等性后，以下配置自动设置（无需手动）：
// - acks=all
// - retries=Integer.MAX_VALUE
// - max.in.flight.requests.per.connection=5

KafkaProducer<String, String> producer = new KafkaProducer<>(props);

// 正常使用即可，重复消息会自动去重
producer.send(new ProducerRecord<>("orders", "key1", "value1"));
```

### 约束（启用后自动生效）

```
1. acks 必须为 all
   props.put("acks", "all");

2. retries 必须大于 0
   props.put("retries", Integer.MAX_VALUE);

3. max.in.flight.requests.per.connection ≤ 5
   props.put("max.in.flight.requests.per.connection", 5);

⚠️ 如果手动设置违反以上约束，会抛 ConfigException
```

### 性能影响

```
启用幂等性 vs 不启用：

性能开销：
  ✅ 增加 ~5% CPU 开销（生成 PID + Sequence Number）
  ✅ 增加 ~10% 网络开销（请求包含 PID + seq）
  ❌ 不影响吞吐（Producer 端开销可忽略）

可靠性提升：
  ✅ 单 Producer 会话内消息不重复
  ✅ 自动去重（无需业务端去重逻辑）
  ✅ 与事务配合可实现精确一次语义
```

## 📊 幂等性的局限性

### 不能解决的场景

```
❌ Producer 重启场景
   - 新 Producer 实例分配新 PID
   - 旧会话的消息被新会话重发
   - 解决：使用事务（Transaction）

❌ 跨 Partition 幂等
   - 幂等性仅保证单 Partition 不重复
   - 跨 Partition 的去重需要事务

❌ Consumer 重平衡场景
   - Consumer 提交 offset 后崩溃
   - 重平衡后新 Consumer 重新消费
   - 解决：Consumer 端手动管理 offset + 幂等消费
```

### 业务端幂等

```java
// 即使有 Producer 幂等性，业务端仍需幂等设计
@Service
public class OrderService {
    
    @Autowired
    private KafkaProducer<String, OrderMessage> producer;
    
    public void createOrder(OrderMessage order) {
        // 1. 先检查数据库是否已处理（幂等检查）
        if (orderRepository.existsById(order.getOrderId())) {
            log.info("Order {} already processed", order.getOrderId());
            return;
        }
        
        // 2. 发送消息（启用幂等性，但仍可能重复）
        producer.send(new ProducerRecord<>("orders", order.getOrderId(), order));
    }
}

@Service
public class OrderConsumer {
    
    @KafkaListener(topics = "orders")
    public void consume(OrderMessage order) {
        // 1. 幂等检查（业务端去重）
        if (orderRepository.existsById(order.getOrderId())) {
            log.info("Order {} already processed", order.getOrderId());
            return;
        }
        
        // 2. 处理订单
        orderRepository.save(order);
    }
}
```

## 🔧 幂等性 vs 事务

| 维度 | 幂等性 | 事务 |
|------|--------|------|
| **作用范围** | 单 Partition | 多 Partition |
| **跨会话** | ❌ | ✅ |
| **原子性** | ❌ | ✅（多消息原子） |
| **性能开销** | 极低 | 中等 |
| **使用复杂度** | 简单 | 复杂 |
| **推荐场景** | 默认开启 | 跨 Partition 写入 |

## 🛠️ 实战：幂等发送完整示例

```java
public class IdempotentProducer {
    
    public static void main(String[] args) {
        // 1. 配置
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        
        KafkaProducer<String, String> producer = new KafkaProducer<>(props);
        
        // 2. 批量发送
        for (int i = 0; i < 100; i++) {
            final int seq = i;
            producer.send(new ProducerRecord<>("orders", "user" + (i % 10), "msg-" + i), 
                new Callback() {
                    @Override
                    public void onCompletion(RecordMetadata metadata, Exception exception) {
                        if (exception != null) {
                            System.err.println("Failed to send msg-" + seq + ": " + exception);
                        } else {
                            System.out.printf("Sent msg-%d → partition=%d offset=%d%n",
                                seq, metadata.partition(), metadata.offset());
                        }
                    }
                });
        }
        
        // 3. flush + close
        producer.flush();
        producer.close();
    }
}

// 即使发送过程中发生网络抖动、Leader 切换、Producer 重启等
// 单 Partition 内消息仍然不重复
```

## 📊 验证幂等性

### 测试用例

```java
// 验证 Producer 重试不导致重复
public class IdempotencyTest {
    
    @Test
    public void testNoDuplicatesWithRetries() {
        // 1. 启动 Producer
        // 2. 发送 1000 条消息
        // 3. 模拟网络中断（中断 ack 但允许消息到达）
        // 4. Producer 重试发送
        // 5. 验证：Consumer 收到的消息数 = 1000（无重复）
    }
}
```

### 监控指标

```java
// 监控幂等性相关指标
public class ProducerMetrics {
    
    // 幂等性相关指标
    double recordSendRate;                  // 发送速率
    double recordErrorRate;                 // 错误速率
    long recordRetryTotal;                  // 重试总次数
    long idempotentProducerErrorTotal;      // 幂等性错误
    long producerIdExpirationTotal;        // PID 过期
}
```

## 🔧 进阶：幂等性 + 幂等消费 = 完整去重

```
完整幂等保证：
  1. Producer 启用幂等性（不重复发送）
  2. Consumer 幂等消费（重复消息不重复处理）

业务端幂等消费实现：
  ✅ 数据库唯一索引（最简单）
  ✅ 乐观锁（version 字段）
  ✅ Redis SETNX（缓存去重）
  ✅ 业务状态机（避免重复状态变更）
```

```java
// 数据库唯一索引实现幂等消费
@Entity
@Table(name = "orders")
public class Order {
    @Id
    private String orderId;  // 主键（消息里的 orderId）
    // ... 其他字段
}

// 处理消息时：
@Service
public class OrderProcessor {
    @Autowired
    private OrderRepository orderRepository;
    
    @Transactional
    public void process(OrderMessage message) {
        // 利用主键冲突实现幂等
        try {
            orderRepository.save(new Order(message.getOrderId(), ...));
        } catch (DuplicateKeyException e) {
            // 主键冲突，说明已经处理过
            log.info("Order {} already processed", message.getOrderId());
        }
    }
}
```

## ⚠️ 常见问题

### 问题 1：PID 过期

```
报错：ProducerId expired
原因：Producer 闲置超过 transaction.timeout.ms（默认 7 天）
解决：
  1. 创建新 Producer 实例（自动分配新 PID）
  2. 调整 transaction.timeout.ms
```

### 问题 2：max.in.flight.requests 限制

```
报错：Invalid max.in.flight.requests.per.connection
解决：启用幂等性后必须 ≤ 5
  props.put("max.in.flight.requests.per.connection", 5);
```

### 问题 3：跨会话仍然重复

```
原因：Producer 重启分配新 PID
解决：
  1. 使用事务（Transaction）
  2. 业务端幂等设计
```

## 🎯 总结

**幂等性核心要点**：
- ✅ Kafka 0.11+ 内置幂等性（enable.idempotence=true）
- ✅ PID + Sequence Number 实现单 Partition 去重
- ✅ 推荐所有 Producer 默认开启
- ✅ 自动设置 acks=all + retries=MAX + max.in.flight ≤ 5
- ⚠️ 只能去重单会话、单 Partition
- ⚠️ 跨会话仍需业务端幂等或事务

**下一步：** [🔐 事务](/04-producer/transaction) — 跨 Partition 原子操作
