---
title: 性能调优
date: 2026-08-15  # date-auto-injected
---

# ⚡ 性能调优

> Kafka Producer 默认配置已经很好，但**生产环境的高并发场景**仍需要精细调优。本章整理实战调优策略。

![Kafka Compression Types](/kafka-compression-types.svg)

## 🎯 性能调优 4 大方向

```
1. 批量发送：linger.ms + batch.size（提高吞吐）
2. 压缩：lz4 / zstd（减少网络带宽）
3. 内存调优：buffer.memory + 序列化（提高并发）
4. 并发调优：max.in.flight + 多实例（提高吞吐）
```

## 📊 核心配置调优

### 1. 批量发送（最重要的优化）

```properties
# ==== 关键参数 ====
linger.ms=20                      # 等待 20ms 收集更多消息（默认 0）
batch.size=65536                  # 批量大小 64KB（默认 16KB）

# 性能提升：5-10 倍
```

**原理**：

```
单条发送：
  消息1 → 序列化 → send() → 网络请求 → ack（ms级）
  消息2 → 序列化 → send() → 网络请求 → ack
  ...
  1000 条：1000 次网络请求，每次 ~5ms = 5000ms

批量发送（linger.ms=20）：
  消息1-50 → 累加到 Batch（20ms 内）
  Batch 满了 → 一次网络请求 → ack
  1000 条：20 次网络请求，每次 ~5ms = 100ms
```

**调优公式**：

```
延迟 = linger.ms + batch 处理时间
吞吐 = batch.size × 1000 / 延迟

示例：
  - batch.size=64KB + linger.ms=10ms
  - 吞吐 = 64KB × 1000 / 10ms = 6.4GB/s（理论值）
  - 实际 ~500MB/s（受网络和 Broker 限制）
```

### 2. 压缩（节省 50-90% 网络带宽）

```properties
# ==== 压缩算法 ====
compression.type=lz4             # 推荐：解压快
# 或
compression.type=zstd            # Kafka 2.1+：压缩比更好
# 或
compression.type=snappy          # 平衡
# 或
compression.type=gzip            # 压缩比最高但 CPU 大
```

**对比**：

| 算法 | 压缩比 | CPU 消耗 | 适用场景 |
|------|-------|---------|---------|
| none | 1.0 | 0 | 不推荐（生产浪费带宽） |
| gzip | 3.5-4.0 | 高 | 文本场景（CPU 富裕） |
| snappy | 2.0-2.5 | 中 | 通用 |
| **lz4** | 2.5-3.0 | 低 | **推荐** |
| zstd | 3.0-3.5 | 中 | Kafka 2.1+ 推荐 |

**CPU 与带宽权衡**：

```
网络带宽贵 vs CPU 便宜：
  ✅ 启用压缩几乎总是值得
  ✅ 推荐 lz4（解压快）
  ✅ Broker 端也解压（影响小）
```

### 3. 内存调优

```properties
# ==== 累加器内存 ====
buffer.memory=67108864            # 64MB（默认 32MB）
# 累加器总内存，超出会阻塞主线程

# ==== JVM 堆 ====
# Kafka Producer 不依赖 JVM 堆
# 但 JVM 堆影响 GC，推荐：
# - 4GB+ Heap
# - G1GC 或 ZGC

# ==== 直接内存（off-heap） ====
# Kafka 3.x 支持，部分数据结构 off-heap
# 减少 GC 压力
```

### 4. 并发调优

```properties
# ==== 并发参数 ====
max.in.flight.requests.per.connection=5   # 最多 5 个未确认请求
# 启用幂等性后强制 ≤ 5

connections.max.idle.ms=540000     # 连接空闲超时

# ==== 多实例 ====
# 增加 Producer 实例数（机器足够的前提下）
# 每个 Producer 独立线程，提高总吞吐
```

## 📊 关键性能指标监控

```java
// Producer JMX 指标
props.put("metric.reporters", "io.opentelemetry.kafka.ClientMetricsProducer");
props.put("metrics.recording.level", "DEBUG");

// 关键指标
double recordSendRate;                  // 发送速率
double recordErrorRate;                 // 错误速率
double requestLatencyAvg;               // 请求延迟
long bufferAvailableBytes;              // 累加器剩余内存
double batchSizeAvg;                    // 平均 Batch 大小
double compressionRateAvg;              // 压缩率
```

## 🛠️ 实战：调优前后对比

### 场景：电商订单发送

```java
// ❌ 默认配置（吞吐低）
Properties defaultProps = new Properties();
defaultProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
defaultProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
defaultProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
// 其他都用默认
// 测试：1 万条消息，每条 1KB
// 耗时：~5000ms（2k msg/s）

// ✅ 调优后配置
Properties tunedProps = new Properties();
tunedProps.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
tunedProps.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class);
tunedProps.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class);

// 关键调优
tunedProps.put(ProducerConfig.LINGER_MS_CONFIG, 20);                // 20ms 批处理
tunedProps.put(ProducerConfig.BATCH_SIZE_CONFIG, 65536);            // 64KB batch
tunedProps.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");      // 启用压缩
tunedProps.put(ProducerConfig.BUFFER_MEMORY_CONFIG, 67108864);     // 64MB 累加器
tunedProps.put(ProducerConfig.ACKS_CONFIG, "1");                  // Leader 写入即返回（单 IDC）
tunedProps.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5); // 5 个并发

// 测试：1 万条消息，每条 1KB
// 耗时：~200ms（50k msg/s）→ 25 倍提升
```

### 性能基准测试

```bash
# 使用 kafka-producer-perf-test.sh 测试
kafka-producer-perf-test.sh \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --num-records 1000000 \
    --record-size 1024 \
    --throughput -1 \
    --producer-props \
        linger.ms=20 \
        batch.size=65536 \
        compression.type=lz4 \
        acks=1

# 输出示例：
# 1000000 records sent, 89432.18 records/sec (87.34 MB/sec)
# 11234 ms total time
```

## 🔧 常见性能瓶颈诊断

### 瓶颈 1：网络带宽

```bash
# 检查网络流量
sar -n DEV 1 5

# 优化：
# 1. 启用压缩
# 2. 减少 acks=all（用 acks=1）
# 3. 升级网络
```

### 瓶颈 2：累加器内存满

```
现象：send() 阻塞，BufferExhaustedException
原因：buffer.memory 不够，或发送速度跟不上生产速度
解决：
  1. 增加 buffer.memory
  2. 增加 linger.ms（给 Sender 时间）
  3. 增加 batch.size（更少请求）
  4. 增加 Broker 吞吐
```

### 瓶颈 3：Broker 处理慢

```
现象：request.timeout.ms 超时
原因：Broker 集群压力大
解决：
  1. 增加 Broker 节点
  2. 增加 partition（提高并行）
  3. 优化 Broker 配置（如 num.io.threads）
  4. 减少 ack（acks=1 代替 acks=all）
```

### 瓶颈 4：序列化慢

```
现象：CPU 占用高，但消息发送慢
原因：序列化器性能差（如 Java 序列化）
解决：
  1. 使用高效的序列化器（JSON > XML > Java 序列化）
  2. 预序列化（如果可能）
  3. 使用 protobuf / avro（比 JSON 快）
```

## 📊 高并发场景配置

### 高吞吐场景（日 TB 级）

```properties
# 超高吞吐配置
bootstrap.servers=broker1:9092,broker2:9092,broker3:9092
acks=1                              # 牺牲可靠性换吞吐
linger.ms=50                        # 更长等待，更大 Batch
batch.size=131072                   # 128KB
compression.type=lz4                # 节省带宽
buffer.memory=134217728             # 128MB 累加器
max.in.flight.requests.per.connection=5
enable.idempotence=true             # 启用幂等性
send.buffer.bytes=131072            # Socket 发送缓冲
receive.buffer.bytes=131072         # Socket 接收缓冲
```

### 低延迟场景（毫秒级）

```properties
# 低延迟配置
linger.ms=0                         # 不等待，立即发送
batch.size=16384                    # 小 Batch
acks=1                              # Leader 写入即返回
max.in.flight.requests.per.connection=5
# 牺牲吞吐换延迟
```

### 高可靠性场景（金融）

```properties
# 强一致性配置
acks=all                            # 等待所有 ISR
enable.idempotence=true             # 幂等性
max.in.flight.requests.per.connection=5
retries=Integer.MAX_VALUE
# 牺牲性能换数据不丢
```

## 🛠️ 调优 Checklist

```markdown
✅ 批量发送：linger.ms=20, batch.size=65536
✅ 启用压缩：compression.type=lz4
✅ 累加器内存：buffer.memory=64MB
✅ 并发度：max.in.flight=5 + 幂等性
✅ Acks 选择：
   - 单 IDC：acks=1
   - 跨 IDC：acks=all
✅ 序列化器：JSON / Avro > Java 序列化
✅ JVM：G1GC / ZGC，Heap ≥ 4GB
✅ 网络：万兆网卡 + 多连接
✅ Broker：
   - num.io.threads=8
   - num.network.threads=3
   - num.partitions = 期望并行度
```

## ⚠️ 调优注意事项

```
⚠️ 不要盲目调优：
  - 先测量，再调优
  - 用 kafka-producer-perf-test.sh 测试

⚠️ 调优是 trade-off：
  - 吞吐 vs 延迟
  - 可靠性 vs 性能
  - CPU vs 网络带宽

⚠️ 测试环境模拟生产：
  - 同样的网络（IDC / 跨地域）
  - 同样的 Broker 集群规模
  - 同样的消息大小和模式
```

## 🎯 总结

**性能调优核心要点**：
- ✅ 批量发送是首要优化（linger.ms + batch.size）
- ✅ 启用压缩节省 50-90% 带宽
- ✅ 合理选择 acks（1 vs all）
- ✅ 启用幂等性（几乎无性能损失）
- ✅ 增加累加器内存
- ⚠️ 调优前先测量
- ⚠️ 调优是 trade-off，没有万能配置

**下一步：** [🎯 消费者原理](/05-consumer/principle) — Consumer 内部机制
