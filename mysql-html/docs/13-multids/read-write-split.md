---
title: 读写分离
---

# 🔀 读写分离

> 读写分离是**扩展读能力**的标准方案。**80% 的互联网应用**都采用主从读写分离。

## 🎯 为什么需要读写分离？

```
单库架构：
- 所有读写都打主库
- 主库 CPU / IO / 锁 压力大
- 读延迟高
- 写并发也受影响

读写分离后：
┌──────────┐  写  ┌──────────┐
│  App     │ ───→ │  Master  │
│          │      └──────────┘
│          │           │ 复制
│          │      ┌──────────┐
│          │ 读  │  Slave 1 │  ← 承担读流量
│          │ ───→ ├──────────┤
│          │      │  Slave 2 │  ← 承担读流量
└──────────┘      └──────────┘

收益：
- 读能力线性扩展（1 主 3 从 = 3 倍读）
- 主库只处理写（压力降低 80%+）
- 读延迟降低
```

## 📊 4 种实现方式

| 方式 | 复杂度 | 性能 | 适用场景 |
|---|---|---|---|
| ① 应用层手动切换 | ⭐ | 高 | 简单读写分离 |
| ② AbstractRoutingDataSource | ⭐⭐ | 高 | 通用方案 |
| ③ MyBatis-Plus dynamic-datasource | ⭐ | 高 | **推荐** |
| ④ 数据库中间件（ProxySQL/ShardingSphere） | ⭐⭐⭐ | 最高 | 性能 + 高可用 |

## 🚀 方式 1：应用层手动切换

```java
@Service
public class UserService {
    
    @Autowired
    private UserMapper userMapper;
    
    // 写操作：手动指定 master
    @Transactional
    public boolean createUser(User user) {
        DataSourceContextHolder.set("master");
        try {
            return userMapper.insert(user) > 0;
        } finally {
            DataSourceContextHolder.clear();
        }
    }
    
    // 读操作：手动指定 slave
    public User findById(Long id) {
        DataSourceContextHolder.set("slave");
        try {
            return userMapper.selectById(id);
        } finally {
            DataSourceContextHolder.clear();
        }
    }
}
```

**缺点：** 代码侵入性强

## 🚀 方式 2：AbstractRoutingDataSource

### 1. 配置主从数据源

```yaml
spring:
  datasource:
    master:
      url: jdbc:mysql://master:3306/mydb
      username: root
      password: xxx
      hikari:
        maximum-pool-size: 10
    slave:
      url: jdbc:mysql://slave:3306/mydb
      username: readonly
      password: xxx
      hikari:
        maximum-pool-size: 30
        read-only: true
```

### 2. 动态路由数据源

```java
public class DynamicRoutingDataSource extends AbstractRoutingDataSource {
    @Override
    protected Object determineCurrentLookupKey() {
        return DataSourceContextHolder.get();
    }
}
```

### 3. 注册 Bean

```java
@Configuration
public class DataSourceConfig {
    
    @Bean
    @ConfigurationProperties("spring.datasource.master")
    public DataSource masterDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean
    @ConfigurationProperties("spring.datasource.slave")
    public DataSource slaveDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean
    @Primary
    public DataSource routingDataSource(
        @Qualifier("masterDataSource") DataSource master,
        @Qualifier("slaveDataSource") DataSource slave
    ) {
        Map<Object, Object> map = new HashMap<>();
        map.put("master", master);
        map.put("slave", slave);
        
        DynamicRoutingDataSource routing = new DynamicRoutingDataSource();
        routing.setTargetDataSources(map);
        routing.setDefaultTargetDataSource(master);
        return routing;
    }
}
```

### 4. AOP 切面（按方法名或注解路由）

```java
@Aspect
@Component
public class ReadWriteSplitAspect {
    
    // 读方法前缀（自动走从库）
    private static final Set<String> READ_PREFIXES = Set.of(
        "find", "get", "list", "search", "query", "count", "select", "exists"
    );
    
    @Before("execution(* com.example.service..*.*(..))")
    public void before(JoinPoint joinPoint) {
        MethodSignature sig = (MethodSignature) joinPoint.getSignature();
        String name = sig.getName();
        
        // 读方法走从库
        if (READ_PREFIXES.stream().anyMatch(name::startsWith)) {
            DataSourceContextHolder.set("slave");
        } else {
            DataSourceContextHolder.set("master");
        }
    }
    
    @After("execution(* com.example.service..*.*(..))")
    public void after() {
        DataSourceContextHolder.clear();
    }
}
```

## 🚀 方式 3：MyBatis-Plus dynamic-datasource（推荐）

### 配置

```yaml
spring:
  datasource:
    dynamic:
      primary: master
      strict: false  # 默认数据源为 master（即使没指定 @DS）
      datasource:
        master:
          url: jdbc:mysql://master:3306/mydb
          username: root
          password: xxx
          hikari:
            maximum-pool-size: 10
        slave_1:
          url: jdbc:mysql://slave1:3306/mydb
          username: readonly
          password: xxx
          hikari:
            maximum-pool-size: 30
            read-only: true
```

### 注解使用

```java
@Service
public class UserService extends ServiceImpl<UserMapper, User> {
    
    // 写操作：默认走 master（primary）
    public boolean createUser(User user) {
        return save(user);
    }
    
    // 读操作：走 slave_1
    @DS("slave_1")
    public List<User> listActive() {
        return list();
    }
    
    // 关键业务（必须读最新）：走 master
    @DS("master")
    public User findByIdForceMaster(Long id) {
        return getById(id);
    }
}
```

### 编程式切换

```java
@Service
public class OrderService {
    
    public Order getOrderFresh(Long orderId) {
        // 强制读主库（保证读到刚写入的数据）
        DynamicDataSourceContextHolder.push("master");
        try {
            return orderMapper.selectById(orderId);
        } finally {
            DynamicDataSourceContextHolder.poll();
        }
    }
    
    public List<Order> listOrders(Long userId) {
        // 普通查询走从库
        DynamicDataSourceContextHolder.push("slave_1");
        try {
            return orderMapper.selectList(
                Wrappers.<Order>lambdaQuery().eq(Order::getUserId, userId)
            );
        } finally {
            DynamicDataSourceContextHolder.poll();
        }
    }
}
```

## 🚀 方式 4：数据库中间件（性能最优）

### ProxySQL

```
┌──────────┐       ┌──────────┐       ┌──────────┐
│   App    │ ────→ │ ProxySQL │ ────→ │  MySQL   │
│          │  3306 │  8066    │  3306 │  Servers │
└──────────┘       └──────────┘       └──────────┘
```

详见 [🚦 ProxySQL 中间件](/07-ha/proxysql) 章节。

### ShardingSphere-JDBC

详见 [🌊 ShardingSphere 实战](/10-sharding/shardingsphere) 章节。

## 📊 实战：完整的读写分离方案

### 关键原则

```
✅ 写操作：固定 master
✅ 读操作：默认 slave，特殊场景强制 master
✅ 事务内：只读 master（避免跨数据源）
✅ 延迟敏感：写后立即读用 master
✅ 报表查询：专门从库
```

### 实战代码

```java
@Service
public class OrderService extends ServiceImpl<OrderMapper, Order> {
    
    // 1. 创建订单（写 master）
    public boolean createOrder(Order order) {
        // save 走 master（默认数据源）
        return save(order);
    }
    
    // 2. 查订单（一般场景走从库）
    @DS("slave_1")
    public Order findById(Long orderId) {
        return getById(orderId);
    }
    
    // 3. 写后立即读（必须主库，避免延迟）
    public Order getOrderImmediately(Long orderId) {
        // ⚠️ 关键：写后立即读必须强制主库
        DynamicDataSourceContextHolder.push("master");
        try {
            return getById(orderId);
        } finally {
            DynamicDataSourceContextHolder.poll();
        }
    }
    
    // 4. 列表查询（从库）
    @DS("slave_1")
    public List<Order> listByUser(Long userId) {
        return list(Wrappers.<Order>lambdaQuery()
            .eq(Order::getUserId, userId)
            .orderByDesc(Order::getCreatedAt));
    }
}
```

### 强制主读 API

```java
@DS("master")
public <T> T forceReadMaster(Supplier<T> action) {
    return action.get();
}

// 使用
Order order = forceReadMaster(() -> orderService.findById(id));
```

## 🔍 主从延迟的处理

### 延迟检测

```sql
-- 从库执行
SHOW SLAVE STATUS\G
-- 看 Seconds_Behind_Master 字段
```

### 应用层处理

```java
// 关键业务（写后立即读）→ 强制主库
@DS("master")
public Order findByIdAfterCreate(Long orderId) {
    return orderMapper.selectById(orderId);
}

// 一般业务（可容忍秒级延迟）→ 从库
@DS("slave")
public List<Order> listByUser(Long userId) {
    return orderMapper.selectList(...);
}
```

## 🎯 总结

**读写分离选型建议：**
- ✅ **小型项目**：应用层手动（@DS 注解）
- ✅ **中大型项目**：MyBatis-Plus dynamic-datasource（最推荐）
- ✅ **超大型 / 高性能**：中间件方案（ProxySQL）

**关键原则：**
- ✅ 写操作固定 master
- ✅ 读操作默认 slave，特殊场景 master
- ✅ 事务内只用 master
- ✅ 写后立即读用 master
- ✅ 监控主从延迟

**MyBatis-Plus dynamic-datasource 优势：**
- ✅ 开箱即用
- ✅ @DS 注解 + 编程式切换
- ✅ 集成事务
- ✅ 集成多种连接池（HikariCP / Druid / Tomcat JDBC）
- ✅ 集成 Seata 分布式事务
- ✅ 集成 MyBatis-Plus 全功能

**下一步：** [🌊 ShardingSphere-JDBC 实战](/13-multids/sharding-jdbc) — 分库分表中间件