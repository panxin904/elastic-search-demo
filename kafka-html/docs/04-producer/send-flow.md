---
title: 消息发送流程
date: 2026-08-15  # date-auto-injected
---

# 📤 消息发送流程

> 详细解读消息从 `producer.send()` 到 Kafka Broker 的完整路径，理解每一步发生了什么。

## 🔄 完整发送流程

```
应用调用:
producer.send(new ProducerRecord<>("orders", "user123", "msg"), callback)
  ↓
[主线程]
1. ProducerInterceptor.onSend()         [可选拦截器]
2. Serializer.serialize(key)            [序列化 Key]
3. Serializer.serialize(value)          [序列化 Value]
4. Partitioner.partition()              [选择 Partition]
5. RecordAccumulator.append()           [累加到 Batch]
   ↓
[唤醒 Sender 线程]
[Sender 线程]
6. 拉取就绪 Batch
7. ClientRequest 封装
8. Selector 发送到 Broker
9. 等待 Broker 响应
10. RecordAccumulator.deallocate()      [释放 Batch]
11. 触发 Callback                         [异步回调]
12. 更新 In-Flight Requests 状态
  ↓
返回 Future<RecordMetadata>
[主线程可调用 .get() 阻塞等待]
```

## 📋 各步骤详解

### 步骤 1：ProducerInterceptor.onSend()

```java
// 自定义拦截器示例
public class TraceIdInterceptor implements ProducerInterceptor<String, String> {
    @Override
    public ProducerRecord<String, String> onSend(ProducerRecord<String, String> record) {
        // 1. 添加 traceId
        record.headers().add("traceId", generateTraceId().getBytes());
        
        // 2. 添加业务元数据
        record.headers().add("source", "order-service".getBytes());
        record.headers().add("timestamp", String.valueOf(System.currentTimeMillis()).getBytes());
        
        return record;
    }
}
```

**作用时机**：
- 在消息序列化之前调用
- 可以修改 record（包括 key、value、headers）
- 多个拦截器按配置顺序执行（可形成拦截器链）

### 步骤 2-3：序列化 Key 和 Value

```java
// Key 序列化
byte[] keyBytes = keySerializer.serialize(topic, record.key());
// Value 序列化
byte[] valueBytes = valueSerializer.serialize(topic, record.value());
```

**常见序列化器**：

| 序列化器 | 序列化内容 | 字节数 |
|---------|-----------|--------|
| StringSerializer | String | 字符串长度 |
| IntegerSerializer | Integer | 4 bytes |
| LongSerializer | Long | 8 bytes |
| ByteArraySerializer | byte[] | 原始字节 |
| JsonSerializer | 对象 → JSON | 取决于对象 |

### 步骤 4：分区器选择 Partition

```java
// DefaultPartitioner 默认实现
public int partition(String topic, Object key, byte[] keyBytes, 
                    Object value, byte[] valueBytes, Cluster cluster) {
    if (keyBytes == null) {
        // 无 key：轮询所有分区（粘性分区优化版本）
        return stickyPartitionCache.partition(topic, cluster);
    }
    // 有 key：hash(key) % partitions
    return Utils.toPositive(Utils.murmur2(keyBytes)) % cluster.partitionsForTopic(topic).size();
}
```

**三种分区策略**：

```
1. 指定 partition（最高优先级）
   producer.send(new ProducerRecord<>("orders", 0, key, value));  // 直接发到 P0

2. 指定 key（hash 路由）
   producer.send(new ProducerRecord<>("orders", key, value));
   → hash(key) % partitions

3. 无 key（轮询）
   producer.send(new ProducerRecord<>("orders", value));
   → 轮询所有分区
```

### 步骤 5：累加到 RecordAccumulator

```java
// RecordAccumulator 内部结构
public final class RecordAccumulator {
    // 按 TopicPartition 分组
    private final Map<TopicPartition, Deque<ProducerBatch>> batches = new HashMap<>();
    
    public RecordAppendResult append(TopicPartition tp, long timestamp, 
                                     byte[] key, byte[] value, 
                                     RecordAccumulator.RecordAppendCallbacks callbacks,
                                     long nowMs) {
        // 1. 找到对应 Partition 的 Deque<ProducerBatch>
        Deque<ProducerBatch> dq = getDeque(tp);
        synchronized (dq) {
            // 2. 尝试追加到最后一个 Batch
            ProducerBatch batch = dq.peekLast();
            if (batch != null && batch.canAppend(...)) {
                // 3. Batch 还有空间，追加
                batch.append(...);
                return new RecordAppendResult(...);
            }
            // 4. Batch 满了或为空，创建新 Batch
            batch = new ProducerBatch(...);
            dq.addLast(batch);
            batch.append(...);
            return new RecordAppendResult(batch, ...);
        }
    }
}
```

**关键逻辑**：

```
累加器结构：
  TopicPartition("orders", 0): [Batch1][Batch2][New Batch]
                              ↑        ↑
                          已发送    已满等待发送

Batch 大小控制：
  - batch.size：单个 Batch 最大字节数（默认 16KB）
  - 超过则新建 Batch

linger.ms：
  - Batch 创建后等待 linger.ms 才发送
  - 让更多消息进入同一 Batch
  - 提高吞吐，但增加少量延迟
```

### 步骤 6：Sender 线程拉取 Batch

```java
// Sender 线程循环
void run() {
    while (running) {
        // 1. 计算哪些 Batch 已就绪
        Map<Integer, List<ProducerBatch>> ready = recordAccumulator.ready(...);
        
        // 2. 处理 in-flight 请求
        long currTimeMs = time.milliseconds();
        for (ClientRequest request : clientRequestQueue) {
            // 检查超时、清理过期请求
        }
        
        // 3. 发送请求
        sendProducerData(ready);
        
        // 4. 处理响应
        completeResponses();
    }
}
```

**Batch 就绪条件**（满足任一即发送）：

```
1. Batch 满了（达到 batch.size）
2. linger.ms 到期
3. 创建时间超过 delivery.timeout.ms
4. 累加器空间不足（必须 flush 部分）
```

### 步骤 7：ClientRequest 封装

```java
public class ClientRequest {
    private final Destination destination;          // Broker 节点
    private final RequestHeader header;              // 请求头
    private final Struct body;                       // 请求体
    private final boolean isInitiate;                // 是否初始化请求
    private final long createdMs;                    // 创建时间
    private final long sendMs;                       // 发送时间
    private final int requestTimeoutMs;              // 超时时间
    private final boolean expectResponse;            // 是否期待响应
    private final Callback callback;                 // 回调
    private final boolean hasCallback;               // 是否有回调
    private final ClientResponseInterceptor interceptor;  // 响应拦截器
}
```

### 步骤 8：Selector 网络发送

```java
// Kafka NIO Selector 发送
public class NetworkClient {
    public List<ClientResponse> poll(...) {
        // 1. 发送数据到 Socket
        selector.send(send);
        // 2. 接收响应
        selector.completedReceives();
        // 3. 处理完成的连接
        selector.completedConnections();
        // 4. 处理完成的发送
        selector.completedSends();
        // 5. 处理断开连接
        selector.disconnected();
        
        // 6. 遍历所有 completedReceives，解析响应
    }
}
```

**发送优化**：

```
linger.ms > 0 时：
  - Batch 等待 linger.ms 收集更多消息
  - 一次网络请求发送多条消息
  - 大幅提升吞吐

发送模型：
  - 多连接复用（max.in.flight.requests.per.connection=5）
  - 同一 Broker 的多个 Batch 可并行发送
```

### 步骤 9：Broker 响应

```
Broker 返回 Response：
  - 成功：RecordMetadata(topic, partition, offset, timestamp)
  - 失败：Exception
    - NotLeaderForPartition：Leader 切换，需要更新元数据
    - RequestTimedOut：请求超时
    - InvalidProducerEpoch：生产者 epoch 过期（事务相关）
    - RecordTooLargeException：消息过大
```

### 步骤 10-11：触发 Callback

```java
// 成功时
callback.onCompletion(RecordMetadata, null);

// 失败时
callback.onCompletion(null, Exception);
```

**Callback 在哪个线程？**

```
场景 1：异步 send，未调用 .get()
  → Callback 在 Sender 线程执行

场景 2：异步 send，调用 .get()
  → .get() 阻塞主线程
  → Callback 仍在 Sender 线程执行
  → .get() 返回后主线程继续

⚠️ Callback 中不要执行耗时操作（会阻塞 Sender 线程）
```

## 📊 完整时序图

```
时间轴（毫秒）：
  0ms    主线程：send(record) → 序列化 → 分区 → 累加到 Batch
  0ms    主线程：返回 Future，立刻执行下一行
  ...    主线程继续处理其他逻辑
  10ms   linger.ms 到期，Batch 就绪
  10ms   Sender 线程：从累加器拉取 Batch
  11ms   Sender 线程：发送到 Broker
  15ms   Broker 处理（写 log + 同步副本）
  16ms   Sender 线程：收到响应
  16ms   Sender 线程：触发 Callback
  16ms   主线程：调用 future.get()（如果调用了）立即返回

总延迟：~16ms
```

## 🔧 关键配置详解

### acks 配置

```properties
# acks=0：不等待响应（最快，可能丢消息）
acks=0

# acks=1：等待 Leader 写入（中等）
acks=1

# acks=all（或 -1）：等待所有 ISR 写入（最安全，最慢）
acks=all

# 推荐生产环境：acks=all
```

### retries 配置

```properties
# 重试次数（默认 2147483647 = Integer.MAX_VALUE）
retries=2147483647

# 重试间隔（默认 100ms）
retry.backoff.ms=100

# 单个请求超时（默认 30s）
request.timeout.ms=30000

# 总投递超时（默认 120s）
delivery.timeout.ms=120000
```

### 幂等性配置

```properties
# 启用幂等性（默认 false，推荐 true）
enable.idempotence=true

# 启用幂等性后：
# - max.in.flight.requests.per.connection ≤ 5
# - retries > 0
# - acks=all（强制）
```

## 🛠️ 实战：监控消息发送

```java
public class MonitoredProducer {
    
    public static void main(String[] args) {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        props.put(ProducerConfig.ACKS_CONFIG, "all");
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
        props.put(ProducerConfig.LINGER_MS_CONFIG, 20);
        props.put(ProducerConfig.BATCH_SIZE_CONFIG, 65536);
        
        KafkaProducer<String, String> producer = new KafkaProducer<>(props);
        
        // 模拟高频发送
        for (int i = 0; i < 10000; i++) {
            ProducerRecord<String, String> record = new ProducerRecord<>(
                "orders",
                "user-" + (i % 100),  // key
                "msg-" + i             // value
            );
            
            producer.send(record, new Callback() {
                @Override
                public void onCompletion(RecordMetadata metadata, Exception exception) {
                    if (exception == null) {
                        long latency = System.currentTimeMillis() - sendTime;
                        Metrics.recordLatency("kafka_producer_latency", latency);
                    } else {
                        Metrics.recordError("kafka_producer_error", exception);
                    }
                }
            });
        }
        
        // flush 等待所有消息发送完成
        producer.flush();
        producer.close();
    }
}
```

## ⚠️ 常见问题

### 问题 1：消息阻塞（Buffer 满）

```
现象：producer.send() 阻塞几秒
原因：RecordAccumulator 内存耗尽
解决：
  1. 减少 linger.ms
  2. 减少 batch.size
  3. 增加 buffer.memory
  4. 检查 Broker 是否可达（消息堆积在累加器）
```

### 问题 2：超时频繁

```
现象：TimeoutException 频繁
原因：
  1. 网络问题
  2. Broker 压力大
  3. request.timeout.ms 设置过小
解决：
  1. 增加 request.timeout.ms
  2. 检查 Broker 健康
  3. 启用 idempotence + 增加 retries
```

### 问题 3：乱序

```
现象：消息顺序错误
原因：max.in.flight.requests.per.connection > 1 且无幂等性
解决：
  1. 启用 enable.idempotence=true
  2. 单 partition 保证顺序（用同一 key）
```

## 🎯 总结

**消息发送流程核心要点**：
- ✅ 主线程累加，Sender 线程发送（异步）
- ✅ RecordAccumulator 是性能关键（批量 + 缓冲）
- ✅ 5 步流程：拦截 → 序列化 → 分区 → 累加 → 发送
- ✅ linger.ms + batch.size 是性能调优核心
- ✅ enable.idempotence 推荐开启
- ⚠️ Callback 中不要做耗时操作
- ⚠️ buffer.memory 耗尽会阻塞主线程

**下一步：** [🔁 幂等性](/04-producer/idempotent) — 消息不重复发送
