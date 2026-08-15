---
title: 手动提交
---

# ✋ 手动提交

> 手动提交 Offset 是**精确控制消息消费时机**的关键。本章详解各种手动提交策略及实战。

## 🎯 为什么需要手动提交？

```
自动提交的问题：
  ✅ 简单
  ❌ 消息可能丢失（处理前提交）
  ❌ 消息可能重复（处理后崩溃但提交失败）

手动提交的优势：
  ✅ 精确控制提交时机（处理完才提交）
  ✅ 配合业务幂等性实现 At Least Once
  ✅ 配合事务实现 Exactly Once
```

## 🔄 commitSync vs commitAsync

### commitSync（同步提交）

```java
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));

try {
    while (running) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        
        for (ConsumerRecord<String, String> record : records) {
            processOrder(record);
        }
        
        // 同步提交（阻塞直到成功或失败）
        consumer.commitSync();
    }
} finally {
    try {
        consumer.commitSync();  // 最后兜底
    } finally {
        consumer.close();
    }
}
```

**行为**：
- 阻塞调用线程
- 提交成功才返回
- 提交失败抛异常（程序可见）
- 默认重试直到成功（直到 session.timeout.ms）

**适用场景**：
- 关键业务（必须确保提交成功）
- 低吞吐场景
- 关闭前必须提交

### commitAsync（异步提交）

```java
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));

try {
    while (running) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        
        for (ConsumerRecord<String, String> record : records) {
            processOrder(record);
        }
        
        // 异步提交（非阻塞）
        consumer.commitAsync((offsets, exception) -> {
            if (exception != null) {
                log.error("Commit failed for offsets: {}", offsets, exception);
                // 重试或告警
            } else {
                log.debug("Committed offsets: {}", offsets);
            }
        });
    }
} finally {
    try {
        consumer.commitSync();  // 最后同步提交（确保关闭前提交）
    } finally {
        consumer.close();
    }
}
```

**行为**：
- 立即返回（不阻塞）
- 失败调用回调（程序可见）
- 不会重试（单次提交）

**适用场景**：
- 高吞吐场景
- 不要求严格保证提交
- 可接受少量消息重复

### 对比

| 维度 | commitSync | commitAsync |
|------|------------|-------------|
| 阻塞 | ✅ 是 | ❌ 否 |
| 重试 | ✅ 自动 | ❌ 否 |
| 失败回调 | 抛异常 | 回调函数 |
| 性能 | 较慢 | 较快 |
| 适用 | 关键业务 | 高吞吐 |

## 📊 三种提交策略

### 策略 1：批量处理 + 同步提交

```java
KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));

while (running) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    
    if (records.isEmpty()) continue;
    
    // 1. 批量处理
    for (ConsumerRecord<String, String> record : records) {
        processOrder(record);
    }
    
    // 2. 整批处理完，提交
    consumer.commitSync();
}

// 特点：简单、可靠、有少量消息重复风险
// 适用：业务幂等、吞吐适中
```

### 策略 2：逐条处理 + 异步提交

```java
KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));

while (running) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    
    for (ConsumerRecord<String, String> record : records) {
        processOrder(record);
        // 每处理一条，异步提交
        Map<TopicPartition, OffsetAndMetadata> offset = Map.of(
            new TopicPartition(record.topic(), record.partition()),
            new OffsetAndMetadata(record.offset() + 1)
        );
        consumer.commitAsync(offset, (offsets, exception) -> {
            if (exception != null) {
                log.error("Commit failed: {}", offsets, exception);
            }
        });
    }
}

// 特点：低延迟、可能丢提交、可能重复
// 适用：高频小消息、可容忍重复
```

### 策略 3：批量处理 + 指定 Offset 提交

```java
KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));

Map<TopicPartition, OffsetAndMetadata> offsetsToCommit = new HashMap<>();

while (running) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    
    for (ConsumerRecord<String, String> record : records) {
        try {
            processOrder(record);
            // 记录每条记录的 Offset
            offsetsToCommit.put(
                new TopicPartition(record.topic(), record.partition()),
                new OffsetAndMetadata(record.offset() + 1)
            );
        } catch (Exception e) {
            // 处理失败，不更新 Offset（下次重新消费）
            offsetsToCommit.remove(new TopicPartition(record.topic(), record.partition()));
            log.error("Process failed", e);
        }
    }
    
    // 提交本批次的所有 Offset
    if (!offsetsToCommit.isEmpty()) {
        consumer.commitSync(offsetsToCommit);
        offsetsToCommit.clear();
    }
}

// 特点：精确控制每条 Offset
// 适用：业务重要、需精确语义
```

## 🛠️ 实战：批量提交策略

```java
public class BatchCommitConsumer {
    
    private final KafkaConsumer<String, String> consumer;
    private final int batchSize = 100;
    private final Duration commitInterval = Duration.ofSeconds(5);
    private long lastCommitTime = System.currentTimeMillis();
    
    public void consume() {
        consumer.subscribe(Arrays.asList("orders"));
        
        Map<TopicPartition, OffsetAndMetadata> offsetsToCommit = new HashMap<>();
        List<ConsumerRecord<String, String>> batch = new ArrayList<>();
        
        while (running) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            
            for (ConsumerRecord<String, String> record : records) {
                batch.add(record);
                
                // 触发条件 1：达到 batch size
                if (batch.size() >= batchSize) {
                    processBatch(batch, offsetsToCommit);
                    commitOffsets(offsetsToCommit);
                    batch.clear();
                    offsetsToCommit.clear();
                    lastCommitTime = System.currentTimeMillis();
                }
            }
            
            // 触发条件 2：超过 commit interval
            if (!batch.isEmpty() && 
                System.currentTimeMillis() - lastCommitTime > commitInterval.toMillis()) {
                processBatch(batch, offsetsToCommit);
                commitOffsets(offsetsToCommit);
                batch.clear();
                offsetsToCommit.clear();
                lastCommitTime = System.currentTimeMillis();
            }
        }
    }
    
    private void processBatch(List<ConsumerRecord<String, String>> batch,
                              Map<TopicPartition, OffsetAndMetadata> offsetsToCommit) {
        for (ConsumerRecord<String, String> record : batch) {
            try {
                processOrder(record);
                
                // 记录 Offset
                offsetsToCommit.put(
                    new TopicPartition(record.topic(), record.partition()),
                    new OffsetAndMetadata(record.offset() + 1)
                );
            } catch (Exception e) {
                // 单条失败不影响整体
                log.error("Process failed at offset {}", record.offset(), e);
                // 不更新 Offset，下次重新消费（依赖业务幂等）
            }
        }
    }
    
    private void commitOffsets(Map<TopicPartition, OffsetAndMetadata> offsets) {
        try {
            consumer.commitSync(offsets);
            log.debug("Committed offsets: {}", offsets);
        } catch (Exception e) {
            log.error("Commit failed", e);
            // 告警或重试
        }
    }
}
```

## 🔧 实战：精确一次（事务 + commitSync）

```java
public class ExactlyOnceConsumer {
    
    private final KafkaConsumer<String, String> consumer;
    private final KafkaProducer<String, String> producer;
    
    public void consume() {
        // Consumer 配置
        Properties consumerProps = new Properties();
        consumerProps.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
        consumerProps.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        
        // Producer 配置（事务）
        Properties producerProps = new Properties();
        producerProps.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "tx-1");
        producerProps.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        
        consumer.subscribe(Arrays.asList("orders"));
        producer.initTransactions();
        
        try {
            while (running) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                
                if (records.isEmpty()) continue;
                
                Map<TopicPartition, OffsetAndMetadata> offsetsToCommit = new HashMap<>();
                
                // 1. 开启事务
                producer.beginTransaction();
                
                try {
                    for (ConsumerRecord<String, String> record : records) {
                        // 2. 处理业务
                        processOrder(record);
                        
                        // 3. 发送到下游
                        producer.send(new ProducerRecord<>("processed", record.key(), record.value()));
                        
                        // 4. 累积 Offset
                        offsetsToCommit.put(
                            new TopicPartition(record.topic(), record.partition()),
                            new OffsetAndMetadata(record.offset() + 1)
                        );
                    }
                    
                    // 5. 提交 Offset（与下游消息原子）
                    producer.sendOffsetsToTransaction(offsetsToCommit, consumer.groupMetadata());
                    
                    // 6. 提交事务（业务处理 + 下游消息 + Offset 提交，三者原子）
                    producer.commitTransaction();
                    
                } catch (Exception e) {
                    // 7. 回滚事务（业务处理、下游消息、Offset 全部回滚）
                    producer.abortTransaction();
                    log.error("Transaction aborted", e);
                }
            }
        } finally {
            producer.close();
            consumer.close();
        }
    }
}
```

## 📊 异常处理

### CommitFailedException

```java
try {
    consumer.commitSync();
} catch (CommitFailedException e) {
    log.error("Commit failed", e);
    // 可能原因：
    // 1. session.timeout.ms 内未提交，Group 已 Rebalance
    // 2. Offset 已过期
    // 3. Broker 不可用
    
    // 处理：
    // 1. 重新订阅（触发 Rebalance）
    // 2. 从最新 Offset 重新消费
    // 3. 告警
}
```

### WakeupException

```java
consumer.wakeup();  // 触发 WakeupException，用于优雅关闭

try {
    while (running) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        // ...
    }
} catch (WakeupException e) {
    // 优雅关闭
    log.info("Wakeup triggered, closing consumer");
} finally {
    try {
        consumer.commitSync();
    } finally {
        consumer.close();
    }
}
```

## 🔧 实战：生产级 Offset 管理

```java
public class ProductionOffsetManager {
    
    // 异步提交 + 错误回调
    private final KafkaConsumer<String, String> consumer;
    private final AtomicReference<Throwable> commitError = new AtomicReference<>();
    
    public void start() {
        consumer.subscribe(Arrays.asList("orders"));
        
        while (running) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            
            for (ConsumerRecord<String, String> record : records) {
                processOrder(record);
            }
            
            // 异步提交
            consumer.commitAsync((offsets, exception) -> {
                if (exception != null) {
                    log.error("Commit failed", exception);
                    commitError.set(exception);
                }
            });
            
            // 检查是否有未处理的提交错误
            if (commitError.get() != null) {
                Throwable ex = commitError.getAndSet(null);
                // 同步重试提交
                try {
                    consumer.commitSync();
                    log.info("Recovered from commit error");
                } catch (Exception e) {
                    log.error("Sync commit failed", e);
                    // 重新订阅
                    consumer.subscribe(Arrays.asList("orders"));
                }
            }
        }
    }
    
    private void processOrder(ConsumerRecord<String, String> record) {
        // 业务处理（应幂等）
    }
}
```

## ⚠️ 常见问题

### 问题 1：commitSync 阻塞严重

```
原因：提交慢导致 Consumer 卡住
解决：
  1. 改用 commitAsync
  2. 减少提交频率（批量提交）
  3. 检查网络和 Broker 健康
```

### 问题 2：commitAsync 提交失败丢失 Offset

```
原因：commitAsync 失败后没有同步兜底
解决：
  1. 关闭时强制 commitSync
  2. 错误告警 + 重试
  3. 业务端幂等
```

### 问题 3：重复消费

```
原因：commitSync 失败但 Consumer 没感知
解决：
  1. 业务端幂等设计
  2. 数据库唯一约束
  3. Redis SETNX
```

## 🎯 总结

**手动提交核心要点**：
- ✅ commitSync 阻塞但可靠
- ✅ commitAsync 非阻塞但可能丢提交
- ✅ 推荐组合：异步提交 + 关闭时同步提交
- ✅ 指定 Offset 提交实现精确控制
- ✅ 事务 + commitSync 实现精确一次
- ⚠️ 业务幂等是手动提交的基础
- ⚠️ 关闭前必须 commitSync

**下一步：** [🧵 多线程消费](/05-consumer/multi-thread) — 高并发消费模式
