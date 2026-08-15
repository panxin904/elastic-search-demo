---
title: Jedis
---

# 🔧 Jedis

> **Jedis**是 Redis 官方推荐的 Java 客户端，**阻塞式同步**调用，简单易用。Spring Boot 1.x 默认使用。

## 🎯 Jedis 特点

```
✅ 同步阻塞 API，简单直接
✅ 官方维护，质量稳定
✅ 连接池支持（commons-pool2）
✅ Pipeline、事务、Pub/Sub
✅ Cluster 集群支持
❌ 线程不安全（每个线程一个连接）
❌ 不支持异步和响应式
❌ 不支持 Redis 6+ 多线程 IO
```

## 📦 引入依赖

```xml
<!-- Maven -->
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
    <version>5.1.0</version>
</dependency>

<!-- Spring Boot 集成 -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
    <exclusions>
        <exclusion>
            <groupId>io.lettuce</groupId>
            <artifactId>lettuce-core</artifactId>
        </exclusion>
    </exclusions>
</dependency>
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
</dependency>
```

## 🚀 快速开始

```java
// 1. 基本连接
Jedis jedis = new Jedis("localhost", 6379);
jedis.set("greeting", "Hello Redis");
String value = jedis.get("greeting");
System.out.println(value);  // Hello Redis
jedis.close();

// 2. 带密码连接
Jedis jedis = new Jedis("localhost", 6379);
jedis.auth("password");
```

## 💧 连接池（推荐）

```java
// 1. 创建连接池
JedisPoolConfig poolConfig = new JedisPoolConfig();
poolConfig.setMaxTotal(50);          // 最大连接数
poolConfig.setMaxIdle(20);           // 最大空闲连接
poolConfig.setMinIdle(5);            // 最小空闲连接
poolConfig.setMaxWaitMillis(2000);  // 最大等待时间（毫秒）
poolConfig.setTestOnBorrow(true);    // 借用时测试

JedisPool pool = new JedisPool(poolConfig, "localhost", 6379, 2000, "password");

// 2. 使用连接池
try (Jedis jedis = pool.getResource()) {
    jedis.set("user:1", "Alice");
    String value = jedis.get("user:1");
}
```

## 📊 5 大类型操作

```java
try (Jedis jedis = pool.getResource()) {
    // String
    jedis.set("user:1:name", "Alice");
    String name = jedis.get("user:1:name");
    jedis.incr("counter");
    jedis.expire("user:1:name", 60);
    
    // Hash
    jedis.hset("user:1", "name", "Alice");
    jedis.hset("user:1", "age", "28");
    Map<String, String> user = jedis.hgetAll("user:1");
    jedis.hincrBy("user:1", "age", 1);
    
    // List
    jedis.lpush("tasks", "task1", "task2");
    List<String> tasks = jedis.lrange("tasks", 0, -1);
    jedis.rpush("tasks", "task3");
    String task = jedis.lpop("tasks");
    
    // Set
    jedis.sadd("tags:article:1", "redis", "db");
    Set<String> tags = jedis.smembers("tags:article:1");
    boolean isMember = jedis.sismember("tags:article:1", "redis");
    
    // ZSet
    jedis.zadd("leaderboard", 95, "Alice");
    jedis.zadd("leaderboard", 87, "Bob");
    List<String> top = jedis.zrevrange("leaderboard", 0, 9);
}
```

## 🚄 Pipeline（性能优化）

> 批量执行命令，减少网络往返。

```java
try (Jedis jedis = pool.getResource()) {
    Pipeline pipeline = jedis.pipelined();
    
    for (int i = 0; i < 1000; i++) {
        pipeline.set("key:" + i, "value" + i);
        pipeline.expire("key:" + i, 60);
    }
    
    // 一次性发送所有命令
    List<Object> results = pipeline.syncAndReturnAll();
    System.out.println("1000 commands executed");
}
```

**性能对比**：
- 单命令 1000 次：~1000 ms
- Pipeline 1000 命令：~10 ms（提升 100 倍）

## 🔒 事务

```java
try (Jedis jedis = pool.getResource()) {
    // WATCH + MULTI + EXEC 实现乐观锁
    jedis.watch("counter");
    String value = jedis.get("counter");
    int newValue = Integer.parseInt(value) + 1;
    
    Transaction tx = jedis.multi();
    tx.set("counter", String.valueOf(newValue));
    List<Object> result = tx.exec();
    
    if (result == null) {
        // WATCH 失败，重试
    }
}
```

## 🔒 分布式锁

```java
// 简单的分布式锁
public class RedisLock {
    private JedisPool pool;
    private String lockKey;
    private int expireSeconds = 30;
    
    public boolean tryLock(String requestId) {
        try (Jedis jedis = pool.getResource()) {
            // SET key value EX seconds NX
            String result = jedis.set(lockKey, requestId, 
                SetParams.setParams().nx().ex(expireSeconds));
            return "OK".equals(result);
        }
    }
    
    public boolean unlock(String requestId) {
        // Lua 脚本保证原子性
        String lua = "if redis.call('get', KEYS[1]) == ARGV[1] then "
                   + "return redis.call('del', KEYS[1]) else return 0 end";
        try (Jedis jedis = pool.getResource()) {
            Object result = jedis.eval(lua, 1, lockKey, requestId);
            return "1".equals(result.toString());
        }
    }
}
```

## 🔀 Cluster 集群

```java
// Jedis Cluster
Set<HostAndPort> nodes = new HashSet<>();
nodes.add(new HostAndPort("192.168.1.10", 7001));
nodes.add(new HostAndPort("192.168.1.10", 7002));
nodes.add(new HostAndPort("192.168.1.10", 7003));

JedisCluster cluster = new JedisCluster(nodes, 2000, 2000, 3, "password", poolConfig);

// 自动路由到正确的 Master
cluster.set("user:1", "Alice");
String value = cluster.get("user:1");

// 跨槽操作需要 hash tag
cluster.set("user:{1001}:name", "Alice");
cluster.set("user:{1001}:age", "28");

cluster.close();
```

## 🔧 Spring Boot 集成

```yaml
# application.yml
spring:
  redis:
    host: localhost
    port: 6379
    password: yourpassword
    timeout: 2000ms
    jedis:
      pool:
        max-active: 50
        max-idle: 20
        min-idle: 5
        max-wait: 2000ms
```

```java
@Configuration
public class JedisConfig {
    
    @Bean
    public JedisPool jedisPool(RedisProperties properties) {
        JedisPoolConfig config = new JedisPoolConfig();
        config.setMaxTotal(50);
        config.setMaxIdle(20);
        config.setMinIdle(5);
        
        RedisProperties.Pool pool = properties.getJedis().getPool();
        if (pool != null) {
            config.setMaxTotal(pool.getMaxActive());
            config.setMaxIdle(pool.getMaxIdle());
            config.setMinIdle(pool.getMinIdle());
        }
        
        return new JedisPool(config,
            properties.getHost(),
            properties.getPort(),
            properties.getTimeout().toMillis(),
            properties.getPassword());
    }
}
```

## ⚙️ 关键配置

```properties
# Jedis 连接参数
spring.redis.host=localhost
spring.redis.port=6379
spring.redis.password=password
spring.redis.timeout=2000              # 连接 / 读超时（毫秒）
spring.redis.client-name=my-app        # 客户端名称（用于排错）

# 连接池参数
spring.redis.jedis.pool.max-active=50   # 最大连接
spring.redis.jedis.pool.max-idle=20     # 最大空闲
spring.redis.jedis.pool.min-idle=5      # 最小空闲
spring.redis.jedis.pool.max-wait=2000   # 最大等待（毫秒）

# Cluster 参数
spring.redis.cluster.nodes=192.168.1.10:7001,192.168.1.10:7002,192.168.1.10:7003
spring.redis.cluster.max-redirects=3    # MOVED 重定向最大次数
```

## 🔄 Jedis vs Lettuce

| 维度 | Jedis | Lettuce |
|------|-------|---------|
| 线程安全 | ❌ 每个线程一个连接 | ✅ 多线程共享 |
| 同步 API | ✅ | ✅ |
| 异步 API | ❌ | ✅ |
| 响应式 | ❌ | ✅ |
| 性能 | 略低（阻塞） | 更高（Netty） |
| Spring Boot 默认 | 1.x 默认 | 2.x+ 默认 |
| 推荐场景 | 简单应用、Redis 6.0- | 现代应用、高并发 |

## 🎯 总结

**Jedis 核心要点**：
- ✅ 官方同步客户端，简单易用
- ✅ 必用连接池（JedisPool）
- ✅ Pipeline 批量操作提升性能
- ⚠️ 线程不安全（每个线程一个连接）
- ⚠️ 不支持异步和响应式（推荐 Lettuce）

**下一步：** [🥬 Lettuce](/05-jdk/lettuce) — 现代异步客户端
