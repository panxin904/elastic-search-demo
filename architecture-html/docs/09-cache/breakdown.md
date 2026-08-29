---
title: 缓存三大问题
date: 2026-08-15  # date-auto-injected
---
# 缓存三大问题

穿透 / 击穿 / 雪崩 —— 缓存系统最大的三个故障场景。

## 1. 缓存穿透（Cache Penetration）

**场景**：查询一个**根本不存在**的数据 → 缓存没有 → 每次都打 DB → DB 被打死。

```
攻击：id=-1, id=99999, ...
正常用户：拿合法 id
→ 都不在缓存
→ 都查 DB
→ DB 挂了
```

### 解决方案

**1. 缓存空对象**

```java
public Product getProduct(Long id) {
  Product cached = redis.get("p:" + id);
  if (cached != null) {
    if (cached.isNull()) return null;  // 缓存了空对象
    return cached;
  }

  Product p = db.query(id);
  if (p == null) {
    redis.setex("p:" + id, 60, NULL_PRODUCT);  // 缓存空对象
    return null;
  }
  redis.setex("p:" + id, 300, p);
  return p;
}
```

**问题**：攻击大量不同 key → 内存被空对象占满。

**2. 布隆过滤器（Bloom Filter）**

```java
// 启动时加载所有存在的 id 到布隆过滤器
// 查询前先过布隆过滤器
if (!bloomFilter.mightContain(id)) return null;  // 一定不存在
// 否则查 DB + 缓存
```

**优点**：极小内存判存在性。
**缺点**：有误判率（1%）。

**3. 限流 + WAF**

```nginx
location /api/ {
  limit_req zone=api burst=20 nodelay;
  if ($http_user_agent ~* "sqlmap|nikto") { return 403; }
}
```

## 2. 缓存击穿（Cache Breakdown）

**场景**：某个 **热点 key 突然过期** → 大量请求同时打 DB → DB 挂。

```
热搜文章 1 万 QPS 查 article:123
突然 article:123 过期
→ 1 万请求同时回源 DB
→ DB 挂了
```

### 解决方案

**1. 永不过期 + 异步刷新**

```java
// 不过期，异步线程定时从 DB 加载
@Scheduled(fixedRate = 30000)  // 30s 刷新
public void refreshHotKey() {
  Product p = db.query(id);
  redis.set("p:" + id, p);
  // 业务读永远命中
}
```

**2. 互斥锁（singleflight）**

```java
public Product getProduct(Long id) {
  Product cached = redis.get("p:" + id);
  if (cached != null) return cached;

  // 只有一个请求去查 DB，其他等
  Product p = singleflight.get("p:" + id, () -> {
    Product fresh = db.query(id);
    redis.setex("p:" + id, 300, fresh);
    return fresh;
  });
  return p;
}
```

**3. 热点 key 永久不过期**

```java
// 检测到热点 key → 续期 TTL
if (hotKeyDetector.isHot(id)) {
  redis.expire("p:" + id, 600);  // 续期到 10 分钟
}
```

**4. 提前过期**

```java
// TTL 提前 10% 异步刷新
private static final int TTL_BUFFER_PERCENT = 10;
public Product getProduct(Long id) {
  int ttl = redis.ttl("p:" + id);
  if (ttl < 300 * TTL_BUFFER_PERCENT / 100) {
    // 异步刷新
    asyncRefresh(id);
  }
  return redis.get("p:" + id);
}
```

## 3. 缓存雪崩（Cache Avalanche）

**场景**：**大量 key 同时过期**（如同一秒过期 / Redis 挂掉） → 大量请求同时打 DB → DB 挂。

```
00:00:00  Redis 挂了
00:00:01  所有请求打 DB
00:00:30  DB 挂了
```

或：

```
热点新闻 8:00 全部过期
8:00:00 全部回源 DB
DB 挂了
```

### 解决方案

**1. 过期时间随机化**

```java
int baseTtl = 300;
int randomTtl = baseTtl + ThreadLocalRandom.current().nextInt(60) - 30;
// 实际 ttl 在 270-330s 之间，避免同时过期
redis.setex("p:" + id, randomTtl, p);
```

**2. 缓存预热**

```java
@PostConstruct
public void warmUp() {
  List<Product> hot = db.findTop100HotProducts();
  hot.forEach(p -> redis.setex("p:" + p.getId(), 600, p));
}
```

**3. 多级缓存**

```
本地（Caffeine）→ Redis → DB
  本地命中 → 不走 Redis
  Redis 命中 → 不走 DB
  本地 + Redis 都没有 → 走 DB（部分请求）
```

**4. Redis 高可用**

- 主从 + Sentinel（自动 failover）
- Cluster 集群（分片 + 副本）
- 持久化（AOF + RDB）

**5. 限流 + 降级**

```java
public Product getProduct(Long id) {
  if (!rateLimiter.allow()) {
    return cached != null ? cached : DEFAULT_PRODUCT;
  }
  // ...
}
```

## 4. 三大问题对比

| 问题 | 触发条件 | 现象 | 核心方案 |
|------|---------|------|---------|
| **穿透** | 查不存在的数据 | 每次都打 DB | 空对象缓存 / 布隆过滤器 |
| **击穿** | 热点 key 过期 | 单 key 高并发打 DB | 互斥锁 / 永不过期 / singleflight |
| **雪崩** | 大量 key 同时过期 | 多 key 高并发打 DB | TTL 随机 / 预热 / 多级缓存 |

## 5. 实战 checklist

```
- [ ] 布隆过滤器防止穿透
- [ ] 互斥锁 / singleflight 防止击穿
- [ ] TTL 随机化防止雪崩
- [ ] 缓存预热（启动时）
- [ ] Redis 高可用（主从 + Sentinel / Cluster）
- [ ] 多级缓存（本地 + Redis + DB）
- [ ] 限流 + 降级（兜底）
- [ ] 监控：命中率 / 延迟 / 内存
```

## 6. 实战：商品查询

```java
@Service
public class ProductService {
  @Autowired StringRedisTemplate redis;
  @Autowired ProductRepo db;
  @Autowired BloomFilter<Long> bloomFilter;
  @Autowired RateLimiter limiter;

  public Product getProduct(Long id) {
    // 1. 限流
    if (!limiter.allow()) return DEFAULT_PRODUCT;

    // 2. 布隆过滤器
    if (!bloomFilter.mightContain(id)) return null;

    // 3. 缓存
    Product cached = redis.get("p:" + id);
    if (cached != null) return cached.isNull() ? null : cached;

    // 4. singleflight 击穿防护
    return singleflight.get("p:" + id, () -> {
      Product p = db.query(id);
      if (p == null) {
        redis.setex("p:" + id, 60, NULL_PRODUCT);
        return null;
      }
      // TTL 随机化防雪崩
      int ttl = 300 + ThreadLocalRandom.current().nextInt(60);
      redis.setex("p:" + id, ttl, p);
      return p;
    });
  }
}
```

## 🔗 下一步
- [多级缓存架构](/09-cache/architecture)
- [一致性策略](/09-cache/consistency)
