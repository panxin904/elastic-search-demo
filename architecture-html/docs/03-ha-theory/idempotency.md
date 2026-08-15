---
title: 幂等性设计
---
# 幂等性设计

## 1. 什么是幂等

**f(f(x)) = f(x)**：执行一次和执行 N 次效果一样。

```
转账 100 元：
  - 幂等接口：调 1 次扣 100，调 10 次还扣 100
  - 非幂等接口：调 1 次扣 100，调 10 次扣 1000（重复扣款！）
```

## 2. 为什么分布式系统必须幂等

```
网络不可靠 → 必然重试
  - 超时重试：客户端 → 服务端已执行但响应丢失
  - MQ 重发：消费者没 ACK → 重投
  - leader 切换：旧 leader 写了一半

→ 如果接口非幂等 → 重复执行 = 业务事故
```

## 3. 三大实现策略

### 策略 1：唯一键（Idempotency Key）

```
Client:  POST /pay
Header: Idempotency-Key: <uuid>

Server:
  1. 看 key 是否已存在 → 复用结果返回
  2. 不存在 → 执行 + 存结果
```

```java
// Stripe 模式
public Result pay(IdempotencyKey key, PayRequest req) {
  Optional<Result> existing = store.find(key);
  if (existing.isPresent()) return existing.get();
  Result result = doPay(req);
  store.saveIfAbsent(key, result, ttl=24h);
  return result;
}
```

### 策略 2：状态机 + 幂等键

```
转账：
  1. transfer_id = uuid (client 生成)
  2. UPDATE account SET balance -= 100 WHERE id=A AND transfer_id != ?
  3. UPDATE account SET balance += 100 WHERE id=B AND transfer_id != ?

效果：相同 transfer_id 执行 N 次 = 执行 1 次
```

### 策略 3：CAS / 乐观锁

```
UPDATE inventory SET stock = stock - 1, version = version + 1
WHERE sku = ? AND version = ?
```

## 4. MQ 消费幂等

```
Consumer:
  1. 收到 message_id = msg-123
  2. SELECT * FROM processed_messages WHERE msg_id = msg-123
  3. 已存在 → 跳过
  4. 不存在 → 处理 → 存
```

```java
@Transactional
public void onMessage(Message msg) {
  // 数据库唯一索引保证原子性
  if (processedMessageRepo.existsById(msg.getId())) return;
  processOrder(msg.getOrder());
  processedMessageRepo.save(new ProcessedMessage(msg.getId()));
}
```

## 5. HTTP 接口幂等

| 场景 | 方案 |
|------|------|
| 支付扣款 | Idempotency-Key + DB 唯一约束 |
| 创建订单 | 业务订单号 + 唯一索引 |
| 状态变更 | 当前状态校验（CAS） |
| 异步任务 | 任务 ID + 结果缓存 |

## 6. 实战：分布式锁

```java
// Redis SETNX 实现幂等锁
public boolean tryLock(String key, String value, int ttl) {
  Boolean ok = redisTemplate.opsForValue().setIfAbsent(key, value, ttl);
  return Boolean.TRUE.equals(ok);
}

// 释放时校验 value 防止误删别人的锁
public void unlock(String key, String value) {
  String script = "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end";
  redisTemplate.execute(new DefaultRedisScript<>(script), List.of(key), value);
}
```

## 7. 反模式

- **缓存幂等 = 不用幂等**：缓存可能丢，应该双写 + 校验
- **DB 唯一约束不是万能**：分布式事务下仍可能脏写
- **MQ at-least-once = 重复消息**：必须 consumer 幂等

## 8. 实战 checklist

```
- [ ] 写接口是否幂等？给个 ID 重试会怎样？
- [ ] MQ consumer 是否有去重表 / 唯一索引？
- [ ] 定时任务是否有分布式锁防重复？
- [ ] 重试时是否携带唯一业务 ID？
- [ ] 数据库操作是否有唯一约束？
- [ ] 缓存删除是否用 CAS 校验？
```

## 🔗 下一步
- [CAP 定理](/03-ha-theory/cap)
- [幂等性设计](/03-ha-theory/idempotency)（就是这一页）
- [Saga 模式](/07-distributed-tx/saga)
- [Kafka vs RabbitMQ](/08-message-queue/compare)
