---
title: 连接池
date: 2026-08-15  # date-auto-injected
---

# 💧 连接池

> Redis 连接是 **TCP 长连接**，频繁创建/销毁开销巨大。**连接池**预先创建一批连接，重复使用，提升性能。

## 🎯 为什么需要连接池？

```
没有连接池：
  每次请求 → 创建连接 → 发送命令 → 关闭连接
  单次耗时：TCP 三次握手 + 命令执行 + 四次挥手 ≈ 几 ms
  
高并发场景：
  10000 QPS × 1 ms = 10000 ms 总连接时间
  10000 并发连接 → 端口耗尽 / 文件描述符耗尽 / Redis OOM

连接池：
  预先创建 N 个连接，循环使用
  单次命令耗时 < 1 ms（复用连接）
```

## 🔧 Jedis 连接池

```java
JedisPoolConfig poolConfig = new JedisPoolConfig();
poolConfig.setMaxTotal(50);           // 最大连接数（核心配置）
poolConfig.setMaxIdle(20);            // 最大空闲连接
poolConfig.setMinIdle(5);             // 最小空闲连接
poolConfig.setMaxWaitMillis(2000);    // 获取连接的最大等待时间
poolConfig.setTestOnBorrow(true);     // 借出时是否验证
poolConfig.setTestOnReturn(false);
poolConfig.setTestWhileIdle(true);    // 空闲时定时验证

JedisPool pool = new JedisPool(poolConfig, "localhost", 6379, 2000, "password");

try (Jedis jedis = pool.getResource()) {
    jedis.set("key", "value");
}
```

### 关键参数详解

```properties
# 核心参数
maxTotal=50              # 最大连接数（推荐：QPS × 平均响应时间 × 1.5）
maxIdle=20               # 最大空闲连接（避免频繁创建/销毁）
minIdle=5                # 最小空闲连接（保证突发性能）
maxWaitMillis=2000       # 借连接超时（避免无限等待）

# 验证参数（推荐开启）
testOnBorrow=true        # 借出时 PING 验证（推荐生产环境）
testOnReturn=false       # 归还时不验证（节省性能）
testWhileIdle=true       # 空闲时定时验证（推荐开启）

# 高级参数
minEvictableIdleTimeMillis=60000  # 空闲连接最小存活时间（60 秒）
timeBetweenEvictionRunsMillis=30000  # 空闲连接扫描间隔（30 秒）
numTestsPerEvictionRun=-1         # 每次扫描测试连接数（-1 为全部）
```

### 连接数估算公式

```
QPS = 10000
平均响应时间 = 1 ms = 0.001 秒
并发连接数 = QPS × 平均响应时间 = 10

推荐 maxTotal = 并发连接数 × 1.5 ~ 2 = 15 ~ 20

实际生产推荐：
  - 普通业务：maxTotal = 50 ~ 100
  - 高并发业务：maxTotal = 200 ~ 500
```

## 🔧 Lettuce 连接池（可选）

> **Lettuce 默认不需要连接池**（线程安全的单连接足够）。但在事务（MULTI/EXEC）等场景下需要独占连接，可启用连接池。

```java
// Lettuce 启用连接池
GenericObjectPoolConfig<StatefulRedisConnection<String, String>> poolConfig = 
    new GenericObjectPoolConfig<>();
poolConfig.setMaxTotal(50);
poolConfig.setMaxIdle(20);
poolConfig.setMinIdle(5);

GenericObjectPool<StatefulRedisConnection<String, String>> pool =
    ConnectionPoolSupport.createGenericObjectPool(
        () -> client.connect(),
        poolConfig
    );

// 使用
try (StatefulRedisConnection<String, String> connection = pool.borrowObject()) {
    connection.sync().set("key", "value");
}
```

### Lettuce 共享连接 vs 连接池

```
默认共享连接：
  ✅ 1 个连接，多线程共享
  ✅ 节省资源（TCP 连接少）
  ⚠️ 事务场景下需独占（阻塞其他线程）

启用连接池：
  ✅ 事务场景下不阻塞其他线程
  ✅ 隔离性更好
  ⚠️ 资源占用高（50 个连接）
```

## 📊 连接池监控

```java
// JedisPool 监控
JedisPool pool = ...;

// 实时状态
int active = pool.getNumActive();      // 活跃连接数
int idle = pool.getNumIdle();          // 空闲连接数
int waiters = pool.getNumWaiters();    // 等待获取连接的线程数

// 监控告警阈值
if (active / maxTotal > 0.8) {
    // 告警：连接池使用率 80%+
}
if (waiters > 10) {
    // 告警：等待获取连接的线程过多
}
```

```yaml
# Prometheus 监控示例
- name: redis_pool_active
  type: gauge
  help: Active connections in Redis pool
  labels: [pool_name]
  query: jedis_pool_active_connections
```

## ⚠️ 常见连接池问题

### 1. 连接泄漏

```
现象：连接数持续增长，最终耗尽
原因：忘记调用 close() / 异常时未释放
解决：
  1. try-with-resources 自动关闭
  2. finally 中释放
  3. 监控连接数告警
```

```java
// ❌ 错误：可能泄漏
Jedis jedis = pool.getResource();
jedis.set("key", "value");
if (someCondition) {
    return;   // 异常路径忘记 close
}
jedis.close();

// ✅ 正确
try (Jedis jedis = pool.getResource()) {
    jedis.set("key", "value");
}
```

### 2. 连接超时

```
现象：大量 getResource() 超时
原因：maxWaitMillis 设置过小 / 连接数不够
解决：
  1. 调大 maxWaitMillis
  2. 增加 maxTotal
  3. 优化慢命令
  4. 开启连接池监控
```

### 3. 连接不可用

```
现象：报 Could not get a resource from the pool
原因：Redis 服务不可用 / 网络断开
解决：
  1. 启用 testOnBorrow 验证
  2. 启用 testWhileIdle
  3. 配置重试机制
```

## 🔧 Lettuce 多线程 + 共享连接 vs HikariCP

```
❌ 不要为 Redis 使用 HikariCP
  - HikariCP 设计的连接池需要每个线程独占连接
  - Redis 的 Lettuce 已经是线程安全的单连接
  - 强行使用 HikariCP 会浪费大量资源

✅ Lettuce 推荐配置：
  - 默认单连接（多线程共享）
  - 仅在需要事务隔离时启用 Lettuce 自带连接池
```

## 🎯 最佳实践

```
✅ 连接池配置
  - maxTotal = 50 ~ 100（普通业务）
  - 启用 testOnBorrow（生产环境）
  - 启用 testWhileIdle（推荐）

✅ 使用方式
  - try-with-resources 自动关闭
  - finally 块兜底释放

✅ 监控告警
  - 连接池活跃数 / 总数比
  - 等待线程数
  - getResource 耗时
```

## 🎯 总结

**连接池核心要点**：
- ✅ Jedis 必须用连接池（线程不安全）
- ✅ Lettuce 默认不需要（线程安全）
- ✅ 连接数估算：QPS × 响应时间 × 1.5
- ✅ 启用 testOnBorrow / testWhileIdle
- ✅ try-with-resources 自动释放

**下一步：** [🌱 Spring Data Redis](/05-jdk/spring-data-redis) — Spring 统一抽象


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
