---
title: 缓存一致性
---

# ⚖️ 缓存一致性

> 缓存与数据库是**两套独立**的数据存储。如何保证两者数据**一致**，是缓存设计的核心难题。

## 🎯 缓存三大经典问题

```
1. 缓存穿透（Cache Penetration）
   查不存在的 key，请求打到数据库

2. 缓存击穿（Cache Breakdown）
   热点 key 过期，瞬间大量请求打到数据库

3. 缓存雪崩（Cache Avalanche）
   大量 key 同时过期，请求全部打到数据库
```

## 📊 三大问题对比

| 维度 | 缓存穿透 | 缓存击穿 | 缓存雪崩 |
|------|---------|---------|---------|
| **原因** | 不存在的 key | 热点 key 过期 | 大量 key 同时过期 |
| **数据库压力** | 每次都打 | 瞬间集中 | 持续性集中 |
| **危害程度** | 中 | 高 | 极高 |
| **典型场景** | 黑客攻击不存在的 ID | 微博热搜 | Redis 重启 |

## 💉 问题 1：缓存穿透

### 场景

```
黑客：查询 /api/user/-1
  → Redis 不存在
  → 数据库也不存在（返回 null）
  → 1000 万次查询都打到数据库

或：
  查询数据库中不存在的 key，每次都走 DB
```

### 解决方案

#### 方案 1：空值缓存

```java
public User getUser(Long id) {
    String key = "user:" + id;
    String cached = redisTemplate.opsForValue().get(key);
    
    if (cached != null) {
        return cached.isEmpty() ? null : JSON.parse(cached);
    }
    
    User user = userMapper.findById(id);
    
    // 即使数据库没有，也缓存空值（短 TTL）
    if (user == null) {
        redisTemplate.opsForValue().set(key, "", 5, TimeUnit.MINUTES);
    } else {
        redisTemplate.opsForValue().set(key, JSON.toJSONString(user), 30, TimeUnit.MINUTES);
    }
    
    return user;
}
```

#### 方案 2：布隆过滤器（推荐）

```java
@Component
public class BloomFilterService {
    
    @Autowired
    private RedissonClient redisson;
    
    private static final String FILTER = "bloom:users";
    
    @PostConstruct
    public void init() {
        RBloomFilter<Long> filter = redisson.getBloomFilter(FILTER);
        filter.tryInit(100_000_000L, 0.01);  // 1 亿容量，1% 误判率
        
        // 启动时加载所有用户 ID
        List<Long> allUserIds = userMapper.findAllIds();
        for (Long id : allUserIds) {
            filter.add(id);
        }
    }
    
    public boolean mightExist(Long id) {
        return redisson.getBloomFilter(FILTER).contains(id);
    }
}

@Service
public class UserService {
    
    @Autowired
    private BloomFilterService bloomFilter;
    
    public User getUser(Long id) {
        // 先用布隆过滤器判断
        if (!bloomFilter.mightExist(id)) {
            return null;  // 一定不存在
        }
        
        // 走正常缓存逻辑
        return getUserFromCache(id);
    }
}
```

## 💥 问题 2：缓存击穿

### 场景

```
微博热搜：明星离婚
  → 微博 key "weibo:hot:123" 缓存中
  → 突然过期
  → 100 万用户同时访问
  → 全部打到数据库
  → 数据库崩溃！
```

### 解决方案

#### 方案 1：互斥锁（Mutex Lock）

```java
public User getUser(Long id) {
    String key = "user:" + id;
    String value = redisTemplate.opsForValue().get(key);
    
    if (value != null) {
        return JSON.parseObject(value, User.class);
    }
    
    // 加分布式锁（只允许一个线程回源）
    RLock lock = redisson.getLock("lock:user:" + id);
    if (lock.tryLock()) {
        try {
            // 双重检查（Double Check）
            value = redisTemplate.opsForValue().get(key);
            if (value != null) {
                return JSON.parseObject(value, User.class);
            }
            
            // 从数据库加载
            User user = userMapper.findById(id);
            redisTemplate.opsForValue().set(key, JSON.toJSONString(user), 30, TimeUnit.MINUTES);
            return user;
        } finally {
            lock.unlock();
        }
    } else {
        // 没拿到锁，等待并重试
        Thread.sleep(50);
        return getUser(id);
    }
}
```

#### 方案 2：逻辑过期（不设物理 TTL）

```java
public User getUser(Long id) {
    String key = "user:" + id;
    String json = redisTemplate.opsForValue().get(key);
    
    if (json == null) {
        return loadFromDb(id);  // 第一次加载
    }
    
    // value 中包含过期时间字段
    JSONObject wrapper = JSON.parseObject(json);
    long expireTime = wrapper.getLongValue("expireTime");
    User user = wrapper.getObject("data", User.class);
    
    if (System.currentTimeMillis() < expireTime) {
        return user;  // 未过期
    }
    
    // 异步刷新（不阻塞当前请求）
    asyncRefresh(id);
    return user;  // 返回旧数据
}

@Async
public void asyncRefresh(Long id) {
    User user = userMapper.findById(id);
    JSONObject wrapper = new JSONObject();
    wrapper.put("data", user);
    wrapper.put("expireTime", System.currentTimeMillis() + 30 * 60 * 1000);
    redisTemplate.opsForValue().set("user:" + id, wrapper.toJSONString());
}
```

## ❄️ 问题 3：缓存雪崩

### 场景

```
Redis 重启或大量 key 同时过期
  → 100 万 QPS 请求全部打到数据库
  → 数据库崩溃

或：
  同一批商品设置了相同的过期时间（如双 11 零点）
  → 同时过期，请求全部打到数据库
```

### 解决方案

#### 方案 1：随机过期时间

```java
public void setCache(String key, Object value, int baseExpireMinutes) {
    // 在基础过期时间上加 0~60 秒随机偏移
    int randomSeconds = ThreadLocalRandom.current().nextInt(60);
    Duration expire = Duration.ofMinutes(baseExpireMinutes).plusSeconds(randomSeconds);
    
    redisTemplate.opsForValue().set(key, JSON.toJSONString(value), expire);
}
```

#### 方案 2：多级缓存

```
L1: 本地缓存（Caffeine，秒级）
L2: Redis 缓存（分钟级）
L3: 数据库（持久化）

Redis 挂掉时，本地缓存仍可服务
```

#### 方案 3：熔断降级

```java
// Sentinel / Resilience4j 熔断
@CircuitBreaker(fallbackMethod = "fallbackGetUser", maxFailures = 10)
public User getUser(Long id) {
    return userMapper.findById(id);  // Redis 挂了直接查 DB
}

public User fallbackGetUser(Long id, Throwable t) {
    // 返回默认值或兜底数据
    return new User("Default", 0);
}
```

## 📋 双写一致性

> **写入数据时，如何保证缓存和数据库一致**？

### 方案 1：先更新数据库，再删除缓存（推荐）

```java
@Transactional
public void updateUser(User user) {
    // 1. 先更新数据库
    userMapper.update(user);
    
    // 2. 再删除缓存
    redisTemplate.delete("user:" + user.getId());
}
```

**为什么不先更新缓存？**
```
场景：A 写数据库 100，B 写数据库 200，并发执行
  步骤 1：A 更新缓存为 100
  步骤 2：B 更新缓存为 200
  步骤 3：B 更新数据库为 200
  步骤 4：A 更新数据库为 100
  
  最终：缓存=200，数据库=100（不一致！）
```

### 方案 2：延迟双删

```java
public void updateUser(User user) {
    // 1. 删除缓存
    redisTemplate.delete("user:" + user.getId());
    
    // 2. 更新数据库
    userMapper.update(user);
    
    // 3. 延迟再删一次（处理并发读写）
    new Thread(() -> {
        try {
            Thread.sleep(500);
            redisTemplate.delete("user:" + user.getId());
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }).start();
}
```

### 方案 3：Binlog 订阅（最终一致）

```
MySQL Binlog → Canal → MQ → Redis 更新

优点：
  - 业务无侵入
  - 最终一致性强
  - 异步处理，性能好

缺点：
  - 引入 Canal + MQ 复杂度
  - 实时性略差（毫秒级）
```

```java
// Canal 监听 Binlog
@Component
public class UserCacheSync {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    @CanalListener("user_table")
    public void onChange(CanalEntry entry) {
        if (entry.getEventType() == EventType.UPDATE) {
            Long userId = entry.getAfter().getId();
            // 删除缓存（下次查询自动回源）
            redisTemplate.delete("user:" + userId);
        }
    }
}
```

## 📊 缓存方案对比

| 方案 | 一致性 | 性能 | 复杂度 |
|------|--------|------|--------|
| **TTL 过期** | 弱 | 高 | 极低 |
| **Cache Aside** | 弱 | 高 | 低 |
| **延迟双删** | 中 | 中 | 中 |
| **Read/Write Through** | 强 | 中 | 中 |
| **Write Behind** | 强 | 高 | 高 |
| **Binlog 订阅（Canal）** | 最终一致 | 高 | 高 |

## 🛠️ 综合实战

```java
@Service
public class UserService {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    @Autowired
    private RBloomFilter<Long> bloomFilter;
    
    @Autowired
    private RedissonClient redisson;
    
    // 综合应用：缓存穿透 + 击穿 + 一致性
    public User getUser(Long id) {
        // 1. 布隆过滤器（防穿透）
        if (!bloomFilter.contains(id)) {
            return null;
        }
        
        // 2. 查缓存
        String key = "user:" + id;
        String json = redisTemplate.opsForValue().get(key);
        if (json != null) {
            return JSON.parseObject(json, User.class);
        }
        
        // 3. 互斥锁（防击穿）
        RLock lock = redisson.getLock("lock:user:" + id);
        if (lock.tryLock(1, 5, TimeUnit.SECONDS)) {
            try {
                // 双重检查
                json = redisTemplate.opsForValue().get(key);
                if (json != null) {
                    return JSON.parseObject(json, User.class);
                }
                
                // 4. 回源 + 随机过期（防雪崩）
                User user = userMapper.findById(id);
                int random = ThreadLocalRandom.current().nextInt(60);
                redisTemplate.opsForValue().set(key, JSON.toJSONString(user),
                    Duration.ofMinutes(30).plusSeconds(random));
                return user;
            } finally {
                lock.unlock();
            }
        }
        
        // 5. 重试
        try {
            Thread.sleep(50);
            return getUser(id);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return null;
        }
    }
    
    // 更新：Cache Aside + 延迟双删
    public void updateUser(User user) {
        // 1. 删除缓存
        redisTemplate.delete("user:" + user.getId());
        
        // 2. 更新数据库
        userMapper.update(user);
        
        // 3. 延迟再删（处理并发读）
        scheduledExecutor.schedule(() -> 
            redisTemplate.delete("user:" + user.getId()),
            500, TimeUnit.MILLISECONDS
        );
    }
}
```

## ⚠️ CAP 理论

```
缓存系统本质：
  - 一致性（Consistency）
  - 可用性（Availability）
  - 分区容错（Partition Tolerance）

CAP 只能选两个：
  - CA：单点（不现实）
  - CP：Redis Sentinel（强一致，可能不可用）
  - AP：Redis Cluster（最终一致，高可用）

实际选择：AP + 最终一致（多数大厂的选择）
```

## 🎯 总结

**缓存一致性核心要点**：
- ✅ 三大问题：穿透 / 击穿 / 雪崩
- ✅ 穿透：空值缓存 + 布隆过滤器
- ✅ 击穿：互斥锁 + 逻辑过期
- ✅ 雪崩：随机过期 + 多级缓存
- ✅ 双写一致性：先更新 DB 再删缓存
- ⚠️ 强一致：放弃缓存（直接读 DB）
- ⚠️ 最终一致：Canal + MQ（推荐生产）

**下一步：** [🗑️ 内存淘汰策略](/07-ops/eviction) — Redis 运维调优

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
