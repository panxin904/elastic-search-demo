---
title: Exactly-once 语义
date: 2026-08-15  # date-auto-injected
---
# Exactly-once 语义

## 1. 三种消息传递语义

```
at-most-once：消息可能丢（不重试）
  适用：可容忍丢失（监控数据）

at-least-once：消息不丢（重试）
  可能重复（消费端去重）
  适用：消息队列默认

exactly-once：消息不丢不重
  唯一一次被处理
  适用：金融 / 计费
```

## 2. Flink exactly-once 原理

```
Source（Kafka）→ 算子（带 Barrier）→ Sink（2PC）

Source 读：
  读 offset + checkpoint 一起持久化

算子处理：
  状态写 checkpoint（HDFS / RocksDB）

Sink 写：
  两阶段提交：
    预提交 → 通知 JobManager
    提交 → 真正写到外部
```

## 3. Flink 端到端 exactly-once

```java
// 1. 启用 checkpoint
env.enableCheckpointing(60_000L);
env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);

// 2. Source 支持（Kafka）
KafkaSource<String> source = KafkaSource.<String>builder()
  .setBootstrapServers("host:9092")
  .setGroupId("my-group")
  .setStartingOffsets(OffsetsInitializer.committedOffsets())
  .setValueOnlyDeserializer(new SimpleStringSchema())
  .build();

// 3. Sink 支持（Kafka 2PC）
KafkaSink<String> sink = KafkaSink.<String>builder()
  .setBootstrapServers("host:9092")
  .setRecordSerializer(new SimpleRecordSerializer("topic"))
  .setDeliveryGuarantee(DeliveryGuarantee.EXACTLY_ONCE)  // 2PC
  .build();
```

## 4. Flink 端到端 exactly-once 条件

```
✅ Source 可重置（Kafka offset）
✅ Sink 支持事务（Kafka 2PC / MySQL XA）
✅ Flink 内部状态 + checkpoint
✅ Sink 幂等（写入多次 = 一次）
```

## 5. 实战案例

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
env.enableCheckpointing(60_000L);
env.setStateBackend(new EmbeddedRocksDBStateBackend());

// 1. Kafka Source（exactly-once）
KafkaSource<Order> source = KafkaSource.<Order>builder()
  .setBootstrapServers("host:9092")
  .setGroupId("order-processor")
  .setTopics("orders")
  .setStartingOffsets(OffsetsInitializer.committedOffsets())
  .setValueOnlyDeserializer(new OrderDeserializer())
  .build();

DataStream<Order> orders = env.fromSource(source, WatermarkStrategy.noWatermarks(), "Kafka Source");

// 2. 状态 + 处理
DataStream<Tuple2<String, Long>> stats = orders
  .keyBy(Order::getUserId)
  .map(new RichMapFunction<Order, Tuple2<String, Long>>() {
    private ValueState<Long> count;
    public void open(Configuration parameters) {
      count = getRuntimeContext().getState(new ValueStateDescriptor<>("cnt", Types.LONG));
    }
    public Tuple2<String, Long> map(Order o) {
      long c = count.value() == null ? 0L : count.value();
      count.update(c + 1);
      return Tuple2.of(o.getUserId(), c + 1);
    }
  });

// 3. Kafka Sink（2PC）
KafkaSink<Tuple2<String, Long>> sink = KafkaSink.<Tuple2<String, Long>>builder()
  .setBootstrapServers("host:9092")
  .setRecordSerializer(new SinkSerializer())
  .setDeliveryGuarantee(DeliveryGuarantee.EXACTLY_ONCE)
  .build();

stats.sinkTo(sink);

env.execute("Order Stats");
```

## 6. 不同 Sink 的 exactly-once 支持

| Sink | 支持 | 方式 |
|------|------|------|
| Kafka | ✅ | 2PC |
| MySQL | ✅ | XA |
| PostgreSQL | ✅ | XA |
| HDFS / S3 | ✅ | 文件 + 状态 |
| Redis | ❌ | 只能幂等 |
| Elasticsearch | ❌ | 只能幂等 |

**非 2PC Sink → 至少一次 + 消费端幂等 = 实际 exactly-once**。

## 7. 幂等 Sink 实战

```java
// Redis 幂等写入
public class RedisIdempotentSink implements SinkFunction<Order> {
  public void invoke(Order order, Context ctx) {
    String key = "order:" + order.getId();
    Boolean success = redis.set(key, serialize(order), "NX");  // 仅不存在时设置
    if (success == null || !success) {
      // 已存在 = 重发，跳过
      return;
    }
    // 正常处理
  }
}
```

## 8. Checkpoint 与 exactly-once 的关系

```
Checkpoint = 算子状态快照
exactly-once = checkpoint + 幂等 sink
```

```
没有 Checkpoint：
  → 失败时无状态
  → 重启丢失进度

没有幂等 Sink：
  → 状态对，但输出可能重复
  → 实际 at-least-once

两者都有：
  → 失败时状态恢复 + 输出不重
  → 真 exactly-once
```

## 9. 实战陷阱

### 陷阱 1：Kafka 消费 offset 错乱

```
Source 算子的 offset 持久化 → Sink 2PC 提交
如果 Sink 2PC 没成功，但 Source checkpoint 推进
→ 下次重启会跳过该 offset，但数据没真正写入
→ 丢数据
```

**解决**：Sink 也用 2PC，或消费端幂等。

### 陷阱 2：状态 + 输出不一致

```
Checkpoint 时算子状态已快照
但 Sink 端 kafka offset 还没 commit
→ 重启后，状态重放但 kafka 已发送
→ 重复消费
```

**解决**：Sink 2PC。

## 10. 实战建议

1. 能用 Flink 自带 Sink → 用 Flink exactly-once
2. Sink 不支持 2PC → 用幂等
3. Checkpoint 间隔：10-60 秒（看延迟容忍）
4. Savepoint：升级 / 回滚前必做
5. 监控：checkpoint 大小 + 时长

## 11. Flink vs Kafka Stream exactly-once

| | Flink | Kafka Streams |
|--|-------|---------------|
| 实现 | 2PC + 状态 | Kafka Transaction + 幂等 |
| 状态 | 内置丰富 | RocksDB State Store |
| 复杂度 | 中 | 低 |
| 适合 | 大数据流 | Kafka 生态 |

## 🔗 下一步
- [Flink 架构](/05-flink/architecture)
- [状态与 Checkpoint](/05-flink/state)
- [Flink CDC](/05-flink/cdc)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [kafka](https://java-px.bot.cd/kafka/):Kafka 流处理
- [es](https://java-px.bot.cd/es/):Elasticsearch
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
