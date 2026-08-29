---
title: 集群规划
date: 2026-08-15  # date-auto-injected
---

# 📐 集群规划

> **集群规划**是 Kafka 实施的第一步，决定了集群的性能、可靠性和成本。本章详解容量评估和资源规划方法。

## 🎯 集群规划步骤

```
1. 需求评估
   - 业务 QPS（读写消息数）
   - 单消息大小
   - 副本数
   - 保留天数
   - SLA（延迟、可用性）

2. 容量计算
   - 磁盘容量
   - 网络带宽
   - CPU / 内存

3. 架构设计
   - Broker 数量
   - Partition 数量
   - 多 AZ 部署

4. 选型决策
   - 硬件规格
   - 软件版本
   - 部署方式
```

## 📊 容量评估

### 1. 消息量评估

```
收集指标：
  - 每天消息总数（按业务 Topic 分别统计）
  - 平均消息大小
  - 峰值 QPS（业务的 2-3 倍）
  - 增长趋势（季度增长 30%？）
  - 写入 / 读取比例

示例：
  - 订单：1 亿条/天，平均 1KB
  - 支付：5000 万条/天，平均 2KB
  - 用户行为：10 亿条/天，平均 500B
  - 总计：15 亿条/天，平均 1KB
```

### 2. 磁盘容量

```
公式：
  磁盘容量 = 消息数 × 单消息大小 × 副本数 × 保留天数 × 安全系数

安全系数 = 1.3（预留 30% 余量）

示例：
  - 15 亿条/天 × 1KB = 150 GB/天
  - 3 副本 = 450 GB/天
  - 7 天保留 = 3.15 TB
  - 1.3 倍 = 4 TB

结论：需要至少 4TB 磁盘
```

### 3. 网络带宽

```
公式：
  网络带宽 = (写入 QPS + 读取 QPS) × 单消息大小 × 副本数

示例：
  - 写入 QPS: 20,000
  - 读取 QPS: 100,000
  - 单消息: 1 KB
  - 副本数: 3

写入带宽 = 20,000 × 1 KB × 3 = 60 MB/s
读取带宽 = 100,000 × 1 KB × 3 = 300 MB/s
总带宽 = 60 + 300 = 360 MB/s

结论：万兆网卡（1 GB/s）足够
```

### 4. Broker 数量

```
公式（按 Broker 容量计算）：
  Broker 数量 = max(
    ceil(磁盘总容量 / 单机磁盘容量),
    ceil(网络总带宽 / 单机网卡带宽),
    ceil(QPS / 单机处理能力)
  )

单机处理能力：
  - NVMe SSD：~100-200 MB/s
  - SATA SSD：~50-100 MB/s
  - HDD：~10-30 MB/s

示例（按磁盘）：
  - 总容量 4TB / 单机 4TB = 1（不够！至少 3 副本）
  - 实际需要 3+ 副本 × 容量 / 容量 = 至少 3 Broker

示例（按网络）：
  - 总带宽 360 MB/s / 单机 1 GB/s = 1（不够）
  - 实际需要 1+ 副本 + 冗余 = 3-5 Broker

示例（按 QPS）：
  - 120,000 QPS / 单机 50,000 = 2.4 → 至少 3 Broker

综合：3-5 Broker
```

## 📊 Partition 数量

### Partition 数评估

```
公式：
  Partition 数 = max(
    目标吞吐 / 单 Partition 吞吐,
    Consumer 数（并行度）
  )

单 Partition 吞吐（经验值）：
  - NVMe SSD：~100 MB/s
  - SATA SSD：~30-50 MB/s
  - HDD：~10-15 MB/s

示例：
  - 目标 300 MB/s
  - 单 Partition（NVMe）：100 MB/s
  - 至少 3 Partition
  - Consumer 数：6
  - 最终：max(3, 6) = 6 Partition
```

### 单 Partition 限制

```
⚠️ 单 Partition 不能无限增长
   - 文件描述符限制
   - Consumer 重平衡慢
   - 副本同步开销

⚠️ Partition 数量过多
   - Controller 压力大
   - 元数据同步慢
   - 选举时间增加

推荐：
  - 单 Broker 不超过 2000 个 Partition
  - 单集群不超过 200,000 个 Partition
```

## 📊 资源规划模板

### 中小型集群（< 100,000 QPS）

```yaml
硬件：
  Broker 数量：3
  单 Broker：
    CPU：8 核
    内存：32 GB
    磁盘：4 TB NVMe SSD
    网络：10 Gbps

Kafka 配置：
  log.retention.hours: 168    # 7 天
  replication.factor: 3
  min.insync.replicas: 2

适用场景：
  - 互联网中型企业
  - 日志 / 事件流
  - 微服务通信
```

### 大型集群（100,000 - 1,000,000 QPS）

```yaml
硬件：
  Broker 数量：5-10
  单 Broker：
    CPU：16-32 核
    内存：64-128 GB
    磁盘：8-16 TB NVMe SSD
    网络：25 Gbps

Kafka 配置：
  log.retention.hours: 72    # 3 天（缩短保留节省空间）
  replication.factor: 3
  min.insync.replicas: 2

适用场景：
  - 大型互联网公司
  - 海量日志
  - 实时计算（Kafka Streams / Flink）
```

### 超大型集群（> 1,000,000 QPS）

```yaml
硬件：
  Broker 数量：10-50
  单 Broker：
    CPU：32+ 核
    内存：128-256 GB
    磁盘：16 TB+ NVMe SSD
    网络：100 Gbps

Kafka 配置：
  log.retention.hours: 24    # 1 天（必须）
  replication.factor: 3
  min.insync.replicas: 2
  多个集群（按业务拆分）

适用场景：
  - 超大型互联网公司
  - 金融交易
  - IoT 海量数据
```

## 📊 架构设计

### 单机房 vs 多机房

```
单机房：
  - 优点：简单、低延迟
  - 缺点：机房故障 = 服务不可用
  - SLA：99.9%

同城双活：
  - 优点：机房级容灾
  - 缺点：跨机房复制延迟
  - SLA：99.95%

异地多活：
  - 优点：地域级容灾
  - 缺点：复杂度高
  - SLA：99.99%
```

### 多 AZ 部署

```yaml
# 推荐：每个 AZ 部署 1+ 个 Broker
# 副本分布在所有 AZ（rack awareness）

# broker 配置
replica.selector.class: org.apache.kafka.common.replica.RackAwareReplicaSelector

# Topic 创建
kafka-topics.sh --create \
    --bootstrap-server kafka:9092 \
    --topic orders \
    --partitions 6 \
    --replication-factor 3
# 副本自动分布在 3 个 AZ
```

## 📊 资源预留

### CPU 预留

```
Kafka Broker CPU 使用：
  - IO 线程：~10%（处理网络 IO）
  - 网络线程：~10%
  - GC 线程：~10%
  - 业务处理：~30%
  - 预留：~40%

推荐 CPU：总核心数 ≥ 16 核（高负载场景）
```

### 内存规划

```
Kafka Broker 内存使用：
  - JVM Heap：4-8 GB（推荐）
  - Page Cache：剩余内存（越大越好）
  - 监控指标：~200 MB

推荐内存：
  - 至少 16 GB
  - 推荐 32-64 GB
  - Page Cache 应 > 实际数据量的 50%
```

### 磁盘规划

```
Kafka Broker 磁盘使用：
  - log.dirs（实际数据）：占大头
  - 系统盘：10-20 GB
  - 监控日志：~10 GB

推荐磁盘：
  - NVMe SSD（推荐）
  - 多磁盘分散（log.dirs 多路径）
  - 监控磁盘使用（> 80% 告警）
```

## 📊 SLA 设计

### 可用性 SLA

```
可用性等级：
  - 99.9%（3 个 9）：年停机时间 < 8.76 小时
  - 99.99%（4 个 9）：年停机时间 < 52 分钟
  - 99.999%（5 个 9）：年停机时间 < 5 分钟

Kafka 默认：
  - 单集群 99.9%
  - 多 AZ 集群 99.95%
  - 多集群 99.99%
```

### 数据可靠性 SLA

```
数据丢失概率：
  - acks=0：可能丢失（不保证）
  - acks=1：Leader 故障可能丢失
  - acks=all + min.insync.replicas=2：基本不丢

推荐配置：
  - acks=all
  - replication.factor=3
  - min.insync.replicas=2
  - 启用幂等性
```

### 性能 SLA

```
延迟 SLA：
  - P50：< 10 ms
  - P99：< 100 ms
  - P999：< 500 ms

吞吐 SLA：
  - 写入：100 MB/s/Broker
  - 读取：200 MB/s/Broker
```

## 🛠️ 实战：完整容量规划

### 1. 需求收集

```
业务方提供：
  - 订单 QPS：50,000
  - 支付 QPS：20,000
  - 用户行为 QPS：200,000
  - 单消息平均大小：1 KB
  - 数据保留：7 天
  - SLA：99.95%
```

### 2. 容量计算

```python
# 总 QPS
total_qps = 50000 + 20000 + 200000 = 270000 QPS

# 峰值 QPS（按 3 倍）
peak_qps = 270000 * 3 = 810000 QPS

# 每天消息数
total_messages = 270000 * 86400 = 23,328,000,000 (23 亿)

# 每天数据量
data_per_day = 23_328_000_000 * 1024 / 1024 / 1024 / 1024 = 22.2 TB/天

# 总磁盘需求（含 3 副本）
total_disk = 22.2 * 3 * 7 = 466 TB

# 网络带宽
write_bandwidth = 810000 * 1KB = 810 MB/s
read_bandwidth = 810000 * 1KB * 3 = 2.4 GB/s (假设读 3 倍于写)
total_bandwidth = write_bandwidth + read_bandwidth = 3.2 GB/s

# Broker 数量
# 按磁盘：466 TB / 16 TB (单机) = 30 Broker
# 按网络：3.2 GB/s / 25 Gbps (单机) ≈ 1.3
# 按 QPS：810000 / 50000 (单机 5 万 QPS) = 16 Broker
# 综合：30 Broker
```

### 3. 集群设计

```
3 副本
30 个 Broker（10 个机架，每个机架 3 个）
多 AZ 部署
NVMe SSD
100 Gbps 网络

Kafka 配置：
  - replication.factor=3
  - min.insync.replicas=2
  - num.partitions = 30 * 100 = 3000（每个 Broker 100 个 Partition）
  - log.retention.hours=168
```

### 4. 容量监控

```yaml
# 关键容量指标
- disk_usage_percent < 80%
- network_bandwidth_used_percent < 70%
- cpu_usage_percent < 80%
- memory_usage_percent < 85%
- consumer_lag < 10000
```

## ⚠️ 常见错误

### 错误 1：低估容量

```
后果：磁盘满、服务不可用
解决：
  1. 预估时加 50% 余量
  2. 监控磁盘使用率
  3. 提前扩容
```

### 错误 2：Partition 过多

```
后果：Controller 压力大、性能下降
解决：
  1. 合理评估 Partition 数
  2. 单 Broker ≤ 2000 Partition
  3. 监控 Partition 数
```

### 错误 3：副本数过少

```
后果：数据可靠性低
解决：
  3 副本是默认推荐
```

### 错误 4：JVM Heap 设置过大

```
后果：GC 时间长
解决：
  1. Heap ≤ 8 GB（推荐 4-6 GB）
  2. 剩余内存给 Page Cache
  3. 使用 G1GC
```

## 🎯 总结

**集群规划核心要点**：
- ✅ 容量评估：消息数 × 大小 × 副本 × 保留
- ✅ 带宽评估：QPS × 大小 × 副本
- ✅ Broker 数量：按磁盘/网络/QPS 取最大
- ✅ Partition 数：按吞吐和并行度
- ✅ 3 副本 + min.insync.replicas=2 是推荐配置
- ✅ NVMe SSD + 万兆网卡
- ⚠️ 容量预估加 50% 余量
- ⚠️ JVM Heap ≤ 8 GB

**下一步：** [⚡ 性能压测](/09-ops/benchmark) — Kafka 性能基线


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
