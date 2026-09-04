---
title: 计数器
date: 2026-08-15  # date-auto-injected
---

# 🔢 计数器

> **计数器**是 Redis 最经典的应用之一。Redis 的 **INCR** 命令是**原子操作**，性能极高，是实现计数器的最佳方案。

![Redis Hyperloglog Bitmap](/redis-hyperloglog-bitmap.svg)

## 🎯 计数器应用场景

```
✅ 文章阅读量（PV）
✅ 用户访问次数
✅ 点赞数 / 收藏数
✅ 商品库存
✅ API 调用次数
✅ 限流计数
✅ 秒杀扣减库存
✅ UV 统计（HyperLogLog）
```

## 📝 INCR 原子性

> Redis 是**单线程执行命令**，INCR 是**原子操作**，无需担心并发问题。

```bash
# INCR 自增 1
INCR counter:article:1001
# 返回：1, 2, 3, ...

# INCRBY 自增 N
INCRBY counter:article:1001 100
# 一次加 100

# DECR 自减
DECR counter:stock:product:1001
# 库存扣减

# DECRBY 自减 N
DECRBY counter:stock:product:1001 5
```

## 🛠️ 实战：文章阅读量

```java
@Service
public class ArticleService {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    // 增加阅读量
    public long incrementViews(Long articleId) {
        String key = "views:article:" + articleId;
        Long views = redisTemplate.opsForValue().increment(key);
        return views != null ? views : 0;
    }
    
    // 获取阅读量
    public long getViews(Long articleId) {
        String value = redisTemplate.opsForValue().get("views:article:" + articleId);
        return value != null ? Long.parseLong(value) : 0;
    }
    
    // 定时同步到数据库
    @Scheduled(fixedRate = 60_000)  // 每分钟
    public void syncToDatabase() {
        // 获取所有文章的访问量
        Set<String> keys = redisTemplate.keys("views:article:*");
        for (String key : keys) {
            Long articleId = Long.parseLong(key.replace("views:article:", ""));
            Long views = redisTemplate.opsForValue().getAndDelete(key);  // 获取并删除
            if (views != null && views > 0) {
                articleMapper.incrementViews(articleId, views);
            }
        }
    }
}
```

## 🛠️ 实战：秒杀库存扣减（Lua 原子）

```java
public boolean deductStock(Long productId, int quantity) {
    String key = "stock:product:" + productId;
    
    // Lua 脚本：检查库存 + 扣减（原子）
    String lua = "if redis.call('get', KEYS[1]) >= tonumber(ARGV[1]) then " +
                 "return redis.call('decrby', KEYS[1], ARGV[1]) " +
                 "else return -1 end";
    
    DefaultRedisScript<Long> script = new DefaultRedisScript<>(lua, Long.class);
    Long result = redisTemplate.execute(script, Arrays.asList(key), String.valueOf(quantity));
    
    // result >= 0 表示扣减成功，-1 表示库存不足
    return result != null && result >= 0;
}
```

## 📊 PV / UV 统计

### PV（页面浏览量）

```bash
# 直接 INCR
INCR pv:page:home

# 每日清零
EXPIRE pv:page:home 86400
```

### UV（独立访客）

> UV 需要去重，普通 SET 占用内存大。**HyperLogLog** 是 Redis 提供的概率数据结构，**12KB 内存统计 2^64 数据**，标准误差 0.81%。

```bash
# 添加访问用户
PFADD uv:home user1 user2 user3 user1
# → 1（新的基数）

PFADD uv:home user1 user4
# → 1（user4 是新的）

# 统计 UV
PFCOUNT uv:home
# → 4（user1, user2, user3, user4）
```

```java
// Java 实现
public long getUV() {
    return redisTemplate.opsForHyperLogLog().size("uv:home");
}

public void addUV(Long userId) {
    redisTemplate.opsForHyperLogLog().add("uv:home", "user:" + userId);
}
```

### PV + UV 组合

```java
// 同时记录 PV 和 UV
public void recordVisit(Long userId) {
    String date = LocalDate.now().toString();
    
    // PV（INCR）
    redisTemplate.opsForValue().increment("pv:" + date);
    redisTemplate.expire("pv:" + date, 25, TimeUnit.HOURS);
    
    // UV（HyperLogLog）
    redisTemplate.opsForHyperLogLog().add("uv:" + date, "user:" + userId);
    redisTemplate.expire("uv:" + date, 25, TimeUnit.HOURS);
}

// 每日统计
public DailyStats getStats(String date) {
    DailyStats stats = new DailyStats();
    String pv = redisTemplate.opsForValue().get("pv:" + date);
    stats.setPv(pv != null ? Long.parseLong(pv) : 0);
    
    Long uv = redisTemplate.opsForHyperLogLog().size("uv:" + date);
    stats.setUv(uv != null ? uv : 0);
    
    return stats;
}
```

## 🛠️ 实战：API 调用次数（限流）

```java
// 每分钟每个用户最多 100 次 API 调用
public boolean isAllowed(Long userId) {
    String key = "ratelimit:api:" + userId;
    
    Long count = redisTemplate.opsForValue().increment(key);
    if (count != null && count == 1) {
        redisTemplate.expire(key, 60, TimeUnit.SECONDS);  // 1 分钟
    }
    
    return count != null && count <= 100;
}
```

## 📊 INCR 性能

```
单线程 Redis 测试（不同 QPS）：

操作                  QPS        平均响应时间
INCR (单 key)        10w+      < 1 ms
INCR + EXPIRE        8w+       < 1 ms
INCR (Pipeline 100)  100w+     < 1 ms (批量)
INCR (Cluster)       100w+     < 2 ms (跨节点)
```

## 🛠️ 实战：点赞数

```java
@Service
public class LikeService {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    // 点赞 / 取消点赞
    public boolean toggleLike(Long articleId, Long userId) {
        String likeKey = "likes:article:" + articleId;
        String userKey = "like:user:" + userId;  // 用户点赞集合
        
        // 判断用户是否已点赞
        Boolean isLiked = redisTemplate.opsForSet().isMember(userKey, "article:" + articleId);
        
        if (Boolean.TRUE.equals(isLiked)) {
            // 取消点赞
            redisTemplate.opsForSet().remove(userKey, "article:" + articleId);
            redisTemplate.opsForValue().decrement(likeKey);
            return false;
        } else {
            // 点赞
            redisTemplate.opsForSet().add(userKey, "article:" + articleId);
            redisTemplate.opsForValue().increment(likeKey);
            return true;
        }
    }
    
    public long getLikes(Long articleId) {
        String value = redisTemplate.opsForValue().get("likes:article:" + articleId);
        return value != null ? Long.parseLong(value) : 0;
    }
    
    // 定时同步到 DB
    @Scheduled(fixedRate = 60_000)
    public void syncToDatabase() {
        // ... 类似文章阅读量
    }
}
```

## 🛠️ 实战：分布式递增 ID

```java
@Service
public class SequenceService {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    // 订单 ID 生成
    public long nextOrderId() {
        String date = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String key = "seq:order:" + date;
        
        Long id = redisTemplate.opsForValue().increment(key);
        if (id != null && id == 1) {
            redisTemplate.expire(key, 25, TimeUnit.HOURS);
        }
        
        return id;
    }
}
```

## ⚠️ 常见问题

### 问题 1：数据丢失

```
场景：Redis 重启，计数器归零
解决：
  1. 启用 AOF（appendfsync everysec）
  2. 定期同步到 MySQL
  3. 启动时从 MySQL 加载初始值
```

### 问题 2：BigKey

```
场景：单个 key 访问量极大（如热门商品库存）
问题：单点压力
解决：
  1. 分段计数（库存拆成多个 key）
  2. 集群分散
  3. 本地缓存 + Redis 兜底
```

### 问题 3：并发扣减库存超卖

```
场景：100 件商品，200 用户同时扣减
问题：超卖 100 件
解决：
  1. Lua 脚本（推荐，原子）
  2. 分布式锁
  3. 数据库乐观锁
```

### 问题 4：HyperLogLog 误差

```
场景：HyperLogLog 标准误差 0.81%
适用：UV 统计（误差可接受）
不适用：需要精确计数的场景（如点赞数）
```

## 🎯 总结

**计数器核心要点**：
- ✅ INCR 原子操作，性能极高
- ✅ 库存扣减：Lua 脚本保证原子
- ✅ PV/UV：INCR + HyperLogLog
- ✅ 点赞/收藏：INCR + Set 记录用户
- ✅ 定期同步到 MySQL（防数据丢失）
- ⚠️ BigKey 风险：分段或拆分
- ⚠️ Redis 丢失：AOF + 持久化兜底

**下一步：** [⚖️ 缓存一致性](/06-practice/cache-consistency) — 缓存三大问题


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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 主存
- [kafka](https://java-px.bot.cd/kafka/):Kafka 异步队列
- [java](https://java-px.bot.cd/java-web-manual/):Java 客户端（Redisson / Jedis）
