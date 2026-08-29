---
title: 数据访问
date: 2026-08-15  # date-auto-injected
---

# 💾 Spring Boot 数据访问

> Spring Boot 集成 MyBatis-Plus / Spring Data JPA 都极简。本章聚焦**企业最常用**的 MyBatis-Plus 集成。

## 🚀 MyBatis-Plus 集成（推荐）

### 添加依赖

```xml
<dependency>
    <groupId>com.baomidou</groupId>
    <artifactId>mybatis-plus-boot-starter</artifactId>
    <version>3.5.5</version>
</dependency>

<dependency>
    <groupId>com.mysql</groupId>
    <artifactId>mysql-connector-j</artifactId>
</dependency>
```

### application.yml

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: xxx
    driver-class-name: com.mysql.cj.jdbc.Driver
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5

mybatis-plus:
  mapper-locations: classpath:mapper/**/*.xml
  type-aliases-package: com.example.entity
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl
  global-config:
    db-config:
      id-type: assign_id
      logic-delete-field: deleted
      logic-delete-value: 1
      logic-not-delete-value: 0
  plugins:
    - com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor
```

### 启动类

```java
@SpringBootApplication
@MapperScan("com.example.mapper")
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
```

### Entity

```java
@Data
@TableName("users")
public class User {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    
    private String username;
    private String email;
    private Integer age;
    private Integer status;
    
    @TableLogic
    private Integer deleted;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
```

### Mapper

```java
public interface UserMapper extends BaseMapper<User> {
    // 自动获得 30+ 通用 CRUD 方法
}
```

### Service

```java
@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User>
    implements UserService {
    // 自动拥有所有 CRUD 方法
}
```

## 📝 复杂查询（XML 方式）

```xml
<!-- UserMapper.xml -->
<select id="searchByName" resultType="User">
    SELECT * FROM users
    <where>
        <if test="keyword != null">AND username LIKE CONCAT('%', #{keyword}, '%')</if>
        <if test="status != null">AND status = #{status}</if>
    </where>
    ORDER BY created_at DESC
</select>
```

```java
public interface UserMapper extends BaseMapper<User> {
    List<User> searchByName(@Param("keyword") String keyword,
                           @Param("status") Integer status);
}
```

## 🔄 多表 JOIN

```java
public interface OrderMapper extends BaseMapper<Order> {
    // 用 @Select 注解
    @Select("""
        SELECT o.*, u.username
        FROM orders o
        JOIN users u ON o.user_id = u.id
        WHERE o.user_id = #{userId}
        ORDER BY o.created_at DESC
    """)
    List<OrderWithUser> getOrdersWithUser(@Param("userId") Long userId);
}
```

## 📊 分页查询

```java
@GetMapping("/page")
public Result<Page<User>> page(
    @RequestParam(defaultValue = "1") int pageNum,
    @RequestParam(defaultValue = "10") int pageSize
) {
    Page<User> page = new Page<>(pageNum, pageSize);
    Page<User> result = userMapper.selectPage(page, null);
    return Result.success(result);
}
```

## 🔗 Spring Data JPA（备选方案）

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
</dependency>
```

```java
@Entity
@Table(name = "users")
@Data
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false)
    private String username;
}

public interface UserRepository extends JpaRepository<User, Long> {
    List<User> findByUsername(String username);
    
    @Query("SELECT u FROM User u WHERE u.email LIKE %:keyword%")
    List<User> searchByEmail(@Param("keyword") String keyword);
}
```

## 🔌 连接池配置（HikariCP）

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20        # 最大连接数
      minimum-idle: 5              # 最小空闲
      connection-timeout: 30000   # 获取连接超时
      idle-timeout: 600000        # 空闲超时
      max-lifetime: 1800000       # 连接最大寿命
      # MySQL 性能优化
      data-source-properties:
        rewriteBatchedStatements: true
        cachePrepStmts: true
        prepStmtCacheSize: 250
```

## 📈 性能优化

```java
// 1. 批量操作（MyBatis-Plus 自动分批）
userService.saveBatch(users, 1000);

// 2. 只查需要的字段
List<User> users = userMapper.selectList(
    Wrappers.<User>lambdaQuery()
        .select(User::getId, User::getUsername)
);

// 3. 懒加载大字段
@TableField(select = false)
private String bio;
```

## 🎯 总结

**推荐方案：MyBatis-Plus**
- ✅ 零 SQL CRUD（80% 场景）
- ✅ 类型安全（Lambda 表达式）
- ✅ 内置分页、逻辑删除、乐观锁
- ✅ 与 Spring Boot 完美集成

**vs Spring Data JPA：**
- ✅ MyBatis-Plus：SQL 灵活，复杂查询强
- ✅ JPA：面向对象，单表简单

**下一步：** [🔄 事务管理](/01-springboot/transaction) — @Transactional 传播机制与事务隔离级别


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
