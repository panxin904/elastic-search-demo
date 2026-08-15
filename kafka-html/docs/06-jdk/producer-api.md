---
title: Producer API
---

# ✍️ Producer API

> Kafka Java Producer 是与 Kafka 集群交互的官方客户端。本章详解 Producer API 的核心用法。

## 🎯 引入依赖

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>3.7.0</version>
</dependency>
```

## 🚀 快速开始

### 最简单的 Producer

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

KafkaProducer<String, String> producer = new KafkaProducer<>(props);

// 发送消息
producer.send(new ProducerRecord<>("orders", "key1", "value1"));

// 同步关闭（flush + close）
producer.close();
```

### 带回调的 Producer

```java
KafkaProducer<String, String> producer = new KafkaProducer<>(props);

// 异步发送 + 回调
producer.send(new ProducerRecord<>("orders", "key1", "value1"), new Callback() {
    @Override
    public void onCompletion(RecordMetadata metadata, Exception exception) {
        if (exception == null) {
            System.out.printf("Sent: topic=%s, partition=%d, offset=%d%n",
                metadata.topic(), metadata.partition(), metadata.offset());
        } else {
            exception.printStackTrace();
        }
    }
});

// flush 等待所有消息发送完成
producer.flush();

// 关闭
producer.close();
```

## 📝 ProducerRecord 详解

### 5 种构造方式

```java
// 1. 仅指定 topic 和 value（key 自动分配）
ProducerRecord<String, String> r1 = new ProducerRecord<>("orders", "value1");

// 2. 指定 topic、key、value（key 用于分区路由）
ProducerRecord<String, String> r2 = new ProducerRecord<>("orders", "key1", "value1");

// 3. 指定 topic、partition、key、value（指定分区）
ProducerRecord<String, String> r3 = new ProducerRecord<>("orders", 0, "key1", "value1");

// 4. 指定 topic、partition、timestamp、key、value（指定时间戳）
ProducerRecord<String, String> r4 = new ProducerRecord<>("orders", 0, System.currentTimeMillis(), "key1", "value1");

// 5. 带 Headers（元数据）
ProducerRecord<String, String> r5 = new ProducerRecord<>("orders", "key1", "value1");
r5.headers().add("traceId", "abc123".getBytes());
r5.headers().add("source", "order-service".getBytes());
```

## 📊 关键配置

```java
Properties props = new Properties();

// ==== 必填 ====
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

// ==== 可靠性 ====
props.put(ProducerConfig.ACKS_CONFIG, "all");
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);
props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);

// ==== 性能 ====
props.put(ProducerConfig.LINGER_MS_CONFIG, 20);
props.put(ProducerConfig.BATCH_SIZE_CONFIG, 65536);
props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");
props.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 67108864);

// ==== 超时 ====
props.put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, 30000);
props.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, 120000);

// ==== 客户端标识 ====
props.put(ProducerConfig.CLIENT_ID_CONFIG, "order-service");
```

## 🔧 发送模式

### 异步发送（Fire-and-Forget）

```java
// 不关心结果，性能最高
producer.send(new ProducerRecord<>("orders", "key1", "value1"));
```

**适用场景**：
- 日志收集
- 监控指标
- 可以容忍少量消息丢失

### 同步发送（Get Future）

```java
// 阻塞等待结果
Future<RecordMetadata> future = producer.send(new ProducerRecord<>("orders", "key1", "value1"));
RecordMetadata metadata = future.get();  // 阻塞
System.out.println("Sent: " + metadata);

// 或带超时
RecordMetadata metadata = future.get(10, TimeUnit.SECONDS);
```

**适用场景**：
- 需要立即知道结果
- 业务流程依赖消息发送成功

### 异步回调（Callback）

```java
// 推荐：非阻塞 + 回调
producer.send(new ProducerRecord<>("orders", "key1", "value1"), new Callback() {
    @Override
    public void onCompletion(RecordMetadata metadata, Exception exception) {
        if (exception == null) {
            // 发送成功
            log.info("Sent to partition={}, offset={}",
                metadata.partition(), metadata.offset());
        } else {
            // 发送失败
            log.error("Send failed", exception);
            // 重试或告警
        }
    }
});
```

**适用场景**：
- 高吞吐（推荐）
- 业务不阻塞
- 异步处理错误

## 🔧 完整示例

### 用户消息发送服务

```java
@Service
public class MessageService {
    
    private final KafkaProducer<String, String> producer;
    
    public MessageService() {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        props.put(ProducerConfig.LINGER_MS_CONFIG, 10);
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, 65536);
        props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");
        props.put(ProducerConfig.CLIENT_ID_CONFIG, "message-service");
        
        this.producer = new KafkaProducer<>(props);
    }
    
    public CompletableFuture<Void> sendOrderEvent(OrderEvent event) {
        return CompletableFuture.runAsync(() -> {
            ProducerRecord<String, String> record = new ProducerRecord<>(
                "order-events",      // topic
                event.getOrderId(),  // key（同订单事件进入同一 Partition）
                event.toJson()       // value
            );
            
            // 添加 Headers（用于链路追踪）
            record.headers().add("traceId", MDC.get("traceId").getBytes());
            record.headers().add("source", "order-service".getBytes());
            
            producer.send(record, new Callback() {
                @Override
                public void onCompletion(RecordMetadata metadata, Exception exception) {
                    if (exception == null) {
                        log.info("Order event sent: orderId={}, partition={}, offset={}",
                            event.getOrderId(), metadata.partition(), metadata.offset());
                    } else {
                        log.error("Send order event failed: orderId={}", event.getOrderId(), exception);
                        // 业务处理：重试、告警、记录到死信队列
                    }
                }
            });
        });
    }
    
    @PreDestroy
    public void close() {
        producer.flush();
        producer.close();
    }
}
```

## 🔧 拦截器

```java
// 自定义拦截器
public class TraceIdInterceptor implements ProducerInterceptor<String, String> {
    
    @Override
    public ProducerRecord<String, String> onSend(ProducerRecord<String, String> record) {
        // 添加 traceId
        String traceId = MDC.get("traceId");
        if (traceId != null) {
            record.headers().add("traceId", traceId.getBytes());
        }
        return record;
    }
    
    @Override
    public void onAcknowledgement(RecordMetadata metadata, Exception exception) {
        if (exception == null) {
            Metrics.counter("kafka_producer_success_total").increment();
        } else {
            Metrics.counter("kafka_producer_error_total").increment();
        }
    }
    
    @Override
    public void close() {
        // 清理资源
    }
    
    @Override
    public void configure(Map<String, ?> configs) {
        // 配置回调
    }
}

// 配置
props.put(ProducerConfig.INTERCEPTOR_CLASSES_CONFIG, TraceIdInterceptor.class.getName());
```

## 🔧 分区器

```java
// 自定义分区器：按业务类型路由
public class OrderPartitioner implements Partitioner {
    
    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        // 1. 优先按 Key 的 hash
        if (keyBytes != null) {
            return Utils.toPositive(Utils.murmur2(keyBytes)) % 
                cluster.partitionsForTopic(topic).size();
        }
        
        // 2. 无 Key，按 value 业务类型路由
        if (value instanceof OrderEvent) {
            OrderEvent event = (OrderEvent) value;
            return Math.abs(event.getType().hashCode() % cluster.partitionsForTopic(topic).size());
        }
        
        // 3. 兜底：使用粘性分区（Kafka 2.4+ 优化）
        return -1;
    }
    
    @Override
    public void close() {}
    
    @Override
    public void configure(Map<String, ?> configs) {}
}

// 配置
props.put(ProducerConfig.PARTITIONER_CLASS_CONFIG, OrderPartitioner.class.getName());
```

## 🔧 序列化器

```java
// 自定义 JSON 序列化器
public class JsonSerializer<T> implements Serializer<T> {
    
    private final ObjectMapper mapper = new ObjectMapper();
    
    @Override
    public byte[] serialize(String topic, T data) {
        if (data == null) return null;
        try {
            return mapper.writeValueAsBytes(data);
        } catch (Exception e) {
            throw new SerializationException("Failed to serialize " + data, e);
        }
    }
}

// 使用
KafkaProducer<String, OrderEvent> producer = new KafkaProducer<>(propsWithJsonSerializer);
producer.send(new ProducerRecord<>("orders", orderId, new OrderEvent(...)));
```

## 🔧 Header 传递

```java
// Producer 端设置 Header
ProducerRecord<String, String> record = new ProducerRecord<>("orders", "key", "value");
record.headers().add("traceId", "abc-123".getBytes());
record.headers().add("source", "order-service".getBytes());
record.headers().add("version", "v1".getBytes());

producer.send(record);

// Consumer 端读取 Header
@KafkaListener(topics = "orders")
public void consume(ConsumerRecord<String, String> record) {
    String traceId = new String(record.headers().lastHeader("traceId").value());
    String source = new String(record.headers().lastHeader("source").value());
    
    MDC.put("traceId", traceId);
    log.info("Process from {}", source);
}
```

## ⚠️ 异常处理

```java
producer.send(record, new Callback() {
    @Override
    public void onCompletion(RecordMetadata metadata, Exception exception) {
        if (exception == null) {
            // 成功
            return;
        }
        
        // 异常分类
        if (exception instanceof RetriableException) {
            // 可重试异常（网络抖动、Leader 切换）
            log.warn("Retriable error", exception);
            // Kafka 自动重试
            
        } else if (exception instanceof AuthorizationException) {
            // 权限异常（不可重试）
            log.error("Auth failed", exception);
            alarm();
            
        } else if (exception instanceof RecordTooLargeException) {
            // 消息过大（不可重试）
            log.error("Message too large", exception);
            sendToDeadLetter(record);
            
        } else if (exception instanceof SerializationException) {
            // 序列化失败（不可重试）
            log.error("Serialize failed", exception);
            
        } else {
            log.error("Unknown error", exception);
        }
    }
});
```

## 🎯 总结

**Producer API 核心要点**：
- ✅ KafkaProducer 线程安全，可共享
- ✅ 5 种 ProducerRecord 构造方式
- ✅ 3 种发送模式：异步、Future、Callback
- ✅ 拦截器、横幅器、序列化器可扩展
- ✅ 回调处理错误分类
- ⚠️ Producer 关闭前必须 flush()
- ⚠️ 序列化失败不可重试

**下一步：** [📥 Consumer API](/06-jdk/consumer-api) — Java 消费者详解
