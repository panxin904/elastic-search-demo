---
title: 整体架构
date: 2026-08-15  # date-auto-injected
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

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Kafka Broker 内部线程模型</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">Acceptor / Processor / IO / ReplicaFetcher / LogCompactor</text>

  <!-- 线程分类 -->
  <g>
    <text x="60" y="90" font-size="13" font-weight="700" fill="#1e293b">① 网络层（3 类）</text>

    <rect class="at-hover-card" x="40" y="105" width="165" height="120" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="122" y="128" text-anchor="middle" font-size="12" font-weight="700" fill="#1e40af">Acceptor</text>
    <text x="122" y="148" text-anchor="middle" font-size="9" fill="#475569">1 个（每端点）</text>
    <text x="55" y="166" font-size="9" fill="#475569">• 接收新连接</text>
    <text x="55" y="181" font-size="9" fill="#475569">• round-robin 分配</text>
    <text x="55" y="196" font-size="9" fill="#475569">• 给 Processor</text>
    <text x="55" y="215" font-size="9" font-weight="700" fill="#1e40af">无读 socket</text>

    <rect class="at-hover-card" x="220" y="105" width="165" height="120" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="302" y="128" text-anchor="middle" font-size="12" font-weight="700" fill="#065f46">Processor</text>
    <text x="302" y="148" text-anchor="middle" font-size="9" fill="#475569">N 个（num.network.threads）</text>
    <text x="235" y="166" font-size="9" fill="#475569">• 维护 client 连接</text>
    <text x="235" y="181" font-size="9" fill="#475569">• read 请求</text>
    <text x="235" y="196" font-size="9" fill="#475569">• 解析协议</text>
    <text x="235" y="215" font-size="9" font-weight="700" fill="#065f46">→ RequestChannel</text>

    <rect class="at-hover-card" x="400" y="105" width="160" height="120" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="480" y="128" text-anchor="middle" font-size="12" font-weight="700" fill="#92400e">IO Thread</text>
    <text x="480" y="148" text-anchor="middle" font-size="9" fill="#475569">M 个（num.io.threads）</text>
    <text x="415" y="166" font-size="9" fill="#475569">• 从 channel 拉请求</text>
    <text x="415" y="181" font-size="9" fill="#475569">• 写 log + 副本同步</text>
    <text x="415" y="196" font-size="9" fill="#475569">• 写 response</text>
    <text x="415" y="215" font-size="9" font-weight="700" fill="#92400e">CPU 密集</text>
  </g>

  <!-- 后台线程 -->
  <g>
    <text x="60" y="245" font-size="13" font-weight="700" fill="#1e293b">② 后台线程（5 类）</text>

    <rect class="at-hover-card" x="40" y="260" width="110" height="80" rx="4" fill="#fee2e2" stroke="#dc2626"/>
    <text x="95" y="280" text-anchor="middle" font-size="10" font-weight="700" fill="#991b1b">ReplicaFetcher</text>
    <text x="95" y="298" text-anchor="middle" font-size="9" fill="#475569">从 leader 拉数据</text>
    <text x="95" y="315" text-anchor="middle" font-size="9" fill="#475569">per follower</text>

    <rect class="at-hover-card" x="160" y="260" width="110" height="80" rx="4" fill="#dcfce7" stroke="#10b981"/>
    <text x="215" y="280" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">LogCompactor</text>
    <text x="215" y="298" text-anchor="middle" font-size="9" fill="#475569">压缩 topic</text>
    <text x="215" y="315" text-anchor="middle" font-size="9" fill="#475569">compact 策略</text>

    <rect class="at-hover-card" x="280" y="260" width="110" height="80" rx="4" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="335" y="280" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">LogCleaner</text>
    <text x="335" y="298" text-anchor="middle" font-size="9" fill="#475569">delete 策略</text>
    <text x="335" y="315" text-anchor="middle" font-size="9" fill="#475569">delete.retention</text>

    <rect class="at-hover-card" x="400" y="260" width="160" height="80" rx="4" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="480" y="280" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">KafkaProducer/Consumer</text>
    <text x="480" y="298" text-anchor="middle" font-size="9" fill="#475569">应用层线程</text>
    <text x="480" y="315" text-anchor="middle" font-size="9" fill="#475569">+ 业务线程</text>
  </g>

  <!-- 请求处理流程 -->
  <g>
    <text x="60" y="360" font-size="13" font-weight="700" fill="#1e293b">③ 请求处理流程（ProduceRequest 路径）</text>

    <rect class="at-hover-card" x="40" y="375" width="520" height="90" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <rect class="at-hover-card" x="55" y="390" width="100" height="35" rx="3" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="105" y="408" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">Acceptor</text>
    <text x="105" y="422" text-anchor="middle" font-size="8" fill="#475569">新连接</text>

    <path d="M 155 407 L 180 407" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="180" y="390" width="105" height="35" rx="3" fill="#dcfce7" stroke="#10b981"/>
    <text x="232" y="408" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">Processor</text>
    <text x="232" y="422" text-anchor="middle" font-size="8" fill="#475569">read + 解析</text>

    <path d="M 285 407 L 310 407" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="310" y="390" width="115" height="35" rx="3" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="367" y="408" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">RequestChannel</text>
    <text x="367" y="422" text-anchor="middle" font-size="8" fill="#475569">共享队列</text>

    <path d="M 425 407 L 450 407" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="450" y="390" width="100" height="35" rx="3" fill="#fee2e2" stroke="#dc2626"/>
    <text x="500" y="408" text-anchor="middle" font-size="10" font-weight="700" fill="#991b1b">IO Thread</text>
    <text x="500" y="422" text-anchor="middle" font-size="8" fill="#475569">写 log + 副本</text>

    <text x="60" y="445" font-size="9" fill="#475569">RequestChannel 是 Processor / IO 之间的解耦桥梁（生产者消费者模式）</text>
  </g>
</svg>
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
