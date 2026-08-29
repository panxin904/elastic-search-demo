---
title: Leader 选举机制
date: 2026-08-15  # date-auto-injected
---

# 👑 Leader 选举机制

> Leader 选举是 Kafka **高可用**的核心机制。理解选举过程对故障排查和性能优化至关重要。

## 🎯 Leader 选举概述

```
Leader 选举触发场景：
  1. Broker 宕机（最常见）
  2. 网络分区
  3. 主动重启
  4. ISR 收缩后

选举目标：
  - 从 ISR 中选新 Leader
  - 保证数据一致性（unclean.election=false）
  - 快速恢复（通常 5-15 秒）
```

## 🔄 选举流程

### 完整时序图

```
时间线（毫秒）：
  T0    Leader B1 宕机
  T1    Follower B2、B3 心跳检测到 B1 失联
        （session.timeout.ms/2 内）
  T2    Controller 检测到 B1 失联（quorum 判定）
  T3    Controller 触发 Leader 选举
        从 ISR 中选新 Leader（假设 B3 被选）
  T4    Controller 更新元数据
        __cluster_metadata log 中记录新 Leader
  T5    Controller 通知所有 Broker
        通过 MetadataResponse
  T6    Producer/Consumer 收到通知
  T7    自动重连新 Leader B3
  T8    恢复正常消费/生产

总耗时：通常 5-15 秒
```

### 选举源码分析

```java
// Controller 处理 Broker 失联
public void onBrokerFailure(int failedBrokerId) {
    // 1. 标记 Broker 离线
    liveBrokers.remove(failedBrokerId);
    
    // 2. 找到所有 Leader 在该 Broker 的 Partition
    List<Partition> affectedPartitions = partitionsOnBroker(failedBrokerId);
    
    // 3. 对每个 Partition 选举新 Leader
    for (Partition partition : affectedPartitions) {
        // 3.1 选择新 Leader（从 ISR 中）
        int newLeaderId = selectNewLeader(partition);
        
        // 3.2 更新元数据
        updatePartitionLeader(partition, newLeaderId);
        
        // 3.3 写入 __cluster_metadata
        appendToMetadataLog(partition, newLeaderId);
        
        // 3.4 通知所有 Broker
        notifyBrokers(partition, newLeaderId);
    }
}

private int selectNewLeader(Partition partition) {
    // 优先：Preferred Replica（AR 中的第一个）
    for (int replica : partition.assignedReplicas) {
        if (partition.isr.contains(replica)) {
            return replica;  // 返回第一个 ISR 中的副本
        }
    }
    
    // 兜底：如果 unclean.leader.election.enable=true，从 AR 中选
    if (unclean.leader.election.enable) {
        return partition.assignedReplicas[0];
    }
    
    // 否则选举失败，Partition 不可用
    throw new ElectionFailedException();
}
```

## 📊 Controller 选举

### Kafka 2.x：基于 ZooKeeper

```
ZooKeeper 集群：
  /brokers/ids        # 注册的 Broker 列表
  /controller          # Controller 临时节点（第一个创建成功的成为 Controller）

Controller 选举：
  1. 每个 Broker 启动时尝试创建 /controller 临时节点
  2. 创建成功的成为 Active Controller
  3. 其他成为 Standby Controller
  4. Active 故障 → 临时节点删除
  5. Standby 重新选举
  6. 选举时间：10-30 秒（ZooKeeper 性能限制）
```

### Kafka 3.x：基于 KRaft

```
KRaft 集群：
  - Active Controller（处理写请求）
  - 多个 Standby Controllers（热备）
  - 通过 Raft 协议同步

选举流程：
  1. Active Controller 心跳超时
  2. Follower 进入 Candidate 状态
  3. 增加 Term，发起 RequestVote RPC
  4. 获得多数派投票后成为新 Leader
  5. 立即开始处理请求

选举时间：1-5 秒（比 ZooKeeper 快 5-10 倍）
```

### KRaft 选举细节

```
节点状态：
  - Leader：处理所有写请求
  - Follower：复制日志
  - Candidate：选举中的候选

选举触发：
  - Follower 在 election.timeout 内未收到 Leader 心跳
  - 超时时间随机化（避免同时选举）

投票规则：
  - 每个节点同一 Term 只能投 1 票
  - Candidate 的日志至少和自己一样新
  - 获得多数派投票（n/2 + 1）即获胜

Term（任期）：
  - 单调递增整数
  - 每次选举开始新 Term
  - 旧的 Leader 收到新 Term 请求会立即退位
```

## 📊 Partition 选举与 Controller 选举的区别

```
Controller 选举：
  - 范围：集群级别（1 个 Controller）
  - 频率：低（只在 Controller 故障时）
  - 时间：秒级

Partition 选举：
  - 范围：Partition 级别（多个 Partition 同时）
  - 频率：高（每次 Broker 故障都会触发）
  - 时间：毫秒级

两者独立：
  - Controller 故障不影响已选举的 Leader
  - Partition 故障不影响 Controller
```

## 📊 unclean.leader.election 配置详解

### 两种策略对比

```
clean leader election（默认，unclean.leader.election.enable=false）：
  - 只能从 ISR 中选 Leader
  - 保证数据一致性
  - 可能导致 Partition 不可用（如果所有 ISR 都挂了）

unclean leader election（unclean.leader.election.enable=true）：
  - 可以从 OSR 中选 Leader
  - 即使所有 ISR 都挂了，集群仍可用
  - 可能丢失数据（OSR 落后 ISR）
```

### 配置选型

```
✅ 金融、订单场景：unclean=false
   - 数据一致性优先，宁可不可用也不丢数据

✅ 日志、监控场景：unclean=true
   - 可用性优先，可以容忍少量数据丢失

⚠️ 默认 unclean=false（推荐）
```

## 📊 选举相关配置

### Controller 选举配置

```properties
# ==== KRaft 模式 ====
process.roles=broker,controller
controller.quorum.voters=1@broker-1:9093,2@broker-2:9093,3@broker-3:9093
controller.election.timeout.ms=30000

# ==== 自动重新平衡（KRaft 模式特有） ====
auto.leader.rebalance.enable=true
leader.imbalance.per.broker.percentage=10
leader.imbalance.check.interval.seconds=300
```

### Partition 选举配置

```properties
# ==== 选举相关 ====
unclean.leader.election.enable=false      # 是否允许 unclean 选举
default.replication.factor=3              # 默认副本数
min.insync.replicas=2                     # 最小同步副本数
replica.lag.time.max.ms=30000             # Follower 落后超时

# ==== 自动重新平衡 ====
auto.leader.rebalance.enable=true          # 自动平衡 Leader
leader.imbalance.per.broker.percentage=10  # 不平衡阈值
leader.imbalance.check.interval.seconds=300
```

### Producer 选举感知

```java
Properties props = new Properties();
// 控制客户端在 Leader 选举期间的行为
props.put(ProducerConfig.MAX_BLOCK_MS_CONFIG, 60000);  // 最大阻塞时间
props.put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, 30000);  // 请求超时
```

## 📊 选举优化

### 减少选举时间

```properties
# 减小超时时间（更快发现故障）
group.session.timeout.ms=10000     # Consumer Group 会话超时（默认 45s）
group.heartbeat.interval.ms=3000   # 心跳间隔（默认 3s）

# Broker 端
group.min.session.timeout.ms=6000  # 最小会话超时
replica.lag.time.max.ms=10000     # 减小 ISR 收缩时间
```

### 减少 Rebalance 影响

```properties
# 使用 CooperativeSticky 策略（增量 Rebalance）
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor

# 静态成员（减少滚动升级 Rebalance）
group.instance.id=consumer-pod-1
```

## 📊 选举监控

### 关键指标

```bash
# Leader 选举速率
kafka_controller_controller_stats_leader_election_rate_and_time_ms

# Unclean 选举速率
kafka_controller_controller_stats_unclean_leader_election_rate_and_time_ms

# Controller 状态
kafka_controller_active_count

# Under-Replicated Partitions
kafka_topic_partition_under_replicated_partition_count
```

### Prometheus 告警

```yaml
groups:
  - name: kafka_election
    rules:
      # Controller 不可用
      - alert: KafkaControllerDown
        expr: kafka_controller_active_count == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Kafka Controller 不可用"
      
      # 频繁 Leader 选举
      - alert: KafkaFrequentLeaderElection
        expr: rate(kafka_controller_controller_stats_leader_election_rate_and_time_ms[1h]) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Leader 选举频繁"
      
      # Unclean 选举（数据可能丢失）
      - alert: KafkaUncleanLeaderElection
        expr: rate(kafka_controller_controller_stats_unclean_leader_election_rate_and_time_ms[5m]) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "发生 Unclean 选举，可能丢失数据"
```

## 📊 选举故障排查

### 故障 1：选举卡住

```
症状：Partition 长时间不可用
原因：
  1. Controller 选举卡住
  2. unclean.election=false 且 ISR 全挂
  3. 网络分区

排查：
  1. 查看 Controller 日志
  2. 检查 KRaft 状态
  3. 检查 ISR 列表

解决：
  1. 重启 Controller
  2. 临时开启 unclean.election
  3. 修复网络
```

### 故障 2：频繁选举

```
症状：Leader 选举频率高（> 10 次/小时）
原因：
  1. Broker 频繁故障
  2. 网络不稳定
  3. session.timeout.ms 过小
  4. GC 停顿导致心跳丢失

排查：
  1. 查看 Broker 健康
  2. 检查 GC 日志
  3. 检查网络

解决：
  1. 增加 session.timeout.ms
  2. 优化 GC
  3. 检查网络
```

### 故障 3：选举时间过长

```
症状：选举耗时 > 30 秒
原因：
  1. Controller 选举慢（ZooKeeper 模式）
  2. 网络分区导致选举超时

解决：
  1. 升级 KRaft（Kafka 3.x）
  2. 增加 election.timeout
  3. 优化网络
```

## 🛠️ 实战：选举调优

### 步骤 1：基线监控

```bash
# 1. 监控选举频率
watch -n 60 "kafka-controller-status.sh --bootstrap-server localhost:9092"

# 2. 查看 ISR 列表
kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic orders

# 3. 监控选举延迟
# JMX: kafka.controller:type=ControllerStats,name=LeaderElectionRateAndTimeMs
```

### 步骤 2：调优配置

```properties
# 1. 选举超时（更短 = 更快发现故障，但易误判）
controller.election.timeout.ms=15000  # 默认 30s，调到 15s

# 2. 心跳超时（与选举超时配合）
group.session.timeout.ms=10000      # 默认 45s
group.heartbeat.interval.ms=3000    # 默认 3s

# 3. 副本同步超时
replica.lag.time.max.ms=15000       # 默认 30s

# 4. 选举策略
partition.assignment.strategy=org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

### 步骤 3：故障演练

```bash
# 1. Kill 一个 Broker
ssh kafka-1 "kill -9 \$(pgrep -f kafka)"

# 2. 观察选举过程
# - 选举耗时
# - 客户端是否自动重连
# - 数据是否丢失

# 3. 重启 Broker
ssh kafka-1 "systemctl start kafka"

# 4. 验证恢复
kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic orders
```

## 🎯 总结

**Leader 选举核心要点**：
- ✅ Controller 从 ISR 中选新 Leader
- ✅ KRaft 比 ZooKeeper 快 5-10 倍
- ✅ unclean.election=false 保证一致性
- ✅ CooperativeSticky 减少 Rebalance 影响
- ✅ 选举时间通常 5-15 秒
- ⚠️ unclean.election 开启可恢复但丢数据
- ⚠️ 选举期间 Partition 短暂不可用
- ⚠️ 频繁选举影响可用性

**下一步：** [🎯 Exactly Once 实现](/10-interview/exactly-once) — 精确一次语义


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
