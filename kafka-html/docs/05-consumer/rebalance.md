---
title: 再平衡
date: 2026-08-15  # date-auto-injected
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

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Kafka Consumer Rebalance 完整流程</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">5 阶段协议 · Eager / Cooperative（增量）两代协议对比</text>

  <!-- 时间线 -->
  <line x1="50" y1="280" x2="550" y2="280" stroke="#64748b" stroke-width="1.5"/>
  <circle cx="100" cy="280" r="6" fill="#dc2626"/>
  <circle cx="200" cy="280" r="6" fill="#f59e0b"/>
  <circle cx="300" cy="280" r="6" fill="#3b82f6"/>
  <circle cx="400" cy="280" r="6" fill="#10b981"/>
  <circle cx="500" cy="280" r="6" fill="#8b5cf6"/>

  <!-- 阶段卡片 -->
  <rect class="at-hover-card" x="60" y="100" width="100" height="50" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
  <text x="110" y="123" text-anchor="middle" font-size="11" font-weight="700" fill="#991b1b">① 触发</text>
  <text x="110" y="140" text-anchor="middle" font-size="9" fill="#475569">成员变更</text>

  <rect class="at-hover-card" x="160" y="100" width="100" height="50" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="210" y="123" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">② 加入组</text>
  <text x="210" y="140" text-anchor="middle" font-size="9" fill="#475569">JoinGroup</text>

  <rect class="at-hover-card" x="260" y="100" width="100" height="50" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="310" y="123" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">③ 同步</text>
  <text x="310" y="140" text-anchor="middle" font-size="9" fill="#475569">SyncGroup</text>

  <rect class="at-hover-card" x="360" y="100" width="100" height="50" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="410" y="123" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">④ 分配</text>
  <text x="410" y="140" text-anchor="middle" font-size="9" fill="#475569">Leader 计算</text>

  <rect class="at-hover-card" x="460" y="100" width="100" height="50" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="510" y="123" text-anchor="middle" font-size="11" font-weight="700" fill="#5b21b6">⑤ 稳定</text>
  <text x="510" y="140" text-anchor="middle" font-size="9" fill="#475569">消费恢复</text>

  <line x1="160" y1="125" x2="160" y2="125" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="160" y1="125" x2="260" y2="125" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="260" y1="125" x2="360" y2="125" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="360" y1="125" x2="460" y2="125" stroke="#64748b" stroke-width="1.5" marker-end="url(#arr)"/>

  <!-- 角色 -->
  <rect x="40" y="170" width="170" height="80" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="125" y="193" text-anchor="middle" font-size="11" font-weight="700" fill="#1e293b">GroupCoordinator</text>
  <text x="50" y="213" font-size="9" fill="#475569">· 选 broker 之一（__consumer_offsets）</text>
  <text x="50" y="228" font-size="9" fill="#475569">· 维护组成员关系</text>
  <text x="50" y="243" font-size="9" fill="#475569">· 驱动协议 5 阶段</text>

  <rect x="220" y="170" width="170" height="80" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="305" y="193" text-anchor="middle" font-size="11" font-weight="700" fill="#1e293b">Group Leader</text>
  <text x="230" y="213" font-size="9" fill="#475569">· 第一个加入者（默认）</text>
  <text x="230" y="228" font-size="9" fill="#475569">· 收集 member metadata</text>
  <text x="230" y="243" font-size="9" fill="#475569">· 运行分配策略（range/round）</text>

  <rect x="400" y="170" width="170" height="80" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="485" y="193" text-anchor="middle" font-size="11" font-weight="700" fill="#1e293b">Members</text>
  <text x="410" y="213" font-size="9" fill="#475569">· 发送 join/sync 请求</text>
  <text x="410" y="228" font-size="9" fill="#475569">· 接收分配结果</text>
  <text x="410" y="243" font-size="9" fill="#475569">· commit offset 到 __consumer_offsets</text>

  <!-- 两代协议对比 -->
  <rect x="30" y="310" width="260" height="155" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="160" y="335" text-anchor="middle" font-size="13" font-weight="700" fill="#92400e">Eager 协议（Stop-The-World）</text>
  <text x="50" y="360" font-size="10" font-weight="700" fill="#1e293b">机制</text>
  <text x="50" y="378" font-size="10" fill="#475569">所有 member 撤销当前 partition</text>
  <text x="50" y="395" font-size="10" fill="#475569">→ 全组重新分配</text>
  <text x="50" y="415" font-size="10" font-weight="700" fill="#dc2626">缺点</text>
  <text x="50" y="433" font-size="10" fill="#475569">· 整个 group 停消费（秒级停顿）</text>
  <text x="50" y="450" font-size="10" fill="#475569">· 高频成员变更时延迟放大</text>

  <rect x="310" y="310" width="260" height="155" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="440" y="335" text-anchor="middle" font-size="13" font-weight="700" fill="#047857">Cooperative 协议（增量）</text>
  <text x="330" y="360" font-size="10" font-weight="700" fill="#1e293b">机制</text>
  <text x="330" y="378" font-size="10" fill="#475569">只撤销需要迁移的 partition</text>
  <text x="330" y="395" font-size="10" fill="#475569">→ 其他 partition 继续消费</text>
  <text x="330" y="415" font-size="10" font-weight="700" fill="#10b981">优点</text>
  <text x="330" y="433" font-size="10" fill="#475569">· 增量迁移，停顿时长显著降低</text>
  <text x="330" y="450" font-size="10" fill="#475569">· Kafka 2.4+ 默认 · KIP-429</text>
</svg>

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

<!-- svg-injected:do-not-edit -->

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Kafka Consumer Group Rebalance</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">Range / RoundRobin / Sticky · Group Coordinator</text>

  <!-- 4 阶段 -->
  <g font-size="11" font-weight="600">
    <rect class="at-hover-card" x="40" y="100" width="125" height="45" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="102" y="120" text-anchor="middle" font-weight="700" fill="#1e3a8a">1. 触发</text>
    <text x="102" y="135" text-anchor="middle" fill="#1e40af">成员变更 / 订阅变更</text>

    <rect class="at-hover-card" x="180" y="100" width="125" height="45" rx="6" fill="#d1fae5" stroke="#10b981" stroke-width="1.5"/>
    <text x="242" y="120" text-anchor="middle" font-weight="700" fill="#064e3b">2. 同步组</text>
    <text x="242" y="135" text-anchor="middle" fill="#065f46">JoinGroup 协议</text>

    <rect class="at-hover-card" x="320" y="100" width="125" height="45" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="382" y="120" text-anchor="middle" font-weight="700" fill="#92400e">3. 分配方案</text>
    <text x="382" y="135" text-anchor="middle" fill="#78350f">分区再分配</text>

    <rect class="at-hover-card" x="460" y="100" width="100" height="45" rx="6" fill="#fce7f3" stroke="#ec4899" stroke-width="1.5"/>
    <text x="510" y="120" text-anchor="middle" font-weight="700" fill="#9f1239">4. 同步</text>
    <text x="510" y="135" text-anchor="middle" fill="#9d174d">SyncGroup</text>
  </g>

  <!-- 箭头 -->
  <g stroke="#64748b" stroke-width="2" fill="none" marker-end="url(#arrow)">
    <line x1="165" y1="122" x2="180" y2="122"/>
    <line x1="305" y1="122" x2="320" y2="122"/>
    <line x1="445" y1="122" x2="460" y2="122"/>
  </g>

  <!-- 分区分配对比 -->
  <g font-size="11" font-weight="600">
    <text x="40" y="180" fill="#1e293b">3 种分配策略对比：</text>

    <rect class="at-hover-card" x="40" y="190" width="160" height="65" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1"/>
    <text x="120" y="210" text-anchor="middle" font-weight="700" fill="#92400e">Range（默认）</text>
    <text x="120" y="228" text-anchor="middle" fill="#78350f">按 topic 分段</text>
    <text x="120" y="245" text-anchor="middle" fill="#78350f">前 N 个 consumer 多分 1 个</text>

    <rect class="at-hover-card" x="220" y="190" width="160" height="65" rx="6" fill="#d1fae5" stroke="#10b981" stroke-width="1"/>
    <text x="300" y="210" text-anchor="middle" font-weight="700" fill="#064e3b">RoundRobin</text>
    <text x="300" y="228" text-anchor="middle" fill="#065f46">全 topic 全 partition</text>
    <text x="300" y="245" text-anchor="middle" fill="#065f46">轮询分配 · 最均匀</text>

    <rect class="at-hover-card" x="400" y="190" width="160" height="65" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1"/>
    <text x="480" y="210" text-anchor="middle" font-weight="700" fill="#1e3a8a">Sticky（Kafka）</text>
    <text x="480" y="228" text-anchor="middle" fill="#1e40af">保留原分配</text>
    <text x="480" y="245" text-anchor="middle" fill="#1e40af">最小化分区迁移</text>
  </g>

  <!-- Stop-the-world 警告 -->
  <g font-size="12">
    <rect class="at-hover-card" x="40" y="280" width="520" height="70" rx="8" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
    <text x="60" y="302" font-weight="700" fill="#7f1d1d">⚠ Rebalance 期间消费暂停（Eager 协议）</text>
    <text x="60" y="322" fill="#991b1b">所有 consumer 停止拉取 → 重新加入 → 重新分配 → 恢复</text>
    <text x="60" y="340" fill="#991b1b">耗时与 partition 数 / consumer 数相关，大集群可能分钟级</text>
  </g>

  <!-- 优化建议 -->
  <g font-size="11">
    <rect class="at-hover-card" x="50" y="370" width="500" height="80" rx="8" fill="#f1f5f9" stroke="#64748b" stroke-width="1"/>
    <text x="300" y="390" text-anchor="middle" font-weight="700" fill="#1e293b">优化方向</text>
    <text x="60" y="410" fill="#475569">✓ partition.assignors = [CooperativeSticky]</text>
    <text x="320" y="410" fill="#475569">✓ 增量协作（只迁移受影响）</text>
    <text x="60" y="428" fill="#475569">✓ session.timeout.ms 调长（避免心跳抖动）</text>
    <text x="320" y="428" fill="#475569">✓ max.poll.interval.ms 调长</text>
    <text x="60" y="445" fill="#475569">✓ 静态成员（KIP-345）· 重连不重平衡</text>
    <text x="320" y="445" fill="#475569">✓ 单 partition 多 consumer 需谨慎</text>
  </g>
</svg>
<!-- svg-injected:do-not-edit -->

## 图示：Kafka Consumer Rebalance 时序（JoinGroup→SyncGroup）

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Kafka 消费者 Rebalance 协议</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">Eager / Cooperative / Range / RoundRobin · 触发条件</text>

  <!-- 触发条件 -->
  <g>
    <text x="60" y="90" font-size="13" font-weight="700" fill="#1e293b">① 触发 Rebalance 的 4 类事件</text>

    <rect class="at-hover-card" x="40" y="105" width="520" height="100" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <rect class="at-hover-card" x="55" y="120" width="115" height="70" rx="4" fill="#fee2e2" stroke="#dc2626"/>
    <text x="112" y="138" text-anchor="middle" font-size="10" font-weight="700" fill="#991b1b">新消费者</text>
    <text x="112" y="156" text-anchor="middle" font-size="9" fill="#475569">加入 group</text>
    <text x="112" y="172" text-anchor="middle" font-size="9" fill="#475569">加入分区</text>
    <text x="112" y="186" text-anchor="middle" font-size="8" fill="#475569">数量变化</text>

    <rect class="at-hover-card" x="180" y="120" width="115" height="70" rx="4" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="237" y="138" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">消费者离开</text>
    <text x="237" y="156" text-anchor="middle" font-size="9" fill="#475569">crash / close</text>
    <text x="237" y="172" text-anchor="middle" font-size="9" fill="#475569">数量变化</text>

    <rect class="at-hover-card" x="305" y="120" width="115" height="70" rx="4" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="362" y="138" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">分区数变化</text>
    <text x="362" y="156" text-anchor="middle" font-size="9" fill="#475569">topic 扩分区</text>
    <text x="362" y="172" text-anchor="middle" font-size="9" fill="#475569">订阅变化</text>

    <rect class="at-hover-card" x="430" y="120" width="120" height="70" rx="4" fill="#dcfce7" stroke="#10b981"/>
    <text x="490" y="138" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">心跳超时</text>
    <text x="490" y="156" text-anchor="middle" font-size="9" fill="#475569">session.timeout.ms</text>
    <text x="490" y="172" text-anchor="middle" font-size="9" fill="#475569">默认 10s</text>
    <text x="490" y="186" text-anchor="middle" font-size="8" fill="#475569">Group Coordinator</text>
  </g>

  <!-- Eager vs Cooperative -->
  <g>
    <text x="60" y="225" font-size="13" font-weight="700" fill="#1e293b">② Eager (stop-the-world) vs Cooperative (增量)</text>

    <rect class="at-hover-card" x="40" y="240" width="250" height="125" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
    <text x="165" y="260" text-anchor="middle" font-size="12" font-weight="700" fill="#991b1b">Eager (RangeAssignor)</text>
    <text x="55" y="282" font-size="10" fill="#475569">• 所有 consumer 撤销所有分区</text>
    <text x="55" y="298" font-size="10" fill="#475569">• 全部停止拉取（STW）</text>
    <text x="55" y="314" font-size="10" fill="#475569">• 重新分配后再启动</text>
    <text x="55" y="332" font-size="10" font-weight="700" fill="#dc2626">⚠️ 长尾延迟（slowest）</text>
    <text x="55" y="350" font-size="9" font-family="monospace" fill="#1e293b">partition.assignment.strategy</text>
    <text x="55" y="362" font-size="9" font-family="monospace" fill="#1e293b">= range/roundrobin</text>

    <rect class="at-hover-card" x="310" y="240" width="250" height="125" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="435" y="260" text-anchor="middle" font-size="12" font-weight="700" fill="#065f46">Cooperative (增量)</text>
    <text x="325" y="282" font-size="10" fill="#475569">• 只迁移需要变动的分区</text>
    <text x="325" y="298" font-size="10" fill="#475569">• 其余 consumer 继续工作</text>
    <text x="325" y="314" font-size="10" fill="#475569">• 渐进式再平衡</text>
    <text x="325" y="332" font-size="10" font-weight="700" fill="#065f46">✅ 抖动小</text>
    <text x="325" y="350" font-size="9" font-family="monospace" fill="#1e293b">CooperativeSticky</text>
    <text x="325" y="362" font-size="9" font-family="monospace" fill="#1e293b">StickyAssignor</text>
  </g>

  <!-- 流程 -->
  <g>
    <text x="60" y="385" font-size="13" font-weight="700" fill="#1e293b">③ Rebalance 协议流程（4 步）</text>

    <rect class="at-hover-card" x="40" y="398" width="520" height="68" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <rect class="at-hover-card" x="55" y="412" width="110" height="42" rx="3" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="110" y="430" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">1. JOIN</text>
    <text x="110" y="445" text-anchor="middle" font-size="8" fill="#475569">发送 JoinGroup</text>

    <path d="M 165 433 L 195 433" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="195" y="412" width="110" height="42" rx="3" fill="#fef3c7" stroke="#f59e0b"/>
    <text x="250" y="430" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">2. SYNC</text>
    <text x="250" y="445" text-anchor="middle" font-size="8" fill="#475569">SyncGroup 同步</text>

    <path d="M 305 433 L 335 433" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="335" y="412" width="110" height="42" rx="3" fill="#dcfce7" stroke="#10b981"/>
    <text x="390" y="430" text-anchor="middle" font-size="10" font-weight="700" fill="#065f46">3. ASSIGN</text>
    <text x="390" y="445" text-anchor="middle" font-size="8" fill="#475569">分配分区</text>

    <path d="M 445 433 L 475 433" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="475" y="412" width="75" height="42" rx="3" fill="#fee2e2" stroke="#dc2626"/>
    <text x="512" y="430" text-anchor="middle" font-size="10" font-weight="700" fill="#991b1b">4. FETCH</text>
    <text x="512" y="445" text-anchor="middle" font-size="8" fill="#475569">重新消费</text>
  </g>
</svg>
