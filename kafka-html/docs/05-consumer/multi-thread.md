---
title: 多线程消费
date: 2026-08-15  # date-auto-injected
---

# 🧵 多线程消费

> Kafka Consumer **本身不是线程安全的**，多线程使用容易踩坑。本章介绍正确的多线程消费模式。

## 🎯 Consumer 线程安全

```
⚠️ KafkaConsumer 线程不安全！
  - 一个 Consumer 实例只能在单线程中使用
  - 多线程共享 Consumer 会导致：
    * 不确定性
    * ConcurrentModificationException
    * Offset 提交混乱

⚠️ KafkaProducer 线程安全！
  - 一个 Producer 实例可被多线程共享
  - 内部有锁和缓存优化
```

## 📊 三种多线程消费模式

### 模式 1：单 Consumer + 多 Worker 线程

```
Consumer Thread（单线程）
  ├─ poll() 拉取消息
  └─ 放入共享队列
                ↓
Worker Thread 1 → 处理 → 提交 Offset
Worker Thread 2 → 处理 → 提交 Offset
Worker Thread N

优点：
  ✅ 拉取和处理并行
  ✅ Offset 提交简单

缺点：
  ❌ 仍受限于单 Consumer 拉取能力
  ❌ 顺序处理困难（多线程消费同一队列）
```

```java
public class ConsumerWithWorker {
    
    private final KafkaConsumer<String, String> consumer;
    private final ExecutorService workerPool;
    private final BlockingQueue<ConsumerRecord<String, String>> queue;
    
    public void start() {
        consumer.subscribe(Arrays.asList("orders"));
        workerPool = Executors.newFixedThreadPool(10);
        queue = new LinkedBlockingQueue<>(1000);
        
        // 1. Consumer 线程（拉取）
        Thread consumerThread = new Thread(() -> {
            while (running) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                for (ConsumerRecord<String, String> record : records) {
                    try {
                        queue.put(record);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            }
        });
        consumerThread.start();
        
        // 2. Worker 线程（处理）
        for (int i = 0; i < 10; i++) {
            workerPool.submit(() -> {
                while (running) {
                    try {
                        ConsumerRecord<String, String> record = queue.poll(1, TimeUnit.SECONDS);
                        if (record != null) {
                            processOrder(record);
                            // 提交 Offset
                            commitOffset(record);
                        }
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                }
            });
        }
    }
    
    private void commitOffset(ConsumerRecord<String, String> record) {
        // 单线程提交（避免线程安全问题）
        synchronized (consumer) {
            consumer.commitSync(Map.of(
                new TopicPartition(record.topic(), record.partition()),
                new OffsetAndMetadata(record.offset() + 1)
            ));
        }
    }
}
```

### 模式 2：多 Consumer 实例（推荐）

```
Consumer 1 → Worker Thread 1（处理）
Consumer 2 → Worker Thread 2（处理）
Consumer N → Worker Thread N（处理）

每个 Consumer 在独立线程
每个 Consumer 处理不同的 Partition

优点：
  ✅ 真正的并行处理
  ✅ 充分利用多核
  ✅ 横向扩展简单

缺点：
  ❌ 增加 Broker 连接数
  ❌ Rebalance 复杂度增加
```

```java
public class MultiConsumerExample {
    
    private final int consumerCount = 5;
    private final ExecutorService executor;
    
    public void start() {
        executor = Executors.newFixedThreadPool(consumerCount);
        
        for (int i = 0; i < consumerCount; i++) {
            executor.submit(() -> {
                Properties props = createProps();
                KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
                
                try {
                    consumer.subscribe(Arrays.asList("orders"));
                    
                    while (running) {
                        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                        for (ConsumerRecord<String, String> record : records) {
                            processOrder(record);
                        }
                        consumer.commitSync();
                    }
                } finally {
                    try {
                        consumer.commitSync();
                    } finally {
                        consumer.close();
                    }
                }
            });
        }
    }
}
```

### 模式 3：Consumer + Worker Pool（处理并行）

```
Consumer Thread（单线程）
  ├─ poll() 拉取消息
  └─ 放入线程池
                ↓
Worker Pool（多线程）
  ├─ Worker 1 → 处理
  ├─ Worker 2 → 处理
  └─ Worker N → 处理

优点：
  ✅ 拉取单线程（顺序）
  ✅ 处理多线程（并行）

缺点：
  ❌ Offset 提交需要额外处理
  ❌ 消息顺序难以保证
```

```java
public class ConsumerWithWorkerPool {
    
    private final KafkaConsumer<String, String> consumer;
    private final ExecutorService workerPool;
    
    public void consume() {
        consumer.subscribe(Arrays.asList("orders"));
        workerPool = Executors.newFixedThreadPool(20);
        
        while (running) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(500));
            
            // 提交到线程池并行处理
            List<Future<?>> futures = new ArrayList<>();
            for (ConsumerRecord<String, String> record : records) {
                futures.add(workerPool.submit(() -> processOrder(record)));
            }
            
            // 等待所有任务完成
            for (Future<?> future : futures) {
                try {
                    future.get(30, TimeUnit.SECONDS);
                } catch (Exception e) {
                    log.error("Process failed", e);
                }
            }
            
            // 提交 Offset
            consumer.commitSync();
        }
    }
}
```

## 🔧 多线程模式选型

### 选型指南

```
✅ 多 Consumer 实例（推荐）：
   - 吞吐优先
   - 简单清晰
   - 集群部署友好

✅ 单 Consumer + Worker Pool：
   - 处理逻辑是 IO 密集型（DB、HTTP）
   - 想在单机获得高吞吐

⚠️ 单 Consumer + 多 Worker（顺序要求）：
   - 需要保证消息顺序
   - 但又想并发处理不同 Partition
```

## 🔧 实战：多 Consumer 模式

### 基础模式

```java
public class MultiConsumerPattern {
    
    public void consume() {
        // 每个线程独立的 Consumer
        for (int i = 0; i < 3; i++) {
            new Thread(() -> {
                Properties props = new Properties();
                props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processor");
                props.put(ConsumerConfig.CLIENT_ID_CONFIG, "consumer-" + Thread.currentThread().getId());
                // ... 其他配置
                
                KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
                
                try {
                    consumer.subscribe(Arrays.asList("orders"));
                    
                    while (running) {
                        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                        for (ConsumerRecord<String, String> record : records) {
                            processOrder(record);
                        }
                        consumer.commitSync();
                    }
                } finally {
                    consumer.close();
                }
            }).start();
        }
    }
}
```

### Spring Kafka 多线程

```java
@Configuration
public class KafkaConsumerConfig {
    
    @Bean
    public ConcurrentKafkaListenerContainerFactory<String, String> kafkaListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, String> factory = 
            new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(consumerFactory());
        // ✅ 设置并发数（每个并发一个 Consumer）
        factory.setConcurrency(3);
        // 开启手动提交
        factory.getContainerProperties().setAckMode(AckMode.MANUAL);
        return factory;
    }
    
    @Bean
    public ConsumerFactory<String, String> consumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processor");
        // ...
        return new DefaultKafkaConsumerFactory<>(props);
    }
}

@Service
public class OrderConsumer {
    
    @KafkaListener(topics = "orders", concurrency = "3")
    public void consume(ConsumerRecord<String, String> record) {
        processOrder(record);
    }
}
```

## 🔧 Offset 提交策略（多线程场景）

### 方案 1：单 Consumer + 单线程提交

```java
// Consumer 单线程拉取和处理
while (running) {
    ConsumerRecords<String, String> records = consumer.poll(...);
    for (ConsumerRecord<String, String> record : records) {
        processOrder(record);  // 可能是异步任务
    }
    // 等待所有任务完成
    waitForAllTasks();
    // 单线程提交 Offset
    consumer.commitSync();
}
```

### 方案 2：批量 Offset 提交（线程安全）

```java
public class SafeOffsetCommitter {
    
    private final KafkaConsumer<String, String> consumer;
    private final Map<TopicPartition, Long> pendingOffsets = new ConcurrentHashMap<>();
    
    public void updateOffset(ConsumerRecord<String, String> record) {
        // 多线程更新 Offset（线程安全）
        pendingOffsets.merge(
            new TopicPartition(record.topic(), record.partition()),
            record.offset() + 1,
            Math::max  // 取最大 Offset
        );
    }
    
    public void commitPeriodically() {
        // 定时器每 5 秒提交一次
        ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
        scheduler.scheduleAtFixedRate(() -> {
            synchronized (consumer) {
                Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
                pendingOffsets.forEach((tp, offset) -> 
                    offsets.put(tp, new OffsetAndMetadata(offset))
                );
                if (!offsets.isEmpty()) {
                    consumer.commitSync(offsets);
                    pendingOffsets.clear();
                }
            }
        }, 5, 5, TimeUnit.SECONDS);
    }
}
```

## 🔧 处理顺序保证

### 按 Key 顺序处理

```java
public class KeyOrderedProcessor {
    
    private final KafkaConsumer<String, String> consumer;
    private final Map<String, BlockingQueue<ConsumerRecord<String, String>>> keyQueues = new ConcurrentHashMap<>();
    private final ExecutorService executor;
    
    public void consume() {
        consumer.subscribe(Arrays.asList("orders"));
        
        // 1. Consumer 拉取并按 Key 分发
        while (running) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            
            for (ConsumerRecord<String, String> record : records) {
                // 2. 按 Key 分发到不同队列
                String key = record.key();
                keyQueues.computeIfAbsent(key, k -> new LinkedBlockingQueue<>())
                    .offer(record);
                
                // 3. 为每个 Key 启动一个 Worker
                if (!keyQueues.get(key).contains(record)) {
                    executor.submit(() -> processKey(key));
                }
            }
        }
    }
    
    private void processKey(String key) {
        BlockingQueue<ConsumerRecord<String, String>> queue = keyQueues.get(key);
        
        while (running) {
            try {
                ConsumerRecord<String, String> record = queue.poll(1, TimeUnit.SECONDS);
                if (record != null) {
                    processOrder(record);
                    // 提交 Offset（按 Key 串行）
                    synchronized (consumer) {
                        consumer.commitSync(Map.of(
                            new TopicPartition(record.topic(), record.partition()),
                            new OffsetAndMetadata(record.offset() + 1)
                        ));
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
}
```

### 整体顺序 vs Key 顺序

```
整体顺序（全局有序）：
  ❌ 单 Partition 上限（~10MB/s）
  ❌ 无法利用多核
  ❌ Kafka 不直接支持

Key 顺序（推荐）：
  ✅ 同 Key 严格有序
  ✅ 不同 Key 可并行
  ✅ 充分利用多核
  ✅ 大多数业务需求
```

## 🔧 实战：多线程消费最佳实践

```java
public class MultiThreadConsumerBestPractice {
    
    private final KafkaConsumer<String, String> consumer;
    private final int numWorkers = 5;
    private final ExecutorService workerPool;
    private final BlockingQueue<ConsumerRecord<String, String>> queue = 
        new LinkedBlockingQueue<>(1000);
    private final Map<TopicPartition, Long> offsetsToCommit = new ConcurrentHashMap<>();
    
    public void start() {
        consumer.subscribe(Arrays.asList("orders"));
        workerPool = Executors.newFixedThreadPool(numWorkers);
        
        // 1. Consumer 线程（拉取）
        Thread consumerThread = new Thread(this::consumeLoop, "kafka-consumer");
        consumerThread.start();
        
        // 2. Worker 线程（处理）
        for (int i = 0; i < numWorkers; i++) {
            workerPool.submit(this::processLoop);
        }
        
        // 3. 定时提交 Offset
        ScheduledExecutorService scheduler = Executors.newSingleThreadScheduledExecutor();
        scheduler.scheduleAtFixedRate(this::commitOffsets, 5, 5, TimeUnit.SECONDS);
    }
    
    private void consumeLoop() {
        while (running) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            for (ConsumerRecord<String, String> record : records) {
                try {
                    queue.put(record);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
    }
    
    private void processLoop() {
        while (running) {
            try {
                ConsumerRecord<String, String> record = queue.poll(1, TimeUnit.SECONDS);
                if (record != null) {
                    processOrder(record);
                    // 记录 Offset（线程安全）
                    offsetsToCommit.merge(
                        new TopicPartition(record.topic(), record.partition()),
                        record.offset() + 1,
                        Math::max
                    );
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
        }
    }
    
    private void commitOffsets() {
        if (offsetsToCommit.isEmpty()) return;
        
        Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
        offsetsToCommit.forEach((tp, offset) -> 
            offsets.put(tp, new OffsetAndMetadata(offset))
        );
        
        synchronized (consumer) {
            try {
                consumer.commitSync(offsets);
                offsetsToCommit.clear();
            } catch (Exception e) {
                log.error("Commit failed", e);
            }
        }
    }
    
    private void processOrder(ConsumerRecord<String, String> record) {
        // 业务处理（应幂等）
        log.info("Process: {}", record);
    }
}
```

## ⚠️ 常见问题

### 问题 1：Consumer 线程不安全导致数据错乱

```
现象：消费位置不连续，Offset 提交混乱
解决：
  1. 单 Consumer 单线程（推荐）
  2. 多 Consumer 多线程（每个 Consumer 独立）
  3. 共享 Consumer 必须同步（synchronized）
```

### 问题 2：多线程消费顺序错乱

```
原因：多线程并行处理同一 Partition
解决：
  1. 按 Key 路由到不同 Worker
  2. 单 Consumer + 异步任务调度
  3. 业务端幂等
```

### 问题 3：Offset 提交乱序

```
原因：多线程提交 Offset，但提交顺序与处理顺序不一致
解决：
  1. 统一线程提交 Offset
  2. 使用 synchronized 同步 Consumer
  3. 使用 Max Offset 策略
```

## 🎯 总结

**多线程消费核心要点**：
- ✅ Consumer 线程不安全，单线程使用
- ✅ 推荐模式：多 Consumer 实例（最简单）
- ✅ 高吞吐模式：单 Consumer + Worker Pool
- ✅ 顺序保证：按 Key 路由
- ✅ Offset 提交：单 Consumer 单线程提交
- ⚠️ 多线程共享 Consumer 必须同步
- ⚠️ 处理并行可能导致顺序错乱

**下一步：** [✍️ Producer API](/06-jdk/producer-api) — Java 客户端深度使用


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
