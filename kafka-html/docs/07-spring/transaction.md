---
title: Spring 事务
---

# 🔐 Spring 事务

> Spring Kafka 集成 Spring 事务，实现**端到端精确一次语义**。本章详解 Spring 中如何使用 Kafka 事务。

## 🎯 Kafka 事务 vs Spring 事务

```
Kafka 事务：
  - Producer 多消息原子性
  - 跨 Partition 原子写入
  - 需要 transactional.id

Spring 事务：
  - 数据库事务（JDBC / JPA）
  - 业务方法事务管理

Spring Kafka 集成：
  - Kafka 事务 + 数据库事务
  - 端到端精确一次
```

## 🔧 Kafka 事务

### 配置事务 Producer

```java
@Configuration
public class KafkaTransactionConfig {
    
    @Bean
    public ProducerFactory<String, String> producerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "my-tx-id");
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        // ...
        
        return new DefaultKafkaProducerFactory<>(props);
    }
}
```

### 使用 Kafka 事务

```java
@Service
public class TransferService {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    public void transfer(String from, String to, int amount) {
        kafkaTemplate.executeInTransaction(operations -> {
            operations.send("account-events", from, "{\"delta\": -" + amount + "}");
            operations.send("account-events", to, "{\"delta\": +" + amount + "}");
            return null;
        });
        // 事务自动提交
    }
}
```

## 🔧 Kafka + 数据库事务（ChainedTransactionManager）

### 传统方案（不推荐）

```java
// ⚠️ ChainedTransactionManager 已废弃
@Bean
public ChainedTransactionManager transactionManager(
        DataSourceTransactionManager dbTransactionManager,
        KafkaTransactionManager kafkaTransactionManager) {
    return new ChainedTransactionManager(dbTransactionManager, kafkaTransactionManager);
}
```

**问题**：
- 已废弃
- 复杂，性能差
- 边界场景难处理

## 🔧 推荐方案：Transactional Event Listener

### 思想

```
事务流程：
  1. 开启数据库事务
  2. 业务处理（写数据库）
  3. 数据库事务提交前，触发 Kafka 发送
  4. 数据库事务提交后，Kafka 消息可见

⚠️ 但 Kafka 消息可能发送失败（与 DB 事务不一致）
```

### 实现

```java
@Component
public class OrderEventPublisher {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    @TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
    public void publishOrderCreated(OrderCreatedEvent event) {
        // 只在数据库事务提交后发送
        kafkaTemplate.send("order-events", event.getOrderId(), event.toJson())
            .whenComplete((result, ex) -> {
                if (ex != null) {
                    log.error("Kafka send failed, but DB already committed", ex);
                    // 告警 + 补偿
                }
            });
    }
}
```

**问题**：
- DB 已提交，但 Kafka 发送失败
- 数据不一致
- 需补偿机制

## 🔧 最佳方案：Outbox Pattern

### 思想

```
事务流程：
  1. 开启数据库事务
  2. 业务处理
  3. 在同一事务中写 Outbox 表（待发送消息）
  4. 数据库事务提交
  5. 独立进程轮询 Outbox 表
  6. 发送到 Kafka
  7. 标记 Outbox 已发送

优势：
  ✅ DB 和 Kafka 消息原子性
  ✅ 不丢消息
  ✅ 至少一次语义
```

### 实现

```java
// 1. Outbox 表
CREATE TABLE outbox (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    topic VARCHAR(255) NOT NULL,
    key VARCHAR(255),
    value TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',  -- PENDING / SENT / FAILED
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP NULL
);

// 2. 业务服务
@Service
@Transactional
public class OrderService {
    
    @Autowired
    private OutboxRepository outboxRepository;
    
    public Order createOrder(OrderDTO dto) {
        // 1. 创建订单（DB）
        Order order = new Order(dto);
        orderRepository.save(order);
        
        // 2. 同一事务写入 Outbox
        Outbox outbox = new Outbox();
        outbox.setTopic("order-events");
        outbox.setKey(order.getId().toString());
        outbox.setValue(order.toJson());
        outbox.setStatus("PENDING");
        outboxRepository.save(outbox);
        
        return order;
        // 事务提交：Order 和 Outbox 一起写入
    }
}

// 3. Outbox 发送器
@Component
public class OutboxSender {
    
    @Autowired
    private OutboxRepository outboxRepository;
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    @Scheduled(fixedRate = 1000)
    public void sendPending() {
        List<Outbox> pending = outboxRepository.findByStatus("PENDING");
        
        for (Outbox outbox : pending) {
            try {
                kafkaTemplate.send(outbox.getTopic(), outbox.getKey(), outbox.getValue())
                    .whenComplete((result, ex) -> {
                        if (ex == null) {
                            outbox.setStatus("SENT");
                            outbox.setSentAt(LocalDateTime.now());
                            outboxRepository.save(outbox);
                        } else {
                            log.error("Failed to send outbox: id={}", outbox.getId(), ex);
                        }
                    });
            } catch (Exception e) {
                log.error("Send error", e);
            }
        }
    }
}
```

### Outbox 进阶：使用 Debezium CDC

```
架构：
  应用 → DB（带 Outbox 表）→ Debezium → Kafka

优势：
  ✅ 完全解耦
  ✅ 高可靠（基于 Binlog）
  ✅ 不影响业务性能

参考：
  https://debezium.io/
```

## 🔧 Spring Kafka 事务集成

### KafkaTransactionManager

```java
@Configuration
@EnableTransactionManagement
public class TransactionConfig {
    
    @Bean
    public ProducerFactory<String, String> producerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "my-tx-id");
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        return new DefaultKafkaProducerFactory<>(props);
    }
    
    @Bean
    public KafkaTransactionManager kafkaTransactionManager(ProducerFactory<String, String> producerFactory) {
        return new KafkaTransactionManager(producerFactory);
    }
}

// 配置使用 KafkaTransactionManager
@Bean
public PlatformTransactionManager transactionManager(
        KafkaTransactionManager kafkaTransactionManager) {
    return kafkaTransactionManager;
}
```

### 使用 @Transactional

```java
@Service
public class OrderService {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    @Transactional("kafkaTransactionManager")
    public void createOrder(OrderEvent event) {
        // Kafka 事务
        kafkaTemplate.send("orders", event.getOrderId(), event.toJson());
        
        // 业务逻辑（其他数据库操作）
        // ...
        
        // 事务自动提交（无异常时）
    }
}
```

## 🔧 实战：订单 + 库存 + 支付 事务

### Outbox 模式实战

```java
// 1. Outbox 实体
@Entity
@Table(name = "outbox")
public class OutboxEvent {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    private String topic;
    private String key;
    @Column(length = 4000)
    private String value;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime sentAt;
}

// 2. 业务服务（事务性写 Outbox）
@Service
@Transactional
public class OrderService {
    
    @Autowired
    private OrderRepository orderRepository;
    @Autowired
    private OutboxRepository outboxRepository;
    
    public Order createOrder(OrderDTO dto) {
        // 1. 业务处理
        Order order = new Order(dto);
        orderRepository.save(order);
        
        // 2. 写 Outbox（同一事务）
        OutboxEvent event = new OutboxEvent();
        event.setTopic("order-events");
        event.setKey(order.getId().toString());
        event.setValue(order.toJson());
        event.setStatus("PENDING");
        outboxRepository.save(event);
        
        // 3. 事务提交
        return order;
    }
    
    @Transactional
    public void updateOrderStatus(Long orderId, String status) {
        // 1. 更新订单状态
        Order order = orderRepository.findById(orderId).orElseThrow();
        order.setStatus(status);
        orderRepository.save(order);
        
        // 2. 写 Outbox
        OutboxEvent event = new OutboxEvent();
        event.setTopic("order-status-events");
        event.setKey(orderId.toString());
        event.setValue("{\"orderId\":" + orderId + ",\"status\":\"" + status + "\"}");
        outboxRepository.save(event);
    }
}

// 3. Outbox 发送器
@Component
public class OutboxPoller {
    
    @Autowired
    private OutboxRepository outboxRepository;
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    @Scheduled(fixedDelay = 100)
    @Transactional
    public void pollAndSend() {
        List<OutboxEvent> pending = outboxRepository.findTop100ByStatusOrderById("PENDING");
        
        for (OutboxEvent event : pending) {
            try {
                kafkaTemplate.send(event.getTopic(), event.getKey(), event.getValue())
                    .whenComplete((result, ex) -> {
                        if (ex == null) {
                            event.setStatus("SENT");
                            event.setSentAt(LocalDateTime.now());
                            outboxRepository.save(event);
                        } else {
                            log.error("Send failed", ex);
                        }
                    });
            } catch (Exception e) {
                log.error("Outbox send error", e);
            }
        }
    }
}
```

## 🔧 Consumer 端事务（精确一次）

### read_committed + 手动提交

```java
@Configuration
public class ConsumerTransactionConfig {
    
    @Bean
    public ConsumerFactory<String, String> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processor");
        props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");  // 关键
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        // ...
        return new DefaultKafkaConsumerFactory<>(props);
    }
}
```

### 消费 + 业务 + 发送下游（事务）

```java
@Service
public class ExactOnceConsumer {
    
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;
    
    @KafkaListener(topics = "orders")
    public void consume(ConsumerRecord<String, String> record, Acknowledgment ack) {
        kafkaTemplate.executeInTransaction(operations -> {
            // 1. 处理业务（写数据库）
            Order order = processOrder(record);
            
            // 2. 发送到下游
            operations.send("processed-orders", order.getId(), order.toJson());
            
            // 3. 提交 Offset（与下游消息原子）
            Map<TopicPartition, OffsetAndMetadata> offsets = Map.of(
                new TopicPartition(record.topic(), record.partition()),
                new OffsetAndMetadata(record.offset() + 1)
            );
            operations.sendOffsetsToTransaction(offsets, consumerGroupMetadata());
            
            // 事务提交（三者原子）
            return null;
        });
        
        ack.acknowledge();
    }
}
```

## 🔧 事务监控

```java
@Component
public class TransactionMonitor {
    
    @Autowired
    private OutboxRepository outboxRepository;
    
    @Scheduled(fixedRate = 60000)
    public void monitorOutboxLag() {
        long pendingCount = outboxRepository.countByStatus("PENDING");
        long failedCount = outboxRepository.countByStatus("FAILED");
        
        if (pendingCount > 10000) {
            alert("Outbox lag too high: " + pendingCount);
        }
        if (failedCount > 0) {
            alert("Outbox send failed: " + failedCount);
        }
    }
}
```

## ⚠️ 常见问题

### 问题 1：事务与 ChainedTransactionManager 已废弃

```
⚠️ Spring 5.x 后 ChainedTransactionManager 已废弃
解决：
  1. 使用 Outbox 模式（推荐）
  2. 使用 Debezium CDC
  3. 手动管理事务边界
```

### 问题 2：Outbox 积压

```
原因：发送速度跟不上生产速度
解决：
  1. 增加并发发送
  2. 增加 Kafka 吞吐
  3. 监控 Outbox lag
```

### 问题 3：事务死锁

```
原因：循环依赖（如 A 等待 B，B 等待 A）
解决：
  1. 避免事务嵌套
  2. 事务尽量短
  3. 合理设置超时
```

## 🎯 总结

**Spring 事务核心要点**：
- ✅ Kafka 事务支持多消息原子写入
- ✅ ChainedTransactionManager 已废弃
- ✅ 推荐 Outbox 模式（数据库事务 + 异步发送）
- ✅ Debezium CDC 是企业级方案
- ✅ Consumer 端 read_committed + 事务发送
- ⚠️ 事务不是万能的，需结合业务场景设计
- ⚠️ Outbox 表可能成为性能瓶颈

**下一步：** [⚙️ Spring Boot 集成](/07-spring/spring-boot) — Spring Boot 配置最佳实践


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
