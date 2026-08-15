---
title: Topic & Partition
---

# 📂 Topic & Partition

> **Topic** 是 Kafka 的消息分类，**Partition** 是 Topic 的物理分片。理解两者的关系是掌握 Kafka 数据模型的关键。

## 🎯 Topic 与 Partition 关系

```
Topic: orders
├── Partition 0: [m0][m1][m2][m3][m4]...  ← 独立有序日志
├── Partition 1: [m0][m1][m2]...           ← 独立有序日志
└── Partition 2: [m0][m1][m2][m3]...       ← 独立有序日志

同一个 Partition 内的消息有序（offset 单调递增）
不同 Partition 之间无序
```

## 📂 Topic 详解

### Topic 是什么？

```
Topic = 消息的逻辑分类
- Producer 按 Topic 写入
- Consumer 按 Topic 订阅
- 一个 Topic 可以有多个 Partition
- 不同 Topic 之间相互独立
```

### 创建 Topic

```bash
# 创建 3 分区、2 副本的 orders topic
bin/kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 3 \
    --replication-factor 2

# 查看 Topic 详情
bin/kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic orders

# 输出：
# Topic: orders   PartitionCount: 3   ReplicationFactor: 2
#   Partition: 0   Leader: 1   Replicas: 1,2   Isr: 1,2
#   Partition: 1   Leader: 2   Replicas: 2,3   Isr: 2,3
#   Partition: 2   Leader: 3   Replicas: 3,1   Isr: 3,1
```

### Topic 配置

```bash
# 修改分区数（只能增加不能减少）
bin/kafka-topics.sh --alter \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 6

# 修改消息保留时间（默认 7 天）
bin/kafka-topics.sh --alter \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --config retention.ms=604800000

# 删除 Topic
bin/kafka-topics.sh --delete \
    --bootstrap-server localhost:9092 \
    --topic orders
```

## 🗂️ Partition 详解

### Partition 是什么？

```
Partition = Topic 的物理分片（append-only 日志）
- 一个 Partition 对应一个目录
- 目录内有多个 .log 段文件（默认 1GB 一个）
- .log 文件内有索引 .index 和时间戳 .timeindex
```

```
data/kafka-logs/
├── orders-0/
│   ├── 00000000000000000000.log      ← 第 1 个段文件
│   ├── 00000000000000000000.index    ← 稀疏索引
│   ├── 00000000000000000000.timeindex
│   ├── 0000000000001073741824.log    ← 第 2 个段文件
│   └── ...
├── orders-1/
└── orders-2/
```

### Partition 的作用

```
✅ 并行度
   - 不同 Partition 可被不同 Consumer 并行消费
   - 单 Consumer Group 最大并行度 = Partition 数

✅ 横向扩展
   - 单 Broker 容量有限
   - Partition 可分布在多个 Broker

✅ 顺序保证
   - 分区内严格有序（offset 单调递增）
   - 分区间无序
```

### Partition 数量选择

```
经验公式：
  partition_count = max(target_throughput / single_partition_throughput, consumer_count)

示例：
  - 目标吞吐 300MB/s
  - 单 Partition 100MB/s
  - 需要 3 个 Partition
  - Consumer 数量 = 2
  - 最终 Partition 数 = max(3, 2) = 3
```

### Partition 数据结构

```
Partition = 顺序追加的日志（Segment 组成）

Segment 1: [m0][m1][m2]...[m999]    ← 达到 log.segment.bytes 触发滚动
Segment 2: [m1000][m1001]...[m1999]
Segment 3: [m2000][m2001]...

每个 Segment 包含：
  - .log       消息内容
  - .index     偏移量到物理位置的索引（稀疏索引）
  - .timeindex 时间戳到偏移量的索引
```

### Segment 滚动策略

```properties
# 触发 Segment 滚动的条件（满足任一即触发）
log.segment.bytes=1073741824      # 默认 1GB
log.segment.ms=604800000          # 默认 7 天
log.roll.hours=168                # 默认 7 天（兼容旧版本）

# 索引粒度
log.index.interval.bytes=4096     # 每 4KB 数据一个索引项
log.index.size.max.bytes=10485760 # 索引文件最大 10MB
```

## 🔍 分区策略

### 默认分区器

```java
// Kafka 默认分区器
public int partition(String topic, Object key, byte[] keyBytes, Object value, byte[] valueBytes, Cluster cluster) {
    List<PartitionInfo> partitions = cluster.partitionsForTopic(topic);
    if (keyBytes == null) {
        // key 为 null，轮询所有分区
        return ThreadLocalRandom.current().nextInt(partitions.size());
    }
    // key 不为 null，按 hash(key) % partitions
    return Utils.toPositive(Utils.murmur2(keyBytes)) % partitions.size();
}
```

### 消息分发到分区的规则

```
1. 指定 partition（最高优先级）
   producer.send(new ProducerRecord(topic, 0, key, value));   // 直接发到 P0

2. 指定 key（按 key hash）
   producer.send(new ProducerRecord(topic, key, value));      // hash(key) % N

3. 无 key（轮询）
   producer.send(new ProducerRecord(topic, value));           // 轮询所有分区
```

### 自定义分区器

```java
public class CustomPartitioner implements Partitioner {
    @Override
    public int partition(String topic, Object key, byte[] keyBytes, Object value,
                        byte[] valueBytes, Cluster cluster) {
        // 自定义逻辑：例如按业务类型分发
        if (key instanceof String) {
            String keyStr = (String) key;
            if (keyStr.startsWith("VIP_")) {
                return 0;  // VIP 用户走专门分区
            }
        }
        return Utils.toPositive(Utils.murmur2(keyBytes)) % cluster.partitionsForTopic(topic).size();
    }
}
```

## 📊 消息在 Partition 中的物理布局

```
Offset 物理位置映射（.index 文件）：

.offset   position
  0        0          ← m0 起始物理位置
  100      4096       ← m100 物理位置
  200      8192       ← m200 物理位置
  ...      ...        ← 稀疏索引（每 4KB 一个）

读 message at offset=150：
  1. 二分查找 index → 找到 offset=100，position=4096
  2. 从 position=4096 开始顺序扫描，直到 offset=150
```

## 🔧 分区扩容

### 增加分区数

```bash
# 单 Topic 增加分区（注意：已有消息不会重新分布）
bin/kafka-topics.sh --alter \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 6

# 集群级重新分配（不同 Broker 间的分区迁移）
cat > reassign.json << EOF
{
  "version": 1,
  "partitions": [
    {"topic": "orders", "partition": 0, "replicas": [1, 3]},
    {"topic": "orders", "partition": 1, "replicas": [2, 3]}
  ]
}
EOF

bin/kafka-reassign-partitions.sh \
    --bootstrap-server localhost:9092 \
    --reassignment-json-file reassign.json \
    --execute
```

### ⚠️ 分区扩容的限制

```
❌ 减少分区数（不支持）
   Kafka 不支持减少分区
   原因：数据重排成本高，且会破坏消费者 offset 语义

⚠️ 增加分区不影响历史消息
   已有消息的 hash(key) % old_N 仍然有效
   新消息按 hash(key) % new_N 路由
   可能导致相同 key 路由到不同分区（顺序破坏）
```

## 📊 Topic vs Partition vs Replica

```
Topic (逻辑分类)
└── Partition 0 (物理分片 0)
    ├── Replica 0 (Leader)      ← 处理读写请求
    ├── Replica 1 (Follower)    ← 同步数据
    └── Replica 2 (Follower)    ← 同步数据
├── Partition 1 (物理分片 1)
│   ├── Replica 0 (Leader)
│   └── ...
└── Partition 2

Topic = 抽象的「类别」
Partition = 物理的「分片」（Topic 内有顺序）
Replica = 每个 Partition 的「副本」（高可用）
```

## 🎯 总结

**Topic & Partition 核心要点**：
- ✅ Topic 是逻辑分类，Partition 是物理分片
- ✅ 分区内有序（offset 单调递增），分区间无序
- ✅ 默认分区器：hash(key) % partitions
- ✅ Partition 数量 = 吞吐上限
- ⚠️ 只增不减（Kafka 不支持减少分区）
- ⚠️ 增加分区会破坏顺序保证

**下一步：** [💬 消息模型](/01-basics/message-model) — 点对点 vs 发布订阅
