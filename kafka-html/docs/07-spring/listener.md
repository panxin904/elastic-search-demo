---
title: KafkaListener 注解
---

# 🎧 @KafkaListener

> **@KafkaListener** 是 Spring Kafka 提供的注解式消费 API，极大简化了 Kafka 消费者开发。

## 🎯 基础使用

### 简单消费

```java
@Component
public class OrderListener {
    
    @KafkaListener(topics = "orders", groupId = "order-processor")
    public void onOrder(OrderEvent event) {
        log.info("Received order: {}", event);
        processOrder(event);
    }
}
```

### 多 Topic 消费

```java
@KafkaListener(topics = {"orders", "payments"})
public void onMessage(@Payload String message,
                      @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
    if ("orders".equals(topic)) {
        processOrder(message);
    } else {
        processPayment(message);
    }
}
```

## 📊 参数详解

### @Payload

```java
// 单个参数：直接是消息体
@KafkaListener(topics = "orders")
public void consume(OrderEvent event) { }

// 必填校验
@KafkaListener(topics = "orders")
public void consume(@Payload @NotNull OrderEvent event) { }
```

### @Header

```java
@KafkaListener(topics = "orders")
public void consume(
    @Payload OrderEvent event,
    @Header(KafkaHeaders.RECEIVED_KEY) String key,
    @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
    @Header(KafkaHeaders.OFFSET) long offset,
    @Header(value = "traceId", required = false) String traceId
) {
    log.info("Partition={}, Offset={}, traceId={}", partition, offset, traceId);
}
```

### @Headers

```java
@KafkaListener(topics = "orders")
public void consume(
    @Payload OrderEvent event,
    @Headers Map<String, Object> headers
) {
    String traceId = (String) headers.get("traceId");
}
```

### ConsumerRecord

```java
@KafkaListener(topics = "orders")
public void consume(ConsumerRecord<String, OrderEvent> record) {
    log.info("Partition={}, Offset={}, Key={}",
        record.partition(), record.offset(), record.key());
}
```

### Acknowledgment（手动提交）

```java
@KafkaListener(topics = "orders")
public void consume(OrderEvent event, Acknowledgment ack) {
    try {
        processOrder(event);
        ack.acknowledge();  // 手动提交
    } catch (Exception e) {
        log.error("Process failed", e);
        // 不 ack，下次重新消费
    }
}
```

## 📊 高级配置

### 并发消费

```java
// concurrency = 3（3 个消费者并行）
@KafkaListener(topics = "orders", concurrency = "3")
public void consume(OrderEvent event) {
    processOrder(event);
}
```

### 批量消费

```java
// 配置 batch listener
@KafkaListener(topics = "orders", containerFactory = "batchListenerFactory")
public void consume(List<OrderEvent> events) {
    log.info("Received {} messages", events.size());
    for (OrderEvent event : events) {
        processOrder(event);
    }
}

// 配置 Batch Listener Factory
@Bean
public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> batchListenerFactory() {
    ConcurrentKafkaListenerContainerFactory<String, OrderEvent> factory = 
        new ConcurrentKafkaListenerContainerFactory<>();
    factory.setConsumerFactory(consumerFactory());
    factory.setBatchListener(true);
    factory.setBatchSize(100);
    return factory;
}
```

### 主题模式匹配

```java
// 监听所有以 order- 开头的 Topic
@KafkaListener(topicPattern = "order-.*")
public void consume(@Payload String message,
                     @Header(KafkaHeaders.RECEIVED_TOPIC) String topic) {
    log.info("Received from {}: {}", topic, message);
}
```

### 手动指定 Partition

```java
@KafkaListener(
    topicPartitions = @TopicPartition(
        topic = "orders",
        partitions = {"0", "1", "2"}
    )
)
public void consume(OrderEvent event) {
    processOrder(event);
}

// 指定从哪个 Offset 开始
@KafkaListener(
    topicPartitions = @TopicPartition(
        topic = "orders",
        partitionOffsets = @PartitionOffset(
            partition = "0",
            initialOffset = "1000"
        )
    )
)
public void consume(OrderEvent event) {
    processOrder(event);
}
```

### 配置属性

```java
@KafkaListener(
    topics = "orders",
    groupId = "order-processor",
    concurrency = "3",
    containerFactory = "kafkaListenerContainerFactory",
    autoStartup = "true",                    // 启动时自动启动
    beanRef = "__listener",                  // Bean 引用
    clientIdPrefix = "order-consumer",       // 客户端 ID 前缀
    properties = {
        @Property(name = "session.timeout.ms", value = "30000"),
        @Property(name = "heartbeat.interval.ms", value = "10000")
    }
)
public void consume(OrderEvent event) {
    processOrder(event);
}
```

## 📊 Ack 模式

### AckMode 配置

```java
@Bean
public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> kafkaListenerContainerFactory() {
    ConcurrentKafkaListenerContainerFactory<String, OrderEvent> factory = 
        new ConcurrentKafkaListenerContainerFactory<>();
    factory.setConsumerFactory(consumerFactory());
    
    // AckMode 选项：
    // RECORD：每条消息处理后提交
    // BATCH：批量处理后提交（默认）
    // TIME：定时提交
    // COUNT：处理 N 条后提交
    // COUNT_TIME：上述任一条件触发
    // MANUAL：手动调用 Acknowledgment.acknowledge()
    // MANUAL_IMMEDIATE：立即手动提交
    
    factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL_IMMEDIATE);
    return factory;
}
```

### 不同场景的 Ack 模式

```java
// 1. RECORD：每条消息提交（低延迟，低吞吐）
factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.RECORD);

// 2. BATCH：批量提交（默认，平衡）
factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.BATCH);

// 3. MANUAL_IMMEDIATE：手动立即提交（精确控制）
factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL_IMMEDIATE);

// 4. MANUAL：手动延迟提交（依赖下一次 poll）
factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL);
```

## 📊 错误处理

### 默认错误处理

```java
// Spring Kafka 提供默认错误处理
@Bean
public DefaultErrorHandler errorHandler() {
    return new DefaultErrorHandler(
        new FixedBackOff(1000L, 3L)  // 重试 3 次，每次间隔 1 秒
    );
}
```

### 自定义错误处理

```java
@Bean
public DefaultErrorHandler errorHandler(KafkaTemplate<String, String> kafkaTemplate) {
    
    // 死信发布器：处理失败的消息发送到 DLT
    DeadLetterPublishingRecoverer recoverer = new DeadLetterPublishingRecoverer(
        kafkaTemplate,
        (record, ex) -> new TopicPartition("orders.DLT", record.partition())
    );
    
    // 重试策略
    FixedBackOff backOff = new FixedBackOff(1000L, 3L);  // 1 秒 × 3 次
    
    return new DefaultErrorHandler(recoverer, backOff);
}
```

### 业务异常处理

```java
@Service
public class RobustListener {
    
    @KafkaListener(topics = "orders")
    public void consume(OrderEvent event, Acknowledgment ack) {
        try {
            // 业务处理
            processOrder(event);
            
            // 成功：提交 Offset
            ack.acknowledge();
            
        } catch (BusinessException e) {
            // 业务异常：跳过这条消息，继续处理
            log.warn("Business error, skipping: orderId={}", event.getOrderId(), e);
            ack.acknowledge();  // 必须 ack，否则会重复消费
            
        } catch (SystemException e) {
            // 系统异常：不 ack，让 Spring Kafka 重试
            log.error("System error, will retry", e);
            throw e;  // 抛出让 ErrorHandler 处理
        }
    }
}
```

## 🛠️ 实战：完整的 @KafkaListener 应用

```java
@Service
@Slf4j
public class OrderEventListener {
    
    @Autowired
    private OrderService orderService;
    
    // 监听订单事件，3 个并发
    @KafkaListener(
        topics = "orders",
        groupId = "order-processor",
        concurrency = "3",
        containerFactory = "manualAckListenerFactory"
    )
    public void onOrderEvent(
        @Payload OrderEvent event,
        @Header(KafkaHeaders.RECEIVED_KEY) String key,
        @Header(KafkaHeaders.RECEIVED_PARTITION) int partition,
        @Header(KafkaHeaders.OFFSET) long offset,
        @Header(name = "traceId", required = false) String traceId,
        Acknowledgment ack
    ) {
        MDC.put("traceId", traceId);
        MDC.put("offset", String.valueOf(offset));
        
        try {
            log.info("Processing order: key={}, partition={}, offset={}, orderId={}",
                key, partition, offset, event.getOrderId());
            
            // 业务处理
            orderService.processOrder(event);
            
            // 提交 Offset
            ack.acknowledge();
            
        } catch (BusinessException e) {
            // 业务异常：跳过
            log.warn("Business error, skip: orderId={}", event.getOrderId(), e);
            ack.acknowledge();
            
        } catch (Exception e) {
            // 系统异常：抛出让 ErrorHandler 重试
            log.error("System error", e);
            throw e;
            
        } finally {
            MDC.clear();
        }
    }
}
```

## 🔧 监听器配置

```java
@Configuration
public class KafkaListenerConfig {
    
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> manualAckListenerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, String> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory());
        
        // 手动 ack 模式
        factory.getContainerProperties().setAckMode(
            ContainerProperties.AckMode.MANUAL_IMMEDIATE);
        
        // 并发数
        factory.setConcurrency(3);
        
        // 错误处理
        factory.setCommonErrorHandler(errorHandler());
        
        return factory;
    }
    
    @Bean
    public DefaultErrorHandler errorHandler(KafkaTemplate<String, String> kafkaTemplate) {
        // 重试 + 死信队列
        DeadLetterPublishingRecoverer recoverer = new DeadLetterPublishingRecoverer(
            kafkaTemplate,
            (record, ex) -> new TopicPartition(record.topic() + ".DLT", record.partition())
        );
        return new DefaultErrorHandler(
            recoverer,
            new ExponentialBackOff(1000L, 2.0)  // 1 秒起步，指数退避
        );
    }
}
```

## ⚠️ 常见问题

### 问题 1：监听器不消费

```
原因：
  1. Topic 不存在
  2. Group 已存在 Offset，无新数据
解决：
  1. 创建 Topic
  2. 设置 auto-offset-reset=earliest
  3. 重置 Offset
```

### 问题 2：Offset 不提交

```
原因：未 ack 或 ack 模式不对
解决：
  1. 调用 ack.acknowledge()
  2. 检查 AckMode 配置
```

### 问题 3：消费慢

```
原因：
  1. 并发度不够
  2. 业务处理慢
解决：
  1. 增加 concurrency
  2. 优化业务逻辑
```

## 🎯 总结

**@KafkaListener 核心要点**：
- ✅ 注解式消费极简开发
- ✅ 支持批量消费、并发消费、主题模式
- ✅ 灵活获取消息元数据（Key、Partition、Offset）
- ✅ 手动 ack 精确控制
- ✅ DefaultErrorHandler 自动重试 + 死信
- ⚠️ 业务异常需要手动处理 ack
- ⚠️ 监听器内部阻塞会影响整个 partition

**下一步：** [🔐 Spring 事务](/07-spring/transaction) — Kafka 事务集成
