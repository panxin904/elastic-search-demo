---
title: Kafka vs RabbitMQ vs RocketMQ
---
# 主流消息队列对比

## 1. 三种定位

| | Kafka | RabbitMQ | RocketMQ |
|--|-------|-----------|-----------|
| 出品 | LinkedIn | RabbitMQ 公司（Pivotal） | 阿里 |
| 定位 | 分布式日志（流处理） | 传统消息队列 | 阿里消息（金融级） |
| 协议 | 自定义 TCP | AMQP 0-9-1 | 自定义 |
| 性能 | **极高**（顺序写） | 中 | 高 |
| 延迟 | 10-50ms | 微秒级 | 5-10ms |
| 吞吐量 | **百万级 QPS** | 十万级 | 十万级 |
| 顺序保证 | **分区有序** | 队列有序 | 队列有序 |
| 消息回溯 | ✅（按 offset） | ❌ | ✅ |
| 事务 | 弱（exactly-once 复杂） | ✅（XA） | ✅ |
| 运维复杂度 | 中（KRaft 后简单） | 中 | 高 |

## 2. Kafka 核心

### 架构

```
Producer → Topic (Partition 0) → Broker 0 ─┐
       → Topic (Partition 1) → Broker 1 ─┼─ Consumer Group
       → Topic (Partition 2) → Broker 2 ─┘
```

- **Topic**：消息类别
- **Partition**：分片（顺序保证单位）
- **Replica**：副本（leader / follower）
- **Consumer Group**：消费者组（每个分区只被组内一个消费者消费）

### 关键特性

- **顺序保证**：分区内有序，跨分区无序
- **at-least-once**：默认，可能重复（消费者要幂等）
- **exactly-once**：Kafka 0.11+ 支持（事务 + 流处理）
- **回溯消费**：按 offset 重读（不像 RabbitMQ ack 后就没了）
- **高吞吐**：顺序写磁盘 + 零拷贝 sendfile

### 典型场景

- **日志 / 事件流**：用户行为 / 审计日志
- **消息总线**：服务间解耦
- **流处理**：Kafka Streams / Flink
- **事件溯源**：DB log = Kafka
- **CDC**：Debezium 订阅 MySQL binlog

## 3. RabbitMQ 核心

### 架构

```
Producer → Exchange (direct/topic/fanout/headers) → Queue → Consumer
```

- **Exchange** 路由消息到 Queue（按 routing key）
- **Queue** 存储消息（持久化 / 镜像队列）
- **死信队列（DLQ）**：消费失败 → 进 DLQ

### 关键特性

- **AMQP 0-9-1** 标准协议
- **灵活的路由**：direct / topic / fanout / headers
- **消息确认（ack）**：消费成功才删除
- **死信队列**：消息被拒或超时 → DLQ
- **镜像队列**：高可用
- **插件系统**：管理 / 联邦 / 主题切换

### 典型场景

- **RPC 调用**（请求-响应模式）
- **复杂路由**（topic / header）
- **任务队列**（带 ack / DLQ）
- **金融交易**（XA 事务）

## 4. RocketMQ 核心

### 阿里特色

- **事务消息**：A 提交 + 消息提交 同事务
- **严格顺序**：全局有序（队列内）
- **金融级特性**：消息轨迹 / 死信 / 重试
- **国产友好**：阿里云原生

### 典型场景

- **金融 / 支付**（事务消息）
- **电商订单**（严格顺序）
- **阿里生态**（云原生）

## 5. 怎么选

| 场景 | 选 | 理由 |
|------|----|------|
| **日志 / 事件流** | Kafka | 高吞吐 + 回溯 |
| **CDC 同步** | Kafka | 顺序写 + 长时间保留 |
| **任务队列** | RabbitMQ | 灵活路由 + DLQ |
| **RPC 调用** | RabbitMQ | 请求-响应 + 低延迟 |
| **金融交易** | RocketMQ | 事务消息 |
| **阿里生态** | RocketMQ | 国产集成 |
| **混合（流+队列）** | Kafka + RabbitMQ | 各取所长 |

## 6. Kafka vs RabbitMQ 关键差异

### 消息模型

Kafka：**分布日志**（Partition = 物理分片）
- Consumer offset 推进 → 重新读历史
- 持久化（默认 7 天）
- 适用：流处理 / 事件溯源

RabbitMQ：**消息队列**（Queue = 内存 + 磁盘）
- Consumer ack → 消息删除（默认）
- 不持久化（要配）
- 适用：任务分发

### 性能

| | Kafka | RabbitMQ |
|--|-------|-----------|
| 写入 | 顺序写 → 极快 | 写队列 → 中 |
| 读 | 顺序读 / 按 offset | 按需拉取 |
| 延迟 | 10-50ms | 1-10ms |
| 吞吐 | 百万级 | 十万级 |

Kafka 是"分布日志"，RabbitMQ 是"消息总线"，定位不同。

## 7. Kafka 实战：电商订单

```java
// 生产
kafkaTemplate.send("order.created", order.getId(), order);
partitionKey = String.valueOf(order.getUserId());  // 同一 user 顺序
```

```java
// 消费
@KafkaListener(topics = "order.created", groupId = "payment-service")
public void handle(OrderEvent e) {
  paymentService.charge(e.getUserId(), e.getAmount());
}
```

## 8. 顺序保证

| MQ | 顺序保证 | 备注 |
|----|---------|------|
| Kafka | 分区内有序 | 用 partition key |
| RabbitMQ | 单队列有序 | 跨队列无序 |
| RocketMQ | 全局有序 | 单队列 |

## 9. 消息可靠性

| 等级 | 实现 |
|------|------|
| **at-most-once** | 生产不重试，消费不重试（可能丢） |
| **at-least-once** | 生产重试 + 消费 ack 在处理后（可能重复） |
| **exactly-once** | 事务消息 + 幂等消费者 + 持久化（Kafka 0.11+） |

**生产默认**：at-least-once → 消费端必须幂等。

## 10. 实战选型

```
K8s + 微服务：Kafka（生态完整）
任务调度（重试 / DLQ）：RabbitMQ
金融支付：RocketMQ / 事务消息
日志聚合：Kafka（ELK / Loki）
IoT 消息：Kafka
RPC：RabbitMQ（AMQP 标准）
```

## 🔗 下一步
- [顺序 / 幂等](/08-message-queue/idempotency)
- [死信 / 重试](/08-message-queue/dlq)
- [Saga 模式](/07-distributed-tx/saga)
