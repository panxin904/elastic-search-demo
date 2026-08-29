---
title: 幂等性：消息去重
date: 2026-08-15  # date-auto-injected
---

# 幂等性：消息去重

> 消息可能重复投递。**让重复消息不影响业务结果**。

## 1. 为什么会有重复？

```
重复场景：

1. 生产者重试：
   - 发消息超时（实际成功）
   - 重试 → Broker 收到 2 条
   → 生产端重复

2. Broker 投递重试：
   - 消费者处理完但 ACK 丢失
   - Broker 重新投递
   → 消费端重复

3. 主从切换：
   - Leader 写了但未同步到 Follower
   - Follower 升级为 Leader
   - 重新投递
   → Broker 端重复

📌 几乎无法避免重复 → 必须在消费端去重
```

## 2. 幂等的定义

```
幂等操作：
  一次执行和多次执行效果相同

例：
  ✓ set x = 5（幂等）
  ✓ delete where id=1（幂等）
  ✗ add x += 5（非幂等）
  ✗ insert into orders（默认非幂等）

业务幂等：
  同一笔订单多次支付 → 只扣一次款
  同一笔请求多次发短信 → 只发一条
```

## 3. 业务层幂等设计

### 3.1 唯一 ID 方案

```
每条消息带唯一 ID：
  - 业务 ID（订单号 / 交易号）
  - 或者消息自带的 messageId

消费时：
  1. 收到消息 msg
  2. 用 ID 查 Redis / DB
  3. 已处理 → 跳过
  4. 未处理 → 处理 + 标记

实现：
  - Redis SETNX（原子）
  - DB 唯一索引（强一致）
```

### 3.2 状态机方案

```
业务有状态，转移幂等：
  - 订单状态：已创建 → 已支付 → 已发货
  - "已支付 → 已支付" 是非法转移
  → 重复消息不会引起状态变化

SQL 实现：
  UPDATE orders SET status='paid' 
  WHERE id=123 AND status='created'

第二次执行：
  - 状态已经是 paid，WHERE 不匹配
  - 影响行数 0
  → 幂等
```

### 3.3 数据库唯一索引

```
利用 UNIQUE 约束：

例：扣款消息处理
  INSERT INTO transactions 
    (biz_id, amount) 
  VALUES ('trade_123', 100)

biz_id 上有唯一索引：
  - 第一次：插入成功
  - 重复消息：插入失败（Duplicate Key）
  → 幂等
```

## 4. 通用去重方案

### 4.1 Redis 方案

```
SETNX 去重：

  msg_id = "trade_123"
  
  if redis.setnx("processed:" + msg_id, 1, ex=86400):
      # 加锁成功 → 第一次处理
      process(msg)
  else:
      # 已处理过
      log.info("duplicate msg, skip")
      return

优点：快
缺点：
  - Redis 故障 → 误判（已处理但查不到）
  - 适合"宁可多处理也不漏"
```

### 4.2 滑动窗口去重

```
场景：
  - 消息频率高
  - 单消息 ID 去重不够

实现：
  - 用 Bloom Filter 记录最近 N 分钟的 ID
  - 收到消息时查 Bloom Filter
  - 命中 → 可能重复（需要二次确认）
  - 不命中 → 一定不重复

适合：
  - 秒杀请求去重
  - 短时间窗口
```

### 4.3 数据库唯一索引 + 重试

```
用数据库保证强一致：

```sql
CREATE TABLE processed_messages (
  msg_id VARCHAR(64) PRIMARY KEY,
  processed_at TIMESTAMP
);
```

处理流程：
  BEGIN
    INSERT INTO processed_messages (msg_id, ...) VALUES (...)
    -- 若 Duplicate Key → 已处理，跳过
    process(msg)
  COMMIT
```

优点：强一致
缺点：每次处理多一次写
```

## 5. 主流 MQ 的幂等支持

### 5.1 Kafka 幂等 Producer

```
enable.idempotence=true（默认开启）：

  - Producer 自动给消息加 PID + sequence number
  - Broker 端去重（根据 PID + sequence）
  - 保证"单分区单会话"不重复

⚠️ 注意：
  - 仅单分区去重
  - 跨分区可能重复
  - 不能跨 Producer 实例
```

### 5.2 Kafka 事务

```
事务 Producer：

  producer.beginTransaction()
  producer.send(msg1)
  producer.send(msg2)
  producer.commitTransaction()

  - 原子：所有消息一起成功 / 一起失败
  - 与消费 offset 提交原子
  → 实现 exactly-once

代价：
  - 性能下降 30%+
  - 实现复杂
```

### 5.3 RocketMQ

```
RocketMQ 没有原生幂等，靠业务层：
  - 用 messageId 去重
  - 或业务唯一键去重

RocketMQ 5.0+ 引入了：
  - 消息轨迹
  - 但幂等仍依赖业务
```

## 6. 业务幂等的工程实践

### 6.1 支付场景

```
订单支付消息：

幂等设计：
  1. 收到"支付成功"消息
  2. UPDATE orders SET status='paid' 
     WHERE id=? AND status='created'
  3. 影响行数 0 → 已处理过，直接 ACK
  4. 影响行数 1 → 处理成功，ACK
  5. 处理失败 → 不 ACK，等重试

数据库唯一索引兜底：
  - transactions 表：biz_id UNIQUE
  - 即使并发处理也只有一个成功
```

### 6.2 库存扣减

```
秒杀扣库存：

非幂等实现：
  UPDATE stock SET count = count - 1 WHERE product_id = 123
  - 重复消息 → 多次扣减 → 超卖

幂等实现（Redis Lua）：
  local key = "stock:" .. product_id
  local msg_id = ARGV[1]
  
  -- 检查是否处理过
  if redis.call('sismember', 'processed_msgs', msg_id) == 1 then
    return 'duplicate'
  end
  
  -- 扣减
  local new_count = redis.call('decr', key)
  if new_count < 0 then
    redis.call('incr', key)
    return 'no_stock'
  end
  
  -- 标记已处理
  redis.call('sadd', 'processed_msgs', msg_id)
  return 'success'

📌 Redis Lua 原子 + 幂等
```

### 6.3 发短信 / 推送

```
短信消息：

幂等设计：
  - 用 biz_id（业务请求 ID）
  - Redis 记录已发送
  - 重复消息直接跳过

  if redis.setnx("sms:" + biz_id, 1, ex=86400):
      send_sms(msg)
  else:
      log.info("duplicate sms, skip")
```

## 7. 幂等 vs 重复消费

```
📌 严格区分：
  - 重复消费：消息被消费了多次
  - 幂等：重复消费但结果一样
  
目标：实现幂等，让重复消费无害

不是所有业务都需要幂等：
  - 读操作（天然幂等）
  - 单次写操作（默认幂等）
  - 状态变更（要幂等）
  - 累计操作（最复杂，需要去重）
```

## 8. 一句话总结

```
📌 消息重复几乎无法避免 → 必须消费端幂等
📌 业务幂等三方案：唯一 ID + 状态机 + DB 唯一索引
📌 通用去重：Redis SETNX（快）/ DB 唯一索引（强一致）/ Bloom Filter（高频）
📌 Kafka 幂等 Producer：单分区不重复（跨分区可能重）
📌 Kafka 事务：exactly-once 但性能差 30%+
📌 实际生产：at-least-once 投递 + 业务层幂等
📌 库存扣减用 Redis Lua 原子操作 + 幂等标记
📌 不是所有业务都需要幂等（读操作天然幂等）
```

## 9. 参考资料

- Kafka Idempotent Producer 文档
- Kafka Transactions (KIP-98)
- RocketMQ 幂等消息实践
- Exactly-Once Semantics Are Possible: Here's How Kafka Does It
- DDIA 第 11 章
- 阿里双十一幂等设计实践


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
<!-- auto-enrich:do-not-edit -->
