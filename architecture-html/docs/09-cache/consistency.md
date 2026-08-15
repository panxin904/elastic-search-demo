---
title: 缓存一致性
---
# 缓存一致性

## 1. 三大经典策略

### Cache Aside（旁路缓存，最常用）

```
读：
  cache = redis.get(key)
  if cache: return cache
  data = db.read(key)
  redis.setex(key, ttl, data)
  return data

写：
  db.write(data)
  redis.del(key)        ← 删缓存，不是更新
```

**特点**：代码简单，DB 是唯一事实源。
**问题**：写后立即读可能读到旧缓存（别人刚回填）。

### Read Through

```
应用只问缓存
  → 缓存没？缓存自己查 DB
  → 缓存满了 / 过期 → 缓存自己回 DB
  → 返回
```

**代表**：Caffeine loadingCache、Hazelcast。

### Write Through

```
应用写缓存
  → 缓存自己同步写 DB
  → 返回成功
```

**特点**：强一致，但慢。

## 2. Cache Aside 的并发问题

### 写后读：经典 race

```
T1: 写 DB
T2: 读 cache → 未命中
T2: 读 DB（读到旧值）
T2: 写 cache（覆盖了 T1 的新值）
T1: 写 cache（旧值 + 删重做覆盖了 T2 的脏值）

结果：cache 里的值是中间态
```

### 双写：先 DB 后 cache

```
T1: 写 DB
T1: 写 cache（新值）
T2: 写 DB（同样新值，没问题）
T2: 写 cache（新值）

T1: 写 cache（旧值，错了！）
T2: 写 cache（又变成新值）
```

写 cache 时序错乱 → 脏数据。

### 解决：先写 DB，再删 cache

```
T1: 写 DB
T1: 删 cache
T2: 读 cache → miss
T2: 读 DB → 新值
T2: 写 cache（新值）

最终：cache = 新值 ✅
```

但仍有问题：T1 删 cache 后崩了，T2 已读 DB，但 cache 还没写新值。**下次读 cache 还是旧值**。

### 解决：延迟双删

```
T1: 写 DB
T1: 删 cache
T1: 异步：500ms 后再删一次
```

**第一次删**：让正在用的连接读到新值（被 T2 重新回填）
**第二次删**：清除被 T2 回填的"可能旧值"

```java
@Transactional
public void updateProduct(Product p) {
  db.update(p);
  redis.del("p:" + p.getId());
  // 延迟再删
  scheduledExecutor.schedule(() -> redis.del("p:" + p.getId()), 500, MILLIS);
}
```

## 3. 订阅 Binlog

不用延迟双删，订阅 DB binlog：

```
应用写 DB
  → DB 写 binlog
  → 订阅服务（如 Debezium / Canal）读 binlog
  → 删 / 更新 cache
```

**优点**：实时 + 准确 + 应用零侵入。
**代表**：Debezium、阿里 Canal。

## 4. 一致性级别

| 策略 | 一致性 | 性能 | 复杂度 |
|------|--------|------|--------|
| Cache Aside | 最终 | 高 | 低 |
| Read Through | 强 | 中 | 中 |
| Write Through | 强 | 中 | 中 |
| Write Behind | 最终 | 极高 | 中 |
| Binlog 订阅 | 最终 | 高 | 高 |

**实战选型**：
- 通用 Web → Cache Aside + 延迟双删
- 电商商品 → Cache Aside
- 库存 / 金融 → 强一致（DB + 短 TTL + 业务幂等）
- 高吞吐 → 订阅 binlog

## 5. 实战：库存缓存

```java
public void deductStock(Long skuId, int qty) {
  // 1. DB 强一致（事务）
  int affected = jdbcTemplate.update(
    "UPDATE inventory SET stock = stock - ? WHERE sku_id = ? AND stock >= ?",
    qty, skuId, qty
  );
  if (affected == 0) throw new OutOfStockException();

  // 2. 删缓存（避免读旧值）
  redis.del("stock:" + skuId);

  // 3. 延迟再删（防其他线程脏回填）
  scheduledExecutor.schedule(() -> redis.del("stock:" + skuId), 500, MILLIS);
}
```

**业务幂等 + 乐观锁 + 缓存失效** = 库存系统。

## 6. 多级缓存一致性

| 层 | 一致性策略 |
|----|-----------|
| 本地内存（Caffeine） | TTL 短 + 主动失效 |
| Redis | 失效 + 延迟双删 |
| DB | 唯一事实源 |

**失效广播**：DB 写完 → 发 Redis 失效事件 → 各级 cache 失效。

## 7. 监控

```java
// 关键指标
metrics.counter("cache.hit", "key", "user:" + id).inc();
metrics.counter("cache.miss", "key", "user:" + id).inc();
metrics.histogram("cache.latency").observe(elapsedMs);
```

**告警**：命中率 < 80% / 平均延迟 > 10ms / 内存 > 80%。

## 8. 实战选型

| 场景 | 选 |
|------|-----|
| 普通 Web | Cache Aside + 延迟双删 |
| 电商商品 | Cache Aside + 布隆过滤器 |
| 库存 / 资金 | 强一致（DB）+ 短缓存 |
| 高吞吐 | Binlog 订阅 + 异步失效 |
| 分布式协调 | Redis 分布式锁 |

## 🔗 下一步
- [多级缓存架构](/09-cache/architecture)
- [缓存三大问题](/09-cache/breakdown)
- [幂等性设计](/03-ha-theory/idempotency)
