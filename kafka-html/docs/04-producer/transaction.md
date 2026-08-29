---
title: 事务
date: 2026-08-15  # date-auto-injected
---

# 🔐 事务

> Kafka 0.11+ 引入**事务（Transaction）**机制，实现**跨 Partition、跨 Topic 的精确一次语义（Exactly Once Semantics, EOS）**。事务是幂等性的超集。

## 🎯 为什么需要事务？

```
幂等性的局限：
  ✅ 单 Producer 会话、单 Partition 内不重复
  ❌ 跨 Partition 不能保证原子性
  ❌ Producer 重启（跨会话）不能保证

事务的解决方案：
  ✅ 跨 Partition / Topic 原子写入（要么全部成功，要么全部失败）
  ✅ 跨会话幂等（PID 持久化）
  ✅ 配合 Consumer 实现端到端精确一次
```

### 应用场景

```
场景 1：转账（A 账户 -100，B 账户 +100）
  - 写入 2 个 Topic
  - 必须原子（A 减了 B 没加 = 数据不一致）

场景 2：订单处理（订单 + 库存 + 支付）
  - 写入 3 个 Topic
  - 必须原子（订单创建了库存没扣 = 超卖）

场景 3：CDC（数据库变更同步）
  - 多张表的变更打包发送
  - 必须原子（要么都成功，要么都失败）
```

## 🎯 事务原理

### 事务协调者（Transaction Coordinator）

```
每个 Producer 的事务由 Transaction Coordinator 管理：
  - Coordinator 由 broker 担任（hash(transactional.id) % partitions 决定）
  - 维护事务状态（persistent in __transaction_state topic）
  - 控制事务的两阶段提交
```

### 事务 ID 与状态

```
Producer 启动事务时：
  1. 向 Coordinator 申请 transactional.id 对应的 PID
  2. 接收事务状态（是否需要回滚、是否初始化）
  3. 开始事务

事务过程：
  1. 写入消息到 Partition（标记为未提交）
  2. 提交事务（写入 commit marker）
  3. Broker 标记所有消息为已提交

事务中断：
  1. 写入 abort marker
  2. Broker 标记所有消息为已中止
```

## 📊 事务流程

```
Producer 开启事务
  ↓
[Begin Transaction]
  ↓
调用 send() 发送消息到多个 Partition/Topic
  ↓
[消息写入，但标记为 "未提交"]
  - Consumer 看不到（read_uncommitted 模式）
  - Consumer 看得到（read_committed 模式但需等 marker）
  ↓
调用 commitTransaction() 或 abortTransaction()
  ↓
[Commit Transaction]
  - Coordinator 写入 commit marker
  - 消息变为 "已提交"
  - Consumer（read_committed）可以消费
  ↓
或 [Abort Transaction]
  - Coordinator 写入 abort marker
  - 消息被标记为废弃
  - Consumer 不会消费
```

## 🔧 使用 Kafka 事务

### Java 代码

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

// 1. 必须设置 transactional.id（每个实例唯一）
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "my-transactional-id");

// 2. 启用幂等性（事务包含幂等性，但需显式开启）
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);

KafkaProducer<String, String> producer = new KafkaProducer<>(props);

// 3. 初始化事务（只能调用一次）
producer.initTransactions();

// 4. 业务逻辑
try {
    // 4.1 开启事务
    producer.beginTransaction();
    
    // 4.2 发送多条消息
    producer.send(new ProducerRecord<>("account-a", "transfer-001", "-100"));
    producer.send(new ProducerRecord<>("account-b", "transfer-001", "+100"));
    producer.send(new ProducerRecord<>("audit-log", "transfer-001", "success"));
    
    // 4.3 提交事务
    producer.commitTransaction();
    
} catch (Exception e) {
    // 4.4 回滚事务
    producer.abortTransaction();
    
    // 业务处理
    log.error("Transaction failed", e);
}
```

### 完整示例：转账

```java
public class TransferService {
    
    @Autowired
    private KafkaProducer<String, String> producer;
    
    public void transfer(String fromAccount, String toAccount, int amount) {
        try {
            producer.beginTransaction();
            
            // 扣减 A 账户
            producer.send(new ProducerRecord<>(
                "account-events", fromAccount, 
                String.format("{\"account\":\"%s\",\"delta\":%d,\"ts\":%d}", 
                    fromAccount, -amount, System.currentTimeMillis())
            ));
            
            // 增加 B 账户
            producer.send(new ProducerRecord<>(
                "account-events", toAccount, 
                String.format("{\"account\":\"%s\",\"delta\":%d,\"ts\":%d}", 
                    toAccount, amount, System.currentTimeMillis())
            ));
            
            // 写审计日志
            producer.send(new ProducerRecord<>(
                "audit-logs", "transfer", 
                String.format("{\"from\":\"%s\",\"to\":\"%s\",\"amount\":%d}", 
                    fromAccount, toAccount, amount)
            ));
            
            // 提交事务
            producer.commitTransaction();
            
            log.info("Transfer committed");
            
        } catch (Exception e) {
            // 回滚事务
            producer.abortTransaction();
            log.error("Transfer aborted", e);
            throw new RuntimeException("Transfer failed", e);
        }
    }
}
```

## 📊 Consumer 端事务支持

### 读取级别

```java
// Consumer 配置：只读取已提交的消息
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");

// 配置：读取所有消息（包括未提交）
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_uncommitted");
```

### 行为对比

| 隔离级别 | 行为 | 性能 |
|---------|------|------|
| `read_uncommitted` | 读取所有消息（默认） | 高 |
| `read_committed` | 只读取已提交消息（跳过未提交和已中止） | 略低 |

```
⚠️ read_committed 模式：
  - 不读取 abort 的消息
  - 不读取尚未 commit 的消息
  - 必须等 commit marker 才返回后续消息
  - 增加少量延迟（毫秒级）
```

### Consumer 端精确一次

```java
// 1. 关闭自动提交 offset
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);

// 2. 设置隔离级别
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");

// 3. 使用 ConsumerSeekAware + 事务 API
consumer.subscribe(topics);
while (running) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    try {
        // 4. 在事务中处理消息 + 提交 offset
        producer.beginTransaction();
        
        for (ConsumerRecord<String, String> record : records) {
            // 业务处理
            processMessage(record);
            // 发送处理结果到下游 Topic
            producer.send(new ProducerRecord<>("processed", record.key(), record.value()));
        }
        
        // 5. 提交事务（消息处理 + offset 提交 + 下游消息发送，全部原子）
        producer.sendOffsetsToTransaction(offsets, consumerGroupId);
        producer.commitTransaction();
        
    } catch (Exception e) {
        producer.abortTransaction();
    }
}
```

## 📊 事务配置详解

```properties
# ==== 必填 ====
transactional.id=my-unique-id           # 事务 ID（全局唯一）
enable.idempotence=true                  # 自动开启

# ==== 超时（可选） ====
transaction.timeout.ms=60000            # 事务超时（默认 60s）
# 超过这个时间未提交的事务会被 Coordinator 自动中止

# ==== 限制（自动设置） ====
acks=all
retries=Integer.MAX_VALUE
max.in.flight.requests.per.connection=5
```

### 事务 ID 设计

```java
// transactional.id 的设计原则：
// 1. 全局唯一（不同 Producer 实例必须不同）
// 2. 稳定（重启后保持不变）
// 3. 有业务含义（推荐）

// 示例 1：按业务 + 实例命名
transactional.id = "order-service-pod-1"

// 示例 2：UUID（推荐，简单）
transactional.id = UUID.randomUUID().toString()

// 示例 3：使用 hostname + pid（适合单体应用）
transactional.id = hostname + "-" + pid
```

⚠️ **重要**：相同的 transactional.id 共享同一个 PID，用于跨会话去重（事务恢复）

### 事务恢复

```
场景：Producer 崩溃后重启

机制：
  - transactional.id 保持不变
  - Coordinator 恢复未完成的事务
  - 如果事务是 ONGOING，Producer 需要决定提交或回滚

配置：
  - transaction.timeout.ms：事务超时（默认 60s）
  - 超过超时未完成的事务自动中止
```

```java
// Producer 崩溃恢复
producer = new KafkaProducer<>(props);
producer.initTransactions();
// 自动检查是否有未完成事务
// 如果有，会抛 ProducerFencedException 或类似异常
// 业务决定是 commitTransaction() 还是 abortTransaction()
```

## 📊 事务性能

```
性能开销（vs 不启用事务）：
  ✅ 增加 ~20% 延迟（commit marker 同步）
  ✅ 增加 ~10% 吞吐量下降（事务状态写入）
  ❌ 单 Partition 内消息不重复
  ✅ 跨 Partition 原子写入

适用场景：
  ✅ 跨 Partition 写入（如转账、订单）
  ✅ 需要 Exactly Once 的场景
  ❌ 单 Partition 简单场景（用幂等性就够了）
```

## 🛠️ 实战：Consumer + Producer 事务（端到端 EOS）

```java
@Service
public class OrderProcessor {
    
    @Autowired
    private KafkaProducer<String, String> producer;
    
    public void process() {
        // 1. Consumer 配置
        Properties consumerProps = new Properties();
        consumerProps.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        consumerProps.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processor");
        consumerProps.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        consumerProps.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
        
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(consumerProps);
        consumer.subscribe(Arrays.asList("orders"));
        
        // 2. Producer 事务配置
        Properties producerProps = new Properties();
        producerProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        producerProps.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "order-processor-tx");
        producerProps.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        
        KafkaProducer<String, String> producer = new KafkaProducer<>(producerProps);
        producer.initTransactions();
        
        // 3. 消费 + 处理 + 写入下游（事务）
        try {
            while (running) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                
                if (records.isEmpty()) continue;
                
                Map<TopicPartition, OffsetAndMetadata> offsetsToCommit = new HashMap<>();
                
                // 4. 开启事务
                producer.beginTransaction();
                
                for (ConsumerRecord<String, String> record : records) {
                    // 5. 处理消息
                    processOrder(record);
                    
                    // 6. 写入下游 Topic
                    producer.send(new ProducerRecord<>("processed-orders", record.key(), "processed-" + record.value()));
                    
                    // 7. 记录 offset
                    offsetsToCommit.put(
                        new TopicPartition(record.topic(), record.partition()),
                        new OffsetAndMetadata(record.offset() + 1)
                    );
                }
                
                // 8. 提交 offset（与业务消息原子提交）
                producer.sendOffsetsToTransaction(offsetsToCommit, consumer.groupMetadata());
                
                // 9. 提交事务
                producer.commitTransaction();
                
            }
        } catch (Exception e) {
            // 10. 回滚事务
            producer.abortTransaction();
            log.error("Processing failed", e);
        }
    }
}
```

## ⚠️ 常见问题

### 问题 1：事务超时

```
报错：TransactionTimedOut
原因：事务执行时间超过 transaction.timeout.ms
解决：
  1. 增加超时：transaction.timeout.ms=120000
  2. 优化事务内逻辑（减少操作时间）
  3. 拆分大事务为小事务
```

### 问题 2：ProducerFenced

```
报错：ProducerFencedException
原因：相同 transactional.id 的旧 Producer 还在运行
解决：
  1. 关闭旧 Producer
  2. 等待旧 Producer 的事务超时
  3. 使用不同的 transactional.id
```

### 问题 3：事务提交慢

```
原因：commit marker 需要写入所有涉及的 partition
解决：
  1. 减少事务涉及 partition 数量
  2. 启用事务压缩
  3. 增加 Broker 网络带宽
```

## 🎯 总结

**事务核心要点**：
- ✅ 跨 Partition 原子操作
- ✅ transactional.id 全局唯一
- ✅ 事务必须配合幂等性使用
- ✅ Consumer 设置 read_committed 只读已提交
- ✅ sendOffsetsToTransaction 实现端到端 EOS
- ⚠️ 性能比幂等性差（增加延迟）
- ⚠️ 事务超时需合理设置

**下一步：** [📊 顺序保证](/04-producer/order) — Kafka 顺序保证实战
