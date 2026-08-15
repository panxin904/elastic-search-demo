---
title: 高频面试题（下）
---

# 📝 高频面试题（下）

> 整理 Kafka **进阶**的 20 道高频面试题，涵盖**底层原理、性能调优、生产实战**。

## 🎯 底层原理

### 1. Kafka 的存储结构是怎样的？

```
Topic
├── Partition 0
│   ├── 00000000000000000000.log      ← Segment 1（默认 1GB）
│   ├── 00000000000000000000.index    ← 偏移量索引
│   ├── 00000000000000000000.timeindex ← 时间戳索引
│   ├── 0000000000001073741824.log    ← Segment 2
│   └── ...
├── Partition 1
│   └── ...
└── Partition 2

每个 Segment：
  - .log：消息内容（顺序追加）
  - .index：偏移量 → 物理位置（稀疏索引）
  - .timeindex：时间戳 → 偏移量
```

### 2. Kafka 的日志分段（Segment）策略？

```
触发滚动条件（满足任一）：
  - log.segment.bytes：默认 1GB
  - log.segment.ms：默认 7 天

滚动流程：
  1. 关闭当前 .log 文件
  2. 创建新 .log 文件（offset 起始）
  3. 旧 Segment 等待过期删除

优势：
  - 大文件变小，删除高效（直接删整个文件）
  - 索引小，加载快
  - 历史数据管理简单
```

### 3. Kafka 的索引机制？

```
稀疏索引（每 4KB 一个索引项）：

.index 文件：
  offset    physical_position
    0        0
    100      4096
    200      8192
    ...

查询流程（offset=150）：
  1. 加载 .index 到内存
  2. 二分查找找到 100（position=4096）
  3. 从 .log 文件的 4096 位置顺序扫描
  4. 找到 offset=150 的消息

时间戳索引（timeindex）：
  - 按时间查询消息（Kafka Streams 用）
```

### 4. Kafka 的副本同步机制？

```
Leader → Follower 拉取同步：

1. Leader 写入 log 文件
2. 更新 LEO（Log End Offset）
3. Follower 发送 FetchRequest(startOffset=LEO)
4. Leader 返回最新消息
5. Follower 写入本地 log
6. 更新 Follower LEO
7. Follower 更新 HW（High Watermark）
   - HW = min(所有 ISR 的 LEO)
8. Consumer 只能读到 HW 之前

⚠️ Follower 落后太久会被踢出 ISR
   - replica.lag.time.max.ms = 30s
```

### 5. Kafka 的 Controller 是什么？

```
Controller = Kafka 集群的大脑

职责：
  - 管理 Partition Leader
  - 管理副本分配
  - 处理 Broker 上下线
  - 维护集群元数据

KRaft 模式（Kafka 3.x）：
  - 一个 Active Controller（写）
  - 多个 Standby Controller（备）
  - 通过 Raft 协议选举
  - 不依赖 ZooKeeper
```

### 6. Kafka 的 KRaft 协议？

```
KRaft = Kafka Raft = 基于 Raft 协议的 Controller 选举

Raft 核心：
  - Leader 选举：Term + Vote
  - 日志复制：AppendEntries
  - 安全性：已提交日志不会丢失

优势（vs ZooKeeper）：
  - 选举快（1-5 秒 vs 10-30 秒）
  - 大集群支持（1M+ Partition vs 200K）
  - 单集群部署（无需 ZK）
```

### 7. Kafka 的 Rebalance 机制？

```
触发场景：
  - Consumer 加入（启动新实例）
  - Consumer 离开（崩溃或主动关闭）
  - 订阅 Topic 变更
  - 心跳超时

Rebalance 流程：
  1. Coordinator 检测 Group 状态变化
  2. 标记 Group 进入 PreparingRebalance
  3. 所有 Consumer 撤销 Partition
  4. 重新加入 Group（JoinGroup）
  5. 选举 Group Leader
  6. 计算新分配
  7. 同步给所有 Consumer
  8. 恢复消费

Eager Rebalance：暂停所有 Consumer
Cooperative Rebalance（2.4+）：增量 Rebalance
```

### 8. Kafka 的消息压缩机制？

```
Kafka 支持端到端压缩：

Producer 压缩：
  - 配置 compression.type=lz4/zstd/snappy/gzip
  - 消息压缩后再发送

Broker 存储：
  - 压缩后的消息存储
  - 节省磁盘

Consumer 解压：
  - Consumer 自动解压
  - 应用层无感知

压缩比：
  - gzip：~3.5x（CPU 高）
  - lz4：~2.5x（推荐）
  - zstd：~3x（Kafka 2.1+）
  - snappy：~2x
```

## 🎯 性能与调优

### 9. Kafka 的吞吐量瓶颈在哪里？

```
瓶颈优先级：
  1. 磁盘 IO（最常见）
     - 升级 NVMe SSD
  2. 网络带宽
     - 升级 10G/25G 网卡
  3. CPU
     - 增加核数
  4. JVM GC
     - G1GC + 调优
     - 或 ZGC（极低延迟）

单 Broker 吞吐：
  - HDD：~30 MB/s
  - SATA SSD：~50-100 MB/s
  - NVMe SSD：~200-500 MB/s
```

### 10. Kafka 的延迟组成？

```
延迟组成（Producer → Broker）：
  - 网络 RTT：~0.1-1ms（同机房）
  - 客户端序列化：~0.1ms
  - 累加器等待（linger.ms）：0-10ms
  - Broker 写入：~1-5ms
  - 副本同步（acks=all）：~1-10ms
  - 磁盘 IO：~0-10ms

优化延迟：
  - 减小 linger.ms
  - 减少副本数（牺牲可用性）
  - acks=1（牺牲一致性）
  - SSD 替代 HDD
```

### 11. Kafka 如何优化 JVM？

```
JVM Heap：
  - 4-6 GB（推荐，不超过 8 GB）
  - 内存留给 Page Cache

GC 选择：
  - G1GC（推荐）：MaxGCPauseMillis=20
  - ZGC（极低延迟）：JDK 11+

关键参数：
  - -Xms = -Xmx（避免堆动态调整）
  - -XX:InitiatingHeapOccupancyPercent=35
  - -XX:G1HeapRegionSize=16M
```

### 12. Kafka 的 Page Cache 优化？

```
Page Cache = 操作系统的文件缓存

✅ 写入：
  消息 → Page Cache（内存）→ 立即返回
  后台线程异步刷盘

✅ 读取：
  Consumer 拉取 → Page Cache（内存命中）→ 返回
  命中率通常 > 90%

优化：
  1. 增加内存（Page Cache 大）
  2. JVM Heap ≤ 8 GB（避免挤占 Page Cache）
  3. 监控 page_cache 命中率
```

## 🎯 生产实战

### 13. Kafka 消息积压怎么处理？

```
应急方案（短期）：
  1. 增加 Consumer 实例（最多到 Partition 数）
  2. 增加 Partition 数（提升并行度）
  3. 优化消费逻辑（异步、批量）

长期方案：
  1. 增加 Broker 节点
  2. 优化消费逻辑
  3. 业务拆分（按重要性）

监控指标：
  - kafka_consumergroup_lag
  - 持续高 lag 告警
```

### 14. Kafka 集群如何扩容？

```
扩容 Broker：
  1. 添加新 Broker 节点
  2. 启动 Kafka
  3. 新 Broker 自动加入集群
  4. 不需要修改任何配置

扩容 Partition：
  kafka-topics.sh --alter \
      --bootstrap-server localhost:9092 \
      --topic orders \
      --partitions 12
  ⚠️ 增加分区会改变 Key 路由（同 Key 可能跨 Partition）

迁移副本（均衡）：
  kafka-reassign-partitions.sh \
      --bootstrap-server localhost:9092 \
      --reassignment-json-file reassign.json \
      --execute
```

### 15. Kafka 副本数怎么选？

```
推荐：3 副本

原因：
  - 容忍 2 个 Broker 故障（max）
  - 常用配置：min.insync.replicas=2
  - 读写分离：1 Leader + 2 Follower

特殊情况：
  - 2 副本：min.insync.replicas=1，容忍 1 故障
  - 5 副本：金融场景，数据可靠性极高

⚠️ 副本数影响：
  - 磁盘占用 × N
  - 网络流量 × N
  - 写入延迟（副本同步）
```

### 16. Kafka 分区数怎么选？

```
原则：
  - 单 Partition 吞吐 ~10-50 MB/s
  - 单 Consumer 处理单 Partition

公式：
  分区数 = max(
      目标吞吐 / 单 Partition 吞吐,
      Consumer 实例数
  )

示例：
  - 目标 300 MB/s
  - 单 Partition ~100 MB/s（NVMe SSD）
  - 至少 3 Partition
  - Consumer 6 个
  - 最终：max(3, 6) = 6 Partition

⚠️ 注意事项：
  - 单 Broker ≤ 2000 Partition
  - 增加 Partition 不可逆
```

### 17. Kafka 消费顺序性如何保证？

```
✅ 同 Partition 内：严格有序
✅ 同 Key 内：保证有序（hash 到同 Partition）
❌ 跨 Partition：无序
❌ 全局有序：需要单 Partition（牺牲性能）

实战：
  1. 启用幂等性（enable.idempotence=true）
  2. max.in.flight.requests.per.connection ≤ 5
  3. acks=all
  4. retries > 0
  5. 业务端幂等
```

### 18. Kafka 的事务怎么实现？

```
Kafka 事务：
  - Producer 事务：跨 Partition 原子写入
  - Consumer read_committed：只读已提交
  - sendOffsetsToTransaction：Offset 原子提交

配置：
  - transactional.id=unique-id
  - enable.idempotence=true
  - isolation.level=read_committed

Java 代码：
  producer.initTransactions();
  producer.beginTransaction();
  producer.send(...);
  producer.sendOffsetsToTransaction(offsets, consumerGroup);
  producer.commitTransaction();  // 原子提交
```

### 19. Kafka 与数据库事务如何保证一致性？

```
问题：DB 事务 + Kafka 发送无法原子

方案 1：Outbox Pattern（推荐）
  - 业务和 Outbox 在同一 DB 事务
  - 独立进程读取 Outbox 并发送
  - 至少一次语义

方案 2：ChainedTransactionManager（已废弃）
  - 链式事务管理
  - DB + Kafka 两阶段提交
  - 不推荐使用

方案 3：Debezium CDC
  - 监听 DB binlog
  - 异步同步到 Kafka
  - 完全解耦
```

### 20. Kafka 适合什么场景？不适合什么场景？

```
✅ 适合：
  - 日志聚合（应用日志、访问日志）
  - 事件流（用户行为、订单事件）
  - 微服务异步通信
  - 流式计算（Kafka Streams、Flink）
  - CDC（数据库变更同步）
  - 消息推送（WebSocket 广播）
  - 削峰填谷（秒杀、下单）

❌ 不适合：
  - 复杂路由（用 RabbitMQ Topic 匹配）
  - 定时消息（用 RabbitMQ 延迟队列）
  - 请求-响应（用 gRPC 或 HTTP）
  - 强事务（用传统 DB 事务）
  - 小数据量、低吞吐（直接 HTTP）
```

## 🎯 总结

**Kafka 高频面试题（下）核心要点**：
- ✅ 理解存储结构（Segment + 稀疏索引）
- ✅ 掌握副本同步机制（ISR + HW）
- ✅ 知道 KRaft 协议（Raft 选举）
- ✅ 理解 Rebalance 和 Consumer Group
- ✅ JVM 和 Page Cache 调优
- ✅ 生产实战（积压、扩容、顺序）
- ✅ Kafka 适用与不适用场景

**下一步：** [🔁 副本同步机制](/10-interview/replica-sync) — 深入原理
