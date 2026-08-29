---
title: Spring Kafka 入门
date: 2026-08-15  # date-auto-injected
---

# 🚀 Spring Kafka 入门

> **Spring for Apache Kafka（Spring Kafka）** 是 Spring 官方提供的 Kafka 集成框架，简化了 Kafka 客户端的使用。

## 🎯 引入依赖

```xml
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
    <version>3.2.0</version>
</dependency>

<!-- Spring Boot 集成 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter</artifactId>
</dependency>
```

## 🚀 快速开始

### 1. Spring Boot 集成

```xml
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  kafka:
    bootstrap-servers: localhost:9092
    consumer:
      group-id: order-processor
      auto-offset-reset: earliest
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.apache.kafka.common.serialization.StringDeserializer
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.apache.kafka.common.serialization.StringSerializer
```

### 2. Producer（KafkaTemplate）

```java
@Service
public class OrderProducer {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    public void sendOrder(OrderEvent event) {
        // 同步发送
        kafkaTemplate.send("orders", event.getOrderId(), event.toJson())
            .whenComplete((result, ex) -> {
                if (ex == null) {
                    log.info("Sent: {}", result.getRecordMetadata().offset());
                } else {
                    log.error("Send failed", ex);
                }
            });
    }
}
```

### 3. Consumer（@KafkaListener）

```java
@Service
public class OrderConsumer {
    
    @KafkaListener(topics = "orders", groupId = "order-processor")
    public void consume(OrderEvent event) {
        log.info("Received: {}", event);
        processOrder(event);
    }
}
```

## 🔧 KafkaTemplate

### 基础 API

```java
@Autowired
private KafkaTemplate<String, String> kafkaTemplate;

// 1. 同步发送（返回 Future）
CompletableFuture<SendResult<String, String>> future = 
    kafkaTemplate.send("orders", "key1", "value1");
SendResult<String, String> result = future.get();
System.out.println("Partition: " + result.getRecordMetadata().partition());

// 2. 异步发送（带回调）
kafkaTemplate.send("orders", "key1", "value1")
    .whenComplete((result, ex) -> {
        if (ex == null) {
            log.info("Sent: {}", result.getRecordMetadata());
        } else {
            log.error("Send failed", ex);
        }
    });

// 3. 指定 Partition
kafkaTemplate.send("orders", 0, "key1", "value1");

// 4. 带时间戳
kafkaTemplate.send("orders", 0, System.currentTimeMillis(), "key1", "value1");

// 5. 带 Headers
Message<String> message = MessageBuilder.withPayload("value1")
    .setHeader("traceId", "abc123")
    .setHeader(KafkaHeaders.TOPIC, "orders")
    .setHeader(KafkaHeaders.KEY, "key1")
    .build();
kafkaTemplate.send(message);
```

### 高级 API

```java
// 1. 事务发送（需要 KafkaTemplate 配置 transactional.id）
kafkaTemplate.executeInTransaction(operations -> {
    operations.send("orders", "key1", "value1");
    operations.send("orders", "key2", "value2");
    return null;
});

// 2. 批量发送
List<ProducerRecord<String, String>> records = Arrays.asList(
    new ProducerRecord<>("orders", "key1", "value1"),
    new ProducerRecord<>("orders", "key2", "value2")
);
records.forEach(r -> kafkaTemplate.send(r));

// 3. 通过 Producer 发送
kafkaTemplate.execute(producer -> {
    producer.send(new ProducerRecord<>("orders", "key", "value"));
    return null;
});
```

## 🔧 @KafkaListener

### 基础用法

```java
// 监听单个 Topic
@KafkaListener(topics = "orders")
public void consume(OrderEvent event) {
    processOrder(event);
}

// 监听多个 Topic
@KafkaListener(topics = {"orders", "payments"})
public void consume(@Payload String message, @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
    if ("orders".equals(topic)) {
        processOrder(message);
    } else {
        processPayment(message);
    }
}

// 指定 Group ID
@KafkaListener(topics = "orders", groupId = "order-processor")
public void consume(OrderEvent event) {
    processOrder(event);
}
```

### 接收完整消息

```java
@KafkaListener(topics = "orders")
public void consume(
    @Payload OrderEvent event,           // 消息体
    @Header(KafkaHeaders.RECEIVED_KEY) String key,        // Key
    @Header(KafkaHeaders.RECEIVED_PARTITION) int partition, // Partition
    @Header(KafkaHeaders.OFFSET) long offset,           // Offset
    @Headers Map<String, Object> headers                // 所有 Headers
) {
    log.info("Key={}, Partition={}, Offset={}", key, partition, offset);
    processOrder(event);
}

// 接收 ConsumerRecord
@KafkaListener(topics = "orders")
public void consume(ConsumerRecord<String, String> record) {
    log.info("Partition={}, Offset={}, Key={}, Value={}",
        record.partition(), record.offset(), record.key(), record.value());
}

// 接收 Acknowledgment（手动提交）
@KafkaListener(topics = "orders")
public void consume(OrderEvent event, Acknowledgment ack) {
    try {
        processOrder(event);
        ack.acknowledge();  // 手动提交 Offset
    } catch (Exception e) {
        log.error("Process failed", e);
    }
}
```

### 并发消费

```java
// concurrency = 3（3 个消费者并行处理）
@KafkaListener(topics = "orders", concurrency = "3")
public void consume(OrderEvent event) {
    processOrder(event);
}

// 动态配置（SpEL）
@KafkaListener(
    topics = "orders",
    concurrency = "${spring.kafka.listener.concurrency:3}"
)
public void consume(OrderEvent event) {
    processOrder(event);
}
```

### 批量消费

```java
@KafkaListener(topics = "orders")
public void consume(List<OrderEvent> events) {
    log.info("Received {} messages", events.size());
    for (OrderEvent event : events) {
        processOrder(event);
    }
}
```

## 🔧 Spring Boot 自动配置

### 默认配置

```yaml
spring:
  kafka:
    # 通用配置
    bootstrap-servers: localhost:9092
    client-id: my-app
    
    # Producer 配置
    producer:
      acks: all
      retries: 3
      batch-size: 16384
      buffer-memory: 33554432
      compression-type: lz4
      properties:
        enable.idempotence: true
        max.in.flight.requests.per.connection: 5
        linger.ms: 10
    
    # Consumer 配置
    consumer:
      group-id: default-group
      auto-offset-reset: earliest
      enable-auto-commit: true
      auto-commit-interval: 5000
      max-poll-records: 500
      isolation-level: read_committed
      properties:
        session.timeout.ms: 30000
        heartbeat.interval.ms: 10000
    
    # Listener 配置
    listener:
      ack-mode: batch
      concurrency: 1
      missing-topics-fatal: false
```

### 自定义配置

```java
@Configuration
public class KafkaConfig {
    
    @Bean
    public ProducerFactory<String, OrderEvent> producerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        
        return new DefaultKafkaProducerFactory<>(props);
    }
    
    @Bean
    public KafkaTemplate<String, OrderEvent> kafkaTemplate() {
        return new KafkaTemplate<>(producerFactory());
    }
    
    @Bean
    public ConsumerFactory<String, OrderEvent> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processor");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonDeserializer.class);
        
        return new DefaultKafkaConsumerFactory<>(props);
    }
    
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> kafkaListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, OrderEvent> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory());
        factory.setConcurrency(3);
        return factory;
    }
}
```

## 🔧 实战：完整的 Order 服务

```java
// 实体类
@Data
public class OrderEvent {
    private String orderId;
    private String userId;
    private BigDecimal amount;
    private String status;
    private LocalDateTime timestamp;
}

// Producer
@Service
public class OrderProducer {
    
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    public void sendOrder(OrderEvent event) {
        kafkaTemplate.send("orders", event.getOrderId(), event)
            .whenComplete((result, ex) -> {
                if (ex == null) {
                    log.info("Order event sent: orderId={}, partition={}, offset={}",
                        event.getOrderId(),
                        result.getRecordMetadata().partition(),
                        result.getRecordMetadata().offset());
                } else {
                    log.error("Failed to send order event", ex);
                }
            });
    }
}

// Consumer
@Service
public class OrderConsumer {
    
    @KafkaListener(topics = "orders", groupId = "order-processor", concurrency = "3")
    public void consume(
        @Payload OrderEvent event,
        @Header(KafkaHeaders.RECEIVED_KEY) String key,
        Acknowledgment ack
    ) {
        try {
            log.info("Processing order: key={}, orderId={}", key, event.getOrderId());
            processOrder(event);
            ack.acknowledge();
        } catch (Exception e) {
            log.error("Failed to process order", e);
            // 不 ack，下次重新消费（业务幂等前提）
        }
    }
    
    private void processOrder(OrderEvent event) {
        // 业务处理（应幂等）
        orderRepository.save(event);
    }
}
```

## ⚙️ 关键配置

```yaml
# Listener 容器配置
spring.kafka.listener:
  ack-mode: manual_immediate      # 手动提交模式
  concurrency: 3                  # 并发数
  missing-topics-fatal: false     # Topic 不存在时不报错
  poll-timeout: 500               # poll 超时
  type: single                    # single / batch
```

## ⚠️ 常见问题

### 问题 1：@KafkaListener 不生效

```
原因：
  1. 未启用 Kafka 监听器
  2. 配置文件错误
解决：
  1. 添加 @EnableKafka 注解
  2. 检查 application.yml
```

### 问题 2：反序列化失败

```
原因：序列化器与反序列化器不匹配
解决：
  1. 统一序列化方案
  2. 使用 JsonSerializer/JsonDeserializer
```

### 问题 3：Offset 不提交

```
原因：未启用自动提交或未手动 ack
解决：
  1. ack-mode: batch（自动提交）
  2. 或手动 ack.acknowledge()
```

## 🎯 总结

**Spring Kafka 核心要点**：
- ✅ Spring Boot 自动配置 KafkaTemplate
- ✅ @KafkaListener 简化消费
- ✅ 同步 + 异步发送 API
- ✅ 批量消费 + 并发消费
- ✅ 事务支持（executeInTransaction）
- ⚠️ 序列化器兼容性
- ⚠️ 注意 ack 模式

**下一步：** [📤 KafkaTemplate](/07-spring/kafka-template) — KafkaTemplate 深度使用


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
