---
title: 限流
---

# 🚦 限流

> **限流（Rate Limiting）**是保护系统稳定性的重要手段：在高并发场景下，限制每个用户/接口的访问速率，防止系统过载。

## 🎯 限流算法

```
1. 固定窗口（Fixed Window）
   - 最简单，1 秒一个窗口
   - 问题：临界问题

2. 滑动窗口（Sliding Window）
   - 更精确，平滑过渡
   - 实现：ZSet + 时间戳

3. 令牌桶（Token Bucket）
   - 平滑限流，允许突发
   - 实现：Lua 脚本原子操作

4. 漏桶（Leaky Bucket）
   - 严格匀速
   - 实现：Lua 脚本
```

## 📊 4 种算法对比

| 维度 | 固定窗口 | 滑动窗口 | 令牌桶 | 漏桶 |
|------|---------|---------|--------|------|
| **精确度** | 低 | 高 | 高 | 高 |
| **允许突发** | ✅ | ✅ | ✅ | ❌ |
| **实现难度** | 简单 | 中等 | 中等 | 中等 |
| **内存开销** | O(1) | O(N) | O(1) | O(1) |
| **适用场景** | 简单限流 | 平滑限流 | 流量整形 | 严格限速 |

## 📝 方案 1：固定窗口（INCR + EXPIRE）

```java
public boolean tryAcquire(String key, int limit, int windowSeconds) {
    Long current = redisTemplate.opsForValue().increment(key);
    
    if (current != null && current == 1) {
        redisTemplate.expire(key, windowSeconds, TimeUnit.SECONDS);
    }
    
    return current != null && current <= limit;
}

// 使用：每个用户每分钟最多 100 次
boolean ok = tryAcquire("ratelimit:user:" + userId, 100, 60);
```

**问题（临界问题）**：
```
时间窗口：[0~1秒][1~2秒][2~3秒]
用户在 0.9 秒时调用 100 次（达到限制）
用户在 1.1 秒时又调用 100 次
实际在 0.2 秒内调用了 200 次（超过系统限制！）
```

## 📝 方案 2：滑动窗口（ZSet）

```lua
-- KEYS[1] = ratelimit key
-- ARGV[1] = current timestamp (ms)
-- ARGV[2] = window size (ms)
-- ARGV[3] = limit
-- ARGV[4] = unique id (UUID)

-- 删除窗口外的请求
redis.call('ZREMRANGEBYSCORE', KEYS[1], 0, ARGV[1] - ARGV[2])

-- 当前窗口内的请求数
local count = redis.call('ZCARD', KEYS[1])

if count >= tonumber(ARGV[3]) then
    return 0  -- 限流
end

-- 记录本次请求
redis.call('ZADD', KEYS[1], ARGV[1], ARGV[4])

-- 设置过期时间（避免内存泄漏）
redis.call('PEXPIRE', KEYS[1], ARGV[2])

return 1  -- 通过
```

```java
public boolean tryAcquire(String key, int limit, int windowMs) {
    String now = String.valueOf(System.currentTimeMillis());
    String uuid = UUID.randomUUID().toString();
    
    DefaultRedisScript<Long> script = new DefaultRedisScript<>(SLIDING_WINDOW_LUA, Long.class);
    Long result = redisTemplate.execute(script,
        Arrays.asList(key),
        now, String.valueOf(windowMs), String.valueOf(limit), uuid
    );
    
    return result != null && result == 1;
}
```

## 📝 方案 3：令牌桶（Lua）

```lua
-- KEYS[1] = bucket key
-- ARGV[1] = capacity (max tokens)
-- ARGV[2] = refill rate (tokens per second)
-- ARGV[3] = current timestamp (ms)
-- ARGV[4] = requested tokens

local bucket = redis.call('HMGET', KEYS[1], 'tokens', 'last_refill')
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local tokens = tonumber(bucket[1]) or capacity
local last_refill = tonumber(bucket[2]) or now

-- 补充令牌
local elapsed = (now - last_refill) / 1000
local refill = elapsed * refill_rate
tokens = math.min(capacity, tokens + refill)

if tokens >= requested then
    tokens = tokens - requested
    redis.call('HMSET', KEYS[1], 'tokens', tokens, 'last_refill', now)
    redis.call('PEXPIRE', KEYS[1], 60000)
    return 1
end

redis.call('HMSET', KEYS[1], 'tokens', tokens, 'last_refill', now)
redis.call('PEXPIRE', KEYS[1], 60000)
return 0
```

```java
public boolean tryAcquire(String key, int capacity, int refillRate, int requested) {
    String now = String.valueOf(System.currentTimeMillis());
    
    DefaultRedisScript<Long> script = new DefaultRedisScript<>(TOKEN_BUCKET_LUA, Long.class);
    Long result = redisTemplate.execute(script,
        Arrays.asList(key),
        String.valueOf(capacity), String.valueOf(refillRate), now, String.valueOf(requested)
    );
    
    return result != null && result == 1;
}
```

## 📝 方案 4：漏桶（Lua）

```lua
-- 漏桶：固定速率流出
-- 如果桶已满，请求被拒绝

local bucket = redis.call('HMGET', KEYS[1], 'water', 'last_leak')
local capacity = tonumber(ARGV[1])
local leak_rate = tonumber(ARGV[2])  -- 每秒漏出多少
local now = tonumber(ARGV[3])

local water = tonumber(bucket[1]) or 0
local last_leak = tonumber(bucket[2]) or now

-- 漏水
local elapsed = (now - last_leak) / 1000
water = math.max(0, water - elapsed * leak_rate)

-- 注水
if water + 1 <= capacity then
    water = water + 1
    redis.call('HMSET', KEYS[1], 'water', water, 'last_leak', now)
    redis.call('PEXPIRE', KEYS[1], 60000)
    return 1
end

redis.call('HMSET', KEYS[1], 'water', water, 'last_leak', now)
redis.call('PEXPIRE', KEYS[1], 60000)
return 0
```

## 🛠️ Spring Boot 拦截器实战

```java
@Component
public class RateLimitInterceptor implements HandlerInterceptor {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    private static final int LIMIT = 100;
    private static final int WINDOW_MS = 60_000;
    
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        // 1. 获取用户标识
        Long userId = (Long) request.getAttribute("userId");
        if (userId == null) {
            return true;
        }
        
        // 2. 限流检查
        String key = "ratelimit:user:" + userId;
        boolean ok = slidingWindow(key, LIMIT, WINDOW_MS);
        
        if (!ok) {
            // 3. 限流处理
            response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
            response.setHeader("Retry-After", "60");
            response.getWriter().write("{\"code\":429,\"msg\":\"请求过快\"}");
            return false;
        }
        
        return true;
    }
    
    private boolean slidingWindow(String key, int limit, int windowMs) {
        String now = String.valueOf(System.currentTimeMillis());
        String uuid = UUID.randomUUID().toString();
        
        DefaultRedisScript<Long> script = new DefaultRedisScript<>(SLIDING_WINDOW_LUA, Long.class);
        Long result = redisTemplate.execute(script,
            Arrays.asList(key),
            now, String.valueOf(windowMs), String.valueOf(limit), uuid
        );
        
        return result != null && result == 1;
    }
}
```

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    
    @Autowired
    private RateLimitInterceptor rateLimitInterceptor;
    
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(rateLimitInterceptor)
            .addPathPatterns("/api/**")
            .excludePathPatterns("/api/login", "/api/register");
    }
}
```

## 📊 Redisson 限流器

```java
@Component
public class RedissonRateLimiter {
    
    @Autowired
    private RedissonClient redisson;
    
    public boolean tryAcquire(String key, int rate, int rateInterval) {
        RRateLimiter limiter = redisson.getRateLimiter(key);
        
        // 设置限流规则
        limiter.trySetRate(RateType.OVERALL, rate, rateInterval, RateIntervalUnit.SECONDS);
        
        // 尝试获取许可
        return limiter.tryAcquire();
    }
}

// 使用：每用户每秒 100 次
boolean ok = rateLimiter.tryAcquire("ratelimit:user:" + userId, 100, 1);
```

## 🎯 选型建议

```
✅ 简单场景：固定窗口（INCR + EXPIRE）
✅ 精确限流：滑动窗口（ZSet + Lua）
✅ 允许突发：令牌桶（Lua 实现）
✅ 严格匀速：漏桶（Lua 实现）
✅ 企业级：Redisson RRateLimiter（封装好）
```

## ⚠️ 限流策略

```java
// 1. 全局限流：所有用户共享一个限流器
//    适用：总流量保护

// 2. 用户限流：每个用户独立限流器
//    适用：防止单个用户滥用

// 3. IP 限流：基于 IP 限流
//    适用：防爬虫、防攻击

// 4. 接口限流：每个接口独立限流
//    适用：保护关键接口

// 5. 多级限流：组合使用
//    全局 + 用户 + 接口 三级限流
```

## 🎯 总结

**限流核心要点**：
- ✅ 4 种算法：固定 / 滑动 / 令牌 / 漏桶
- ✅ Redis + Lua 原子保证
- ✅ Spring 拦截器自动限流
- ✅ Redisson RRateLimiter 简化开发
- ⚠️ 临界问题：固定窗口有边界效应
- ⚠️ 选型：业务量、精度要求综合考虑

**下一步：** [🌐 分布式限流](/06-practice/distributed-ratelimit) — 集群环境下的精确限流
