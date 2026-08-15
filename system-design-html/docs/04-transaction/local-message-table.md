---
title: 本地消息表
---

# 本地消息表

> 把分布式事务拆成本地事务 + 消息表，异步重试保证最终一致。**最简单、最广泛使用的分布式事务方案**。

## 1. 什么是本地消息表？

```
核心思想：
  - 把"业务操作"和"消息发送"绑定到同一个本地事务
  - 消息存业务库的消息表
  - 后台任务轮询消息表，发送到 MQ
  - 消费方处理后回调业务方

特点：
  - 业务代码改动小
  - 依赖业务库（不用单独的事务协调器）
  - 性能好（异步 + 解耦）
  - 最终一致（不是强一致）
```

## 2. 整体架构

```
┌──────────┐                          ┌──────────┐
│ 业务库    │                          │  MQ     │
│ ┌──────┐ │                          │         │
│ │订单表│ │                          │         │
│ ├──────┤ │                          │         │
│ │消息表│ │  轮询 →  发送             │         │
│ └──────┘ │  ────→  ────→            │         │
└──────────┘                          └────┬────┘
                                          │
                                          ↓
                                      ┌──────────┐
                                      │  库存服务 │
                                      │ 扣库存    │
                                      └──────────┘
```

## 3. 核心流程

### 3.1 发送方流程

```
1. 开启本地事务：
   BEGIN TRANSACTION;

2. 写业务表：
   INSERT INTO orders (user_id, amount) VALUES (?, ?);

3. 写消息表（同库同事务）：
   INSERT INTO local_messages
     (msg_id, topic, content, status, retry_count, next_retry_at)
   VALUES
     (?, 'order.created', ?, 'pending', 0, NOW());

4. 提交本地事务：
   COMMIT;

5. 后台轮询任务：
   - 查 status='pending' AND next_retry_at < NOW()
   - 发送到 MQ
   - 成功 → UPDATE status='sent'
   - 失败 → retry_count++，指数退避
```

### 3.2 消费方流程

```
1. 收到 MQ 消息
2. 执行业务：
   - 检查幂等（msg_id 去重）
   - 扣库存
3. 业务成功 → ACK 消息
4. 业务失败：
   - 重试（MQ 自带）
   - 重试超限 → 死信队列 + 人工
```

## 4. 关键设计

### 4.1 消息表结构

```sql
CREATE TABLE local_messages (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    msg_id       VARCHAR(64) NOT NULL UNIQUE,  -- 全局唯一
    topic        VARCHAR(128) NOT NULL,
    content      TEXT NOT NULL,
    status       VARCHAR(16) NOT NULL DEFAULT 'pending',  -- pending/sent/failed
    retry_count  INT NOT NULL DEFAULT 0,
    next_retry_at DATETIME NOT NULL,
    created_at   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at      DATETIME,
    INDEX idx_status_retry (status, next_retry_at)
);
```

要点：
```
- msg_id 唯一：消费方去重
- status：跟踪消息状态
- retry_count：控制最大重试
- next_retry_at：指数退避
- 索引：扫描 pending 消息要快
```

### 4.2 轮询调度

```java
@Scheduled(fixedDelay = 1000)  // 每秒一次
public void pollAndSend() {
    List<Message> messages = messageDao.findPending(
        limit = 100,
        now = System.currentTimeMillis()
    );

    for (Message msg : messages) {
        try {
            mqProducer.send(msg.topic, msg.content);
            messageDao.markSent(msg.id);
        } catch (Exception e) {
            messageDao.markRetry(msg.id, exponentialBackoff(msg.retryCount));
        }
    }
}

private long exponentialBackoff(int retryCount) {
    return (long) (1000 * Math.pow(2, retryCount));  // 1s, 2s, 4s, 8s, ...
}
```

### 4.3 防重复消费

```
方案 1：消费方幂等表
  - 收到消息先写消费记录（msg_id 唯一）
  - 重复消息直接跳过

方案 2：业务幂等
  - 订单状态：已支付 → 跳过
  - 库存扣减：CAS（compare and swap）

📌 99% 的场景：消费方做幂等就够
```

### 4.4 指数退避

```
重试策略：
  - 第 1 次：1s 后
  - 第 2 次：2s 后
  - 第 3 次：4s 后
  - 第 4 次：8s 后
  - 第 5 次：16s 后
  - 第 6 次：32s 后
  - 第 N 次：min(2^N, 300s)

最大重试：
  - retry_count > 10 → 死信队列
  - 人工处理

抖动：
  - 2^N × (0.5 + random(0, 0.5))
  - 避免雪崩
```

## 5. 高级话题

### 5.1 消息表膨胀

```
问题：
  - 长期运行，消息表越来越大
  - 索引越来越大，扫描变慢

方案：
  1. 定期清理（status='sent' 且 sent_at < 30 天前 → 删除）
  2. 分区表（按月分区）
  3. 归档到冷库
```

### 5.2 分布式定时任务

```
单机轮询的问题：
  - 单点故障
  - 不能水平扩展

方案：
  1. ShedLock（基于 DB 锁）
     - 多个实例同时跑，只有一个拿锁成功
     - 简单可靠

  2. XXL-Job / Elastic-Job
     - 分布式调度平台
     - 任务分片、失败转移

  3. 直接用 MQ 的延迟消息
     - 不用轮询
     - 复杂度上升
```

### 5.3 消息延迟

```
场景：
  - 业务提交 → 轮询延迟 → 消息发出
  - 平均延迟 500ms-2s
  - 部分场景不能接受

优化：
  1. 减小轮询间隔（1s → 100ms）
  2. 实时监听 binlog（Canal）
  3. 用 RocketMQ 事务消息
  4. 多线程并发消费
```

### 5.4 与业务事务强一致

```
问题：
  - 业务事务 commit 后，进程崩溃
  - 消息没发出去

解决：
  1. 后台轮询补偿（已发）
  2. 业务 commit 前发消息
     - 风险：业务回滚但消息已发
     - 解决：消费方做幂等
  3. 两阶段提交消息 + 业务（不推荐，太重）
```

## 6. 与其他方案对比

| 方案 | 一致性 | 性能 | 复杂度 | 侵入 |
|---|---|---|---|---|
| **本地消息表** | 最终一致 | 高 | 低 | 小 |
| **事务消息** | 最终一致 | 高 | 中 | 中 |
| **TCC** | 强一致 | 中 | 高 | 大 |
| **Saga** | 最终一致 | 高 | 中 | 中 |
| **2PC** | 强一致 | 低 | 低 | 小 |

## 7. 适用场景

```
✅ 适合：
  - 业务对实时性要求不高（秒级延迟可接受）
  - 业务能容忍最终一致
  - 不希望引入复杂框架（用现成的轮询 + 业务库）
  - 跨服务事务，参与方 2-5 个

❌ 不适合：
  - 强一致（用 TCC 或 2PC）
  - 实时性要求高（毫秒级）
  - 参与方多（10+ 个，复杂度爆炸）
```

## 8. 经典案例

### 8.1 电商下单

```
业务：
  - 订单服务：创建订单
  - 库存服务：扣减库存
  - 支付服务：待支付状态
  - 营销服务：发优惠券

流程：
  1. 订单服务本地事务：
     - INSERT orders
     - INSERT local_messages（topic=order.created, content=订单信息）
  2. 后台轮询 → 发到 MQ
  3. 库存服务消费：扣库存
  4. 支付服务消费：创建待支付
  5. 营销服务消费：发券

📌 阿里早期大规模使用此模式
```

### 8.2 跨行转账

```
A 行 → B 行
  - A 行扣款 + 写消息表（topic=transfer.out）
  - 后台发消息 → MQ
  - B 行消费 → 加款

容错：
  - 消费失败重试
  - 最终 B 行加款
  - 最坏：A 扣款但 B 没加款 → 人工对账
```

## 9. 一句话总结

```
📌 本地消息表 = 本地事务 + 消息表 + 异步轮询，最终一致
📌 流程：业务 + 消息表同事务 → 轮询发 MQ → 消费方幂等处理
📌 优点：代码侵入小、依赖少、性能高
📌 缺点：延迟秒级、需要消费方幂等、需要定时清理消息表
📌 关键设计：消息表索引（status+next_retry_at）+ 消费幂等（msg_id）+ 指数退避
📌 优化方向：Canal 监听 binlog / RocketMQ 事务消息 / 分布式调度
📌 适合：电商下单、跨行转账、跨服务状态同步
📌 阿里大规模生产验证
```

## 10. 参考资料

- eBay 经典论文 "Local Message Table" 模式
- RocketMQ 事务消息设计
- "Patterns of Enterprise Application Architecture"
- Seata 事务模式
- Canal binlog 订阅
- 阿里中间件团队博客
