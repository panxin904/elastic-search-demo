---
title: 分布式限流
---
# 分布式限流

## 1. 为什么分布式限流

```
单实例限流：本地计数器 / Guava RateLimiter
  - 问题：N 个实例，每个 QPS = 100，但用户能绕到不同实例 → 实际 100N

分布式限流：全局共享计数
  - 真实限流 100 QPS
  - 多实例协调
```

## 2. 三大方案

### 方案 1：Redis + Lua（最常用）

```
  ┌─ Instance A ─┐   ┌─ Instance B ─┐   ┌─ Instance C ─┐
  │   check   ↓    │   check   ↓    │   check   ↓    │
  │   INCR   atomically via Redis Lua      │
  │   ↓   return allowed/denied            │
  └──────────┘   └──────────┘   └──────────┘
              ↓
            Redis
```

**优点**：单次 round-trip，原子，简单。
**缺点**：Redis 故障 → 限流失效（可降级到本地限流）。

### 方案 2：Redis Cluster（分片）

按 key hash 到不同 slot，**分片**提升吞吐。

```
key "rate:user:1" → slot 1
key "rate:user:2" → slot 2
...
```

10 节点 Redis Cluster → 理论限流 RPS × 10。

### 方案 3：Sentinel / 滑动窗口（精确）

分布式版本，状态在 Redis 共享，但用 sliding window log 而非 token bucket，更精确。

## 3. 实战：Redis + Lua 令牌桶

```lua
-- KEYS[1] = "rl:" + userId
-- ARGV[1] = capacity
-- ARGV[2] = refillRate (tokens/sec)
-- ARGV[3] = now (sec)
-- ARGV[4] = requestId (for tracking)

local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local reqId = ARGV[4]

local data = redis.call("HMGET", key, "tokens", "ts")
local tokens = tonumber(data[1]) or capacity
local last = tonumber(data[2]) or now

tokens = math.min(capacity, tokens + (now - last) * rate)

if tokens >= 1 then
  tokens = tokens - 1
  redis.call("HMSET", key, "tokens", tokens, "ts", now)
  redis.call("EXPIRE", key, math.ceil(capacity / rate) * 2)
  return 1
else
  return 0
end
```

## 4. Java 集成

```java
@Service
public class DistributedRateLimiter {
  @Autowired StringRedisTemplate redis;

  private static final DefaultRedisScript<List> SCRIPT = new DefaultRedisScript<>(
    "redis.call('HMGET', KEYS[1], 'tokens', 'ts')
" +
    "local tokens = tonumber(ARGV[3]) or tonumber(ARGV[1])
" +
    "local last = tonumber(ARGV[4]) or tonumber(ARGV[3])
" +
    "tokens = math.min(tonumber(ARGV[1]), tokens + (tonumber(ARGV[3]) - last) * tonumber(ARGV[2]))
" +
    "if tokens >= 1 then
" +
    "  redis.call('HMSET', KEYS[1], 'tokens', tokens-1, 'ts', tonumber(ARGV[3]))
" +
    "  redis.call('EXPIRE', KEYS[1], 60)
" +
    "  return 1
" +
    "else
" +
    "  return 0
" +
    "end",
    List.class
  );

  public boolean allow(String userId) {
    List<Long> result = redis.execute(SCRIPT, List.of("rl:" + userId),
      "100", "10", String.valueOf(System.currentTimeMillis() / 1000),
      UUID.randomUUID().toString());
    return result.get(0) == 1L;
  }
}
```

## 5. 多级限流

```java
// 多维度：用户 + 接口 + IP
public boolean check(String userId, String api, String ip) {
  return userLimiter.allow(userId)
      && apiLimiter.allow(api)
      && ipLimiter.allow(ip);
}
```

## 6. 限流策略分发

```
限流后：
  - 拒绝：直接返回 429 Too Many Requests
  - 排队：MQ 异步处理
  - 降级：返回缓存（stale-while-revalidate）
  - 熔断：见 circuit-breaker
```

## 7. Redis 故障降级

```java
public boolean allow(String userId) {
  try {
    return distributedLimiter.allow(userId);
  } catch (RedisException e) {
    return localLimiter.allow(userId);  // 降级到本地限流
  }
}
```

**降级原则**：宁可限流过松，不要让限流挂掉整个业务。

## 🔗 下一步
- [令牌桶算法](/04-rate-limit/token-bucket)
- [熔断器三态](/05-circuit-breaker/states)
- [Fallback 设计](/05-circuit-breaker/fallback)
