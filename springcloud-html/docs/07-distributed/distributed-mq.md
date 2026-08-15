---
title: 分布式消息队列
---

# 💬 分布式消息队列

> 用**异步消息**解耦分布式系统，是分布式架构的核心组件。

## 🎯 消息队列解决的问题

| 问题 | MQ 如何解决 |
|---|---|
| **服务耦合** | 上下游通过消息解耦，不需要直接调用 |
| **流量削峰** | 突发流量写入 MQ，消费者按能力消费 |
| **异步处理** | 非关键路径异步化，提升主链路响应速度 |
| **数据同步** | 数据库变更 → MQ → 同步到 ES / 缓存 / 大数据 |

## 📊 MQ 三要素

```
生产者 ─→ [消息] ─→ 消息队列（Broker）──→ 消费者
                 │
                 ├── 持久化（避免丢消息）
                 ├── 顺序性（FIFO）
                 ├── 幂等性（重复消费）
                 └── 可靠性（不丢不重）
```

## 🛠️ 主流 MQ 对比

| 特性 | **Kafka** | **RocketMQ** | **RabbitMQ** | **Pulsar** |
|---|---|---|---|---|
| **定位** | 日志 / 事件流 | 业务消息 | 灵活路由 | 云原生 |
| **吞吐** | ⭐⭐⭐⭐⭐（百万/s）| ⭐⭐⭐⭐（十万/s）| ⭐⭐（万/s）| ⭐⭐⭐⭐ |
| **延迟** | 毫秒级 | 毫秒级 | 微秒级 | 毫秒级 |
| **事务消息** | ❌（弱）| ✅（强）| ❌ | ✅ |
| **消息顺序** | 分区有序 | 队列有序 | 队列有序 | 分区有序 |
| **消息回溯** | ✅ | ✅ | ❌ | ✅ |
| **延迟消息** | ❌ | ✅（18 个级别）| ❌（插件）| ✅ |
| **死信队列** | ❌ | ✅ | ✅ | ✅ |
| **协议** | 自定义 | 自定义 | AMQP | 自定义 |
| **语言** | Scala / Java | Java | Erlang | Java |
| **生态** | 大数据 / Flink | 阿里 | 老牌企业 | Yahoo / 腾讯 |

## 📐 MQ 三大协议

| 协议 | 模型 | 特点 |
|---|---|---|
| **AMQP** | 队列 / 交换机 | RabbitMQ 使用，标准协议 |
| **MQTT** | Pub/Sub | 物联网 |
| **STOMP** | 简单文本 | 简单场景 |
| **OpenMessaging** | 队列 + 流 | RocketMQ / Kafka 参与制定 |

## 🚀 Kafka 核心概念

### 架构图

```
┌─────────┐
│Producer │
└────┬────┘
     ↓
  ┌─────────────────────────────┐
  │   Topic（主题）             │
  │  ┌───────┬───────┬───────┐  │
  │  │P0     │P1     │P2     │  │
  │  │分区0  │分区1  │分区2  │  │
  │  │M0 M1 M2│M3 M4 M5│M6 M7  │  │
  │  └───┬───┘└───┬───┘└───┬───┘  │
  │      │        │        │      │
  │   ┌──▼──┐  ┌──▼──┐  ┌──▼──┐   │
  │   │C1   │  │C2   │  │C3   │   │
  │   └─────┘  └─────┘  └─────┘   │
  └─────────────────────────────┘
       ↑              ↑
       │              │
   Zookeeper / KRaft (Controller)
```

### 核心概念

| 概念 | 含义 |
|---|---|
| **Producer** | 生产者 |
| **Consumer** | 消费者 |
| **Broker** | Kafka 服务节点 |
| **Topic** | 消息主题（逻辑分类）|
| **Partition** | 分区（物理并行单位）|
| **Offset** | 消息位移（消费进度）|
| **Consumer Group** | 消费者组（负载均衡单位）|
| **Replication** | 副本（高可用）|

### 关键特性

**1. 分区（Partition）：水平扩展的基石**

```
Topic: order-events（3 个分区）
  Partition 0: [msg0, msg1, msg2]
  Partition 1: [msg3, msg4, msg5]
  Partition 2: [msg6, msg7, msg8]
```

- 单分区有序，分区间无序
- 并发度 = 分区数

**2. 副本（Replication）**

```
Partition 0
  ├── Leader（主）── 读写
  └── Follower（从）── 同步 Leader
```

**3. ISR（In-Sync Replicas）**

- Leader 维护的"同步副本集合"
- Follower 落后太多会被踢出 ISR

**4. 消费模式**

| 模式 | 特点 |
|---|---|
| **点对点** | 一个消息只被一个消费者消费（不同组）|
| **发布订阅** | 一个消息被多个消费者消费（同一组竞争 / 多组各自一份）|

**5. 投递语义（Delivery Semantics）**

| 语义 | 含义 | 实现 |
|---|---|---|
| **At Most Once** | 至多一次（可能丢）| 提交 Offset 后处理 |
| **At Least Once** | 至少一次（可能重）| 处理后提交 Offset |
| **Exactly Once** | 精确一次 | Kafka 0.11+ 事务 + 幂等 |

## 🚀 RocketMQ 核心概念

### 架构图

```
┌─────────┐
│Producer │
└────┬────┘
     ↓
┌─────────────────────────────┐
│   NameServer（路由中心）    │
│   （轻量注册中心）           │
└─────────────┬───────────────┘
              ↓
┌─────────────────────────────┐
│   Broker Cluster            │
│   ┌─────────┐ ┌─────────┐   │
│   │Broker-A │ │Broker-B │   │
│   │ Master  │ │ Master  │   │
│   │  ┌────┐ │ │  ┌────┐ │   │
│   │  │Sla │ │ │  │Sla │ │   │
│   │  └────┘ │ │  └────┘ │   │
│   └─────────┘ └─────────┘   │
└─────────────────────────────┘
              ↓
       ┌──────────────┐
       │   Consumer   │
       └──────────────┘
```

### 核心概念

| 概念 | 含义 |
|---|---|
| **NameServer** | 路由注册中心（无状态）|
| **Broker** | 消息存储节点 |
| **Producer** | 生产者 |
| **Consumer** | 消费者 |
| **Topic** | 消息主题 |
| **Message Queue** | 消息队列（Topic 内部分片）|
| **Tag** | 消息标签（细粒度过滤）|
| **Key** | 消息 Key（用于查询）|

### RocketMQ 独有特性

| 特性 | 说明 |
|---|---|
| **事务消息** | 二阶段提交 + 状态回查 |
| **顺序消息** | 全局 / 分区顺序 |
| **延迟消息** | 18 个级别（1s ~ 2h）|
| **消息回溯** | 按时间重投 |
| **死信队列** | 重试超限进 DLQ |

### 事务消息流程

```
1. Producer 发送 Half 消息（消费者不可见）
2. Producer 执行本地事务（更新订单）
3. 根据本地事务结果，发送 commit / rollback
4. 若 MQ 未收到 ack，回查本地事务状态
5. 根据回查结果 commit / rollback
```

## 🔧 实战：Kafka + Spring Boot

### 生产者

```java
@Component
public class KafkaProducer {
    @Autowired
    private KafkaTemplate<String, String> kafkaTemplate;

    public void send(String topic, String key, String msg) {
        // key 相同 → 同一分区 → 顺序消费
        kafkaTemplate.send(topic, key, msg)
            .addCallback(
                success -> log.info("Sent: {}", success),
                failure -> log.error("Failed", failure)
            );
    }
}
```

### 消费者

```java
@Component
public class KafkaConsumer {

    @KafkaListener(topics = "order-events", groupId = "order-service")
    public void onMessage(
        @Header(KafkaHeaders.RECEIVED_KEY) String key,
        @Payload String payload,
        @Header(KafkaHeaders.OFFSET) long offset) {

        // 1. 幂等检查
        if (isProcessed(key)) return;

        // 2. 业务处理
        handleOrderEvent(payload);

        // 3. 标记已处理
        markProcessed(key);
    }
}
```

### 幂等性设计

```java
// 方案 1：唯一键 + DB 唯一约束
@Insert("INSERT INTO order_event_log(event_id, processed_at) VALUES(#{eventId}, NOW())")
int insertEventLog(String eventId);
// INSERT 失败 → 重复消息

// 方案 2：Redis SETNX
Boolean first = redisTemplate.opsForValue()
    .setIfAbsent("event:" + eventId, "1", 7, TimeUnit.DAYS);
if (!first) return;  // 已处理过

// 方案 3：业务唯一键（订单 ID）
if (orderRepo.existsByEventId(eventId)) return;
```

## ⚠️ MQ 常见问题

### 1. 消息丢失

| 阶段 | 丢消息原因 | 解决方案 |
|---|---|---|
| **生产** | 网络抖动 / Producer 宕机 | 同步 / 异步双确认 |
| **存储** | Broker 宕机 / 磁盘损坏 | 多副本 + 持久化 |
| **消费** | 提交 Offset 后崩溃 | 处理后再提交 Offset |

**RocketMQ 同步发送：**
```java
SendResult result = producer.send(msg);
if (result.getSendStatus() == SendStatus.SEND_OK) {
    // 发送成功
}
```

### 2. 消息重复

**原因：** Producer 重试 + Consumer ACK 失败

**解决：** 幂等设计（业务唯一键 / 状态机 / 乐观锁）

### 3. 消息顺序

**Kafka 单分区有序，多分区无序**

**解决：**
```java
// 同一业务 Key 路由到同一分区
kafkaTemplate.send(topic, orderId, payload);  // orderId 作为 key
```

### 4. 消息积压

**原因：** 消费速度 < 生产速度

**解决：**
- 增加消费者并发
- 优化消费逻辑
- 临时扩容消费者
- 紧急时跳过非关键消息

### 5. 延迟消息

| MQ | 支持方式 |
|---|---|
| **Kafka** | 不原生支持（需要外部调度）|
| **RocketMQ** | 原生 18 个级别（1s ~ 2h）|
| **RabbitMQ** | TTL + 死信队列 |
| **Pulsar** | 原生支持任意延迟 |

## 🎯 选型建议

```
                          业务场景？
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
   日志/事件流            业务消息           复杂路由
        │                    │                    │
     Kafka               RocketMQ            RabbitMQ
        │
   大数据生态？
        │
   Kafka（与 Flink / Spark 无缝集成）
```

| 场景 | 推荐 |
|---|---|
| 日志采集 / 大数据 / 事件溯源 | **Kafka** |
| 电商订单 / 交易 / 异步通知 | **RocketMQ** |
| 金融复杂路由 / 多协议 | **RabbitMQ** |
| 云原生 / 多租户 | **Pulsar** |

## 🎓 面试高频问题

| 问题 | 关键点 |
|---|---|
| MQ 解决了什么问题？| 解耦、异步、削峰、数据同步 |
| Kafka vs RocketMQ？| Kafka 适合日志/事件流，RocketMQ 适合业务消息 |
| 如何保证消息不丢失？| 生产同步确认 + Broker 持久化 + 消费后提交 Offset |
| 如何保证幂等？| 业务唯一键 + DB 唯一索引 / Redis SETNX |
| Kafka 分区的作用？| 水平扩展 + 并行消费 |

---

- 上一章：[🆔 分布式 ID](/07-distributed/distributed-id)
- 下一章：[📊 分布式存储](/07-distributed/distributed-storage)