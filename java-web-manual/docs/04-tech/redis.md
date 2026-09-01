---
title: Redis
date: 2026-08-15  # date-auto-injected
---

# Redis

Redis 是高性能的 KV 内存数据库，Java Web 中最常用的缓存和分布式协调中间件。

## 常用数据结构

| 结构 | 命令 | 应用场景 |
|---|---|---|
| String | SET/GET | 缓存、计数器、分布式锁 |
| Hash | HSET/HGET | 对象缓存（用户信息） |
| List | LPUSH/RPOP | 消息队列、最新列表 |
| Set | SADD/SINTER | 标签、共同好友 |
| Sorted Set | ZADD/ZRANGE | 排行榜、延迟队列 |

## Spring Boot 集成

```yaml
spring:
  redis:
    host: localhost
    port: 6379
    password:
    lettuce:
      pool:
        max-active: 8
        max-idle: 8
        min-idle: 0
```

```java
@Autowired
private StringRedisTemplate redisTemplate;

// 缓存
redisTemplate.opsForValue().set("user:1", jsonStr, 30, TimeUnit.MINUTES);

// 分布式锁
Boolean locked = redisTemplate.opsForValue()
    .setIfAbsent("lock:order:1", "1", 10, TimeUnit.SECONDS);

// 发布订阅
redisTemplate.convertAndSend("order:created", orderJson);

// 延迟队列（ZSet）
redisTemplate.opsForZSet().add("delay:task", taskId,
    System.currentTimeMillis() + 60000);
```

## 缓存穿透/击穿/雪崩

| 问题 | 方案 |
|---|---|
| 穿透（查不存在的数据） | 布隆过滤器、缓存空值(短TTL) |
| 击穿（热点Key过期） | 互斥锁 + 异步刷新、逻辑过期 |
| 雪崩（大量Key同时过期） | TTL加随机值、多级缓存、限流 |

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="redis" :height="400" />
