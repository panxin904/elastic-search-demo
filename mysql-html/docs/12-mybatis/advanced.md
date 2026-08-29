---
title: MyBatis-Plus 高级特性
date: 2026-08-15  # date-auto-injected
---

# 🚀 MyBatis-Plus 高级特性

> 深入 MyBatis-Plus 的进阶特性：**逻辑删除、乐观锁、自动填充、租户插件**，让企业级开发更高效。

## 🕐 高级特性概览

| 特性 | 解决的问题 | 应用场景 |
|---|---|---|
| **逻辑删除** | 软删除，数据可恢复 | 所有业务表 |
| **乐观锁** | 防止并发更新丢失 | 库存、订单状态 |
| **自动填充** | 自动维护时间/用户字段 | 所有业务表 |
| **多租户** | 自动按租户隔离数据 | SaaS 系统 |
| **数据权限** | 按用户权限过滤数据 | 多角色系统 |
| **乐观锁 + 悲观锁** | 高并发场景 | 金融、库存 |
| **动态表名** | 分表分库场景 | 大数据量表 |
| **SQL 注入器** | 扩展自定义 SQL | 自定义批量操作 |

## 🗑️ 逻辑删除（最常用）

### 配置

```yaml
mybatis-plus:
  global-config:
    db-config:
      logic-delete-field: deleted  # 数据库字段名
      logic-delete-value: 1         # 删除值（已删除）
      logic-not-delete-value: 0     # 未删除值
```

### 实体类

```java
@Data
@TableName("users")
public class User {
    @TableId
    private Long id;
    
    private String userName;
    
    // ✅ 关键注解
    @TableLogic
    private Integer deleted;  // 0=未删除 1=已删除
}
```

### 自动效果

```java
// 查询：自动加 WHERE deleted = 0
List<User> users = userMapper.selectList(null);
// SQL: SELECT * FROM users WHERE deleted = 0

// 删除：自动改为 UPDATE
userMapper.deleteById(1L);
// SQL: UPDATE users SET deleted=1 WHERE id=1 AND deleted=0

// 统计：自动加 WHERE deleted = 0
long count = userMapper.selectCount(null);
// SQL: SELECT COUNT(*) FROM users WHERE deleted = 0

// 批量删除
userMapper.deleteByIds(Arrays.asList(1, 2, 3));
// SQL: UPDATE users SET deleted=1 WHERE id IN (1,2,3) AND deleted=0
```

### 高级用法

```java
// 1. 查询包含已删除的
List<User> all = userMapper.selectList(
    Wrappers.<User>lambdaQuery().eq(User::getDeleted, 1)
);

// 2. 手动控制（临时关闭逻辑删除）
@TableName(value = "users", excludeProperty = "deleted")
public class UserTemp {
    private Integer deleted;  // 不参与逻辑删除
}

// 3. 自定义逻辑删除值
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
public @interface CustomLogic {
    String value() default "is_deleted";  // 字段名
    String deleteValue() default "Y";     // 已删除值
    String notDeleteValue() default "N";  // 未删除值
}
```

## 🔒 乐观锁（防止并发丢失更新）

### 经典问题

```java
// ❌ 并发问题：两个请求同时修改同一行
// 请求 A: 读 product(stock=10), 准备更新为 9
// 请求 B: 读 product(stock=10), 准备更新为 8
// 请求 A: UPDATE product SET stock=9 WHERE id=1   → 成功
// 请求 B: UPDATE product SET stock=8 WHERE id=1   → 成功
// 最终 stock=8，A 的更新丢失！
```

### 乐观锁方案

```sql
ALTER TABLE products ADD COLUMN version INT DEFAULT 1 COMMENT '乐观锁版本';
```

```java
@Data
@TableName("products")
public class Product {
    @TableId
    private Long id;
    
    private Integer stock;
    
    @Version  // ✅ 关键注解
    private Integer version;
}
```

### 自动效果

```java
// 第一次更新：version 1 → 2
Product p1 = productService.getById(1);
p1.setStock(9);
boolean ok1 = productService.updateById(p1);
// SQL: UPDATE products SET stock=9, version=2 WHERE id=1 AND version=1
// 返回 true

// 第二次并发更新：version=1 已经不匹配
Product p2 = productService.getById(1);  // 重新读，version=2
p2.setStock(8);
boolean ok2 = productService.updateById(p2);
// SQL: UPDATE products SET stock=8, version=3 WHERE id=1 AND version=2
// 返回 true（但基于的是新版本）

// 如果两个并发请求都读到 version=1：
// 请求 A: UPDATE ... SET version=2 WHERE version=1 → 影响 1 行
// 请求 B: UPDATE ... SET version=2 WHERE version=1 → 影响 0 行（被 B 抢先）
// 业务层可以检测：如果 ok=false，说明更新失败，重试
```

### 性能优化：用原子操作

```java
// ✅ 推荐：避免读改写（用 SQL 原子操作）
@Update("UPDATE products SET stock = stock - #{quantity} WHERE id = #{id} AND stock >= #{quantity}")
int decreaseStock(@Param("id") Long id, @Param("quantity") Integer quantity);

// 业务层判断返回值
int affected = productMapper.decreaseStock(1, 1);
if (affected == 0) {
    // 库存不足
}
```

## 🕐 自动填充（create_time / update_time）

### 实体类注解

```java
@Data
@TableName("orders")
public class Order {
    @TableId
    private Long id;
    
    private BigDecimal amount;
    
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
    
    @TableField(fill = FieldFill.UPDATE)
    private LocalDateTime paidAt;  // 只在 update 时填充
}
```

### 实现 MetaObjectHandler

```java
@Component
public class MyMetaObjectHandler implements MetaObjectHandler {
    
    @Override
    public void insertFill(MetaObject metaObject) {
        LocalDateTime now = LocalDateTime.now();
        this.strictInsertFill(metaObject, "createdAt", LocalDateTime.class, now);
        this.strictInsertFill(metaObject, "updatedAt", LocalDateTime.class, now);
        
        // ✅ 可选：自动填充当前用户
        Long currentUserId = SecurityContext.getCurrentUserId();
        this.strictInsertFill(metaObject, "createBy", Long.class, currentUserId);
    }
    
    @Override
    public void updateFill(MetaObject metaObject) {
        // 只在字段为 null 时填充（避免覆盖用户设置的值）
        this.strictUpdateFill(metaObject, "updatedAt", LocalDateTime.class, LocalDateTime.now());
        
        Long currentUserId = SecurityContext.getCurrentUserId();
        this.strictUpdateFill(metaObject, "updateBy", Long.class, currentUserId);
    }
}
```

### 高级用法

```java
// 1. 字段已有值时不覆盖
@TableField(fill = FieldFill.INSERT_UPDATE)
// 如果 createTime 已有值，只更新 updateTime

// 2. 关闭自动填充（运行时）
StrictFillUtils.strictFillStrategy(false);  // 禁用
```

## 🏢 多租户（企业级 SaaS 必备）

### 场景

```
SaaS 系统：多个公司（租户）共用一个数据库
- 每个租户的数据自动隔离
- 不需要每个查询手动加 WHERE tenant_id = ?
```

### 实体类

```java
@Data
@TableName("orders")
public class Order {
    @TableId
    private Long id;
    
    private Long tenantId;  // 租户 ID
    
    private BigDecimal amount;
}
```

### 多租户插件

```java
@Component
public class TenantLineInner implements TenantLineHandler {
    
    @Override
    public Expression getTenantId() {
        // 从 SecurityContext 获取当前租户 ID
        Long tenantId = SecurityContext.getTenantId();
        if (tenantId == null) {
            return new NullValue();  // 没租户返回 null
        }
        return new LongValue(tenantId);
    }
    
    @Override
    public boolean ignoreTable(String tableName) {
        // 字典表、配置表不需要加租户过滤
        return Arrays.asList("sys_dict", "sys_config").contains(tableName);
    }
    
    @Override
    public boolean ignoreInsert(List<TableFieldInfo> fields, String tenantId) {
        // 插入时，tenantId 由框架自动填充
        return true;  // 由 MetaObjectHandler 处理
    }
}
```

### 自动元数据处理器（自动填租户 ID）

```java
@Component
public class TenantMetaHandler implements MetaObjectHandler {
    
    @Override
    public void insertFill(MetaObject metaObject) {
        Long tenantId = SecurityContext.getTenantId();
        this.strictInsertFill(metaObject, "tenantId", Long.class, tenantId);
        // 同时填充时间字段
        this.strictInsertFill(metaObject, "createdAt", LocalDateTime.class, LocalDateTime.now());
    }
    
    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updatedAt", LocalDateTime.class, LocalDateTime.now());
    }
}
```

### 配置 + 注册

```yaml
mybatis-plus:
  plugins:
    - com.baomidou.mybatisplus.extension.plugins.inner.TenantLineInnerInterceptor
```

```java
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor(
    TenantLineInner tenantLineInner
) {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    interceptor.addInnerInterceptor(new PaginationInnerInterceptor());  // 必须放最后
    interceptor.addInnerInterceptor(tenantLineInner);
    return interceptor;
}
```

### 自动效果

```java
// 业务代码完全无感
List<Order> orders = orderMapper.selectList(null);
// SQL: SELECT * FROM orders WHERE tenant_id = 123

orderMapper.insert(order);
// 自动填 tenant_id = 123

orderMapper.deleteById(1L);
// SQL: UPDATE orders SET deleted=1 WHERE id=1 AND tenant_id=123
```

## 🔐 数据权限（行级权限）

### 场景

```
系统有：管理员、部门经理、普通员工
- 管理员看所有数据
- 部门经理看本部门数据
- 员工只看自己的数据
```

### 实体类

```java
@Data
@TableName("orders")
public class Order {
    @TableId
    private Long id;
    
    private Long deptId;  // 部门 ID
    private Long userId;
    private BigDecimal amount;
}
```

### 数据权限插件

```java
@Component
public class DataScopeInner implements DataPermissionHandler {
    
    @Override
    public Expression getSqlSegment(PlainExpression[] where, DataPermissionContext ctx) {
        // 获取当前用户的权限范围
        Set<Long> allowedDeptIds = SecurityContext.getDataScopeDeptIds();
        
        // 构建 SQL 片段
        if (allowedDeptIds.isEmpty()) {
            // 无权限，返回永假
            return new NullValue();
        }
        
        // dept_id IN (1, 2, 3)
        StringJoiner joiner = new StringJoiner(", ", "(", ")");
        for (Long deptId : allowedDeptIds) {
            joiner.add(String.valueOf(deptId));
        }
        return new StringValue("dept_id IN " + joiner.toString() + " AND deleted = 0");
    }
}
```

### 使用

```java
// 员工 A 登录，只能看自己部门的数据
List<Order> orders = orderMapper.selectList(null);
// SQL: SELECT * FROM orders WHERE dept_id IN (1, 2) AND deleted=0

// 管理员登录，看所有数据
// SQL: SELECT * FROM orders WHERE deleted=0
```

## 🧩 动态表名（分表场景）

### 案例：按月分表

```sql
CREATE TABLE orders_202501 (...);
CREATE TABLE orders_202502 (...);
-- 每个月一张表
```

```java
@Component
public class DynamicTableNameInner implements DynamicTableNameHandler {
    
    @Override
    public String dynamicTableName(String sql, String tableName) {
        if ("orders".equals(tableName)) {
            String month = LocalDate.now().format(DateTimeFormatter.ofPattern("yyyyMM"));
            return "orders_" + month;
        }
        return tableName;
    }
}
```

**业务代码：**
```java
// 业务代码用逻辑表名
orderMapper.insert(order);  
// 实际表名: orders_202507
```

## 🔧 SQL 注入器（自定义批量 SQL）

### 场景：批量插入并返回 IDs

```java
@Component
public class InsertBatchWithReturnId implements ISqlInjector {
    
    @Override
    public List<AbstractMethod> getMethodList(Class<?> mapperClass, GlobalConfig globalConfig) {
        return Arrays.asList(new InsertBatchSomeColumn());
    }
}

// 自定义方法
public interface UserMapper extends BaseMapper<User> {
    @Insert("INSERT INTO user (name, email) VALUES (#{name}, #{email})")
    int customInsert(User user);
}
```

## 🎯 数据脱敏（保护敏感字段）

### 自定义注解 + 拦截器

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
public @interface SensitiveField {
    SensitiveType value();
}

public enum SensitiveType {
    PHONE, ID_CARD, EMAIL
}

// 实体类
@Data
public class User {
    private String name;
    
    @SensitiveField(SensitiveType.PHONE)
    private String phone;
    
    @SensitiveField(SensitiveType.ID_CARD)
    private String idCard;
}

// 脱敏处理器（在 ResultSetHandler 拦截）
@Intercepts(@Signature(type = ResultSetHandler.class, method = "handleResultSets", args = {Statement.class}))
public class DataMaskInterceptor implements Interceptor {
    
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        Object result = invocation.proceed();
        if (result instanceof List) {
            for (Object obj : (List<?>) result) {
                maskObject(obj);
            }
        } else if (result != null) {
            maskObject(result);
        }
        return result;
    }
    
    private void maskObject(Object obj) {
        Class<?> clazz = obj.getClass();
        for (Field field : clazz.getDeclaredFields()) {
            SensitiveField ann = field.getAnnotation(SensitiveField.class);
            if (ann == null) continue;
            
            field.setAccessible(true);
            try {
                Object value = field.get(obj);
                if (value instanceof String) {
                    String masked = mask((String) value, ann.value());
                    field.set(obj, masked);
                }
            } catch (Exception ignored) {}
        }
    }
    
    private String mask(String value, SensitiveType type) {
        switch (type) {
            case PHONE: return value.replaceAll("(\\d{3})\\d{4}", "$1****");
            case ID_CARD: return value.replaceAll("(\\d{4})\\d+(\\d{4})", "$1**********$2");
            case EMAIL: return value.replaceAll("(?<=.).(?=[^@]*?@)", "*");
            default: return value;
        }
    }
}
```

## 📊 动态数据源（读写分离）

```java
@Configuration
public class DataSourceConfig {
    
    @Bean
    @Primary
    public DataSource masterDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:mysql://master:3306/mydb")
            .build();
    }
    
    @Bean
    public DataSource slaveDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:mysql://slave:3306/mydb")
            .build();
    }
}

// 动态切换
public class DataSourceContextHolder {
    private static final ThreadLocal<String> TYPE = new ThreadLocal<>();
    
    public static void set(String type) { TYPE.set(type); }
    public static String get() { return TYPE.get(); }
    public static void clear() { TYPE.remove(); }
}

// 在 Service 层切换（手动）
@Service
public class UserService {
    @ReadOnly  // 自定义注解切到从库
    public List<User> findAll() {
        return userMapper.selectList(null);
    }
}
```

## 🎯 总结

**企业级 MP 最佳实践：**
- ✅ 用 `@TableLogic` 做软删除
- ✅ 用 `@Version` 防并发丢失
- ✅ 用 `MetaObjectHandler` 填时间/用户
- ✅ 用 `TenantLineInner` 实现多租户
- ✅ 用 `DataPermissionInterceptor` 做行级权限
- ✅ 用 Redis 做二级缓存（不用 MP 内置）

**性能优化要点：**
- ✅ 批量操作分批（1000/批）
- ✅ 解决 N+1（JOIN 或批量 IN）
- ✅ 深分页用游标分页
- ✅ 大字段懒加载

**下一步：** [🔧 MyBatis 与 Spring Boot 集成实战](/12-mybatis/spring-boot) — 完整项目实战