---
title: 多级缓存架构
date: 2026-08-15  # date-auto-injected
---
# 多级缓存架构

## 1. 为什么需要缓存

```
数据库查询：
  - 单次查询 10-50ms（随机 IO）
  - 热点数据 90% 请求只查 10% 数据

加缓存：
  - 内存查询 0.1ms（100-1000 倍）
  - 抗数据库压力
  - 减少网络 / 序列化开销
```

## 2. 多级缓存架构

```
        ┌─ CDN (地理级)         ← 静态资源、距离远
        │   ttl: 1d-30d
        ▼
     ┌─ Nginx / 网关 (集群级)   ← HTML / API 响应
     │   ttl: 1m-1h
     ▼
  ┌─ 本地缓存 (进程内)         ← Cache Aside
  │   Caffeine / Guava       ttl: 1m-10m
  ▼
┌─ Redis / Memcached (分布式) ← 多副本共享
│   ttl: 10m-1h
▼
┌─ 数据库 (持久层)            ← 最终一致源
```

## 3. 缓存三大模式

### Cache Aside（最常用）

```
读：
  1. 查缓存 → 命中？返回
  2. 未命中 → 查 DB → 写缓存 → 返回

写：
  1. 写 DB
  2. 删缓存（不是更新缓存！避免并发写不一致）
```

**代表**：所有主流缓存库都支持。

### Read Through

```
应用只问缓存
  → 缓存没？缓存自己查 DB + 写自己
  → 返回
```

**代表**：Hazelcast / Caffeine loadingCache。

### Write Through

```
应用写缓存
  → 缓存自己写 DB（同步）
  → 返回成功
```

**特点**：强一致，但慢。

### Write Behind（异步回写）

```
应用写缓存（立刻返回）
  缓存自己异步批量写 DB
```

**特点**：最快，但丢数据风险。

## 4. 一致性策略

### Cache Aside + 过期 + 延迟双删

```java
public Product getProduct(Long id) {
  Product cached = redis.get("p:" + id);
  if (cached != null) return cached;

  Product fresh = db.query("SELECT ... WHERE id = ?", id);
  redis.setex("p:" + id, 300, fresh);  // 5min TTL
  return fresh;
}

public void updateProduct(Product p) {
  db.update(p);
  redis.del("p:" + p.getId());       // 立即删
  asyncDelete("p:" + p.getId(), 500);   // 延迟再删一次（防并发脏读）
}
```

**延迟双删**：解决"先删缓存 → 并发请求回填旧值 → 写 DB → DB 旧值"问题。

### Read Through（适合读多写少）

```java
LoadingCache<Long, Product> cache = CacheBuilder.newBuilder()
  .maximumSize(10_000)
  .expireAfterWrite(10, TimeUnit.MINUTES)
  .build(CacheLoader.from(id -> db.query(id)));
```

## 5. 多级缓存协同

```java
// 读：本地 → Redis → DB
Product getProduct(Long id) {
  // 1. 本地内存缓存
  Product p = localCache.get(id);
  if (p != null) return p;

  // 2. Redis
  p = redis.get("p:" + id);
  if (p != null) {
    localCache.set(id, p);
    return p;
  }

  // 3. DB
  p = db.query(id);
  redis.setex("p:" + id, 300, p);
  localCache.set(id, p);
  return p;
}
```

## 6. 缓存架构选型

| 场景 | 推荐 |
|------|------|
| 读多写少（电商详情）| Redis + 本地缓存 |
| 强一致（库存）| DB + 短期缓存 |
| 热点数据 | Caffeine / Guava |
| 大数据量 | Redis Cluster + 分片 |
| 地理分布 | CDN + 多级缓存 |

## 7. 实战：Spring Cache 抽象

```java
@Cacheable(value = "users", key = "#id", unless = "#result == null")
public User getUser(Long id) { ... }

@CachePut(value = "users", key = "#id")
public User updateUser(User u) { ... }

@CacheEvict(value = "users", key = "#id")
public void deleteUser(Long id) { ... }
```

## 8. 实战 checklist

- [ ] TTL 多长？基于业务访问频率
- [ ] 缓存什么？热点数据 vs 全量
- [ ] 失效策略？TTL / 主动失效 / 双删
- [ ] 序列化？JSON / Protobuf
- [ ] 大 key 怎么办？拆 / 压缩
- [ ] 监控？命中率 / 延迟 / 内存

## 🔗 下一步
- [缓存三大问题](/09-cache/breakdown)
- [一致性策略](/09-cache/consistency)
