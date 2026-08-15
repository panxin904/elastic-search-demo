---
title: Segment 快照机制
---

# 📸 Segment 快照机制

> Kafka 通过 **Segment 文件**实现类似 RDB 的快照机制。本章详解 Segment 的结构、滚动策略和恢复机制。

## 🎯 Segment 是什么？

```
Segment = Kafka 日志文件的基本单位

类比 Redis RDB：
  RDB 是 Redis 内存快照
  Segment 是 Kafka 日志片段（append-only）

特点：
  ✅ append-only（顺序写）
  ✅ 达到大小或时间后滚动
  ✅ 老的 Segment 可独立删除
  ✅ 每个 Segment 有自己的索引
```

## 📂 Segment 文件结构

```
data/kafka-logs/
├── orders-0/
│   ├── 00000000000000000000.log         ← Segment 1
│   ├── 00000000000000000000.index       ← 偏移量索引
│   ├── 00000000000000000000.timeindex   ← 时间戳索引
│   ├── 0000000000001073741824.log       ← Segment 2（达到 1GB 滚动）
│   ├── 0000000000001073741824.index
│   ├── 0000000000001073741824.timeindex
│   └── ...
├── orders-1/
│   ├── 00000000000000000000.log
│   └── ...
└── orders-2/
    └── ...
```

### 文件命名规则

```
Segment 文件名 = Segment 中第一条消息的 offset（20 位数字）

示例：
  00000000000000000000.log   ← offset 0 起始
  0000000000001073741824.log  ← offset 1073741824 起始（1GB 处）

命名约定：
  - 20 位数字（前导零）
  - 方便排序和查找
  - 直接用 offset 命名，无需查表
```

## 📊 Segment 内部结构

### .log 文件

```
.log 文件 = 消息的二进制流（append-only）

格式：
┌──────────────────────────────────────────┐
│ 8 bytes  │ offset (int64)                  │
├──────────┼────────────────────────────────┤
│ 4 bytes  │ message size (int32)            │
├──────────┼────────────────────────────────┤
│ 1 byte   │ crc32 (int8)                    │
├──────────┼────────────────────────────────┤
│ 1 byte   │ attributes (1 byte)             │
├──────────┼────────────────────────────────┤
│ N bytes  │ key (varint length + bytes)     │
├──────────┼────────────────────────────────┤
│ N bytes  │ value (varint length + bytes)   │
└──────────┴────────────────────────────────┘
```

### .index 文件（稀疏索引）

```
稀疏索引（每 4KB 一个索引项）：

offset    physical_position
  0        0
  100      4096
  200      8192
  ...

查询 offset=150：
  1. 加载 .index 到内存
  2. 二分查找找到 100（position=4096）
  3. 从 .log 文件的 4096 位置顺序扫描
  4. 找到 offset=150 的消息
```

### .timeindex 文件

```
时间戳 → 偏移量 索引：

timestamp          offset
1721037600000       100
1721037605000       200
1721037610000       300
...

用途：
  - 按时间查询消息
  - Kafka Streams 用
  - 消息回溯（按时间）
```

## 🔄 Segment 滚动策略

### 触发条件

```properties
# 满足任一条件即触发滚动
log.segment.bytes=1073741824          # 1GB（默认）
log.segment.ms=604800000              # 7 天（默认）
log.roll.hours=168                    # 兼容旧版本（默认 7 天）

# 滚动优先级：
# 1. log.segment.bytes 先到达
# 2. log.segment.ms 先到达
# 3. log.roll.hours 先到达
```

### 滚动流程

```
1. 当前 Segment 写满（或时间到）
   ↓
2. 关闭当前 .log 文件（关闭文件描述符）
   ↓
3. 创建新 .log 文件（新 offset 起始）
   ↓
4. 写入新 offset 起始的消息
   ↓
5. 旧 Segment 等待过期删除

优点：
  ✅ 大文件变小（删除高效）
  ✅ 索引小（加载快）
  ✅ 历史数据管理灵活
```

## 📊 Segment 与恢复

### Broker 重启恢复

```
Kafka Broker 重启：
  1. 加载所有 Partition 的元数据
  2. 加载每个 Partition 最新活跃的 Segment
  3. 加载索引到内存（.index + .timeindex）
  4. 不需要重放历史消息（已经在磁盘）

⚠️ 重要：
  - Segment 文件保留所有已写入的消息
  - 重启不丢数据
  - 启动速度快（索引加载）
```

### Segment 删除策略

```properties
# ==== 保留策略 ====
log.retention.ms=604800000            # 7 天（时间）
log.retention.bytes=1073741824        # 1GB（大小 per partition）

# ==== 删除流程 ====
# 1. Kafka 启动 Log Retention 线程
# 2. 每 log.retention.check.interval.ms 检查一次（默认 5 分钟）
# 3. 检查每个 Segment 的最后修改时间
# 4. 满足删除条件（时间或大小）→ 标记删除
# 5. 等 log.segment.delete.delay.ms（默认 60 秒）
# 6. 实际删除文件
```

## 📊 Segment 索引优化

### 索引加载优化

```
Kafka 启动时：
  - 加载所有活跃 Segment 的索引到内存
  - 每个 Segment 索引约几 MB
  - 假设 1000 个 Segment → 几 GB 内存（可接受）

查询优化：
  - 二分查找（O(log N)）
  - 直接定位到物理位置
  - 顺序扫描（O(M)）
```

### 索引大小

```
索引项大小：每条 12 字节（offset 8 bytes + position 4 bytes）
索引间隔：4 KB 数据一个索引项
1 GB Segment 的索引：
  - 1 GB / 4 KB = 250,000 个索引项
  - 250,000 × 12 = 3 MB 索引
```

## 🛠️ Segment 实战调优

### 推荐配置

```properties
# 小消息场景
log.segment.bytes=1073741824          # 1GB
log.segment.ms=604800000              # 7 天

# 大消息场景
log.segment.bytes=536870912           # 512MB（避免单 Segment 过大）

# 时间敏感场景
log.segment.ms=3600000               # 1 小时滚动（更快清理）

# 磁盘空间紧张
log.segment.bytes=268435456           # 256MB（更多 Segment，更灵活清理）
```

## 📊 Segment 监控

### 关键指标

```bash
# 查看每个 Segment 大小
ls -lh /data/kafka-logs/orders-0/

# 查看磁盘使用
du -sh /data/kafka-logs/*

# 查看各 Topic Segment 数
kafka-log-dirs.sh --bootstrap-server localhost:9092 \
    --describe --broker-list 1
```

### 监控告警

```yaml
- alert: KafkaSegmentTooLarge
  expr: kafka_log_log_size{topic="orders"} > 5 * 1024 * 1024 * 1024
  for: 30m
  labels:
    severity: warning
  annotations:
    summary: "Kafka Segment 文件超过 5GB"
```

## 🎯 总结

**Segment 快照机制核心要点**：
- ✅ Segment 是 Kafka 日志的基本单位
- ✅ 顺序写盘，append-only
- ✅ 滚动策略：大小 + 时间
- ✅ 稀疏索引（每 4KB 一个）
- ✅ 删除策略：时间或大小
- ⚠️ Segment 大小影响索引效率
- ⚠️ 删除延迟 60 秒（防止误删）

**下一步：** [📜 刷盘机制](/03-persistence/aof) — 数据安全细节