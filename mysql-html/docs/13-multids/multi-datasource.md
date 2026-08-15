---
title: 多数据源配置
---

# 🔀 多数据源配置

> 真实的 Java 项目中，**多数据源**是常见需求：业务库 / 报表库分离、读写分离前的过渡、跨库查询等。本章从基础到高级，详解多数据源的正确姿势。

## 🎯 多数据源的应用场景

```
┌──────────────────────────────────────────┐
│         Spring Boot Application             │
│                                          │
│  ┌──────────┐  ┌──────────┐  ┌────────┐  │
│  │ 业务库    │  │ 报表库    │  │日志库 │   │
│  │ (主库)    │  │ (OLAP)   │  │(ES/MySQL) │
│  │ user_db  │  │ report_db│  │log_db  │   │
│  └──────────┘  └──────────┘  └────────┘  │
└──────────────────────────────────────────┘
```

**典型场景：**
- ✅ 业务库 + 报表库分离（不影响业务）
- ✅ 多租户系统（每租户独立库）
- ✅ 异构数据库（MySQL + PostgreSQL + MongoDB）
- ✅ 读写分离前的过渡（主从两个数据源）
- ✅ 微服务中（每个服务独立库）

## 🚀 方式 1：application.yml 配置多数据源

### application.yml

```yaml
spring:
  datasource:
    # 数据源 1：主业务库
    master:
      url: jdbc:mysql://master:3306/user_db?useSSL=false&serverTimezone=Asia/Shanghai
      username: root
      password: xxx
      driver-class-name: com.mysql.cj.jdbc.Driver
      hikari:
        maximum-pool-size: 20
        pool-name: MasterHikariPool
    
    # 数据源 2：报表库
    report:
      url: jdbc:mysql://report:3306/report_db
      username: readonly
      password: xxx
      driver-class-name: com.mysql.cj.jdbc.Driver
      hikari:
        maximum-pool-size: 10
        pool-name: ReportHikariPool
    
    # 数据源 3：日志库（可异构）
    log:
      url: jdbc:mysql://log:3306/log_db
      username: log_user
      password: xxx
      driver-class-name: com.mysql.cj.jdbc.Driver
      hikari:
        maximum-pool-size: 5
        pool-name: LogHikariPool
```

## 🔧 方式 2：Java Config 配置多数据源

### 1. 主数据源配置

```java
@Configuration
@MapperScan(
    basePackages = "com.example.mapper.master",  // 主库 Mapper 路径
    sqlSessionFactoryRef = "masterSqlSessionFactory"
)
public class MasterDataSourceConfig {
    
    @Primary  // ⚠️ 关键：标记为默认数据源
    @Bean(name = "masterDataSource")
    @ConfigurationProperties("spring.datasource.master")
    public DataSource masterDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Primary
    @Bean(name = "masterSqlSessionFactory")
    public SqlSessionFactory masterSqlSessionFactory(
        @Qualifier("masterDataSource") DataSource dataSource
    ) throws Exception {
        SqlSessionFactoryBean factory = new SqlSessionFactoryBean();
        factory.setDataSource(dataSource);
        factory.setMapperLocations(
            new PathMatchingResourcePatternResolver()
                .getResources("classpath:mapper/master/*.xml")
        );
        // 配置驼峰转换
        factory.getObject().getConfiguration()
            .setMapUnderscoreToCamelCase(true);
        return factory.getObject();
    }
    
    @Primary
    @Bean(name = "masterTransactionManager")
    public DataSourceTransactionManager masterTransactionManager(
        @Qualifier("masterDataSource") DataSource dataSource
    ) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

### 2. 从数据源配置

```java
@Configuration
@MapperScan(
    basePackages = "com.example.mapper.report",
    sqlSessionFactoryRef = "reportSqlSessionFactory"
)
public class ReportDataSourceConfig {
    
    @Bean(name = "reportDataSource")
    @ConfigurationProperties("spring.datasource.report")
    public DataSource reportDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean(name = "reportSqlSessionFactory")
    public SqlSessionFactory reportSqlSessionFactory(
        @Qualifier("reportDataSource") DataSource dataSource
    ) throws Exception {
        SqlSessionFactoryBean factory = new SqlSessionFactoryBean();
        factory.setDataSource(dataSource);
        factory.setMapperLocations(
            new PathMatchingResourcePatternResolver()
                .getResources("classpath:mapper/report/*.xml")
        );
        return factory.getObject();
    }
    
    @Bean(name = "reportTransactionManager")
    public DataSourceTransactionManager reportTransactionManager(
        @Qualifier("reportDataSource") DataSource dataSource
    ) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

### 3. Mapper 目录结构

```
src/main/java/com/example/mapper/
├── master/                      # 主库的 Mapper
│   ├── UserMapper.java
│   └── OrderMapper.java
└── report/                      # 报表库的 Mapper
    ├── ReportSaleMapper.java
    └── ReportUserMapper.java

src/main/resources/mapper/
├── master/
│   ├── UserMapper.xml
│   └── OrderMapper.xml
└── report/
    ├── ReportSaleMapper.xml
    └── ReportUserMapper.xml
```

## 🎯 方式 3：MyBatis-Plus 多数据源

### 简化配置

```java
@DS("master")  // ⚠️ 注解指定数据源
@Repository
public interface UserMapper extends BaseMapper<User> {
    // 默认用 master
}
```

```java
@DS("report")
@Repository
public interface ReportSaleMapper extends BaseMapper<ReportSale> {
    // 用 report
}
```

### 方法级别切换

```java
@DS("report")
public List<ReportSale> getAllSales() {
    return reportSaleMapper.selectList(null);
}
```

### 完整 MyBatis-Plus 多数据源配置

```java
@Configuration
@MapperScan(
    basePackages = "com.example.mapper",
    sqlSessionFactoryRef = "sqlSessionFactory"
)
public class MultiDataSourceConfig {
    
    @Bean
    @Primary
    @ConfigurationProperties("spring.datasource.master")
    public DataSource masterDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean
    @ConfigurationProperties("spring.datasource.report")
    public DataSource reportDataSource() {
        return DataSourceBuilder.create().build();
    }
    
    @Bean
    @Primary
    public SqlSessionFactory sqlSessionFactory(
        DataSource dataSource  // 动态数据源（见下章）
    ) throws Exception {
        MybatisSqlSessionFactoryBean factory = new MybatisSqlSessionFactoryBean();
        factory.setDataSource(dataSource);
        return factory.getObject();
    }
}
```

## 🧪 事务管理（重要！）

### 跨数据源不能在一个事务里！

```java
// ❌ 错误：跨数据源用同一个事务
@Transactional("masterTransactionManager")  // 只能管理 master
public void wrong() {
    userMapper.insert(user);  // 走 master
    
    reportMapper.insert(report);  // 走 report（脱离事务！）
}
```

### 跨数据源用 ChainedTransactionManager（不推荐）

```java
// ⚠️ Spring 官方已不推荐 ChainedTransactionManager
// 因为不能保证原子性
```

### ✅ 跨数据源事务：分布式事务（Seata）

详见 [🔄 分布式事务](/13-multids/transaction) 章节。

### 单数据源内事务（正常情况）

```java
@Transactional("masterTransactionManager")
public void createUser(User user) {
    userMapper.insert(user);  // 在 master 事务里
    orderMapper.insert(order);  // 也在 master 事务里
}
```

## 🎯 实战：业务库 + 报表库分离

```java
@Service
public class UserService {
    
    @Autowired
    private UserMapper userMapper;  // 走 master
    
    @Autowired
    private ReportUserMapper reportUserMapper;  // 走 report
    
    // 业务方法
    public User findById(Long id) {
        return userMapper.selectById(id);
    }
    
    // 报表方法（直连报表库）
    public List<ReportUser> getReportData() {
        return reportUserMapper.selectList(null);
    }
}
```

```java
// Controller
@RestController
@RequestMapping("/user")
public class UserController {
    
    @Autowired private UserService userService;
    
    @GetMapping("/{id}")
    public User getById(@PathVariable Long id) {
        return userService.findById(id);  // 走 master
    }
    
    @GetMapping("/report")
    public List<ReportUser> report() {
        return userService.getReportData();  // 走 report
    }
}
```

## 🛠️ 常见问题

### 问题 1：循环依赖

```
报错：The dependencies of some of the beans in the application context form a cycle
```

**解决：** 用 `@Lazy` 延迟注入
```java
@Autowired
@Lazy
private DataSource dataSource;
```

### 问题 2：找不到 Mapper

```
报错：No qualifying bean of type 'UserMapper'
```

**解决：** 检查 `@MapperScan` 的 basePackages
```java
@MapperScan(basePackages = "com.example.mapper.master")
```

### 问题 3：MyBatis-Plus 找不到表

```
报错：Table 'xxx' doesn't exist
```

**原因：** 不同数据源指向不同库  
**解决：** 在 `@TableName` 指定 schema
```java
@TableName(value = "user_db.users")  // 完整：库名.表名
```

## 🎯 总结

**多数据源选型：**
- ✅ 简单场景：MyBatis-Plus `@DS` 注解（最简单）
- ✅ 复杂场景：Java Config 分离 Mapper
- ✅ 读写分离前：建议先上多数据源，再升级为动态数据源

**目录结构最佳实践：**
- 按数据源分包（master/、report/、log/）
- 事务管理器按数据源配置
- Mapper XML 按数据源分目录

**事务原则：**
- ✅ 单数据源内：一个 `@Transactional` 搞定
- ❌ 跨数据源：必须用分布式事务（Seata）
- ❌ 不要用 ChainedTransactionManager（已废弃）

**下一步：** [🔀 动态数据源](/13-multids/dynamic-datasource) — 运行时切换数据源（读写分离前置）