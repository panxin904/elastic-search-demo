---
title: 缓存三大问题
---

# ❄️ 缓存三大问题

> 缓存穿透、击穿、雪崩是后端面试"必背题"。本篇详细拆解三者的**成因、区别、解决方案**，并提供完整 Java 代码示例。

## 一、三大问题对照表

| 问题 | 本质 | 典型场景 | 后果 |
|------|------|----------|------|
| **穿透** | 查询不存在的数据 | 攻击者伪造 ID | 每次都打到 DB |
| **击穿** | 热点 key 突然过期 | 秒杀爆款 | 瞬间高并发压垮 DB |
| **雪崩** | 大量 key 同时过期 | 凌晨批量预热 | DB 请求量激增 |

三者经常被混淆，**核心区分点**：

```text
穿透：key 在 DB 也不存在（攻击 / 业务冷数据）
击穿：key 在 DB 存在，但缓存刚好过期（热点）
雪崩：N 个 key 同时过期（大面积失效）
```

## 二、缓存穿透（Cache Penetration）

### 2.1 问题

查询一个**永远不存在**的 key，每次请求都从 Redis miss → 打 DB → 返回 null。攻击者可以伪造大量不存在的 ID 把 DB 打挂。

```text
GET user:9999999
       ↓
   Redis miss
       ↓
   DB query → null
       ↓
   返回 null（但 DB 已经被打了）
```

### 2.2 解决方案

#### 方案 1：空值缓存

DB 返回 null 时，往 Redis 写一个短 TTL 的空值：

```java
public User getUser(Long id) {
    String key = "user:" + id;
    // 1. 查 Redis
    String json = redis.opsForValue().get(key);
    if (json != null) {
        // 哨兵值
        if (json.equals("__NULL__")) return null;
        return JsonUtil.parse(json, User.class);
    }

    // 2. 查 DB
    User user = userMapper.selectById(id);
    if (user == null) {
        // 写空值，TTL 短一些防止长期占内存
        redis.opsForValue().set(key, "__NULL__", 5, TimeUnit.MINUTES);
        return null;
    }

    // 3. 写回缓存
    redis.opsForValue().set(key, JsonUtil.toJson(user), 30, TimeUnit.MINUTES);
    return user;
}
```

**优点**：实现简单，5 行代码搞定。
**缺点**：恶意攻击会写入大量空值占用内存。

#### 方案 2：布隆过滤器（推荐）

所有可能存在的 ID 提前写入布隆过滤器，请求先经过布隆过滤器判断"可能存在"才放行。

```java
@Component
public class BloomFilterService {

    private final BloomFilter<Long> filter = BloomFilter.create(
        Funnels.longFunnel(),
        10_000_000L,    // 预计元素数 1000 万
        0.001           // 误判率 0.1%
    );

    @PostConstruct
    public void init() {
        // 启动时全量加载 ID 到布隆过滤器
        List<Long> allIds = userMapper.selectAllIds();
        allIds.forEach(filter::put);
    }

    public boolean mightExist(Long id) {
        return filter.mightContain(id);
    }
}

@Service
public class UserService {

    @Autowired
    private BloomFilterService bloomFilter;

    public User getUser(Long id) {
        // 1. 布隆过滤器拦截
        if (!bloomFilter.mightExist(id)) {
            return null;  // 一定不存在，直接返回
        }

        // 2. 正常查 Redis + DB
        String key = "user:" + id;
        String json = redis.opsForValue().get(key);
        if (json != null) return JsonUtil.parse(json, User.class);

        User user = userMapper.selectById(id);
        if (user != null) {
            redis.opsForValue().set(key, JsonUtil.toJson(user), 30, TimeUnit.MINUTES);
        }
        return user;
    }
}
```

**原理**

布隆过滤器由一个 bit 数组 + N 个哈希函数组成：

```text
插入 key "alice":
   h1("alice") % m = 2  → bit[2] = 1
   h2("alice") % m = 5  → bit[5] = 1
   h3("alice") % m = 8  → bit[8] = 1

查询 key "bob":
   任一 bit[x] = 0 → 一定不存在
   所有 bit[x] = 1 → 可能存在（有误判率）
```

**优点**：内存极省（1000 万元素 ~1.7 MB），查询 O(1)。
**缺点**：有误判率（可调），不支持删除（除非用 Counting Bloom Filter）。

## 三、缓存击穿（Cache Breakdown）

### 3.1 问题

某个**超级热点 key** 突然过期，恰好此时大量并发请求打过来，全部 miss → 全部打到 DB。

```text
key = "seckill:item:888"
       ↓
   过期瞬间
       ↓
   1 万个并发请求同时打到 DB
       ↓
   DB 崩溃
```

### 3.2 解决方案

#### 方案 1：互斥锁（Mutex Lock）

只让第一个请求去 DB 加载，其他请求等待重试：

```java
public User getUserWithMutex(Long id) {
    String key = "user:" + id;
    String lockKey = "lock:" + key;
    String json = redis.opsForValue().get(key);
    if (json != null) return JsonUtil.parse(json, User.class);

    // 抢锁，只有一个线程去 DB 加载
    if (tryLock(lockKey)) {
        try {
            // 双重检查：拿到锁后再次查缓存
            json = redis.opsForValue().get(key);
            if (json != null) return JsonUtil.parse(json, User.class);

            User user = userMapper.selectById(id);
            if (user != null) {
                redis.opsForValue().set(key, JsonUtil.toJson(user), 30, TimeUnit.MINUTES);
            }
            return user;
        } finally {
            unlock(lockKey);
        }
    }

    // 没抢到锁 → 睡一会儿重试
    try { Thread.sleep(100); } catch (InterruptedException e) {}
    return getUserWithMutex(id);  // 递归重试
}

private boolean tryLock(String key) {
    return Boolean.TRUE.equals(
        redis.opsForValue().setIfAbsent(key, "1", 10, TimeUnit.SECONDS));
}

private void unlock(String key) {
    String lua = "if redis.call('get', KEYS[1]) == '1' then " +
                 "return redis.call('del', KEYS[1]) else return 0 end";
    redis.execute(new DefaultRedisScript<>(lua, Long.class),
        Collections.singletonList(key));
}
```

**优点**：强一致。
**缺点**：其他线程被锁阻塞，可用性略降。

#### 方案 2：逻辑过期（推荐）

key 永不过期，存一个 `expireAt` 字段，后台异步刷新：

```java
@Data
public class CacheData<T> {
    private T data;
    private long expireAt;   // 逻辑过期时间
}

public User getUserWithLogicalExpire(Long id) {
    String key = "user:" + id;
    String json = redis.opsForValue().get(key);
    if (json == null) {
        // 冷启动：直接查 DB 并写入
        return loadAndCache(id);
    }

    CacheData<User> cache = JsonUtil.parse(json, new TypeReference<>() {});
    if (System.currentTimeMillis() < cache.getExpireAt()) {
        return cache.getData();   // 未过期
    }

    // 已过期 → 异步刷新（不等）
    asyncRefresh(id);
    return cache.getData();       // 返回旧数据
}

private void asyncRefresh(Long id) {
    String lockKey = "lock:refresh:" + id;
    // 用线程池而非锁阻塞
    executor.submit(() -> {
        if (!tryLock(lockKey)) return;  // 只让一个线程刷新
        try {
            User user = userMapper.selectById(id);
            CacheData<User> newData = new CacheData<>();
            newData.setData(user);
            newData.setExpireAt(System.currentTimeMillis() + 30 * 60 * 1000);
            redis.opsForValue().set("user:" + id,
                JsonUtil.toJson(newData), 24, TimeUnit.HOURS);
        } finally {
            unlock(lockKey);
        }
    });
}
```

**优点**：用户始终能拿到数据（即使过期），可用性高。
**缺点**：可能返回旧数据，适合"宁可读旧不可卡顿"的场景（如商品详情）。

#### 方案 3：热点 key 永不过期 + 后台异步刷新

适用场景：key 已知是热点（如秒杀商品 ID）。

```java
@PostConstruct
public void initHotKeys() {
    // 启动时预热，永不过期
    List<User> hotUsers = userMapper.selectHotUsers();
    hotUsers.forEach(u ->
        redis.opsForValue().set("user:" + u.getId(),
            JsonUtil.toJson(u)));
}

@Scheduled(fixedRate = 10_000)  // 每 10 秒刷新
public void refreshHotKeys() {
    // 后台异步更新缓存
}
```

## 四、缓存雪崩（Cache Avalanche）

### 4.1 问题

**大量 key 在同一时刻**过期（一般因为批量预热时设置相同 TTL），导致瞬时所有请求打到 DB。

```text
00:00:00 同时 SET 100 万 key，TTL = 60 分钟
01:00:00 同时过期
       ↓
   100 万请求瞬间打到 DB
       ↓
   DB 崩溃
```

### 4.2 解决方案

#### 方案 1：随机过期时间

```java
public void setWithRandomTTL(String key, Object value, int baseSeconds) {
    // 基础时间 + 随机抖动（±10 分钟）
    int ttl = baseSeconds + new Random().nextInt(1200) - 600;
    redis.opsForValue().set(key, JsonUtil.toJson(value), ttl, TimeUnit.SECONDS);
}

// 批量预热
public void warmup(List<Long> ids) {
    for (Long id : ids) {
        User u = userMapper.selectById(id);
        setWithRandomTTL("user:" + id, u, 3600);  // 3600 ± 600 秒
    }
}
```

**TTL 抖动效果**：原本同时过期 → 错峰在 ±10 分钟内陆续过期。

#### 方案 2：多级缓存架构

```text
L1: Caffeine（本地，30s TTL）        ← 抗 80% 请求
L2: Redis Cluster（5min TTL）         ← 抗 15% 请求
L3: MySQL                            ← 兜底 5% 请求
```

L1 命中不依赖 Redis，Redis 全挂也能撑 30 秒。多级缓存中各级 TTL 错峰设计。

#### 方案 3：熔断降级 + 限流

```java
@Component
public class UserServiceWithCircuitBreaker {

    @Autowired
    private UserMapper userMapper;

    @CircuitBreaker(name = "userService", fallbackMethod = "fallback")
    @RateLimiter(name = "userService")
    public User getUser(Long id) {
        return userMapper.selectById(id);
    }

    // 熔断降级：返回兜底数据
    public User fallback(Long id, Throwable t) {
        log.warn("用户服务降级, id={}, cause={}", id, t.getMessage());
        return new User(id, "默认用户", "default@xx.com");
    }
}
```

**核心依赖** Resilience4j / Sentinel：

- 熔断：连续 N 次失败打开熔断器，后续请求直接走 fallback。
- 限流：超过阈值拒绝请求，保护 DB。

#### 方案 4：缓存预热 + 后台异步刷新

```java
@Component
public class CacheWarmer {

    @Autowired
    private StringRedisTemplate redis;

    @Autowired
    private UserMapper userMapper;

    @PostConstruct
    public void warmupOnStart() {
        // 应用启动时全量预热
        List<User> allUsers = userMapper.selectAll();
        allUsers.parallelStream().forEach(u ->
            redis.opsForValue().set("user:" + u.getId(),
                JsonUtil.toJson(u), 3600, TimeUnit.SECONDS));
    }

    @Scheduled(cron = "0 0 3 * * ?")  // 每天凌晨 3 点刷新
    public void refreshDaily() {
        warmupOnStart();
    }
}
```

## 五、综合对比

| 维度 | 穿透 | 击穿 | 雪崩 |
|------|------|------|------|
| **请求的 key** | 不存在 | 存在但过期 | 大量同时过期 |
| **解决方案** | 布隆过滤器 / 空值缓存 | 互斥锁 / 逻辑过期 | 随机 TTL / 多级缓存 / 熔断 |
| **代码量** | 5~50 行 | 20~50 行 | 10~30 行 |
| **额外组件** | Guava BloomFilter | Redisson Lock | Resilience4j / Sentinel |

## 六、生产推荐组合

```text
所有请求
   ↓
布隆过滤器（拦截不存在 key）        ← 解决穿透
   ↓
Redis Cluster（命中率 95%）          ← 主缓存
   ↓ miss
互斥锁 + 双重检查                    ← 解决击穿
   ↓
DB 查询
```

预热阶段：

```text
启动时预热 + 异步刷新（解决雪崩）
所有 key 随机 TTL（±10 分钟抖动）
```

## 七、面试追问清单

| 追问 | 答案 |
|------|------|
| 布隆过滤器误判怎么办？ | 误判会多查一次 DB，不会导致数据不一致，可接受 |
| 互斥锁失败怎么办？ | 客户端降级返回默认值，避免请求堆积 |
| 逻辑过期能保证强一致吗？ | 不能，只能保证最终一致 |
| 多级缓存如何同步？ | L1 用短 TTL 自动失效，L2 主动 Pub/Sub 广播失效消息 |
| 缓存预热怎么实现？ | 启动时 `@PostConstruct` 全量加载，或用 Job 定时刷新 |

## 八、下一步

缓存三大问题的核心是**减少 DB 压力**。下一篇进入分布式分片的经典算法：**一致性 Hash**。

**下一步：** [🎯 一致性 Hash](/08-interview/consistent-hash)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
