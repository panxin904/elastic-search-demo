---
title: 消费者组
date: 2026-08-15  # date-auto-injected
---

# 👥 消费者组

> **Consumer Group**是 Kafka 核心概念之一，理解其工作原理是掌握 Kafka 的关键。本章深入 Group 协作、Rebalance、Offset 提交等机制。

## 🎯 消费者组是什么？

```
Consumer Group = 一组 Consumer 实例协作消费同一个 Topic

核心规则：
  ✅ 同组内：每条消息只被组内一个 Consumer 消费（负载均衡）
  ✅ 不同组：每条消息被每个组消费一次（广播）
  ✅ 每组独立维护 Offset
```

### 工作模型

```
Topic: orders (3 partitions)

Consumer Group A:                 Consumer Group B:
  C1 (consumer-1) → P0              D1 → P0
  C2 (consumer-2) → P1, P2          D2 → P1, P2
  
同组内：每条消息只被组内一个 Consumer 处理
不同组：每条消息被每个组都消费一次
```

## 🛠️ 模拟器：消费者组再平衡

<ClientOnly>
  <ConsumerSimulator />
</ClientOnly>

试试用模拟器观察：
- 3 个 Partition 分配给 1 个 Consumer
- 新增 Consumer 触发 Rebalance
- 模拟故障触发 Rebalance

## 📊 关键术语

```
Consumer Group ID
  - 标识一个 Consumer Group
  - 同组内 Consumer 协作消费
  - 不同组独立消费

Group Coordinator
  - 管理 Group 状态的 Broker
  - 由 hash(groupId) % __consumer_offsets partition 数 决定

Group Leader
  - Group 内第一个加入的 Consumer
  - 负责计算 Partition 分配方案

Partition Assignment
  - Group Leader 决定的 Partition 分配
  - 同步给所有 Consumer

Member ID
  - Group 内 Consumer 唯一标识
  - 由 Consumer ID + UUID 组成
```

## 🔄 Group 加入流程

```
1. Consumer 启动，向 GroupCoordinator 发送 JoinGroup 请求
   ↓
2. Coordinator 等待所有 Consumer 加入
   ├─ 等到 session.timeout.ms 或所有 Consumer 都加入
   ↓
3. Coordinator 选举 Group Leader（第一个加入的）
   ↓
4. Group Leader 收到所有 Consumer 信息
   ↓
5. Group Leader 调用 Partition Assignor 计算分配方案
   ↓
6. Group Leader 发送分配方案到 Coordinator
   ↓
7. Coordinator 通过 SyncGroup 同步给所有 Consumer
   ↓
8. 所有 Consumer 开始拉取分配到的 Partition
   ↓
9. 正常消费阶段
```

### 简化时序图

```
C1           C2           Coordinator
 |             |                |
 |--JoinGroup->|------>Coordinator|
 |             |<----JoinGroup----|
 |<-----------SyncGroup--------->|
 |             |        (assignment)
 |<--SyncGroup--|<--SyncGroup-----|
 |             |                |
  开始拉取      开始拉取
  P0, P1, P2   (no assignment)
```

## 🔄 Rebalance（再平衡）

### 触发场景

```
1. Consumer 加入（启动新实例）
2. Consumer 离开（崩溃或主动关闭）
3. 订阅的 Topic 变更
4. Group 内 Consumer 数量变化
5. 心跳超时（session.timeout.ms）
```

### Rebalance 过程

```
1. Coordinator 检测到 Group 状态变化
   ↓
2. 标记 Group 进入 PreparingRebalance 状态
   ↓
3. 所有 Consumer 暂停消费（保留 Offset）
   ↓
4. 触发 Rebalance
   ├─ Group 内所有 Consumer 重新加入（JoinGroup）
   ├─ 选举新 Leader
   ├─ 计算新分配方案
   └─ 同步给所有 Consumer
   ↓
5. Group 进入 CompletingRebalance 状态
   ↓
6. Consumer 恢复消费（从新的 Partition 分配）
```

### Rebalance 时延

```
正常 Rebalance：5-10 秒
原因：
  - 等待 session.timeout.ms（10s）
  - JoinGroup + SyncGroup RPC
  - 暂停消费

影响：
  ⚠️ Rebalance 期间 Consumer 暂停消费
  ⚠️ 频繁 Rebalance 会降低吞吐
```

### Rebalance 性能问题

```
旧版 Eager Rebalance：
  1. 撤销所有 Consumer 的 Partition 分配
  2. 所有 Consumer 暂停消费
  3. 重新加入
  4. 重新分配
  5. 恢复消费
  → Stop-The-World（STW）效果

新版 Cooperative Rebalance（Kafka 2.4+）：
  1. 仅撤销需要重新分配的 Partition
  2. 其他 Partition 继续消费
  3. 增量 Rebalance
  → 大幅减少 STW 时间
```

## 📊 Partition 分配策略

### 4 种分配策略对比

```
1. Range Assignor（默认）
   - 按 Topic 分配
   - 同 Topic 的 Partition 连续分配
   - 可能分配不均（特别是多个 Topic）

2. RoundRobin Assignor
   - 全局轮询
   - 分配最均匀

3. Sticky Assignor
   - 尽量保持原分配（最小变动）
   - 减少 Rebalance 时的重新分配

4. CooperativeSticky Assignor
   - 协作式增量 Rebalance
   - Kafka 2.4+ 推荐
```

### 配置分配策略

```java
// 默认 Range
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    RangeAssignor.class.getName());

// RoundRobin
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    RoundRobinAssignor.class.getName());

// Sticky（推荐）
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    StickyAssignor.class.getName());

// CooperativeSticky（Kafka 2.4+ 推荐）
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    CooperativeStickyAssignor.class.getName());

// 自定义分配策略（实现 PartitionAssignor 接口）
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    CustomAssignor.class.getName());
```

## 📊 Group 状态管理

### Group 状态

```
Empty           - 没有活跃 Consumer
Stable          - 正常运行
PreparingRebalance - 准备重新分配
CompletingRebalance - 完成重新分配
Dead            - Group 已删除
```

### 查看 Group 状态

```bash
# 查看 group 状态
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --state

# 输出：
# GROUP            COORDINATOR (ID)      STATE
# order-processor  1 (node1:9092)        Stable
```

## 🔧 健康监控

### 监控关键指标

```bash
# 1. Lag 监控（最关键）
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor

# 2. Lag 趋势（持续监控）
watch -n 5 "kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor"

# 3. Prometheus 监控（推荐）
# 部署 kafka_exporter 暴露 Prometheus 指标
# 关键指标：
# - kafka_consumergroup_lag
# - kafka_consumergroup_members
# - kafka_consumergroup_offset
```

### 健康检查清单

```markdown
✅ 所有 Consumer 正常连接（心跳正常）
✅ 所有 Partition 已分配（无空 Partition）
✅ Lag 在可接受范围（< 10000 或业务 SLA）
✅ 没有频繁 Rebalance（< 1 次/小时）
✅ Offset 持续推进（不在某条消息卡住）
✅ 错误率低（< 0.1%）
```

## 🛠️ 实战：优化 Group 性能

### 1. 减少 Rebalance 频率

```properties
# 调高心跳和会话超时（减少误判）
heartbeat.interval.ms=10000     # 默认 3s，调到 10s
session.timeout.ms=30000        # 默认 10s，调到 30s
# session.timeout 必须 > heartbeat.interval * 2

# 注意：
# - 增加超时 → 故障检测变慢
# - 减少超时 → 易误判导致 Rebalance
```

### 2. 使用 CooperativeSticky 策略

```java
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    CooperativeStickyAssignor.class.getName());
```

### 3. 增加 Partition 数

```bash
# 适度增加 partition（增加并行度）
kafka-topics.sh --alter \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 12

# 注意：Consumer 数量不应超过 Partition 数
```

### 4. JVM 优化

```properties
# Kafka Broker JVM
KAFKA_HEAP_OPTS="-Xmx6G -Xms6G"
KAFKA_JVM_PERFORMANCE_OPTS="-server -XX:+UseG1GC -XX:MaxGCPauseMillis=20"
```

## 🔧 Group 操作命令

```bash
# 列出所有 group
kafka-consumer-groups.sh --list --bootstrap-server localhost:9092

# 查看 group 详情
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor

# 查看 group 成员
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --members

# 重置 offset
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-earliest \
    --execute

# 删除 group
kafka-consumer-groups.sh --delete \
    --bootstrap-server localhost:9092 \
    --group old-group
```

## ⚠️ 常见问题

### 问题 1：Group 频繁 Rebalance

```
原因：
  1. 网络不稳定（心跳丢失）
  2. GC 停顿（heartbeat.interval.ms 内未发送心跳）
  3. Consumer 处理逻辑卡死（max.poll.interval.ms 触发）

解决：
  1. 增加 heartbeat.interval.ms 和 session.timeout.ms
  2. 优化 GC（G1GC / ZGC）
  3. 处理逻辑异步化
  4. 增加 max.poll.interval.ms
```

### 问题 2：Lag 一直增长

```
原因：
  1. Consumer 处理慢
  2. Consumer 数量不够

解决：
  1. 扩容 Consumer 实例
  2. 增加 Partition 数
  3. 优化消费逻辑
  4. 检查 Consumer 健康状态
```

### 问题 3：Consumer 一直 Empty

```
原因：
  1. 没有任何 Consumer 在 Group 中
  2. 所有 Consumer 都崩溃了

解决：
  1. 启动 Consumer
  2. 检查 Consumer 日志
  3. 检查 Group 是否已删除
```

## 🎯 总结

**消费者组核心要点**：
- ✅ 同组内点对点（负载均衡）
- ✅ 不同组发布订阅（广播）
- ✅ Rebalance 重新分配 Partition
- ✅ CooperativeSticky 减少 STW
- ✅ GroupCoordinator 管理 Group 状态
- ⚠️ Rebalance 期间暂停消费
- ⚠️ 频繁 Rebalance 影响性能

**下一步：** [📍 偏移量提交](/05-consumer/offset) — Offset 管理机制详解
