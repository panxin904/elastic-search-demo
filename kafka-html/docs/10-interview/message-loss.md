---
title: 消息丢失解决方案
---

# 🚨 消息丢失解决方案

> 消息丢失是 Kafka 生产环境的**最大风险**之一。本章详解消息丢失的所有场景和解决方案。

## 🎯 消息丢失场景总览

```
1. Producer 端丢失
   - 网络丢失
   - acks 不当
   - 异步发送未感知

2. Broker 端丢失
   - Leader 故障
   - 副本同步不足
   - 磁盘损坏

3. Consumer 端丢失
   - 自动提交后崩溃
   - 处理失败未重试

4. 系统性丢失
   - 数据中心故障
   - 配置错误
```

## 🔧 Producer 端消息丢失

### 场景 1：acks=0

```java
// ❌ 错误配置：不等待 Broker 确认
Properties props = new Properties();
props.put(ProducerConfig.ACKS_CONFIG, "0");  // 危险！

KafkaProducer<String, String> producer = new KafkaProducer<>(props);
producer.send(new ProducerRecord<>("orders", "key", "value"));
// 不等响应就返回，消息可能丢失
```

```
风险：
  - Producer 发送后立即返回
  - 如果网络丢包或 Broker 故障，消息丢失
  - 没有任何保障

解决：
  - 永远不要使用 acks=0
```

### 场景 2：acks=1 + Leader 故障

```java
// ⚠️ 有风险配置：等 Leader 写入但不等副本
props.put(ProducerConfig.ACKS_CONFIG, "1");

// 风险：
// T1: Leader 写入 log
// T2: Leader 返回 ack
// T3: Leader 故障
// T4: Follower 被选为 Leader（未同步最新数据）
// T5: msg 丢失！
```

```
风险：
  - Leader 写入后立即返回 ack
  - Follower 还在异步同步
  - 如果此时 Leader 故障，msg 丢失

解决：
  - 使用 acks=all + min.insync.replicas=2
```

### 场景 3：异步发送未处理异常

```java
// ❌ 异步发送丢失异常
producer.send(record);  // 不处理回调
// 如果失败，异常被吞掉，消息丢失

// ✅ 正确：处理回调
producer.send(record, (metadata, exception) -> {
    if (exception != null) {
        log.error("Send failed", exception);
        // 重试 / 死信 / 告警
    }
});
```

### ✅ Producer 端完整解决方案

```java
Properties props = new Properties();
props.put(ProducerConfig.ACKS_CONFIG, "all");
props.put(ProducerConfig.RETRIES_CONFIG, Integer.MAX_VALUE);
props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, true);
props.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);
props.put(ProducerConfig.DELIVERY_TIMEOUT_MS_CONFIG, 120000);
props.put(ProducerConfig.REQUEST_TIMEOUT_MS_CONFIG, 30000);

KafkaProducer<String, String> producer = new KafkaProducer<>(props);

// 同步发送 + 回调
producer.send(record, new Callback() {
    @Override
    public void onCompletion(RecordMetadata metadata, Exception exception) {
        if (exception != null) {
            // 错误处理：记录、重试、告警
            log.error("Send failed", exception);
            deadLetterQueue.send(record, exception);
            alert();
        }
    }
});
```

## 🔧 Broker 端消息丢失

### 场景 1：Leader 故障 + 副本不足

```
配置：
  - replication.factor=1（单副本）
  - Leader 故障 → 数据丢失

风险：
  - 单副本 = 没有冗余
  - Leader 故障 = 数据丢失

解决：
  - replication.factor=3
  - min.insync.replicas=2
  - acks=all
```

### 场景 2：min.insync.replicas=1

```
配置：
  - replication.factor=3
  - min.insync.replicas=1
  - Leader 写入即返回成功

风险：
  - 仅 Leader 写入，其他副本异步同步
  - Leader 故障时，Follower 可能没有数据
  - 数据丢失

解决：
  - min.insync.replicas=2
  - acks=all
  - 强制等待至少 2 个副本写入
```

### 场景 3：unclean.leader.election=true

```
配置：
  - unclean.leader.election.enable=true
  - 所有 ISR 都不可用时，从 OSR 选 Leader

风险：
  - OSR 数据落后 ISR
  - 新 Leader 数据可能不是最新的
  - 数据丢失

解决：
  - unclean.leader.election.enable=false（默认）
  - 宁愿分区不可用也不丢数据
```

### ✅ Broker 端完整解决方案

```properties
# ==== 推荐配置 ====
replication.factor=3              # 3 副本
min.insync.replicas=2              # 至少 2 个副本写入
unclean.leader.election.enable=false # 禁止从 OSR 选 Leader
default.replication.factor=3       # Topic 默认副本数
acks=all                           # Producer 端配置
```

## 🔧 Consumer 端消息丢失

### 场景 1：自动提交后崩溃

```
配置：
  - enable.auto.commit=true
  - auto.commit.interval.ms=5000

时间线：
  T1   Consumer poll() 拉取 msg-1, msg-2
  T2   Consumer 处理 msg-1
  T3   5 秒后自动提交 offset=2
  T4   Consumer 处理 msg-2 前崩溃
  T5   Consumer 重启，从 offset=2 消费
  T6   msg-2 丢失（未处理但已提交）

风险：
  - 自动提交 + 业务处理是独立的
  - 提交后崩溃 = 业务未完成 = 数据丢失

解决：
  - 关闭自动提交
  - 处理完手动提交
```

### 场景 2：处理失败未重试

```java
// ❌ 错误：处理失败不重试
@KafkaListener(topics = "orders")
public void consume(OrderEvent event) {
    processOrder(event);  // 失败抛异常
    // 自动 ack（如启用）
}

// ✅ 正确：失败重试 + 死信
@KafkaListener(topics = "orders")
public void consume(OrderEvent event, Acknowledgment ack) {
    try {
        processOrder(event);
        ack.acknowledge();  // 处理成功才提交
    } catch (Exception e) {
        log.error("Process failed", e);
        // 重试 3 次后发到 DLT
        throw e;  // 让 Spring Kafka 重试
    }
}
```

### ✅ Consumer 端完整解决方案

```java
Properties props = new Properties();
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);  // 关闭自动提交
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");  // 只读已提交
props.put(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Arrays.asList("orders"));

while (running) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    
    for (ConsumerRecord<String, String> record : records) {
        try {
            processRecord(record);  // 业务处理
            // 处理成功才提交 Offset
        } catch (Exception e) {
            log.error("Process failed", e);
            deadLetterQueue.send(record, e);  // 发送到死信
        }
    }
    
    // 手动提交
    consumer.commitSync();
}
```

## 🔧 系统级丢失场景

### 场景 1：机房故障

```
场景：单个机房断电
  - 所有 Broker 不可用
  - 所有 Producer/Consumer 不可用
  - 数据可能丢失（如果未同步到备机房）

解决：
  - 跨机房部署（MirrorMaker 2.0）
  - 多副本跨机房
  - 异地备份
```

### 场景 2：磁盘损坏

```
场景：Broker 磁盘物理损坏
  - log 文件丢失
  - 该 Broker 上的数据丢失（如果单副本）

解决：
  - RAID 10（磁盘冗余）
  - 多副本（跨 Broker）
  - 远程备份（异地容灾）
```

### 场景 3：配置错误

```
常见配置错误：
  1. replication.factor=1
  2. min.insync.replicas=1
  3. acks=0
  4. enable.auto.commit=true + 业务处理异常

解决：
  - 配置审计（定期检查）
  - 配置版本控制
  - 自动化配置验证
```

## 📊 完整防丢方案

### 生产环境配置

```properties
# ==== Producer ====
acks=all
enable.idempotence=true
retries=Integer.MAX_VALUE
max.in.flight.requests.per.connection=5
delivery.timeout.ms=120000
```

```properties
# ==== Broker ====
replication.factor=3
min.insync.replicas=2
unclean.leader.election.enable=false
log.flush.interval.messages=10000
log.flush.interval.ms=1000
```

```java
// ==== Consumer ====
props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");

// 处理完手动 ack
ack.acknowledge();
```

### 数据校验

```java
// 业务端幂等设计（即使消息重复也不丢数据）
@Transactional
public void processOrder(OrderEvent event) {
    // 主键约束（数据库兜底）
    try {
        orderRepository.save(new Order(event.getOrderId(), ...));
    } catch (DuplicateKeyException e) {
        // 已处理过，跳过
    }
}
```

## 📊 监控告警

```yaml
groups:
  - name: kafka_data_loss
    rules:
      # Under-Replicated Partitions（同步问题）
      - alert: KafkaUnderReplicated
        expr: sum(kafka_topic_partition_under_replicated_partition_count) > 0
        for: 5m
        labels:
          severity: warning
      
      # ISR 频繁收缩（网络或磁盘问题）
      - alert: KafkaISRShrinksFrequently
        expr: rate(kafka_server_replica_manager_isr_shrinks_total[5m]) > 1
        for: 5m
        labels:
          severity: warning
      
      # Producer 错误率
      - alert: KafkaProducerErrors
        expr: rate(producer_record_error_total[5m]) > 10
        for: 5m
        labels:
          severity: warning
```

## 📊 实战：消息零丢失系统设计

### 完整架构

```
┌────────────────────────────────────────┐
│          Producer                       │
│   ✅ acks=all                           │
│   ✅ enable.idempotence=true            │
│   ✅ 异步回调 + 异常重试                 │
│   ✅ Outbox Pattern（数据库兜底）         │
└────────────────────────────────────────┘
                ↓
┌────────────────────────────────────────┐
│          Kafka Cluster                   │
│   ✅ replication.factor=3               │
│   ✅ min.insync.replicas=2              │
│   ✅ unclean.leader.election=false      │
│   ✅ 多机房（MirrorMaker 2.0）           │
└────────────────────────────────────────┘
                ↓
┌────────────────────────────────────────┐
│          Consumer                       │
│   ✅ ENABLE_AUTO_COMMIT=false           │
│   ✅ 手动 ack                            │
│   ✅ 业务幂等（数据库唯一约束）          │
│   ✅ 死信队列兜底                        │
└────────────────────────────────────────┘
```

### Outbox Pattern

```java
@Service
@Transactional
public class OrderService {
    
    @Autowired
    private OrderRepository orderRepository;
    @Autowired
    private OutboxRepository outboxRepository;
    
    public Order createOrder(OrderDTO dto) {
        // 1. 业务逻辑（DB 事务）
        Order order = new Order(dto);
        orderRepository.save(order);
        
        // 2. 写 Outbox（同一事务）
        Outbox outbox = new Outbox();
        outbox.setTopic("order-events");
        outbox.setKey(order.getId());
        outbox.setValue(order.toJson());
        outbox.setStatus("PENDING");
        outboxRepository.save(outbox);
        
        // 事务提交：order + outbox 一起持久化
        return order;
    }
}

// Outbox 发送器（独立线程）
@Component
public class OutboxSender {
    
    @Scheduled(fixedDelay = 100)
    @Transactional
    public void sendPending() {
        List<Outbox> pending = outboxRepository.findByStatus("PENDING");
        for (Outbox outbox : pending) {
            kafkaTemplate.send(outbox.getTopic(), outbox.getKey(), outbox.getValue())
                .whenComplete((result, ex) -> {
                    if (ex == null) {
                        outbox.setStatus("SENT");
                        outboxRepository.save(outbox);
                    }
                });
        }
    }
}
```

**优势**：
- ✅ DB 事务保证 order 和 outbox 原子
- ✅ outbox 必发送（独立进程）
- ✅ 不依赖 Kafka 事务
- ✅ 完全解耦

## 📊 消息丢失检测

### 对账机制

```java
// 定时对账：DB 数据 vs Kafka 数据
@Component
public class DataReconciliationJob {
    
    @Scheduled(cron = "0 0 2 * * ?")  // 每天凌晨 2 点
    public void reconcile() {
        // 1. 从 DB 拉取最近 24 小时订单
        List<Order> orders = orderRepository.findLast24Hours();
        
        // 2. 从 Kafka 拉取（按 offset 范围）
        // ...
        
        // 3. 对比
        for (Order order : orders) {
            // 检查 Kafka 中是否有对应消息
            if (!kafkaContains(order)) {
                // 缺失：告警 + 重发
                alert("Order missing in Kafka: " + order.getId());
                kafkaTemplate.send("order-events", order.getId(), order.toJson());
            }
        }
    }
}
```

## ⚠️ 常见误区

### 误区 1：启用幂等性就一定不丢

```
❌ 错误认知
✅ 幂等性是防止 Producer 重复发送（不是防丢失）
   - 幂等性：单会话不重复
   - 持久化：acks=all + min.insync.replicas=2
```

### 误区 2：acks=all 就一定不丢

```
⚠️ 部分情况下仍可能丢
   - unclean.leader.election=true 时
   - 整个集群故障时

✅ 推荐组合：
   - acks=all
   - min.insync.replicas=2
   - replication.factor=3
   - unclean.leader.election=false
```

### 误区 3：3 副本就一定不丢

```
⚠️ 如果 acks=1 + Leader 故障，仍可能丢
✅ 必须 acks=all + 副本同步确认
```

## 🎯 总结

**消息丢失解决方案核心要点**：
- ✅ Producer：acks=all + 幂等性 + 回调
- ✅ Broker：replication.factor=3 + min.insync.replicas=2
- ✅ Consumer：手动 ack + 业务幂等
- ✅ Outbox Pattern（DB+Kafka 原子）
- ✅ 监控告警（Under-Replicated、ISR 收缩）
- ✅ 数据对账（定期校验）
- ⚠️ 没有万能方案，需组合使用
- ⚠️ 业务幂等是最后防线

**下一步：** [🆚 Kafka vs RocketMQ](/10-interview/kafka-vs-rocketmq) — 选型对比

## 📚 跨站参考：📊 监控告警

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **observability** 站（[https://java-px.bot.cd/observability/](https://java-px.bot.cd/observability/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [mysql](https://java-px.bot.cd/mysql/) / [video](https://java-px.bot.cd/video/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。


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
