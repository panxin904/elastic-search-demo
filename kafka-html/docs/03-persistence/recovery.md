---
title: 数据保留策略
date: 2026-08-15  # date-auto-injected
---

# ⏰ 数据保留策略

> Kafka 的**数据保留策略**决定消息何时被删除，是**磁盘管理**和**数据可重放性**的关键。

## 🎯 为什么需要保留策略？

```
✅ 磁盘管理
   - Kafka 消息持久化到磁盘
   - 不清理会无限增长

✅ 数据可重放
   - 保留期内可重放历史消息
   - 支持 Kafka Streams 流处理

✅ 合规要求
   - 某些业务需要保留 30 天+
   - 审计、回溯需求
```

## 📊 保留策略配置

### 基于时间

```properties
# ==== 保留时间 ====
log.retention.ms=604800000      # 7 天（毫秒，最优先）
log.retention.minutes=10080     # 7 天（分钟）
log.retention.hours=168         # 7 天（小时，默认）

# 优先级：ms > minutes > hours
```

### 基于大小

```properties
# ==== 保留大小（per Partition） ====
log.retention.bytes=1073741824   # 1GB

# ⚠️ 注意：是每个 Partition 的限制
# 不是整个 Topic 的限制
```

### 同时使用

```properties
# 同时设置时间和大小
log.retention.ms=604800000
log.retention.bytes=1073741824
# 满足任一条件即清理
```

## 📊 删除策略

### Delete（默认）

```properties
log.cleanup.policy=delete
# 超过保留时间或大小的消息直接删除
```

### Compact（压缩）

```properties
log.cleanup.policy=compact
# 只保留每个 Key 的最新消息
# 适用场景：CDC、用户状态
```

### 混合策略

```properties
log.cleanup.policy=delete,compact
# Compact 一段时间后再 Delete
# 通过两个时间阈值控制
log.cleaner.delete.retention.ms=86400000
```

## 📊 删除机制

### Log Retention 线程

```
Kafka 启动 Log Retention 线程：
  - 每 log.retention.check.interval.ms 检查一次（默认 5 分钟）
  - 检查每个 Segment 的最后修改时间
  - 判断是否过期
  - 删除过期 Segment

时间线：
  T0   Segment 创建
  T1   写入消息
  T2   持续写入...
  T3   当前时间 - Segment 最后修改时间 > retention.ms
  T4   标记删除
  T5   等 log.segment.delete.delay.ms（默认 60 秒）
  T6   实际删除文件
```

### 删除触发条件

```
1. 时间条件
   now - segment.lastModifiedTime > retention.ms

2. 大小条件（per partition）
   partition.totalSize > retention.bytes
   → 删除最旧的 Segment

3. 主动删除
   kafka-topics.sh --delete --topic XXX
```

## 📊 实战配置

### 不同业务的保留策略

```bash
# 订单数据（保留 30 天）
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic orders \
    --config retention.ms=2592000000  # 30 天

# 日志数据（保留 3 天）
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic logs \
    --config retention.ms=259200000   # 3 天

# 用户状态（compact）
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic user-profile \
    --config cleanup.policy=compact
```

### 动态修改

```bash
# 修改 retention
kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type topics --entity-name orders \
    --add-config "retention.ms=86400000"
```

## 📊 Compact 详解

### 适用场景

```
✅ 数据库变更同步（CDC）
   - INSERT / UPDATE / DELETE
   - 只关心最新状态

✅ 用户配置
   - 每次更新覆盖
   - 关心最新值

✅ 设备状态
   - 心跳上报
   - 只保留最后状态
```

### Compact 流程

```
1. Log Cleaner 线程扫描
2. 找出"脏" Segment（可被清理）
3. 重新写入每个 Key 的最新消息
4. 删除旧消息
5. 替换原 Segment

⚠️ Compact 不影响 Producer / Consumer
   - Compact 后台异步执行
```

### Compact 配置

```properties
log.cleanup.policy=compact
log.cleaner.min.cleanable.ratio=0.5   # 脏数据 > 50% 触发
log.cleaner.dedupe.buffer.size=134217728  # 128MB
log.cleaner.io.buffer.size=524288       # 512KB
```

## 📊 监控与告警

```yaml
- alert: KafkaRetentionDisabled
  expr: kafka_topic_partition_retention_bytes == -1
  labels:
    severity: warning
  annotations:
    summary: "Kafka Topic 未配置保留策略"

- alert: KafkaRetentionLow
  expr: kafka_topic_partition_log_end_offset - kafka_topic_partition_log_start_offset > 1000000000
  labels:
    severity: warning
  annotations:
    summary: "Kafka Topic 消息数超过 10 亿"
```

## 🛠️ 实战：磁盘容量规划

### 估算公式

```
磁盘占用 = 消息数 × 单消息大小 × 副本数 × 保留时间（秒） / 写入速率（条/秒）

示例：
  - 100 万条/秒
  - 单消息 1 KB
  - 3 副本
  - 保留 7 天

磁盘占用 = 100 万 × 1 KB × 3 × 604800 = 1.7 PB
```

### 容量监控

```bash
# 监控磁盘使用
df -h /data/kafka-logs

# 监控各 Topic
du -sh /data/kafka-logs/*

# 监控删除进度
kafka-log-dirs.sh --bootstrap-server localhost:9092 \
    --describe --broker-list 1
```

## 🎯 总结

**数据保留策略核心要点**：
- ✅ 基于时间（retention.ms）和大小（retention.bytes）
- ✅ Delete 策略：删除过期消息
- ✅ Compact 策略：只保留最新消息（按 Key）
- ✅ 混合策略：先 compact 后 delete
- ✅ 容量规划要考虑副本数和保留时间
- ⚠️ 磁盘满是常见故障
- ⚠️ Compaction 占用 IO（业务低峰期触发）

**下一步：** [🔄 数据恢复策略](/03-persistence/recovery) — 灾难恢复


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
