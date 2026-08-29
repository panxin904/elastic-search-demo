---
title: 生产者原理
date: 2026-08-15  # date-auto-injected
---

# 🎯 生产者原理

> Kafka Producer 是高性能消息发送客户端。本章深入 Producer 内部机制，理解**消息发送流程、序列化器、分区器、累加器**等核心组件。

## 🏗️ Producer 架构

```
┌──────────────────────────────────────────────────────────┐
│                    Kafka Producer                          │
│                                                            │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│  │ 拦截器   │ → │ 序列化器 │ → │ 分区器   │               │
│  └──────────┘   └──────────┘   └──────────┘               │
│        ↓                                          ↓        │
│  ┌─────────────────────────────────────────────────────┐ │
│  │           RecordAccumulator (累加器)                  │ │
│  │   按 Partition 分组的双端队列                        │ │
│  │   [Partition 1][Partition 2][Partition 3]          │ │
│  └─────────────────────────────────────────────────────┘ │
│        ↓                                                  │
│  ┌──────────┐                                             │
│  │  Sender  │ (后台线程，异步发送)                       │
│  └──────────┘                                             │
│        ↓                                                  │
│  ┌──────────┐                                             │
│  │ Selector│ (NIO 网络通信)                              │
│  └──────────┘                                             │
└──────────────────────────────────────────────────────────┘
                ↓ 网络
        Kafka Broker
```

## 🎯 核心组件

### 1. 拦截器（ProducerInterceptor）

```
作用：在消息发送前后进行自定义处理
时机：
  - onSend(record)：发送前调用（可修改 record）
  - onAcknowledgement(metadata, exception)：收到 ack 后调用

典型用途：
  - 添加全局 TraceId
  - 消息加密
  - 监控埋点
  - 敏感信息脱敏
```

```java
public class TraceIdInterceptor implements ProducerInterceptor<String, String> {
    
    @Override
    public ProducerRecord<String, String> onSend(ProducerRecord<String, String> record) {
        // 添加 traceId 到 header
        record.headers().add("traceId", UUID.randomUUID().toString().getBytes());
        return record;
    }
    
    @Override
    public void onAcknowledgement(RecordMetadata metadata, Exception exception) {
        if (exception == null) {
            // 发送成功
            log.info("Sent: {}", metadata);
        } else {
            // 发送失败
            log.error("Send failed", exception);
        }
    }
}

// 配置
props.put(ProducerConfig.INTERCEPTOR_CLASSES_CONFIG, TraceIdInterceptor.class.getName());
```

### 2. 序列化器（Serializer）

```
作用：将 Java 对象转换为字节数组
默认：Kafka 内置基本类型序列化器

常见序列化器：
  - StringSerializer
  - ByteArraySerializer
  - IntegerSerializer / LongSerializer
  - 自定义序列化器（JSON / Avro / Protobuf）

⚠️ 序列化器要求：
  - 生产者和消费者必须使用兼容的序列化方式
  - 字段顺序要一致
  - 反序列化失败会丢消息
```

```java
// 自定义 JSON 序列化器
public class JsonSerializer<T> implements Serializer<T> {
    
    private ObjectMapper mapper = new ObjectMapper();
    
    @Override
    public byte[] serialize(String topic, T data) {
        if (data == null) return null;
        try {
            return mapper.writeValueAsBytes(data);
        } catch (JsonProcessingException e) {
            throw new SerializationException("Failed to serialize", e);
        }
    }
}

// 推荐：使用 Jackson / FastJSON
public class User {
    private Long id;
    private String name;
    // ... getter/setter
}
```

### 3. 分区器（Partitioner）

```
作用：决定消息发送到哪个 Partition
默认：DefaultPartitioner

分区策略（优先级）：
  1. ProducerRecord 指定了 partition → 直接使用
  2. 指定了 key → hash(key) % partitions
  3. 无 key → 轮询所有分区
```

```java
// 自定义分区器
public class OrderPartitioner implements Partitioner {
    
    @Override
    public int partition(String topic, Object key, byte[] keyBytes, 
                        Object value, byte[] valueBytes, Cluster cluster) {
        List<PartitionInfo> partitions = cluster.partitionsForTopic(topic);
        int size = partitions.size();
        
        // 订单按用户 ID 路由
        if (key instanceof String) {
            String keyStr = (String) key;
            if (keyStr.startsWith("VIP_")) {
                // VIP 用户走专门分区
                return 0;
            }
        }
        
        // 普通用户按 hash 分布
        return Utils.toPositive(Utils.murmur2(keyBytes)) % size;
    }
}

// 配置
props.put(ProducerConfig.PARTITIONER_CLASS_CONFIG, OrderPartitioner.class.getName());
```

### 4. RecordAccumulator（累加器）

```
作用：缓存消息，按 Partition 分组，达到 batch.size 后批量发送
结构：
  - 每个 Partition 一个双端队列（Deque<ProducerBatch>）
  - 多个消息追加到同一 Batch（变长）
  - Batch 满了或 linger.ms 到期就发送

线程模型：
  - 主线程：累加消息
  - Sender 线程：异步发送 Batch
  - 减少网络 IO 次数
```

```
RecordAccumulator:
  Topic: orders
    ├─ Partition 0: [Batch1][Batch2][Batch3]  (Deque)
    ├─ Partition 1: [Batch1][Batch2]
    └─ Partition 2: [Batch1]
```

### 5. Sender 线程

```
作用：后台线程，从 RecordAccumulator 拉取 Batch 发送到 Broker
工作流程：
  1. 从累加器获取就绪的 Batch
  2. 包装成 ClientRequest
  3. 通过 NIO Selector 发送到 Broker
  4. 处理响应（更新 offset、回调、错误处理）

并发模型：
  - 单 Sender 线程（Kafka 3.x 之前）
  - Kafka 3.x 支持多 Sender 线程（提升吞吐）
```

## 🔄 消息发送完整流程

```
1. 应用调用 producer.send(record, callback)
   ↓
2. 拦截器 onSend(record)  [可选]
   ↓
3. 序列化器 serialize(key) + serialize(value)
   ↓
4. 分区器 partition(topic, key)
   ↓
5. 累加器 append(partition, record)
   ├─ 找到对应 partition 的 Batch
   ├─ 加入 Batch（如 Batch 满了或 linger.ms 到期，发起新 Batch）
   └─ 唤醒 Sender 线程
   ↓
6. Sender 线程异步处理
   ├─ 拉取就绪的 Batch
   ├─ 发送到对应的 Broker Leader
   ├─ 等待 Broker 响应
   └─ 触发 callback（成功 / 失败）
   ↓
7. 返回 Future<RecordMetadata>
```

## 📊 关键配置

```properties
# ==== 必填 ====
bootstrap.servers=localhost:9092
key.serializer=org.apache.kafka.common.serialization.StringSerializer
value.serializer=org.apache.kafka.common.serialization.StringSerializer

# ==== 可靠性 ====
acks=all                          # 等待所有 ISR 同步
retries=2147483647                # 无限重试（默认）
enable.idempotence=true            # 幂等性（推荐开启）
max.in.flight.requests.per.connection=5  # 最多 5 个未确认请求

# ==== 性能调优 ====
linger.ms=10                      # 等待 10ms 收集更多消息（默认 0）
batch.size=65536                  # 批量大小（默认 16KB）
compression.type=lz4              # 压缩算法
buffer.memory=33554432            # 累加器总内存（默认 32MB）

# ==== 超时 ====
request.timeout.ms=30000          # 单个请求超时
delivery.timeout.ms=120000        # 总超时（包括重试）

# ==== 其他 ====
client.id=producer-1              # 客户端 ID（用于日志追踪）
```

## 📊 性能优化

### 调优 Batch 发送

```properties
# 增大 batch.size（提高吞吐）
batch.size=131072  # 128KB（默认 16KB）

# 增加 linger.ms（让更多消息进入同一 Batch）
linger.ms=20       # 20ms（默认 0）

# 增大累加器内存
buffer.memory=67108864  # 64MB（默认 32MB）
```

### 调优压缩

```properties
# lz4：解压快（推荐）
compression.type=lz4

# zstd：高压缩比（Kafka 2.1+，推荐）
compression.type=zstd

# 启用压缩后：
# - 网络传输减少（节省带宽）
# - 磁盘 IO 减少（节省空间）
# - 略微增加 CPU 开销
```

### 调优并发

```properties
# 最多未确认请求数（影响吞吐和延迟）
max.in.flight.requests.per.connection=5  # 默认 5

# 启用幂等性后最大只能是 5
enable.idempotence=true
```

## 🛠️ 实战代码

### 基础 Producer

```java
Properties props = new Properties();
props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

KafkaProducer<String, String> producer = new KafkaProducer<>(props);

// 异步发送
for (int i = 0; i < 100; i++) {
    producer.send(new ProducerRecord<>("orders", "key-" + i, "value-" + i));
}

// 同步发送（带回调）
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

producer.close();
```

### 带 Key 的 Producer

```java
// 同 key 进入同 partition（保证顺序）
for (int i = 0; i < 100; i++) {
    String userId = "user" + (i % 10);  // 10 个用户
    producer.send(new ProducerRecord<>("orders", userId, "msg-" + i));
}
```

### 自定义分区器

```java
public class BusinessPartitioner implements Partitioner {
    
    @Override
    public int partition(String topic, Object key, byte[] keyBytes,
                        Object value, byte[] valueBytes, Cluster cluster) {
        // 根据业务路由
        if (value instanceof Order) {
            Order order = (Order) value;
            // 按订单类型路由到不同 partition
            return order.getType().hashCode() % cluster.partitionsForTopic(topic).size();
        }
        // 默认轮询
        return -1;  // 触发默认分区器
    }
    
    @Override
    public void close() {}
    
    @Override
    public void configure(Map<String, ?> configs) {}
}
```

### 带拦截器的 Producer

```java
public class MetricsInterceptor implements ProducerInterceptor<String, String> {
    private final AtomicLong sentCount = new AtomicLong(0);
    
    @Override
    public ProducerRecord<String, String> onSend(ProducerRecord<String, String> record) {
        sentCount.incrementAndGet();
        return record;
    }
    
    @Override
    public void onAcknowledgement(RecordMetadata metadata, Exception exception) {
        if (exception == null) {
            // 记录 Prometheus 指标
            Metrics.counter("kafka_producer_sent_total").increment();
        } else {
            Metrics.counter("kafka_producer_error_total").increment();
        }
    }
    
    @Override
    public void close() {
        // 输出统计
        System.out.println("Total sent: " + sentCount.get());
    }
}
```

## 📊 错误处理

```java
producer.send(record, new Callback() {
    @Override
    public void onCompletion(RecordMetadata metadata, Exception exception) {
        if (exception == null) {
            // 成功
        } else {
            // 错误分类
            if (exception instanceof RetriableException) {
                // 可重试异常（网络抖动、Leader 切换）
                log.warn("Retriable error, will retry", exception);
            } else if (exception instanceof AuthorizationException) {
                // 权限异常（不可重试）
                log.error("Auth failed", exception);
                // 报警
            } else if (exception instanceof RecordTooLargeException) {
                // 消息过大（不可重试）
                log.error("Message too large", exception);
            } else {
                // 其他异常
                log.error("Send failed", exception);
            }
        }
    }
});
```

## 🎯 总结

**生产者原理核心要点**：
- ✅ 拦截器 → 序列化 → 分区 → 累加 → 异步发送
- ✅ RecordAccumulator 缓存消息，按 batch.size 批量发送
- ✅ Sender 线程异步处理，提高吞吐
- ✅ 自定义分区器满足业务路由需求
- ✅ 拦截器实现监控、加密等横切关注点
- ⚠️ 序列化器兼容性（生产者和消费者必须一致）
- ⚠️ 累加器内存耗尽会阻塞主线程

**下一步：** [📤 消息发送流程](/04-producer/send-flow) — 从 send 到 Broker 的完整路径


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
