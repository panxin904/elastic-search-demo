---
title: 核心概念
---

# 🧩 核心概念

> Kafka 的术语多但不难。理解 **Broker / Topic / Partition / Producer / Consumer / Consumer Group / Offset** 这 7 个核心概念就够了。

## 🏗️ Kafka 集群拓扑

```
┌──────────────────────────────────────────────────┐
│                  Kafka Cluster                   │
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │ Broker 1 │  │ Broker 2 │  │ Broker 3 │         │
│  └──────────┘  └──────────┘  └──────────┘         │
│       │             │             │               │
│       └──────┬──────┴──────┬──────┘               │
│              │             │                      │
│         ┌────┴─────────────┴────┐                 │
│         │      Topic: orders    │                 │
│         │  P0  P1  P2  P3  P4   │                 │
│         └────────────────────────┘                 │
└──────────────────────────────────────────────────┘
            ↑                          ↑
       Producer                     Consumer
```

## 🎯 7 大核心概念

### 1. Broker（Kafka 服务器）

```
Broker = Kafka 服务节点
- 一个 Kafka 集群由多个 Broker 组成
- 每个 Broker 持有一部分分区数据
- Broker 启动时向 Controller 注册
```

```bash
# 查看集群所有 Broker
bin/kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# 输出会显示 broker.id 和 hostname:port
```

### 2. Topic（消息主题）

```
Topic = 消息的逻辑分类（类似数据库的表）
- Producer 写入 Topic
- Consumer 从 Topic 读取
- Topic 可以有多个分区
```

```bash
# 创建 Topic（3 分区、2 副本）
bin/kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 3 \
    --replication-factor 2
```

### 3. Partition（分区）

```
Partition = Topic 的物理分片
- 一个 Topic 可以有多个分区
- 分区内消息有序（offset 单调递增）
- 分区间无序（不同分区独立）
- 每个分区是一个 append-only 日志
```

```
Topic: orders (3 partitions)

Partition 0:  [m0] [m1] [m2] [m3] [m4]  ← offset 0,1,2,3,4
Partition 1:  [m0] [m1] [m2]               ← offset 0,1,2
Partition 2:  [m0] [m1] [m2] [m3] [m4] [m5] ← offset 0,1,2,3,4,5
```

### 4. Producer（生产者）

```
Producer = 消息生产者
- 向指定 Topic 发送消息
- 默认按 hash(key) % partitions 决定分区
- 可自定义分区器
```

```java
// Java 示例
KafkaProducer<String, String> producer = new KafkaProducer<>(props);
producer.send(new ProducerRecord<>("orders", "key1", "value1"));
```

### 5. Consumer（消费者）

```
Consumer = 消息消费者
- 从指定 Topic 拉取消息
- 主动管理 offset（消费位置）
- 单线程消费一个 Partition
```

### 6. Consumer Group（消费者组）

```
Consumer Group = 一组 Consumer 协作消费同一个 Topic
- 组内每个 Consumer 负责不同 Partition
- 同组内消息只会被消费一次
- 不同组各自独立消费（每条消息被每个组消费一次）
```

```
Topic: orders (3 partitions)

Consumer Group A:                     Consumer Group B:
  C1 (consumer-1) → P0                 D1 → P0, P1, P2
  C2 (consumer-2) → P1, P2              D2 (空闲)
```

### 7. Offset（偏移量）

```
Offset = 消息在分区中的位置（单调递增 long）
- 每个分区独立计数
- Consumer 通过 offset 跟踪消费进度
- 默认持久化到 __consumer_offsets topic
```

```
Partition 0:  [m0(0)] [m1(1)] [m2(2)] [m3(3)] [m4(4)]
                              ↑
                          当前 Consumer 消费到 offset=2
```

## 📊 概念关系图

```
Cluster
├── Broker 1
│   ├── Topic: orders
│   │   ├── Partition 0 (Leader) ← Replica on Broker 2
│   │   └── Partition 1 (Follower)
│   └── Topic: payments
│       └── Partition 0 (Leader)
├── Broker 2
│   └── ...
└── Broker 3
    └── ...

Producer → Topic → Partition → Message (offset)

Consumer Group
├── Consumer 1 → 消费 Partition 0, 1
├── Consumer 2 → 消费 Partition 2
└── Consumer 3 → 空闲
```

## 🎯 一个消息的生命周期

```
1. Producer 创建消息
   ProducerRecord(topic="orders", key="user123", value="...")

2. Producer 选择 Partition
   默认: hash("user123") % 3 = 1
   → 发送到 Partition 1

3. Broker 接收并追加
   Partition 1: [..., msg(offset=100)]
                  ↑ offset 单调递增

4. Consumer 拉取
   Consumer 从 Partition 1 的 offset=50 开始读取（之前消费的位置）

5. 处理消息
   业务逻辑

6. 提交 Offset
   offset=100 持久化到 __consumer_offsets
```

## 📊 关键概念速查表

| 概念 | 数量 | 作用 | 比喻 |
|------|------|------|------|
| Cluster | 1 个 | 整体服务 | 公司 |
| Broker | N 个 | 服务器节点 | 部门 |
| Topic | N 个 | 消息分类 | 项目类型 |
| Partition | N 个/Topic | 物理分片 | 子项目 |
| Replica | N 个/Partition | 副本 | 备份文件 |
| Producer | 多个 | 写入消息 | 提交人 |
| Consumer | 多个 | 读取消息 | 审阅人 |
| Consumer Group | N 个 | 协作消费 | 审阅组 |
| Offset | 无限 | 消费位置 | 页码 |

## ⚠️ 常见误区

### 误区 1：Topic = Queue

```
❌ Topic 不是简单的 Queue
✅ Topic 是「逻辑分类」，物理上是多个分区的有序日志

Queue: 先进先出，全局有序
Topic: 分区内有序，分区间无序
```

### 误区 2：Consumer Group 越多越好

```
❌ Consumer Group 越多 → 每条消息被处理次数越多（资源浪费）
✅ 根据业务需求创建 Group
   - 同组：负载均衡（一条消息只被组内一个 Consumer 处理）
   - 不同组：广播（一条消息被每个组消费一次）
```

### 误区 3：Partition 越多越好

```
❌ Partition 越多 = 性能越好？不一定
✅ Partition 数量 = 吞吐量上限
   - 单 Partition 单 Consumer 顺序消费
   - Partition 过多 → Controller 管理开销大
   - 建议：先按业务预估，再实测调整
```

## 🎯 总结

**Kafka 核心概念要点**：
- ✅ Broker（服务器）/ Topic（分类）/ Partition（分片）
- ✅ Producer / Consumer / Consumer Group / Offset
- ✅ 分区内有序，分区间无序
- ✅ 多副本高可用
- ✅ 横向扩展通过增加 Partition

**下一步：** [📂 Topic & Partition](/01-basics/topic-partition) — 消息存储模型详解
