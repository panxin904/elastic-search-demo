---
title: 漏桶 / 滑动窗口
---
# 漏桶 + 滑动窗口

## 1. 漏桶算法

水滴匀速流出，无论输入多快，输出都是恒定速率。

```
      输入
       ↓ 任意速率
   ┌───────────┐
   │  桶（队列）  │  桶满 → 溢出（拒绝/丢弃）
   └─────┬─────┘
         ↓ 恒定速率 r
       输出
```

**特点**：
- 严格匀速（无法应对突发）
- 实现简单（队列 + 定时器）
- 适合流量整形（Traffic Shaping）

## 2. 漏桶 vs 令牌桶

| | 令牌桶 | 漏桶 |
|--|--------|------|
| 突发允许 | ✅ 桶内令牌可累积 | ❌ 超出即拒绝 |
| 平滑性 | 平均速率受控 | 严格匀速 |
| 流量整形 | 弱 | 强 |
| 算法 | 复杂 | 简单 |
| 场景 | API 网关 | 网络 QoS |

## 3. 滑动窗口算法

把固定窗口的"硬边界"变成"滚动边界"，解决"边界翻倍"问题。

```
固定窗口（每分钟 100）：
  11:59:59 请求 100 → 拒绝
  12:00:00 又是 100 → 允许
  → 2 秒内 200 请求，违反"100/分钟"语义

滑动窗口：
  12:00:30 的请求 → 看 [11:59:30, 12:00:30] 这 60 秒
  → 精确按时间窗口统计
```

## 4. 滑动窗口实现

```java
// SlidingWindowCounter
class SlidingWindow {
  Queue<Long> timestamps = new ArrayDeque<>();
  int limit;
  int windowMs;
  
  boolean allow(long now) {
    // 移除窗口外的
    while (!timestamps.isEmpty() && now - timestamps.peek() > windowMs) {
      timestamps.poll();
    }
    if (timestamps.size() < limit) {
      timestamps.offer(now);
      return true;
    }
    return false;
  }
}
```

**复杂度**：O(limit) 空间 + O(1) 摊销时间（每个请求最多一次 poll）。

## 5. 滑动日志（精确但占空间）

存每个请求的时间戳 → 精确但 O(limit) 空间。

## 6. 滑动计数（折中）

按时间分桶（如每 100ms 一格），移动窗口叠加最近 N 格：

```
[t=0.0]  [t=0.1]  [t=0.2]  ...  [t=1.0]
  5        8        3              2
sum = 5+8+3+...+2  =  N
```

**复杂度**：O(窗口大小) 空间、O(1) 时间。

## 7. Redis 滑动窗口实现

```lua
-- KEYS[1] = key
-- ARGV[1] = limit
-- ARGV[2] = window seconds
-- ARGV[3] = now (sec)
-- ARGV[4] = unique key (e.g. user id, for tracking individual requests)
-- ARGV[5] = request id (for ZADD uniqueness)

-- Remove old entries
redis.call("ZREMRANGEBYSCORE", KEYS[1], 0, tonumber(ARGV[3]) - tonumber(ARGV[2]))

-- Count current entries
local count = redis.call("ZCARD", KEYS[1])

if count < tonumber(ARGV[1]) then
  redis.call("ZADD", KEYS[1], tonumber(ARGV[3]), ARGV[4] .. ":" .. ARGV[5])
  redis.call("EXPIRE", KEYS[1], tonumber(ARGV[2]))
  return 1
else
  return 0
end
```

## 8. 实战：多级限流

```
用户层：每用户 100 QPS（令牌桶）
接口层：每接口 1000 QPS（令牌桶）
集群层：总流量 100K QPS（漏桶）
```

多级限流 = 任一级超限就拒绝。

## 9. 选型

| 场景 | 算法 |
|------|------|
| API 网关 | 令牌桶（允许突发） |
| 秒杀 | 滑动窗口 + 队列 |
| 流量整形 | 漏桶 |
| 简单限流 | 固定窗口（实现最简） |
| 实时 QPS 监控 | 滑动窗口 |

## 🔗 下一步
- [令牌桶算法](/04-rate-limit/token-bucket)
- [分布式限流](/04-rate-limit/distributed)
- [熔断器三态](/05-circuit-breaker/states)
