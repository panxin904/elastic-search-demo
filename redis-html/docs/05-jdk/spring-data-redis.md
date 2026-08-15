---
title: Spring Data Redis
---

# 🌱 Spring Data Redis

> Spring Data Redis 是 Spring 提供的 Redis 统一抽象层，封装了 Jedis / Lettuce，提供 `RedisTemplate` 和 `StringRedisTemplate` 统一 API。

## 🎯 Spring Data Redis 特点

```
✅ 统一 API（屏蔽 Jedis / Lettuce 差异）
✅ RedisTemplate + StringRedisTemplate
✅ 内置序列化器（String / Jackson / JDK）
✅ 自动管理连接池
✅ 支持 Pipeline / 事务 / Pub/Sub
✅ 支持 Cluster / Sentinel
✅ 与 Spring Cache / Spring Session 集成
```

## 📦 引入依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

## 🚀 快速开始

```yaml
# application.yml
spring:
  redis:
    host: localhost
    port: 6379
    password: yourpassword
    timeout: 2000ms
    database: 0
    lettuce:
      pool:
        max-active: 50
        max-idle: 20
        min-idle: 5
```

```java
@Service
public class UserService {
    
    @Autowired
    private StringRedisTemplate redisTemplate;
    
    public void saveUser(User user) {
        redisTemplate.opsForValue().set("user:" + user.getId(), user.getName());
    }
    
    public String getUser(Long id) {
        return redisTemplate.opsForValue().get("user:" + id);
    }
}
```

## 🔧 RedisTemplate API

```java
// String 操作
redisTemplate.opsForValue().set("key", "value");
redisTemplate.opsForValue().set("key", "value", 60, TimeUnit.SECONDS);
String v = redisTemplate.opsForValue().get("key");
Long count = redisTemplate.opsForValue().increment("counter");
Boolean hasKey = redisTemplate.hasKey("key");

// Hash 操作
redisTemplate.opsForHash().put("user:1", "name", "Alice");
redisTemplate.opsForHash().put("user:1", "age", "28");
Map<Object, Object> entries = redisTemplate.opsForHash().entries("user:1");
Object name = redisTemplate.opsForHash().get("user:1", "name");

// List 操作
redisTemplate.opsForList().leftPush("tasks", "task1");
redisTemplate.opsForList().rightPush("tasks", "task2");
List<Object> tasks = redisTemplate.opsForList().range("tasks", 0, -1);
Object first = redisTemplate.opsForList().leftPop("tasks");

// Set 操作
redisTemplate.opsForSet().add("tags", "redis", "db");
Set<Object> tags = redisTemplate.opsForSet().members("tags");
Boolean isMember = redisTemplate.opsForSet().isMember("tags", "redis");

// ZSet 操作
redisTemplate.opsForZSet().add("leaderboard", "Alice", 95);
Set<Object> top = redisTemplate.opsForZSet().reverseRange("leaderboard", 0, 9);
Double score = redisTemplate.opsForZSet().score("leaderboard", "Alice");

// Key 通用操作
redisTemplate.delete("key");
redisTemplate.expire("key", 60, TimeUnit.SECONDS);
redisTemplate.getExpire("key");
Set<String> keys = redisTemplate.keys("user:*");
```

## 🔄 序列化器对比（关键）

> Spring Data Redis 默认使用 **JDK 序列化**（二进制，不易读）。生产环境强烈推荐改用 **Jackson** 或 **String**。

| 序列化器 | 类 | 优点 | 缺点 |
|---------|---|------|------|
| **StringRedisSerializer** | String | 简单、跨语言 | 只能序列化 String |
| **Jackson2JsonRedisSerializer** | JSON | 跨语言、可读 | 性能略低 |
| **GenericJackson2JsonRedisSerializer** | JSON | 带类型信息 | 性能略低 |
| **JdkSerializationRedisSerializer** | Java | 默认 | 二进制、不可读、不可跨语言 |

```java
@Configuration
public class RedisConfig {
    
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);
        
        // JSON 序列化器
        Jackson2JsonRedisSerializer<Object> jsonSerializer = 
            new Jackson2JsonRedisSerializer<>(Object.class);
        
        // String 序列化 key
        StringRedisSerializer stringSerializer = new StringRedisSerializer();
        
        template.setKeySerializer(stringSerializer);
        template.setHashKeySerializer(stringSerializer);
        template.setValueSerializer(jsonSerializer);
        template.setHashValueSerializer(jsonSerializer);
        
        template.afterPropertiesSet();
        return template;
    }
}
```

## 📊 序列化器性能对比

```
序列化 10000 个 User 对象（JSON 字段约 200 字节）：

StringRedisSerializer：
  写入：~50 ms
  读取：~30 ms

Jackson2JsonRedisSerializer：
  写入：~150 ms
  读取：~120 ms

JdkSerializationRedisSerializer：
  写入：~30 ms
  读取：~20 ms
  （二进制，不可读）

Jdk 反序列化漏洞警告：
  ⚠️ JDK 序列化存在反序列化漏洞风险
  ⚠️ 生产环境强烈推荐改用 Jackson 或 String
```

## 🚄 Pipeline 批量操作

```java
List<Object> results = redisTemplate.executePipelined((RedisCallback<Object>) connection -> {
    StringRedisConnection stringConn = (StringRedisConnection) connection;
    for (int i = 0; i < 1000; i++) {
        stringConn.set("key:" + i, "value" + i);
    }
    return null;
});
```

## 🔒 事务

```java
// 启用事务支持
@Bean
public PlatformTransactionManager transactionManager(DataSource dataSource) {
    return new DataSourceTransactionManager(dataSource);
}

// 编程式事务
redisTemplate.execute(new SessionCallback<Object>() {
    @Override
    public Object execute(RedisOperations operations) throws DataAccessException {
        operations.multi();
        operations.opsForValue().set("key1", "value1");
        operations.opsForValue().set("key2", "value2");
        return operations.exec();
    }
});

// @Transactional 注解（注意：Redis 事务不保证原子性回滚）
@Transactional
public void updateRedis() {
    redisTemplate.opsForValue().set("key", "value");
}
```

## ⚠️ 异常处理

```java
try {
    redisTemplate.opsForValue().get("key");
} catch (RedisConnectionFailureException e) {
    // Redis 服务不可用
    log.error("Redis connection failed", e);
} catch (RedisSystemException e) {
    // Redis 系统错误
    log.error("Redis system error", e);
} catch (RedisCommandTimeoutException e) {
    // 命令超时
    log.warn("Redis command timeout", e);
}
```

## 🔧 Cluster 集群

```yaml
spring:
  redis:
    cluster:
      nodes:
        - 192.168.1.10:7001
        - 192.168.1.10:7002
        - 192.168.1.10:7003
        - 192.168.1.10:7004
        - 192.168.1.10:7005
        - 192.168.1.10:7006
      max-redirects: 3
```

## 🔧 Sentinel 高可用

```yaml
spring:
  redis:
    sentinel:
      master: mymaster
      nodes:
        - 192.168.1.10:26379
        - 192.168.1.11:26379
        - 192.168.1.12:26379
      password: yourpassword
```

## 🛠️ 实战：自定义 RedisTemplate

```java
@Configuration
public class RedisConfig {
    
    @Bean
    public StringRedisTemplate stringRedisTemplate(RedisConnectionFactory factory) {
        return new StringRedisTemplate(factory);
    }
    
    @Bean
    public RedisTemplate<String, User> userRedisTemplate(RedisConnectionFactory factory) {
        RedisTemplate<String, User> template = new RedisTemplate<>();
        template.setConnectionFactory(factory);
        
        Jackson2JsonRedisSerializer<User> serializer = 
            new Jackson2JsonRedisSerializer<>(User.class);
        
        template.setKeySerializer(new StringRedisSerializer());
        template.setValueSerializer(serializer);
        
        return template;
    }
}
```

```java
@Autowired
private RedisTemplate<String, User> userRedisTemplate;

public void saveUser(User user) {
    userRedisTemplate.opsForValue().set("user:" + user.getId(), user);
}

public User getUser(Long id) {
    return userRedisTemplate.opsForValue().get("user:" + id);
}
```

## 🎯 总结

**Spring Data Redis 核心要点**：
- ✅ 统一抽象，屏蔽 Jedis / Lettuce 差异
- ✅ RedisTemplate + StringRedisTemplate
- ✅ 序列化器：Jackson 推荐，JDK 不推荐
- ✅ Pipeline / 事务 / Pub/Sub 全支持
- ⚠️ JDK 序列化有反序列化漏洞风险
- ⚠️ Redis 事务不保证原子性

**下一步：** [🎁 Spring Cache 集成](/05-jdk/spring-cache) — 注解式缓存
