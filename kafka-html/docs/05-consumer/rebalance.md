---
title: 再平衡
---

# 🔄 再平衡

> **Rebalance（再平衡）**是 Consumer Group 中 Partition 重新分配的过程。理解 Rebalance 对高可用系统至关重要。

## 🎯 什么是 Rebalance？

```
Rebalance = Consumer Group 中 Partition 重新分配

目的：
  ✅ 负载均衡（Group 内 Consumer 数量变化时重新分配）
  ✅ 故障恢复（Consumer 崩溃后重新分配其 Partition）
  ✅ 弹性伸缩（添加/移除 Consumer）

代价：
  ⚠️ Rebalance 期间 Consumer 暂停消费
  ⚠️ 频繁 Rebalance 降低吞吐
```

## 📊 Rebalance 触发场景

```
1. Consumer 加入
   - 启动新实例
   - Group 规模从 N 变成 N+1

2. Consumer 离开
   - 主动调用 close()
   - 进程崩溃
   - 心跳超时

3. 订阅变更
   - subscribe() 增加/减少 Topic
   - Pattern 订阅的 Topic 数量变化

4. Partition 变更
   - 增加 Partition
   - 删除 Partition

5. 心跳超时
   - session.timeout.ms 内未收到心跳
```

## 🔄 Rebalance 流程

### Eager Rebalance（默认）

```
1. Coordinator 检测到 Group 状态变化
   ↓
2. 标记 Group 进入 PreparingRebalance 状态
   ↓
3. 所有 Consumer 撤销所有 Partition 分配
   ↓
4. 所有 Consumer 重新加入 Group（JoinGroup）
   ↓
5. 选举 Group Leader
   ↓
6. Group Leader 计算新的 Partition 分配
   ↓
7. 同步给所有 Consumer（SyncGroup）
   ↓
8. Group 进入 Stable 状态
   ↓
9. Consumer 恢复消费
```

**问题：Stop-The-World（STW）**

```
所有 Consumer 必须撤销所有 Partition 才能继续
  → 整个 Group 暂停消费
  → 大量 Partition 重新分配开销
  → 频繁 Rebalance 时影响显著
```

### Cooperative Incremental Rebalance（Kafka 2.4+ 推荐）

```
1. Coordinator 检测到需要重新分配的 Partition
   ↓
2. 仅撤销需要重新分配的 Partition
   ↓
3. 其他 Partition 继续消费（不受影响）
   ↓
4. 重新分配这些 Partition
   ↓
5. Consumer 继续处理其他 Partition
   ↓
6. 增量完成 Rebalance
```

**优势**：
- ✅ 减少 STW 时间（从 10 秒降到 1 秒）
- ✅ 减少 Partition 重新分配
- ✅ 适合大规模 Consumer Group

### 配置 Cooperative Rebalance

```java
// Kafka 2.4+ 推荐
Properties props = new Properties();
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    CooperativeStickyAssignor.class.getName());

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));
```

## 📊 Partition 分配策略详解

### Range Assignor（默认）

```
原理：按 Topic 分配，每个 Topic 内的 Partition 连续分配给 Consumer

示例：
  Topic: orders（4 个 Partition）, Topic: payments（3 个 Partition）
  Consumer Group: 2 个 Consumer（C1, C2）

  orders:
    C1 → P0, P1
    C2 → P2, P3
  
  payments:
    C1 → P0
    C2 → P1, P2

问题：分配不均（C2 多了一个）
```

### RoundRobin Assignor

```
原理：全局轮询所有 Partition

示例：
  所有 Partition: orders-P0, orders-P1, orders-P2, orders-P3, payments-P0, payments-P1, payments-P2
  C1: orders-P0, orders-P2, payments-P1
  C2: orders-P1, orders-P3, payments-P0, payments-P2

优点：分配最均匀
缺点：Rebalance 时所有 Partition 都重新分配（STW）
```

### Sticky Assignor

```
原理：尽量保持原分配，最小化变动

示例：
  Rebalance 前：
    C1 → P0, P1, P2
    C2 → P3, P4
  
  增加 C3 后：
    C1 → P0, P1
    C2 → P3
    C3 → P2, P4  ← 只有 C2 的 P3 和 C1 的 P2 重新分配
```

**优势**：
- ✅ 减少 Rebalance 影响
- ✅ 增量分配
- ⚠️ 仍需 STW（Eager 模式）

### CooperativeSticky Assignor（Kafka 2.4+）

```
原理：Sticky + 增量 Rebalance

示例：
  Rebalance 前：
    C1 → P0, P1, P2
    C2 → P3, P4
  
  增加 C3 后：
    阶段 1：C2 撤销 P3
    阶段 2：C3 加入，获取 P3 + P4
    阶段 3：C1 撤销 P2（让给 C3）
    阶段 4：C3 获取 P2
```

**优势**：
- ✅ Sticky 优点 + 无 STW
- ✅ Kafka 2.4+ 生产推荐

## 🔧 Rebalance 监听器

### ConsumerRebalanceListener

```java
consumer.subscribe(Arrays.asList("orders"), new ConsumerRebalanceListener() {
    
    // Partition 撤销时调用
    @Override
    public void onPartitionsRevoked(Collection<TopicPartition> partitions) {
        log.info("Partitions revoked: {}", partitions);
        
        // 在这里提交 Offset
        consumer.commitSync(currentOffsets);
    }
    
    // Partition 分配时调用
    @Override
    public void onPartitionsAssigned(Collection<TopicPartition> partitions) {
        log.info("Partitions assigned: {}", partitions);
        
        // 自定义 Offset 起点
        consumer.seekToBeginning(partitions);
        // 或 seek(tp, offset)
    }
});
```

### 实战：处理 Rebalance 时的资源清理

```java
public class RebalanceAwareConsumer {
    
    public void consume() {
        Properties props = new Properties();
        // ... 配置 ...
        
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
        Map<TopicPartition, OffsetAndMetadata> offsetsToCommit = new HashMap<>();
        
        consumer.subscribe(Arrays.asList("orders"), new ConsumerRebalanceListener() {
            
            @Override
            public void onPartitionsRevoked(Collection<TopicPartition> partitions) {
                log.info("Rebalance: Partitions revoked: {}", partitions);
                
                // 提交 Offset（必须！）
                try {
                    consumer.commitSync(offsetsToCommit);
                    log.info("Committed offsets before rebalance: {}", offsetsToCommit);
                } catch (CommitFailedException e) {
                    log.warn("Commit failed during rebalance", e);
                }
                
                // 清理资源（如数据库连接）
                cleanupResources();
            }
            
            @Override
            public void onPartitionsAssigned(Collection<TopicPartition> partitions) {
                log.info("Rebalance: Partitions assigned: {}", partitions);
                
                // 初始化资源
                initializeResources(partitions);
                
                // 自定义 Offset 起点
                consumer.seekToBeginning(partitions);
            }
        });
        
        // 正常消费循环
        while (running) {
            ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
            
            for (ConsumerRecord<String, String> record : records) {
                processOrder(record);
                offsetsToCommit.put(
                    new TopicPartition(record.topic(), record.partition()),
                    new OffsetAndMetadata(record.offset() + 1)
                );
            }
            
            // 异步提交
            consumer.commitAsync(offsetsToCommit, null);
        }
    }
}
```

## 🔧 减少 Rebalance 频率

### 1. 调高超时

```properties
# 默认值
heartbeat.interval.ms=3000      # 3 秒
session.timeout.ms=10000        # 10 秒

# 调优后
heartbeat.interval.ms=10000     # 10 秒
session.timeout.ms=30000        # 30 秒
# session.timeout 必须 > heartbeat.interval * 2
```

### 2. JVM 优化（避免 GC 停顿导致心跳丢失）

```bash
KAFKA_HEAP_OPTS="-Xmx4G -Xms4G"
KAFKA_JVM_PERFORMANCE_OPTS="-server -XX:+UseG1GC -XX:MaxGCPauseMillis=20"
```

### 3. 使用 CooperativeSticky 策略

```java
props.put(ConsumerConfig.PARTITION_ASSIGNMENT_STRATEGY_CONFIG,
    CooperativeStickyAssignor.class.getName());
```

### 4. 静态成员（Kafka 2.3+）

```properties
# 静态成员：减少不必要的 Rebalance（Pod 滚动升级时）
group.instance.id=consumer-1
```

**传统 Rebalance**：
- Pod 重启 → 加入 Group → 触发 Rebalance
- 短暂不可用

**静态成员**：
- Pod 重启时，Group Coordinator 等待 `session.timeout.ms`
- 如果 Pod 在超时前回来，避免 Rebalance

```java
// 配置静态成员 ID
props.put(ConsumerConfig.GROUP_INSTANCE_ID_CONFIG, "consumer-pod-1");
```

## 🔧 实战：平滑的滚动升级

### 滚动升级场景

```
应用滚动升级步骤：
  1. 启动新 Consumer 实例
  2. 加入 Group
  3. Rebalance（重新分配）
  4. 新 Consumer 开始消费
  5. 旧 Consumer 离开
  6. 再次 Rebalance
  → 多次 Rebalance，影响可用性
```

### 优化：静态成员 + 长会话超时

```yaml
# application.yml
spring:
  kafka:
    consumer:
      group-id: order-processor
      properties:
        # 静态成员 ID（避免滚动升级时的 Rebalance）
        group.instance.id: ${HOSTNAME}
        # 长会话超时
        session.timeout.ms: 60000
        heartbeat.interval.ms: 10000
      partition-assignment-strategy: 
        org.apache.kafka.clients.consumer.CooperativeStickyAssignor
```

### 灰度发布策略

```
1. 同时运行新旧版本 Consumer
2. 逐步把流量切到新版本（按 Partition）
3. 旧版本处理完后下线
4. 整个过程无 Rebalance
```

## 📊 Rebalance 监控

### 关键指标

```java
// Consumer JMX 指标
double rebalanceRatePerHour;        // 每小时 Rebalance 次数
long rebalanceTimeMsAvg;            // Rebalance 平均耗时
long assignmentSize;                 // 当前分配的 Partition 数
long lastRebalanceTimestampMs;       // 上次 Rebalance 时间
```

### 告警规则

```
🚨 Rebalance 频率过高
  - 每小时 Rebalance > 5 次 → 告警
  - Rebalance 耗时 > 30 秒 → 告警

🚨 Consumer 数量异常
  - 活跃 Consumer < 期望数量 → 告警
  - 活跃 Consumer 突然变化 → 告警

🚨 Partition 分配异常
  - 有 Partition 未分配 → 告警
  - Consumer 分配不均 → 告警
```

## ⚠️ 常见问题

### 问题 1：频繁 Rebalance 导致消费慢

```
现象：每分钟 Rebalance 多次
原因：
  1. session.timeout.ms 设置过小
  2. 网络不稳定
  3. GC 停顿
解决：
  1. 增加 session.timeout.ms
  2. 优化 GC
  3. 检查网络
```

### 问题 2：Rebalance 耗时过长

```
现象：Rebalance 持续 30 秒+
原因：
  1. Consumer 数量过多
  2. 分配算法慢
  3. 网络慢
解决：
  1. 使用 CooperativeSticky（增量 Rebalance）
  2. 减少 Consumer 数量
  3. 检查网络
```

### 问题 3：Rebalance 后消费丢消息

```
原因：未在 Rebalance 时提交 Offset
解决：
  1. 在 onPartitionsRevoked 中 commitSync
  2. 或启用事务 + read_committed
```

## 🎯 总结

**再平衡核心要点**：
- ✅ Rebalance 重新分配 Partition
- ✅ Eager Rebalance（STW）+ Cooperative Rebalance（增量）
- ✅ CooperativeSticky 是 Kafka 2.4+ 推荐
- ✅ ConsumerRebalanceListener 处理 Rebalance 事件
- ✅ 静态成员减少滚动升级 Rebalance
- ⚠️ Rebalance 期间暂停消费
- ⚠️ 频繁 Rebalance 影响可用性

**下一步：** [✋ 手动提交](/05-consumer/manual-commit) — Offset 提交策略详解


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
