---
title: Lettuce
---

# 🥬 Lettuce

> **Lettuce**是基于 **Netty** 的高性能 Redis 客户端，**线程安全**，支持**同步 / 异步 / 响应式**三种模式。Spring Boot 2.x+ 默认客户端。

## 🎯 Lettuce 特点

```
✅ 基于 Netty NIO，性能优秀
✅ 线程安全（多线程共享一个连接）
✅ 同步 / 异步 / 响应式 三种 API
✅ 支持 Redis 6+ 多线程 IO
✅ 支持 Redis Sentinel / Cluster
✅ 支持 Redis 6 客户端缓存（Client-side Caching）
✅ Spring Boot 2.x+ 默认
```

## 📦 引入依赖

```xml
<dependency>
    <groupId>io.lettuce</groupId>
    <artifactId>lettuce-core</artifactId>
    <version>6.3.0.RELEASE</version>
</dependency>
```

## 🚀 快速开始

```java
// 同步 API
RedisClient redisClient = RedisClient.create("redis://localhost:6379");
StatefulRedisConnection<String, String> connection = redisClient.connect();

RedisCommands<String, String> commands = connection.sync();
commands.set("greeting", "Hello Redis");
String value = commands.get("greeting");

connection.close();
redisClient.shutdown();

// 异步 API
RedisAsyncCommands<String, String> async = connection.async();
RedisFuture<String> future = async.get("greeting");
future.thenAccept(v -> System.out.println("Async value: " + v));

// 响应式 API（Reactive Streams）
RedisReactiveCommands<String, String> reactive = connection.reactive();
reactive.set("greeting", "Hello").block();
reactive.get("greeting").subscribe(v -> System.out.println("Reactive: " + v));
```

## 🔒 线程安全

> **Lettuce 一个连接可被多个线程共享**，这是与 Jedis 最大的区别。

```java
StatefulRedisConnection<String, String> connection = redisClient.connect();

// 线程 1
new Thread(() -> {
    connection.sync().set("key1", "value1");
}).start();

// 线程 2
new Thread(() -> {
    String v = connection.sync().get("key2");
    System.out.println(v);
}).start();

// 线程 3
new Thread(() -> {
    connection.async().incr("counter").thenAccept(System.out::println);
}).start();

// ✅ 所有线程共享同一个 connection
// ✅ Lettuce 内部使用线程安全的 Netty Channel
```

**对比 Jedis**：
```
Jedis：线程 1 / 线程 2 / 线程 3 = 3 个连接（线程不安全）
Lettuce：线程 1 / 线程 2 / 线程 3 = 1 个共享连接
```

## 🔧 Lettuce 连接池（可选）

> Lettuce 默认**不需要**连接池（线程安全的单连接足够）。但某些场景下（如事务 MULTI）需要独占连接，可启用连接池。

```java
// Lettuce 连接池（基于 commons-pool2）
GenericObjectPoolConfig<StatefulRedisConnection<String, String>> poolConfig =
    new GenericObjectPoolConfig<>();
poolConfig.setMaxTotal(50);
poolConfig.setMaxIdle(20);
poolConfig.setMinIdle(5);

ConnectionPoolSupport.createGenericObjectPool(
    () -> client.connect(),
    poolConfig
);
```

## ⚙️ 高级配置

```java
ClientOptions options = ClientOptions.builder()
    .autoReconnect(true)                    // 自动重连
    .pingBeforeActivateConnection(true)     // 连接前 ping
    .socketOptions(SocketOptions.builder()
        .connectTimeout(Duration.ofSeconds(2))   // 连接超时
        .keepAlive(true)                          // TCP keepalive
        .build())
    .timeoutOptions(TimeoutOptions.builder()
        .fixedTimeout(Duration.ofSeconds(2))      // 命令超时
        .build())
    .build();

ClientResources resources = ClientResources.builder()
    .ioThreadPoolSize(4)                     // IO 线程数
    .computationThreadPoolSize(4)            // 计算线程数
    .build();

RedisClient client = RedisClient.create(resources, "redis://localhost:6379");
client.setOptions(options);
```

## 🔒 分布式锁（Lettuce 实现）

```java
@Component
public class LettuceLock {
    
    @Autowired
    private StringRedisTemplate redisTemplate;  // Spring Data Redis
    
    public boolean tryLock(String key, String requestId, long expireSeconds) {
        Boolean result = redisTemplate.opsForValue()
            .setIfAbsent(key, requestId, expireSeconds, TimeUnit.SECONDS);
        return Boolean.TRUE.equals(result);
    }
    
    public boolean unlock(String key, String requestId) {
        String lua = "if redis.call('get', KEYS[1]) == ARGV[1] then "
                   + "return redis.call('del', KEYS[1]) else return 0 end";
        DefaultRedisScript<Long> script = new DefaultRedisScript<>(lua, Long.class);
        Long result = redisTemplate.execute(script, Arrays.asList(key), requestId);
        return result != null && result > 0;
    }
}
```

## 🔀 Cluster 集群

```java
// Cluster 客户端（自动路由）
RedisClusterClient clusterClient = RedisClusterClient.create("redis://192.168.1.10:7001");

// 拓扑刷新（自动发现新节点）
clusterClient.reloadPartitions();

// 同步连接（自动路由到正确的 Master）
StatefulRedisClusterConnection<String, String> connection = clusterClient.connect();
RedisAdvancedClusterCommands<String, String> commands = connection.sync();

commands.set("user:1", "Alice");           // 自动路由到 slot 5258 对应的 Master
String value = commands.get("user:1");

// 跨槽操作
commands.set("user:{1001}:name", "Alice");
commands.set("user:{1001}:age", "28");
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
    lettuce:
      pool:
        max-active: 50
        max-idle: 20
        min-idle: 5
        max-wait: 2000ms
      shutdown-timeout: 200ms
```

```java
@Configuration
public class LettuceConfig {
    
    @Bean
    public LettuceConnectionFactory lettuceConnectionFactory(RedisProperties properties) {
        RedisStandaloneConfiguration standalone = new RedisStandaloneConfiguration();
        standalone.setHostName(properties.getHost());
        standalone.setPort(properties.getPort());
        standalone.setPassword(properties.getPassword());
        
        ClientOptions options = ClientOptions.builder()
            .autoReconnect(true)
            .build();
        
        LettuceClientConfiguration clientConfig = LettuceClientConfiguration.builder()
            .commandTimeout(Duration.ofSeconds(2))
            .clientOptions(options)
            .build();
        
        return new LettuceConnectionFactory(standalone, clientConfig);
    }
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate(LettuceConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);
        
        Jackson2JsonRedisSerializer<Object> jacksonSerializer = 
            new Jackson2JsonRedisSerializer<>(Object.class);
        
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(jacksonSerializer);
        template.setHashKeySerializer(new StringRedisSerializer());
        template.setHashValueSerializer(jacksonSerializer);
        
        return template;
    }
}
```

## 📊 性能对比

| 维度 | Jedis | Lettuce |
|------|-------|---------|
| **10 万次 GET** | ~5000ms | ~2000ms |
| **Pipeline 1000 命令** | ~50ms | ~30ms |
| **连接数（高并发）** | 50 | 1 |
| **内存占用** | 高（50 连接） | 低（1 连接） |
| **异步 API** | ❌ | ✅ |
| **响应式** | ❌ | ✅ |

## 🚀 异步与响应式示例

### 异步批量操作

```java
RedisAsyncCommands<String, String> async = connection.async();

// 并行发起多个命令
RedisFuture<String> f1 = async.get("key1");
RedisFuture<String> f2 = async.get("key2");
RedisFuture<String> f3 = async.get("key3");

// 一次性获取所有结果
CompletableFuture.allOf(f1, f2, f3)
    .thenRun(() -> {
        try {
            String v1 = f1.get();
            String v2 = f2.get();
            String v3 = f3.get();
            System.out.println(v1 + " " + v2 + " " + v3);
        } catch (Exception e) {
            e.printStackTrace();
        }
    });
```

### 响应式 Pipeline

```java
RedisReactiveCommands<String, String> reactive = connection.reactive();

Flux.just("key1", "key2", "key3", "key4", "key5")
    .flatMap(reactive::get)
    .doOnNext(System.out::println)
    .subscribe();
```

## 🎯 总结

**Lettuce 核心要点**：
- ✅ 基于 Netty NIO，高性能
- ✅ 线程安全，多线程共享连接
- ✅ 同步 / 异步 / 响应式 三种 API
- ✅ Spring Boot 2.x+ 默认客户端
- ⚠️ 某些场景需连接池（如事务）

**下一步：** [🔴 Redisson](/05-jdk/redisson) — 分布式工具集
