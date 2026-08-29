---
title: 高频面试题（上）
date: 2026-08-15  # date-auto-injected
---

# 📝 高频面试题（上）

> 整理 Kafka **基础到进阶**的 20 道高频面试题，涵盖**架构、原理、特性**三大方向。

## 🎯 Kafka 基础

### 1. Kafka 是什么？有哪些特点？

```
Kafka = 分布式发布订阅消息系统

核心特点：
  ✅ 高吞吐（百万级 TPS）
  ✅ 持久化（消息存磁盘）
  ✅ 水平扩展（增加 Broker）
  ✅ 高可用（多副本）
  ✅ 流处理（Kafka Streams）

适用场景：
  - 日志聚合
  - 消息队列
  - 流式计算
  - CDC（数据变更同步）
```

### 2. Kafka 与传统 MQ 的区别？

| 维度 | Kafka | RabbitMQ | RocketMQ |
|------|-------|----------|----------|
| 定位 | 分布式日志 | 业务消息 | 业务消息 |
| 吞吐 | 百万级 | 万级 | 十万级 |
| 消息保留 | 持久化 N 天 | 消费即删 | 持久化 |
| 顺序保证 | 分区内 | Queue 内 | Queue 内 |
| 消息回溯 | ✅ | ❌ | ⚠️ |
| 适用 | 日志、大数据 | 业务 | 业务、金融 |

### 3. Kafka 的核心概念有哪些？

```
Broker    - Kafka 服务器节点
Topic     - 消息主题（逻辑分类）
Partition - Topic 的分片
Replica   - 分区副本（高可用）
Producer  - 消息生产者
Consumer  - 消息消费者
Consumer Group - 消费者组
Offset    - 消息位置（Partition 内单调递增）
ISR       - 同步副本列表
Controller - 集群元数据管理
ZooKeeper/KRaft - 早期依赖 / 新一代共识协议
```

### 4. Kafka 的消息模型是什么？

```
Kafka = 发布订阅 + 点对点 混合模型

✅ 同组内（点对点）：
   - 一条消息只被组内一个 Consumer 消费
   - 负载均衡

✅ 不同组（发布订阅）：
   - 每条消息被每个组都消费一次
   - 广播

✅ 消息持久化：
   - 消息保留 N 天（默认 7 天）
   - Consumer 可重放历史消息
```

### 5. Kafka 的消费模式？

```
1. 点对点（Point-to-Point）
   - 一条消息只被一个 Consumer 消费
   - 类似 Queue

2. 发布订阅（Pub/Sub）
   - 一条消息被多个 Consumer 订阅
   - 类似 Topic

3. Kafka 的混合模式（Consumer Group）
   - 同组：点对点（每条消息只被组内一个 Consumer 处理）
   - 不同组：发布订阅（每条消息被每个组消费一次）
```

## 🎯 Kafka 架构

### 6. Kafka 的整体架构是怎样的？

```
Kafka 集群 = N 个 Broker + KRaft 集群（Kafka 3.x）

┌─────────────────────────────────────┐
│         Kafka Cluster                │
│  ┌──────┐ ┌──────┐ ┌──────┐        │
│  │ B1   │ │ B2   │ │ B3   │         │
│  │ CTR  │ │ CTR  │ │ CTR  │ ← KRaft │
│  │ BRK  │ │ BRK  │ │ BRK  │         │
│  └──────┘ └──────┘ └──────┘        │
└─────────────────────────────────────┘
       ↑                  ↑
   Producers         Consumer Groups
```

### 7. Kafka 为什么这么快？

```
1. 顺序写盘
   - 磁盘顺序 IO ≈ 内存随机 IO
   - 顺序写 + HDD = ~200 MB/s
   - 顺序写 + NVMe SSD = ~3 GB/s

2. Page Cache
   - 操作系统文件缓存
   - 读命中 Page Cache = 内存 IO
   - 命中率通常 > 90%

3. 零拷贝
   - sendfile 系统调用
   - 数据不需要经过应用层
   - 减少 CPU 和内存拷贝

4. 批量发送
   - 一次网络请求发送多条消息
   - 提高吞吐，降低延迟

5. 异步刷盘
   - 写 Page Cache 后立即返回
   - 后台线程异步刷盘
```

### 8. Kafka 的高可用是怎么实现的？

```
1. 多副本机制
   - 每个 Partition 有 N 个副本（默认 3）
   - 分布在不同 Broker

2. ISR 同步
   - ISR（In-Sync Replicas）= 与 Leader 同步的副本
   - 写操作需要 ISR 中所有副本确认（acks=all）

3. Leader 选举
   - Leader 故障时，从 ISR 中选举新 Leader
   - 自动触发，秒级恢复

4. Controller
   - 集群 Controller 管理所有 Partition Leader
   - KRaft 模式基于 Raft 协议选举

5. 数据冗余
   - 多副本 = 数据冗余
   - 至少 min.insync.replicas 个副本写入才认为成功
```

### 9. Kafka 的分区副本机制？

```
每个 Topic 分为多个 Partition
每个 Partition 有 N 个副本（replication.factor）

副本角色：
  - Leader：处理读写请求
  - Follower：从 Leader 拉取同步

副本集合：
  - AR（Assigned Replicas）：所有副本
  - ISR（In-Sync Replicas）：同步副本
  - OSR（Out-of-Sync Replicas）：落后副本

关系：AR = ISR + OSR
```

### 10. Kafka 的 Leader 选举机制？

```
触发场景：
  - Broker 宕机
  - 网络分区
  - 主动转移

选举流程：
  1. Controller 检测 Leader 失联
  2. 从 ISR 中选择新 Leader
  3. 更新元数据
  4. 通知所有 Broker
  5. 自动恢复

⚠️ 选举期间 Partition 短暂不可用（毫秒级）
```

## 🎯 Kafka 特性

### 11. Kafka 消息顺序保证？

```
✅ 单 Partition 内：消息严格有序（offset 单调递增）
✅ 单 Key 内：保证有序（key hash 到同 Partition）
❌ 跨 Partition：无序
❌ 全局有序：需要单 Partition（牺牲性能）

实战：
  - Producer 启用幂等性（enable.idempotence=true）
  - max.in.flight.requests.per.connection ≤ 5
  - 业务端幂等设计
```

### 12. Kafka 消息丢失场景？

```
1. Producer 端
   - acks=0：可能丢失
   - acks=1：Leader 故障可能丢失
   - 解决：acks=all + min.insync.replicas=2

2. Consumer 端
   - 自动提交 Offset 后崩溃
   - 解决：关闭自动提交，处理完手动提交

3. Broker 端
   - ISR 中所有副本都不可用 + unclean.election=false
   - 解决：unclean.election.enable=false（默认）

⚠️ 完全避免丢失：
   - acks=all + replication.factor=3 + min.insync.replicas=2
   - 启用幂等性
   - 业务端幂等
```

### 13. Kafka 消息重复消费？

```
原因：
  - At Least Once 提交 Offset 后崩溃
  - Rebalance 时未提交 Offset
  - 网络问题导致重试

解决：
  1. 业务端幂等（推荐）
     - 数据库唯一索引
     - Redis SETNX
     - 乐观锁
  2. 启用事务（精确一次）
  3. 幂等性（Producer 端）
```

### 14. Kafka 的 Exactly Once 语义？

```
EOS = 精确一次 = 既不丢也不重

实现：
  1. Producer 幂等性（PID + Sequence Number）
     - 单会话内不重复
  2. 事务（Transactional）
     - 跨 Partition 原子写入
     - 跨会话幂等
  3. Consumer read_committed
     - 只读已提交消息

Kafka 配置：
  - enable.idempotence=true
  - transactional.id=unique-id
  - isolation.level=read_committed
```

### 15. Kafka 的延迟是多少？

```
典型延迟（NVMe SSD + 3 副本）：

操作                     P50    P99
Produce (acks=1)        1ms    5ms
Produce (acks=all)      5ms    50ms
Consume (单条)          1ms    10ms
事务提交                10ms   100ms

延迟组成：
  - 网络 RTT：~1ms（同机房）
  - Broker 处理：~1-5ms
  - 副本同步：~1-10ms
  - Page Cache：~0（命中）
  - 磁盘 IO：~1-10ms（不命中）
```

## 🎯 高级特性

### 16. Kafka 如何保证数据一致性？

```
1. Producer 幂等性
   - PID + Sequence Number
   - 防止重复发送

2. 事务
   - 事务 ID（transactional.id）
   - 跨 Partition 原子写入
   - 跨会话幂等

3. 副本同步
   - ISR（In-Sync Replicas）
   - Leader 写入后复制到 Follower
   - 读已确认（committed）的消息

4. Consumer read_committed
   - 只读取已提交的消息
   - 跳过未提交和已中止的消息
```

### 17. Kafka 的零拷贝原理？

```
传统 IO：
  磁盘 → Page Cache → JVM Buffer → Socket Buffer → 网卡
  4 次拷贝（2 次 DMA + 2 次 CPU）

零拷贝（sendfile）：
  磁盘 → Page Cache → 网卡
  2 次拷贝（2 次 DMA，0 次 CPU）

Kafka 应用：
  Broker → Consumer 读取消息
  Consumer → Broker 写入消息

性能提升：3-5 倍
```

### 18. Kafka 的消费者组机制？

```
Consumer Group：
  - 多个 Consumer 协作消费同一 Topic
  - 同组内每条消息只被消费一次
  - 不同组各自维护 Offset

分配策略：
  - Range Assignor（默认）
  - RoundRobin Assignor
  - Sticky Assignor
  - CooperativeSticky Assignor（Kafka 2.4+ 推荐）

Rebalance：
  - Consumer 加入/离开触发
  - CooperativeSticky 减少 STW
```

### 19. Kafka 的 Offset 管理？

```
Offset = 消息在 Partition 中的位置（long）

存储位置：
  - 默认：__consumer_offsets Topic
  - 50 个 Partition
  - Key = (groupId, topic, partition)

提交方式：
  - 自动提交（默认 5 秒）
  - 手动提交（commitSync / commitAsync）

重置策略：
  - auto.offset.reset=latest（默认）
  - earliest（最早）
  - none（无 Offset 时报错）
```

### 20. Kafka 和 RocketMQ 的区别？

| 维度 | Kafka | RocketMQ |
|------|-------|-----------|
| 背景 | LinkedIn 开源 | 阿里开源 |
| 定位 | 分布式日志 | 业务消息 |
| 吞吐 | 百万级 | 十万级 |
| 延迟 | ms 级 | ms 级 |
| 事务 | ✅（Kafka 0.11+） | ✅（更成熟） |
| 消息查询 | ❌ | ✅（按 MessageKey 查询） |
| 定时消息 | ❌ | ✅ |
| 顺序消息 | 分区内 | ✅（更灵活） |
| 生态 | Confluent | Apache |
| 适用 | 日志、大数据 | 业务、金融 |

## 🎯 总结

**Kafka 高频面试题（上）核心要点**：
- ✅ 理解 Kafka 基础概念（Broker / Topic / Partition）
- ✅ 掌握 Kafka 整体架构（KRaft）
- ✅ 知道 Kafka 为什么快（顺序写、零拷贝、Page Cache）
- ✅ 理解顺序保证、消息丢失、重复消费
- ✅ 了解 EOS 语义和事务
- ✅ Kafka vs RocketMQ 选择

**下一步：** [📝 高频面试题（下）](/10-interview/advanced) — 进阶面试题
