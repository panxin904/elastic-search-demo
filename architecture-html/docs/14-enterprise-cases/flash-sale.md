---
title: 秒杀系统
date: 2026-08-15  # date-auto-injected
---
# 秒杀系统设计

## 1. 核心挑战

秒杀 = 100 万用户抢 100 件商品
  99% 请求是"无效"的（用户抢不到）
  1% 请求是"有效"的（抢到）
  → 系统要在极端流量下保持稳定
  → 不能超卖
  → 用户体验好

三大挑战：
1. 瞬时高并发：100 万 QPS，10 万倍日常流量
2. 读多写少：库存查询 1000x，写 1x
3. 超卖防护：原子扣减，不能超卖

## 2. 整体架构

```
     ┌─────────────────────────────────┐
     │   CDN / WAF / 静态资源            │
     └─────────────────────────────────┘
                 ↓
     ┌─────────────────────────────────┐
     │   网关 / 限流 / 验证码            │
     └─────────────────────────────────┘
                 ↓
     ┌─────────────────────────────────┐
     │   秒杀服务（核心）                │
     │  - 库存预热 Redis                │
     │  - 原子扣减 Redis Lua            │
     │  - 异步下单 MQ                  │
     └─────────────────────────────────┘
                 ↓
     ┌─────────────────────────────────┐
     │   订单服务 / 支付服务 / 库存服务  │
     │   (Kafka 异步)                  │
     └─────────────────────────────────┘
```

## 3. 五大核心技术

### 3.1 库存预热 + 原子扣减

```
1. 秒杀开始前（小时级）：
   - 预热 Redis：stock:seckill:item:123 = 100
   - 加载用户白名单（防黄牛）

2. 秒杀开始时：
   用户请求 → Redis Lua：
     1. if user_id in BLACKLIST: return FAIL
     2. if EXISTS(seckill:order:user:123:item) > 0: return DUP
     3. stock = DECR stock:seckill:item:123
        if stock < 0: return FAIL
     4. SET seckill:order:user:123:item = 1
     5. return OK
   → 原子（Redis 单线程 + Lua 原子）
   → 不超卖
   → 幂等（SET NX 防重）
```

### 3.2 限流与削峰

```
CDN：静态资源 + WAF
  → 拦 50% 无效请求

网关限流：
  - 每用户限流 1 req/sec（Lua sliding window）
  - 总 QPS 限流 100K（令牌桶）
  - IP 限流 5 req/sec

验证码：分流机器人
  - 简单数字（70% 通过）
  - 滑块（30% 行为分析）
  - SMS 验证（5% 兜底）
```

### 3.3 异步下单（MQ 解耦）

```
秒杀 Redis 扣减成功
  → 写 Redis order:pending:{orderId} = {user, item, ...}
  → 发 MQ topic=seckill.order
  → 用户轮询 Redis order:{orderId} 查状态

消费者：
  → 写 MySQL orders 表（事务）
  → 扣真实库存（DB 事务）
  → 发 SMS 通知
  → 改 order 状态 PAID
```

好处：秒杀服务快速返回，DB 写入异步。

### 3.4 库存超卖防护

两层防护：
1. Redis Lua 原子扣减（保证不会多人抢到同一件）
2. MySQL 事务扣库存（保证 DB 不超卖）

```sql
UPDATE inventory
SET stock = stock - 1
WHERE sku_id = 'item-123' AND stock > 0
AND status = 'ACTIVE';
-- affected_rows 判断是否成功
-- affected=0 → 失败，Redis 已扣但 DB 失败 → 补回 Redis
```

### 3.5 防黄牛与多账号

1. 设备指纹：同一设备只能抢 1 单
2. IP 限流：每 IP 限流
3. 实名认证：黑名单验证
4. 验证码 + 行为分析：识别机器人
5. 抢购资格：白名单 / 邀请制

## 4. 性能数据

| 指标 | 数值 |
|------|------|
| 峰值 QPS | 100 万 |
| Redis 读 | 50 万 qps（单 Redis Cluster） |
| MySQL 写 | 1 万 qps（分库分表） |
| 平均延迟 | 50ms（Redis Lua） |
| P99 延迟 | 200ms |
| 库存超卖 | 0（Redis Lua + DB 事务） |

## 5. 实战：Redis Lua 原子扣减

```java
@Service
public class SeckillService {
  @Autowired StringRedisTemplate redis;

  public boolean tryAcquire(Long userId, Long itemId) {
    String lua = """
      local stockKey = KEYS[1]
      local orderKey = KEYS[2]
      local stock = tonumber(redis.call('GET', stockKey))
      if stock <= 0 then return 0 end
      if redis.call('EXISTS', orderKey) == 1 then return 0 end
      redis.call('DECR', stockKey)
      redis.call('SET', orderKey, '1', 'EX', 600)
      return 1
    """;
    DefaultRedisScript<Long> script = new DefaultRedisScript<>(lua, Long.class);
    Long result = redis.execute(script, List.of(
      "stock:item:" + itemId,
      "order:user:" + userId + ":item:" + itemId
    ));
    return result == 1L;
  }
}
```

## 6. 实战：削峰

峰值 100 万 QPS → 各层削峰
  CDN：50% 命中
  网关：限流 30%
  验证码：分流 50%
  秒杀服务：实际接受 30 万 QPS
  Redis 预扣：5 万 qps
  MySQL：1 万 qps
  → 10x 削峰

## 7. 实战：前端优化

1. 静态化：商品详情 CDN 缓存
2. 防重提交：按钮点击后 disable + loading
3. 请求合并：多次点击合并为 1 次
4. 排队：前端展示排队进度
5. 乐观更新：先展示结果，等后端确认

## 8. 实战：后端关键点

1. 预热：秒杀前加载库存到 Redis
2. 库存校验：Redis 原子 + MySQL 事务（双保险）
3. 异步下单：Redis 标记 + MQ + 消费者
4. 对账：Redis 扣减 vs MySQL 实际下单 → 差异修复
5. 限流：令牌桶 / 滑动窗口
6. 熔断：下游服务故障 → 降级
7. 补偿：MQ 消费失败 → 退库存

## 9. 容量规划

100 万用户 → 10 万有效请求
  Redis：10 万 qps → 需要 1 Redis Cluster（16 节点）
  MySQL：1 万 qps → 32 库 32 表分库分表
  MQ：1 万 tps → Kafka 5 节点
  应用：30 万 qps → 50 台 8 核 Pod

## 10. 常见失败

- 库存超卖：Redis 单节点宕机 → 减扣和写库不一致
- 系统雪崩：MQ 消费慢 → Redis 内存爆
- 黄牛抢光：风控失效
- 用户投诉：白屏 / 慢

## 11. 监控指标

- 实时订单数（Redis INCR）
- 库存剩余（Redis GET）
- MySQL 写入 QPS
- 消费 lag
- 接口延迟 P99
- 失败率

## 12. 实战选型

| 规模 | 方案 |
|------|------|
| 中小（1 万商品） | Redis + MySQL + MQ |
| 大（10 万） | Redis Cluster + 分库分表 + 多级缓存 |
| 超大（100 万） | 阿里云 AHAS / 京东云 JSF / 自研 |

## 🔗 下一步
- [限流令牌桶算法](/04-rate-limit/token-bucket)
- [分布式事务 Saga](/07-distributed-tx/saga)
- [多级缓存架构](/09-cache/architecture)