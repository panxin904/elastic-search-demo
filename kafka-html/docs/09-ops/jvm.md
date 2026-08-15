---
title: JVM 调优
---

# 💾 JVM 调优

> **JVM 调优**是 Kafka Broker 性能的关键。Kafka 对 GC 非常敏感（GC 停顿会导致 ISR 抖动），合理的 JVM 配置至关重要。

## 🎯 Kafka 与 JVM

### Kafka 的内存使用

```
Kafka Broker 内存使用：
  - JVM Heap：Java 对象（少量）
  - Page Cache：OS 文件缓存（大量）
  - Direct Memory：Netty（少量）

JVM Heap 占用：
  - Producer/Consumer 元数据
  - Controller 状态
  - 网络缓冲区
  - 配置信息
  - 仅占总内存的 10-20%

Page Cache 占用：
  - log 文件缓存（最重要）
  - 索引缓存
  - 占用 60-80% 内存
```

### 为什么 Kafka 对 GC 敏感

```
Kafka 单 Broker 维护：
  - 数百万个 Producer/Consumer 连接
  - 数十万 Topic-Partition 元数据
  - 大量网络缓冲区

长 GC 停顿（Stop-The-World）：
  - 客户端请求超时
  - 心跳丢失 → Rebalance
  - Controller 切换
  - ISR 抖动
```

## 📊 JVM Heap 配置

### 堆大小

```bash
# 推荐配置
export KAFKA_HEAP_OPTS="-Xms4G -Xmx4G"

# ⚠️ 不要超过 8 GB
# - 更大的堆 → 更长的 GC 停顿
# - 内存留给 Page Cache 更重要
```

**经验法则**：
```
JVM Heap = 4-6 GB（推荐）
Page Cache = 总内存 - Heap - 其他（应 > 50%）

例如 32 GB 服务器：
  - JVM Heap：4-6 GB
  - 系统 + 其他：~2 GB
  - Page Cache：~24 GB（关键）
```

### 堆大小决策

```
服务器内存   JVM Heap   Page Cache
8 GB         2-3 GB     ~5 GB     （小型集群）
16 GB        4 GB       ~11 GB    （中型集群）
32 GB        6 GB       ~25 GB    （大型集群）
64 GB        6-8 GB     ~55 GB    （超大型集群）

⚠️ Heap > 8 GB 风险：
  - Full GC 停顿可能达 10+ 秒
  - 影响 Kafka 可用性
```

## 📊 垃圾回收器选择

### G1GC（推荐）

```bash
# 推荐配置（Kafka 3.x 默认）
export KAFKA_JVM_PERFORMANCE_OPTS="-server \
    -XX:+UseG1GC \
    -XX:MaxGCPauseMillis=20 \
    -XX:G1HeapRegionSize=16M \
    -XX:InitiatingHeapOccupancyPercent=35 \
    -XX:+DisableExplicitGC"
```

**G1GC 优势**：
- ✅ 可预测的停顿时间（MaxGCPauseMillis）
- ✅ 适合大堆（> 4 GB）
- ✅ 高吞吐
- ✅ 增量回收

### ZGC（超低延迟）

```bash
# 适合超低延迟场景（Kafka 3.x+）
export KAFKA_JVM_PERFORMANCE_OPTS="-server \
    -XX:+UnlockExperimentalVMOptions \
    -XX:+UseZGC \
    -XX:ConcGCThreads=4"
```

**ZGC 优势**：
- ✅ 停顿时间 < 1ms（即使大堆）
- ✅ 适合延迟敏感业务
- ⚠️ Kafka 3.0+ 实验性支持
- ⚠️ CPU 消耗略高

### 其他 GC（不推荐）

```
❌ ParallelGC（吞吐量优先，但停顿时间长）
❌ CMS（已废弃，JDK 14+ 移除）
❌ SerialGC（单线程，性能差）
```

## 📊 G1GC 参数详解

### 核心参数

```bash
# 最大停顿时间（核心目标）
-XX:MaxGCPauseMillis=20          # 目标停顿 20ms（Kafka 推荐）

# 堆区域大小（推荐 16 MB）
-XX:G1HeapRegionSize=16M          # Region 大小

# 堆占用阈值（触发并发 GC）
-XX:InitiatingHeapOccupancyPercent=35  # 35% 占用就开始 GC（Kafka 推荐）

# 并发 GC 线程数（推荐 = CPU 核数 / 4）
-XX:ConcGCThreads=4

# 关闭显式 GC（避免业务代码触发）
-XX:+DisableExplicitGC
```

### 完整配置

```bash
export KAFKA_JVM_PERFORMANCE_OPTS="-server \
    -Xms4G \
    -Xmx4G \
    -XX:MaxGCPauseMillis=20 \
    -XX:+UseG1GC \
    -XX:G1HeapRegionSize=16M \
    -XX:InitiatingHeapOccupancyPercent=35 \
    -XX:ConcGCThreads=4 \
    -XX:+DisableExplicitGC \
    -XX:+ExplicitGCInvokesConcurrent \
    -XX:MaxGCPauseMillis=20"
```

## 📊 GC 监控

### JMX 指标

```bash
# 使用 jstat 监控 GC
jstat -gcutil <pid> 1000

# 输出：
#   S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT
#   0.00   0.00  45.32  28.65  91.83  89.41     12    0.123     2    0.234    0.357
```

字段说明：
- S0/S1：Survivor 区使用率
- E：Eden 区使用率
- O：Old 区使用率
- M：Metaspace 使用率
- YGC：Young GC 次数
- YGCT：Young GC 总时间
- FGC：Full GC 次数
- FGCT：Full GC 总时间
- GCT：GC 总时间

### Prometheus 指标

```promql
# GC 暂停时间（秒）
jvm_gc_pause_seconds_sum
jvm_gc_pause_seconds_count
jvm_gc_pause_seconds_max

# 堆内存使用
jvm_memory_bytes_used{area="heap"}
jvm_memory_bytes_max{area="heap"}

# 各区域使用
jvm_memory_bytes_used{area="eden"}
jvm_memory_bytes_used{area="old"}
```

### GC 日志

```bash
# 启用 GC 日志
export KAFKA_JVM_PERFORMANCE_OPTS="$KAFKA_JVM_PERFORMANCE_OPTS \
    -Xlog:gc*:file=/var/log/kafka/gc.log:time,uptime:filecount=10,filesize=100M"

# 使用 GC 工具分析
gceasy.io 上传分析
```

## 📊 JVM 调优实战

### 场景 1：Full GC 频繁

```
症状：
  - FGC 次数持续增长
  - 单次 Full GC > 1 秒
  - 客户端超时

诊断：
  jstat -gcutil <pid>
  → 看 FGCT 是否持续增长

原因：
  1. Heap 过小
  2. 老年代被占满
  3. 内存泄漏

解决：
  1. 增加 Heap（但不超过 8 GB）
  2. 检查是否有内存泄漏（dump heap）
  3. 优化代码（避免大对象）
```

### 场景 2：Young GC 频繁

```
症状：
  - YGC 次数高（每秒多次）
  - 延迟波动

诊断：
  jstat -gcutil <pid>
  → 看 YGC 频率

原因：
  1. Eden 区太小
  2. 短生命周期对象过多

解决：
  1. 增加 Heap
  2. 调整 G1 Region 大小
  3. 优化对象分配
```

### 场景 3：GC 停顿过长

```
症状：
  - MaxGCPauseMillis > 100ms
  - 客户端 RPC 超时
  - 心跳丢失

诊断：
  GC 日志

解决：
  1. 增加 Heap（> 8 GB 时考虑 ZGC）
  2. 调整 InitiatingHeapOccupancyPercent
  3. 切换到 ZGC（极低延迟）
```

## 📊 Kafka 关键 JVM 配置

### 完整配置示例

```bash
#!/bin/bash
# /opt/kafka/bin/kafka-server-start.sh 中设置

export KAFKA_HEAP_OPTS="-Xms6G -Xmx6G"

export KAFKA_JVM_PERFORMANCE_OPTS="-server \
    -Xms6G \
    -Xmx6G \
    -XX:MaxGCPauseMillis=20 \
    -XX:+UseG1GC \
    -XX:G1HeapRegionSize=16M \
    -XX:InitiatingHeapOccupancyPercent=35 \
    -XX:ConcGCThreads=4 \
    -XX:+DisableExplicitGC \
    -XX:+ExplicitGCInvokesConcurrent \
    -XX:+UseCompressedOops \
    -XX:+UseCompressedClassPointers \
    -XX:MetaspaceSize=96m \
    -XX:MaxMetaspaceSize=256m \
    -XX:ReservedCodeCacheSize=240m \
    -Xlog:gc*,safepoint:file=/var/log/kafka/gc.log:time,uptime:filecount=10,filesize=100M"
```

### 关键参数解释

| 参数 | 含义 | 推荐值 |
|------|------|--------|
| -Xms / -Xmx | JVM 初始/最大堆 | 4-6 GB（建议相等） |
| MaxGCPauseMillis | 最大 GC 停顿 | 20 ms |
| G1HeapRegionSize | G1 Region 大小 | 16 MB |
| InitiatingHeapOccupancyPercent | 触发并发 GC 阈值 | 35% |
| ConcGCThreads | 并发 GC 线程 | CPU 核数 / 4 |
| MetaspaceSize | 元空间初始大小 | 96m |
| MaxMetaspaceSize | 元空间最大 | 256m |

## 📊 JVM 监控告警

### Prometheus 告警规则

```yaml
groups:
  - name: kafka_jvm
    rules:
      # Full GC 频繁
      - alert: KafkaFullGCFrequent
        expr: rate(jvm_gc_pause_seconds_sum{gc="G1 Old Generation"}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Kafka Full GC 频繁"
      
      # GC 停顿过长
      - alert: KafkaLongGCPause
        expr: jvm_gc_pause_seconds_max > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "JVM GC 暂停超过 1 秒"
      
      # 堆内存使用率高
      - alert: KafkaHeapMemoryHigh
        expr: jvm_memory_bytes_used{area="heap"} / jvm_memory_bytes_max{area="heap"} > 0.85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Kafka JVM 堆内存使用超过 85%"
      
      # Old Gen 使用率高
      - alert: KafkaOldGenHigh
        expr: jvm_memory_bytes_used{area="old"} / jvm_memory_bytes_max{area="old"} > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Kafka Old Gen 使用超过 80%"
```

## 📊 不同场景的 JVM 配置

### 高吞吐场景

```bash
# 优化吞吐（中等延迟）
-Xmx8G                          # 较大堆
-XX:MaxGCPauseMillis=50         # 允许较长停顿
-XX:G1HeapRegionSize=32M        # 较大 Region
-XX:InitiatingHeapOccupancyPercent=45
```

### 低延迟场景

```bash
# 优化延迟（中等吞吐）
-Xmx4G                          # 较小堆
-XX:MaxGCPauseMillis=10         # 严格停顿
-XX:+UseZGC                     # 极低延迟 GC
-XX:ConcGCThreads=8
```

### 大内存服务器

```bash
# 64GB+ 内存服务器
-Xmx6G                          # Heap 不要太大
# 剩余内存（50+ GB）给 Page Cache
```

## 🛠️ 实战：JVM 调优步骤

### 步骤 1：基线监控

```bash
# 1. 启用 GC 日志
export KAFKA_JVM_PERFORMANCE_OPTS="-Xlog:gc*:file=/var/log/kafka/gc.log"

# 2. 监控关键指标
jstat -gcutil <pid> 1000        # GC 频率
jstat -gccapacity <pid>         # 堆容量

# 3. 记录基线
- Full GC 次数：~0/小时（理想）
- Young GC 频率：~10 次/分钟
- 平均 GC 停顿：< 20ms
```

### 步骤 2：分析瓶颈

```bash
# 1. GC 日志分析
# 上传 gc.log 到 gceasy.io
# 查看 GC 频率、停顿、堆使用

# 2. JFR 分析（Java Flight Recorder）
jcmd <pid> JFR.start name=kafka profile
jcmd <pid> JFR.dump name=kafka filename=kafka.jfr
# 用 JDK Mission Control 分析

# 3. Heap dump（疑似内存泄漏）
jcmd <pid> GC.heap_dump /tmp/kafka-heap.hprof
# 用 Eclipse MAT 分析
```

### 步骤 3：调优

```bash
# 根据分析调整：
# 1. Full GC 频繁 → 增加 Heap
# 2. Young GC 频繁 → 增加 Heap 或 调整 G1 Region
# 3. 停顿过长 → 降低 MaxGCPauseMillis 或 切换 ZGC
```

### 步骤 4：验证

```bash
# 压测验证调优效果
kafka-producer-perf-test.sh \
    --bootstrap-server localhost:9092 \
    --topic stress-test \
    --num-records 1000000 \
    --record-size 1024 \
    --throughput -1

# 对比调优前后的：
# - 吞吐
# - P50/P99/P999 延迟
# - GC 频率
# - 资源使用
```

## ⚠️ 常见错误

### 错误 1：JVM Heap 设置过大

```
后果：
  - Full GC 停顿 10+ 秒
  - Kafka 可用性下降
  - 客户端超时

解决：
  Heap ≤ 6-8 GB（推荐）
```

### 错误 2：GC 算法选择错误

```
后果：
  - ParallelGC：长 GC 停顿
  - SerialGC：性能差

解决：
  G1GC（推荐）或 ZGC（极低延迟）
```

### 错误 3：忽略 GC 日志

```
后果：
  - 问题发现不及时
  - 调优无依据

解决：
  开启 GC 日志 + 定期分析
```

### 错误 4：Metaspace 设置过小

```
症状：
  - java.lang.OutOfMemoryError: Metaspace
  - 频繁 Full GC

解决：
  -XX:MetaspaceSize=256m
  -XX:MaxMetaspaceSize=512m
```

## 🎯 总结

**JVM 调优核心要点**：
- ✅ Heap 4-6 GB（推荐，不超过 8 GB）
- ✅ G1GC（推荐）或 ZGC（极低延迟）
- ✅ MaxGCPauseMillis=20ms
- ✅ 内存留给 Page Cache（50%+）
- ✅ 开启 GC 日志
- ✅ 监控 GC 指标
- ⚠️ Heap 不要过大
- ⚠️ 关注 Full GC 频率

**下一步：** [🗑️ 日志清理](/09-ops/log-cleanup) — 磁盘管理
