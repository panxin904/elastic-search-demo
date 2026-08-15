---
title: KafkaTemplate
---

# 📤 KafkaTemplate

> **KafkaTemplate** 是 Spring Kafka 提供的 Producer 高级抽象，简化了消息发送并提供丰富的功能。

## 🎯 KafkaTemplate 基础

### 注入使用

```java
@Service
public class MessageService {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    public void sendMessage(String topic, String key, String message) {
        kafkaTemplate.send(topic, key, message);
    }
}
```

### 配置自定义 KafkaTemplate

```java
@Configuration
public class KafkaTemplateConfig {
    
    @Bean
    public ProducerFactory<String, String> stringProducerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        return new DefaultKafkaProducerFactory<>(props);
    }
    
    @Bean
    public KafkaTemplate<String, String> stringKafkaTemplate() {
        return new KafkaTemplate<>(stringProducerFactory());
    }
}
```

## 📊 发送 API

### 1. send(topic, data)

```java
// 最简单（无 Key）
kafkaTemplate.send("orders", "order message");

// 返回 CompletableFuture
CompletableFuture<SendResult<String, String>> future = kafkaTemplate.send("orders", "msg");
```

### 2. send(topic, key, data)

```java
// 指定 Key（按 Key 分区）
kafkaTemplate.send("orders", "user123", "order message");

// 返回 Future
CompletableFuture<SendResult<String, String>> future = 
    kafkaTemplate.send("orders", "user123", "msg");
```

### 3. send(topic, partition, key, data)

```java
// 指定 Partition
kafkaTemplate.send("orders", 0, "user123", "msg");
```

### 4. send(topic, partition, timestamp, key, data)

```java
// 指定时间戳
long timestamp = System.currentTimeMillis();
kafkaTemplate.send("orders", 0, timestamp, "user123", "msg");
```

### 5. send(Message<?> message)

```java
// 通过 Spring Message 发送
Message<String> message = MessageBuilder.withPayload("value")
    .setHeader(KafkaHeaders.TOPIC, "orders")
    .setHeader(KafkaHeaders.KEY, "user123")
    .setHeader(KafkaHeaders.PARTITION, 0)
    .setHeader("traceId", "abc123")
    .build();

kafkaTemplate.send(message);
```

## 📊 异步回调

### 完整异步发送

```java
@Service
public class OrderProducer {
    
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    public void sendOrder(OrderEvent event) {
        kafkaTemplate.send("orders", event.getOrderId(), event)
            .whenComplete((result, ex) -> {
                if (ex == null) {
                    // 成功
                    RecordMetadata metadata = result.getRecordMetadata();
                    log.info("Sent: topic={}, partition={}, offset={}, timestamp={}",
                        metadata.topic(), metadata.partition(), metadata.offset(), metadata.timestamp());
                } else {
                    // 失败
                    log.error("Send failed: orderId={}", event.getOrderId(), ex);
                    handleFailure(event, ex);
                }
            });
    }
    
    private void handleFailure(OrderEvent event, Throwable ex) {
        // 重试或死信队列
        if (ex instanceof RetriableException) {
            // 记录到重试队列
            retryQueue.add(event);
        } else {
            // 死信队列
            deadLetterQueue.send(event, ex.getMessage());
        }
    }
}
```

### 同步发送

```java
public void sendSync(OrderEvent event) {
    try {
        SendResult<String, OrderEvent> result = kafkaTemplate
            .send("orders", event.getOrderId(), event)
            .get(10, TimeUnit.SECONDS);  // 阻塞最多 10 秒
        
        RecordMetadata metadata = result.getRecordMetadata();
        log.info("Sync sent: partition={}, offset={}", 
            metadata.partition(), metadata.offset());
    } catch (TimeoutException e) {
        log.error("Send timeout", e);
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    } catch (ExecutionException e) {
        log.error("Send failed", e);
    }
}
```

## 📊 事务支持

### KafkaTemplate 事务

```java
@Configuration
public class TransactionConfig {
    
    @Bean
    public ProducerFactory<String, String> producerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "my-tx-id");
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        // ... 其他配置
        
        DefaultKafkaProducerFactory<String, String> factory = 
            new DefaultKafkaProducerFactory<>(props);
        factory.setTransactionIdPrefix("tx-");  // 自动生成事务 ID
        return factory;
    }
}
```

```java
@Service
public class TransferService {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    public void transfer(String from, String to, int amount) {
        // 在事务中发送
        kafkaTemplate.executeInTransaction(operations -> {
            operations.send("account-a", from, "{\"delta\": -" + amount + "}");
            operations.send("account-b", to, "{\"delta\": +" + amount + "}");
            operations.send("audit-log", "transfer", "{\"from\": \"" + from + "\", \"to\": \"" + to + "\"}");
            return null;
        });
        // 事务自动提交（无异常时）
    }
    
    public void transferWithException(String from, String to, int amount) {
        try {
            kafkaTemplate.executeInTransaction(operations -> {
                operations.send("account-a", from, "{\"delta\": -" + amount + "}");
                operations.send("account-b", to, "{\"delta\": +" + amount + "}");
                
                // 业务异常，事务自动回滚
                if (amount > 10000) {
                    throw new RuntimeException("Transfer limit exceeded");
                }
                return null;
            });
        } catch (Exception e) {
            // 事务已回滚
            log.error("Transfer rolled back", e);
        }
    }
}
```

## 📊 批量发送

```java
@Service
public class BatchProducer {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    public void sendBatch(List<OrderEvent> events) {
        // 1. 逐条发送（KafkaTemplate 内部会批处理）
        events.forEach(event -> 
            kafkaTemplate.send("orders", event.getOrderId(), event.toJson()));
        
        // 2. flush 等待所有消息发送完成
        kafkaTemplate.flush();
    }
    
    public void sendBatchWithResult(List<OrderEvent> events) {
        // 收集所有 Future
        List<CompletableFuture<SendResult<String, String>>> futures = events.stream()
            .map(event -> kafkaTemplate.send("orders", event.getOrderId(), event.toJson()))
            .collect(Collectors.toList());
        
        // 等待所有完成
        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
            .whenComplete((result, ex) -> {
                if (ex == null) {
                    long successCount = futures.stream()
                        .map(CompletableFuture::join)
                        .filter(r -> r != null)
                        .count();
                    log.info("All sent: success={}/{}", successCount, events.size());
                } else {
                    log.error("Batch send failed", ex);
                }
            });
    }
}
```

## 📊 高级特性

### 设置 Headers

```java
// 方式 1：通过 ProducerRecord
ProducerRecord<String, String> record = new ProducerRecord<>("orders", "key", "value");
record.headers().add("traceId", "abc-123".getBytes());
record.headers().add("source", "order-service".getBytes());
kafkaTemplate.send(record);

// 方式 2：通过 Spring Message
Message<String> message = MessageBuilder.withPayload("value")
    .setHeader("traceId", "abc-123")
    .setHeader("source", "order-service")
    .build();
kafkaTemplate.send("orders", "key", message);
```

### 异步监听结果

```java
// 监听器方式（不阻塞）
kafkaTemplate.setProducerListener(new ProducerListener<String, String>() {
    @Override
    public void onSuccess(ProducerRecord<String, String> record, RecordMetadata metadata) {
        log.info("Sent successfully: {}", metadata);
    }
    
    @Override
    public void onError(ProducerRecord<String, String> record, Exception ex) {
        log.error("Send failed", ex);
    }
});
```

### 自定义 KafkaTemplate

```java
@Bean
public KafkaTemplate<String, OrderEvent> orderKafkaTemplate() {
    KafkaTemplate<String, OrderEvent> template = new KafkaTemplate<>(orderProducerFactory());
    
    // 设置默认 Topic
    template.setDefaultTopic("orders");
    
    // 设置 Producer 监听器
    template.setProducerListener(new LoggingProducerListener<>());
    
    return template;
}
```

## 🛠️ 实战：完整的 Producer 服务

```java
@Service
public class OrderProducer {
    
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    private final MeterRegistry meterRegistry;
    
    public OrderProducer(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
    }
    
    public CompletableFuture<SendResult<String, OrderEvent>> sendOrder(OrderEvent event) {
        // 1. 添加 TraceId
        Message<OrderEvent> message = MessageBuilder.withPayload(event)
            .setHeader(KafkaHeaders.KEY, event.getOrderId())
            .setHeader(KafkaHeaders.TOPIC, "orders")
            .setHeader("traceId", MDC.get("traceId"))
            .setHeader("source", "order-service")
            .build();
        
        // 2. 发送
        CompletableFuture<SendResult<String, OrderEvent>> future = 
            kafkaTemplate.send(message);
        
        // 3. 回调记录指标
        future.whenComplete((result, ex) -> {
            if (ex == null) {
                meterRegistry.counter("kafka_send_success_total",
                    "topic", "orders").increment();
            } else {
                meterRegistry.counter("kafka_send_error_total",
                    "topic", "orders").increment();
            }
        });
        
        return future;
    }
}
```

## 🔧 KafkaTemplate 异常处理

```java
@Service
public class SafeProducer {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    public void sendWithRetry(String topic, String key, String value, int maxRetries) {
        int attempt = 0;
        while (attempt < maxRetries) {
            try {
                kafkaTemplate.send(topic, key, value)
                    .whenComplete((result, ex) -> {
                        if (ex != null) {
                            handleFailure(topic, key, value, ex, attempt);
                        }
                    })
                    .get(10, TimeUnit.SECONDS);  // 阻塞等待
                return;  // 成功
            } catch (Exception e) {
                attempt++;
                if (attempt >= maxRetries) {
                    log.error("Send failed after {} retries", maxRetries, e);
                    // 死信队列或告警
                    deadLetterQueue.send(topic, key, value, e.getMessage());
                    return;
                }
                
                // 指数退避
                try {
                    Thread.sleep((long) Math.pow(2, attempt) * 100);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
    }
}
```

## ⚠️ 常见问题

### 问题 1：KafkaTemplate 注入失败

```
原因：缺少 KafkaTemplate Bean
解决：
  1. 使用 Spring Boot 自动配置
  2. 或显式配置 KafkaTemplate
```

### 问题 2：消息发送成功但消费失败

```
原因：序列化器与反序列化器不匹配
解决：
  1. 统一序列化方案
  2. 监控 Consumer 端反序列化异常
```

## 🎯 总结

**KafkaTemplate 核心要点**：
- ✅ Spring Kafka 的核心 Producer API
- ✅ 5 种 send 重载方法
- ✅ 异步回调 + 同步发送
- ✅ 事务支持（executeInTransaction）
- ✅ Spring Message 集成（Headers）
- ⚠️ 注意序列化器兼容性
- ⚠️ 异常处理要分级（可重试 vs 不可重试）

**下一步：** [🎧 @KafkaListener](/07-spring/listener) — 监听器深度使用
