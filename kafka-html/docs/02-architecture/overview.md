---
title: 整体架构
---

# 🎯 整体架构

> 理解 Kafka 集群的**整体拓扑**是深入学习的前提。本章从集群视角讲解各组件的职责与协作。

## 🏗️ Kafka 集群拓扑

```
┌──────────────────────────────────────────────────────────┐
│                    Kafka Cluster (3 Brokers)               │
│                                                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────┐│
│  │    Broker 1      │  │    Broker 2      │  │ Broker 3 ││
│  │  ┌─────────────┐ │  │  ┌─────────────┐ │  │ ┌────────┐││
│  │  │ Controller  │ │  │  │ Controller  │ │  │ │Controller││
│  │  │ (Active)    │ │  │  │ (Standby)   │ │  │ │(Standby)││
│  │  └─────────────┘ │  │  └─────────────┘ │  │ └────────┘││
│  │  ┌─────────────┐ │  │  ┌─────────────┐ │  │ ┌────────┐│
│  │  │   Broker    │ │  │  │   Broker    │ │  │ │ Broker ││
│  │  │  (logs)     │ │  │  │  (logs)     │ │  │ │ (logs) ││
│  │  └─────────────┘ │  │  └─────────────┘ │  │ └────────┘│
│  └──────────────────┘  └──────────────────┘  └──────────┘│
│         ↑                       ↑                  ↑       │
└─────────┼───────────────────────┼──────────────────┼───────┘
          │                       │                  │
     ┌────┴────┐              ┌───┴────┐         ┌────┴────┐
     │Producer│              │Producer│         │Producer│
     └────────┘              └────────┘         └────────┘
          ↑                       ↑                  ↑
          └───────────────────────┼──────────────────┘
                                  │
                            Consumer Groups
```

## 🎯 核心组件职责

### 1. Broker（Kafka 服务器）

```
职责：
  ✅ 存储消息数据（Partition 日志）
  ✅ 处理 Producer/Consumer 请求
  ✅ 复制数据到 Follower
  ✅ 监控 Leader 状态

一个 Broker 同时承担 2 个角色（Kafka 3.x KRaft 模式）：
  - Controller：集群元数据管理
  - Broker：消息存储与传输
```

### 2. Controller（控制器）

```
Controller = 集群的大脑
- 管理所有 Partition 的 Leader 选举
- 管理副本分配
- 处理 Broker 上下线
- 维护集群元数据

Kafka 3.x（KRaft 模式）：
  - 一个 Active Controller（处理写）
  - 多个 Standby Controller（热备）
  - 通过 Raft 协议同步
  - 不再依赖 ZooKeeper
```

### 3. Coordinator（消费者组协调器）

```
Coordinator = 消费者组协调器
- 每个 Consumer Group 有一个 Coordinator
- 由 Group Topic Partition 决定哪个 Broker 当 Coordinator
  （hash(groupId) % __consumer_offsets partition 数）
- 负责：
  ✅ 消费者加入/退出
  ✅ 触发再平衡（Rebalance）
  ✅ Offset 提交与查询
```

### 4. Partition & Replica

```
Partition = Topic 的分片
Replica = Partition 的副本
  - Leader：处理读写
  - Follower：从 Leader 拉取同步
  - ISR（In-Sync Replicas）：同步副本列表

示例：
  Partition 0: [Leader=Broker1, Followers=Broker2,3, ISR={1,2,3}]
```

## 📊 Kafka 内部模块

```
┌─────────────────────────────────────────────────┐
│                  Kafka Broker                    │
├─────────────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │
│ │Producer │ │Consumer │ │   Admin │ │ Streams │ │ ← Client Layer
│ │  API    │ │  API    │ │  Client │ │   API   │ │
│ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │
├─────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│ │ Network  │ │  Group   │ │  Replica │          │ ← Coordinator Layer
│ │  Layer   │ │Coordinator│ │  Manager │          │
│ └──────────┘ └──────────┘ └──────────┘          │
├─────────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│ │  Log     │ │  Log     │ │  Log     │          │ ← Storage Layer
│ │ Segment 1│ │ Segment 2│ │ Segment 3│          │
│ └──────────┘ └──────────┘ └──────────┘          │
└─────────────────────────────────────────────────┘
```

## 🔄 数据流转详细过程

### Producer 发送消息

```
1. Producer.send(record)
   ↓
2. 序列化（key + value）
   ↓
3. 选择 Partition（默认 hash(key) % N）
   ↓
4. 放入 ProducerBatch（按 Partition 分组）
   ↓
5. Sender 线程异步发送
   ↓
6. 到达 Broker 的 Leader Replica
   ↓
7. Leader 写入本地 log 文件（顺序追加）
   ↓
8. Follower 从 Leader 拉取同步
   ↓
9. 满足 acks 配置后，Producer 收到 ack
   ↓
10. 返回 RecordMetadata（topic/partition/offset）
```

### Consumer 拉取消息

```
1. Consumer.poll(timeout)
   ↓
2. 通过 Coordinator 找到 Group Coordinator
   ↓
3. 发送 Fetch 请求到所有分配的 Partition Leader
   ↓
4. Broker 从 log 文件读取（零拷贝 sendfile）
   ↓
5. 返回 ConsumerRecords 批次
   ↓
6. Consumer 处理消息
   ↓
7. 提交 Offset 到 __consumer_offsets topic
```

## 🔧 KRaft vs ZooKeeper

### Kafka 2.x（依赖 ZooKeeper）

```
┌────────────────────────────────────────┐
│              ZooKeeper Ensemble         │
│              (3 或 5 节点)              │
│  - 存储集群元数据                      │
│  - 选主 Controller                      │
│  - 通知 Broker 变化                     │
└────────────────────────────────────────┘
              ↕
┌────────────────────────────────────────┐
│              Kafka Brokers              │
│  - 通过 ZooKeeper 同步元数据            │
│  - Controller 是临时选举的              │
└────────────────────────────────────────┘

缺点：
  ❌ 双集群运维（ZK + Kafka）
  ❌ Controller 选举慢
  ❌ 集群规模受限（ZK 性能）
```

### Kafka 3.x（KRaft 模式）

```
┌────────────────────────────────────────┐
│        Kafka 集群（KRaft 模式）          │
│  ┌─────────────┐  ┌─────────────────┐  │
│  │ Controller 1 │  │ Controller 2,3  │  │
│  │  (Active)    │  │  (Standby)      │  │
│  │  Raft 同步   │  │  Raft 同步       │  │
│  └─────────────┘  └─────────────────┘  │
│              ↓                          │
│  ┌─────────────────────────────────┐   │
│  │  Broker 1, 2, 3                 │   │
│  │  (每个节点同时是 Controller)     │   │
│  └─────────────────────────────────┘   │
└────────────────────────────────────────┘

优点：
  ✅ 单一集群
  ✅ Raft 协议选主快（秒级）
  ✅ 集群规模可达百万级 Partition
  ✅ 元数据日志持久化
```

## 📊 集群规模参考

```
3 节点集群（小）：
  - 适合 100MB/s 以内流量
  - 适合 1000 个 Topic 以内

5-10 节点集群（中）：
  - 适合 GB/s 级流量
  - 10000 个 Topic
  - 100000 个 Partition

50+ 节点集群（大）：
  - 适合 10GB/s+ 流量
  - 百万级 Partition
  - 需要精细调优（KRaft 模式）
```

## 🎯 关键配置文件

### broker 核心配置

```properties
# ==== 集群标识 ====
broker.id=1
listeners=PLAINTEXT://0.0.0.0:9092
advertised.listeners=PLAINTEXT://node1:9092

# ==== KRaft 模式 ====
process.roles=broker,controller
controller.quorum.voters=1@node1:9093,2@node2:9093,3@node3:9093
controller.listener.names=CONTROLLER

# ==== 日志与存储 ====
log.dirs=/data/kafka-logs
num.partitions=3
default.replication.factor=2
min.insync.replicas=2
log.retention.hours=168

# ==== 性能调优 ====
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
```

## 🎯 总结

**整体架构核心要点**：
- ✅ Broker 同时承担 Controller + Broker 角色（KRaft）
- ✅ Partition 分布在不同 Broker（负载均衡）
- ✅ 多副本 + ISR（高可用）
- ✅ Controller 集群（Raft 协议选主）
- ✅ Kafka 3.x 摆脱 ZooKeeper
- ⚠️ 集群规模决定性能上限

**下一步：** [🎮 Controller 控制器](/02-architecture/controller) — 集群大脑详解
