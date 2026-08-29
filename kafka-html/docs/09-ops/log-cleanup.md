---
title: 日志清理
date: 2026-08-15  # date-auto-injected
---

# 🗑️ 日志清理

> **日志清理**是 Kafka 运维的重要工作。Kafka 的数据存在磁盘上，需要**定期清理过期消息**，避免磁盘占满。

## 🎯 Kafka 日志结构

### Segment 文件

```
data/kafka-logs/
├── orders-0/
│   ├── 00000000000000000000.log         ← 第 1 个段
│   ├── 00000000000000000000.index       ← 索引
│   ├── 00000000000000000000.timeindex
│   ├── 0000000000001073741824.log      ← 第 2 个段（达到 1GB 滚动）
│   ├── 0000000000001073741824.index
│   └── 0000000000001073741824.timeindex
├── orders-1/
│   ├── 00000000000000000000.log
│   └── ...
└── orders-2/
    └── ...
```

### 日志大小估算

```
每个 Segment：1 GB（默认）
每个 Partition：N 个 Segment（取决于数据量）
总磁盘占用 = Σ Partition 数 × 副本数 × 平均 Segment 数 × 1 GB

示例：
  - 100 个 Partition
  - 3 副本
  - 每个 Partition 10 个 Segment
  - 总占用 = 100 × 3 × 10 × 1 GB = 3 TB
```

## 📊 保留策略

### 基于时间（retention.ms）

```properties
# 消息保留时间（最常用）
log.retention.hours=168          # 默认 7 天
log.retention.minutes=10080      # 7 天（分钟）
log.retention.ms=604800000       # 7 天（毫秒）

# 不同 Topic 不同保留
# （在 Topic 创建时设置）
kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --config retention.ms=259200000  # 3 天
```

**优点**：
- ✅ 简单直观
- ✅ 自动清理

**缺点**：
- ⚠️ 不考虑数据量

### 基于大小（retention.bytes）

```properties
# 每个 Partition 保留的最大字节数
log.retention.bytes=1073741824   # 1 GB

# ⚠️ 这是 per Partition，不是 Topic 总量
```

**适用场景**：
- 数据量相对稳定的 Topic
- 磁盘有限的场景

### 混合策略

```properties
# 同时设置时间和大小
log.retention.ms=604800000       # 7 天
log.retention.bytes=1073741824   # 1 GB

# 两个条件满足任一即清理（通常先达到 size）
```

### 删除策略

```properties
# 删除策略（delete 或 compact）
log.cleanup.policy=delete         # 默认（删除过期消息）

# compact：只保留每个 Key 最新值
log.cleanup.policy=compact
log.cleanup.policy=compact,delete  # 混合策略
```

## 🔧 日志清理机制

### Log Cleaner 线程

```
Kafka Broker 启动 Log Cleaner 线程：
  - 定时扫描所有 Partition
  - 检查 Segment 是否过期
  - 删除过期 Segment
  - 释放磁盘空间

清理流程：
  1. 检查 Segment 的最后修改时间
  2. 如果 (now - lastModified) > retention.ms
     → 删除 Segment
  3. 如果 Partition 总大小 > retention.bytes
     → 删除最早的 Segment
```

### 配置参数

```properties
# ==== 清理频率 ====
log.retention.check.interval.ms=300000  # 5 分钟检查一次

# ==== 文件删除策略 ====
log.segment.delete.delay.ms=60000      # Segment 标记删除后等 60 秒才删

# ==== Compact 模式 ====
log.cleaner.backoff.ms=15000           # 清理线程空闲多久后休眠
log.cleaner.dedupe.buffer.size=134217728  # 去重缓存 128 MB
log.cleaner.io.buffer.size=524288     # IO 缓存
```

## 🛠️ 日志清理实战

### 场景 1：紧急清理（磁盘满）

```bash
# 1. 检查磁盘使用
df -h /var/lib/kafka

# 2. 查看占用大的 Topic
du -sh /data/kafka-logs/orders-*

# 3. 修改 retention.ms（临时降低）
kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type topics --entity-name orders \
    --add-config "retention.ms=86400000"  # 改为 1 天

# 4. 手动触发清理
# Kafka 会自动检测到配置变化，下次清理时删除过期文件
# 或者重启 Kafka 强制清理
```

### 场景 2：手动删除历史数据

```bash
# 1. 备份数据（可选）
mkdir -p /backup/orders-2024-07
cp /data/kafka-logs/orders-0/0000000000000000*.log /backup/orders-2024-07/

# 2. 删除过期 Segment
# 警告：直接删除 log 文件会导致数据丢失
# 推荐：用 Kafka 命令而不是直接删除

# 3. 删除整个 Topic
kafka-topics.sh --delete --bootstrap-server localhost:9092 --topic old-topic

# 4. 等待异步删除
# Kafka 会异步删除磁盘文件
```

### 场景 3：清理 Compact Topic

```bash
# Compact 模式：只保留每个 Key 最新值
kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic user-profile \
    --config cleanup.policy=compact

# 手动触发压缩
kafka-log-dirs.sh --bootstrap-server localhost:9092 \
    --describe --broker-list 1

# 查看 compaction 进度
kafka-log-dirs.sh --bootstrap-server localhost:9092 \
    --describe --broker-list 1 | grep "compaction"
```

### 场景 4：定期清理脚本

```bash
#!/bin/bash
# kafka-cleanup.sh
# 定期清理 30 天前的数据（保险起见）

BROKER="localhost:9092"
KAFKA_DIR="/data/kafka-logs"
RETENTION_DAYS=7

# 1. 修改所有 Topic 的 retention
for topic in $(kafka-topics.sh --list --bootstrap-server $BROKER); do
    kafka-configs.sh --bootstrap-server $BROKER \
        --alter --entity-type topics --entity-name $topic \
        --add-config "retention.ms=$((RETENTION_DAYS * 86400 * 1000))" 2>/dev/null
done

# 2. 检查磁盘
disk_usage=$(df -h $KAFKA_DIR | awk 'NR==2 {print $5}' | tr -d '%')

if [ "$disk_usage" -gt 80 ]; then
    # 3. 触发清理（缩小 retention）
    for topic in $(kafka-topics.sh --list --bootstrap-server $BROKER); do
        kafka-configs.sh --bootstrap-server $BROKER \
            --alter --entity-type topics --entity-name $topic \
            --add-config "retention.ms=$((3 * 86400 * 1000))" 2>/dev/null  # 3 天
    done
    echo "WARNING: Disk usage $disk_usage%, retention reduced to 3 days"
fi

# 4. 报告
echo "$(date): Cleanup completed, disk usage: $disk_usage%"
```

### Cron 定时执行

```bash
# 每天凌晨 2 点执行清理
0 2 * * * /opt/kafka/scripts/kafka-cleanup.sh >> /var/log/kafka-cleanup.log 2>&1
```

## 📊 日志清理监控

### 关键指标

```bash
# 1. 磁盘使用（最关键）
df -h /data/kafka-logs

# 2. 各 Topic 占用
du -sh /data/kafka-logs/*

# 3. Kafka log.dirs 信息
kafka-log-dirs.sh --bootstrap-server localhost:9092 \
    --describe --broker-list 1

# 输出：
#   Topic  Partition  Log Size  Log Offset  Lag
#   orders  0          1024MB   1000000     0
#   orders  1          2048MB   2000000     0
#   ...
```

### Prometheus 告警

```yaml
groups:
  - name: kafka_disk
    rules:
      # 磁盘使用 > 80%
      - alert: KafkaDiskUsageHigh
        expr: 100 - (node_filesystem_avail_bytes{f mountpoint="/var/lib/kafka"} / node_filesystem_size_bytes{f mountpoint="/var/lib/kafka"} * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Kafka 磁盘使用超过 80%"
      
      # 磁盘使用 > 90%
      - alert: KafkaDiskUsageCritical
        expr: 100 - (node_filesystem_avail_bytes{f mountpoint="/var/lib/kafka"} / node_filesystem_size_bytes{f mountpoint="/var/lib/kafka"} * 100) > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Kafka 磁盘使用超过 90%"
```

## 📊 Compact 模式详解

### Compact vs Delete

| 维度 | Delete | Compact |
|------|--------|---------|
| 保留所有消息 | ❌ | ❌ |
| 保留每个 Key 最新 | ❌ | ✅ |
| 适用场景 | 日志、事件流 | 配置、状态 |
| 磁盘占用 | 较大 | 较小（每个 Key 1 条） |
| 索引大小 | 较大 | 较小 |

### Compact 实战

```bash
# 创建 Compact Topic
kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic user-profile \
    --partitions 6 \
    --replication-factor 3 \
    --config cleanup.policy=compact \
    --config min.cleanable.dirty.ratio=0.1

# Compact Topic 监控
kafka-log-dirs.sh --bootstrap-server localhost:9092 \
    --describe --broker-list 1 \
    --topic user-profile
```

### Compact 触发条件

```properties
# compaction 触发条件
log.cleaner.dedupe.buffer.size=134217728  # 去重缓存
log.cleaner.io.buffer.load.factor=0.9    # 触发 GC 阈值

# 触发比率（脏数据比例）
min.cleanable.dirty.ratio=0.5             # 脏数据 > 50% 触发
```

## 📊 Compact vs Delete 选型

### 选 Delete 的场景

```
✅ 日志收集（应用日志、访问日志）
✅ 事件流（订单事件、用户行为）
✅ 消息通知
✅ 任何"事件型"数据
```

### 选 Compact 的场景

```
✅ 数据库变更同步（CDC，每个 key 只关心最新状态）
✅ 用户配置（每次更新覆盖旧值）
✅ 设备状态（心跳上报）
✅ 任何"状态型"数据
```

### 选 Compact + Delete 的场景

```
✅ 短保留后转 compact（如 7 天后压缩）
✅ 减少存储占用同时保留最近历史
```

## 🛠️ 日志清理最佳实践

### 1. 规划 retention

```
✅ 按业务设置不同 retention
   - 订单：30 天（合规要求）
   - 日志：7 天
   - 临时数据：1 天
   - 用户状态：永久（compact）

✅ 监控磁盘使用，提前告警
   - 50%：提醒
   - 80%：告警
   - 90%：紧急
```

### 2. 自动化清理

```yaml
✅ Cron 定时清理脚本
✅ 监控 + 自动扩容
✅ 提前扩容（不等到满）
```

### 3. 备份策略

```
⚠️ 不要直接 rm log 文件
⚠️ 删除前确认不需要数据
⚠️ 重要数据先备份
```

## ⚠️ 常见问题

### 问题 1：磁盘满导致 Kafka 不可用

```
症状：
  - Producer 报 No space left on device
  - Broker 拒绝写入

解决：
  1. 紧急扩容（加磁盘）
  2. 减少 retention.ms
  3. 删除旧 Topic
  4. 迁移冷数据到对象存储
```

### 问题 2：清理不及时

```
原因：log.retention.check.interval.ms 太大（默认 5 分钟）
解决：
  减小检查间隔（生产可保持 5 分钟）
```

### 问题 3：Compact 占用大量 IO

```
现象：Compact 时 Broker IO 占用高
解决：
  - 增加 dedupe.buffer.size
  - 调整 compaction 线程数
  - 业务低峰期手动触发
```

### 问题 4：误删 Topic 数据

```
场景：kafka-topics.sh --delete 后数据真的没了
解决：
  1. 删除前备份
  2. 设置 topic 级别的 deletion protection（不推荐）
  3. 软删除（设置 retention.ms=1ms，数据自动清理）
```

## 🎯 总结

**日志清理核心要点**：
- ✅ 基于 retention.ms 或 retention.bytes 自动清理
- ✅ Delete 策略：删除过期消息
- ✅ Compact 策略：保留每个 Key 最新
- ✅ 监控磁盘使用，提前告警
- ✅ 按业务设置不同 retention
- ⚠️ 不要直接 rm log 文件
- ⚠️ Compact 占用 IO（业务低峰期触发）

**下一步：** [📈 监控指标](/09-ops/metrics) — Kafka 全维度监控
