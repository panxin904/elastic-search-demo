---
title: Consumer API
---

# 📥 Consumer API

> Kafka Java Consumer 提供了灵活的消息消费接口。本章详解 Consumer API 的核心用法。

## 🎯 引入依赖

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-clients</artifactId>
    <version>3.7.0</version>
</dependency>
```

## 🚀 快速开始

```java
Properties props = new Properties();
props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ConsumerConfig.GROUP_ID_CONFIG, "my-group");
props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));

try {
    while (running) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        for (ConsumerRecord<String, String> record : records) {
            System.out.printf("offset=%d, key=%s, value=%s%n",
                record.offset(), record.key(), record.value());
        }
    }
} finally {
    consumer.close();
}
```

## 📊 关键配置

```java
Properties props = new Properties();

// ==== 必填 ====
props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ConsumerConfig.GROUP_ID_CONFIG, "my-group");
props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());

// ==== 订阅方式 ====
// Topic 列表
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG, 
    CooperativeStickyAssignor.class.getName());

// ==== 拉取配置 ====
props.put(ConsumerConfig.FETCH_MIN_BYTES_CONFIG, 1);
props.put(ConsumerConfig.FETCH_MAX_BYTES_CONFIG, 52428800);   // 50MB
props.put(ConsumerConfig.FETCH_MAX_WAIT_MS_CONFIG, 500);
props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 500);
props.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 300000);  // 5 分钟

// ==== 心跳 ====
props.put(ConsumerConfig.HEARTBEAT_INTERVAL_MS_CONFIG, 3000);
props.put(ConsumerConfig.SESSION_TIMEOUT_MS_CONFIG, 10000);

// ==== 自动提交 ====
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);  // 推荐关闭
props.put(ConsumerConfig.AUTO_COMMIT_INTERVAL_MS_CONFIG, 5000);

// ==== 消费起点 ====
props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

// ==== 隔离级别 ====
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");

// ==== 客户端标识 ====
props.put(ConsumerConfig.CLIENT_ID_CONFIG, "consumer-app-1");
```

## 🔧 订阅方式

### subscribe(Topics)

```java
// 订阅多个 Topic
consumer.subscribe(Arrays.asList("orders", "payments"));

// 订阅带正则
consumer.subscribe(Pattern.compile("order-.*"));

// 带回调
consumer.subscribe(Arrays.asList("orders"), new ConsumerRebalanceListener() {
    @Override
    public void onPartitionsRevoked(Collection<TopicPartition> partitions) {
        log.info("Revoked: {}", partitions);
    }
    
    @Override
    public void onPartitionsAssigned(Collection<TopicPartition> partitions) {
        log.info("Assigned: {}", partitions);
    }
});
```

### assign(Partitions)

```java
// 手动指定 Partition（不通过 Group 协调）
List<TopicPartition> partitions = Arrays.asList(
    new TopicPartition("orders", 0),
    new TopicPartition("orders", 1)
);
consumer.assign(partitions);

// 指定 offset 起点
consumer.seek(new TopicPartition("orders", 0), 100);

// 从最早开始
consumer.seekToBeginning(partitions);

// 从最新开始
consumer.seekToEnd(partitions);

// ⚠️ assign 模式：自己管理 offset（不提交到 Group）
```

### Unsubscribe

```java
consumer.unsubscribe();
```

## 📊 poll() 方法

```java
// 基础 poll
ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

// 短轮询（推荐）
ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));

// 长轮询
ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(5));

// 空轮询
if (records.isEmpty()) {
    // 没有数据
}

// 遍历消息
for (ConsumerRecord<String, String> record : records) {
    // 处理每条消息
}

// 遍历特定 Partition
for (TopicPartition partition : records.partitions()) {
    List<ConsumerRecord<String, String>> partitionRecords = records.records(partition);
    for (ConsumerRecord<String, String> record : partitionRecords) {
        // 处理
    }
}
```

## 🔧 Offset 管理

### 自动提交

```java
// 默认自动提交（每 5 秒）
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, true);

// 禁用自动提交（推荐）
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
```

### 手动提交

```java
// 同步提交
consumer.commitSync();

// 异步提交
consumer.commitAsync(new OffsetCommitCallback() {
    @Override
    public void onComplete(Map<TopicPartition, OffsetAndMetadata> offsets, Exception exception) {
        if (exception == null) {
            log.debug("Committed: {}", offsets);
        } else {
            log.error("Commit failed", exception);
        }
    }
});

// 指定 Offset 提交
Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
for (ConsumerRecord<String, String> record : records) {
    offsets.put(
        new TopicPartition(record.topic(), record.partition()),
        new OffsetAndMetadata(record.offset() + 1)
    );
}
consumer.commitSync(offsets);
```

### Seek 定位

```java
// 定位到指定 offset
consumer.seek(new TopicPartition("orders", 0), 100);

// 定位到开头
consumer.seekToBeginning(Collections.singletonList(
    new TopicPartition("orders", 0)));

// 定位到末尾
consumer.seekToEnd(Collections.singletonList(
    new TopicPartition("orders", 0)));

// 获取当前 offset
long offset = consumer.position(new TopicPartition("orders", 0));

// 获取已提交 offset
OffsetAndMetadata committed = consumer.committed(
    new TopicPartition("orders", 0));
long committedOffset = committed.offset();
```

## 📊 ConsumerRecord 详解

```java
public class ConsumerRecord<K, V> {
    private final String topic;            // Topic
    private final int partition;          // Partition
    private final long offset;            // Offset
    private final long timestamp;         // 时间戳
    private final TimestampType timestampType;  // 时间戳类型
    private final int serializedKeySize;   // Key 序列化字节数
    private final int serializedValueSize; // Value 序列化字节数
    private final K key;                  // Key
    private final V value;                // Value
    private final Headers headers;         // Headers
    private final Optional<Integer> leaderEpoch;  // Leader epoch
}
```

## 🔧 实战：完整 Consumer 服务

```java
@Service
public class OrderConsumer {
    
    private final KafkaConsumer<String, String> consumer;
    private volatile boolean running = true;
    private final Map<TopicPartition, OffsetAndMetadata> offsetsToCommit = new HashMap<>();
    
    @PostConstruct
    public void init() {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processor");
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");
        props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
        props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
            CooperativeStickyAssignor.class.getName());
        props.put(ConsumerConfig.CLIENT_ID_CONFIG, "order-consumer");
        
        this.consumer = new KafkaConsumer<>(props);
        this.consumer.subscribe(Arrays.asList("orders"), new ConsumerRebalanceListener() {
            @Override
            public void onPartitionsRevoked(Collection<TopicPartition> partitions) {
                // Rebalance 时提交 Offset
                try {
                    consumer.commitSync(offsetsToCommit);
                    log.info("Committed offsets before rebalance");
                } catch (CommitFailedException e) {
                    log.warn("Commit failed during rebalance", e);
                }
            }
            
            @Override
            public void onPartitionsAssigned(Collection<TopicPartition> partitions) {
                log.info("Assigned partitions: {}", partitions);
            }
        });
        
        // 启动消费线程
        Thread consumerThread = new Thread(this::consume, "order-consumer");
        consumerThread.start();
    }
    
    private void consume() {
        try {
            while (running) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                
                if (records.isEmpty()) continue;
                
                for (ConsumerRecord<String, String> record : records) {
                    try {
                        // 处理消息（业务逻辑）
                        processOrder(record);
                        
                        // 记录 Offset
                        offsetsToCommit.put(
                            new TopicPartition(record.topic(), record.partition()),
                            new OffsetAndMetadata(record.offset() + 1)
                        );
                    } catch (Exception e) {
                        log.error("Process failed at offset {}", record.offset(), e);
                        throw e;
                    }
                }
                
                // 同步提交 Offset
                consumer.commitSync(offsetsToCommit);
            }
        } catch (WakeupException e) {
            log.info("Wakeup triggered");
        } catch (Exception e) {
            log.error("Consumer error", e);
        } finally {
            try {
                consumer.commitSync(offsetsToCommit);
            } catch (Exception e) {
                log.error("Final commit failed", e);
            }
            consumer.close();
        }
    }
    
    @PreDestroy
    public void close() {
        running = false;
        consumer.wakeup();  // 触发 WakeupException
    }
}
```

## 🔧 优雅关闭

```java
public class GracefulShutdown {
    
    private final KafkaConsumer<String, String> consumer;
    
    public void gracefulShutdown() {
        // 1. 设置停止标志
        running = false;
        
        // 2. 唤醒阻塞中的 poll()
        consumer.wakeup();
        
        // 3. 等待消费循环退出
        // 4. 最终提交 Offset
        consumer.commitSync();
        
        // 5. 关闭 Consumer
        consumer.close();
    }
}
```

## 🔧 反序列化器

```java
// 自定义 JSON 反序列化器
public class JsonDeserializer<T> implements Deserializer<T> {
    
    private final ObjectMapper mapper = new ObjectMapper();
    private Class<T> targetClass;
    
    @Override
    public T deserialize(String topic, byte[] data) {
        if (data == null) return null;
        try {
            return mapper.readValue(data, targetClass);
        } catch (Exception e) {
            throw new SerializationException("Failed to deserialize", e);
        }
    }
    
    @Override
    public void configure(Map<String, ?> configs, boolean isKey) {
        String className = (String) configs.get("json.deserializer.class");
        try {
            this.targetClass = (Class<T>) Class.forName(className);
        } catch (ClassNotFoundException e) {
            throw new SerializationException("Class not found", e);
        }
    }
}
```

## ⚠️ 常见问题

### 问题 1：Consumer 线程不安全

```
⚠️ KafkaConsumer 不是线程安全的！
解决：
  1. 单线程使用（推荐）
  2. 共享必须同步（synchronized）
  3. 多线程使用多个 Consumer 实例
```

### 问题 2：消息重复消费

```
原因：Offset 提交时机不正确
解决：
  1. 关闭自动提交
  2. 处理完再 commitSync
  3. 业务端幂等
```

### 问题 3：Consumer 崩溃导致 Rebalance

```
原因：session.timeout.ms 内未发送心跳
解决：
  1. 增加 session.timeout.ms
  2. 检查 GC
  3. 检查网络
```

## 🎯 总结

**Consumer API 核心要点**：
- ✅ KafkaConsumer 线程不安全
- ✅ subscribe（自动分配）+ assign（手动指定）
- ✅ poll() 主动拉取消息
- ✅ commitSync 阻塞 vs commitAsync 非阻塞
- ✅ ConsumerRebalanceListener 处理 Rebalance
- ✅ wakeup() + WakeupException 优雅关闭
- ⚠️ 消费完再提交 Offset
- ⚠️ 关闭前必须 commitSync

**下一步：** [🔧 AdminClient](/06-jdk/admin-client) — 集群管理 API
