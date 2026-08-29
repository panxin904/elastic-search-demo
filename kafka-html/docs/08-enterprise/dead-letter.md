---
title: 死信队列
date: 2026-08-15  # date-auto-injected
---

# ☠️ 死信队列

> **死信队列（Dead Letter Queue, DLQ）**是处理失败消息的标准模式。Kafka 通过 **DLT Topic** 实现。

## 🎯 什么是死信队列？

```
死信队列 = 存储"无法处理"消息的专用 Topic

场景：
  - 消息反序列化失败
  - 业务处理异常
  - 重试次数用尽
  - 消息过期（TTL 过期）

作用：
  ✅ 隔离失败消息（不阻塞正常消费）
  ✅ 后续排查和重试
  ✅ 数据可追溯
```

## 🔧 实现方案

### 方案 1：Spring Kafka 自带 DLT

```java
// Spring Kafka 内置 DLT 支持
@Configuration
public class DLTConfig {
    
    @Bean
    public DeadLetterPublishingRecoverer deadLetterRecoverer(
            KafkaTemplate<String, String> kafkaTemplate) {
        
        return new DeadLetterPublishingRecoverer(
            kafkaTemplate,
            // 路由规则：失败消息发到 {topic}.DLT
            (record, ex) -> new TopicPartition(record.topic() + ".DLT", record.partition())
        );
    }
    
    @Bean
    public DefaultErrorHandler errorHandler(DeadLetterPublishingRecoverer recoverer) {
        // 重试 3 次后发送到 DLT
        return new DefaultErrorHandler(recoverer, new FixedBackOff(1000L, 3L));
    }
}
```

### 方案 2：自定义 DLT

```java
@Service
public class CustomDLTHandler {
    
    @Autowired
    private KafkaTemplate<String, String> dltTemplate;
    
    @DltHandler  // Spring Kafka 注解
    public void handleDlt(ConsumerRecord<String, String> record) {
        log.error("DLT message received: topic={}, offset={}", 
            record.topic(), record.offset());
        
        // 1. 添加错误信息到 header
        ProducerRecord<String, String> dlt = new ProducerRecord<>(
            record.topic() + ".DLT", 
            record.key(), 
            record.value()
        );
        dlt.headers().add("X-Original-Topic", record.topic().getBytes());
        dlt.headers().add("X-Original-Partition", String.valueOf(record.partition()).getBytes());
        dlt.headers().add("X-Original-Offset", String.valueOf(record.offset()).getBytes());
        dlt.headers().add("X-Error-Time", String.valueOf(System.currentTimeMillis()).getBytes());
        
        // 2. 发送到 DLT
        dltTemplate.send(dlt);
        
        // 3. 报警
        alarm("Message moved to DLT: " + record.topic());
    }
}
```

## 📊 DLT Topic 设计

### 方式 1：独立 DLT Topic

```bash
# 为每个业务 Topic 创建对应的 DLT
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic orders.DLT --partitions 3 --replication-factor 2

kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic payments.DLT --partitions 3 --replication-factor 2
```

### 方式 2：统一 DLT Topic

```bash
# 所有失败消息发到同一个 DLT
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic all.dlt --partitions 6 --replication-factor 2

# 用 header 区分原始 topic
```

### 推荐

```
✅ 每个业务 Topic 独立 DLT（推荐）
   - 业务隔离
   - 独立消费
   - 独立清理

⚠️ 统一 DLT
   - 简单但管理复杂
   - 业务间相互影响
```

## 🛠️ 实战：完整的 DLT 方案

### 1. 创建 DLT Topic

```bash
# 业务 Topic
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic orders --partitions 6 --replication-factor 3

# DLT
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic orders.DLT --partitions 6 --replication-factor 3 \
    --config retention.ms=2592000000  # 保留 30 天（DLT 排查需要）
```

### 2. Producer（业务正常发送）

```java
@Service
public class OrderProducer {
    
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    public void sendOrder(OrderEvent event) {
        kafkaTemplate.send("orders", event.getOrderId(), event);
    }
}
```

### 3. Consumer（带 DLT）

```java
@Service
public class OrderConsumer {
    
    @KafkaListener(topics = "orders", groupId = "order-processor")
    public void consume(OrderEvent event, Acknowledgment ack) {
        try {
            orderService.process(event);
            ack.acknowledge();
        } catch (BusinessException e) {
            // 业务异常：跳过 + 记录日志（不重试）
            log.warn("Business error, skip: orderId={}", event.getOrderId(), e);
            ack.acknowledge();
        } catch (Exception e) {
            // 系统异常：抛出让 ErrorHandler 处理（重试 → DLT）
            log.error("System error, will retry/DLT", e);
            throw e;
        }
    }
}

@Configuration
public class DLTConfig {
    
    @Bean
    public DeadLetterPublishingRecoverer deadLetterRecoverer(
            KafkaTemplate<String, Object> kafkaTemplate) {
        return new DeadLetterPublishingRecoverer(
            kafkaTemplate,
            (record, ex) -> new TopicPartition("orders.DLT", record.partition())
        );
    }
    
    @Bean
    public DefaultErrorHandler errorHandler(DeadLetterPublishingRecoverer recoverer) {
        // 重试 3 次，每次间隔 1 秒
        return new DefaultErrorHandler(recoverer, new FixedBackOff(1000L, 3L));
    }
}
```

### 4. DLT Consumer（排查和重试）

```java
@Service
public class DLTConsumer {
    
    @KafkaListener(topics = "orders.DLT", groupId = "dlt-monitor")
    public void consumeDLT(ConsumerRecord<String, String> record) {
        log.error("DLT message received: topic={}, partition={}, offset={}, value={}",
            record.topic(), record.partition(), record.offset(), record.value());
        
        // 1. 解析错误信息（从 headers）
        String errorClass = getHeader(record, KafkaHeaders.DLT_EXCEPTION_FQCN);
        String errorMessage = getHeader(record, KafkaHeaders.DLT_EXCEPTION_MESSAGE);
        String originalTopic = getHeader(record, KafkaHeaders.DLT_ORIGINAL_TOPIC);
        
        // 2. 分类处理
        if (isRetriable(errorClass)) {
            // 可重试：延迟后重发到主 Topic
            delayRetry(originalTopic, record);
        } else {
            // 不可重试：人工处理或写入数据库
            saveForManualProcessing(record, errorMessage);
        }
        
        // 3. 报警
        alarm("DLT message: " + originalTopic + " - " + errorMessage);
    }
    
    private String getHeader(ConsumerRecord<String, String> record, String key) {
        Header header = record.headers().lastHeader(key);
        return header != null ? new String(header.value()) : null;
    }
}
```

## 🔧 DLT 重试策略

### 智能重试

```java
@Service
public class SmartRetryDLT {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    // 重试策略：
    // 1. 第一次失败：5 秒后重试
    // 2. 第二次失败：1 分钟后重试
    // 3. 第三次失败：10 分钟后重试
    // 4. 第四次失败：进入死信队列（人工处理）
    
    public void scheduleRetry(ConsumerRecord<String, String> record, int attemptCount) {
        long delayMs = getRetryDelay(attemptCount);
        
        // 1. 重新发送到主 Topic（带 Retry 标记）
        ProducerRecord<String, String> retryRecord = new ProducerRecord<>(
            record.topic(),
            record.partition(),
            record.key(),
            record.value()
        );
        retryRecord.headers().add("X-Retry-Attempt", String.valueOf(attemptCount + 1).getBytes());
        retryRecord.headers().add("X-Retry-Delay", String.valueOf(delayMs).getBytes());
        
        // 2. 延迟发送
        kafkaTemplate.send(retryRecord)
            .whenComplete((result, ex) -> {
                if (ex == null) {
                    log.info("Retry scheduled, attempt={}, delay={}ms", 
                        attemptCount + 1, delayMs);
                }
            });
    }
    
    private long getRetryDelay(int attempt) {
        return switch (attempt) {
            case 1 -> 5_000;       // 5 秒
            case 2 -> 60_000;      // 1 分钟
            case 3 -> 600_000;     // 10 分钟
            default -> 3_600_000;  // 1 小时（最终）
        };
    }
}
```

### 自定义重试 Topic

```bash
# 不同重试次数的 Topic
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic orders.retry.1 --partitions 6 --replication-factor 2
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic orders.retry.2 --partitions 6 --replication-factor 2
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic orders.retry.3 --partitions 6 --replication-factor 2

# 最终死信 Topic
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic orders.DLT --partitions 6 --replication-factor 2
```

```java
// 重试转发
@KafkaListener(topics = "orders.retry.1", groupId = "retry-forwarder")
public void retry1(ConsumerRecord<String, String> record) {
    try {
        Thread.sleep(5_000);  // 5 秒
    } catch (InterruptedException e) {}
    
    try {
        orderService.process(parseEvent(record.value()));
    } catch (Exception e) {
        // 失败：发到下一级重试
        kafkaTemplate.send("orders.retry.2", record.key(), record.value());
    }
}
```

## 📊 DLT 监控

### 关键指标

```java
@Component
public class DLTMonitor {
    
    @Autowired
    private MeterRegistry meterRegistry;
    
    private final Counter dltMessages = Counter.builder("kafka_dlt_messages_total")
        .description("Total messages moved to DLT")
        .register(meterRegistry);
    
    @KafkaListener(topics = "orders.DLT", groupId = "dlt-monitor")
    public void monitor(ConsumerRecord<String, String> record) {
        // 1. 记录指标
        dltMessages.increment();
        
        // 2. 解析错误信息
        String errorClass = getHeader(record, KafkaHeaders.DLT_EXCEPTION_FQCN);
        String errorMessage = getHeader(record, KafkaHeaders.DLT_EXCEPTION_MESSAGE);
        String originalTopic = getHeader(record, KafkaHeaders.DLT_ORIGINAL_TOPIC);
        
        // 3. 分类告警
        if (errorClass != null && errorClass.contains("DeserializationException")) {
            // 反序列化错误（Schema 变更）
            alertCritical("Schema change detected: " + originalTopic);
        } else {
            // 其他错误
            alertWarn("DLT message: " + originalTopic + " - " + errorMessage);
        }
    }
}
```

### 告警规则

```
🚨 立即告警：
  - DLT 消息突然增多（> 10 条/分钟）
  - 反序列化错误（Schema 变更）
  - 未知异常（可能是代码 bug）

⚠️ 延迟告警：
  - DLT 消息累计 > 100 条
  - DLT 消息超过 7 天未处理
```

## 🛠️ 实战：完整的死信队列方案

### 1. 部署 DLT Topic

```bash
# 业务 Topic
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic orders --partitions 6 --replication-factor 3

# DLT Topic
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic orders.DLT --partitions 6 --replication-factor 3 \
    --config retention.ms=2592000000

# 重试 Topic
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic orders.retry --partitions 6 --replication-factor 2 \
    --config retention.ms=86400000  # 重试 Topic 保留 1 天
```

### 2. 配置 Spring Kafka

```java
@Configuration
@EnableKafka
public class KafkaConfig {
    
    @Bean
    public ProducerFactory<String, String> producerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
        return new DefaultKafkaProducerFactory<>(props);
    }
    
    @Bean
    public KafkaTemplate<String, String> kafkaTemplate() {
        return new KafkaTemplate<>(producerFactory());
    }
    
    @Bean
    public ConsumerFactory<String, String> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processor");
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class);
        return new DefaultKafkaConsumerFactory<>(props);
    }
    
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, String> factory =
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory());
        
        // 错误处理：重试 + DLT
        DeadLetterPublishingRecoverer recoverer = new DeadLetterPublishingRecoverer(
            kafkaTemplate(),
            (record, ex) -> new TopicPartition(record.topic() + ".DLT", record.partition())
        );
        
        // 重试 3 次后发送 DLT
        factory.setCommonErrorHandler(new DefaultErrorHandler(
            recoverer,
            new FixedBackOff(1000L, 3L)  // 1 秒 × 3 次
        ));
        
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.RECORD);
        return factory;
    }
}
```

### 3. 业务 Consumer

```java
@Service
public class OrderConsumer {
    
    @KafkaListener(topics = "orders", groupId = "order-processor")
    public void consume(String message, Acknowledgment ack) {
        try {
            OrderEvent event = parseEvent(message);
            orderService.process(event);
            ack.acknowledge();
        } catch (BusinessException e) {
            // 业务异常：跳过（不重试）
            log.warn("Business error, skip: {}", e.getMessage());
            ack.acknowledge();
        } catch (Exception e) {
            // 系统异常：抛出让 ErrorHandler 重试
            throw e;
        }
    }
}
```

### 4. DLT 监控告警

```java
@Service
public class DLTAlerter {
    
    @KafkaListener(topics = "orders.DLT", groupId = "dlt-monitor")
    public void alert(ConsumerRecord<String, String> record) {
        String errorClass = getHeader(record, KafkaHeaders.DLT_EXCEPTION_FQCN);
        String errorMessage = getHeader(record, KafkaHeaders.DLT_EXCEPTION_MESSAGE);
        String originalTopic = getHeader(record, KafkaHeaders.DLT_ORIGINAL_TOPIC);
        int originalPartition = Integer.parseInt(getHeader(record, KafkaHeaders.DLT_ORIGINAL_PARTITION));
        long originalOffset = Long.parseLong(getHeader(record, KafkaHeaders.DLT_ORIGINAL_OFFSET));
        
        // 发送告警（钉钉/企业微信）
        String alertMessage = String.format(
            "🚨 DLT Message\n" +
            "原始 Topic: %s\n" +
            "分区: %d, Offset: %d\n" +
            "异常类型: %s\n" +
            "异常信息: %s",
            originalTopic, originalPartition, originalOffset, errorClass, errorMessage
        );
        
        sendAlert(alertMessage);
    }
}
```

## ⚠️ 常见问题

### 问题 1：DLT Topic 满

```
现象：DLT Topic 消息堆积
解决：
  1. 监控 + 告警
  2. 定期清理（retain 7-30 天）
  3. 人工处理后归档
```

### 问题 2：DLT 重试导致死循环

```
场景：DLT Consumer 失败 → 进入 DLT → 再失败
解决：
  1. DLT Consumer 不进 DLT（直接失败）
  2. 或单独的 DLT 重试 Topic
```

### 问题 3：DLT 影响正常消费

```
场景：DLT 消费慢影响正常 topic
解决：
  1. DLT 用独立 Consumer Group
  2. DLT Topic 单独集群（如果数据敏感）
```

## 🎯 总结

**死信队列核心要点**：
- ✅ Spring Kafka 内置 DLT 支持
- ✅ 推荐每业务 Topic 独立 DLT
- ✅ 重试 + DLT 是标准模式
- ✅ DLT Consumer 必须独立
- ✅ 监控 DLT 至关重要
- ⚠️ DLT 需定期清理
- ⚠️ DLT Consumer 不能失败再进 DLT

**下一步：** [📦 消息积压](/08-enterprise/backlog) — 消费慢处理

## 📚 跨站参考：📊 监控告警

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **observability** 站（[https://java-px.bot.cd/observability/](https://java-px.bot.cd/observability/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [mysql](https://java-px.bot.cd/mysql/) / [video](https://java-px.bot.cd/video/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。


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
