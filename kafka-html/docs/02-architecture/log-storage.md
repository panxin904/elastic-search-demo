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

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Kafka Log Segment 索引</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">稀疏索引 · offset → position · O(log n) 二分查找 · index.interval.bytes</text>

  <!-- 物理文件布局 -->
  <g>
    <text x="60" y="95" font-size="13" font-weight="700" fill="#1e293b">partition-0 目录</text>

    <!-- log 文件 -->
    <rect class="at-hover-card" x="40" y="110" width="400" height="50" rx="4" fill="#fef3c7" stroke="#f59e0b" stroke-width="2"/>
    <text x="60" y="130" font-size="11" font-weight="700" fill="#92400e">00000000000000000000.log</text>
    <text x="60" y="148" font-size="10" fill="#475569">真实数据：message1, message2, ...</text>

    <!-- index 文件 -->
    <rect class="at-hover-card" x="40" y="170" width="400" height="50" rx="4" fill="#dbeafe" stroke="#3b82f6" stroke-width="2"/>
    <text x="60" y="190" font-size="11" font-weight="700" fill="#1e40af">00000000000000000000.index</text>
    <text x="60" y="208" font-size="10" fill="#475569">稀疏索引：每隔 N bytes 记录一个 offset→position 映射</text>

    <!-- timeindex 文件 -->
    <rect class="at-hover-card" x="40" y="230" width="400" height="40" rx="4" fill="#d1fae5" stroke="#10b981" stroke-width="2"/>
    <text x="60" y="248" font-size="11" font-weight="700" fill="#065f46">00000000000000000000.timeindex</text>
    <text x="60" y="263" font-size="10" fill="#475569">timestamp → offset 映射（用于按时间消费）</text>

    <!-- 注意 -->
    <text x="60" y="295" font-size="10" fill="#dc2626" font-weight="700">⚠️ 索引文件加载到内存（mmap），log 文件按需 mmap 部分页</text>
  </g>

  <!-- 索引查找流程 -->
  <g>
    <text x="60" y="325" font-size="13" font-weight="700" fill="#1e293b">offset=5000 查找示例</text>

    <!-- log 内容示意 -->
    <rect class="at-hover-card" x="40" y="345" width="525" height="60" rx="6" fill="#f1f5f9" stroke="#94a3b8"/>
    <text x="60" y="365" font-size="10" fill="#475569">index.interval.bytes=4096 · 每 4KB 写一条索引</text>

    <g font-family="monospace" font-size="9">
      <rect class="at-hover-card" x="60" y="375" width="100" height="20" rx="3" fill="#dbeafe" stroke="#3b82f6"/>
      <text x="110" y="389" text-anchor="middle" fill="#1e40af">offset 0 → 0</text>

      <rect class="at-hover-card" x="170" y="375" width="100" height="20" rx="3" fill="#dbeafe" stroke="#3b82f6"/>
      <text x="220" y="389" text-anchor="middle" fill="#1e40af">offset 100 → 4096</text>

      <rect class="at-hover-card" x="280" y="375" width="100" height="20" rx="3" fill="#fef3c7" stroke="#f59e0b"/>
      <text x="330" y="389" text-anchor="middle" fill="#92400e" font-weight="700">offset 5000 → 204800</text>

      <rect class="at-hover-card" x="390" y="375" width="155" height="20" rx="3" fill="#dbeafe" stroke="#3b82f6"/>
      <text x="467" y="389" text-anchor="middle" fill="#1e40af">offset 5102 → 208896</text>
    </g>

    <!-- 箭头 -->
    <line x1="330" y1="395" x2="330" y2="420" stroke="#10b981" stroke-width="2" marker-end="url(#arr)"/>
  </g>

  <!-- 关键说明 -->
  <g>
    <rect class="at-hover-card" x="40" y="425" width="525" height="45" rx="6" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="60" y="447" font-size="11" font-weight="700" fill="#1e40af">查找流程：</text>
    <text x="60" y="463" font-size="11" fill="#1e40af">二分索引（O(log n)）→ 找到 ≤5000 的最大 offset → 从 position 开始顺序扫描</text>
  </g>
</svg>
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

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600" >Kafka PageCache + 稀疏索引</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">顺序写 + OS PageCache · offset → position 映射</text>

  <!-- PageCache 写入流程 -->
  <g>
    <text x="60" y="90" font-size="13" font-weight="700" fill="#1e293b">① 写入流程：Producer → PageCache → 异步刷盘</text>

    <rect class="at-hover-card" x="40" y="105" width="520" height="100" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <rect class="at-hover-card" x="55" y="120" width="115" height="70" rx="4" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="112" y="140" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">Producer</text>
    <text x="112" y="158" text-anchor="middle" font-size="9" font-family="monospace" fill="#1e293b">append</text>
    <text x="112" y="174" text-anchor="middle" font-size="9" fill="#475569">顺序写</text>

    <path d="M 170 155 L 200 155" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="200" y="120" width="115" height="70" rx="4" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="257" y="140" text-anchor="middle" font-size="11" font-weight="700" fill="#065f46">JVM 堆</text>
    <text x="257" y="158" text-anchor="middle" font-size="9" fill="#475569">ByteBuffer</text>
    <text x="257" y="174" text-anchor="middle" font-size="9" fill="#475569">memory mapped</text>

    <path d="M 315 155 L 345 155" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="345" y="120" width="115" height="70" rx="4" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="402" y="140" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">OS PageCache</text>
    <text x="402" y="158" text-anchor="middle" font-size="9" fill="#475569">4KB 页面</text>
    <text x="402" y="174" text-anchor="middle" font-size="9" fill="#475569">内核缓冲</text>

    <path d="M 460 155 L 490 155" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)" stroke-dasharray="3,2"/>

    <rect class="at-hover-card" x="490" y="120" width="60" height="70" rx="4" fill="#1e293b"/>
    <text x="520" y="140" text-anchor="middle" font-size="10" font-weight="700" fill="#a7f3d0">磁盘</text>
    <text x="520" y="158" text-anchor="middle" font-size="9" fill="#a7f3d0">async</text>
    <text x="520" y="174" text-anchor="middle" font-size="9" fill="#a7f3d0">fsync</text>

    <text x="55" y="195" font-size="9" fill="#475569">⚡ 性能：Producer 写仅 0.0001ms，OS 后续异步刷盘（fsync 由 OS 策略决定）</text>
  </g>

  <!-- 稀疏索引 -->
  <g>
    <text x="60" y="225" font-size="13" font-weight="700" fill="#1e293b">② Kafka 稀疏索引（offset → byte position）</text>

    <rect class="at-hover-card" x="40" y="240" width="520" height="155" rx="6" fill="#f1f5f9" stroke="#64748b" stroke-width="1.5"/>

    <!-- 索引条目 -->
    <rect class="at-hover-card" x="55" y="258" width="490" height="50" rx="3" fill="#dbeafe" stroke="#3b82f6"/>
    <text x="70" y="278" font-size="10" font-weight="700" fill="#1e40af">index (稀疏索引)</text>
    <text x="70" y="296" font-size="9" font-family="monospace" fill="#1e293b">offset 0    → position 0</text>
    <text x="240" y="296" font-size="9" font-family="monospace" fill="#1e293b">offset 1000 → position 16384</text>
    <text x="430" y="296" font-size="9" font-family="monospace" fill="#1e293b">offset 2000 → position 32768</text>

    <path d="M 300 308 L 300 330" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arr)"/>

    <!-- log 文件 -->
    <text x="70" y="345" font-size="10" font-weight="700" fill="#1e293b">log 文件（连续字节）</text>

    <rect class="at-hover-card" x="70" y="350" width="100" height="32" rx="2" fill="#dcfce7" stroke="#10b981"/>
    <text x="120" y="370" text-anchor="middle" font-size="9" font-weight="700" fill="#065f46">msg 0-999</text>

    <rect class="at-hover-card" x="180" y="350" width="100" height="32" rx="2" fill="#dcfce7" stroke="#10b981"/>
    <text x="230" y="370" text-anchor="middle" font-size="9" font-weight="700" fill="#065f46">msg 1000-1999</text>

    <rect class="at-hover-card" x="290" y="350" width="100" height="32" rx="2" fill="#dcfce7" stroke="#10b981"/>
    <text x="340" y="370" text-anchor="middle" font-size="9" font-weight="700" fill="#065f46">msg 2000-2999</text>

    <rect class="at-hover-card" x="400" y="350" width="155" height="32" rx="2" fill="#dcfce7" stroke="#10b981"/>
    <text x="477" y="370" text-anchor="middle" font-size="9" font-weight="700" fill="#065f46">msg 3000+ (未索引)</text>

    <text x="55" y="390" font-size="9" fill="#475569">查找 offset 1500 → 二分索引 → 落在 offset 1000 → 线性扫描到 1500（2 步 O(log N + N)）</text>
  </g>

  <!-- 性能优势 -->
  <g>
    <text x="60" y="415" font-size="13" font-weight="700" fill="#1e293b">③ 为什么 Kafka 这么快？</text>

    <rect class="at-hover-card" x="40" y="428" width="520" height="40" rx="4" fill="#fef9c3" stroke="#facc15"/>
    <text x="300" y="446" text-anchor="middle" font-size="10" fill="#854d0e">顺序写 + 零拷贝 + PageCache + 稀疏索引 = 单机百万级 TPS</text>
  </g>
</svg>
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
