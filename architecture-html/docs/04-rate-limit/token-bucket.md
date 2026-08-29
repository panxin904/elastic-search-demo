---
title: 令牌桶算法
date: 2026-08-15  # date-auto-injected
---
# 令牌桶算法

## 1. 核心思想

想象一个桶，按固定速率往里放令牌；每个请求消耗一个令牌；桶空则拒绝。

```
    持续加水            取水
   (速率 r)            (每请求 1 个令牌)
     ↓                  ↓
   ┌──────────────────┐
   │ ● ● ● ● ● ●     │  ← 桶容量 = b
   └──────────────────┘
     桶满 → 溢出（丢弃令牌）
     桶空 → 拒绝请求
```

**优点**：允许突发（桶内累计的令牌），同时限制平均速率。

## 2. 数学模型

```
桶容量：b（最多 b 个令牌）
补充速率：r（个/秒）
当前令牌：t（0 ≤ t ≤ b）
请求消耗：1 个令牌
请求到达：
  t ≥ 1 → t -= 1，允许
  t < 1 → 拒绝
时间流逝：t += r * dt（不超过 b）
```

**关键参数**：
- `b` 决定允许的突发长度
- `r` 决定平均吞吐

## 3. 优缺点

| 优点 | 缺点 |
|------|------|
| 允许突发（桶满时） | 桶满丢弃 → 用户感知"突然后就限流" |
| 配置简单 | 双参数（b + r）难调 |
| O(1) 时间空间 | 不绝对精确（取决于 r） |

## 4. Redis + Lua 实现

```lua
-- KEYS[1] = rate:user:123
-- ARGV[1] = capacity (b)
-- ARGV[2] = refill rate (tokens/sec)
-- ARGV[3] = current timestamp (sec)
-- ARGV[4] = requested tokens (default 1)

local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4]) or 1

local data = redis.call("HMGET", key, "tokens", "last_refill")
local tokens = tonumber(data[1]) or capacity
local last_refill = tonumber(data[2]) or now

local elapsed = now - last_refill
tokens = math.min(capacity, tokens + elapsed * rate)

local allowed = 0
if tokens >= requested then
  tokens = tokens - requested
  allowed = 1
end

redis.call("HMSET", key, "tokens", tokens, "last_refill", now)
redis.call("EXPIRE", key, math.ceil(capacity / rate) * 2)

return {allowed, tokens}
```

调用：EVALSHA 上述 Lua 脚本，传入 keys/args。**O(1)，原子，单次 Redis round-trip**。

## 5. 实战：API 网关限流

```yaml
# 网关配置（伪代码）
user_quota = {
  capacity: 100,    # 桶 100 个令牌
  rate: 10         # 每秒补充 10 个
}
# 用户单秒能调用 10 次（持续），但可以突发到 100 次（桶空前）
```

**业务参数**：
- 普通用户：b=60, r=1（1 次/秒，突发 60 次）
- VIP 用户：b=600, r=10
- 内部 API：b=10000, r=1000

## 6. 实战：分布式场景

单实例用本地内存（Guava RateLimiter），分布式必须用 Redis（共享令牌数）。

```java
// Spring Boot + Redis + Lua
@Service
public class RateLimiter {
  @Autowired StringRedisTemplate redis;
  public boolean allow(String userId) {
    Long result = redis.execute(redisScript, List.of("rl:" + userId),
      "100", "10", String.valueOf(System.currentTimeMillis()/1000));
    return result == 1;
  }
}
```

## 7. 选型 vs 漏桶 vs 滑动窗口

| 算法 | 突发 | 平滑 | 适用 |
|------|------|------|------|
| **令牌桶** | ✅ 允许 | 平均速率受限 | API 网关（最常用） |
| **漏桶** | ❌ 强制匀速 | 严格 | 流量整形（削峰填谷） |
| **滑动窗口** | 有限 | 平滑 | 实时统计（QPS 监控） |
| **固定窗口** | 边界翻倍 | 突变 | 简单场景 |

**选择**：API 网关首选**令牌桶**；秒杀系统用**滑动窗口 + 排队**。

## 🔗 下一步
- [漏桶 / 滑动窗口](/04-rate-limit/leaky-bucket)
- [分布式限流](/04-rate-limit/distributed)
- [熔断器三态](/05-circuit-breaker/states)
