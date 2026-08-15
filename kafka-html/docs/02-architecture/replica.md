---
title: 分区副本机制
---

# 🗂️ 分区副本机制

> **副本（Replica）**是 Kafka 高可用的基石。每个 Partition 有多个副本，分布在不同 Broker，Leader 故障时自动选举新 Leader。

## 🎯 副本机制基础

### 副本结构

```
Topic: orders (replication-factor=3)
├── Partition 0
│   ├── Replica 0 (Leader) on Broker 1    ← 处理读写
│   ├── Replica 1 (Follower) on Broker 2  ← 同步数据
│   └── Replica 2 (Follower) on Broker 3  ← 同步数据
├── Partition 1
│   ├── Replica 0 (Leader) on Broker 2
│   ├── Replica 1 (Follower) on Broker 3
│   └── Replica 2 (Follower) on Broker 1
└── Partition 2
    ├── Replica 0 (Leader) on Broker 3
    ├── Replica 1 (Follower) on Broker 1
    └── Replica 2 (Follower) on Broker 2
```

### 关键术语

```
AR（Assigned Replicas）
  - 分区所有副本的集合
  - 由副本分配策略决定

ISR（In-Sync Replicas）
  - 与 Leader 保持同步的副本
  - 故障转移时只从 ISR 选 Leader

OSR（Out-of-Sync Replicas）
  - 落后 Leader 太多的副本
  - 不在 ISR 列表中

Leader Replica
  - 处理读写请求
  - 由 Controller 选举

Follower Replica
  - 从 Leader 拉取数据
  - 备用 Leader
```

## 🔄 副本同步流程

### Follower 拉取同步

```
时间线：
  T0   Leader 写入 msg(offset=100)
  T1   Leader 更新 LEO（Log End Offset）= 101
  T2   Follower 发送 FetchRequest(startOffset=99)
  T3   Leader 返回 msg + 元数据
  T4   Follower 写入本地 log
  T5   Follower 更新 LEO = 100
  T6   Follower 发送 FetchRequest(startOffset=100)
  T7   Leader 返回 msg + 元数据
  T8   Follower 写入本地 log
  T9   Follower 更新 LEO = 101
```

### 关键概念

```
LEO（Log End Offset）
  - 日志末端偏移量
  - 表示副本写入到哪里

HW（High Watermark）
  - 已提交偏移量（消费者可见的边界）
  - HW = min(所有 ISR 的 LEO)
  - 消费者只能读到 HW 之前的数据

LSO（Log Start Offset）
  - 日志起始偏移量（默认 0）
  - 因消息删除可能大于 0
```

```
Partition (Leader):  [m0 m1 m2 m3 m4 m5]    LEO=6, HW=4
Partition (Follower A): [m0 m1 m2 m3]    LEO=4   ← 同步
Partition (Follower B): [m0 m1 m2 m3 m4]  LEO=5   ← 稍慢

HW = min(LEO_A, LEO_B, LEO_Leader) = 4
Consumer 只能看到 offset 0-3
m4、m5 已写入 Leader，但还未被所有 Follower 同步
```

## ⚙️ 副本同步配置

```properties
# ==== 副本相关配置 ====
default.replication.factor=3        # Topic 默认副本数
min.insync.replicas=2               # 最小同步副本数（影响 acks=all 行为）
replica.fetch.min.bytes=1           # 拉取最小字节（减少小请求）
replica.fetch.max.bytes=1048576     # 拉取最大字节（默认 1MB）
replica.fetch.wait.max.ms=500       # 长轮询等待时间

# ==== ISR 管理 ====
replica.lag.time.max.ms=30000       # Follower 超时时间（默认 30s）
# 超过这个时间被踢出 ISR

# ==== 落后副本处理 ====
unclean.leader.election.enable=false # 是否允许 OSR 当 Leader（关闭更安全）
```

## 📊 副本与生产者关系

### acks 配置（生产者端）

```java
Properties props = new Properties();
props.put(ProducerConfig.ACKS_CONFIG, "all");
```

| acks 值 | 行为 | 可靠性 | 性能 |
|---------|------|--------|------|
| **0** | 不等响应 | ❌ 可能丢失 | ⭐⭐⭐⭐⭐ |
| **1** | 等 Leader 写入 | ⚠️ Leader 故障可能丢失 | ⭐⭐⭐⭐ |
| **all** (或 -1) | 等所有 ISR 写入 | ✅ 强保证 | ⭐⭐ |

```
acks=all + min.insync.replicas=2：
  - Leader 写入 + ISR 中至少 1 个 Follower 写入 = 才返回成功
  - 即使 Leader 故障，剩余 ISR 中有完整数据
  - 最安全的配置
```

## 📊 副本与消费者关系

```
Consumer 只能读取 HW 之前的数据：

Producer 发送 m5 → Leader 写入 → Follower 同步
                                              ↓
                                          HW=5（所有 ISR 同步完成）
                                          ↓
Consumer.poll() 读取 → 看到 m0~m4 + m5

Producer 发送 m6 → Leader 写入 → Follower 未同步
                                              ↓
                                          HW=5（Follower 还没追上）
                                          ↓
Consumer.poll() 读取 → 只看到 m0~m4（HW 边界）
```

## ⚠️ 副本同步异常场景

### 场景 1：Follower 落后

```
原因：Follower GC、网络故障、磁盘慢
处理：
  1. 超过 replica.lag.time.max.ms（30s）被踢出 ISR
  2. OSR 不参与 Leader 选举
  3. Follower 恢复后，重新追上 Leader，加入 ISR

影响：
  - Leader 选举时，OSR 不可选
  - acks=all 时不等待 OSR（只等 ISR）
```

### 场景 2：Leader 故障

```
原因：Leader Broker 宕机
处理流程：
  1. Controller 检测到 Leader 失联（超时）
  2. 从 ISR 中选新 Leader
  3. Producer 收到 MetadataResponse，更新到新 Leader
  4. Consumer 收到 FetchResponse，自动重连新 Leader

Producer 处理：
  - 自动重试（retries 配置）
  - 幂等性保证（enable.idempotence=true）
```

### 场景 3：所有 ISR 不可用

```
现象：Leader 故障，且 ISR 中所有 Follower 都不可用
处理：
  - 如果 unclean.leader.election.enable=false
    → 等待旧 Leader 恢复（分区不可用）
  - 如果 unclean.leader.election.enable=true
    → 从 OSR 中选新 Leader（可能数据丢失，但分区可用）
```

## 🔧 副本分配策略

### 默认分配策略

```java
// Kafka 0.11+ 默认分配策略
// 目标：均匀分配副本到所有 Broker
// 规则：
//   1. 副本因子 ≤ Broker 数量
//   2. 第一个副本随机选择
//   3. 其他副本选择不同机架（如果配置）
//   4. 所有副本分布在不同 Broker
```

### 手动重新分配

```bash
# 1. 生成 reassignment.json
cat > reassign.json << EOF
{
  "version": 1,
  "partitions": [
    {"topic": "orders", "partition": 0, "replicas": [1, 2]},
    {"topic": "orders", "partition": 1, "replicas": [2, 3]},
    {"topic": "orders", "partition": 2, "replicas": [3, 1]}
  ]
}
EOF

# 2. 执行重新分配
bin/kafka-reassign-partitions.sh \
    --bootstrap-server localhost:9092 \
    --reassignment-json-file reassign.json \
    --execute

# 3. 验证进度
bin/kafka-reassign-partitions.sh \
    --bootstrap-server localhost:9092 \
    --reassignment-json-file reassign.json \
    --verify
```

## 🛠️ 副本数选择建议

```
小集群（3 节点）：
  - replication.factor=3（满副本）
  - min.insync.replicas=2（容忍 1 节点故障）

中集群（5-10 节点）：
  - replication.factor=3（多数派）
  - min.insync.replicas=2

大集群（10+ 节点）：
  - replication.factor=3（成本与可靠性平衡）
  - 重要数据可设为 5
  - min.insync.replicas=2

⚠️ 副本数不是越多越好：
  - 副本数 = 3 时，磁盘空间 3 倍
  - 副本数 = 5 时，写入延迟增加
  - 一般 3 副本足够
```

## 🎯 总结

**副本机制核心要点**：
- ✅ 每个 Partition 有 N 个副本（默认 3）
- ✅ Leader 处理读写，Follower 同步数据
- ✅ ISR（同步副本）是故障转移的候选
- ✅ acks=all + min.insync.replicas=2 最强保证
- ✅ Controller 选举新 Leader（从 ISR 选）
- ⚠️ unclean.election 关闭可避免数据丢失
- ⚠️ 副本数影响磁盘空间和写入延迟

**下一步：** [👑 Leader 选举](/02-architecture/leader-election) — 故障转移详解
