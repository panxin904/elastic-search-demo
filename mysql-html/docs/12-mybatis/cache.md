---
title: MyBatis 缓存机制
---

# ⚙️ MyBatis 缓存机制

> MyBatis 提供两级缓存，正确使用可以**减少 60% 以上**的数据库查询。但用错会有脏读问题。

## 🎯 两级缓存架构

```
┌──────────────────────────────────────────┐
│             Application                   │
│                                          │
│  ┌────────────────────────────────┐      │
│  │   Session 1 (一级缓存)          │      │  ← 默认开启
│  └────────────────────────────────┘      │
│  ┌────────────────────────────────┐      │
│  │   Session 2 (一级缓存)          │      │
│  └────────────────────────────────┘      │
│                                          │
│  ┌─────────────────────────────────────┐ │
│  │  Mapper 级别二级缓存                │ │  ← 需要开启
│  │  (跨 Session 共享)                │ │
│  └─────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐  │
│  │        MySQL                        │  │  ← 一二级缓存都没命中
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
```

## 📌 一级缓存（默认开启）

### 特性

| 特性 | 说明 |
|---|---|
| 默认 | 开启 |
| 范围 | SqlSession 级别（同一会话内） |
| 实现 | PerpetualCache（HashMap） |
| 生命周期 | SqlSession 关闭时清空 |
| 失效 | 任何 update/insert/delete 操作 |

### 示例

```java
public void demoLevel1Cache() {
    // 1. 同一 SqlSession 内，第二次查询命中一级缓存
    try (SqlSession session = sqlSessionFactory.openSession()) {
        UserMapper mapper = session.getMapper(UserMapper.class);
        
        // 第一次查询：查数据库
        User u1 = mapper.selectById(1);
        System.out.println("第一次查询: " + u1);
        
        // 第二次查询：命中缓存
        User u2 = mapper.selectById(1);
        System.out.println("第二次查询: " + u2);
        
        System.out.println(u1 == u2);  // true（同一个对象）
    }
    
    // 不同 SqlSession：缓存隔离
    try (SqlSession session2 = sqlSessionFactory.openSession()) {
        UserMapper mapper2 = session2.getMapper(UserMapper.class);
        User u3 = mapper2.selectById(1);  // 再次查数据库（不同 Session）
    }
}
```

### 一级缓存失效场景

```java
SqlSession session = sqlSessionFactory.openSession();
UserMapper mapper = session.getMapper(UserMapper.class);

mapper.selectById(1);  // 查 DB

// 任何写入操作都会清空一级缓存
mapper.update(null, Wrappers.lambdaUpdate(...));
// 在一级缓存执行 update 时，会清空该 Session 的所有缓存

mapper.selectById(1);  // 又查 DB
```

**注意：** 一级缓存的是**整个 SqlSession** 的，不是单个 Mapper。建议：

```java
// ✅ 短事务原则（推荐）
@Transactional
public void businessMethod() {
    UserService userService;
    userService.findById(1);
    userService.update(...);
    userService.findById(1);  // 命中一级缓存
}

// 或每次操作都用新 Session（@Transactional 会复用）
```

## 📌 二级缓存

### 特性

| 特性 | 说明 |
|---|---|
| 默认 | 关闭 |
| 范围 | Mapper 级别（跨 Session 共享） |
| 实现 | PerpetualCache / LRU / FIFO |
| 配置 | `<cache>` 或 `@CacheNamespace` |
| 失效 | 配置的 flushInterval / 大小上限 |

### 开启二级缓存

**方式 1：XML 配置**

```xml
<!-- UserMapper.xml -->
<mapper namespace="com.example.mapper.UserMapper">
    
    <!-- 开启二级缓存 -->
    <cache
        size="512"
        flushInterval="60000"
        readOnly="true"
        eviction="LRU"
    />
    
    <!-- 映射 -->
    <select id="selectById" resultType="User">
        SELECT * FROM users WHERE id = #{id}
    </select>
    
</mapper>
```

**方式 2：注解配置（MyBatis 3.4+）**

```java
@CacheNamespace(
    size = 512,                  // 最多 512 个对象
    flushInterval = 60000,       // 60 秒清空
    readOnly = true,             // 只读（性能更好）
    eviction = LruCache.class    // LRU 淘汰算法
)
public interface UserMapper extends BaseMapper<User> {
    // ...
}
```

**方式 3：在 properties 中配置全局**

```yaml
mybatis:
  configuration:
    cache-enabled: true  # 全局开启
```

### 二级缓存生效场景

```java
// ✅ 跨 Session 共享
try (SqlSession s1 = sqlSessionFactory.openSession()) {
    User u1 = s1.getMapper(UserMapper.class).selectById(1);  // 查 DB
}

try (SqlSession s2 = sqlSessionFactory.openSession()) {
    User u2 = s2.getMapper(UserMapper.class).selectById(1);  // 命中二级缓存！
}

// ✅ 在不同 namespace 间隔离
// ✅ 同一 namespace 下所有 select 自动使用
```

### 配置详解

```xml
<cache
    size="512"              <!-- 最多缓存 512 个对象 -->
    flushInterval="60000"   <!-- 60 秒自动清空 -->
    readOnly="true"         <!-- 只读（推荐，性能 +20%） -->
    eviction="LRU"          <!-- LRU 淘汰（最近最少使用） -->
    
    <!-- 也可以选：FIFO（先进先出）、SOFT（软引用）、WEAK（弱引用） -->
    
    type="org.mybatis.caches.redis.RedisCache"  <!-- 使用 Redis 做缓存（分布式） -->
/>
```

## 🔌 第三方缓存实现

### 用 Redis 做二级缓存（分布式推荐）

```xml
<dependency>
    <groupId>org.mybatis.caches</groupId>
    <artifactId>mybatis-redis</artifactId>
    <version>1.3.0</version>
</dependency>
```

```xml
<!-- UserMapper.xml -->
<cache type="org.mybatis.caches.redis.RedisCache"
       size="10000"
       flushInterval="60000" />
```

```properties
# redis.properties
host=localhost
port=6379
password=
database=0
```

**优势：**
- ✅ 跨服务器共享
- ✅ 持久化
- ✅ 自动清理（TTL）

## ⚠️ 二级缓存的脏读问题

### 经典问题

```java
// T1: 读
User u1 = userMapper.selectById(1);  // 命中缓存返回旧值
// 但数据库已被 T2 改了！

// T2: 写（另一个 Session）
userMapper2.updateById(user);  // 直接写 DB（不更新二级缓存！）

// T1: 再读
User u2 = userMapper.selectById(1);  // 还是旧值！❌ 脏读
```

### 解决：flushCache

```java
// 方式 1：执行 update/insert/delete 会清空二级缓存（默认行为）
userMapper.updateById(user);  // 会清空 UserMapper 的所有缓存

// 方式 2：手动清空
userMapper.flushCache();  // 强制清空当前 Mapper 的二级缓存

// 方式 3：用 Redis 等外部缓存，更可靠
```

## 🎯 MyBatis-Plus 的缓存

### 一级缓存

同 MyBatis，**SqlSession 级别**（线程隔离）。

### 二级缓存

**开启方式：**

```yaml
mybatis-plus:
  configuration:
    cache-enabled: true
```

**但 MP 不推荐用二级缓存**，因为：

1. ✅ MP 推荐用 **Redis / Caffeine 等进程外缓存**（如 Spring Cache）
2. ✅ 事务写操作频繁，二级缓存失效多
3. ✅ 分布式场景下，进程内缓存意义不大

**MP 推荐架构：**

```
┌──────────┐    ┌─────────┐    ┌─────────┐
│   App    │ →  │  Redis  │ →  │  MySQL  │
└──────────┘    └─────────┘    └─────────┘
   二级缓存       缓存层        数据库
  (本地)        (跨实例)
```

## 🎯 实战建议

### 1. 关闭二级缓存的场景

```java
// ✅ 推荐：以下场景不要用二级缓存
// - 实时性要求高（金融、库存）
// - 写操作频繁
// - 分布式部署（用 Redis 替代）
// - 数据量大（缓存占内存）
```

### 2. 多级缓存架构

```java
// ✅ 推荐：Caffeine（本地 L1）+ Redis（分布式 L2）
@Service
public class UserService {
    
    @Autowired
    private UserMapper userMapper;
    
    @Autowired
    private CacheManager cacheManager;  // Spring Cache
    
    @Cacheable(value = "user", key = "#id", 
               unless = "#result == null")
    public User findById(Long id) {
        return userMapper.selectById(id);
    }
    
    @CacheEvict(value = "user", key = "#user.id")
    public User update(User user) {
        userMapper.updateById(user);
        return user;
    }
}
```

## ⚙️ 自定义缓存实现

```java
// 实现 Cache 接口
public class RedisMybatisCache implements Cache {
    
    private final String id;
    private final RedisTemplate<String, Object> redis;
    private static final String PREFIX = "mybatis:cache:";
    
    public RedisMybatisCache(String id) {
        this.id = id;
        this.redis = SpringContextHolder.getBean(RedisTemplate.class);
    }
    
    @Override
    public String getId() {
        return id;
    }
    
    @Override
    public void putObject(Object key, Object value) {
        redis.opsForValue().set(PREFIX + id + ":" + key, value);
    }
    
    @Override
    public Object getObject(Object key) {
        return redis.opsForValue().get(PREFIX + id + ":" + key);
    }
    
    @Override
    public Object removeObject(Object key) {
        return redis.delete(PREFIX + id + ":" + key);
    }
    
    @Override
    public void clear() {
        // 删除该 namespace 的所有 key
        Set<String> keys = redis.keys(PREFIX + id + ":*");
        if (!keys.isEmpty()) {
            redis.delete(keys);
        }
    }
    
    @Override
    public int getSize() {
        return redis.keys(PREFIX + id + ":*").size();
    }
}
```

**注册：**

```java
public class CacheFactory implements CacheFactory {
    @Override
    public Cache buildCache(String id) {
        return new RedisMybatisCache(id);
    }
}

<!-- UserMapper.xml -->
<cache type="com.example.cache.RedisMybatisCacheFactory"/>
```

## 🎯 总结

**两级缓存对比：**

| 维度 | 一级缓存 | 二级缓存 |
|---|---|---|
| 默认 | 开启 | 关闭 |
| 范围 | SqlSession | Mapper（跨 Session） |
| 实现 | HashMap | 可插拔（LRU / Redis） |
| 写操作失效 | ✅ | ✅ |
| 分布式 | ❌ | 需外部存储（Redis） |
| 性能 | 最快 | 快 |

**最佳实践：**
- ✅ 一级缓存保留（性能好）
- ❌ 二级缓存默认关闭
- ✅ 分布式用 Spring Cache + Redis
- ✅ 实时性要求高的场景不用缓存
- ✅ 用 `@CacheEvict` 管理缓存失效

**MyBatis-Plus 推荐：**
- ❌ 不内置推荐使用二级缓存
- ✅ 集成 Spring Cache + Redis
- ✅ 用 `@Cacheable` / `@CacheEvict` 注解管理

**下一步：** [🎨 MyBatis-Plus 代码生成器](/12-mybatis/generator) — 一键生成全套 CRUD 代码