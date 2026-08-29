---
title: 消息顺序性
date: 2026-08-15  # date-auto-injected
---

# 消息顺序性

> 消息队列是**乱序**的，但有些业务必须**有序**。

## 1. 为什么需要顺序？

```
业务场景：

1. 订单状态：
   创建 → 支付 → 发货 → 收货
   必须按这个顺序处理
   否则：先发货后支付（不可能）

2. 数据库 binlog：
   binlog 必须按顺序应用
   否则数据不一致

3. 排行榜更新：
   用户的多个操作（涨粉、点赞、上传）
   应按时间顺序应用

4. 金融账务：
   存款 → 取款 → 转账
   顺序错就漏账
```

## 2. 顺序的种类

```
全局顺序：
  所有消息按全局时间顺序处理
  → 极难实现，几乎没有系统支持

分区顺序：
  同一分区内消息有序
  不同分区间可能乱序
  → Kafka / RocketMQ 默认保证

业务顺序：
  同一业务键的消息有序
  不同业务键的消息乱序
  → 工程上最容易实现
```

## 3. Kafka 的顺序保证

### 3.1 单分区有序

```
Kafka：
  - 单分区（Partition）内消息严格有序
  - 分区间无序
  - 单消费者处理单分区可保证顺序

producer：
  - 默认按 key 哈希到分区
  - 同 key 的消息进入同分区
  → 同 key 的消息有序

consumer：
  - 单消费者实例消费单分区
  - 同分区消息按 offset 处理
  → 保证顺序
```

### 3.2 配置顺序保证

```properties
# Producer
max.in.flight.requests.per.connection=5   # ≤5 保证幂等有序
enable.idempotence=true                   # 必开

# Consumer
max.poll.records=1                         # 一次只拉 1 条
isolation.level=read_committed            # 只读已提交
```

### 3.3 顺序的代价

```
顺序保证的代价：
  - 单分区处理能力受限（无法水平扩展）
  - 分区数固定后难以扩展
  - 失败时整个分区阻塞

例：
  - 10 个分区 → 10 个消费者
  - 1 个分区的消费者挂了 → 该分区消息阻塞
  → 全局吞吐量受限于"最慢分区"
```

## 4. RocketMQ 的顺序保证

### 4.1 顺序消息类型

```
全局顺序：
  - 整个 topic 一个队列
  - 性能差（单点）
  - 用法：少数强顺序场景

分区顺序（MessageQueueOrderly）：
  - 同一队列有序
  - 不同队列可并行
  - 用法：同业务键的消息进入同队列
```

### 4.2 使用示例

```java
// 生产顺序消息
MessageQueueSelector selector = new MessageQueueSelector() {
    @Override
    public MessageQueue select(List<MessageQueue> queues, Message msg, Object arg) {
        // 按订单 ID 哈希到固定队列
        int hash = arg.hashCode() % queues.size();
        return queues.get(Math.abs(hash));
    }
};

producer.send(msg, selector, orderId);

// 消费顺序消息
consumer.registerMessageListener(new MessageListenerOrderly() {
    @Override
    public ConsumeOrderlyStatus consumeMessage(...) {
        process(msg);
        return ConsumeOrderlyStatus.SUCCESS;
    }
});
```

### 4.3 顺序消息的注意点

```
📌 RocketMQ 顺序消息的坑：
   - 消费者多实例时，自动负载均衡
   - 队列被多个消费者抢时，顺序会乱
   - 解决：用 MessageListenerOrderly 而不是 MessageListenerConcurrently
   - 锁定队列（rebalance 时等锁）
```

## 5. 业务层保证顺序

### 5.1 单一队列串行

```
把所有相关消息送到同一队列：
  - 同业务键 → 同一分区
  - 单消费者串行处理

实现：
  - Kafka：key 设为业务 ID
  - RocketMQ：MessageQueueSelector
  - RabbitMQ：单队列 + 顺序消费
```

### 5.2 业务状态机

```
即使消息乱序，业务也能纠正：

订单状态机：
  - 任何"非法转移"都忽略
  - 例：先收到"已发货"再收到"已支付"
    - 已发货时订单未支付？忽略发货消息
    - 已发货时订单已支付？正常

📌 用状态机天然容错
```

### 5.3 版本号 / 时间戳

```
消息带版本号：

  msg: { order_id: 123, version: 5, action: 'pay' }

消费时：
  if msg.version < current_version:
      skip  # 过期消息
  
  process(msg)
  current_version = msg.version

适合：
  - 数据同步
  - 增量更新
```

## 6. 顺序处理的常见问题

### 6.1 消息积压导致顺序错乱

```
场景：
  - 消费者处理慢
  - 消息堆积
  - 重试后可能乱序处理

解决：
  - 增加消费者（同分区多实例）
  - 优化处理逻辑
  - 限制消费速度
```

### 6.2 重试导致顺序错乱

```
场景：
  - 消息 1 处理失败
  - 消息 2 处理成功
  - 消息 1 重试成功
  → 顺序颠倒

解决：
  - 重试时整批回退
  - 或：失败消息单独进死信队列
  - 或：业务层纠正
```

### 6.3 多消费者并行

```
场景：
  - 分区数 5
  - 消费者数 10
  - 部分消费者空闲
  - 部分分区被多消费者抢

解决：
  - 消费者数 ≤ 分区数
  - 或用顺序消费模式（RocketMQ MessageListenerOrderly）
```

## 7. 工程实践

### 7.1 哪些业务必须顺序？

```
📌 强烈推荐顺序：
   - 金融账务（账本一致）
   - 数据库 binlog（数据一致）
   - 状态机强依赖顺序的业务

📌 不必顺序：
   - 点赞 / 评论 / 浏览（可乱序）
   - 排行榜更新（最终一致）
   - 日志收集（不依赖顺序）
```

### 7.2 顺序 vs 性能 权衡

```
顺序保证 = 性能损失：
  - 单分区吞吐有限
  - 失败影响放大
  - 难以水平扩展

决策树：
  Q1: 业务能不能容忍乱序？
    Yes → 不强求顺序
    No  → Q2
  Q2: 数据量级多少？
    小（<1k TPS）→ 强顺序
    大 → 分区顺序 + 业务容错
```

### 7.3 实战：MySQL binlog 同步

```
Canal 订阅 binlog → MQ → 下游消费者

顺序保证：
  - binlog 严格有序
  - 按库 / 表 分区，同表消息进同分区
  - 单消费者串行处理

性能：
  - 多个库 / 多张表可并行
  - 单表串行处理（保证 binlog 顺序）
```

## 8. 一句话总结

```
📌 全局顺序几乎无法实现；分区顺序是主流
📌 Kafka 单分区有序，跨分区乱序（按 key 保证同 key 有序）
📌 RocketMQ 顺序消息：分区顺序 + MessageListenerOrderly
📌 业务层容错：状态机 + 版本号 + 业务键路由
📌 顺序 vs 性能权衡：强顺序 = 性能损失（单分区吞吐受限）
📌 不是所有业务都需要顺序：点赞/评论/日志都可以乱序
📌 重试可能导致顺序错乱：失败消息单独处理
```

## 9. 参考资料

- Kafka Documentation: Message Ordering
- RocketMQ 顺序消息：官方文档
- Message Ordering in Distributed Systems (Microsoft 博客)
- DDIA 第 11 章
- 阿里 RocketMQ 顺序消息实战


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
