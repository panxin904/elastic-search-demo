---
title: Spring Cache 集成
---

# 🎁 Spring Cache 集成

> Spring Cache 是 Spring 提供的**缓存抽象层**，通过注解方式实现方法级缓存。支持 Redis、Caffeine、EhCache 等多种实现。

## 🎯 Spring Cache 特点

```
✅ 注解式缓存（@Cacheable / @CachePut / @CacheEvict）
✅ 抽象层，可切换实现（Redis / Caffeine / EhCache）
✅ 与 Spring 事务集成
✅ 支持多级缓存
✅ 支持自定义 KeyGenerator
✅ 支持 TTL（Time-To-Live）
```

## 📦 引入依赖

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-cache</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
</dependency>
```

## 🚀 快速开始

```java
@SpringBootApplication
@EnableCaching    // 启用缓存
public class Application { }

@Service
public class UserService {
    
    // 第一次查询数据库，后续从缓存取
    @Cacheable(value = "users", key = "#id")
    public User getUser(Long id) {
        System.out.println("Querying database for user: " + id);
        return userMapper.findById(id);
    }
    
    // 更新时删除缓存
    @CachePut(value = "users", key = "#user.id")
    @CacheEvict(value = "users", key = "#user.id")
    public User updateUser(User user) {
        userMapper.update(user);
        return user;
    }
    
    // 删除时清空缓存
    @CacheEvict(value = "users", key = "#id")
    public void deleteUser(Long id) {
        userMapper.delete(id);
    }
}
```

## 📌 核心注解

### @Cacheable（查缓存）

```java
// value：缓存名称（对应 Redis key 前缀）
// key：缓存 key（SpEL 表达式）
@Cacheable(value = "users", key = "#id")
public User getUser(Long id) { ... }

// condition：满足条件才缓存
@Cacheable(value = "users", key = "#id", condition = "#id > 0")
public User getUser(Long id) { ... }

// unless：不满足条件才缓存（结果判断）
@Cacheable(value = "users", key = "#id", unless = "#result == null")
public User getUser(Long id) { ... }

// sync：同步模式（避免缓存击穿）
@Cacheable(value = "users", key = "#id", sync = true)
public User getUser(Long id) { ... }
```

### @CachePut（更新缓存）

```java
// 方法执行后更新缓存（不影响方法返回值）
@CachePut(value = "users", key = "#user.id")
public User updateUser(User user) {
    userMapper.update(user);
    return user;
}
```

### @CacheEvict（清空缓存）

```java
// 单 key 删除
@CacheEvict(value = "users", key = "#id")
public void deleteUser(Long id) { ... }

// allEntries：清空所有
@CacheEvict(value = "users", allEntries = true)
public void clearAllUsers() { ... }

// beforeInvocation：方法执行前清空
@CacheEvict(value = "users", key = "#id", beforeInvocation = true)
public void deleteUser(Long id) { ... }
```

### @Caching（组合）

```java
@Caching(
    cacheable = @Cacheable(value = "user", key = "#id"),
    evict = {
        @CacheEvict(value = "user-list", key = "#id"),
        @CacheEvict(value = "user-detail", key = "#id")
    }
)
public User getUserWithMulti(Long id) { ... }
```

## ⚙️ Redis 缓存配置

```java
@Configuration
@EnableCaching
public class CacheConfig {
    
    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory factory) {
        // 全局配置
        RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10))    // 默认 TTL 10 分钟
            .disableCachingNullValues()          // 不缓存 null
            .serializeKeysWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new StringRedisSerializer()))
            .serializeValuesWith(RedisSerializationContext.SerializationPair
                .fromSerializer(new GenericJackson2JsonRedisSerializer()));
        
        // 针对不同缓存设置不同 TTL
        Map<String, RedisCacheConfiguration> configs = new HashMap<>();
        configs.put("users", defaultConfig.entryTtl(Duration.ofMinutes(30)));
        configs.put("products", defaultConfig.entryTtl(Duration.ofHours(1)));
        configs.put("sessions", defaultConfig.entryTtl(Duration.ofMinutes(5)));
        
        return RedisCacheManager.builder(factory)
            .cacheDefaults(defaultConfig)
            .withInitialCacheConfigurations(configs)
            .build();
    }
}
```

## 🎯 多级缓存（Caffeine + Redis）

> 本地缓存（Caffeine）+ 分布式缓存（Redis），兼顾速度和一致性。

```xml
<dependency>
    <groupId>com.github.ben-manes.caffeine</groupId>
    <artifactId>caffeine</artifactId>
</dependency>
```

```java
@Configuration
@EnableCaching
public class CacheConfig {
    
    @Bean
    public CacheManager cacheManager() {
        // L1: 本地缓存（Caffeine，10 秒过期，最多 1000 条）
        CaffeineCacheManager localCacheManager = new CaffeineCacheManager();
        localCacheManager.setCaffeine(Caffeine.newBuilder()
            .maximumSize(1000)
            .expireAfterWrite(Duration.ofSeconds(10)));
        
        // L2: Redis 缓存（10 分钟过期）
        RedisCacheConfiguration redisConfig = RedisCacheConfiguration.defaultCacheConfig()
            .entryTtl(Duration.ofMinutes(10));
        RedisCacheManager redisCacheManager = RedisCacheManager.builder(connectionFactory)
            .cacheDefaults(redisConfig)
            .build();
        
        // 组合：先查 L1，未命中查 L2，再未命中查数据库
        return new CompositeCacheManager(localCacheManager, redisCacheManager);
    }
}
```

## 🔑 自定义 KeyGenerator

```java
// 默认 KeyGenerator（key + #参数名）
// 可自定义复杂 key 逻辑

@Bean
public KeyGenerator customKeyGenerator() {
    return new KeyGenerator() {
        @Override
        public Object generate(Object target, Method method, Object... params) {
            StringBuilder sb = new StringBuilder();
            sb.append(target.getClass().getSimpleName()).append(":");
            sb.append(method.getName()).append(":");
            for (Object param : params) {
                sb.append(param.toString()).append(":");
            }
            return sb.toString();
        }
    };
}

// 使用
@Cacheable(value = "users", keyGenerator = "customKeyGenerator")
public List<User> getUsersByRole(String role, int page) { ... }
```

## ⚠️ 缓存三大问题处理

### 缓存穿透（不存在的 key）

```java
// 方案 1：缓存空值（NULL）
@Cacheable(value = "users", key = "#id", unless = "#result == null")
public User getUser(Long id) {
    return userMapper.findById(id);  // null 也缓存
}

// 方案 2：布隆过滤器（推荐）
@Cacheable(value = "users", key = "#id", condition = "bloomFilter.contains(#id)")
public User getUser(Long id) {
    if (!bloomFilter.contains(id)) {
        return null;
    }
    return userMapper.findById(id);
}
```

### 缓存击穿（热点 key 过期）

```java
// sync = true：同一时刻只有一个线程查询数据库
@Cacheable(value = "hot-product", key = "#id", sync = true)
public Product getHotProduct(Long id) {
    return productMapper.findById(id);
}
```

### 缓存雪崩（大量 key 同时过期）

```java
// 在配置中加随机 TTL 偏移
RedisCacheConfiguration defaultConfig = RedisCacheConfiguration.defaultCacheConfig()
    .entryTtl(Duration.ofMinutes(10).plusSeconds(ThreadLocalRandom.current().nextLong(60)));
// 实际 TTL：10 分钟 ± 0~60 秒，避免同时过期
```

## 🛠️ 实战：用户服务完整缓存

```java
@Service
public class UserService {
    
    @Autowired
    private UserMapper userMapper;
    
    @Cacheable(value = "user", key = "#id", sync = true)
    public User getUser(Long id) {
        log.info("Querying database for user: {}", id);
        return userMapper.findById(id);
    }
    
    @CachePut(value = "user", key = "#user.id")
    public User updateUser(User user) {
        userMapper.update(user);
        return user;
    }
    
    @CacheEvict(value = "user", key = "#id")
    public void deleteUser(Long id) {
        userMapper.delete(id);
    }
    
    @Cacheable(value = "user-list", key = "#page + ':' + #size")
    public Page<User> listUsers(int page, int size) {
        log.info("Querying database for users: page={}, size={}", page, size);
        return userMapper.findPage(page, size);
    }
    
    @CacheEvict(value = "user-list", allEntries = true)
    public void clearUserListCache() {
        // 清空所有用户列表缓存
    }
}
```

## 🎯 总结

**Spring Cache 核心要点**：
- ✅ 注解式缓存：@Cacheable / @CachePut / @CacheEvict
- ✅ Redis 作为分布式缓存实现
- ✅ 支持多级缓存（Caffeine + Redis）
- ✅ sync = true 防缓存击穿
- ✅ unless 缓存空值防穿透
- ⚠️ TTL 加随机偏移防雪崩

**下一步：** [🔒 分布式锁](/06-practice/distributed-lock) — 企业实战第 1 课
