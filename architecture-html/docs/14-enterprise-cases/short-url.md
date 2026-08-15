---
title: 短链系统
---
# 短链系统设计

## 1. 业务

长链 https://example.com/article/2024/01/15/long-title → 短链 https://ex.co/Ab3xY
点击短链 → 302 跳转长链

## 2. 核心要求

| 要求 | 数值 |
|------|------|
| QPS | 100 万 (读) / 1 万 (写) |
| 延迟 | P99 < 50ms |
| 存储 | 千亿短链 / PB 级 |
| 命中率 | 99.9%（缓存） |

## 3. 整体架构

写短链：长链 → Hash → 短码 → DB + 缓存
  长链 https://example.com/...
  Hash  → SHA256 取前 7 位 → Base62 → 短码 Ab3xY
  存储：DB（持久）+ Redis（缓存）+ CDN

读短链：短码 → 缓存 / DB → 302 跳转
  短码 Ab3xY → 查 Redis 缓存 → 命中返回长链
  → 未命中 → 查 DB → 写回缓存

## 4. 短码生成

### 方案 1：Hash + 截断

```java
String longUrl = "https://example.com/article/2024/01/15/long-title";
String hash = DigestUtils.md5Hex(longUrl);  // 32 字符
String shortCode = hash.substring(0, 6);      // 截 6 位
// 62^6 = 568 亿，足够 100 亿短链
```

问题：hash 冲突（极小但有）→ DB 唯一约束 + 重新生成。

### 方案 2：自增 ID + 进制转换

```java
Long id = autoIncrementId;  // 10 亿 = 10 位
String shortCode = idToBase62(id);
// 1234567890 → "1ly7vk" (62^6 = 568 亿)
```

优：简单、唯一、不冲突。
优：泄露 ID 自增规律（可用 hash 混淆）。

### 方案 3：Snowflake 风格

64-bit id = 1 bit 符号 + 41 bit 时间戳 + 10 bit 机器 + 12 bit 序列
→ base62 编码为短码

优：趋势递增、唯一。

## 5. 存储设计

### DB（持久层）

```sql
CREATE TABLE short_url (
  id BIGINT PRIMARY KEY,                    -- 自增 / Snowflake
  short_code VARCHAR(16) UNIQUE NOT NULL,   -- 短码
  long_url VARCHAR(2048) NOT NULL,         -- 长链
  user_id BIGINT,
  created_at TIMESTAMP,
  expires_at TIMESTAMP NULL,              -- NULL = 永久
  INDEX idx_short_code (short_code),
  INDEX idx_created (created_at)
);
```

### Redis 缓存（读性能）

key:  short:code:{shortCode}
value: {longUrl, createdAt, ttl}
TTL:   30 天（业务可配置）

### 多级缓存

CDN / Nginx  →  Redis →  DB
  1万QPS      50万QPS   1万QPS
  P99<5ms     P99<10ms  P99<50ms

## 6. 重定向策略

### 301 vs 302

| | 301 (永久) | 302 (临时) |
|--|-----------|-----------|
| 浏览器 | 缓存 | 每次重新请求 |
| 适用 | 长链地址稳定 | 短链 + 统计点击 |
| 用途 | 跳转 | 灵活管理 |

实际：用 302（短链通常需要修改或撤销），同时统计点击数据。

### 跳转实现

```java
@GetMapping("/{code}")
public ResponseEntity<Void> redirect(@PathVariable String code) {
  // 1. 查 Redis
  String longUrl = redis.get("short:code:" + code);
  if (longUrl != null) {
    metrics.counter("redirect.cache_hit").inc();
    return ResponseEntity.status(302).header("Location", longUrl).build();
  }

  // 2. 查 DB
  ShortUrl url = shortUrlRepo.findByCode(code).orElse(null);
  if (url == null) return ResponseEntity.notFound().build();

  // 3. 写缓存（TTL 30天）
  redis.setex("short:code:" + code, 30*86400, url.getLongUrl());
  return ResponseEntity.status(302).header("Location", url.getLongUrl()).build();
}
```

## 7. 高并发架构

```
CDN (回源到 NGNX)
  ↓
  100万 QPS
  ↓
NGINX (短链跳转)
  ↓
  50万 QPS
  ↓
Redis Cluster (16 节点)
  ↓
  10万 QPS
  ↓
MySQL (分库分表, 32 库)
  ↓
  1万 QPS
```

性能优化：
- 短链 90% 是"热门"（新闻 / 营销），Redis 缓存 99.9% 命中
- 写短链（发号）QPS = 读短链（跳转）QPS / 100

## 8. 发号器设计

### Snowflake ID

```java
public class ShortUrlGenerator {
  // 1 bit sign | 41 bit timestamp | 5 bit datacenter | 5 bit worker | 12 bit sequence
  public long nextId() {
    return (System.currentTimeMillis() - epoch) << 22 | datacenterId << 17 | workerId << 12 | sequence++;
  }

  public String toShortCode(long id) {
    return Base62.encode(id);
  }
}
```

特点：趋势递增 → 16 库分片按 ID 范围。

### 号段预生成（减少 DB 写）

1. 发号器预生成 1-10000 的 ID
2. 应用按需取（无 DB 写）
3. 短码与 ID 一一对应
4. 定期回填（异步）

性能：写 DB 频率降 100x。

## 9. 防刷与限流

```java
// 每用户每天最多创建 10 个短链
RateLimiter perUserLimiter = RateLimiter.create(10, Duration.ofDays(1));

public String createShortUrl(String longUrl, Long userId) {
  if (!perUserLimiter.tryAcquire(userId)) {
    throw new TooManyRequests("超过每日创建上限");
  }
  return saveShortUrl(longUrl, userId);
}
```

## 10. 监控

- 创建 QPS
- 跳转 QPS
- 缓存命中率
- P99 跳转延迟
- 短链剩余空间（62^6 = 568 亿，够 100 年）
- 黑名单拦截数

## 11. 实战选型

小规模：MySQL + Redis + Nginx（单实例）
中等：MySQL 分库分表 + Redis Cluster + CDN
大：TiDB / OceanBase + Redis Cluster + CDN + K8s
超：阿里云短链服务 / 自研 + 多级缓存

## 12. 安全考虑

- 短链 = 短哈希：可能被遍历（rainbow table）
- 解决：长 ID 转换（无规律）+ 限流 + 异常检测
- 恶意长链：黑名单 URL（病毒 / 钓鱼）
- 鉴权：API 调用短链服务要鉴权（API key / OAuth）

## 🔗 下一步
- [分布式 ID](/10-database-sharding/id)
- [限流令牌桶算法](/04-rate-limit/token-bucket)
- [异地多活](/14-enterprise-cases/multi-region)