---
title: Topic 管理
date: 2026-08-15  # date-auto-injected
---

# 📂 Topic 管理

> Topic 是 Kafka 的消息分类，是日常运维的核心对象。本章详解 kafka-topics.sh 的所有用法。

## 🎯 Topic 生命周期

```
创建 → 查看 → 修改 → 删除

CREATE → DESCRIBE → ALTER → DELETE
```

## 📝 创建 Topic

### 基础创建

```bash
# 最简单的创建（使用 broker 默认配置）
kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic my-topic

# 指定分区数和副本数
kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 3 \
    --replication-factor 2
```

### 带配置的创建

```bash
# 创建带完整配置的 topic
kafka-topics.sh --create \
    --bootstrap-server localhost:9092 \
    --topic user-events \
    --partitions 6 \
    --replication-factor 3 \
    --config retention.ms=604800000 \
    --config cleanup.policy=delete \
    --config compression.type=producer \
    --config min.insync.replicas=2 \
    --config segment.ms=86400000 \
    --config segment.bytes=1073741824
```

### 批量创建

```bash
# 批量创建多个 topic（脚本）
cat > create-topics.sh << 'EOF'
#!/bin/bash
BROKER="localhost:9092"

topics=(
    "orders:3:2"
    "payments:6:2"
    "shipments:3:1"
    "users:2:2"
    "audit-logs:3:2"
)

for entry in "${topics[@]}"; do
    IFS=':' read -r name partitions rf <<< "$entry"
    kafka-topics.sh --create \
        --bootstrap-server $BROKER \
        --topic $name \
        --partitions $partitions \
        --replication-factor $rf \
        --if-not-exists
done
EOF

chmod +x create-topics.sh
./create-topics.sh
```

## 🔍 查看 Topic

### 列出所有 Topic

```bash
# 列出所有 topic
kafka-topics.sh --list --bootstrap-server localhost:9092

# 列出匹配模式的 topic
kafka-topics.sh --list --bootstrap-server localhost:9092 --topic 'orders*'

# 排除内部 topic
kafka-topics.sh --list --bootstrap-server localhost:9092 --exclude-internal

# 查看所有 topic（包括内部）
kafka-topics.sh --list --bootstrap-server localhost:9092
```

### 查看 Topic 详情

```bash
# 单个 topic 详情
kafka-topics.sh --describe --bootstrap-server localhost:9092 --topic orders

# 输出：
# Topic: orders   PartitionCount: 3   ReplicationFactor: 2
#   TopicId: abc123def456
#   Partition: 0   Leader: 1   Replicas: 1,2   Isr: 1,2
#   Partition: 1   Leader: 2   Replicas: 2,3   Isr: 2,3
#   Partition: 2   Leader: 3   Replicas: 3,1   Isr: 3,1

# 多个 topic
kafka-topics.sh --describe --bootstrap-server localhost:9092 \
    --topic orders,payments,users

# 显示未授权的 topic
kafka-topics.sh --describe --bootstrap-server localhost:9092 \
    --topic orders --include-authorized-operations
```

### 查看 Topic 配置

```bash
# 查看 topic 的所有配置
kafka-configs.sh --bootstrap-server localhost:9092 \
    --describe --entity-type topics --entity-name orders

# 输出：
# Configs for topic 'orders' are:
#   cleanup.policy=delete
#   compression.type=producer
#   retention.ms=604800000
#   segment.bytes=1073741824
#   ...
```

## ✏️ 修改 Topic

### 增加分区数

```bash
# 把 orders 从 3 分区增加到 6 分区
kafka-topics.sh --alter \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 6

# 警告：
# ⚠️ 已有消息的 hash(key) % 3 仍然有效
# ⚠️ 新消息按 hash(key) % 6 路由
# ⚠️ 同 key 的消息可能分布到不同分区（顺序破坏！）
```

### 修改 Topic 配置

```bash
# 修改单个配置
kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type topics --entity-name orders \
    --add-config "retention.ms=259200000"

# 修改多个配置
kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type topics --entity-name orders \
    --add-config "retention.ms=259200000,cleanup.policy=compact"

# 删除配置（恢复默认值）
kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type topics --entity-name orders \
    --delete-config "retention.ms"
```

### 关键 Topic 配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `retention.ms` | 604800000 (7天) | 消息保留时间 |
| `retention.bytes` | -1 | 消息保留大小（per partition） |
| `cleanup.policy` | delete | delete / compact / delete,compact |
| `compression.type` | producer | none / gzip / snappy / lz4 / zstd |
| `segment.ms` | 604800000 (7天) | Segment 滚动时间 |
| `segment.bytes` | 1073741824 (1GB) | Segment 滚动大小 |
| `min.insync.replicas` | 1 | 最小同步副本数 |
| `max.message.bytes` | 1048588 | 单条消息最大字节数 |
| `flush.messages` | 9223372036854775807 | 强制 flush 间隔（条） |
| `flush.ms` | 9223372036854775807 | 强制 flush 间隔（毫秒） |

## 🗑️ 删除 Topic

```bash
# 删除单个 topic
kafka-topics.sh --delete \
    --bootstrap-server localhost:9092 \
    --topic orders

# 确认提示：
# Are you sure you want to delete the topic 'orders'? (yes/no)
# 输入 yes 确认

# 批量删除
for topic in orders payments users; do
    kafka-topics.sh --delete \
        --bootstrap-server localhost:9092 \
        --topic $topic
done

# 注意事项：
# ⚠️ 删除需要 server.properties 配置 delete.topic.enable=true（默认 true）
# ⚠️ 删除是不可逆的！所有消息和 offset 都会清除
# ⚠️ 数据保留期过后才真正释放磁盘空间
```

## 🔄 Topic 重命名

```bash
# Kafka 不支持直接重命名 Topic
# 替代方案：
# 1. 创建新 Topic + 数据迁移（推荐）
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic new-orders --partitions 3 --replication-factor 2

# 2. 用 MirrorMaker / Kafka Connect 同步数据

# 3. 用 Consumer 读旧 + Producer 写到新
```

## 📊 Topic 配置详解

### cleanup.policy

```bash
# delete（默认）：定期删除过期消息
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic logs --config cleanup.policy=delete --partitions 3 --replication-factor 2

# compact：只保留每个 key 的最新消息（适合 changelog 场景）
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic user-profile --config cleanup.policy=compact --partitions 3 --replication-factor 2

# delete,compact：先 delete 一段时间，再 compact（混合策略）
kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type topics --entity-name logs \
    --add-config "cleanup.policy=delete,compact,segment.ms=3600000"
```

### retention.ms vs retention.bytes

```bash
# 时间维度（先到先删）
kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type topics --entity-name logs \
    --add-config "retention.ms=86400000"

# 大小维度（per partition，达到上限就删最早）
kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type topics --entity-name logs \
    --add-config "retention.bytes=1073741824"

# 两个同时设置：满足任一即删除
kafka-configs.sh --bootstrap-server localhost:9092 \
    --alter --entity-type topics --entity-name logs \
    --add-config "retention.ms=86400000,retention.bytes=1073741824"
```

## 🛠️ 实战：创建生产级 Topic

```bash
# 订单 topic（高吞吐、低延迟）
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 12 \
    --replication-factor 3 \
    --config retention.ms=259200000 \
    --config compression.type=lz4 \
    --config min.insync.replicas=2 \
    --config segment.ms=86400000 \
    --config max.message.bytes=1048576

# 用户配置 topic（最终状态）
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic user-profile \
    --partitions 6 \
    --replication-factor 3 \
    --config cleanup.policy=compact \
    --config segment.ms=3600000

# 日志 topic（短保留）
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic app-logs \
    --partitions 6 \
    --replication-factor 2 \
    --config retention.ms=86400000 \
    --config cleanup.policy=delete
```

## ⚠️ 常见问题

### 问题 1：Topic 已存在

```
报错：Topic 'orders' already exists
解决：
  - 加 --if-not-exists 参数
  - 或先删除再创建（数据丢失）
```

### 问题 2：副本数超过 Broker 数

```
报错：Replication factor: 3 larger than available brokers: 2
解决：
  - 减少副本数：replication-factor=2
  - 或增加 Broker 数量
```

### 问题 3：减少分区失败

```
报错：The proposed topic has more partitions than allowed
解决：
  Kafka 不支持减少分区，只能增加
  如需减少，需要创建新 topic 并迁移数据
```

## 🎯 总结

**Topic 管理核心要点**：
- ✅ kafka-topics.sh 完整 CLI
- ✅ 创建 / 查看 / 修改 / 删除 4 个操作
- ✅ 配置项众多（retention / cleanup.policy / segment 等）
- ✅ 减少分区不支持
- ⚠️ 删除是不可逆的
- ⚠️ 增加分区会破坏顺序保证

**下一步：** [✉️ 生产消费调试](/03-cli/produce-consume) — 命令行生产消费实战
