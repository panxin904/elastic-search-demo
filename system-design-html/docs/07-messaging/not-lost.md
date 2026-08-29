---
title: 消息可靠性：不丢消息
date: 2026-08-15  # date-auto-injected
---

# 消息可靠性：不丢消息

> 消息队列最基础的承诺：**至少一次投递**。但工程上要付出很大代价。

## 1. 消息丢失的三大环节

```
生产 → Broker → 消费

每个环节都可能丢：
  1. 生产者发送失败（网络 / 超时）
  2. Broker 收到但未持久化（宕机）
  3. Broker 持久化但消费者未收到（网络 / 宕机）
  4. 消费者收到但处理失败（应用崩溃）

📌 任何环节不可靠都会丢消息
```

## 2. 生产者端：不丢

### 2.1 同步发送 + 重试

```
producer.send(msg) 可能失败：
  - 网络抖动
  - Broker 短暂不可达

解决：
  producer.send(msg, new SendCallback() {
    onSuccess: 确认收到
    onFailure: 重试 N 次
  })

📌 同步等 ACK 才返回 → 延迟高但可靠
```

### 2.2 失败重试策略

```
重试算法：
  - 指数退避：间隔 = base * 2^attempt
  - 最多重试 N 次（3-5）
  - 加随机抖动（防止雪崩）

RocketMQ / Kafka 都有 retry 参数：
  - retries: 3
  - retryBackoffMs: 100
  - deliveryTimeoutMs: 30000

📌 重试可能造成重复消息（与 idempotent.md 联动）
```

### 2.3 事务消息（精确一次）

```
问题：
  业务操作 + 发消息需要原子
  - 业务成功但消息没发出去 → 丢
  - 消息发出但业务失败 → 误投递

RocketMQ 事务消息：
  1. 发 Half 消息（对消费者不可见）
  2. 执行本地事务
  3. 根据事务结果 Commit / Rollback Half 消息
  4. Broker 收到 Commit 后才对消费者可见
  5. 超时未决 → 反查本地事务状态

Kafka 事务（Kafka 0.11+）：
  - 事务协调器
  - 类似两阶段提交
  - 幂等 Producer + 事务
```

### 2.4 本地消息表

```
无事务消息能力的 MQ（Redis / RabbitMQ 旧版）：

思路：
  1. 业务事务 + 写本地消息表（同库）
  2. 后台 worker 轮询消息表
  3. 发到 MQ
  4. 收到 ACK 后标记消息已发
  5. 失败重试

优点：
  - 不依赖 MQ 事务能力
  - 简单可靠

缺点：
  - 业务表 + 消息表同库
  - 轮询有延迟
```

## 3. Broker 端：不丢

### 3.1 持久化

```
Broker 收到消息后必须持久化才能返回 ACK：

  生产者发 → Broker 写 PageCache → 同步刷盘 → 返回 ACK

📌 关键：必须等"刷盘"成功才返回
   - Kafka：acks=all + replication.factor=3
   - RocketMQ：SYNC_FLUSH + 主从同步
```

### 3.2 同步刷盘 vs 异步刷盘

```
异步刷盘：
  写 PageCache → 后台线程异步刷盘 → 返回 ACK
  优点：快（μs 级）
  缺点：可能丢（宕机时未刷盘的数据）

同步刷盘：
  写 PageCache → 同步刷盘 → 返回 ACK
  优点：可靠
  缺点：慢（ms 级）

📌 金融场景必须同步刷盘
   互联网场景默认异步 + 多副本足够
```

### 3.3 副本同步

```
Kafka：
  topic 默认 3 副本
  - 1 Leader（读写）
  - 2 Follower（只读、同步 Leader）
  - Leader 写入需等所有 ISR 确认（acks=all）

ISR（In-Sync Replicas）：
  - 与 Leader 保持同步的副本
  - Leader 挂了从 ISR 选新 Leader

📌 replication.factor=3 + acks=all
   = 最多容忍 1 副本故障而不丢
```

### 3.4 主从切换

```
Leader 挂了：
  - Controller 选新 Leader（从 ISR）
  - 未同步到 ISR 的消息可能丢

工程建议：
  - min.insync.replicas=2（至少 2 副本才写入）
  - unclean.leader.election.enable=false（不允许非 ISR 当 Leader）
  → 双保险
```

## 4. 消费者端：不丢

### 4.1 手动 ACK

```
消费者模式：

自动 ACK（默认）：
  收到消息立即 ACK
  → 处理失败时消息已 ACK → 丢
  ❌ 不可靠

手动 ACK：
  收到消息 → 处理成功 → 手动 ACK
  → 处理失败时不 ACK → 重试 / 进死信
  ✓ 可靠

代码示例：
  consumer.consume(msg -> {
    process(msg);
    consumer.ack(msg);  // 处理完才 ACK
  });
```

### 4.2 消费失败处理

```
处理失败怎么办？

策略 1：重试
  - 立即重试（可能永远失败）
  - 退避重试（推荐）

策略 2：死信队列
  - 重试 N 次失败 → 进死信队列
  - 人工处理

策略 3：告警 + 跳过
  - 记录 + 告警 + 跳过（可能丢）

RocketMQ：
  - 重试队列（默认 16 次）
  - 死信队列（%DLQ%）
  - 重试 Topic + 重试时间
```

### 4.3 至少一次 vs 最多一次

```
至少一次（at-least-once）：
  - 处理完才 ACK
  - 可能重复（ACK 前重启）
  - 配合幂等使用（见 idempotent.md）

最多一次（at-most-once）：
  - 收到就 ACK
  - 不重复但可能丢

精确一次（exactly-once）：
  - 处理 + ACK 原子
  - 难实现，成本高

📌 99% 场景选 at-least-once + 幂等
```

## 5. 端到端可靠性配置

### 5.1 Kafka

```properties
# Producer
acks=all                          # 等待所有 ISR 确认
retries=2147483647                # 无限重试
enable.idempotence=true           # 幂等 producer
max.in.flight.requests.per.connection=5

# Broker
replication.factor=3              # 3 副本
min.insync.replicas=2             # 至少 2 同步
unclean.leader.election.enable=false

# Consumer
enable.auto.commit=false          # 手动提交 offset
isolation.level=read_committed    # 只读已提交消息
```

### 5.2 RocketMQ

```properties
# Producer
sendMsgTimeout=10000
retryTimesWhenSendFailed=3
retryTimesWhenSendAsyncFailed=3

# Broker
flushDiskType=SYNC_FLUSH
brokerRole=SYNC_MASTER

# Consumer
messageModel=CLUSTERING
consumeMessageBatchMaxSize=1
```

## 6. 监控与告警

```
必须监控：
  1. 生产成功率（producer.send 成功比例）
  2. Broker 刷盘延迟（落盘延迟）
  3. 主从同步延迟（replica lag）
  4. 消费积压（consumer lag）
  5. 重试次数（retry 比例）

告警：
  - 生产失败率 > 阈值 → 告警
  - replica lag > 阈值 → 告警
  - consumer lag 持续增长 → 告警
```

## 7. 常见误区

### 7.1 误以为"消息进了 MQ 就不会丢"

```
MQ 默认配置可能不保可靠：
  - Kafka 默认 acks=1（只等 Leader）
  - 异步刷盘
  - 自动 ACK
  → 默认配置可能丢消息
```

### 7.2 误以为"重试就够了"

```
重试的问题：
  - 业务失败（如参数错误）→ 重试永远失败
  - 无限重试 → 消息阻塞后续
  → 必须有死信队列 + 监控
```

### 7.3 误以为"exactly-once 容易"

```
exactly-once 实现的代价：
  - Kafka 事务：性能下降 30%+
  - 应用层复杂
  - 测试困难
  → 大部分业务用 at-least-once + 幂等就够了
```

## 8. 一句话总结

```
📌 三大环节都可能丢消息：生产、Broker、消费
📌 生产者：同步 ACK + 重试 + 事务消息
📌 Broker：同步刷盘 + 多副本 + ISR 限制
📌 消费者：手动 ACK + 失败重试 + 死信队列
📌 推荐：at-least-once + 幂等（见 idempotent.md）
📌 Kafka 关键配置：acks=all + replication.factor=3 + min.insync.replicas=2
📌 监控：生产成功率 / replica lag / consumer lag
```

## 9. 参考资料

- Kafka Documentation: Producer Configs + Consumer Configs
- RocketMQ 官方文档：消息可靠性
- Kafka: The Definitive Guide (Neha Narkhede, 2017)
- Designing Data-Intensive Applications 第 11 章
- 阿里 RocketMQ 不丢消息实践


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
