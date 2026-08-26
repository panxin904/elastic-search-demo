---
title: Kafka Streams
---

# 🌊 Kafka Streams

> **Kafka Streams** 是 Kafka 官方的**流处理库**，用于构建实时、弹性、可扩展的流处理应用。

## 🎯 Kafka Streams 是什么？

```
Kafka Streams = 基于 Kafka 的轻量级流处理框架

特点：
  ✅ 库（不是集群），集成到应用中
  ✅ 精确一次语义（Exactly Once）
  ✅ 状态管理（State Store）
  ✅ 窗口操作（Window）
  ✅ KTable / KStream API
  ✅ 与 Kafka 深度集成（offsets 存 Kafka）
```

## 🚀 快速开始

### 引入依赖

```xml
<dependency>
    <groupId>org.apache.kafka</groupId>
    <artifactId>kafka-streams</artifactId>
    <version>3.7.0</version>
</dependency>
```

### Hello World：Word Count

```java
Properties props = new Properties();
props.put(StreamsConfig.APPLICATION_ID_CONFIG, "word-count-app");
props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());

StreamsBuilder builder = new StreamsBuilder();

// 1. 从 input topic 读数据流
KStream<String, String> textLines = builder.stream("input-text");

// 2. 处理：拆分单词 → 计数 → 输出
KTable<String, Long> wordCounts = textLines
    .flatMapValues(line -> Arrays.asList(line.toLowerCase().split("\\W+")))
    .groupBy((key, word) -> word)
    .count();

// 3. 写回 output topic
wordCounts.toStream().to("output-word-count", Produced.with(Serdes.String(), Serdes.Long()));

// 4. 启动
KafkaStreams streams = new KafkaStreams(builder.build(), props);
streams.start();
```

## 📊 核心概念

### KStream vs KTable

```
KStream = 数据流（事件流）
  - 不可变记录
  - 每条记录都是一个事件
  - 例：用户点击事件流

KTable = 变更日志（changelog）
  - 每个 Key 的最新值
  - 类比数据库表
  - 例：用户当前状态
```

```java
// KStream
KStream<String, Long> stream = builder.stream("input");

// KTable
KTable<String, Long> table = builder.table("input");

// 流转表
KTable<String, User> userTable = stream.groupByKey().reduce(...);

// 表转流
KStream<String, User> userStream = table.toStream();
```

### KStream 操作

```java
// 1. 过滤
KStream<String, String> filtered = stream.filter((key, value) -> value.startsWith("ERROR"));

// 2. 映射
KStream<String, Integer> mapped = stream.mapValues(value -> value.length());

// 3. 分组
KGroupedStream<String, String> grouped = stream.groupByKey();

// 4. 聚合
KTable<String, Long> count = grouped.count();

// 5. 连接（Join）
KStream<String, String> joined = stream.join(
    otherStream,
    (value1, value2) -> value1 + ":" + value2,
    JoinWindows.of(Duration.ofMinutes(5))
);

// 6. 窗口
KTable<Windowed<String>, Long> windowedCount = stream
    .groupByKey()
    .windowedBy(TimeWindows.of(Duration.ofMinutes(1)))
    .count();
```

## 🔄 状态管理

### State Store

```java
// 内存 State Store（速度快，但不持久化）
KStream<String, String> stream = builder.stream("input");
stream
    .groupByKey()
    .count(Materialized.as("counts-store"));

// RocksDB State Store（持久化）
props.put(StreamsConfig.STATE_DIR_CONFIG, "/var/lib/kafka-streams");

stream
    .groupByKey()
    .count(Materialized.as("counts-store")
        .withValueSerde(Serdes.Long()));
```

### 自定义 State Store

```java
// 自定义 KeyValueStore
Materialized<String, Long> materialized = Materialized
    .<String, Long>as(Stores.persistentKeyValueStore("my-store"))
    .withKeySerde(Serdes.String())
    .withValueSerde(Serdes.Long());

stream.groupByKey().count(materialized);
```

## 📊 实战：实时订单分析

### 1. 需求

```
实时统计：
  - 每分钟订单数
  - 每分钟订单总额
  - 用户消费排行
```

### 2. 实现

```java
@Configuration
public class OrderStreamConfig {
    
    @Bean
    public KafkaStreams orderStreams() {
        Properties props = new Properties();
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "order-analytics");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, "exactly_once_v2");
        
        StreamsBuilder builder = new StreamsBuilder();
        
        // 1. 读订单流
        KStream<String, String> orderStream = builder.stream("orders");
        
        // 2. 解析 JSON
        KStream<String, OrderEvent> orders = orderStream
            .mapValues(value -> parseOrder(value))
            .filter((key, order) -> order != null);
        
        // 3. 每分钟订单数（窗口）
        orders
            .groupBy((key, order) -> "all")
            .windowedBy(TimeWindows.of(Duration.ofMinutes(1)))
            .count()
            .toStream()
            .to("analytics.order-count", Produced.with(
                WindowedSerdes.timeWindowedSerde(String.class),
                Serdes.Long()
            ));
        
        // 4. 每分钟订单总额
        orders
            .mapValues(order -> order.getAmount())
            .groupBy((key, amount) -> "all")
            .windowedBy(TimeWindows.of(Duration.ofMinutes(1)))
            .reduce((a, b) -> a.add(b))
            .toStream()
            .to("analytics.order-amount", Produced.with(
                WindowedSerdes.timeWindowedSerde(String.class),
                Serdes.BigDecimal()
            ));
        
        // 5. 用户消费排行
        orders
            .groupBy((key, order) -> order.getUserId())
            .aggregate(
                () -> 0L,
                (userId, order, total) -> total + order.getAmount().longValue(),
                Materialized.<String, Long>as("user-spending")
                    .withKeySerde(Serdes.String())
                    .withValueSerde(Serdes.Long())
            )
            .toStream()
            .to("analytics.user-spending");
        
        // 6. 启动
        KafkaStreams streams = new KafkaStreams(builder.build(), props);
        streams.start();
        
        return streams;
    }
    
    private OrderEvent parseOrder(String json) {
        try {
            return JSON.parseObject(json, OrderEvent.class);
        } catch (Exception e) {
            return null;
        }
    }
}
```

## 🔄 窗口操作

### 窗口类型

```java
// 1. 滚动窗口（不重叠）
TimeWindows tumblingWindow = TimeWindows.of(Duration.ofMinutes(1));

// 2. 滑动窗口（重叠）
SlidingWindows slidingWindow = SlidingWindows.of(Duration.ofMinutes(5))
    .advanceBy(Duration.ofMinutes(1));

// 3. 会话窗口（按活动）
SessionWindows sessionWindow = SessionWindows.of(Duration.ofMinutes(5));
```

### 实战：滑动窗口限流

```java
KTable<Windowed<String>, Long> rateLimiter = orders
    .groupByKey()
    .windowedBy(SlidingWindows.of(Duration.ofSeconds(10)).advanceBy(Duration.ofSeconds(1)))
    .count();

// 检查每用户每 10 秒的订单数
rateLimiter
    .toStream()
    .filter((windowedKey, count) -> count > 100)
    .to("rate-limit-violations");
```

## 🔄 Exactly Once 语义

### 配置

```java
Properties props = new Properties();
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, "exactly_once_v2");
```

### 工作原理

```
EOS v2（Kafka 2.5+）：
  - Producer 事务（发送结果到 Kafka）
  - Consumer 事务（消费进度提交）
  - State Store 事务（状态更新）
  - 三者原子提交

优势：
  ✅ 端到端精确一次
  ✅ 不丢不重
  ✅ 自动故障恢复
```

### 实战

```java
// 启用 EOS
props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, "exactly_once_v2");

// Streams 自动处理事务
// - 生产者：发送结果到 Kafka（事务）
// - 消费者：提交 Offset（事务）
// - State Store：更新状态（事务）

KStream<String, OrderEvent> orders = builder.stream("orders", 
    Consumed.with(Serdes.String(), orderSerde));

orders
    .groupByKey()
    .aggregate(...)
    .toStream()
    .to("output", Produced.with(...));
// 所有处理都是原子的
```

## 📊 KTable 操作

### 创建 KTable

```java
// 方式 1：从 Topic 创建
KTable<String, Order> orderTable = builder.table("orders");

// 方式 2：从 KStream 转换
KTable<String, Order> orderTable = stream.groupByKey().reduce(...);
```

### KTable 操作

```java
// 1. 查询（不实际查询，只是定义查询）
orderTable.filter((key, order) -> order.getStatus().equals("PAID"));

// 2. 转换
KTable<String, OrderDTO> dtoTable = orderTable.mapValues(order -> 
    new OrderDTO(order.getId(), order.getAmount()));

// 3. Join
KTable<String, UserOrder> joined = userTable.join(orderTable,
    (user, order) -> new UserOrder(user, order));
```

## 🛠️ 实战：实时用户画像

```java
// 用户行为 → 用户画像
KStream<String, UserAction> actions = builder.stream("user-actions");

KTable<String, UserProfile> profile = actions
    .groupByKey()
    .aggregate(
        UserProfile::new,  // 初始化
        (userId, action, profile) -> profile.update(action),  // 更新
        Materialized.<String, UserProfile>as("user-profiles")
            .withKeySerde(Serdes.String())
            .withValueSerde(userProfileSerde)
    );

// 输出用户画像变化
profile.toStream().to("user-profiles-changelog");

// 关联查询
KTable<String, Order> orders = builder.table("orders");
KTable<String, UserOrderView> view = profile.join(orders,
    (profile, order) -> new UserOrderView(profile, order));

view.toStream().to("user-orders-enriched");
```

## 🔧 集成 Spring Boot

```java
@Configuration
@EnableKafkaStreams
public class KafkaStreamsConfig {
    
    @Bean
    public StreamsBuilderFactoryBean streamsBuilderFactoryBean(KafkaProperties props) {
        Map<String, Object> config = new HashMap<>();
        config.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, props.getBootstrapServers());
        config.put(StreamsConfig.APPLICATION_ID_CONFIG, "my-streams-app");
        config.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, "exactly_once_v2");
        config.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        config.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        
        return new StreamsBuilderFactoryBean(config);
    }
}
```

## ⚠️ 常见问题

### 问题 1：State Store 数据丢失

```
原因：State Store 没持久化
解决：
  1. 使用 RocksDB State Store
  2. 启用 replication.factor
  3. 监控 State Store 大小
```

### 问题 2：处理延迟

```
原因：State Store 频繁 IO
解决：
  1. 增加 State Store 内存缓存
  2. 优化状态访问模式
  3. 增加并行度
```

### 问题 3：重新处理历史数据

```
原因：Group ID 改变或 State Store 丢失
解决：
  1. 保留 Group ID
  2. 备份 State Store
  3. 设置 retention.ms 留充足时间
```

## 🎯 总结

**Kafka Streams 核心要点**：
- ✅ 库而非集群（集成到应用）
- ✅ KStream + KTable API
- ✅ 状态管理（State Store）
- ✅ 窗口操作（TimeWindow / SessionWindow）
- ✅ Exactly Once 语义（v2）
- ✅ 与 Spring Boot 集成
- ⚠️ State Store 需要持久化
- ⚠️ EOS 性能开销

**下一步：** [📊 监控告警](/08-enterprise/monitoring) — Kafka 监控体系

## 📚 跨站参考：📊 监控告警

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **observability** 站（[https://java-px.bot.cd/observability/](https://java-px.bot.cd/observability/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [mysql](https://java-px.bot.cd/mysql/) / [video](https://java-px.bot.cd/video/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。


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
