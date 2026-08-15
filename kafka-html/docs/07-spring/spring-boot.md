---
title: Spring Boot 集成
---

# ⚙️ Spring Boot 集成

> Spring Boot 为 Kafka 提供了**自动配置**，本章详解 Spring Boot 集成 Kafka 的最佳实践。

## 🎯 引入依赖

```xml
<!-- Spring Boot Starter -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter</artifactId>
</dependency>

<!-- Spring for Apache Kafka -->
<dependency>
    <groupId>org.springframework.kafka</groupId>
    <artifactId>spring-kafka</artifactId>
</dependency>
```

## 🚀 快速开始

### 1. 完整 application.yml

```yaml
spring:
  application:
    name: order-service
  
  kafka:
    # ==== 通用配置 ====
    bootstrap-servers: localhost:9092
    client-id: order-service
    
    # ==== Producer 配置 ====
    producer:
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      acks: all
      retries: 3
      batch-size: 16384
      buffer-memory: 33554432
      compression-type: lz4
      properties:
        enable.idempotence: true
        max.in.flight.requests.per.connection: 5
        linger.ms: 10
        delivery.timeout.ms: 120000
        request.timeout.ms: 30000
    
    # ==== Consumer 配置 ====
    consumer:
      group-id: order-processor
      auto-offset-reset: earliest
      enable-auto-commit: false
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      max-poll-records: 500
      properties:
        spring.json.trusted.packages: 'com.example.model'
        spring.json.value.default.type: com.example.model.OrderEvent
        session.timeout.ms: 30000
        heartbeat.interval.ms: 10000
        isolation.level: read_committed
    
    # ==== Listener 配置 ====
    listener:
      ack-mode: manual_immediate
      concurrency: 3
      missing-topics-fatal: false
      poll-timeout: 500
      type: single
      properties:
        spring.json.trusted.packages: 'com.example.model'
```

### 2. 实体类

```java
@Data
@AllArgsConstructor
@NoArgsConstructor
public class OrderEvent {
    private String orderId;
    private String userId;
    private BigDecimal amount;
    private String status;
    private LocalDateTime createdAt;
}
```

### 3. Producer

```java
@Service
public class OrderProducer {
    
    @Autowired
    private KafkaTemplate<String, OrderEvent> kafkaTemplate;
    
    public void sendOrder(OrderEvent event) {
        kafkaTemplate.send("orders", event.getOrderId(), event)
            .whenComplete((result, ex) -> {
                if (ex == null) {
                    log.info("Order sent: {}", result.getRecordMetadata().offset());
                } else {
                    log.error("Send failed", ex);
                }
            });
    }
}
```

### 4. Consumer

```java
@Service
public class OrderConsumer {
    
    @KafkaListener(topics = "orders", groupId = "order-processor")
    public void consume(OrderEvent event, Acknowledgment ack) {
        try {
            log.info("Order received: {}", event);
            processOrder(event);
            ack.acknowledge();
        } catch (Exception e) {
            log.error("Process failed", e);
        }
    }
    
    private void processOrder(OrderEvent event) {
        // 业务处理
    }
}
```

## 🔧 JSON 序列化配置

### Producer JSON 序列化

```yaml
spring:
  kafka:
    producer:
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      properties:
        # 添加类型信息（用于 Consumer 反序列化）
        spring.json.add.type.headers: true
```

### Consumer JSON 反序列化

```yaml
spring:
  kafka:
    consumer:
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      properties:
        # 信任的包（反序列化时允许）
        spring.json.trusted.packages: 'com.example.order,com.example.payment'
        # 默认类型（header 中无类型时使用）
        spring.json.value.default.type: com.example.order.OrderEvent
```

### 指定 Type Header 禁用

```java
// 在 Producer 端禁用类型 header（减少体积）
@Bean
public ProducerFactory<String, OrderEvent> producerFactory() {
    Map<String, Object> props = new HashMap<>();
    props.put(JsonSerializer.ADD_TYPE_INFO_HEADERS, false);
    // ...
}
```

## 🔧 自定义配置

### 自定义 Producer

```java
@Configuration
public class KafkaProducerConfig {
    
    @Bean
    public ProducerFactory<String, OrderEvent> orderProducerFactory(KafkaProperties properties) {
        Map<String, Object> props = properties.buildProducerProperties();
        
        // 自定义配置
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        props.put(ProducerConfig.LINGER_MS_CONFIG, 20);
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, 65536);
        
        return new DefaultKafkaProducerFactory<>(props, 
            new StringSerializer(),
            new JsonSerializer<>(OrderEvent.class));
    }
    
    @Bean
    public KafkaTemplate<String, OrderEvent> orderKafkaTemplate() {
        return new KafkaTemplate<>(orderProducerFactory(null));
    }
}
```

### 自定义 Consumer

```java
@Configuration
public class KafkaConsumerConfig {
    
    @Bean
    public ConsumerFactory<String, OrderEvent> orderConsumerFactory(KafkaProperties properties) {
        Map<String, Object> props = properties.buildConsumerProperties();
        
        // 自定义配置
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processor");
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
        
        JsonDeserializer<OrderEvent> deserializer = new JsonDeserializer<>(OrderEvent.class);
        deserializer.addTrustedPackages("com.example.*");
        
        return new DefaultKafkaConsumerFactory<>(props,
            new StringDeserializer(),
            deserializer);
    }
    
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, OrderEvent> orderListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, OrderEvent> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(orderConsumerFactory(null));
        factory.setConcurrency(3);
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL_IMMEDIATE);
        return factory;
    }
}
```

## 🔧 多 Kafka 集群

### 配置

```java
@Configuration
public class MultiKafkaConfig {
    
    @Bean
    public KafkaTemplate<String, String> primaryKafkaTemplate() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "primary-kafka:9092");
        // ...
        return new KafkaTemplate<>(new DefaultKafkaProducerFactory<>(props));
    }
    
    @Bean
    public KafkaTemplate<String, String> secondaryKafkaTemplate() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "secondary-kafka:9092");
        // ...
        return new KafkaTemplate<>(new DefaultKafkaProducerFactory<>(props));
    }
}
```

### 使用

```java
@Service
public class MultiClusterProducer {
    
    @Autowired
    @Qualifier("primaryKafkaTemplate")
    private KafkaTemplate<String, String> primaryTemplate;
    
    @Autowired
    @Qualifier("secondaryKafkaTemplate")
    private KafkaTemplate<String, String> secondaryTemplate;
    
    public void sendToPrimary(String message) {
        primaryTemplate.send("topic1", message);
    }
    
    public void sendToSecondary(String message) {
        secondaryTemplate.send("topic2", message);
    }
}
```

## 🔧 监听器配置

### 监听器 + 错误处理

```java
@Configuration
public class KafkaListenerConfig {
    
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory(
            ConsumerFactory<String, String> consumerFactory,
            KafkaTemplate<String, String> kafkaTemplate) {
        
        ConcurrentKafkaListenerContainerFactory<String, String> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory);
        factory.setConcurrency(3);
        
        // 错误处理：重试 + 死信队列
        DeadLetterPublishingRecoverer recoverer = new DeadLetterPublishingRecoverer(
            kafkaTemplate,
            (record, ex) -> new TopicPartition("orders.DLT", record.partition())
        );
        
        ExponentialBackOff backOff = new ExponentialBackOff(1000L, 2.0);
        factory.setCommonErrorHandler(new DefaultErrorHandler(recoverer, backOff));
        
        return factory;
    }
}
```

### 条件化监听器

```java
@Component
@ConditionalOnProperty(name = "app.kafka.consumer.enabled", havingValue = "true", matchIfMissing = true)
public class ConditionalKafkaConsumer {
    
    @KafkaListener(topics = "orders")
    public void consume(OrderEvent event) {
        // 只有配置启用时才生效
        processOrder(event);
    }
}
```

## 🔧 健康检查

```yaml
# application.yml
spring:
  kafka:
    # 健康检查
    health:
      enabled: true
      # 检查间隔
      interval: 30s
      # 异常时是否启动
      fail-fast: false
```

### 自定义健康检查

```java
@Component
public class KafkaHealthIndicator implements HealthIndicator {
    
    @Autowired
    private AdminClient adminClient;
    
    @Override
    public Health health() {
        try {
            DescribeClusterResult result = adminClient.describeCluster();
            int nodeCount = result.nodes().get(5, TimeUnit.SECONDS).size();
            return Health.up()
                .withDetail("nodes", nodeCount)
                .withDetail("controller", result.controller().get().id())
                .build();
        } catch (Exception e) {
            return Health.down(e).build();
        }
    }
}
```

## 🔧 监控集成

### Micrometer 集成

```yaml
spring:
  kafka:
    # 启用 Micrometer 指标
    properties:
      metrics.recording.level: INFO
```

```java
@Component
public class KafkaMetrics {
    
    private final MeterRegistry meterRegistry;
    private final Counter messagesSent;
    private final Counter messagesError;
    
    public KafkaMetrics(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.messagesSent = Counter.builder("kafka_messages_sent_total")
            .description("Total Kafka messages sent")
            .register(meterRegistry);
        this.messagesError = Counter.builder("kafka_messages_error_total")
            .description("Total Kafka send errors")
            .register(meterRegistry);
    }
    
    public void recordSent() {
        messagesSent.increment();
    }
    
    public void recordError() {
        messagesError.increment();
    }
}
```

### Prometheus 暴露

```yaml
# application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always
    prometheus:
      enabled: true
  metrics:
    tags:
      application: order-service
```

```bash
# 访问指标
curl http://localhost:8080/actuator/prometheus
```

## 🔧 测试

### 单元测试

```java
@SpringBootTest
@EmbeddedKafka(topics = "orders", partitions = 1)
public class OrderProducerTest {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    @Autowired
    private EmbeddedKafkaBroker broker;
    
    @Test
    public void testSendOrder() throws Exception {
        kafkaTemplate.send("orders", "key1", "value1").get(10, TimeUnit.SECONDS);
        
        // 验证
        ConsumerRecord<String, String> record = 
            KafkaTestUtils.getSingleRecord(consumer, "orders");
        assertEquals("value1", record.value());
    }
}
```

### 集成测试（Testcontainers）

```java
@SpringBootTest
@Testcontainers
class KafkaIntegrationTest {
    
    @Container
    static KafkaContainer kafka = new KafkaContainer(
        DockerImageName.parse("confluentinc/cp-kafka:7.5.0"));
    
    @DynamicPropertySource
    static void kafkaProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.kafka.bootstrap-servers", kafka::getBootstrapServers);
    }
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    @Test
    void testKafkaIntegration() {
        // 完整测试
        kafkaTemplate.send("test-topic", "key", "value");
        // 验证
    }
}
```

## 🛠️ 实战：Spring Boot 微服务集成

```yaml
# application.yml 完整配置
spring:
  application:
    name: order-service
  
  kafka:
    bootstrap-servers: kafka1:9092,kafka2:9092,kafka3:9092
    client-id: ${spring.application.name}
    
    producer:
      acks: all
      retries: 3
      batch-size: 65536
      buffer-memory: 67108864
      compression-type: lz4
      key-serializer: org.apache.kafka.common.serialization.StringSerializer
      value-serializer: org.springframework.kafka.support.serializer.JsonSerializer
      properties:
        enable.idempotence: true
        max.in.flight.requests.per.connection: 5
        linger.ms: 20
        delivery.timeout.ms: 120000
    
    consumer:
      group-id: order-processor
      auto-offset-reset: earliest
      enable-auto-commit: false
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: org.springframework.kafka.support.serializer.JsonDeserializer
      max-poll-records: 500
      properties:
        spring.json.trusted.packages: 'com.example.*'
        session.timeout.ms: 30000
        heartbeat.interval.ms: 10000
        isolation.level: read_committed
    
    listener:
      ack-mode: manual_immediate
      concurrency: 3
      missing-topics-fatal: false

management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: always
```

```java
@SpringBootApplication
@EnableKafka
public class OrderServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderServiceApplication.class, args);
    }
}
```

## ⚠️ 常见问题

### 问题 1：Spring Boot 启动失败

```
原因：Kafka 连接失败
解决：
  1. 检查 bootstrap-servers
  2. 关闭健康检查启动失败（fail-fast: false）
```

### 问题 2：JSON 反序列化失败

```
原因：包名不在 trusted.packages
解决：
  spring.json.trusted.packages: 'com.example.*'
```

### 问题 3：Listener 不消费

```
原因：Offset 已提交，无新数据
解决：
  1. 重置 Group Offset
  2. 或修改 group-id（重新消费）
```

## 🎯 总结

**Spring Boot 集成核心要点**：
- ✅ spring-kafka 简化开发
- ✅ application.yml 集中配置
- ✅ 自动配置 KafkaTemplate + Listener
- ✅ JSON 序列化通过 spring.json.trusted.packages
- ✅ 健康检查 + 监控集成
- ✅ 单元测试（@EmbeddedKafka）+ 集成测试（Testcontainers）
- ⚠️ 多集群需自定义配置
- ⚠️ 监控指标配置

**下一步：** [🔁 消息幂等性](/08-enterprise/idempotent) — 实战中的消息幂等
