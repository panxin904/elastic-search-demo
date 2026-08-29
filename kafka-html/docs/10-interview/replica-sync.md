---
title: 副本同步机制
date: 2026-08-15  # date-auto-injected
---

# 🔁 副本同步机制

> Kafka 的副本同步机制是**数据可靠性和高可用**的核心。本章深入讲解 Leader-Follower 同步的完整流程。

## 🎯 副本同步全景

```
┌────────────────────────────────────────────┐
│              Partition 0                     │
│                                              │
│  Leader (Broker 1)    Follower (Broker 2)  │
│  ┌─────────────┐      ┌─────────────┐     │
│  │ msg-1       │      │ msg-1       │     │
│  │ msg-2       │      │ msg-2       │     │
│  │ msg-3 (LEO) │ ←──→ │ msg-3 (HW)  │     │
│  └─────────────┘      └─────────────┘     │
│        ↑                      ↑             │
│        └─────── LEO=3 ────────┘             │
│                                              │
│  Follower (Broker 3)                       │
│  ┌─────────────┐                           │
│  │ msg-1       │                           │
│  │ msg-2       │                           │
│  │ msg-3       │                           │
│  └─────────────┘                           │
└────────────────────────────────────────────┘
```

## 📊 关键概念

### LEO（Log End Offset）

```
LEO = 日志末端偏移量
  - 表示副本已写入到哪里
  - 下一个待写入消息的 offset

每个副本都有自己的 LEO：
  - Leader LEO：3（已写入 3 条）
  - Follower 1 LEO：3（同步了 3 条）
  - Follower 2 LEO：2（同步了 2 条，落后）
```

### HW（High Watermark）

```
HW = 已提交偏移量（消费可见的边界）
  - HW = min(所有 ISR 副本的 LEO)
  - Consumer 只能读到 HW 之前
  - HW 之后的消息还未被所有 ISR 同步

例如：
  - Leader LEO = 3
  - Follower 1 LEO = 3
  - Follower 2 LEO = 2
  - HW = min(3, 3, 2) = 2
  - Consumer 只能看到 offset 0, 1, 2
```

### LSO（Log Start Offset）

```
LSO = 日志起始偏移量
  - 因消息删除可能大于 0
  - Consumer 最早可读位置
```

## 🔄 同步流程

### Follower 拉取同步

```
时间线：
  T0   Leader 写入 msg(offset=100)
  T1   Leader 更新 LEO=101
  T2   Follower 发送 FetchRequest(startOffset=99)
  T3   Leader 返回 FetchResponse（包含 msg-100 + LEO=101）
  T4   Follower 写入本地 log
  T5   Follower 更新 LEO=100
  T6   Leader 更新 HW=min(Leader LEO, 所有 Follower LEO)=100
  T7   Consumer 看到 offset 100
```

### 完整时序图

```
Producer          Leader            Follower 1      Follower 2
    |                |                  |                |
    |--send msg-100->|                  |                |
    |                |--写入 log        |                |
    |                |  (LEO=101)      |                |
    |                |<--FetchRequest(99)|              |
    |                |                  |                |
    |                |--FetchResponse(msg-100, LEO=101)-->|  ← 异步
    |                |                  |                |
    |                |<--Ack-----------|                |
    |                |  LEO=100         |                |
    |                |                  |                |
    |                |--FetchRequest---|                |
    |                |                  |                |
    |                |--FetchResponse(msg-100)----------->|  ← 异步
    |                |                  |                |
    |                |                  |              <-写入 log
    |                |                  |                |  LEO=100
    |                |                  |                |
    |                |  HW=min(101,100,100)=100          |
    |                |                  |                |
    |<--ack----------|                  |                |
    |                |                  |                |
```

## 📊 关键源码分析

### Leader 处理 Produce 请求

```java
// Kafka Apis.handleProduceRequest()
public ProduceResponse handleProduceRequest(ProduceRequest request) {
    // 1. 写入本地 log
    log.append(messages);
    
    // 2. 更新 LEO
    leaderLog.leo = leaderLog.leo + messages.size();
    
    // 3. 等待 ISR 副本同步
    if (acks == "all") {
        // 等待 min.insync.replicas 个副本确认
        while (ackedReplicas.size() < minISR) {
            waitForFollowerAcks();
        }
    }
    
    // 4. 更新 HW
    long hw = computeHighWatermark();
    
    // 5. 返回响应
    return new ProduceResponse(hw);
}
```

### Follower 拉取数据

```java
// ReplicaFetcherThread.fetchFromLeader()
public void fetchFromLeader() {
    // 1. 构造 FetchRequest
    FetchRequest request = new FetchRequest(
        topic, partition,
        follower.leo,         // 从 Follower LEO 开始
        maxBytes
    );
    
    // 2. 发送到 Leader
    SendResult result = leader.send(request);
    
    // 3. 接收响应
    FetchResponse response = result.get();
    
    // 4. 写入本地 log
    log.append(response.messages);
    
    // 5. 更新 LEO
    follower.leo = follower.leo + response.messages.size();
    
    // 6. 发送 Ack 给 Leader
    leader.send(new FetchResponseAck(follower.leo));
}
```

## 📊 数据丢失与不一致分析

### 场景 1：acks=1，Leader 故障

```
时间线：
  T0   Producer 发送 msg-100（acks=1）
  T1   Leader 写入 log（LEO=101）
  T2   Leader 返回 ack（ack=1，不等副本）
  T3   Leader 故障
  T4   Follower 1 被选为 Leader（LEO=99）
  T5   Producer 不知道 msg-100 已经写入，重发
  T6   Follower 1 收到，LEO=100（重复）

结果：
  - msg-100 写入两次（重复）
  - msg-101 丢失（Leader 没来得及同步给 Follower）
```

### 场景 2：acks=all，min.insync.replicas=2

```
时间线：
  T0   Producer 发送 msg-100（acks=all）
  T1   Leader 写入 log
  T2   Leader 等待 ISR（1 个 Follower）
  T3   Follower 写入（LEO=101）
  T4   Follower Ack
  T5   Leader 收到 Ack，返回给 Producer
  T6   Leader 故障
  T7   Follower 1 被选为 Leader（LEO=101）
  T8   Producer 重连 Follower 1
  T9   继续写入（不丢）

结果：
  - 不丢
  - 可能有重复（Producer 重试时）
```

## 📊 ISR 管理

### Follower 加入 ISR 条件

```
Follower 保持 ISR 成员的条件：
  - 与 Leader 的 LEO 差距 ≤ replica.lag.time.max.ms（默认 30s）
  - 持续满足条件

被踢出 ISR：
  - 超过 replica.lag.time.max.ms 未同步
  - 网络问题、磁盘 IO 慢
```

### Follower 重新加入 ISR

```
被踢出 ISR 后：
  - 标记为 OSR（Out-of-Sync Replicas）
  - 继续尝试从 Leader 同步
  - 追上 Leader 后重新加入 ISR

⚠️ 重新加入期间：
  - 该 Follower 不参与 Leader 选举
  - 即使 OSR 包含较新数据，也不能选为 Leader（除非 unclean.election）
```

## 📊 副本分配策略

### 默认策略

```python
# Kafka 副本分配算法（简化版）
def assign_replicas(topic, partitions, brokers):
    for partition in range(partitions):
        # 第一个副本（Leader）：轮询选择
        leader = brokers[partition % len(brokers)]
        
        # 其他副本：在不同机架/不同 broker 上
        replicas = [leader]
        for i in range(1, replication_factor):
            broker_idx = (partition + i) % len(brokers)
            replicas.append(brokers[broker_idx])
        
        assign(partition, replicas)
```

### 机架感知分配

```properties
# broker 配置
broker.rack=us-east-1a    # 机架 A
broker.rack=us-east-1b    # 机架 B
broker.rack=us-east-1c    # 机架 C

# Topic 创建时副本跨机架
# replicas 会分布在不同机架
```

## 📊 高可用场景

### 场景 1：1 个 Follower 故障

```
原始 ISR：[Leader(B1), Follower(B2), Follower(B3)]
故障后 ISR：[Leader(B1), Follower(B3)]
min.insync.replicas=2

正常：2 副本写入（Leader + B3），HW = Leader LEO
新 Follower B2 加入后，自动追上 Leader，重新加入 ISR
```

### 场景 2：Leader 故障

```
原 Leader B1 故障
Controller 检测心跳超时（session.timeout.ms）
从 ISR [B2, B3] 中选新 Leader（如 B2）
Producer/Consumer 收到 MetadataRefresh，重连 B2

恢复时间：通常 5-15 秒
数据：可能丢失（如果 Leader 没来得及同步）
```

### 场景 3：所有 ISR 不可用

```
如果 unclean.leader.election.enable=false
  → 等待 ISR 中任意一个恢复
  → Partition 不可用（无法写）

如果 unclean.leader.election.enable=true
  → 从 OSR 中选 Leader
  → 可能丢失数据（OSR 落后 ISR）
  → 但 Partition 仍可用
```

## 🛠️ 实战：监控副本同步

### 关键指标

```bash
# 1. 查看 ISR 列表
kafka-topics.sh --describe --bootstrap-server localhost:9092 \
    --topic orders | grep -E "Partition|Isr"

# 2. Under-Replicated Partitions
kafka-topics.sh --describe --bootstrap-server localhost:9092 \
    --topic orders | grep "Isr:" | awk '{split($0, a, "Isr: "); print a[2]}'

# 3. 监控同步延迟
# 通过 JMX: kafka.server:type=ReplicaFetcherManager,name=MaxLag,topic=orders,partition=0
```

### JMX 指标

```
kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions
kafka.server:type=ReplicaFetcherManager,name=MaxLag
kafka.server:type=ReplicaManager,name=ISRShrinksPerSec
kafka.server:type=ReplicaManager,name=ISRExpandsPerSec
```

### Prometheus 告警

```yaml
- alert: KafkaUnderReplicatedPartitions
  expr: sum(kafka_topic_partition_under_replicated_partition_count) > 0
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "Kafka 存在副本同步失败的 Partition"

- alert: KafkaReplicaLagHigh
  expr: kafka_server_replica_fetcher_manager_max_lag > 10000
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "副本同步延迟超过 10000"
```

## ⚠️ 常见问题

### 问题 1：ISR 频繁收缩

```
原因：
  - 网络抖动
  - Follower GC 停顿
  - 磁盘 IO 慢

解决：
  1. 增加 replica.lag.time.max.ms
  2. 优化 GC
  3. 升级磁盘
```

### 问题 2：副本同步延迟大

```
原因：
  - Follower 处理慢
  - 网络带宽不足

解决：
  1. 监控 lag 指标
  2. 优化 Follower
  3. 升级网络
```

### 问题 3：数据丢失风险

```
场景：acks=1 + Leader 故障
解决：
  - acks=all + min.insync.replicas=2
  - 或同步双写（应用层保证）
```

## 🎯 总结

**副本同步机制核心要点**：
- ✅ LEO 表示日志末端，HW 表示已提交边界
- ✅ Follower 主动拉取（不是 Leader 推送）
- ✅ ISR 机制保证数据一致性
- ✅ 多副本 + min.insync.replicas 防止数据丢失
- ✅ Leader 选举从 ISR 中选新 Leader
- ⚠️ unclean.election 开启可恢复服务但可能丢数据
- ⚠️ 副本同步延迟影响可用性

**下一步：** [🚨 消息丢失解决方案](/10-interview/message-loss) — 不丢消息实战
