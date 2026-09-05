---
title: 消费者原理
date: 2026-08-15  # date-auto-injected
---

# 🎯 消费者原理

> Kafka Consumer 是主动拉取（Pull）模式的消费者，通过**消费者组**协作消费，理解其内部机制是使用 Kafka 的关键。

## 🏗️ Consumer 架构

```
┌──────────────────────────────────────────────────────────┐
│                   Kafka Consumer                            │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           ConsumerNetworkClient (网络客户端)            │ │
│  │   与 Broker 通信，发送 Fetch 请求                       │ │
│  └──────────────────────────────────────────────────────┘ │
│        ↓                                                   │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           Fetcher (拉取器)                             │ │
│  │   拉取消息并解析为 ConsumerRecord                       │ │
│  └──────────────────────────────────────────────────────┘ │
│        ↓                                                   │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           ConsumerRecords (消息集合)                    │ │
│  │   一次 poll() 返回的批量消息                            │ │
│  └──────────────────────────────────────────────────────┘ │
│        ↓                                                   │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           应用业务处理                                  │ │
│  └──────────────────────────────────────────────────────┘ │
│        ↓                                                   │
│  ┌──────────────────────────────────────────────────────┐ │
│  │           Offset Commit (提交 Offset)                   │ │
│  │   提交到 __consumer_offsets                            │ │
│  └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## 🎯 Consumer 核心组件

### 1. Fetcher（拉取器）

```
作用：拉取消息并解析

工作流程：
  1. 接收 FetchRequest 请求
  2. 通过 ConsumerNetworkClient 发送到 Broker
  3. Broker 返回 FetchResponse（消息批次）
  4. Fetcher 解析为 ConsumerRecord
  5. 放入 CompletedFetch 队列

优化：
  - 批量拉取（提高吞吐）
  - 长轮询（减少空轮询）
```

### 2. ConsumerNetworkClient（网络客户端）

```
作用：与 Broker 通信

功能：
  - 异步发送 FetchRequest
  - 接收 FetchResponse
  - 心跳维护（与 Coordinator）
  - 自动重连

底层：基于 Java NIO Selector
```

### 3. Offset 管理（关键）

```
Offset = 消息在 Partition 中的位置
  - 单调递增 long
  - 每个 Partition 独立

存储位置：
  - 默认：__consumer_offsets Topic
  - 默认 50 个 Partition
  - 由 GroupCoordinator 维护

提交方式：
  - 自动提交（默认 5 秒）
  - 手动提交（同步 / 异步）
```

### 4. 订阅管理（SubscriptionState）

```
作用：管理 Consumer 订阅的 Topic 和 Partition

数据结构：
  - subscribed：订阅的 Topic 集合
  - assignment：分配给本 Consumer 的 Partition 集合
  - position：每个 Partition 的消费位置

工作流程：
  1. subscribe(topics)：订阅 Topic
  2. 加入 Consumer Group
  3. Group Coordinator 分配 Partition
  4. Consumer 拉取分配到的 Partition
```

### 5. GroupCoordinator（消费者组协调器）

```
作用：管理 Consumer Group 的协调者

职责：
  - 消费者加入/退出
  - 触发 Rebalance（再平衡）
  - Offset 提交与查询
  - Partition 分配

选举：hash(groupId) % __consumer_offsets partition 数
  → 决定哪个 Broker 当 Coordinator
```

![Kafka Consumer Fetch](/kafka-consumer-fetch.svg)

## 🔄 消息拉取流程

```
Consumer.poll(timeout)
  ↓
1. 检查是否需要加入 Group
   ├─ 是 → 发送 JoinGroup 请求
   └─ 否 → 跳过
   ↓
2. 等待 Group 同步（Sync Group）
   ├─ 等所有 Consumer 加入
   └─ Coordinator 分配 Partition
   ↓
3. 发送 FetchRequest 到分配的 Partition Leader
   ↓
4. Broker 处理：
   ├─ 从 log 文件读取消息
   ├─ 应用 zero-copy 发送
   └─ 返回 FetchResponse
   ↓
5. Consumer 解析为 ConsumerRecords
   ↓
6. 返回给应用业务处理
   ↓
7. 提交 Offset（自动或手动）
```

## 📊 关键配置

```properties
# ==== 必填 ====
bootstrap.servers=localhost:9092
group.id=my-consumer-group
key.deserializer=org.apache.kafka.common.serialization.StringDeserializer
value.deserializer=org.apache.kafka.common.serialization.StringDeserializer

# ==== 拉取策略 ====
fetch.min.bytes=1                  # 每次 fetch 最小字节
fetch.max.bytes=52428800          # 每次 fetch 最大字节（默认 50MB）
fetch.max.wait.ms=500             # 长轮询等待时间

# ==== 心跳 ====
heartbeat.interval.ms=3000        # 心跳间隔（默认 3s）
session.timeout.ms=10000          # 会话超时（默认 10s）
# session.timeout 应 ≥ heartbeat.interval * 3

# ==== 自动提交 ====
enable.auto.commit=true            # 默认 true
auto.commit.interval.ms=5000       # 自动提交间隔

# ==== 消费起点 ====
auto.offset.reset=latest          # latest / earliest / none
# latest: 从最新开始（默认）
# earliest: 从最早开始
# none: 报错

# ==== 其他 ====
max.poll.records=500              # 每次 poll 最大记录数
max.poll.interval.ms=300000        # 两次 poll 最大间隔（默认 5 分钟）
```

## 🔄 主动拉取 vs 推送

### Kafka 的 Pull 模式

```
Consumer 主动调用 poll() 拉取消息

优点：
  ✅ Consumer 控制消费速率（不易被打挂）
  ✅ 批量拉取（提高吞吐）
  ✅ 适合不同消费能力的 Consumer

缺点：
  ⚠️ 轮询开销（无消息时也有空轮询）
  ⚠️ 实时性稍差（取决于 poll 间隔）
```

### 长轮询优化

```
fetch.max.wait.ms 配置：
  - Broker 在没有数据时，最多等待 fetch.max.wait.ms
  - 有数据立刻返回
  - 超时返回空（不阻塞）

实现：
  Consumer 发送 FetchRequest
  ↓
  Broker 检查：
    ├─ 有数据 → 立即返回
    └─ 无数据 → 等待 fetch.max.wait.ms
              ├─ 有数据 → 返回
              └─ 超时 → 返回空
```

## 📊 Consumer Group 工作机制

### 加入 Group

```
1. Consumer 启动
2. 向 GroupCoordinator 发送 JoinGroup 请求
3. Coordinator 等待所有 Consumer 加入（session.timeout.ms）
4. Coordinator 选举 Group Leader（通常是第一个加入的）
5. Group Leader 收到所有 Consumer 信息
6. Group Leader 决定 Partition 分配策略
7. Leader 发送分配结果到 Coordinator
8. Coordinator 同步给所有 Consumer
9. Consumer 开始拉取消息
```

### Partition 分配策略

```java
// Range 分配（默认）
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG, 
    RangeAssignor.class.getName());

// RoundRobin 分配
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    RoundRobinAssignor.class.getName());

// Sticky 分配（Kafka 0.11+）
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    StickyAssignor.class.getName());

// CooperativeSticky（Kafka 2.4+）
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    CooperativeStickyAssignor.class.getName());
```

### Rebalance（再平衡）

```
触发场景：
  1. Consumer 加入（启动新实例）
  2. Consumer 离开（崩溃或主动关闭）
  3. 订阅的 Topic 变更
  4. Group 内 Consumer 数量变化

再平衡过程：
  1. Coordinator 检测到变化（心跳超时）
  2. 触发 Rebalance
  3. 所有 Consumer 暂停消费
  4. 重新加入 Group
  5. 重新分配 Partition
  6. 恢复消费
```

## 🛠️ Consumer 生命周期

```
1. 配置 Properties
   ↓
2. 创建 KafkaConsumer
   ↓
3. subscribe(topics)
   ↓
4. poll(timeout)
   ├─ 第一次 poll：触发 JoinGroup + Rebalance
   └─ 后续 poll：直接拉取消息
   ↓
5. 处理 ConsumerRecords
   ↓
6. commitSync() 或 commitAsync() 提交 Offset
   ↓
7. close()
   - 关闭连接
   - 提交未提交的 Offset
   - 离开 Group
```

## 📊 Java 代码示例

### 基础 Consumer

```java
Properties props = new Properties();
props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
props.put(ConsumerConfig.GROUP_ID_CONFIG, "my-group");
props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));

try {
    while (true) {
        // 拉取消息（最多等待 100ms）
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        
        for (ConsumerRecord<String, String> record : records) {
            System.out.printf("offset=%d, key=%s, value=%s%n",
                record.offset(), record.key(), record.value());
            
            // 业务处理
            processOrder(record);
        }
    }
} finally {
    try {
        consumer.commitSync();  // 最后一次提交
    } finally {
        consumer.close();        // 关闭
    }
}
```

### 带手动 Offset 提交

```java
KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));

try {
    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        
        for (ConsumerRecord<String, String> record : records) {
            // 业务处理
            processOrder(record);
        }
        
        // 手动提交（同步）
        consumer.commitSync();
        
        // 或异步提交
        consumer.commitAsync((offsets, exception) -> {
            if (exception != null) {
                log.error("Commit failed", exception);
            }
        });
    }
} finally {
    consumer.close();
}
```

## ⚠️ 常见问题

### 问题 1：Consumer 频繁 Rebalance

```
原因：session.timeout.ms 太小，心跳超时
解决：
  1. 增加 session.timeout.ms（默认 10s，调到 30s）
  2. 增加 heartbeat.interval.ms（默认 3s，调到 10s）
  3. 检查 GC（避免长 GC 导致心跳丢失）
  4. 检查网络稳定性
```

### 问题 2：Consumer 消费慢

```
原因：
  1. 业务处理逻辑慢
  2. 单 Consumer 跟不上
解决：
  1. 优化业务逻辑
  2. 增加 Consumer 实例（partition 数量允许）
  3. 增加 max.poll.records（每次拉更多）
```

### 问题 3：消息丢失

```
原因：自动提交后未处理就崩溃
解决：
  1. 关闭自动提交（enable.auto.commit=false）
  2. 处理完再提交 Offset
  3. 或使用事务 + read_committed
```

## 🎯 总结

**消费者原理核心要点**：
- ✅ 主动拉取模式（Poll-based）
- ✅ Consumer Group 协作消费
- ✅ GroupCoordinator 管理 Group 状态
- ✅ Pull 模式控制消费速率
- ✅ Offset 持久化到 __consumer_offsets
- ⚠️ Rebalance 期间暂停消费
- ⚠️ Consumer 必须管理 Offset 提交

**下一步：** [👥 消费者组](/05-consumer/group) — Group 协作机制详解


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
