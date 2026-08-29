---
title: 分布式锁
date: 2026-08-15  # date-auto-injected
---

# 🔒 分布式锁

> 分布式系统中，多个进程需要对**共享资源**进行互斥访问。Redis 凭借其**单线程命令执行**特性，是实现分布式锁的经典方案。

<ClientOnly>
  <DistributedLock />
</ClientOnly>

## 🎯 分布式锁的 4 个核心要求

```
1. 互斥（Mutual Exclusion）
   - 任意时刻只有一个客户端持有锁
2. 防死锁（Deadlock Free）
   - 即使持有锁的客户端崩溃，锁也要能被释放
3. 容错（Fault Tolerance）
   - 只要大部分 Redis 节点正常，锁就能正常服务
4. 可重入（Reentrant）
   - 同一线程可多次获取同一把锁
```

## ⚠️ 错误的实现：SETNX + EXPIRE

```java
// ❌ 致命问题：两个操作不是原子的
jedis.setnx("lock:order:1001", "request_id");
jedis.expire("lock:order:1001", 30);

// 问题：
// 1. SETNX 成功后，客户端崩溃，EXPIRE 没执行
// 2. 锁永远不会释放，死锁！
```

## ⚠️ 半正确：SET NX EX（原子但无续期）

```java
// ✅ 原子操作
String result = jedis.set("lock:order:1001", "request_id", SetParams.setParams().nx().ex(30));

// 问题：
// 1. 业务执行时间超过 30 秒
// 2. 锁自动释放，其他线程可能拿到锁
// 3. 业务未完成，锁已被释放（数据不一致！）
```

## ✅ 正确实现：Redisson 看门狗

> Redisson 的 **看门狗（Watchdog）**机制：自动续期锁。

```java
RLock lock = redisson.getLock("lock:order:1001");

// 1. 加锁（默认 30 秒过期，看门狗每 10 秒续期）
lock.lock();
try {
    // 业务逻辑（可执行任意长时间）
    doBusiness();
} finally {
    // 2. 释放锁
    lock.unlock();
}

// 推荐：tryLock 带超时
if (lock.tryLock(5, 10, TimeUnit.SECONDS)) {
    try {
        doBusiness();
    } finally {
        if (lock.isHeldByCurrentThread()) {
            lock.unlock();
        }
    }
}
```

### 看门狗原理

```
时间线：
  T0    客户端 A 加锁成功（30 秒过期）
  T0    看门狗启动：每 10 秒续期一次
  T10   续期：expire = 30 秒
  T20   续期：expire = 30 秒
  T30   续期：expire = 30 秒
  ...
  T90   业务执行完，客户端 A 调用 unlock
  T90   看门狗停止续期
  T90   锁释放，客户端 B 可加锁

关键源码（scheduleExpirationRenewal）：
  - 启动 ScheduledFuture，每 10 秒执行续期任务
  - 续期 Lua 脚本：
    if redis.call('hexists', KEYS[1], ARGV[2]) == 1 then
        redis.call('pexpire', KEYS[1], ARGV[1])
        return 1
    else
        return 0
    end
```

## 🛠️ 手动实现分布式锁（不依赖 Redisson）

### 加锁（Lua 脚本）

```lua
-- KEYS[1] = lock key
-- ARGV[1] = request id
-- ARGV[2] = expire milliseconds
if redis.call('EXISTS', KEYS[1]) == 0 then
    redis.call('HSET', KEYS[1], ARGV[1], '1')
    redis.call('PEXPIRE', KEYS[1], ARGV[2])
    return 1
end

-- 检查是否是自己的锁（可重入）
if redis.call('HEXISTS', KEYS[1], ARGV[1]) == 1 then
    redis.call('HINCRBY', KEYS[1], ARGV[1], '1')
    redis.call('PEXPIRE', KEYS[1], ARGV[2])
    return 1
end

return 0
```

### 释放锁（Lua 脚本）

```lua
-- KEYS[1] = lock key
-- ARGV[1] = request id
if redis.call('HEXISTS', KEYS[1], ARGV[1]) == 0 then
    return 0
end

-- 重入次数 -1
local count = redis.call('HINCRBY', KEYS[1], ARGV[1], '-1')
if count == 0 then
    redis.call('DEL', KEYS[1])
    return 1
end
return 0
```

### Java 实现

```java
@Component
public class RedisLock {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    private static final String LOCK_LUA = "...";  // 上面的 Lua 脚本
    
    public boolean tryLock(String key, String requestId, long expireMs) {
        Long result = redisTemplate.execute(
            new DefaultRedisScript<>(LOCK_LUA, Long.class),
            Arrays.asList(key),
            requestId, String.valueOf(expireMs)
        );
        return result != null && result == 1;
    }
    
    public boolean unlock(String key, String requestId) {
        String lua = "if redis.call('hexists', KEYS[1], ARGV[1]) == 0 then " +
                     "return 0 else " +
                     "local count = redis.call('hincrby', KEYS[1], ARGV[1], -1) " +
                     "if count == 0 then return redis.call('del', KEYS[1]) else return 0 end end";
        Long result = redisTemplate.execute(
            new DefaultRedisScript<>(lua, Long.class),
            Arrays.asList(key), requestId
        );
        return result != null && result == 1;
    }
}
```

## 🚀 Redlock（多 Master 集群）

> Redis 作者 antirez 提出的**多 Master 集群分布式锁算法**。

```
Redlock 算法（5 步）：
  1. 获取当前时间（毫秒）
  2. 依次在 N 个独立的 Master 节点上尝试加锁
     （超时时间：锁过期时间 - 获取锁耗时）
  3. 计算加锁总耗时
     （获取锁耗时 = 当前时间 - 步骤 1 时间）
  4. 判定是否加锁成功
     - 在 ≥ N/2+1 个节点上加锁成功
     - 且总耗时 < 锁过期时间
  5. 加锁失败，依次释放所有节点的锁

实际使用少（要求 5 个独立 Master，成本高）。
```

```java
// Redisson RedLock 示例
RLock lock1 = redisson1.getLock("lock");
RLock lock2 = redisson2.getLock("lock");
RLock lock3 = redisson3.getLock("lock");

RedissonRedLock redLock = new RedissonRedLock(lock1, lock2, lock3);
redLock.lock();
try {
    // 业务逻辑
} finally {
    redLock.unlock();
}
```

## 🛠️ 实战：秒杀系统

```java
@Service
public class SeckillService {
    
    @Autowired
    private RedissonClient redisson;
    
    public void seckill(Long userId, Long productId) {
        RLock lock = redisson.getLock("lock:seckill:" + productId);
        
        try {
            if (lock.tryLock(3, 10, TimeUnit.SECONDS)) {
                try {
                    // 1. 查库存
                    int stock = redisTemplate.opsForValue().get("stock:" + productId);
                    if (stock <= 0) {
                        throw new BusinessException("已售罄");
                    }
                    
                    // 2. 减库存（Lua 保证原子）
                    String lua = "if redis.call('get', KEYS[1]) > 0 then " +
                                 "return redis.call('decr', KEYS[1]) else return -1 end";
                    Long result = redisTemplate.execute(
                        new DefaultRedisScript<>(lua, Long.class),
                        Arrays.asList("stock:" + productId)
                    );
                    
                    if (result < 0) {
                        throw new BusinessException("已售罄");
                    }
                    
                    // 3. 创建订单
                    createOrder(userId, productId);
                    
                } finally {
                    lock.unlock();
                }
            } else {
                throw new BusinessException("系统繁忙，请重试");
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new BusinessException("系统错误");
        }
    }
}
```

## ⚠️ 常见误区

### 误区 1：用 GETSET 实现锁

```bash
# ❌ 错误
SET lock:order:1001 <current_time + 30000>
# 问题：多个客户端同时设置，后设置的会覆盖
```

### 误区 2：超时时间过短

```java
// ❌ 锁 1 秒过期，业务执行 5 秒
lock.tryLock(0, 1, TimeUnit.SECONDS);

// ✅ 推荐：锁时间略大于业务超时时间
lock.tryLock(0, 30, TimeUnit.SECONDS);
// 或用 Redisson 看门狗自动续期
```

### 误区 3：不释放锁

```java
// ❌ 业务异常时未释放锁
lock.lock();
doBusiness();   // 抛出异常
lock.unlock();  // 不会执行！

// ✅ try-finally 保证释放
lock.lock();
try {
    doBusiness();
} finally {
    lock.unlock();
}
```

## 🎯 总结

**分布式锁核心要点**：
- ❌ SETNX + EXPIRE：非原子，不安全
- ⚠️ SET NX EX：原子但无续期
- ✅ Redisson 看门狗：自动续期，最佳实践
- ✅ 释放锁必须用 Lua 脚本（CAS）
- ✅ try-finally 保证释放

**下一步：** [👤 分布式 Session](/06-practice/session) — 集群会话共享
