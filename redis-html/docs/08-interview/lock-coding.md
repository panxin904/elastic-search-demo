---
title: 分布式锁手撕
---

# 🔒 分布式锁手撕

> 字节、阿里、腾讯高频手撕题。本篇实现一个**完整生产级** Redis 分布式锁，覆盖：原子加锁、UUID 防误删、Lua 原子释放、可重入、Watch Dog 续期、锁超时保护。

## 一、题目描述

> 实现一个 Redis 分布式锁，要求：
> 1. 互斥：同一时刻只有一个客户端持有锁。
> 2. 防误删：释放锁时只能删除自己加的锁。
> 3. 可重入：同一线程可多次加锁（递归调用场景）。
> 4. 容错：持锁客户端崩溃后锁能自动释放。
> 5. 续期：长任务执行时锁不过期。
> 6. 单点故障兜底：Redis 主从切换时锁尽量不丢。

## 二、v1 最简版（基础）

只满足前 4 个要求：

```java
public class SimpleRedisLock {

    private final StringRedisTemplate redis;
    private final String lockKey;
    private final String lockValue;     // UUID + 线程 ID
    private final long expireMillis;

    public SimpleRedisLock(StringRedisTemplate redis,
                           String lockKey,
                           long expireMillis) {
        this.redis = redis;
        this.lockKey = lockKey;
        this.lockValue = UUID.randomUUID() + ":" + Thread.currentThread().getId();
        this.expireMillis = expireMillis;
    }

    /**
     * 原子加锁：SET key value NX PX ttl
     */
    public boolean tryLock() {
        Boolean ok = redis.opsForValue()
            .setIfAbsent(lockKey, lockValue, expireMillis, TimeUnit.MILLISECONDS);
        return Boolean.TRUE.equals(ok);
    }

    /**
     * 原子释放：先校验 value 再 DEL，避免误删别人的锁
     */
    public void unlock() {
        String lua = "if redis.call('get', KEYS[1]) == ARGV[1] then " +
                     "return redis.call('del', KEYS[1]) " +
                     "else return 0 end";
        redis.execute(new DefaultRedisScript<>(lua, Long.class),
            Collections.singletonList(lockKey), lockValue);
    }
}
```

**核心要点**

- `SET NX PX` 一条命令搞定原子加锁 + 设过期，杜绝老版本 `SETNX + EXPIRE` 的中间态。
- 用 UUID 防误删，删除前必须**先 GET 比较再 DEL**。这两步必须用 Lua 保证原子性。

**缺陷**

- 不可重入：同一线程第二次加锁会失败。
- 无续期：任务执行时间超过 expireMillis 会导致锁提前释放。
- 主从切换可能丢锁。

## 三、v2 生产级（可重入 + 续期 + 单点故障保护）

完整代码：

```java
public class RedisDistributedLock {

    private static final String LOCK_PREFIX = "lock:";
    private static final long DEFAULT_EXPIRE_MS = 30_000;     // 默认 30 秒
    private static final long WATCHDOG_PERIOD_MS = 10_000;   // 看门狗 10 秒续期一次

    private final StringRedisTemplate redis;
    private final String lockKey;
    private final String lockValue;
    private final long expireMillis;

    /** 每个线程独立的可重入计数 + 看门狗 */
    private static final ThreadLocal<LockHolder> HOLDER = new ThreadLocal<>();

    /** 看门狗调度器 */
    private static final ScheduledExecutorService WATCHDOG =
        Executors.newScheduledThreadPool(1, r -> {
            Thread t = new Thread(r, "redis-lock-watchdog");
            t.setDaemon(true);
            return t;
        });

    public RedisDistributedLock(StringRedisTemplate redis, String resource) {
        this(redis, resource, DEFAULT_EXPIRE_MS);
    }

    public RedisDistributedLock(StringRedisTemplate redis,
                                String resource,
                                long expireMillis) {
        this.redis = redis;
        this.lockKey = LOCK_PREFIX + resource;
        this.lockValue = UUID.randomUUID().toString();
        this.expireMillis = expireMillis;
    }

    /**
     * 可重入加锁。
     * 同线程再次调用 → 计数 +1，直接返回成功。
     * 异线程 → 阻塞自旋抢锁，最多等 waitMillis。
     */
    public boolean tryLock(long waitMillis) throws InterruptedException {
        // 可重入：当前线程已持有 → 计数 +1
        LockHolder holder = HOLDER.get();
        if (holder != null && holder.lockValue.equals(lockValue)) {
            holder.reentrantCount++;
            return true;
        }

        long deadline = System.currentTimeMillis() + waitMillis;
        while (System.currentTimeMillis() < deadline) {
            if (tryLockOnce()) {
                // 启动看门狗续期
                startWatchdog();
                HOLDER.set(new LockHolder(lockValue, 1));
                return true;
            }
            Thread.sleep(50); // 50ms 重试一次
        }
        return false;
    }

    public void unlock() {
        LockHolder holder = HOLDER.get();
        if (holder == null || !holder.lockValue.equals(lockValue)) {
            throw new IllegalStateException("当前线程未持有该锁");
        }

        // 可重入：计数 > 1 时只减计数，不释放
        if (holder.reentrantCount > 1) {
            holder.reentrantCount--;
            return;
        }

        // 真正释放：CAS 用 Lua 原子校验 + DEL
        String lua = "if redis.call('get', KEYS[1]) == ARGV[1] then " +
                     "return redis.call('del', KEYS[1]) " +
                     "else return 0 end";
        Long deleted = redis.execute(new DefaultRedisScript<>(lua, Long.class),
            Collections.singletonList(lockKey), lockValue);

        stopWatchdog();
        HOLDER.remove();

        if (deleted == null || deleted == 0) {
            // 锁已被自动过期释放，但业务已完成，正常返回
        }
    }

    /* ----------------------- 内部方法 ----------------------- */

    private boolean tryLockOnce() {
        Boolean ok = redis.opsForValue().setIfAbsent(
            lockKey, lockValue, expireMillis, TimeUnit.MILLISECONDS);
        return Boolean.TRUE.equals(ok);
    }

    private final ScheduledFuture<?>[] watchdogFuture = new ScheduledFuture<?>[1];

    private void startWatchdog() {
        // 续期 = expireMillis / 3，即默认 10 秒续到 30 秒
        long renewPeriod = expireMillis / 3;
        watchdogFuture[0] = WATCHDOG.scheduleAtFixedRate(() -> {
            try {
                // 仅当仍是自己的锁才续期（防止误续期别人接管的锁）
                String lua = "if redis.call('get', KEYS[1]) == ARGV[1] then " +
                             "return redis.call('pexpire', KEYS[1], ARGV[2]) " +
                             "else return 0 end";
                redis.execute(new DefaultRedisScript<>(lua, Long.class),
                    Collections.singletonList(lockKey),
                    lockValue, String.valueOf(expireMillis));
            } catch (Exception e) {
                // 续期失败说明 Redis 不可达，等待下一次重试
            }
        }, renewPeriod, renewPeriod, TimeUnit.MILLISECONDS);
    }

    private void stopWatchdog() {
        if (watchdogFuture[0] != null) {
            watchdogFuture[0].cancel(false);
            watchdogFuture[0] = null;
        }
    }

    /** 线程局部持有者 */
    private static class LockHolder {
        final String lockValue;
        int reentrantCount;

        LockHolder(String lockValue, int count) {
            this.lockValue = lockValue;
            this.reentrantCount = count;
        }
    }
}
```

## 四、Redisson 看门狗原理

Redisson 是 Java 生态最流行的 Redis 客户端，分布式锁是其核心特性。看门狗实现比上面的 demo 更精细：

```java
// Redisson 源码简化版：org.redisson.RedissonLock
private void scheduleExpirationRenewal(long threadId) {
    ExpirationEntry entry = new ExpirationEntry();
    // entry 只保存一次（首次加锁时），可重入不重复创建
    ExpirationEntry oldEntry = EXPIRATION_RENEWAL_MAP
        .putIfAbsent(getEntryName(), entry);
    if (oldEntry != null) {
        // 已存在 → 可重入
        oldEntry.addThreadId(threadId);
    } else {
        entry.addThreadId(threadId);
        // 关键：续期任务，internalLockLeaseTime / 3 = 10s 续一次
        renewExpiration();
    }
}

private void renewExpiration() {
    Timeout task = getServiceManager().newTimeout(t -> {
        ExpirationEntry ent = EXPIRATION_RENEWAL_MAP.get(getEntryName());
        if (ent == null) return;

        Long threadId = ent.getFirstThreadId();
        if (threadId == null) return;

        // 异步续期到 30 秒
        CompletionStage<Boolean> future = renewLeaseAsync(threadId);
        future.whenComplete((result, e) -> {
            if (e == null && result) {
                // 续期成功 → 递归调度下一次续期
                renewExpiration();
            } else {
                // 续期失败（锁不在了）→ 取消
                cancelExpirationRenewal(null);
            }
        });
    }, internalLockLeaseTime / 3, TimeUnit.MILLISECONDS);
    entry.setTimeout(task);
}
```

**Redisson 关键设计**

| 特性 | 实现 |
|------|------|
| 默认锁过期时间 | `lockWatchdogTimeout = 30s` |
| 续期周期 | `internalLockLeaseTime / 3 = 10s` |
| 续期 Lua | `pexpire` 续期 + value 校验 |
| 可重入 | 用 Hash 结构存 `threadId → 重入次数` |
| 主从切换 | 单 Redis 实例（不解决 Redlock 场景） |
| Redisson MultiLock | Redlock 算法的工程实现 |

## 五、Redlock 多实例实现

为应对单 Redis 实例宕机导致的锁丢失问题：

```java
public class Redlock {

    private final List<StringRedisTemplate> redises;
    private final int quorum;        // 至少 N/2 + 1 成功
    private final long validityTime; // 锁有效时间 ms
    private final long clockDrift;   // 时钟漂移容忍

    public Redlock(List<StringRedisTemplate> redises) {
        this.redises = redises;
        this.quorum = redises.size() / 2 + 1;
        this.validityTime = 30_000;
        this.clockDrift = 100; // 100ms 漂移
    }

    public boolean tryLock(String resource, long waitMillis) {
        long start = System.currentTimeMillis();
        int successCount = 0;

        for (StringRedisTemplate redis : redises) {
            Boolean ok = redis.opsForValue().setIfAbsent(
                "lock:" + resource, UUID.randomUUID().toString(),
                validityTime, TimeUnit.MILLISECONDS);
            if (Boolean.TRUE.equals(ok)) successCount++;
        }

        long elapsed = System.currentTimeMillis() - start;
        long drift = (long) (validityTime * 0.01) + clockDrift;

        if (successCount >= quorum && elapsed < validityTime - drift) {
            return true;
        }

        // 失败回滚：向所有实例尝试 DEL
        for (StringRedisTemplate redis : redises) {
            try {
                redis.delete("lock:" + resource);
            } catch (Exception ignored) {}
        }
        return false;
    }
}
```

**Redlock 的工程争议**

- **Martin Kleppmann** 认为 Redlock 依赖系统时钟，时钟跳跃（NTP 调整、闰秒）会让锁失效。
- **antirez** 反驳称时钟跳跃是小概率事件，且 quorum 机制能容忍 1~2 个节点异常。
- **生产实践**：90% 场景用 **Zookeeper** 或 **etcd** 实现强一致分布式锁，Redis 锁用于允许偶尔失败的场景（如幂等保护）。

## 六、面试追问清单

| 追问 | 回答要点 |
|------|----------|
| 为什么不用 `SETNX + EXPIRE`？ | 两条命令非原子，EXPIRE 失败会死锁 |
| 为什么用 Lua 释放？ | GET + DEL 非原子，中间状态可能误删别人的锁 |
| 续期失败怎么办？ | 不阻塞业务，下次续期会成功；若锁已过期则业务可能并发执行，靠幂等兜底 |
| 主从切换会丢锁吗？ | 会。setnx 到主后异步复制前主宕机，从升主后无锁信息。Redlock / ZK 可缓解 |
| Redisson 和自己实现的区别？ | Redisson 提供阻塞、可中断、公平锁、读写锁、信号量等完整抽象，且集成 Netty / Lua 缓存 |

## 七、下一步

分布式锁的核心是"原子加锁 + 防误删 + 容错"。下一篇实现另一个经典算法：**LRU 缓存淘汰**，字节跳动常考原题。

**下一步：** [📚 LRU 算法手撕](/08-interview/lru)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
