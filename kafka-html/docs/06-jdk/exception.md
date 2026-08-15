---
title: 异常处理
---

# 🚨 异常处理

> Kafka 客户端会抛出各种异常，理解异常类型和处理方式对**生产稳定性**至关重要。

## 🎯 异常分类

### 异常层级

```
KafkaException (基类)
├── ConfigException                配置错误
├── SerializationException          序列化错误
├── ProducerFencedException         事务边界错误
├── TimeoutException                超时
├── InterruptedException            阻塞中断
├── AuthenticationException         认证失败
├── AuthorizationException          授权失败
├── InvalidConfigurationException   无效配置
├── InvalidTopicException           无效 Topic
├── RecordTooLargeException         消息过大
├── OffsetOutOfRangeException      Offset 越界
├── CommitFailedException           提交失败
├── WakeupException                 唤醒异常
├── RebalanceInProgressException    Rebalance 进行中
└── RetriableException (接口)
    ├── NetworkException              网络错误（可重试）
    ├── NotLeaderForPartitionException Leader 切换
    ├── UnknownTopicOrPartitionException  Topic/Partition 不存在
    └── RequestTimedOutException      请求超时
```

### 可重试 vs 不可重试

```java
// RetriableException 接口
public interface RetriableException { }

// Kafka 会自动重试（基于 retries 配置）

// 不可重试异常
- SerializationException     // 序列化错误（重试也无用）
- RecordTooLargeException    // 消息过大
- AuthenticationException   // 认证失败
- AuthorizationException     // 授权失败
- ConfigException            // 配置错误
```

## 📊 Producer 异常

### 异常处理模式

```java
producer.send(record, new Callback() {
    @Override
    public void onCompletion(RecordMetadata metadata, Exception exception) {
        if (exception == null) {
            // 发送成功
            log.info("Sent to partition={}, offset={}",
                metadata.partition(), metadata.offset());
        } else {
            // 发送失败
            handleSendException(record, exception);
        }
    }
});

private void handleSendException(ProducerRecord<String, String> record, Exception e) {
    if (e instanceof RetriableException) {
        // 可重试异常（Kafka 已自动重试，仍失败 → 重试耗尽）
        log.warn("Retriable error after retries", e);
        // 重试或降级
        
    } else if (e instanceof SerializationException) {
        // 序列化失败（不可重试）
        log.error("Serialization failed", e);
        // 跳过、告警
        
    } else if (e instanceof RecordTooLargeException) {
        // 消息过大
        log.error("Message too large: {} bytes", record.value().length(), e);
        // 切分消息或拒绝发送
        
    } else if (e instanceof BufferExhaustedException) {
        // 累加器内存满
        log.error("Buffer exhausted", e);
        // 阻塞已发生，需排查
        
    } else if (e instanceof AuthorizationException) {
        // 权限不足
        log.error("Auth failed", e);
        // 配置 ACL
        
    } else {
        log.error("Unknown error", e);
    }
}
```

### 常见 Producer 异常

#### 1. TimeoutException

```
原因：
  1. request.timeout.ms 超时
  2. Broker 压力大
  3. 网络问题

处理：
  ✅ Kafka 自动重试（retries 配置）
  ✅ 增加超时时间
  ✅ 检查 Broker 健康
```

```java
// 自定义超时处理
try {
    producer.send(record).get(5, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    log.warn("Send timeout", e);
    // 记录到监控，发告警
}
```

#### 2. RecordTooLargeException

```
原因：消息大小超过 max.request.size（默认 1MB）
处理：
  1. 增加 max.request.size（不建议，超过 1MB 会影响性能）
  2. 切分大消息
  3. 存储到对象存储，Kafka 只传引用
```

```java
try {
    producer.send(record).get();
} catch (RecordTooLargeException e) {
    // 切分消息
    List<ProducerRecord<String, byte[]>> chunks = splitMessage(record);
    for (ProducerRecord<String, byte[]> chunk : chunks) {
        producer.send(chunk);
    }
}
```

#### 3. BufferExhaustedException

```
原因：RecordAccumulator 内存耗尽
处理：
  1. 增加 buffer.memory
  2. 增加 linger.ms（让 Sender 处理更多）
  3. 检查 Broker 健康（堆积可能是 Broker 慢）
```

#### 4. ProducerFencedException

```
原因：同 transactional.id 的旧 Producer 还在运行
处理：
  1. 关闭旧 Producer
  2. 使用不同的 transactional.id
```

#### 5. NetworkException

```
原因：网络断开
处理：
  ✅ Kafka 自动重连（reconnect.backoff.ms）
  ✅ 自动重试
  ⚠️ 持续网络问题需告警
```

## 📊 Consumer 异常

### 异常处理模式

```java
try {
    while (running) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        
        for (ConsumerRecord<String, String> record : records) {
            try {
                processRecord(record);
            } catch (Exception e) {
                handleProcessException(record, e);
            }
        }
        
        try {
            consumer.commitSync();
        } catch (CommitFailedException e) {
            handleCommitException(e);
        }
    }
} catch (WakeupException e) {
    // 优雅关闭
} catch (Exception e) {
    log.error("Consumer error", e);
} finally {
    try {
        consumer.commitSync();
    } catch (Exception e) {
        log.error("Final commit failed", e);
    }
    consumer.close();
}
```

### 常见 Consumer 异常

#### 1. OffsetOutOfRangeException

```
原因：
  1. 请求的 Offset 小于 earliest 或大于 latest
  2. 日志被删除（retention 过期）
  3. 指定了错误的 partition

处理：
  1. 设置 auto.offset.reset=earliest
  2. 增加 retention.ms
  3. 重新设置 Offset
```

```java
try {
    consumer.seek(tp, offset);
} catch (OffsetOutOfRangeException e) {
    log.warn("Offset out of range, resetting", e);
    consumer.seekToBeginning(Collections.singletonList(tp));
}
```

#### 2. CommitFailedException

```
原因：
  1. Rebalance 进行中
  2. session.timeout.ms 超时
  3. Offset 已过期

处理：
  1. 在 onPartitionsRevoked 中提交 Offset
  2. 增加 session.timeout.ms
  3. 重新订阅
```

```java
try {
    consumer.commitSync();
} catch (CommitFailedException e) {
    log.warn("Commit failed", e);
    // 重新订阅
    consumer.subscribe(topics);
}
```

#### 3. WakeupException

```
原因：调用 consumer.wakeup() 触发
处理：
  1. 优雅关闭 Consumer
  2. 提交 Offset
  3. 关闭连接
```

```java
try {
    consumer.poll(Duration.ofMillis(100));
} catch (WakeupException e) {
    log.info("Consumer waking up");
    // 优雅关闭
}
```

#### 4. RecordTooLargeException (Consumer)

```
原因：单条消息超过 fetch.max.bytes
处理：
  1. 增加 fetch.max.bytes
  2. 检查 Producer 端消息大小
```

#### 5. AuthenticationException / AuthorizationException

```
原因：SASL / SSL 配置错误或权限不足
处理：
  1. 检查认证配置
  2. 配置 ACL
  3. 检查证书有效性
```

## 🛠️ 实战：生产级异常处理

### Producer 异常处理完整示例

```java
public class RobustProducer {
    
    private final KafkaProducer<String, String> producer;
    private final AtomicLong successCount = new AtomicLong(0);
    private final AtomicLong failureCount = new AtomicLong(0);
    
    public void sendWithRetry(ProducerRecord<String, String> record, int maxRetries) {
        int attempt = 0;
        while (attempt <= maxRetries) {
            try {
                RecordMetadata metadata = producer.send(record).get(10, TimeUnit.SECONDS);
                successCount.incrementAndGet();
                log.debug("Sent: partition={}, offset={}", 
                    metadata.partition(), metadata.offset());
                return;
                
            } catch (Exception e) {
                failureCount.incrementAndGet();
                
                if (!shouldRetry(e) || attempt == maxRetries) {
                    log.error("Send failed after {} attempts", attempt + 1, e);
                    // 发送到死信队列
                    sendToDeadLetter(record, e);
                    return;
                }
                
                // 指数退避
                long backoff = (long) Math.pow(2, attempt) * 100;
                try {
                    Thread.sleep(backoff);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return;
                }
                
                attempt++;
            }
        }
    }
    
    private boolean shouldRetry(Exception e) {
        return e instanceof RetriableException 
            || e instanceof TimeoutException
            || e instanceof NetworkException;
    }
    
    private void sendToDeadLetter(ProducerRecord<String, String> record, Exception e) {
        // 发送到死信队列或告警系统
        ProducerRecord<String, String> dlq = new ProducerRecord<>(
            "dead-letter-queue",
            record.key(),
            record.value()
        );
        dlq.headers().add("error", e.getMessage().getBytes());
        dlq.headers().add("original-topic", record.topic().getBytes());
        producer.send(dlq);
    }
}
```

### Consumer 异常处理完整示例

```java
public class RobustConsumer {
    
    private final KafkaConsumer<String, String> consumer;
    private final AtomicLong processedCount = new AtomicLong(0);
    private final AtomicLong errorCount = new AtomicLong(0);
    
    public void consume() {
        Map<TopicPartition, OffsetAndMetadata> offsetsToCommit = new HashMap<>();
        
        try {
            while (running) {
                try {
                    ConsumerRecords<String, String> records = 
                        consumer.poll(Duration.ofMillis(500));
                    
                    if (records.isEmpty()) continue;
                    
                    for (ConsumerRecord<String, String> record : records) {
                        try {
                            // 处理消息
                            processRecord(record);
                            
                            // 累积 Offset
                            offsetsToCommit.put(
                                new TopicPartition(record.topic(), record.partition()),
                                new OffsetAndMetadata(record.offset() + 1)
                            );
                            
                            processedCount.incrementAndGet();
                            
                        } catch (Exception e) {
                            // 处理失败
                            handleProcessError(record, e);
                            
                            // 跳过这条消息（继续处理后续）
                            // ⚠️ 业务幂等前提
                            offsetsToCommit.put(
                                new TopicPartition(record.topic(), record.partition()),
                                new OffsetAndMetadata(record.offset() + 1)
                            );
                            
                            errorCount.incrementAndGet();
                        }
                    }
                    
                    // 提交 Offset
                    try {
                        consumer.commitSync(offsetsToCommit);
                        offsetsToCommit.clear();
                    } catch (CommitFailedException e) {
                        log.warn("Commit failed (likely during rebalance)", e);
                        offsetsToCommit.clear();
                    }
                    
                } catch (WakeupException e) {
                    log.info("Wakeup triggered, shutting down");
                    break;
                } catch (TimeoutException e) {
                    log.warn("Poll timeout", e);
                } catch (Exception e) {
                    log.error("Consumer error", e);
                    // 短暂休眠避免 CPU 占用过高
                    sleep(1000);
                }
            }
        } finally {
            // 最终提交
            try {
                consumer.commitSync(offsetsToCommit);
            } catch (Exception e) {
                log.error("Final commit failed", e);
            }
            consumer.close();
        }
    }
    
    private void handleProcessError(ConsumerRecord<String, String> record, Exception e) {
        log.error("Process failed at offset {}: {}", record.offset(), e.getMessage(), e);
        
        // 上报到监控系统
        Metrics.counter("kafka_process_error_total").increment();
        
        // 发送告警（可选）
        if (errorCount.get() > 100) {
            alarm("Consumer error rate too high");
        }
    }
}
```

## 📊 监控异常

### 关键指标

```java
// 监控各类异常
public class KafkaExceptionMetrics {
    // Producer 异常
    Counter producerRetriableError = Metrics.counter("kafka_producer_retriable_error_total");
    Counter producerNonRetriableError = Metrics.counter("kafka_producer_non_retriable_error_total");
    Counter producerTimeoutError = Metrics.counter("kafka_producer_timeout_error_total");
    
    // Consumer 异常
    Counter consumerCommitError = Metrics.counter("kafka_consumer_commit_error_total");
    Counter consumerProcessError = Metrics.counter("kafka_consumer_process_error_total");
    Counter consumerDeserializationError = Metrics.counter("kafka_consumer_deserialization_error_total");
    
    // 记录异常
    void recordProducerException(Exception e) {
        if (e instanceof RetriableException) {
            producerRetriableError.increment();
        } else if (e instanceof TimeoutException) {
            producerTimeoutError.increment();
        } else {
            producerNonRetriableError.increment();
        }
    }
}
```

### 告警规则

```
🚨 高错误率告警：
  - Producer 错误率 > 1% → 告警
  - Consumer 错误率 > 1% → 告警
  - Commit 失败率 > 5% → 告警

🚨 关键错误告警：
  - AuthenticationException → 立即告警
  - AuthorizationException → 立即告警
  - OffsetOutOfRangeException → 立即告警

🚨 集群异常告警：
  - Rebalance 频率 > 5 次/小时 → 告警
  - Lag 持续增长 > 30 分钟 → 告警
```

## ⚠️ 异常处理最佳实践

```
✅ 区分可重试和不可重试异常
✅ 可重试异常配合重试 + 指数退避
✅ 不可重试异常记录日志 + 死信队列
✅ 异步处理异常（不阻塞主流程）
✅ 监控异常频率和类型
✅ CommitFailedException 不 panic（通常是 Rebalance）
✅ WakeupException 用于优雅关闭
⚠️ 不要捕获 Exception 后不处理
⚠️ 不要无限重试
```

## 🎯 总结

**异常处理核心要点**：
- ✅ Kafka 异常分可重试 / 不可重试
- ✅ Producer 自动重试 RetriableException
- ✅ Consumer 需手动管理 Offset
- ✅ WakeupException 用于优雅关闭
- ✅ CommitFailedException 通常是 Rebalance
- ⚠️ 序列化错误不可重试
- ⚠️ 异常必须监控和告警

**下一步：** [🚀 Spring Kafka 入门](/07-spring/intro) — Spring 集成基础
