---
title: 分布式限流
date: 2026-08-15  # date-auto-injected
---

# 🌐 分布式限流

> 在**集群部署**下，每个应用节点独立计数会导致总限流超标。**分布式限流**通过 Redis 集中计数，确保整个集群共享一个限流额度。

## 🎯 为什么需要分布式限流？

```
单机限流（集群部署）：
  Tomcat A：用户调用 100 次（达到限制）
  Tomcat B：用户调用 100 次（达到限制）
  Tomcat C：用户调用 100 次（达到限制）
  
  实际：用户调用了 300 次（超过限制 200 次！）❌

分布式限流：
  Redis 集中计数：用户调用 100 次（达到限制）
  Tomcat A / B / C 任意节点调用 → 都从 Redis 拿计数
  
  实际：用户只能调用 100 次 ✅
```

## 🔧 方案 1：Redis 集中计数

### 令牌桶（Lua 脚本）

```lua
-- 集群共享一个 bucket，所有节点都操作这个 key
-- KEYS[1] = bucket key（全局唯一）
-- ARGV[1] = capacity
-- ARGV[2] = refill_rate
-- ARGV[3] = now (ms)
-- ARGV[4] = requested

local bucket = redis.call('HMGET', KEYS[1], 'tokens', 'last_refill')
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local requested = tonumber(ARGV[4])

local tokens = tonumber(bucket[1]) or capacity
local last_refill = tonumber(bucket[2]) or now

-- 补充令牌
local elapsed = (now - last_refill) / 1000
tokens = math.min(capacity, tokens + elapsed * refill_rate)

if tokens >= requested then
    tokens = tokens - requested
    redis.call('HMSET', KEYS[1], 'tokens', tokens, 'last_refill', now)
    redis.call('PEXPIRE', KEYS[1], 60000)
    return tokens * 1000  -- 剩余令牌数（放大 1000）
end

redis.call('HMSET', KEYS[1], 'tokens', tokens, 'last_refill', now)
redis.call('PEXPIRE', KEYS[1], 60000)
return 0
```

### Java 实现

```java
@Component
public class DistributedRateLimiter {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    private static final String TOKEN_BUCKET_LUA = "...";  // 上面的 Lua 脚本
    
    public boolean tryAcquire(String key, int capacity, int refillRate, int requested) {
        String now = String.valueOf(System.currentTimeMillis());
        
        DefaultRedisScript<Long> script = new DefaultRedisScript<>(TOKEN_BUCKET_LUA, Long.class);
        Long result = redisTemplate.execute(script,
            Arrays.asList("ratelimit:" + key),
            String.valueOf(capacity),
            String.valueOf(refillRate),
            now,
            String.valueOf(requested)
        );
        
        // 返回值 > 0 表示通过
        return result != null && result > 0;
    }
}
```

## 🔧 方案 2：Redisson 分布式限流

```java
@Component
public class RedissonDistributedLimiter {
    
    @Autowired
    private RedissonClient redisson;
    
    public boolean tryAcquire(String key, int rate, int rateInterval) {
        // 全局限流（集群共享）
        RRateLimiter limiter = redisson.getRateLimiter(key);
        
        // RateType.OVERALL = 集群共享
        // RateType.PER_CLIENT = 每客户端独立
        limiter.trySetRate(RateType.OVERALL, rate, rateInterval, RateIntervalUnit.SECONDS);
        
        return limiter.tryAcquire(1);  // 申请 1 个许可
    }
}

// 使用
boolean ok = redissonLimiter.tryAcquire("order:create", 1000, 1);
// 整个集群每秒最多创建 1000 个订单
```

**两种 RateType 对比**：
```
RateType.OVERALL：
  - 集群共享一个限流额度
  - 适用：全局限流（如秒杀系统总限流 1000 QPS）

RateType.PER_CLIENT：
  - 每个 Redisson 客户端独立限流
  - 适用：分布式限流失效时的兜底
```

## 🔧 方案 3：滑动窗口（ZSet 分布式实现）

```java
@Component
public class DistributedSlidingWindow {
    
    private static final String LUA_SCRIPT = "...";
    
    public boolean tryAcquire(String key, int limit, long windowMs) {
        String now = String.valueOf(System.currentTimeMillis());
        String uuid = UUID.randomUUID().toString();
        
        DefaultRedisScript<Long> script = new DefaultRedisScript<>(LUA_SCRIPT, Long.class);
        Long result = redisTemplate.execute(script,
            Arrays.asList("sliding:" + key),
            now, String.valueOf(windowMs), String.valueOf(limit), uuid
        );
        
        return result != null && result == 1;
    }
}

// 使用：集群每秒最多 1000 次调用
boolean ok = slidingWindow.tryAcquire("api:hot-product", 1000, 1000);
```

## 🛠️ 实战：秒杀系统分布式限流

```java
@Service
public class SeckillService {
    
    @Autowired
    private DistributedRateLimiter rateLimiter;
    
    public void seckill(Long userId, Long productId) {
        // 1. 全局限流（整个集群每秒最多 1 万次）
        if (!rateLimiter.tryAcquire("seckill:global", 10000, 10000, 1)) {
            throw new BusinessException("活动太火爆，请稍后重试");
        }
        
        // 2. 商品限流（每个商品每秒最多 1000 次）
        if (!rateLimiter.tryAcquire("seckill:product:" + productId, 1000, 1000, 1)) {
            throw new BusinessException("该商品太火爆，请稍后重试");
        }
        
        // 3. 用户限流（每个用户每分钟最多 5 次）
        if (!rateLimiter.tryAcquire("seckill:user:" + userId, 5, 60, 1)) {
            throw new BusinessException("您的操作太频繁");
        }
        
        // 4. 业务处理
        processSeckill(userId, productId);
    }
}
```

## 📊 分布式限流 vs 单机限流

| 维度 | 单机限流 | 分布式限流 |
|------|---------|-----------|
| **实现** | Guava RateLimiter / Semaphore | Redis Lua / Redisson |
| **精度** | 高 | 略低（网络开销） |
| **多节点** | ❌ 各节点独立 | ✅ 全集群共享 |
| **Redis 依赖** | 无 | 强依赖 |
| **性能** | 极高 | 略低（一次网络） |
| **适用** | 局部限流 | 全局限流 |

## 🛠️ 实战：Nginx + Redis 二级限流

```nginx
# nginx.conf
http {
    # Nginx 限流（第一层）
    limit_req_zone $binary_remote_addr zone=ip_limit:10m rate=10r/s;
    
    server {
        location /api/ {
            limit_req zone=ip_limit burst=20 nodelay;
            proxy_pass http://backend;
        }
    }
}
```

```java
// 应用层限流（第二层）
@Component
public class GlobalRateLimitInterceptor {
    
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        String key = "global:" + request.getRequestURI();
        
        // 总限流（集群共享）
        if (!rateLimiter.tryAcquire(key, 1000, 1, 1)) {
            return false;  // 限流
        }
        
        return true;
    }
}
```

```
两层限流的好处：
  - Nginx 层：防 DDoS、防爬虫（粗粒度）
  - 应用层：业务限流、用户限流（细粒度）
```

## ⚠️ 分布式限流的坑

### 坑 1：Redis 单点瓶颈

```
场景：所有节点都打 Redis 集中计数
问题：Redis QPS 压力大
解决：
  1. 本地缓存（每节点缓存部分限额）
  2. 限流 + 采样（如只对 10% 请求计数）
  3. 多 Redis 实例分摊
```

### 坑 2：Redis 不可用

```
场景：Redis 挂掉，限流失效
策略：
  1. Fail-Open：Redis 挂了放行所有请求（保护业务）
  2. Fail-Close：Redis 挂了拒绝所有请求（保护系统）
  推荐：Fail-Open + 业务降级
```

### 坑 3：时间窗口边界

```
场景：使用系统时间，多节点时钟不一致
解决：
  1. 使用 NTP 同步时钟
  2. 使用 Redis 时间（TIME 命令）
  3. 接受小幅误差
```

## 🛠️ 实战：Spring Boot + Redisson 多级限流

```java
@Component
public class MultiLevelRateLimiter {
    
    @Autowired
    private RedissonClient redisson;
    
    public boolean tryAcquire(Long userId, String apiPath) {
        // L1: 全局限流（每秒 10 万次）
        RRateLimiter global = redisson.getRateLimiter("global:" + apiPath);
        global.trySetRate(RateType.OVERALL, 100_000, 1, RateIntervalUnit.SECONDS);
        if (!global.tryAcquire()) return false;
        
        // L2: 用户限流（每用户每秒 100 次）
        RRateLimiter user = redisson.getRateLimiter("user:" + userId + ":" + apiPath);
        user.trySetRate(RateType.OVERALL, 100, 1, RateIntervalUnit.SECONDS);
        if (!user.tryAcquire()) return false;
        
        return true;
    }
}
```

## 🎯 总结

**分布式限流核心要点**：
- ✅ Redis 集中计数，全集群共享
- ✅ Lua 脚本保证原子性
- ✅ Redisson RRateLimiter 简化实现
- ✅ 多级限流：全局 + 用户 + 接口
- ⚠️ Redis 单点：考虑本地缓存或 Fail-Open
- ⚠️ 时钟不一致：使用 Redis TIME 或 NTP 同步

**下一步：** [📨 Stream 消息队列](/06-practice/stream-mq) — Redis Stream 实战

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
