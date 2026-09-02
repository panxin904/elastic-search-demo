---
title: Exactly Once 实现
date: 2026-08-15  # date-auto-injected
---

# 🎯 Exactly Once 实现

> **Exactly Once 语义（EOS）**是消息系统的最高可靠性保证。Kafka 通过**幂等性 + 事务**实现 EOS。

## 🎯 什么是 Exactly Once？

```
3 种消息传递语义：

1. At Most Once（最多一次）
   - 消息可能丢
   - 不可能重复
   - acks=0 + 自动提交

2. At Least Once（至少一次，默认）
   - 消息不可能丢
   - 可能重复
   - acks=all + 手动提交

3. Exactly Once（精确一次）
   - 消息不可能丢
   - 不可能重复
   - acks=all + 幂等性 + 事务
```

![Kafka 事务与幂等性原理](/kafka-transaction-idempotent.svg)

## 📊 EOS 实现的三层保障

```
Layer 1: 幂等性（Idempotence）
  - Producer 单会话内不重复
  - PID + Sequence Number

Layer 2: 事务（Transaction）
  - 跨 Partition 原子写入
  - 跨会话幂等
  - 跨系统协调（DB + Kafka）

Layer 3: 读已提交（read_committed）
  - Consumer 只读已提交消息
  - 跳过未提交和已中止消息
```

## 🔧 Layer 1：幂等性

### 原理

```
Producer 启动时：
  1. Broker 分配唯一 PID（Producer ID）
  2. PID + Partition 维护 Sequence Number

每次发送：
  - Producer 在消息中携带 (PID, partition, seq)
  - Broker 收到后检查 seq 是否连续
  - 如果是重复消息（seq ≤ 已收到），直接丢弃

示例：
  Producer PID=12345
    消息1: (PID=12345, partition=0, seq=0) → 接受
    消息2: (PID=12345, partition=0, seq=1) → 接受
    消息3: (PID=12345, partition=0, seq=2) → 接受
    重试消息3: (PID=12345, partition=0, seq=2) → 丢弃（重复）
```

### 配置

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);

// 启用幂等性后自动设置：
// - acks=all
// - retries=Integer.MAX_VALUE
// - max.in.flight.requests.per.connection=5
```

### 幂等性的局限

```
❌ 只能去重单会话（Producer 实例）
❌ 只能去重单 Partition（不同 Partition 独立计数）
✅ 跨 Partition 需用事务
```

## 🔧 Layer 2：事务

### 原理

```
事务流程：
  1. 开启事务（beginTransaction）
  2. 发送消息（不立即对 Consumer 可见）
  3. 提交事务（commitTransaction）→ 消息可见
     或中止事务（abortTransaction）→ 消息被丢弃

Broker 处理：
  - 收到消息时标记为 "未提交"
  - 事务提交时写入 commit marker
  - Consumer 设置 read_committed 只读已提交
```

### 配置

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "my-tx-id");  // 必须设置
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
producer.initTransactions();  // 初始化事务

// 事务使用
try {
    producer.beginTransaction();
    producer.send(new ProducerRecord<>("topic1", "key1", "value1"));
    producer.send(new ProducerRecord<>("topic2", "key2", "value2"));
    producer.commitTransaction();  // 原子提交
} catch (Exception e) {
    producer.abortTransaction();  // 中止事务
}
```

### 事务 + Consumer Offset

```java
// sendOffsetsToTransaction：原子提交 Offset + 业务消息

public void consumeAndProduce(ConsumerRecord<String, String> record, Consumer<?, ?> consumer) {
    producer.beginTransaction();
    
    try {
        // 1. 业务处理
        processMessage(record);
        
        // 2. 发送下游消息
        producer.send(new ProducerRecord<>("processed", record.key(), record.value()));
        
        // 3. 提交 Offset（与下游消息原子）
        Map<TopicPartition, OffsetAndMetadata> offsets = Map.of(
            new TopicPartition(record.topic(), record.partition()),
            new OffsetAndMetadata(record.offset() + 1)
        );
        producer.sendOffsetsToTransaction(offsets, consumer.groupMetadata());
        
        // 4. 提交事务
        producer.commitTransaction();
    } catch (Exception e) {
        producer.abortTransaction();
        throw e;
    }
}
```

### 事务的局限

```
❌ 性能开销：相比非事务，吞吐降低 20-50%
✅ 跨 Partition 原子
✅ 跨会话幂等
```

## 🔧 Layer 3：read_committed

### 原理

```
Consumer 配置 isolation.level=read_committed：
  - 只读取已 commit 的消息
  - 跳过未 commit 的消息
  - 跳过 abort 的消息

Broker 处理：
  - 事务提交时写入 commit marker
  - Consumer 拉到 commit marker 后才返回该 Partition 的消息
  - abort 的消息会被跳过
```

### 配置

```properties
# Consumer 配置
isolation.level=read_committed       # 默认 read_uncommitted
auto.offset.reset=earliest
```

### read_committed vs read_uncommitted

| 模式 | 行为 | 性能 |
|------|------|------|
| read_committed | 只读已提交 | 略低（需等 commit marker） |
| read_uncommitted | 读所有消息（含未提交） | 高 |

## 🔧 实战：端到端 EOS

### 完整代码

```java
@Service
public class ExactlyOnceProcessor {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    public void processAndSend(ConsumerRecord<String, String> record, Acknowledgment ack) {
        kafkaTemplate.executeInTransaction(operations -> {
            try {
                // 1. 业务处理（带幂等）
                String orderId = handleBusinessLogic(record);
                
                // 2. 发送到下游 Topic
                operations.send("processed-orders", orderId, "processed");
                
                // 3. 提交 Offset（与下游消息原子）
                Map<TopicPartition, OffsetAndMetadata> offsets = Map.of(
                    new TopicPartition(record.topic(), record.partition()),
                    new OffsetAndMetadata(record.offset() + 1)
                );
                operations.sendOffsetsToTransaction(offsets, consumer.groupMetadata());
                
                // 事务自动提交（无异常时）
            } catch (Exception e) {
                throw e;  // 触发事务回滚
            }
            return null;
        });
        
        // 事务提交后 ack（保险起见）
        ack.acknowledge();
    }
    
    private String handleBusinessLogic(ConsumerRecord<String, String> record) {
        // 业务幂等（Redis SETNX 或 DB 唯一约束）
        String orderId = record.key();
        Boolean firstTime = redisTemplate.opsForValue()
            .setIfAbsent("processed:" + orderId, "1", 24, TimeUnit.HOURS);
        if (!Boolean.TRUE.equals(firstTime)) {
            return orderId;  // 已处理过
        }
        // 实际业务处理
        orderService.process(record.value());
        return orderId;
    }
}
```

### Consumer 配置

```java
@KafkaListener(
    topics = "orders",
    groupId = "order-processor",
    containerFactory = "eosListenerFactory"
)
public void consume(ConsumerRecord<String, String> record, Acknowledgment ack) {
    exactlyOnceProcessor.processAndSend(record, ack);
}

@Configuration
public class KafkaConfig {
    
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> eosListenerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, String> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(eosConsumerFactory());
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL);
        return factory;
    }
    
    @Bean
    public ConsumerFactory<String, String> eosConsumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processor");
        props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        return new DefaultKafkaConsumerFactory<>(props);
    }
}
```

## 🔧 EOS 性能影响

```
测试场景：单 Partition，1KB 消息

配置：                  吞吐        延迟
无 EOS                  200 MB/s    1-5 ms
仅幂等性                180 MB/s    2-10 ms（性能损失 10%）
事务 + EOS               100 MB/s    10-50 ms（性能损失 50%）

结论：
  - 幂等性：性能影响小，强烈推荐
  - 事务：性能影响大，按需使用
```

## 🔧 EOS 适用场景

### 必须用 EOS

```
✅ 金融交易（支付、转账）
✅ 库存扣减（避免超卖）
✅ 订单状态变更（避免状态错乱）
✅ 关键业务消息
```

### 可选 EOS（业务幂等代替）

```
⚠️ 日志收集（丢失少量无所谓）
⚠️ 用户行为（重复处理可容忍）
⚠️ 通知推送（业务幂等通过其他方式保证）
```

## 🔧 EOS 调优

```properties
# Producer 端
transactional.id=unique-id          # 唯一事务 ID
transaction.timeout.ms=60000        # 事务超时
enable.idempotence=true             # 幂等性
acks=all                            # 所有副本确认

# Consumer 端
isolation.level=read_committed     # 只读已提交
enable.auto.commit=false            # 手动提交
```

## 🔧 EOS 故障恢复

### Producer 崩溃

```
场景：事务进行中 Producer 崩溃

恢复：
  - 启动新的 Producer（同 transactional.id）
  - initTransactions() 会检查未完成事务
  - 决定 commit 或 abort（取决于业务状态）

⚠️ 事务 ID 必须保持不变
   - 通常基于 hostname + 业务标识
   - 或基于 ZooKeeper 唯一序列
```

### Broker 崩溃

```
场景：事务提交时 Broker 崩溃

恢复：
  - Controller 选举新 Leader
  - 从 Raft Log 恢复事务状态
  - 已提交事务的消息对 Consumer 可见

Kafka 自动处理：
  - Controller 通过 KRaft 恢复
  - Consumer 通过 read_committed 过滤
```

## 🔧 EOS vs 业务幂等

```
EOS：
  ✅ Kafka 内置保证
  ✅ 跨 Partition 原子
  ❌ 性能开销
  ❌ 与外部系统（如 DB）协调复杂

业务幂等：
  ✅ 性能无开销
  ✅ 与外部系统天然集成（DB 唯一约束）
  ❌ 需要业务实现
  ❌ 跨服务一致性需额外处理

推荐：
  ✅ 单一服务内：用 EOS（简单）
  ✅ 跨服务：用业务幂等 + Outbox Pattern
```

## 🔧 EOS 实战：转账场景

### 需求

```
用户 A 转账 100 元给用户 B：
  1. A 账户减 100
  2. B 账户加 100
  3. 发送通知消息
  
要求：要么全成功，要么全失败（不丢钱）
```

### 实现

```java
@Service
public class TransferService {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    public void transfer(String from, String to, int amount) {
        kafkaTemplate.executeInTransaction(operations -> {
            // 1. 发送 A 账户扣款事件
            operations.send("account-events", from, 
                "{\"account\":\"" + from + "\",\"delta\":-" + amount + "}");
            
            // 2. 发送 B 账户加款事件
            operations.send("account-events", to, 
                "{\"account\":\"" + to + "\",\"delta\":+" + amount + "}");
            
            // 3. 发送通知
            operations.send("notifications", "transfer",
                "{\"from\":\"" + from + "\",\"to\":\"" + to + "\",\"amount\":" + amount + "}");
            
            return null;
            // 事务自动提交（三者原子）
        });
    }
}

// A 账户消费
@KafkaListener(topics = "account-events", groupId = "account-A-consumer")
public void consumeA(String message) {
    AccountEvent event = parse(message);
    accountService.deduct(event.getAccount(), event.getDelta());  // 扣款
}

// B 账户消费
@KafkaListener(topics = "account-events", groupId = "account-B-consumer")
public void consumeB(String message) {
    AccountEvent event = parse(message);
    accountService.add(event.getAccount(), event.getDelta());  // 加款
}
```

**EOS 保证**：
- ✅ 三个消息原子发送（要么都成功，要么都失败）
- ✅ Consumer 只读已提交消息
- ✅ 不会出现 "扣了 A 但没加 B"

## ⚠️ 常见误区

### 误区 1：幂等性等于 EOS

```
❌ 错误认知
✅ 幂等性只是 EOS 的一部分
   - 幂等性：防止重复发送
   - 事务：跨 Partition 原子
   - read_committed：只读已提交
   - 三者结合才是完整 EOS
```

### 误区 2：EOS 完全无重复

```
⚠️ 即使有 EOS，仍可能重复：
   - 事务提交后，但 Producer ack 未到达
   - Consumer 处理后，但 Offset 未提交
   - 网络分区恢复后的重复处理

✅ 业务端幂等仍是基础
```

### 误区 3：EOS 没有性能影响

```
❌ 错误认知
✅ 事务有性能开销（20-50%）
   - 需协调 Controller
   - 需写 commit marker
   - Consumer 需等待 marker
```

## 🎯 总结

**Exactly Once 实现核心要点**：
- ✅ 三层保障：幂等性 + 事务 + read_committed
- ✅ 幂等性：单会话单 Partition 去重
- ✅ 事务：跨 Partition 原子写入
- ✅ read_committed：Consumer 只读已提交
- ✅ 事务 + sendOffsetsToTransaction 实现端到端 EOS
- ⚠️ 事务有性能开销（20-50%）
- ⚠️ EOS 不替代业务幂等
- ⚠️ 跨服务一致仍需 Outbox Pattern

**下一步：** [🚀 Kafka 为什么快](/10-interview/why-fast) — 性能深度剖析
