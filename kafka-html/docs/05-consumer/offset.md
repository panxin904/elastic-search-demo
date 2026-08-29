---
title: 偏移量提交
date: 2026-08-15  # date-auto-injected
---

# 📍 偏移量提交

> **Offset** 是 Consumer 的核心概念。理解 Offset 提交机制是**消息不丢、不重复**的关键。

## 🎯 Offset 是什么？

```
Offset = 消息在 Partition 中的位置（long，单调递增）
  - 从 0 开始
  - 每条消息 +1
  - Consumer 通过 Offset 跟踪消费进度

Partition 0: [m0][m1][m2][m3][m4][m5]
              0   1   2   3   4   5  ← offset
                          ↑
                  Consumer 消费到 offset=3，下次从 4 开始
```

## 📊 Offset 提交方式

### 1. 自动提交（默认）

```java
Properties props = new Properties();
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, true);
props.put(ConsumerConfig.AUTO_COMMIT_INTERVAL_MS_CONFIG, 5000);  // 5 秒

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));

while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        processOrder(record);
    }
    // 每 5 秒自动提交 Offset
}
```

**优点**：
- 简单，不用管 Offset
- 适合消息丢失不敏感场景

**缺点**：
- 消息丢失风险（提交后崩溃 → 已提交但未处理的消息丢失）
- 消息重复风险（未提交前崩溃 → 重新消费）

### 2. 手动同步提交

```java
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));

try {
    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        
        for (ConsumerRecord<String, String> record : records) {
            processOrder(record);  // 处理
        }
        
        // 同步提交（阻塞直到完成）
        consumer.commitSync();
    }
} finally {
    try {
        consumer.commitSync();  // 最后一次提交
    } finally {
        consumer.close();
    }
}
```

**优点**：
- 精确控制提交时机
- 消息不丢（处理完再提交）

**缺点**：
- 同步阻塞（提交慢会卡住 Consumer）
- 降低吞吐

### 3. 手动异步提交

```java
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders));

try {
    while (true) {
        ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
        
        for (ConsumerRecord<String, String> record : records) {
            processOrder(record);
        }
        
        // 异步提交（非阻塞）
        consumer.commitAsync((offsets, exception) -> {
            if (exception != null) {
                log.error("Commit failed for offsets {}", offsets, exception);
            } else {
                log.debug("Committed offsets {}", offsets);
            }
        });
    }
} finally {
    try {
        consumer.commitSync();  // 最后一次同步提交（确保关闭前提交）
    } finally {
        consumer.close();
    }
}
```

**优点**：
- 不阻塞 Consumer 线程
- 高吞吐

**缺点**：
- 可能提交失败但不知道
- 关闭前需同步提交兜底

### 4. 指定 Offset 提交

```java
KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));

while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    
    // 指定要提交的 Offset
    Map<TopicPartition, OffsetAndMetadata> offsets = new HashMap<>();
    
    for (ConsumerRecord<String, String> record : records) {
        // 业务处理
        processOrder(record);
        
        // 记录每个 Partition 的 Offset
        offsets.put(
            new TopicPartition(record.topic(), record.partition()),
            new OffsetAndMetadata(record.offset() + 1)
        );
    }
    
    // 提交指定 Offset
    consumer.commitSync(offsets);
}
```

**用途**：
- 批量提交（处理完一批再提交）
- 自定义提交策略（如每 100 条提交一次）

## 📊 Offset 存储

### 存储位置

```
__consumer_offsets Topic（内部 Topic）
  - 默认 50 个 Partition
  - 由 GroupCoordinator 管理
  - Key: (groupId, topic, partition)
  - Value: Offset + Metadata

存储结构：
  compaction 策略（compact）
  - 只保留每个 Key 的最新 Value（最新 Offset）
```

### 查看 Offset 提交

```bash
# 查看 group 提交的所有 offset
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor

# 输出：
# GROUP            TOPIC    PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# order-processor  orders   0          12345           12400           55
# order-processor  orders   1          67890           67900           10
# order-processor  orders   2          1234            1300            66
```

### 自定义 Offset 存储

```java
// 高级用法：把 Offset 存到外部存储（如 MySQL、Redis）
public class CustomOffsetStore {
    
    @Autowired
    private DataSource dataSource;
    
    public void storeOffset(String groupId, TopicPartition tp, long offset) {
        // 存到数据库
        jdbcTemplate.update(
            "INSERT INTO kafka_offsets (group_id, topic, partition, offset) " +
            "VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE offset = ?",
            groupId, tp.topic(), tp.partition(), offset, offset
        );
    }
    
    public long loadOffset(String groupId, TopicPartition tp) {
        // 从数据库读取
        return jdbcTemplate.queryForObject(
            "SELECT offset FROM kafka_offsets WHERE group_id = ? AND topic = ? AND partition = ?",
            Long.class,
            groupId, tp.topic(), tp.partition()
        );
    }
}

// 使用
SeekToCurrentOffsetCallback callback = new SeekToCurrentOffsetCallback() {
    @Override
    public void onPartitionsAssigned(Map<TopicPartition, Long> assignments, ConsumerSeekCallback callback) {
        // 从外部存储加载 Offset
        assignments.forEach((tp, defaultOffset) -> {
            long savedOffset = offsetStore.loadOffset(groupId, tp);
            callback.seek(tp, savedOffset >= 0 ? savedOffset : defaultOffset);
        });
    }
};
```

## 📊 Offset 重置策略

```properties
# auto.offset.reset 配置
auto.offset.reset=latest          # 默认（最新）
auto.offset.reset=earliest        # 最早
auto.offset.reset=none            # 无效 Offset 时抛异常
```

### 触发时机

```
当 Consumer Group 没有提交过 Offset 时（首次启动），使用此配置

场景：
  1. Group 第一次启动
  2. Offset 过期被删除
  3. 显式重置 Offset

⚠️ 已经提交的 Offset 不受 auto.offset.reset 影响
```

## 🔧 Offset 与消费语义的对应

```
At Most Once（最多一次）：
  1. poll() 拉取
  2. 处理
  3. commitSync() / commitAsync()
  → 可能丢失（处理前崩溃）

At Least Once（至少一次，默认）：
  1. poll() 拉取
  2. commitSync() 提交 Offset
  3. 处理
  → 可能重复（提交后处理前崩溃）

Exactly Once（精确一次）：
  1. poll() 拉取
  2. 在事务中处理 + 发送下游
  3. commitTransaction() 原子提交
  → 不丢不重
```

## 📊 实战：正确的 Offset 提交

```java
public class CorrectOffsetConsumer {
    
    public void consume() {
        Properties props = new Properties();
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, "order-processor");
        
        // 1. 关闭自动提交
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
        
        // 2. 读取精度控制
        props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
        
        // 3. 业务超时
        props.put(ConsumerConfig.MAX_POLL_INTERVAL_MS_CONFIG, 300000);  // 5 分钟
        
        KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
        consumer.subscribe(Arrays.asList("orders"));
        
        try {
            while (running) {
                ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
                
                if (records.isEmpty()) continue;
                
                // 4. 处理 + 累积 Offset
                Map<TopicPartition, OffsetAndMetadata> offsetsToCommit = new HashMap<>();
                
                for (ConsumerRecord<String, String> record : records) {
                    try {
                        // 5. 业务处理
                        processOrder(record);
                        
                        // 6. 记录 Offset（+1 表示下次从这个开始）
                        offsetsToCommit.put(
                            new TopicPartition(record.topic(), record.partition()),
                            new OffsetAndMetadata(record.offset() + 1)
                        );
                    } catch (Exception e) {
                        // 7. 业务异常，不更新 Offset（下次重新消费）
                        log.error("Process failed at offset {}", record.offset(), e);
                        throw e;  // 中断整个 poll 循环
                    }
                }
                
                // 8. 提交 Offset（只在所有都处理成功时提交）
                if (!offsetsToCommit.isEmpty()) {
                    consumer.commitSync(offsetsToCommit);
                }
            }
        } finally {
            try {
                consumer.commitSync();  // 最后兜底
            } finally {
                consumer.close();
            }
        }
    }
}
```

## 🔧 Offset 重置命令

```bash
# 重置到最早（从头消费）
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-earliest \
    --execute

# 重置到最新
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-latest \
    --execute

# 重置到指定 Offset
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-offset 1000 \
    --execute

# 重置到指定时间
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-datetime 2024-07-15T10:00:00.000 \
    --execute
```

## ⚠️ 常见问题

### 问题 1：消息重复消费

```
原因：At Least Once 语义，处理完前崩溃
解决：
  1. 业务端幂等设计（唯一索引、Redis SETNX）
  2. 启用事务（精确一次）
```

### 问题 2：消息丢失

```
原因：自动提交后未处理就崩溃
解决：
  1. 关闭自动提交（enable.auto.commit=false）
  2. 处理完再提交 Offset
```

### 问题 3：Offset 提交失败

```
原因：网络问题、Coordinator 不可用
解决：
  1. 启用重试（retries 配置）
  2. 异步提交 + 错误回调
  3. 监控 Offset 提交日志
```

### 问题 4：Lag 一直 0 但日志显示没消费

```
原因：可能消息被 Compact 清理了
解决：
  1. 检查 cleanup.policy
  2. 增加 retention.ms
```

## 🎯 总结

**Offset 提交核心要点**：
- ✅ Offset 是消息在 Partition 中的位置
- ✅ 存储在 __consumer_offsets Topic
- ✅ 默认自动提交（5 秒）
- ✅ 推荐手动提交（处理完再提交）
- ✅ commitSync 阻塞 vs commitAsync 非阻塞
- ⚠️ 自动提交有消息丢失风险
- ⚠️ 手动提交有消息重复风险（需业务幂等）

**下一步：** [🔄 再平衡](/05-consumer/rebalance) — Rebalance 机制详解


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
