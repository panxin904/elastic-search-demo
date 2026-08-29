---
title: Redisson
date: 2026-08-15  # date-auto-injected
---

# 🔴 Redisson

> **Redisson**是 Redis 官方的**分布式 Java 对象和服务**库，提供丰富的分布式工具：分布式锁、集合、队列、Map、Topic 等。底层基于 Netty。

## 🎯 Redisson 特点

```
✅ 分布式锁（含看门狗自动续期）
✅ 分布式集合（RMap、RList、RQueue、RSet）
✅ 分布式服务（Topic、RemoteService、LiveObject）
✅ 分布式对象（RAtomicLong、RBitSet、RTopic）
✅ 看门狗机制（自动续期，防止锁过期）
✅ 高可扩展性（200+ 分布式对象）
✅ 支持 Redis Sentinel / Cluster / Master-Slave
```

## 📦 引入依赖

```xml
<dependency>
    <groupId>org.redisson</groupId>
    <artifactId>redisson-spring-boot-starter</artifactId>
    <version>3.27.2</version>
</dependency>
```

## 🚀 快速开始

```java
// 1. 直接使用 Redisson 客户端
Config config = new Config();
config.useSingleServer()
    .setAddress("redis://localhost:6379")
    .setPassword("password")
    .setDatabase(0);

RedissonClient redisson = Redisson.create(config);

// 2. Spring Boot 集成（自动配置）
@SpringBootApplication
public class Application { }

# application.yml
spring:
  redis:
    host: localhost
    port: 6379
    password: password

# 自动注入
@Autowired
RedissonClient redisson;
```

## 🔒 分布式锁（核心特性）

### 基本使用

```java
// 获取锁
RLock lock = redisson.getLock("lock:order:1001");

// 加锁（默认 30 秒，看门狗自动续期）
lock.lock();

try {
    // 业务逻辑
    System.out.println("Doing business...");
} finally {
    lock.unlock();
}
```

### tryLock（带超时）

```java
RLock lock = redisson.getLock("lock:order:1001");

// 尝试加锁，最多等待 5 秒，锁 10 秒后自动释放
boolean success = lock.tryLock(5, 10, TimeUnit.SECONDS);

if (success) {
    try {
        // 业务逻辑
    } finally {
        lock.unlock();
    }
} else {
    // 获取锁失败
    throw new RuntimeException("Failed to acquire lock");
}
```

### 看门狗机制

> **Watchdog**是 Redisson 分布式锁的核心，自动续期防止锁过期。

```
锁生命周期：
  1. 加锁成功，默认过期时间 30 秒
  2. 看门狗每 10 秒续期一次（续到 30 秒）
  3. 业务执行完，调用 unlock
  4. 看门狗停止续期，锁释放

为什么需要看门狗？
  - 防止业务执行时间超过 TTL，锁被自动释放
  - 防止其他线程在业务未完成时拿到锁

源码（看门狗续期）：
  - RedissonLock.tryAcquireInnerAsync() 加锁
  - scheduleExpirationRenewal() 启动续期任务
  - 每 lockWatchdogTimeout/3（默认 10s）续期一次
  - 续期 Lua: if redis.call('hexists', KEYS[1], ARGV[2]) == 1 then pexpire KEYS[1] ARGV[1] end
```

### 公平锁 / 读写锁

```java
// 公平锁（FIFO，按请求顺序获取）
RLock fairLock = redisson.getFairLock("lock:fair:order:1001");
fairLock.lock();

// 读写锁
RReadWriteLock rwLock = redisson.getReadWriteLock("lock:rw:user:1001");
RLock readLock = rwLock.readLock();
RLock writeLock = rwLock.writeLock();

// 多线程可同时读
readLock.lock();
try { /* read */ } finally { readLock.unlock(); }

// 写时独占
writeLock.lock();
try { /* write */ } finally { writeLock.unlock(); }

// 联锁（MultiLock，多个锁一起加）
RLock lock1 = redisson.getLock("lock1");
RLock lock2 = redisson.getLock("lock2");
RedissonMultiLock multiLock = new RedissonMultiLock(lock1, lock2);
multiLock.lock();
```

## 📊 分布式集合

```java
// 分布式 Map（Hash 结构）
RMap<String, User> map = redisson.getMap("users");
map.put("user:1", new User("Alice", 28));
User user = map.get("user:1");

// 分布式 List
RList<String> list = redisson.getList("tasks");
list.add("task1");
list.add("task2");
String first = list.remove(0);

// 分布式 Set
RSet<String> set = redisson.getSet("tags");
set.add("redis");
set.add("db");

// 分布式 Queue
RQueue<String> queue = redisson.getQueue("job:queue");
queue.offer("job1");
String job = queue.poll();

// 分布式 Deque（双端队列）
RDeque<String> deque = redisson.getDeque("deque");
deque.addFirst("first");
deque.addLast("last");

// 分布式 BlockingQueue
RBlockingQueue<String> bq = redisson.getBlockingQueue("blocking");
bq.put("task");
String task = bq.take();           // 阻塞获取

// 分布式 DelayedQueue（延迟队列）
RDelayedQueue<String> dq = redisson.getDelayedQueue(bq);
dq.offer("task1", 5, TimeUnit.SECONDS);  // 5 秒后进入队列
```

## 📊 分布式对象

```java
// 分布式 AtomicLong
RAtomicLong counter = redisson.getAtomicLong("counter");
counter.incrementAndGet();              // 原子自增
counter.addAndGet(10);                 // 原子加 10

// 分布式 BitSet
RBitSet bitSet = redisson.getBitSet("bitmap");
bitSet.set(0, true);
bitSet.set(7, true);
boolean v = bitSet.get(7);

// 分布式 Bloom Filter
RBloomFilter<String> filter = redisson.getBloomFilter("filter");
filter.tryInit(100_000_000, 0.01);   // 1 亿容量，1% 误判率
filter.add("user:1");
boolean exists = filter.contains("user:1");

// 分布式 SetBits（HyperLogLog）
RHyperLogLog<String> hll = redisson.getHyperLogLog("uv");
hll.add("user:1");
hll.add("user:2");
long count = hll.count();              // 基数估计
```

## 📨 分布式 Topic（Pub/Sub）

```java
// 发布
RTopic topic = redisson.getTopic("news");
long receivers = topic.publish("Hello World");

// 订阅
RTopic topic = redisson.getTopic("news");
topic.addListener(String.class, (channel, msg) -> {
    System.out.println("Received: " + msg);
});
```

## 🛠️ Spring Boot 集成实战

```java
@Service
public class OrderService {
    
    @Autowired
    private RedissonClient redisson;
    
    // 分布式锁下单
    public Order createOrder(Long orderId) {
        RLock lock = redisson.getLock("lock:order:" + orderId);
        
        try {
            // 最多等 5 秒，加锁后 10 秒自动释放
            if (lock.tryLock(5, 10, TimeUnit.SECONDS)) {
                // 业务逻辑
                return doCreateOrder(orderId);
            } else {
                throw new BusinessException("系统繁忙，请稍后重试");
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new BusinessException("获取锁失败");
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }
    
    // 分布式限流
    public boolean tryAcquire() {
        RRateLimiter limiter = redisson.getRateLimiter("ratelimit:order");
        limiter.trySetRate(RateType.OVERALL, 100, 1, RateIntervalUnit.SECONDS);
        return limiter.tryAcquire();
    }
    
    // 布隆过滤器防穿透
    public boolean checkUserExists(Long userId) {
        RBloomFilter<Long> filter = redisson.getBloomFilter("filter:users");
        filter.tryInit(1_000_000L, 0.01);
        if (!filter.contains(userId)) {
            return false;
        }
        return true;
    }
}
```

## ⚙️ Cluster 集群配置

```java
Config config = new Config();
config.useClusterServers()
    .addNodeAddress("redis://192.168.1.10:7001")
    .addNodeAddress("redis://192.168.1.10:7002")
    .addNodeAddress("redis://192.168.1.10:7003")
    .setPassword("password")
    .setScanInterval(2000);   // 集群拓扑扫描间隔

RedissonClient redisson = Redisson.create(config);
```

## 🎯 总结

**Redisson 核心要点**：
- ✅ 分布式工具集（200+ 对象）
- ✅ 看门狗机制（自动续期）
- ✅ 分布式锁、集合、队列、Topic
- ✅ 布隆过滤器、限流器、AtomicLong
- ⚠️ 比 Jedis/Lettuce 稍重（依赖 Netty）
- ⚠️ 需要了解各分布式对象的使用场景

**下一步：** [💧 连接池](/05-jdk/connection-pool) — 深入理解连接池


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
