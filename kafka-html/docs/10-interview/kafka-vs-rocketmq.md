---
title: Kafka vs RocketMQ
---

# 🆚 Kafka vs RocketMQ

> Kafka 和 RocketMQ 都是流行的消息中间件，但定位和适用场景不同。本章详细对比两者。

## 🎯 基本对比

| 维度 | Kafka | RocketMQ |
|------|-------|-----------|
| **背景** | LinkedIn 开源，2011 | 阿里开源，2012 |
| **语言** | Scala + Java | Java |
| **顶级项目** | Apache | Apache |
| **定位** | 分布式日志 + MQ | 业务消息 MQ |
| **协议** | 自定义协议 | 自定义协议 |

## 📊 架构对比

### Kafka 架构

```
┌────────────────────────────────────┐
│         Kafka Cluster              │
│                                    │
│  ┌──────┐ ┌──────┐ ┌──────┐      │
│  │ B1   │ │ B2   │ │ B3   │       │
│  │ CTR  │ │ CTR  │ │ CTR  │ ← KRaft│
│  │ BRK  │ │ BRK  │ │ BRK  │       │
│  └──────┘ └──────┘ └──────┘      │
│                                    │
│  Topic + Partition + Replica       │
│  Controller（选举）                 │
│  __consumer_offsets               │
└────────────────────────────────────┘
```

### RocketMQ 架构

```
┌────────────────────────────────────────┐
│         RocketMQ Cluster                  │
│                                          │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │ NameServer│  │ NameServer│  │NameServer││  ← 无状态注册中心
│  └──────────┘  └──────────┘  └────────┘│
│  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │ B1   │  │ B2   │  │ B3   │          │  ← Broker
│  └──────┘  └──────┘  └──────┘         │
│                                          │
│  Topic + Queue + MessageQueue           │
└──────────────────────────────────────────┘
```

### 架构差异

| 维度 | Kafka | RocketMQ |
|------|-------|----------|
| 注册中心 | KRaft（内置） | NameServer（无状态） |
| Broker 角色 | 同时担任 Controller + Broker | 纯 Broker |
| 元数据存储 | __cluster_metadata Topic | NameServer 内存 |
| 选举算法 | Raft | DLedger（Raft） |

## 📊 性能对比

### 吞吐量

| 场景 | Kafka | RocketMQ |
|------|-------|-----------|
| 顺序写 | ~500 MB/s | ~200 MB/s |
| 随机读 | ~300 MB/s | ~100 MB/s |
| 百万级 QPS | ✅ 轻松 | ⚠️ 需要优化 |
| 万级 TPS | ✅ | ✅ |

```
Kafka 高吞吐原因：
  1. 顺序写 + 零拷贝
  2. Page Cache
  3. 批量发送
  4. 异步刷盘
```

### 延迟

| 场景 | Kafka | RocketMQ |
|------|-------|-----------|
| P50 | 1-5ms | 1-5ms |
| P99 | 10-50ms | 5-20ms |
| P999 | 100-500ms | 50-200ms |

## 📊 功能对比

| 功能 | Kafka | RocketMQ |
|------|-------|----------|
| **消息顺序** | 分区内 | Queue 内（更灵活） |
| **消息查询** | ❌ | ✅（按 MessageKey） |
| **定时消息** | ❌ | ✅（任意精度） |
| **事务消息** | ✅（0.11+） | ✅（更成熟） |
| **消息回溯** | ✅（按 offset） | ✅（按 offset / 时间） |
| **消息重试** | 需自己实现 | 内置 |
| **死信队列** | 需自己实现 | 内置 |
| **消息轨迹** | ❌ | ✅（内置） |
| **消息过滤** | ❌（需消费端过滤） | ✅（SQL / Tag） |
| **广播消费** | 多 Consumer Group | 多 Consumer Group |
| **集群消费** | ✅ | ✅ |
| **消息堆积** | ✅（天然支持） | ✅（天然支持） |

### 顺序消息对比

```
Kafka 顺序消息：
  - 单 Partition 内有序
  - 必须用同 Key 路由到同 Partition
  - 全局有序需要单 Partition

RocketMQ 顺序消息：
  - 单 Queue 内有序
  - 通过 MessageQueueSelector 路由
  - 更灵活的顺序控制
```

### 定时消息对比

```
Kafka：
  - 不支持
  - 需自己实现（延迟队列）

RocketMQ：
  - 内置支持
  - 任意精度（毫秒级）
  - 实现简单
```

### 事务消息对比

```
Kafka 事务：
  - 跨 Partition 原子写入
  - 需要 transactional.id
  - EOS 语义（v2）

RocketMQ 事务：
  - 两阶段提交（发送 + 回查）
  - 与本地事务绑定
  - 半消息机制
```

## 📊 适用场景对比

### Kafka 适用场景

```
✅ 大数据流处理
   - Kafka Streams、Flink、Spark Streaming
   - 实时计算（高吞吐）

✅ 日志收集
   - 应用日志、访问日志
   - 聚合后写入 ES / Hadoop

✅ 事件溯源（Event Sourcing）
   - 消息持久化保留
   - 可重放历史

✅ CDC（数据变更同步）
   - Debezium + Kafka
   - 数据库变更实时同步

✅ 微服务事件驱动
   - 跨服务事件传递
   - 微服务解耦
```

### RocketMQ 适用场景

```
✅ 业务消息
   - 订单、支付、交易
   - 强事务支持

✅ 定时任务
   - 订单超时关闭
   - 定时通知

✅ 消息查询
   - 按 MessageKey 查消息
   - 业务排查

✅ 消息过滤
   - SQL 过滤（Tag / SQL92）
   - 减少网络传输

✅ 金融交易
   - 事务消息更成熟
   - 顺序消息更灵活
```

## 📊 运维对比

| 维度 | Kafka | RocketMQ |
|------|-------|----------|
| 部署复杂度 | 中（KRaft） | 低（NameServer 无状态） |
| 监控成熟度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 生态丰富度 | ⭐⭐⭐⭐⭐（Confluent） | ⭐⭐⭐（Apache） |
| 大数据集成 | ⭐⭐⭐⭐⭐（Spark / Flink） | ⭐⭐ |
| 中文社区 | 中等 | 活跃（阿里维护） |
| 商业支持 | Confluent | 阿里云 |

## 📊 代码对比

### Producer 示例

```java
// Kafka
KafkaProducer<String, String> producer = new KafkaProducer<>(props);
producer.send(new ProducerRecord<>("orders", "key", "value"));

// RocketMQ
DefaultMQProducer producer = new DefaultMQProducer("producer-group");
producer.setNamesrvAddr("localhost:9876");
producer.start();
Message msg = new Message("orders", "value".getBytes());
producer.send(msg);
```

### Consumer 示例

```java
// Kafka
KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));
while (running) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    // 处理 records
}

// RocketMQ
DefaultMQPushConsumer consumer = new DefaultMQPushConsumer("consumer-group");
consumer.setNamesrvAddr("localhost:9876");
consumer.subscribe("orders", "*");
consumer.registerMessageListener((MessageListenerConcurrently) (msgs, context) -> {
    // 处理 msgs
    return ConsumeConcurrentlyStatus.CONSUME_SUCCESS;
});
consumer.start();
```

## 🎯 选型决策

### 决策树

```
数据量级？
  ├─ 日 TB+ → Kafka（高吞吐首选）
  ├─ 日 GB- → 都可（看下面）
  └─ 日 MB- → RocketMQ（简单）

业务场景？
  ├─ 大数据 / 日志 → Kafka
  ├─ 业务消息 / 金融 → RocketMQ
  └─ 微服务事件 → 都可

需要定时消息？
  ├─ 是 → RocketMQ
  └─ 否 → Kafka

需要消息查询？
  ├─ 是 → RocketMQ
  └─ 否 → Kafka

需要事务消息？
  ├─ 强事务 → RocketMQ（更成熟）
  └─ 简单事务 → Kafka 0.11+

需要流处理？
  ├─ 是 → Kafka（Kafka Streams / Flink）
  └─ 否 → 都可
```

### 推荐组合

```
✅ 大数据 / 日志聚合 / 实时计算 → Kafka
✅ 业务消息 / 订单交易 / 支付 → RocketMQ
✅ 简单微服务 → 都可（Kafka 社区更大）
```

## 📊 大厂实践

| 公司 | 选择 | 原因 |
|------|------|------|
| LinkedIn | Kafka | 自研 |
| Uber | Kafka | 高吞吐 |
| Netflix | Kafka | 高吞吐 + OSS |
| Twitter | Kafka | 实时计算 |
| 阿里 | RocketMQ | 业务消息 |
| 美团 | RocketMQ | 业务消息 |
| 字节跳动 | Kafka（自研） | 大数据 + 业务 |
| 滴滴 | RocketMQ | 业务消息 |
| 快手 | Kafka | 大数据 + 流计算 |

## 📊 迁移与共存

### 迁移路径

```
RocketMQ → Kafka：
  1. 双写（RocketMQ + Kafka）
  2. 逐步切流量
  3. 下线 RocketMQ

Kafka → RocketMQ：
  1. 双写
  2. 逐步切
  3. 下线 Kafka
```

### 共存架构

```
某些业务用 Kafka（日志）
某些业务用 RocketMQ（业务）
通过 ETL 同步数据
```

## 🎯 总结

**Kafka vs RocketMQ 选型核心要点**：
- ✅ Kafka 适合大数据、日志、高吞吐
- ✅ RocketMQ 适合业务消息、定时、查询
- ✅ Kafka 生态更丰富（Confluent、大数据）
- ✅ RocketMQ 事务和定时更成熟
- ✅ 两者可共存
- ⚠️ 根据业务选型，不是哪个更好
- ⚠️ 大厂实践可参考但不照搬

**下一步：** [👑 Leader 选举机制](/10-interview/election) — 深入选举原理
