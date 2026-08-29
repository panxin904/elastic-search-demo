---
title: 消息模型
date: 2026-08-15  # date-auto-injected
---

# 💬 消息模型

> Kafka 的消息模型结合了**点对点**和**发布订阅**两种模式。本章对比主流消息模型，帮助理解 Kafka 的设计哲学。

## 🎯 两种经典消息模型

### 点对点模型（Queue）

```
Producer A ──┐                ┌── Consumer 1
Producer B ──┼─── Queue ──────┼── Consumer 2
Producer C ──┘                └── Consumer 3

特点：
  ✅ 一条消息只被一个 Consumer 消费
  ✅ 消息消费后即删除（传统 MQ）
  ✅ 负载均衡
```

### 发布订阅模型（Pub/Sub）

```
                 ┌── Consumer 1
Producer ────────┼── Consumer 2
                 └── Consumer 3

特点：
  ✅ 一条消息被所有 Consumer 接收（广播）
  ✅ 适合通知、事件订阅
  ❌ 无法做负载均衡
```

## 🎯 Kafka 的混合模型

> Kafka 通过 **Consumer Group** 巧妙地同时支持两种模型。

### 模型示意

```
Topic: orders (3 partitions)

                  ┌── Consumer Group A ──────────┐
                  │ C1 (P0)                       │
Producer ────────┤ C2 (P1, P2)                    │
                  └───────────────────────────────┘
                  ┌── Consumer Group B ──────────┐
                  │ D1 (P0, P1, P2)               │
                  └───────────────────────────────┘

同组内：一条消息只被组内一个 Consumer 处理（点对点）
不同组：每条消息会被每个组处理一次（发布订阅）
```

### 核心规则

```
✅ 同组内：
   - 一个 Partition 同时只被组内一个 Consumer 消费
   - 一条消息只被组内一个 Consumer 处理
   - 负载均衡模式

✅ 不同组：
   - 每个 Group 独立维护消费进度（offset）
   - 同一条消息会被每个 Group 都消费一次
   - 广播模式

✅ 消息持久化：
   - 无论是否被消费，消息保留 N 天（默认 7 天）
   - Consumer 可随时重放历史消息
```

## 🔄 消息流转生命周期

```
1. Producer.send(record)
   ↓
2. 序列化 + 选择 Partition（默认 hash(key) % N）
   ↓
3. 发送到 Leader Replica
   ↓
4. Leader 写入本地 Log（顺序追加）
   ↓
5. Follower 从 Leader 拉取同步（异步）
   ↓
6. ISR 全部 ack 后（取决于 ack 配置），Producer 收到响应
   ↓
7. Consumer.poll() 拉取（主动拉取模式）
   ↓
8. Consumer 处理消息
   ↓
9. Consumer 提交 offset（自动 / 手动）
   ↓
10. 消息保留 N 天后被删除（log.retention）
```

## 📊 Kafka vs 其他 MQ 的消息模型

| 维度 | Kafka | RabbitMQ | RocketMQ | ActiveMQ |
|------|-------|----------|----------|----------|
| **模型** | 混合（消费者组） | 灵活（Exchange） | 混合 | Queue + Topic |
| **消费方式** | 主动拉取 | 推送 + 拉取 | 主动拉取 | 推送 |
| **消息保留** | N 天（磁盘） | 消费即删 | N 天 | 消费即删 |
| **消息回放** | ✅ | ❌ | ⚠️ 有限 | ❌ |
| **顺序保证** | 分区内 | Queue 内 | Queue 内 | Queue 内 |
| **广播** | 多消费者组 | Fanout Exchange | 多消费者组 | Topic 模式 |
| **集群** | 多副本分区 | 镜像队列 | 多副本 | 主从 |

## 🎯 主动拉取 vs 推送

### Kafka 的主动拉取模式（Pull）

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

```java
// Java Consumer 拉取示例
while (running) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        processMessage(record);
    }
}
```

### Kafka 2.4+ 的 Push 增强

```java
// 通过自定义分配器实现准推送
consumer.subscribe(topics, new ConsumerRebalanceListener() {
    @Override
    public void onPartitionsAssigned(...) { ... }
});

// 或使用 Spring Kafka 的 @KafkaListener（注解驱动）
@KafkaListener(topics = "orders")
public void listen(String message) {
    processMessage(message);
}
```

## 🔄 消费语义

### At Most Once（最多一次）

```
处理顺序：
  1. 拉取消息
  2. 处理
  3. 提交 offset

可能丢失：如果 3 之前崩溃，下次从新 offset 开始（消息丢失）
```

### At Least Once（至少一次，默认）

```
处理顺序：
  1. 拉取消息
  2. 提交 offset
  3. 处理

可能重复：如果 2 之后 3 之前崩溃，下次重新消费（消息重复）
✅ 大多数场景选这个，配合幂等性解决重复
```

### Exactly Once（精确一次）

```
处理顺序（需要事务）：
  1. 开启事务
  2. 拉取消息
  3. 处理消息
  4. 提交 offset
  5. 提交事务

保证：要么全部成功，要么全部回滚
⚠️ 性能开销大
```

## 📊 关键配置影响消息模型

```properties
# Producer 端
acks=all                  # 等待所有 ISR 同步成功（最强保证）
enable.idempotence=true   # 幂等性（避免重复消息）
transactional.id=tx-1    # 事务支持（Exactly Once）

# Consumer 端
enable.auto.commit=true   # 自动提交 offset（默认）
auto.commit.interval.ms=5000  # 自动提交间隔
isolation.level=read_committed  # 只读取已提交的消息（事务场景）
auto.offset.reset=earliest  # 没有 offset 时从最早开始
```

## 🎯 实战案例

### 案例 1：日志聚合（多 Consumer Group）

```
应用日志 → Kafka topic: app-logs
                ├── Consumer Group: ELK (ELK 索引)
                ├── Consumer Group: Hadoop (离线分析)
                └── Consumer Group: Prometheus (监控告警)
```

### 案例 2：异步解耦（点对点）

```
订单服务 ──→ Kafka topic: order-events
                └── Consumer Group: order-processor (单组单 Consumer)
                → 每条订单只被处理一次
```

### 案例 3：事件溯源（重放历史）

```
用户行为 → Kafka topic: user-events (保留 90 天)
                ├── Consumer Group: real-time-analytics (实时分析)
                ├── Consumer Group: offline-train (离线训练)
                └── 需要重放时：重置 offset 到指定时间点
```

## 🎯 总结

**消息模型核心要点**：
- ✅ Kafka 通过 Consumer Group 实现混合模型
- ✅ 同组内点对点（负载均衡），不同组发布订阅（广播）
- ✅ 主动拉取模式（Consumer 控制消费速率）
- ✅ 3 种消费语义：At Most / At Least / Exactly Once
- ✅ 消息持久化 + 可重放（区别于传统 MQ）

**下一步：** [🎯 整体架构](/02-architecture/overview) — 集群拓扑详解

## 📚 跨站参考：📊 监控告警

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **observability** 站（[https://java-px.bot.cd/observability/](https://java-px.bot.cd/observability/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [mysql](https://java-px.bot.cd/mysql/) / [video](https://java-px.bot.cd/video/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。
