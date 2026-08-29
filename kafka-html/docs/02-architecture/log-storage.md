---
title: 日志存储
date: 2026-08-15  # date-auto-injected
---

# 📜 日志存储

> Kafka 的高性能很大一部分来自**磁盘顺序写** + **Page Cache**。理解日志存储结构对性能调优至关重要。

## 🎯 日志存储结构

```
data/kafka-logs/
├── orders-0/                          ← Partition 0 目录
│   ├── 00000000000000000000.log       ← 第 1 个段文件
│   ├── 00000000000000000000.index     ← 稀疏索引（offset → position）
│   ├── 00000000000000000000.timeindex ← 时间戳索引
│   ├── 0000000000000012345678.log     ← 第 2 个段文件（达到 1GB 滚动）
│   ├── 0000000000000012345678.index
│   └── ...
├── orders-1/
│   ├── 00000000000000000000.log
│   └── ...
└── orders-2/
    └── ...

每个 .log 文件内部：
[m0|m1|m2|m3|m4|...|m999999]  ← 二进制消息内容（顺序追加）
[m1000000|m1000001|...]
```

## 📂 Segment 文件详解

### Segment 组成

```
Segment N
├── .log       消息内容（顺序追加，最大 1GB）
├── .index     偏移量到物理位置的索引（稀疏索引）
└── .timeindex 时间戳到偏移量的索引（按时间查询用）
```

### Segment 滚动策略

```properties
# 满足任一条件即触发滚动
log.segment.bytes=1073741824      # 1GB
log.segment.ms=604800000          # 7 天
log.roll.hours=168                # 兼容旧版本（默认 7 天）

# 滚动后：
#  - 关闭当前 .log 文件
#  - 创建新的 .log 文件（offset 起始）
#  - 旧的 Segment 等待过期删除
```

### 索引文件结构

```
.index 文件（稀疏索引）：

offset    physical_position
  0          0          ← m0 物理位置
  100        4096       ← m100 物理位置
  200        8192       ← m200 物理位置
  ...
  
每隔 log.index.interval.bytes（默认 4096 字节）一个索引项

查询 offset=150：
  1. 加载 .index 到内存
  2. 二分查找找到 100（position=4096）
  3. 从 .log 文件的 4096 位置开始顺序扫描
  4. 找到 offset=150 的消息
```

## 🚀 高性能写盘机制

### 顺序写 vs 随机写

```
随机写（传统数据库）：
  - 磁头需要移动
  - 典型延迟：5-10ms
  - SSD：100-200μs

顺序写（Kafka）：
  - 磁头不移动（或 SSD 无寻道时间）
  - 典型延迟：机械硬盘 100-200μs
  - SSD：20-50μs
  - 接近内存速度（受限于磁盘 IO）

Kafka 优势：
  - 顺序写 + Page Cache ≈ 内存 IO 性能
  - 即使在 HDD 上也能达到 100MB/s+
```

### Page Cache 优化

```
写入流程：
  Producer → Broker
  ↓
  Kafka 写入 Page Cache（OS 文件缓存）
  ↓
  立即返回 ack（fsync 异步）
  ↓
  后台线程定期 flush 到磁盘

读取流程：
  Consumer 请求
  ↓
  Kafka 从 Page Cache 读取（命中）
  ↓
  立即返回（不读磁盘）
  
命中率：
  - 生产环境 Page Cache 命中率 > 90%
  - 几乎所有读都从内存命中
```

### fsync 策略

```properties
# log.flush.interval.messages=10000    # 每 10000 条消息 fsync 一次
# log.flush.interval.ms=1000          # 每 1 秒 fsync 一次
# 默认不主动 fsync，依赖 OS 后台刷盘

# 风险：崩溃时可能丢失最后 N 条消息（Page Cache 中）
# 解决：生产环境建议 acks=all + replication.factor>=3
```

## 📊 文件格式

### 消息二进制格式

```
消息 V2 格式（默认）：

┌─────────────────────────────────────────────────┐
│ 8 bytes  │  offset (int64)                       │
├──────────┼──────────────────────────────────────┤
│ 4 bytes  │  message size (int32)                │
├──────────┼──────────────────────────────────────┤
│ 1 byte   │  crc32 (int8)                        │
├──────────┼──────────────────────────────────────┤
│ 1 byte   │  attributes (1 byte)                 │
├──────────┼──────────────────────────────────────┤
│ N bytes  │  key (varint length + bytes)         │
├──────────┼──────────────────────────────────────┤
│ N bytes  │  value (varint length + bytes)       │
├──────────┼──────────────────────────────────────┤
│ N bytes  │  headers (varint length + bytes)     │
└─────────────────────────────────────────────────┘
```

### 压缩（Compression）

```java
Properties props = new Properties();
props.put(ProducerConfig.COMPRESSION_TYPE_CONFIG, "lz4");  // 或 gzip, snappy, zstd
```

```
压缩优势：
  - 网络传输减少
  - 磁盘 IO 减少
  - 存储空间减少

压缩算法对比：
  - none：无压缩（最快，体积最大）
  - gzip：压缩率最高（最慢）
  - snappy：平衡（推荐）
  - lz4：解压快（推荐）
  - zstd：压缩率好 + 速度（Kafka 2.1+ 推荐）
```

## 🗑️ 日志删除策略

### 删除策略

```properties
# 默认 7 天过期
log.retention.hours=168

# 或基于大小（推荐）
log.retention.bytes=1073741824  # 1GB（per partition）

# 优先级：retention.ms > retention.minutes > retention.hours
```

### 删除流程

```
1. Kafka 启动一个日志删除线程（Log Retention Thread）
2. 定期扫描所有 .log 文件
3. 判断条件：
   - 文件最后修改时间 + retention.ms < 当前时间 → 删除
   - 文件总大小 + 当前总大小 > retention.bytes → 删除最早
4. 删除文件 + 索引

⚠️ 删除策略：
  - delete（默认）：物理删除
  - compact：日志压缩（保留每个 key 的最新值）
```

### Compact 策略

```
适用场景：
  - 数据有"最终状态"（如用户配置、设备状态）
  - 不需要保留历史修改

原理：
  - 后台线程定期扫描
  - 对每个 key，只保留最新的消息
  - 删除旧的消息

示例：
  用户: A 的状态变更：
    offset=100: user:A = {name: "tom", age: 25}
    offset=200: user:A = {name: "tom", age: 26}
    offset=300: user:A = {name: "tom", age: 27}
    
  Compact 后：
    offset=300: user:A = {name: "tom", age: 27}
```

## 📊 磁盘 IO 性能优化

### 性能指标参考

```
单机 Kafka 性能（HDD）：
  - 生产：100-200 MB/s
  - 消费：200-400 MB/s
  - 延迟：5-10 ms

单机 Kafka 性能（NVMe SSD）：
  - 生产：500-1000 MB/s
  - 消费：1000+ MB/s
  - 延迟：1-2 ms
```

### 优化建议

```
✅ 用 SSD 或 NVMe
   - 顺序写 + SSD = 接近内存性能
   - 推荐 NVMe SSD（3000 MB/s+）

✅ 多磁盘
   - 配置多个 log.dirs
   - RAID 0（性能优先）或 RAID 10（安全优先）

✅ 调整 Page Cache
   - 增加服务器内存
   - 至少 8GB Page Cache

✅ 压缩
   - 启用 zstd / lz4
   - 减少磁盘 IO 和网络带宽

✅ 批量写入
   - linger.ms=10
   - batch.size=64KB
   - 减少磁盘 IO 次数
```

## 🔧 关键配置

```properties
# ==== 日志分段 ====
log.segment.bytes=1073741824           # 1GB
log.segment.ms=604800000               # 7 天
log.index.interval.bytes=4096          # 索引粒度

# ==== 保留策略 ====
log.retention.hours=168                # 7 天
log.retention.bytes=1073741824         # 1GB per partition
log.cleanup.policy=delete              # delete / compact / delete,compact

# ==== 刷盘策略 ====
log.flush.interval.messages=10000      # 每 10000 条消息 fsync
log.flush.interval.ms=1000             # 每 1 秒 fsync
# 一般不需要主动 fsync（依赖 OS）

# ==== 索引 ====
log.index.size.max.bytes=10485760      # 索引文件最大 10MB
log.segment.index.bytes=10485760       # 同上（兼容）

# ==== Page Cache ====
# Kafka 不直接配置 Page Cache
# 由 OS 自动管理（/proc/sys/vm/dirty_*）
```

## ⚠️ 常见问题

### 问题 1：磁盘 IO 抖动

```
现象：写入延迟突增
原因：磁盘后台操作（rebalance、compaction）
解决：
  1. 错峰执行 compaction（业务低峰期）
  2. 增加磁盘带宽（NVMe RAID）
  3. 调小 log.segment.bytes（更频繁滚动）
```

### 问题 2：磁盘满了

```
现象：Producer 报 No space left on device
解决：
  1. 扩容磁盘
  2. 减少 retention 时间
  3. 启用 compact 策略
  4. 多 log.dirs 分摊
```

### 问题 3：Page Cache 命中率低

```
现象：Consumer 读取慢（频繁读盘）
原因：
  1. 服务器内存不够
  2. 多个 Kafka 实例抢占 Page Cache
解决：
  1. 增加内存
  2. 隔离 Broker（每个 Broker 独占内存）
  3. 减少 log.retention（更早释放 Page Cache）
```

## 🎯 总结

**日志存储核心要点**：
- ✅ 分段（Segment）顺序写盘
- ✅ Page Cache 加速读写
- ✅ 稀疏索引快速定位
- ✅ 压缩减少 IO 和存储
- ✅ 顺序写 ≈ 内存性能
- ⚠️ 推荐 NVMe SSD + 大内存
- ⚠️ retention 策略影响磁盘占用

**下一步：** [🚀 零拷贝原理](/02-architecture/zero-copy) — 高吞吐核心


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
