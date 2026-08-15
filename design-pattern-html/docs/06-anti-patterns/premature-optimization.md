---
title: Premature Optimization 提前优化
description: 症状 + 病因 + 药方 + 性能分析 + Knuth 法则
---

# Premature Optimization 提前优化

## 症状

```java
// 为了不存在的瓶颈写复杂代码
public class OrderRepository {
    // 3 层缓存 + Redis + 本地 LRU + 数据库
    public Order findById(long id) {
        Order o = lruCache.get(id);
        if (o == null) {
            o = caffeineCache.get(id);
            if (o == null) {
                o = redis.get(id);
                if (o == null) {
                    o = jdbc.query("SELECT * FROM orders WHERE id = ?", id);
                    redis.set(id, o);
                    caffeineCache.put(id, o);
                }
                lruCache.put(id, o);
            }
        }
        return o;
    }
}
```

**典型表现**：
1. 多层缓存（LRU + Caffeine + Redis）但没测过性能瓶颈
2. 「听说 Redis 很快」就加缓存
3. 复杂索引（联合索引 + 部分索引 + 函数索引）但 QPS 不高
4. 自定义数据结构替代 ArrayList / HashMap（但数据量不大）
5. 异步 / 并发代码（但 QPS 只有 100）

## 病因

1. **Donald Knuth 警告过：「过早优化是万恶之源」**
   - 但被很多人「选择性遗忘」

2. **没做 profiling 就开始优化**
   - 不测就猜性能瓶颈
   - 90% 的猜测是错的

3. **「听说 Redis 很快」就加缓存**
   - 没考虑：数据一致性 / 缓存穿透 / 缓存雪崩
   - 没考虑：维护成本 > 性能收益

4. **「听说并行更快」就加并发**
   - 没考虑：线程切换开销 / 锁竞争 / 死锁风险

5. **追求「完美架构」**
   - 复杂架构有学习成本和维护成本
   - 简单架构 80% 够用

6. **老板/PM 压力**
   - 「能不能跑得更快一点」
   - 没数据支撑的优化

## 药方

## 1. 先测量，后优化

```bash
# Java: JMH (Java Microbenchmark Harness)
jmh -prof gc -wi 5 -i 5 -f 1 .
# 输出：每个方法的吞吐量 / 平均时间 / GC 次数

# Go: pprof + benchmark
go test -bench=. -benchmem -cpuprofile=cpu.p
go tool pprof cpu.p
# 交互：(pprof) top10  // 看 CPU 占用最高的方法

# Python: cProfile
python -m cProfile -s cumtime script.py

# Node.js: 0x / clinic.js
clinic doctor -- node server.js

# 通用：APM 工具
# - Java: Arthas / async-profiler
# - Go: pprof / continuous profiling (Pyroscope)
# - Python: py-spy / Scalene
```

## 2. 80/20 法则

20% 的代码承担 80% 的性能问题：

```bash
# 找出热点（用 pprof）
go tool pprof cpu.p
(pprof) top10
# 80% 的 CPU 时间都在 /usr/local/go/net/http/server.go
# → 优化 HTTP 框架不是优化你的代码

(pprof) list myFunction
# 看自己的函数在做什么
```

## 3. YAGNI（You Aren't Gonna Need It）

```java
// ❌ 提前优化
public class UserService {
    // "未来可能有 100 万用户" → 加分页 + 缓存 + 多级缓存
    public List<User> findAll(int page, int size) {
        // 实际上系统只有 1000 用户
    }
}

// ✅ YAGNI：先实现再说
public class UserService {
    public List<User> findAll() {
        return userRepo.findAll();
    }
    // 真的有性能问题再加分页
}
```

## 4. Knuth 原文

```text
"We should forget about small efficiencies, say about 97% of the time:
premature optimization is the root of all evil.

Yet we should not pass up our opportunities in that critical 3%."
                                    —— Donald Knuth, 1974
```

**翻译**：97% 的情况下忘掉那些小效率（不要为它们优化），提前优化是万恶之源。但在关键的 3% 上不要放弃优化机会。

**关键**：**先测量再优化**，确定那 3% 在哪。

## 实战案例：缓存降级

## 第一次实现（YAGNI）

```java
@Service
public class ProductService {
    @Autowired private ProductRepository repo;

    public Product findById(long id) {
        return repo.findById(id).orElseThrow();
    }
}
```

**性能**：100 QPS，平均延迟 5ms。**完全够用**。

## 性能问题出现（QPS 10000）

```bash
# pprof 报告显示 ProductService.findById 占 60% CPU
# 原因：DB 查询 + 网络 IO
```

## 添加一级缓存（Redis）

```java
@Service
public class ProductService {
    @Autowired private ProductRepository repo;
    @Autowired private RedisTemplate<String, Product> redis;

    public Product findById(long id) {
        // 1. 先查 Redis
        Product cached = redis.opsForValue().get("product:" + id);
        if (cached != null) return cached;

        // 2. 缓存未命中，查 DB
        Product product = repo.findById(id).orElseThrow();

        // 3. 写入 Redis
        redis.opsForValue().set("product:" + id, product, Duration.ofMinutes(10));
        return product;
    }
}
```

**性能**：5000 QPS，平均延迟 1ms。

## 仍然不够（QPS 50000）

```bash
# 再 profile 发现 Redis IO 占 40%
# 加本地缓存（Caffeine）
```

## 优化到极致（多级缓存）

```java
@Service
public class ProductService {
    @Autowired private ProductRepository repo;
    @Autowired private RedisTemplate<String, Product> redis;
    
    private final Cache<Long, Product> localCache = Caffeine.newBuilder()
        .maximumSize(10_000)
        .expireAfterWrite(Duration.ofMinutes(1))
        .build();

    public Product findById(long id) {
        // 1. 本地缓存（最快）
        Product cached = localCache.getIfPresent(id);
        if (cached != null) return cached;

        // 2. Redis
        cached = redis.opsForValue().get("product:" + id);
        if (cached != null) {
            localCache.put(id, cached);
            return cached;
        }

        // 3. DB
        Product product = repo.findById(id).orElseThrow();

        // 4. 写入两级缓存
        redis.opsForValue().set("product:" + id, product, Duration.ofMinutes(10));
        localCache.put(id, product);
        return product;
    }
}
```

**性能**：50000 QPS，平均延迟 0.1ms。

## 演进路径（关键）

| QPS | 实现 | 复杂度 |
|---|---|---|
| 100 | 直接查 DB | ⭐ |
| 5000 | + Redis 一级缓存 | ⭐⭐ |
| 50000 | + Caffeine 本地缓存 | ⭐⭐⭐ |
| 200000 | + 多级缓存 + 数据预热 | ⭐⭐⭐⭐ |

**关键**：每一步都有数据支撑，**不是提前实现的**。

## 常见过早优化

## 1. 多层缓存（无 profiling）

```java
// ❌ 不必要的复杂
LRU + Caffeine + Redis + DB

// ✅ 真有性能问题再加
// 单层 Redis 解决 80% 场景
```

## 2. 自定义数据结构（无业务量）

```java
// ❌ 自定义跳表（数据量 < 1 万）
public class CustomSkipList<K, V> { /* 500 行 */ }

// ✅ Java 标准库够用
ConcurrentSkipListMap<K, V>
```

## 3. 复杂索引（无 QPS）

```sql
-- ❌ 加 5 个联合索引（QPS 只有 100）
CREATE INDEX idx1 ON orders(user_id, status, created_at);
CREATE INDEX idx2 ON orders(status, user_id, created_at);
-- ...

-- ✅ 单索引解决 80% 查询
CREATE INDEX idx_user_status ON orders(user_id, status);
```

## 4. 异步 + 队列（无并发量）

```java
// ❌ 所有操作都异步（QPS < 1000）
@Async public CompletableFuture<Order> create() { /* ... */ }

// ✅ 同步阻塞（QPS < 1000 完全可以）
public Order create() { /* 简单清晰 */ }
```

## 5. 微服务拆分（业务简单）

```java
// ❌ 5 个微服务（业务只有 3 个模块）
order-service / payment-service / inventory-service / shipping-service / notification-service

// ✅ 单体或模块化单体（业务初期）
OrderModule { /* 5 个 Service 放一起 */ }
```

## 何时优化 / 何时不优化

## 不优化（97% 场景）

- ✅ 业务代码读起来清晰
- ✅ 性能不构成瓶颈（QPS < 1000）
- ✅ 没有用户投诉
- ✅ 没有 SLA 要求

## 优化（3% 场景）

- ⚠️ 监控告警：接口延迟 P99 > 1s
- ⚠️ 用户反馈：页面卡顿
- ⚠️ 容量预警：CPU / 内存使用率 > 80%
- ⚠️ 业务峰值：双 11 / 618 等大促

## 优化的正确流程

```text
1. 监控发现性能问题（不是猜的）
   ↓
2. profiling 找到瓶颈（不是拍脑袋）
   ↓
3. 优化瓶颈（最小改动）
   ↓
4. 验证优化效果（A/B 测试）
   ↓
5. 监控确认问题解决
   ↓
6. 记录到知识库（避免重复犯）
```

## 优化原则

1. **先测量后优化**（不要猜）
2. **80/20**（优化 20% 代码解决 80% 问题）
3. **简单优先**（单层 Redis 解决 80% 缓存问题）
4. **数据说话**（优化前后对比）
5. **回滚预案**（优化可能引入 bug）

## 适用边界

✅ **避免优化**：
- 业务代码读起来清晰
- QPS < 1000
- 没有 SLA 要求
- 没有用户投诉

⚠️ **需要优化**：
- P99 > 1s（接口太慢）
- CPU / 内存 > 80%（资源紧张）
- 业务峰值（大促 / 突发流量）
- SLA 要求（P99 < 100ms）

💡 **最佳实践**：
- **监控先行**：APM 工具（SkyWalking / Datadog / Pyroscope）
- **profiling 工具**：JMH / pprof / async-profiler
- **性能测试**：JMeter / k6 / Gatling
- **A/B 测试**：优化前后对比
- **回滚预案**：优化可能引入 bug
- **文档记录**：每个优化都有 ADR
