---
title: 消息积压
---

# 📦 消息积压

> **消息积压（Lag）**是 Kafka 生产环境最常见的问题之一。本章详解积压原因、监控和处理方案。

## 🎯 什么是消息积压？

```
积压 = Consumer 消费速度跟不上 Producer 生产速度

表现：
  - Consumer Group 的 lag 持续增长
  - 业务处理延迟增加
  - 磁盘占用增加（Kafka 保留消息）
  - 最终可能导致磁盘满
```

### 关键指标

```
Lag = LEO（Log End Offset）- Consumer Offset

LEO = 当前 Partition 最新消息的 Offset
Consumer Offset = Consumer 已消费的 Offset

Lag = LEO - Consumer Offset = 还没消费的消息数
```

## 📊 积压原因分析

### 原因 1：Consumer 数量不够

```
场景：
  - 12 个 Partition
  - 只有 3 个 Consumer
  - 最多并行 3 个 Partition

问题：
  - 9 个 Partition 的消息堆积
  - lag 持续增长
```

### 原因 2：Consumer 处理慢

```
场景：
  - Consumer 处理一条消息 100ms
  - 每秒只能处理 10 条
  - Producer 每秒发送 1000 条

问题：
  - lag 每秒增长 990 条
```

### 原因 3：Consumer 故障

```
场景：
  - Consumer 崩溃
  - 重新加入需要 Rebalance
  - 期间消息堆积
```

### 原因 4：突发流量

```
场景：
  - 平时每秒 100 条
  - 促销活动每秒 10000 条
  - Consumer 跟不上
```

### 原因 5：下游系统慢

```
场景：
  - Consumer 处理完消息后写数据库
  - 数据库压力大（慢 SQL、锁竞争）
  - Consumer 处理阻塞
```

## 🔧 监控积压

### 使用 kafka-consumer-groups.sh

```bash
# 查看 Lag
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor

# 输出：
# GROUP            TOPIC    PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG    CONSUMER-ID
# order-processor  orders   0          10000           15000           5000   consumer-1-...
# order-processor  orders   1          8000            12000           4000   consumer-1-...
# order-processor  orders   2          6000            9000            3000   consumer-2-...
```

### 使用 kafka_exporter（推荐）

```bash
# 部署 kafka_exporter
docker run -d --name kafka-exporter \
    -p 9308:9308 \
    bitnami/kafka-exporter \
    --kafka.server=localhost:9092
```

```yaml
# Prometheus 配置
scrape_configs:
  - job_name: kafka
    static_configs:
      - targets: ['localhost:9308']
```

```promql
# Lag 总量
sum(kafka_consumergroup_lag) by (consumergroup, topic)

# 单个 Partition Lag
kafka_consumergroup_lag{consumergroup="order-processor",partition="0"}
```

### Grafana 告警

```yaml
# 告警规则
groups:
  - name: kafka_lag
    rules:
      - alert: KafkaConsumerLag
        expr: sum(kafka_consumergroup_lag) by (consumergroup) > 10000
        for: 5m
        annotations:
          summary: "Consumer group {{ $labels.consumergroup }} lag too high"
```

## 🔧 处理积压的方案

### 方案 1：临时扩容 Consumer

```bash
# 1. 增加 Consumer 实例（最多到 Partition 数）
# 原来 3 个 Consumer，扩展到 6 个
# 触发 Rebalance，自动重新分配 Partition

# 2. 监控 Lag 变化
watch -n 5 "kafka-consumer-groups.sh --describe --bootstrap-server localhost:9092 --group order-processor"
```

**优点**：快速见效
**缺点**：临时方案，业务逻辑慢则无解

### 方案 2：增加 Partition 数

```bash
# 增加 Partition（提升并行度）
kafka-topics.sh --alter \
    --bootstrap-server localhost:9092 \
    --topic orders \
    --partitions 12  # 从 6 增加到 12

# ⚠️ 已有消息的 hash(key) % 6 仍然有效
# ⚠️ 新消息按 hash(key) % 12 路由
# ⚠️ 同 Key 顺序可能破坏
```

**注意**：增加 Partition 是不可逆操作，需谨慎

### 方案 3：批量消费优化

```java
// 增加每次 poll 的记录数
props.put(ConsumerConfig.MAX_POLL_RECORDS_CONFIG, 1000);  // 默认 500

// 增加批量处理大小
@KafkaListener(topics = "orders", containerFactory = "batchFactory")
public void consumeBatch(List<OrderEvent> events, Acknowledgment ack) {
    // 批量处理（一次处理 1000 条）
    for (OrderEvent event : events) {
        processOrder(event);
    }
    ack.acknowledge();  // 一次性提交
}
```

**优点**：减少网络和提交开销
**缺点**：单条失败影响整批

### 方案 4：异步处理

```java
@KafkaListener(topics = "orders", concurrency = "3")
public void consume(OrderEvent event, Acknowledgment ack) {
    // 1. 提交到线程池（不阻塞 Consumer）
    executor.submit(() -> {
        try {
            processOrder(event);
        } catch (Exception e) {
            log.error("Process failed", e);
            deadLetterQueue.send(event);
        }
    });
    
    // 2. 立即 ack（不等待处理）
    ack.acknowledge();
}

private final ExecutorService executor = Executors.newFixedThreadPool(50);
```

**优点**：Consumer 不阻塞
**缺点**：处理失败时已 ack（需 Outbox 兜底）

### 方案 5：优化消费逻辑

```java
// 1. 优化数据库操作
@KafkaListener(topics = "orders")
public void consume(OrderEvent event, Acknowledgment ack) {
    // ❌ 单条提交
    orderRepository.save(order);
    
    // ✅ 批量提交
    batchOrders.add(order);
    if (batchOrders.size() >= 100) {
        orderRepository.saveAll(batchOrders);
        batchOrders.clear();
    }
    ack.acknowledge();
}

// 2. 减少不必要的 IO
// ❌ 每次查询数据库
Order order = orderRepository.findById(event.getOrderId());

// ✅ 本地缓存（短 TTL）
Order cachedOrder = localCache.get(event.getOrderId());
if (cachedOrder == null) {
    cachedOrder = orderRepository.findById(event.getOrderId());
    localCache.put(event.getOrderId(), cachedOrder, 30, TimeUnit.SECONDS);
}

// 3. 异步 IO
// ❌ 同步调用外部 API
paymentService.verify(event);

// ✅ 异步调用
CompletableFuture.supplyAsync(() -> paymentService.verify(event));
```

### 方案 6：动态调整 Partition 数量

```bash
# 实时监控 + 自动扩容

# 1. 检查 Lag
LAG=$(kafka-consumer-groups.sh --describe --bootstrap-server localhost:9092 \
    --group order-processor | awk '{sum+=$5} END {print sum}')

# 2. 如果 Lag > 10000，扩容 Consumer
if [ "$LAG" -gt 10000 ]; then
    kubectl scale deployment order-consumer --replicas=6
    echo "Scaled to 6 consumers"
fi
```

## 🔧 实战：完整的积压处理流程

### 1. 发现积压（告警）

```
Grafana 告警：
  KafkaConsumerLag
    order-processor  lag = 50000（持续 10 分钟）

PagerDuty → oncall 工程师
```

### 2. 排查原因

```bash
# 1. 查看哪个 Partition 积压最严重
kafka-consumer-groups.sh --describe \
    --bootstrap-server localhost:9092 \
    --group order-processor

# 发现：所有 6 个 Partition 都有积压

# 2. 检查 Consumer 状态
# 应用日志：发现 consumer 处理慢（数据库慢查询）

# 3. 进一步排查
# 数据库慢日志：发现 order 表有个索引缺失
```

### 3. 短期措施

```bash
# 1. 扩容 Consumer（4 → 8）
kubectl scale deployment order-consumer --replicas=8

# 2. 监控 Lag 下降
watch -n 5 "kafka-consumer-groups.sh --describe --bootstrap-server localhost:9092 --group order-processor"
```

### 4. 长期方案

```sql
-- 1. 添加索引
CREATE INDEX idx_order_status ON orders(status);

-- 2. 优化慢查询
ALTER TABLE orders ADD INDEX idx_created_at (created_at);
```

```java
// 3. 优化 Consumer 代码
@KafkaListener(topics = "orders", concurrency = "6")
public void consume(OrderEvent event, Acknowledgment ack) {
    // 批量提交（每 100 条 commit 一次）
    batchProcess(event);
    ack.acknowledge();
}
```

### 5. 预防措施

```yaml
# 1. 容量规划
预计 QPS: 10,000
每条处理时间: 10ms
需要 Consumer 数: 10000 / (1000/10) = 100
需要 Partition 数: 100（至少 100 个 Partition 才能 100 个并行 Consumer）
需要 Broker 数: 5（每 Broker 30+ Partition）

# 2. 监控告警
- Lag > 10000 持续 5 分钟 → 告警
- Lag 增长率 > 100 条/秒 → 告警
- Consumer 数 < Partition 数 → 告警
```

## 🔧 积压恢复策略

### 重置 Offset（慎用）

```bash
# 场景：积压大量历史数据，需要跳过

# 重置到最新（跳过所有历史）
kafka-consumer-groups.sh --reset-offsets \
    --bootstrap-server localhost:9092 \
    --group order-processor \
    --topic orders \
    --to-latest \
    --execute

# ⚠️ 风险：丢失历史消息
```

### 迁移到独立 Topic

```java
// 1. 创建新 Topic（更高吞吐）
// 2. Producer 改用新 Topic
// 3. Consumer 消费完旧 Topic 后下线
```

### 压缩历史消息

```bash
# 使用 compact 策略
kafka-topics.sh --create --bootstrap-server localhost:9092 \
    --topic orders-compact \
    --partitions 6 --replication-factor 2 \
    --config cleanup.policy=compact

# 适用场景：每个 Key 只关心最新值
```

## 📊 积压处理清单

```
✅ 预防措施：
  - 合理规划 Partition 数
  - Consumer 数 = Partition 数（最佳）
  - 监控 Lag 和增长趋势
  - 容量评估和压测

✅ 应急措施：
  - 扩容 Consumer（短期）
  - 增加 Partition（中期）
  - 优化消费逻辑（长期）

✅ 工具：
  - kafka-consumer-groups.sh（CLI）
  - kafka_exporter（监控）
  - Grafana Dashboard
  - 自动化扩容脚本
```

## ⚠️ 常见问题

### 问题 1：Consumer 扩容后 Lag 不下降

```
原因：
  1. 扩容后 Consumer 还在 Rebalance
  2. Consumer 处理能力受限（IO/DB）
  3. Consumer 数已等于 Partition 数
解决：
  1. 等待 Rebalance 完成（几秒）
  2. 增加 Partition 数
  3. 优化消费逻辑
```

### 问题 2：磁盘满导致 Kafka 不可用

```
原因：积压消息占满磁盘
解决：
  1. 扩容磁盘
  2. 减少 retention.ms
  3. 清理历史消息
```

### 问题 3：Consumer 一直 GC 导致 Lag

```
原因：长 GC 导致心跳超时
解决：
  1. 优化 JVM（-Xmx、GC 算法）
  2. 增加 session.timeout.ms
```

## 🎯 总结

**消息积压核心要点**：
- ✅ Lag = LEO - Consumer Offset
- ✅ 积压原因：Consumer 不够 / 处理慢 / 突发流量
- ✅ 短期方案：扩容 Consumer
- ✅ 长期方案：增加 Partition + 优化逻辑
- ✅ 监控告警至关重要
- ⚠️ 增加 Partition 不可逆
- ⚠️ 重置 Offset 有数据丢失风险

**下一步：** [🔌 Kafka Connect](/08-enterprise/connect) — 数据集成
