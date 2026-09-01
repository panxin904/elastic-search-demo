---
title: 缓存策略
date: 2026-08-15  # date-auto-injected
---

# 缓存策略

合理使用缓存能大幅提升系统性能，但缓存引入的复杂性也带来了新挑战。

## 缓存读写模式

### Cache Aside（最常用）

```
读：先查缓存 → 命中则返回 → 未命中则查DB → 写入缓存 → 返回
写：更新DB → 删除缓存（不是更新缓存）
```

```java
public User getUser(Long id) {
    String key = "user:" + id;
    User user = redisTemplate.opsForValue().get(key);
    if (user != null) return user;

    user = userMapper.selectById(id);
    if (user != null) {
        redisTemplate.opsForValue().set(key, user, 30, TimeUnit.MINUTES);
    }
    return user;
}

public void updateUser(User user) {
    userMapper.updateById(user);
    redisTemplate.delete("user:" + user.getId());  // 删缓存，不更新
}
```

## 缓存三大问题

| 问题 | 原因 | 解决方案 |
|---|---|---|
| 缓存穿透 | 查不存在的数据，绕过缓存打DB | 布隆过滤器 / 缓存空值 |
| 缓存击穿 | 热点key过期，大量请求打DB | 互斥锁 / 永不过期 + 异步更新 |
| 缓存雪崩 | 大量key同时过期 | 过期时间加随机值 / 多级缓存 |

## Spring Cache 注解

```java
@Cacheable(value = "user", key = "#id")       // 查缓存
@CachePut(value = "user", key = "#result.id")  // 更新缓存
@CacheEvict(value = "user", key = "#id")       // 删除缓存
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="cache-strategy" :height="400" />
