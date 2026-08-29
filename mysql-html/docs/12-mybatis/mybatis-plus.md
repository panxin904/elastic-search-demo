---
title: MyBatis-Plus 实战
date: 2026-08-15  # date-auto-injected
---

# 🚀 MyBatis-Plus 实战

> MyBatis-Plus（MP）是 MyBatis 的**增强工具**，**只做增强不做改变**，极大简化 CRUD 开发。是现代 Java 项目的首选 ORM。

## 🎯 MyBatis-Plus 是什么？

MyBatis-Plus 是在 MyBatis 基础上**只做增强**的框架，提供了：

- ✅ **内置通用 CRUD**：无需写 SQL 即可完成 80% 的单表操作
- ✅ **内置分页插件**：一行代码实现分页
- ✅ **代码生成器**：一键生成 Entity / Mapper / Service / Controller
- ✅ **内置通用 Service**：业务层通用 CRUD
- ✅ **逻辑删除**：自动添加 deleted 字段过滤
- ✅ **自动填充**：自动填充 create_time / update_time
- ✅ **多租户**：自动加租户 ID 过滤
- ✅ **SQL 注入器**：自由扩展 SQL

## 🚀 快速开始

### 1. 添加依赖

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

### 2. application.yml 配置

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: xxx

mybatis-plus:
  # Mapper XML 位置
  mapper-locations: classpath:mapper/**/*.xml
  # 实体类别名
  type-aliases-package: com.example.entity
  # 实体类父类（如 BaseEntity 含公共字段）
  type-aliases-super-type: com.example.entity.BaseEntity
  
  configuration:
    # 下划线转驼峰
    map-underscore-to-camel-case: true
    # 缓存
    cache-enabled: false
    # 驼峰转下划线（可选）
    mapUnderscoreToCamelCase: true
  
  # 全局配置
  global-config:
    banner: false
    db-config:
      # 主键类型（auto / assign_id / assign_uuid）
      id-type: assign_id
      # 逻辑删除字段名
      logic-delete-field: deleted
      # 逻辑删除默认值
      logic-delete-value: 1
      # 逻辑未删除值
      logic-not-delete-value: 0
  
  # 扩展插件
  plugins:
    # 分页插件（必须放最后）
    - com.baomidou.mybatisplus.extension.plugins.inner.PaginationInnerInterceptor
    # 乐观锁插件
    - com.baomidou.mybatisplus.extension.plugins.inner.OptimisticLockerInnerInterceptor
    # 数据权限插件
    - com.baomidou.mybatisplus.extension.plugins.inner.DataPermissionInterceptor
```

### 3. 实体类（关键）

```java
package com.example.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("users")  // 指定表名
public class User {
    
    @TableId(type = IdType.ASSIGN_ID)  // 主键策略（雪花算法）
    private Long id;
    
    @TableField("user_name")  // 字段与列名不一致时映射
    private String userName;
    
    @TableField(select = false)  // 查询时不返回该字段（用于密码）
    private String password;
    
    private String email;
    private Integer age;
    private Integer status;
    
    @TableField(fill = FieldFill.INSERT)  // 插入时自动填充
    private LocalDateTime createdAt;
    
    @TableField(fill = FieldFill.INSERT_UPDATE)  // 插入和更新时填充
    private LocalDateTime updatedAt;
    
    @TableLogic  // 逻辑删除字段
    @TableField(select = false)  // 默认不查询
    private Integer deleted;
    
    @Version  // 乐观锁版本号
    private Integer version;
    
    // 不存在的字段（使用 transient 或 static）
    @TableField(exist = false)
    private String notExistField;
}
```

## 📚 BaseMapper 通用 CRUD

### Mapper 接口（继承 BaseMapper）

```java
package com.example.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.example.entity.User;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface UserMapper extends BaseMapper<User> {
    // ✅ 已经拥有 30+ 常用方法，无需写 SQL！
    // 自定义方法放下面
    List<User> findCustom();
}
```

### 自动获得的方法

```java
@Service
public class UserService {
    
    @Autowired
    private UserMapper userMapper;
    
    // ========== 新增 ==========
    public void createUser(User user) {
        // 插入（自动填充 createdAt）
        userMapper.insert(user);
        log.info("新用户 ID: {}", user.getId());
    }
    
    // 批量插入
    public void batchCreate(List<User> users) {
        for (User user : users) {
            userMapper.insert(user);
        }
        // 推荐：使用 IService 的 saveBatch（更高效）
        // userService.saveBatch(users);
    }
    
    // ========== 删除 ==========
    // 物理删除
    public void deleteUser(Long id) {
        userMapper.deleteById(id);  // 真删
    }
    
    // 逻辑删除（推荐）
    @Test
    public void logicDelete() {
        // update user set deleted=1 where id=? and deleted=0
        userMapper.deleteById(1L);  // 自动逻辑删除
    }
    
    // 批量删除
    public void deleteBatch(List<Long> ids) {
        userMapper.deleteByIds(ids);
    }
    
    // 按条件删除
    public void deleteInactiveUsers() {
        // delete from users where status=0
        userMapper.delete(
            Wrappers.<User>lambdaQuery()
                .eq(User::getStatus, 0)
        );
    }
    
    // ========== 修改 ==========
    public void updateUser(User user) {
        userMapper.updateById(user);  // 按 ID 更新
    }
    
    // 条件更新
    public void activateUsers(List<Long> ids) {
        User update = new User();
        update.setStatus(1);
        userMapper.update(update, 
            Wrappers.<User>lambdaQuery().in(User::getId, ids)
        );
    }
    
    // ========== 查询（单个） ==========
    public User getById(Long id) {
        return userMapper.selectById(id);
    }
    
    // 复杂条件查询
    public User findByEmail(String email) {
        return userMapper.selectOne(
            Wrappers.<User>lambdaQuery()
                .eq(User::getEmail, email)
                .last("LIMIT 1")
        );
    }
    
    // ========== 查询（列表） ==========
    public List<User> listAll() {
        return userMapper.selectList(null);
    }
    
    public List<User> listActiveUsers() {
        return userMapper.selectList(
            Wrappers.<User>lambdaQuery()
                .eq(User::getStatus, 1)
                .orderByDesc(User::getCreatedAt)
        );
    }
    
    // ========== 查询（分页） ==========
    public IPage<User> pageActive(int page, int size) {
        // 第一个参数必须配合分页插件使用
        return userMapper.selectPage(
            new Page<>(page, size),
            Wrappers.<User>lambdaQuery().eq(User::getStatus, 1)
        );
    }
    
    // ========== 统计 ==========
    public long countActive() {
        return userMapper.selectCount(
            Wrappers.<User>lambdaQuery().eq(User::getStatus, 1)
        );
    }
}
```

## 🎯 条件构造器（LambdaQueryWrapper）

### 基础查询

```java
// 传统写法：复杂字符串拼接
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("status", 1)
       .like("user_name", "张")
       .orderByDesc("created_at")
       .last("LIMIT 10");

// ✅ Lambda 写法：类型安全，IDE 提示
LambdaQueryWrapper<User> wrapper = Wrappers.lambdaQuery(User.class);
wrapper.eq(User::getStatus, 1)
       .like(User::getUserName, "张")  // 编译期检查字段名
       .orderByDesc(User::getCreatedAt)
       .last("LIMIT 10");

List<User> users = userMapper.selectList(wrapper);
```

### 复杂条件组合

```java
LambdaQueryWrapper<User> wrapper = Wrappers.lambdaQuery(User.class);

// 等于 / 不等于
.eq(User::getStatus, 1)
.ne(User::getStatus, 0)

// 大于 / 小于 / BETWEEN
.gt(User::getAge, 18)
.lt(User::getAge, 60)
.between(User::getCreatedAt, startTime, endTime)

// LIKE（左/右/全模糊）
.like(User::getUserName, "张")       // %张%
.likeLeft(User::getUserName, "张")    // 张%
.likeRight(User::getUserName, "张")   // %张

// IN / NOT IN
.in(User::getId, Arrays.asList(1, 2, 3))
.notIn(User::getStatus, 0, 99)

// 范围
.between(User::getAge, 18, 30)
.notBetween(User::getCreatedAt, ...)

// NULL 判断
.isNull(User::getEmail)
.isNotNull(User::getPhone)

// 排序
.orderByAsc(User::getId)
.orderByDesc(User::getCreatedAt)
.orderByDesc(User::getStatus)
.orderByAsc(User::getId)

// 限制
.last("LIMIT 10")

// 组合 AND / OR
wrapper.and(w -> w.eq(User::getStatus, 1).or().eq(User::getStatus, 2))
wrapper.or(w -> w.gt(User::getAge, 18).lt(User::getAge, 30))
```

### 只查部分字段（select）

```java
// select 指定字段
wrapper.select(User::getId, User::getUserName, User::getEmail);

List<User> users = userMapper.selectList(wrapper);
// 查询结果只包含这三个字段
```

## 📄 分页插件

### 基础分页

```java
@GetMapping("/page")
public PageResult<User> page(
    @RequestParam(defaultValue = "1") int pageNum,
    @RequestParam(defaultValue = "10") int pageSize,
    @RequestParam(required = false) String name,
    @RequestParam(required = false) Integer status
) {
    // 分页参数（必须用 MyBatis-Plus 的 Page）
    Page<User> page = new Page<>(pageNum, pageSize);
    
    // 条件
    LambdaQueryWrapper<User> wrapper = Wrappers.lambdaQuery(User.class);
    if (name != null) wrapper.like(User::getUserName, name);
    if (status != null) wrapper.eq(User::getStatus, status);
    
    // 查询（自动分页）
    IPage<User> result = userMapper.selectPage(page, wrapper);
    
    // 返回分页结果
    return PageResult.success(result.getRecords(), result.getTotal());
}
```

### 返回结构

```java
@Data
public class PageResult<T> {
    private int pageNum;
    private int pageSize;
    private long total;
    private List<T> records;
    
    public static <T> PageResult<T> success(List<T> records, long total) {
        PageResult<T> r = new PageResult<>();
        r.setRecords(records);
        r.setTotal(total);
        return r;
    }
}

// 返回示例
{
  "pageNum": 1,
  "pageSize": 10,
  "total": 1024,
  "records": [...]
}
```

### 复杂分页（多表 JOIN）

```java
// 先查 product 表的 ID（带条件）
Page<Product> page = new Page<>(pageNum, pageSize);
IPage<Product> result = productMapper.selectPage(page, 
    Wrappers.<Product>lambdaQuery()
        .eq(Product::getStatus, 1)
        .like(Product::getName, "iPhone")
);
// 拿到 ID 列表后，再去查关联表（避免 JOIN 复杂度）
```

## 🕐 自动填充（create_time / update_time）

### 1. 实体类注解

```java
@TableField(fill = FieldFill.INSERT)
private LocalDateTime createdAt;

@TableField(fill = FieldFill.INSERT_UPDATE)
private LocalDateTime updatedAt;

@TableField(fill = FieldFill.UPDATE)
private LocalDateTime lastLoginTime;
```

### 2. 实现 MetaObjectHandler

```java
@Component
public class MyMetaObjectHandler implements MetaObjectHandler {
    
    @Override
    public void insertFill(MetaObject metaObject) {
        LocalDateTime now = LocalDateTime.now();
        this.strictInsertFill(metaObject, "createdAt", LocalDateTime.class, now);
        this.strictInsertFill(metaObject, "updatedAt", LocalDateTime.class, now);
        // 可选：自动填充当前用户
        // this.strictInsertFill(metaObject, "createBy", Long.class, getCurrentUserId());
    }
    
    @Override
    public void updateFill(MetaObject metaObject) {
        this.strictUpdateFill(metaObject, "updatedAt", LocalDateTime.class, LocalDateTime.now());
        // 可选：自动填充更新人
        // this.strictUpdateFill(metaObject, "updateBy", Long.class, getCurrentUserId());
    }
}
```

## 🗑️ 逻辑删除

### 1. 实体类 + 数据库

```sql
ALTER TABLE users ADD COLUMN deleted INT DEFAULT 0 COMMENT '0=未删 1=已删';
```

```java
@TableName("users")
@Data
public class User {
    @TableId(type = IdType.ASSIGN_ID)
    private Long id;
    
    // 其他字段...
    
    @TableLogic  // 关键注解
    @TableField(select = false)  // 默认不返回该字段
    private Integer deleted;
}
```

### 2. 自动效果

```java
// 查询时：自动过滤 deleted = 0
List<User> users = userMapper.selectList(null);
// SQL: SELECT * FROM users WHERE deleted = 0

// 删除时：自动改为 update
userMapper.deleteById(1L);
// SQL: UPDATE users SET deleted = 1 WHERE id = 1 AND deleted = 0

// ⚠️ 想查全部（含删除的）
List<User> all = userMapper.selectList(
    Wrappers.<User>lambdaQuery().eq(User::getDeleted, 1)
);
```

## 🔧 IService 通用 Service

```java
public interface UserService extends IService<User> {
    // ✅ 已拥有 30+ 通用方法
}

@Service
public class UserServiceImpl extends ServiceImpl<UserMapper, User> implements UserService {
    
    @Autowired
    private UserMapper userMapper;
    
    public void demo() {
        // 批量插入（默认 1000/批，自动分批）
        saveBatch(list);
        
        // 链式操作
        save(user);  // insert or update
        
        // 链式 lambda
        update().eq(...).set(...).update();
        remove().eq(...).remove();
        
        // 分页（链式）
        page(new Page<>(1, 10), 
             Wrappers.<User>lambdaQuery().eq(User::getStatus, 1)
        );
    }
    
    // 自定义业务方法
    public void customBusiness(Long userId) {
        User user = getById(userId);
        // 自定义逻辑...
    }
    
    @Override
    public boolean updateById(User entity) {
        // 可重写父类方法添加额外逻辑
        return super.updateById(entity);
    }
}
```

### 链式 Lambda（最强大特性）

```java
// 链式更新
userService.update()
    .eq("status", 0)
    .set("status", 1)
    .set("update_time", LocalDateTime.now())
    .update();

// 链式删除
userService.remove()
    .in("id", Arrays.asList(1, 2, 3))
    .remove();

// 链式查询
List<User> users = userService.lambdaQuery()
    .eq(User::getStatus, 1)
    .like(User::getUserName, "张")
    .list();
```

## 🚀 代码生成器

```java
public class CodeGenerator {
    public static void main(String[] args) {
        FastAutoGenerator.create("jdbc:mysql://localhost:3306/mydb", "root", "xxx")
            .globalConfig(builder -> builder
                .outputDir(System.getProperty("user.dir") + "/src/main/java")
                .author("YourName")
                .build()
            )
            .packageConfig(builder -> builder
                .parent("com.example")
                .moduleName("myapp")
                .build()
            )
            .strategyConfig(builder -> builder
                .addInclude("user", "order", "product")  // 要生成的表
                .addTablePrefix("t_")  // 去掉表前缀
                .entityBuilder()
                    .enableLombok()
                    .logicDeleteColumnName("deleted")
                    .idType(IdType.ASSIGN_ID)
                .build()
            )
            .templateEngine(new FreemarkerTemplateEngine())
            .execute();
    }
}
```

**生成内容：**
```
src/main/java/com/example/
├── entity/
│   ├── User.java         (含 @TableName, @TableField 等)
│   ├── Order.java
│   └── Product.java
├── mapper/
│   ├── UserMapper.java   (extends BaseMapper)
│   ├── OrderMapper.java
│   └── ProductMapper.java
├── service/
│   ├── UserService.java  (extends IService)
│   ├── UserServiceImpl.java
│   └── ...
└── controller/
    ├── UserController.java  (基础 CRUD 接口)
    └── ...
```

## 🛡️ 乐观锁（防并发更新丢失）

### 实体类

```java
@Version  // 乐观锁注解
private Integer version;
```

```sql
ALTER TABLE products ADD COLUMN version INT DEFAULT 1 COMMENT '乐观锁版本';
```

### 使用

```java
// 第一次更新：version 自动从 1 → 2
Product product = productService.getById(1);
product.setPrice(100);
productService.updateById(product);
// SQL: UPDATE product SET price=100, version=2 WHERE id=1 AND version=1

// 第二次更新：where version=1 已经不匹配，更新失败
product.setPrice(99);
boolean success = productService.updateById(product);
// 返回 false（更新条数 = 0）
```

**应用场景：**
- 库存扣减（防止超卖）
- 并发修改（如订单状态）
- 分布式系统中的 ABA 问题

## 🏢 多租户（自动加租户 ID）

```java
// 实体类
@TableField(fill = FieldFill.INSERT)
private Long tenantId;

// 多租户插件
@Component
public class TenantLineInner implements TenantLineHandler {
    @Override
    public Expression getTenantId() {
        return new LongValue(SecurityContext.getTenantId());  // 从 Security 取
    }
    
    @Override
    public boolean ignoreTable(String tableName) {
        // 忽略不需要加租户的表（如字典表）
        return Arrays.asList("sys_dict").contains(tableName);
    }
}
```

```yaml
mybatis-plus:
  plugins:
    - com.baomidou.mybatisplus.extension.plugins.inner.TenantLineInnerInterceptor
```

**自动效果：**
- 所有查询自动加 `WHERE tenant_id = ?`
- 所有写入自动加 `tenant_id = ?`

## 📊 性能配置

```yaml
mybatis-plus:
  configuration:
    # 缓存
    cache-enabled: true
    # 延迟加载
    lazy-loading-enabled: true
    # 执行器类型：SIMPLE / REUSE / BATCH
    default-executor-type: REUSE
    # 默认 Statement 超时（秒）
    default-statement-timeout: 30
```

```java
// 批量操作配置
@Transactional
public void batchInsert(List<User> users) {
    // 默认每批 1000
    userService.saveBatch(users, 1000);
    
    // 禁用批处理（性能更好但占内存）
    userService.saveBatch(users, 1000, false);  
}
```

## 🎯 总结

**MyBatis-Plus 核心优势：**
- ✅ **零 SQL CRUD**：80% 的单表操作无需写 SQL
- ✅ **类型安全**：Lambda 表达式编译期检查
- ✅ **代码生成**：一键生成全套代码
- ✅ **插件丰富**：分页、乐观锁、逻辑删除、多租户
- ✅ **MyBatis 兼容**：原有 MyBatis 代码无需改动

**最佳实践：**
- ✅ 用 LambdaQueryWrapper（类型安全）
- ✅ 用 IService 继承（通用方法）
- ✅ 用 @TableLogic（逻辑删除）
- ✅ 用自动填充（时间字段）
- ✅ 用乐观锁（并发更新）
- ✅ 复杂查询仍用 XML（动态 SQL）

**下一步：** [⚙️ MyBatis 缓存机制](/12-mybatis/cache) — 一级缓存 / 二级缓存的正确打开方式