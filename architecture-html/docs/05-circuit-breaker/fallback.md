---
title: Fallback 设计
---
# Fallback 设计

## 1. Fallback 策略

服务降级：限流/熔断后**还能返回有意义结果**，而不是直接报错。

| 策略 | 描述 | 适用 |
|------|------|------|
| **默认值** | 返回兜底值（null / empty list / {}） | 简单读 |
| **缓存** | 返回 stale cache | 读多写少 |
| **降级逻辑** | 简化版功能（如返回热门而非个性化） | 推荐系统 |
| **快速失败** | 直接抛异常 | 强一致场景 |
| **排队** | 入 MQ 异步处理 | 写操作 |
| **重试** | 短时间内重试 N 次 | 瞬态故障 |

## 2. 4 种降级层次

```
Tier 1: 强依赖（支付核心） → 熔断直接报错
Tier 2: 重要功能（推荐）  → 缓存 + 默认
Tier 3: 锦上添花（评论） → 隐藏 / 默认占位
Tier 4: 可有可无（统计）  → 直接跳过
```

## 3. 实战：电商推荐 fallback

```java
public List<Product> recommend(User user) {
  try {
    return mlModel.recommend(user);       // 个性化推荐
  } catch (DegradeException e) {
    return popularProducts();            // 热门兜底
  } catch (Exception e) {
    return cache.get("top10");           // 缓存兜底
  }
}
```

## 4. Fallback 链设计

```
请求 → 限流（100 QPS）→ 缓存（stale-while-revalidate）→ 主服务 → 兜底（默认值）
  失败 ←                                失败
```

每层都做降级：**部分可用 > 整体不可用**。

## 5. 缓存降级（stale-while-revalidate）

```java
public Product getProduct(Long id) {
  Product cached = cache.get("p:" + id);
  if (cached != null) return cached;          // 返回 stale cache
  try {
    Product fresh = productClient.get(id);
    cache.set("p:" + id, fresh, 5min);
    return fresh;
  } catch (Exception e) {
    if (cached != null) return cached;       // 异常时回退
    throw e;
  }
}
```

**Stale-While-Revalidate**：先返回旧值，异步刷新，不阻塞用户。

## 6. Fallback 设计原则

```
1. 快速失败 > 慢死（fail fast）
2. 缓存降级 > 直接报错（保护下游）
3. 默认值 > 空指针（友好）
4. 降级触发告警（不能静默）
5. 业务分级（核心支付不降级，评论可降级）
```

## 7. 实战：多级 fallback

```java
public User getUser(Long id) {
  // Tier 1: 缓存（50ms）
  User cached = localCache.get(id);
  if (cached != null) return cached;

  // Tier 2: 主服务
  try {
    return userService.getUser(id);
  } catch (CircuitOpenException e) {
    // Tier 3: 只读副本
    return readOnlyUserService.getUser(id);
  } catch (Exception e) {
    // Tier 4: 缓存（即使 stale）
    return redisCache.get(id) or User.guest();
  }
}
```

## 8. 实战：监控 fallback

```java
// 触发 fallback 时上报
@Around("fallbackMethod")
public void trackFallback() {
  metrics.counter("fallback.triggered",
    "service", "user", "reason", ex.getClass().getSimpleName()).inc();
}
```

## 9. Fallback 反模式

- **静默降级**：fallback 触发没告警 → 雪崩
- **fallback 内部再降级**：无限套娃 → 难调试
- **fallback 返回错误**：形同虚设
- **没测试 fallback**：生产触发 fallback 不知道

## 🔗 下一步
- [熔断器三态](/05-circuit-breaker/states)
- [Sentinel / Hystrix](/05-circuit-breaker/impl)
