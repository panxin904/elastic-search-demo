---
title: Leader 选举
date: 2026-08-15  # date-auto-injected
---

# 👑 Leader 选举

> 当某个 Partition 的 Leader 故障时，Kafka 自动从 ISR 中选举新 Leader，**秒级故障转移**。

## 🎯 Leader 选举触发场景

```
1. Broker 宕机
   - 主机断电、进程崩溃、OOM
   - 该 Broker 上的 Leader Partition 需要重新选举

2. 网络分区
   - Leader 失联（其他 Broker 无法访问）
   - Controller 触发新 Leader 选举

3. 主动下线
   - 运维重启 Broker
   - 该 Broker 上的 Leader 转移

4. ISR 收缩
   - Follower 落后太久被踢出 ISR
   - 当只剩 1 个 ISR 时，重启可能触发选举
```

## 🔄 选举流程

### Controller 主导选举

```
1. Controller 监测到 Leader 失联
   ↓
2. 从 ISR 列表中选出新 Leader
   ↓
3. 更新元数据（__cluster_metadata）
   ↓
4. 通过 MetadataResponse 通知所有 Brokers
   ↓
5. Producers/Consumers 收到通知，自动重连
   ↓
6. 新 Leader 开始处理读写请求
```

### ISR 选择规则

```
选举优先级（从高到低）：
  1. ISR 列表中的第一个副本（Preferred Replica）
  2. ISR 中的其他副本
  3. 如果 unclean.leader.election.enable=true，选 AR 中其他副本

⚠️ 选举期间：
  - 该 Partition 短暂不可用（毫秒级）
  - Producers 自动重试
  - Consumers 自动重连
```

## 📊 选举时序

```
时间线（毫秒）：
  T0   旧 Leader 宕机
  T1   Controller 心跳超时（默认 10000ms）
       实际发现时间 = session.timeout.ms / 2 = 5s
  T2   Controller 触发选举
  T3   选出新 Leader（< 1s）
  T4   更新元数据（< 1s）
  T5   通知 Brokers（< 1s）
  T6   客户端感知新 Leader（< 1s）

总耗时：通常 5-15 秒
```

## 🎯 Preferred Replica（优先副本）

### 什么是 Preferred Replica

```
Preferred Replica = AR 中的第一个副本（通常是第一个被创建的副本）

设计目标：
  - 默认情况下，Preferred Replica 是 Leader
  - 平衡集群负载，避免某些 Broker 过载

触发选举 Preferred Replica：
  - Broker 上线后
  - 手动调用 preferred-replica-election
```

### 手动选举

```bash
# 触发所有 Topic 的 Preferred Replica 选举
bin/kafka-preferred-replica-election.sh \
    --bootstrap-server localhost:9092

# 触发指定 Topic 的选举
bin/kafka-preferred-replica-election.sh \
    --bootstrap-server localhost:9092 \
    --path-to-json-file preferred-replica.json
```

## 📊 unclean.leader.election 配置

### 两种选举策略对比

```
clean leader election（默认）：
  - 只能从 ISR 中选 Leader
  - 保证数据一致性（不会丢数据）
  - 可能导致分区不可用（如果所有 ISR 都挂了）

unclean leader election：
  - 可以从 OSR 中选 Leader
  - 即使所有 ISR 都挂了，集群仍可用
  - 可能丢失数据（OSR 落后 ISR）
```

### 配置

```properties
# server.properties
unclean.leader.election.enable=false  # 默认 false（推荐生产环境）
```

### 选型建议

```
✅ 金融、订单场景：unclean=false
   - 数据一致性优先，宁可不可用也不丢数据

✅ 日志、监控场景：unclean=true
   - 可用性优先，可以容忍少量数据丢失

⚠️ 默认 false（推荐）
   - 多数场景关闭即可
```

## 🔧 选举相关配置

```properties
# ==== Controller 选举相关 ====
controller.election.timeout.ms=30000      # Controller 选举超时（KRaft）
default.replication.factor=3             # 默认副本数
min.insync.replicas=2                     # 最小同步副本数
unclean.leader.election.enable=false      # 是否允许 unclean 选举

# ==== Follower 超时 ====
replica.lag.time.max.ms=30000             # Follower 超时（影响 ISR）
replica.fetch.min.bytes=1                 # 拉取最小字节
replica.fetch.max.bytes=1048576           # 拉取最大字节

# ==== 选举后清理 ====
auto.leader.rebalance.enable=true        # 自动重新选举 Preferred Replica
leader.imbalance.per.broker.percentage=10 # 触发重新选举的不平衡阈值
```

## 📊 Leader 选举与数据一致性

### 场景 1：clean election（推荐）

```
旧 Leader: Broker 1
ISR: [Broker 1, Broker 2, Broker 3]

T0  Broker 1 宕机
T1  Controller 选举：从 ISR 选 Broker 2
T2  Broker 2 成为新 Leader
T3  数据完整性：Broker 2 有完整数据（之前是 ISR）
T4  Producer 继续发送（acks=all 已等到 ISR 同步）
T5  Consumer 继续消费（数据连续，无丢失）
```

### 场景 2：unclean election（数据可能丢失）

```
旧 Leader: Broker 1 (HW=100)
ISR: [Broker 1]
OSR: [Broker 2 (LEO=80), Broker 3 (LEO=70)]

T0  Broker 1 宕机（且不可恢复）
T1  Controller 检测 ISR 已全部挂掉
T2  unclean election 启用：从 OSR 选 Broker 2（LEO=80）当 Leader
T3  数据丢失：offset 80~100 的数据丢失
T4  Producer 继续发送（从 offset=80 开始）
T5  Consumer 看到 offset 不连续（有消息丢失）
```

## 🛠️ 实战：观察 Leader 选举

```bash
# 1. 查看当前 Leader 分布
bin/kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic orders

# 输出：
# Topic: orders   PartitionCount: 3   ReplicationFactor: 2
#   Partition: 0   Leader: 1   Replicas: 1,2   Isr: 1,2
#   Partition: 1   Leader: 2   Replicas: 2,3   Isr: 2,3
#   Partition: 2   Leader: 3   Replicas: 3,1   Isr: 3,1

# 2. 关闭 Broker 1（kill -9 PID）
# 3. 等待 10 秒，观察选举结果
bin/kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic orders

# 输出：
#   Partition: 0   Leader: 2   Replicas: 1,2   Isr: 2  ← 新 Leader
#   Partition: 2   Leader: 3   Replicas: 3,1   Isr: 3  ← 新 Leader

# 4. 重启 Broker 1
# 5. 等待 30 秒，Broker 1 重新加入 ISR
bin/kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic orders
# 输出：Isr 中重新出现 Broker 1
```

## ⚠️ 选举常见问题

### 问题 1：选举频繁（脑裂风险）

```
现象：Leader 反复切换
原因：
  1. Broker 网络不稳定
  2. GC 停顿导致心跳超时
  3. 磁盘 IO 阻塞
解决：
  1. 调整 session.timeout.ms / heartbeat.interval.ms
  2. 优化 JVM 参数（避免长 GC）
  3. 检查磁盘性能
```

### 问题 2：分区不可用时间过长

```
现象：故障后 30 秒以上才恢复
原因：
  1. unclean.leader.election=false 且所有 ISR 都挂
  2. Controller 选举慢
解决：
  1. 增加 ISR 副本数（min.insync.replicas）
  2. 检查 Controller 集群健康
```

### 问题 3：Preferred Replica 不平衡

```
现象：某些 Broker 是大量 Partition 的 Leader，其他 Broker 是 Follower
原因：
  1. 选举失败后没有自动重新平衡
  2. 某些 Broker 频繁故障
解决：
  1. 启用 auto.leader.rebalance.enable=true
  2. 定期手动触发 preferred-replica-election
```

## 🎯 总结

**Leader 选举核心要点**：
- ✅ Controller 主导选举，从 ISR 中选新 Leader
- ✅ 选举耗时通常 5-15 秒
- ✅ Preferred Replica 平衡负载
- ✅ clean election 保证一致性，unclean election 牺牲一致性换可用性
- ⚠️ unclean.leader.election 谨慎开启
- ⚠️ Leader 选举期间分区短暂不可用

**下一步：** [📜 日志存储](/02-architecture/log-storage) — 磁盘 IO 优化


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
