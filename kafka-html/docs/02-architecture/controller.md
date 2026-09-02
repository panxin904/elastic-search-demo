---
title: Controller 控制器
date: 2026-08-15  # date-auto-injected
---

# 🎮 Controller 控制器

> **Controller**是 Kafka 集群的**大脑**，负责集群元数据管理、Leader 选举、Broker 上下线通知。

## 🎯 Controller 是什么？

```
Controller = 集群中负责协调的 Broker
- 一个集群有一个 Active Controller
- 其他 Broker 是 Standby Controller（KRaft 模式）
- 通过 Raft 协议保证元数据一致性
- 不再依赖外部组件（Kafka 3.x 已移除 ZooKeeper）
```

## 📊 Controller 的职责

```
┌──────────────────────────────────────────────┐
│              Active Controller                │
├──────────────────────────────────────────────┤
│ 1. Partition Leader 选举                      │
│    - Broker 故障时选举新 Leader              │
│    - 触发 Preferred Replica Election         │
│                                               │
│ 2. Broker 管理                                │
│    - Broker 注册/下线                        │
│    - 维护 Broker 列表（cluster metadata）   │
│                                               │
│ 3. Topic 管理                                │
│    - Topic 创建/删除                         │
│    - 分区扩容                                │
│    - 分区重分配                              │
│                                               │
│ 4. 元数据持久化                              │
│    - 写入 __cluster_metadata topic         │
│    - 持久化集群状态                          │
└──────────────────────────────────────────────┘
```

## 🔄 KRaft Controller 集群

### KRaft 架构

```
┌────────────────────────────────────────────────────┐
│           Kafka KRaft Cluster                       │
│                                                     │
│  Node 1            Node 2            Node 3         │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐    │
│  │Controller│ ←→  │Controller│ ←→  │Controller│    │
│  │ (Active) │     │ (Standby)│     │ (Standby)│    │
│  └──────────┘     └──────────┘     └──────────┘    │
│        ↕ Raft       ↕ Raft           ↕ Raft        │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐    │
│  │  Broker  │     │  Broker  │     │  Broker  │    │
│  └──────────┘     └──────────┘     └──────────┘    │
└────────────────────────────────────────────────────┘
- Active Controller：处理所有写请求
- Standby Controller：从 Active 同步日志，热备
- 选举超时（默认 30 秒）触发新选举
```

### KRaft 优势

```
✅ 无需 ZooKeeper
   - 单一集群运维
   - 没有 ZK 性能瓶颈

✅ 快速选举
   - Raft 选举通常 1-2 秒
   - ZooKeeper 选举通常 10-30 秒

✅ 大规模支持
   - 支持 100 万级 Partition
   - ZooKeeper 只能支持几万级

✅ 强一致性
   - Raft 协议保证所有 Controller 元数据一致
   - 数据不会因 Controller 切换而丢失
```

## 🔄 Controller 选举流程

![Kafka Controller 选举时序](/kafka-controller-election.svg)

### 启动时选举

```
1. 节点启动，向其他节点发送 RequestVote RPC
2. 节点收到多数票（n/2 + 1）后成为 Leader
3. Leader 开始处理请求
4. Followers 复制 Leader 的日志
```

### Controller 故障转移

```
时间线：
  T0  Active Controller 宕机
  T1  Standby Controller 心跳超时
  T2  Standby Controller 发起选举
  T3  多数 Standby 同意（n/2+1）
  T4  新 Controller 切换为 Active
  T5  集群恢复服务

选举超时时间：
  - 受 election.timeout.ms 控制（默认 30 秒）
  - 选举期间集群处于只读状态
  - 通常选举时间 < 5 秒
```

## 📊 Controller 内部数据

### 元数据缓存

```java
// Controller 维护的关键数据结构
public class ControllerContext {
    private Map<String, Topic> topics;                    // 所有 Topic
    private Map<Partition, PartitionState> partitionStates; // 所有 Partition
    private Set<Integer> liveBrokers;                      // 在线 Broker
    private Map<Integer, Map<Topic, Partition>> replicasForBrokers;  // 副本分配
    private Map<Group, SubscriptionState> groups;          // 消费者组
}
```

### 关键 Topic

```
__cluster_metadata
  - KRaft 模式下的元数据日志（Raft Log）
  - 持久化所有 Controller 状态变更

__consumer_offsets
  - 存储所有消费者组的 offset
  - 默认 50 个 Partition

__transaction_state
  - 存储事务状态（Kafka 事务）
  - 默认 50 个 Partition
```

## 🔧 Controller 配置

```properties
# ==== KRaft 模式配置 ====
process.roles=broker,controller
controller.quorum.voters=1@node1:9093,2@node2:9093,3@node3:9093
controller.listener.names=CONTROLLER

# ==== Controller 选举相关 ====
# 选举超时（毫秒）
controller.election.timeout.ms=30000

# Controller 元数据日志配置
metadata.log.dir=/data/kafka-meta    # KRaft 元数据日志目录
metadata.log.max.retention.bytes=1073741824

# ==== Controller 处理线程 ====
num.controller.threads=4
```

## 🛠️ Controller 管理的实际操作

### 创建 Topic（Controller 处理）

```
1. 客户端发送 CREATE TOPIC 请求
2. Controller 收到请求
3. 选择 Partition Leader（均衡分配）
4. 写入元数据日志（__cluster_metadata）
5. 复制到 Standby Controllers
6. 通知所有 Brokers 元数据变更
7. Brokers 响应 MetadataRequest，更新本地元数据
```

### 故障转移（Controller 处理）

```
1. Broker 1 心跳超时
2. Controller 监测到 Broker 1 离线
3. 对 Broker 1 上的所有 Leader Partition 触发选举
4. 从 ISR 中选新 Leader
5. 更新元数据
6. 通知所有 Brokers
7. Producers 收到 MetadataRefresh，开始发到新 Leader
```

## 📊 Controller 性能

```
Controller 处理能力：
  - 单 Controller 可处理 10000+ Broker 元数据更新
  - Controller 是单点（Active）
  - 元数据变更先写入 Raft Log，再通知 Brokers

性能调优：
  - 增加 Standby Controller 数量（提高可靠性）
  - controller.quorum.voters 选择奇数（3、5、7）
  - 元数据变更频率高时考虑分散 Topic
```

## ⚠️ Controller 故障场景

### 场景 1：Active Controller 宕机

```
现象：所有 Producer 收到 NotControllerException
处理：
  1. Standby Controller 在 30 秒内发起选举
  2. 新 Active Controller 产生
  3. 集群恢复（Producer 收到 MetadataResponse 后自动重试）
```

### 场景 2：网络分区

```
现象：Controller 无法与其他 Broker 通信
处理：
  1. 分区侧的 Controller 自动降级
  2. 多数派分区保留 Active Controller（继续服务）
  3. 少数派分区拒绝写入（保护数据一致性）
```

### 场景 3：元数据不一致

```
现象：__cluster_metadata 日志与 Broker 状态不一致
处理：
  1. Raft 协议保证一致性
  2. Controller 会自动重放日志
  3. 极少见，通常是配置错误
```

## 🎯 总结

**Controller 核心要点**：
- ✅ Kafka 集群的大脑（元数据管理）
- ✅ KRaft 模式：Active + Standby
- ✅ 选举基于 Raft 协议（快 + 强一致）
- ✅ 1 个 Active + N 个 Standby
- ✅ Kafka 3.x 不再依赖 ZooKeeper
- ⚠️ 选举期间集群只读
- ⚠️ Active Controller 单点（但 Standby 热备）

**下一步：** [🗂️ 分区副本机制](/02-architecture/replica) — 数据可靠性详解


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
