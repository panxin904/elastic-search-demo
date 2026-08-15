---
title: 动态数据源
---

# 🔀 动态数据源

> 动态数据源是**运行时切换数据库连接**的能力。读写分离、多租户、分库分表的基础。

## 🎯 为什么需要动态数据源？

```
场景：用户下单
1. 主库写入（master）
2. 同时更新库存（master）
3. 记录日志（master 或 log 库）
4. 发送消息（Kafka）

如果用静态多数据源：
- 每个方法都写 @DS("master")
- 业务代码与数据源耦合

用动态数据源：
- @Transactional("master") 自动选 master
- 运行时根据注解/方法名/上下文自动切换
```

## 🚀 方式 1：Spring AbstractRoutingDataSource

### 核心原理

```
┌──────────────────────────────────┐
│   业务代码（不知道用哪个库）       │
└─────────────┬────────────────────┘
              │
┌─────────────▼────────────────────┐
│  AbstractRoutingDataSource        │  ← Spring 抽象类
│  （根据 key 选择数据源）            │
└─────────────┬────────────────────┘
              │
   ┌──────────┼──────────┐
   ▼          ▼          ▼
┌──────┐  ┌──────┐  ┌──────┐
│master│  │slave1│  │slave2│
└──────┘  └──────┘  └──────┘
```

### 1. 自定义路由 key

```java
public class DataSourceContextHolder {
    private static final ThreadLocal<String> CURRENT = new ThreadLocal<>();
    
    public static void set(String key) { CURRENT.set(key); }
    public static String get() { return CURRENT.get(); }
    public static void clear() { CURRENT.remove(); }
}
```

### 2. 自定义 RoutingDataSource

```java
public class DynamicRoutingDataSource extends AbstractRoutingDataSource {
    
    @Override
    protected Object determineCurrentLookupKey() {
        return DataSourceContextHolder.get();
    }
}
```

### 3. 加载所有数据源 + 注册

```java
@Configuration
public class DynamicDataSourceConfig {
    
    @Bean
    public DataSource dynamicDataSource(
        @Qualifier("masterDataSource") DataSource master,
        @Qualifier("slave1DataSource") DataSource slave1,
        @Qualifier("slave2DataSource") DataSource slave2
    ) {
        Map<Object, Object> targetDataSources = new HashMap<>();
        targetDataSources.put("master", master);
        targetDataSources.put("slave1", slave1);
        targetDataSources.put("slave2", slave2);
        
        DynamicRoutingDataSource routing = new DynamicRoutingDataSource();
        routing.setTargetDataSources(targetDataSources);
        routing.setDefaultTargetDataSource(master);  // 默认走 master
        return routing;
    }
}
```

### 4. 工具方法：手动切换

```java
public class DataSourceHelper {
    public static void master() { DataSourceContextHolder.set("master"); }
    public static void slave() { DataSourceContextHolder.set("slave1"); }
    public static void clear() { DataSourceContextHolder.clear(); }
}
```

### 5. 业务代码使用

```java
@Service
public class UserService {
    
    public User findById(Long id) {
        // 手动切换
        DataSourceHelper.slave();  // 走从库
        try {
            return userMapper.selectById(id);
        } finally {
            DataSourceContextHolder.clear();
        }
    }
}
```

### 6. AOP 切面：注解切换（推荐）

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface UseDataSource {
    String value();
}

// 切面
@Aspect
@Component
public class DataSourceAspect {
    
    @Before("@annotation(useDataSource)")
    public void switchDataSource(UseDataSource useDataSource) {
        DataSourceContextHolder.set(useDataSource.value());
    }
    
    @After("@annotation(useDataSource)")
    public void restoreDataSource() {
        DataSourceContextHolder.clear();
    }
}

// 使用
@Service
public class UserService {
    
    @UseDataSource("slave1")
    public List<User> findActiveUsers() {
        return userMapper.selectList(null);
    }
}
```

## 🚀 方式 2：MyBatis-Plus 动态数据源

### 引入 dynamic-datasource-spring-boot-starter

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>dynamic-datasource-spring-boot-starter</artifactId>
    <version>3.6.1</version>
</dependency>
```

### 配置

```yaml
spring:
  datasource:
    dynamic:
      primary: master
      strict: true  # 严格匹配（未指定数据源抛异常）
      datasource:
        master:
          url: jdbc:mysql://master:3306/mydb
          username: root
          password: xxx
          driver-class-name: com.mysql.cj.jdbc.Driver
          hikari:
            maximum-pool-size: 20
        
        slave_1:
          url: jdbc:mysql://slave1:3306/mydb
          username: readonly
          password: xxx
          hikari:
            maximum-pool-size: 30
            read-only: true
        
        slave_2:
          url: jdbc:mysql://slave2:3306/mydb
          username: readonly
          password: xxx
          hikari:
            maximum-pool-size: 30
            read-only: true
```

### 使用

```java
@DS("master")  // 指定数据源
@Service
public class UserService {
    
    // 默认 master
    public boolean createUser(User user) {
        return save(user);
    }
    
    @DS("slave_1")  // 读从库 1
    public List<User> listActive() {
        return list();
    }
    
    @DS("slave_2")  // 读从库 2
    public List<User> listAllFromSlave2() {
        return list();
    }
}
```

### 事务（自动选 master）

```java
@DS("master")  // 写库
@Transactional
public void createOrder(Order order) {
    // 写主库
    orderMapper.insert(order);
    // 写从库（脱离事务，会立即提交！）
    // ⚠️ 不推荐跨数据源事务
}
```

### 动态切换（运行时）

```java
// 方式 1：方法注解（编译时确定）
@DS("slave_1")
public List<X> query() { ... }

// 方式 2：编程式切换（运行时确定）
public List<X> query(String tenant) {
    DynamicDataSourceContextHolder.push(tenant);  // 切换
    try {
        return xMapper.selectList(null);
    } finally {
        DynamicDataSourceContextHolder.poll();  // 恢复
    }
}
```

### 集成 Spring 事务

```java
@DS("master")
@Transactional(propagation = Propagation.REQUIRED)
public void createOrder(Order order) {
    // 事务内用 master
    orderMapper.insert(order);
    itemMapper.insert(item);
}
```

## 🎯 方式 3：基于方法名的自动路由

```java
// 自定义路由策略
public class NameBasedDataSourceRouter {
    public String determineKey() {
        // 获取当前方法名
        String methodName = MethodStack.getCurrentMethodName();
        
        // 读方法走从库
        if (methodName.startsWith("find") || 
            methodName.startsWith("get") || 
            methodName.startsWith("list") ||
            methodName.startsWith("search")) {
            return "slave";
        }
        
        // 写方法走主库
        return "master";
    }
}
```

## 📊 多数据源 + 事务

### 单数据源事务

```java
@DS("master")
@Transactional  // 走 master 事务
public void createOrder() {
    // orderMapper 和 itemMapper 都用 master（在事务里）
}
```

### 跨数据源（需要 Seata）

详见 [🔄 分布式事务](/13-multids/transaction) 章节。

## 🛠️ 实战：多租户 + 读写分离

```java
@DS("#tenantId")  // SpEL 表达式动态路由
@Service
public class OrderService {
    
    public List<Order> getOrders(Long tenantId) {
        // 根据 tenantId 路由到对应租户的库
        return orderMapper.selectList(null);
    }
}
```

```yaml
# 配置（dynamic-datasource）
spring:
  datasource:
    dynamic:
      datasource:
        tenant_001:
          url: jdbc:mysql://host:3306/tenant_001
        tenant_002:
          url: jdbc:mysql://host:3306/tenant_002
        # 自动根据 tenant_001、tenant_002 路由
```

## 🎯 总结

**动态数据源选型：**
- ✅ 简单场景：MyBatis-Plus dynamic-datasource（推荐）
- ✅ 复杂场景：AbstractRoutingDataSource（更灵活）
- ✅ 读写分离前置：先用动态数据源，再升级为读写分离

**使用原则：**
- ✅ 写操作固定 master（简单明确）
- ✅ 读操作可动态选 slave（灵活）
- ✅ 事务内只用 master（避免跨数据源事务）
- ✅ 动态切换要在 finally 里清理 ThreadLocal

**MyBatis-Plus dynamic-datasource 优势：**
- ✅ 开箱即用
- ✅ 支持 @DS 注解 + 编程式
- ✅ 集成 Spring 事务
- ✅ 集成 MyBatis-Plus 全功能
- ✅ 支持 Seata 分布式事务

**下一步：** [🔀 读写分离](/13-multids/read-write-split) — 基于动态数据源实现读写分离