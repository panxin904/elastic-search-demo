---
title: Kafka Streams
---
# Kafka Streams

## 1. 是什么

Kafka 内置的流处理库（lib 形式，无独立集群）。

```
Kafka Cluster（KRaft）
   ↓
Source (Consumer)  →  StreamProcessor  →  Sink (Producer)
  Kafka Topic        KTable / KStream   Kafka Topic
```

**优势**：
- 零运维（没新集群，复用 Kafka broker）
- exactly-once（Kafka 0.11+ 事务）
- 与 Kafka 生态整合（Connect / Schema Registry）

## 2. KStream vs KTable

```java
KStream<String, Order> orders = builder.stream("orders");
// 事件流（insert / update / delete 都算独立事件）

KTable<String, Order> ordersTable = builder.table("orders");
// 表（最新状态，update 覆盖前值）
```

## 3. 核心 API

```java
// 1. 过滤 / 转换
KStream<String, Order> validOrders = orders
  .filter((k, v) -> v.getAmount() > 0)
  .mapValues(v -> v.setStatus("valid"));

// 2. 分组聚合
KTable<String, Long> userCount = validOrders
  .groupBy((k, v) -> v.getUserId())
  .count();

// 3. Join
KStream<String, Order> enriched = validOrders
  .leftJoin(userCount, (order, count) -> {
    order.setUserOrderCount(count);
    return order;
  }, Joined.with(Serdes.String(), orderSerde, Serdes.Long()));

// 4. 窗口
KTable<Windowed<String>, Long> hourlyCount = validOrders
  .groupByKey()
  .windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(1)))
  .count();

// 5. 输出
hourlyCount.toStream().to("user_count_per_minute");
```

## 4. Exactly-once

```java
// Kafka 0.11+ 事务
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "my-tx-id");

KStream<String, String> output = builder.stream("input");
output.mapValues(v -> transform(v))
  .to("output");

// Exactly-once：Kafka Streams + Kafka Sink 2PC
```

## 5. 实战场景

| 场景 | 方案 |
|------|------|
| 实时指标 | Kafka Streams + ClickHouse |
| 实时推荐 | Kafka Streams + Redis / ES |
| 实时 ETL | Kafka Streams + Kafka 多个 Topic |
| 事件驱动 | Kafka Streams + 微服务 |

## 6. Kafka Streams vs Flink

| | Kafka Streams | Flink |
|--|--------------|-------|
| 集群 | 复用 Kafka | 独立集群 |
| 部署 | lib（嵌入 app）| 独立 JobManager / TaskManager |
| 状态 | RocksDB | RocksDB / Memory |
| 延迟 | 毫秒 | 毫秒 |
| Exactly-once | ✅（Kafka 事务）| ✅（2PC）|
| 适合 | Kafka 生态 | 大数据 / 复杂流 |

## 7. 实战案例

### 实时用户行为聚合

```java
StreamsBuilder builder = new StreamsBuilder();

KStream<String, ClickEvent> clicks = builder
  .stream("clicks", Consumed.with(Serdes.String(), clickSerde));

// 每用户每分钟点击数
KTable<Windowed<String>, Long> userClicks = clicks
  .groupBy((k, v) -> v.getUserId())
  .windowedBy(TimeWindows.ofSizeAndGrace(Duration.ofMinutes(1), Duration.ofSeconds(5)))
  .count();

// 写入 Redis（在线服务查询）
userClicks
  .toStream()
  .map((k, v) -> new KeyValue<>(k.key(), v))
  .to("user-click-stats", Produced.with(Serdes.String(), Serdes.Long()));
```

## 8. 实战技巧

```java
// 1. 设置 commit interval
props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 1000);

// 2. 缓存大小
props.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 64 * 1024 * 1024);

// 3. 状态存储（默认 RocksDB）
props.put(StreamsConfig.STATE_DIR_CONFIG, "/var/lib/kafka-streams");

// 4. 错误处理
output.peek((k, v) -> log.info("processed: {}", v))
  .mapValues(v -> transform(v))
  .to("output");
```

## 9. 实战选型

| 场景 | 选 |
|------|-----|
| Kafka 生态内 | Kafka Streams（简单） |
| 复杂流处理 | Flink（强） |
| 实时 ETL 多源 | Flink（强） |
| 状态大 | Flink + RocksDB |
| 团队已用 Kafka | Kafka Streams（降低运维） |

## 🔗 下一步
- [Flink CDC](/05-flink/cdc)
- [数据血缘](/07-kafka-streaming/lineage)
- [OLAP vs OLTP](/08-modeling/olap-oltp)
