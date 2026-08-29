---
title: MyBatis 性能优化
date: 2026-08-15  # date-auto-injected
---

# 🎯 MyBatis 性能优化

> MyBatis 性能问题 90% 都来自 **N+1 查询、批量操作不当、慢 SQL**。学会这些优化技巧，**性能提升 10-50 倍**。

## 🚨 问题 1：N+1 查询问题（最常见）

### 什么是 N+1？

```java
// 场景：查询 10 个用户，每个用户的订单
public class UserService {
    
    public List<UserDTO> getUserWithOrders() {
        // 1️⃣ 查询 10 个用户
        List<User> users = userMapper.selectList(null);  // 1 次查询
        
        // 2️⃣ ❌ 对每个用户，单独查询订单
        List<UserDTO> result = new ArrayList<>();
        for (User user : users) {
            // N=10 次查询
            List<Order> orders = orderMapper.selectByUserId(user.getId());
            result.add(new UserDTO(user, orders));
        }
        return result;
        // 总查询次数：1 + 10 = 11 次（N+1 公式）
    }
}
```

### 解决方案

**方案 1：JOIN 查询（推荐）**

```xml
<!-- UserMapper.xml -->
<resultMap id="userWithOrdersMap" type="UserDTO">
    <id column="id" property="id"/>
    <result column="user_name" property="userName"/>
    <!-- 一对多：订单列表 -->
    <collection property="orders" ofType="Order">
        <id column="order_id" property="id"/>
        <result column="amount" property="amount"/>
        <result column="created_at" property="createdAt"/>
    </collection>
</resultMap>

<select id="getUserWithOrders" resultMap="userWithOrdersMap">
    SELECT 
        u.id, u.user_name,
        o.id AS order_id, o.amount, o.created_at
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    WHERE u.status = 1
    ORDER BY u.id, o.created_at
</select>
```

**方案 2：MyBatis-Plus 的 `@RelationField`（3.5.3+）**

```java
// 实体类声明关联
@Data
@TableName("users")
public class User {
    private Long id;
    private String userName;
    
    // 字段无关，关联查订单
    @RelationField(
        relation = "订单列表",
        select = "SELECT * FROM orders WHERE user_id = #{id}"
    )
    private List<Order> orders;
}

// 查询时自动加载关联
List<UserDTO> users = userMapper.selectJoinList(UserDTO.class, ...);
// 自动执行关联查询，避免 N+1
```

**方案 3：批量 IN 查询**

```java
// 2️⃣ 查询所有订单，IN 一次查完
List<Long> userIds = users.stream().map(User::getId).collect(toList());
List<Order> allOrders = orderMapper.selectByUserIds(userIds);  // 1 次查询

// 3️⃣ 在内存中分组关联
Map<Long, List<Order>> ordersByUser = allOrders.stream()
    .collect(groupingBy(Order::getUserId));

return users.stream()
    .map(u -> new UserDTO(u, ordersByUser.getOrDefault(u.getId(), emptyList())))
    .collect(toList());

// 总查询次数：2 次（用户 + 订单）
```

## 🚨 问题 2：慢 SQL 优化

### 案例：列表查询慢

```java
// ❌ 慢查询
@GetMapping("/list")
public List<Product> list() {
    return productMapper.selectList(null);  // 全表扫描
    // SELECT * FROM product
    // 100 万行 = 几十秒
}
```

**优化：必传分页参数**

```java
@GetMapping("/page")
public IPage<Product> page(
    @RequestParam(defaultValue = "1") Integer pageNum,
    @RequestParam(defaultValue = "20") Integer pageSize,
    @RequestParam(required = false) String name,
    @RequestParam(required = false) Long categoryId
) {
    // 强制分页（必须传分页参数）
    if (pageSize > 100) pageSize = 100;  // 限制最大
    
    Page<Product> page = new Page<>(pageNum, pageSize);
    LambdaQueryWrapper<Product> wrapper = Wrappers.<Product>lambdaQuery();
    
    // 条件筛选（避免无关查询带出全部数据）
    if (name != null) wrapper.like(Product::getName, name);
    if (categoryId != null) wrapper.eq(Product::getCategoryId, categoryId);
    wrapper.eq(Product::getStatus, 1);  // 默认过滤
    
    return productMapper.selectPage(page, wrapper);
}
```

### 案例：复杂统计查询

```xml
<!-- ❌ 错误：先查全部再内存统计 -->
<select id="getStats" resultType="map">
    SELECT * FROM orders  <!-- 全表扫描 -->
</select>

<!-- ✅ 正确：直接用 SQL 聚合 -->
<select id="getStats" resultType="map">
    SELECT 
        DATE_FORMAT(created_at, '%Y-%m') AS month,
        COUNT(*) AS cnt,
        SUM(amount) AS total
    FROM orders
    WHERE status = 'paid'
      AND created_at >= #{startDate}
    GROUP BY DATE_FORMAT(created_at, '%Y-%m')
</select>
```

## 🚨 问题 3：批量操作优化

### ❌ 循环单条插入

```java
// ❌ 性能极差（1000 条 = 1000 次网络往返）
public void batchInsert(List<User> users) {
    for (User user : users) {
        userMapper.insert(user);
    }
}
```

### ✅ 批量插入

```xml
<!-- UserMapper.xml -->
<insert id="batchInsert" useGeneratedKeys="true" keyProperty="id">
    INSERT INTO user (user_name, email, age) VALUES
    <foreach collection="list" item="user" separator=",">
        (#{user.userName}, #{user.email}, #{user.age})
    </foreach>
</insert>
```

```java
// ✅ 单条 SQL 插入
userMapper.batchInsert(userList);
```

**MyBatis-Plus 方式：**

```java
// ✅ 自动分批（默认 1000/批）
userService.saveBatch(users);
// 或自定义批次大小
userService.saveBatch(users, 500);
```

### ✅ 批量更新（高效方式）

```java
// ❌ 错误：N 次更新
for (User user : users) {
    userMapper.updateById(user);
}

// ✅ 正确：一条 SQL 批量更新
public void batchUpdateStatus(List<Long> ids, Integer status) {
    userMapper.update(null,
        Wrappers.<User>lambdaUpdate()
            .in(User::getId, ids)
            .set(User::getStatus, status)
    );
    // SQL: UPDATE user SET status=? WHERE id IN (?, ?, ...)
}
```

### ✅ 批量更新不同值（CASE WHEN）

```xml
<!-- 一条 SQL 更新不同用户的不同字段 -->
<update id="batchUpdateSelective">
    UPDATE user
    <trim prefix="SET" suffixOverrides=",">
        <foreach collection="list" item="user" separator=",">
            <if test="user.userName != null">user_name = CASE id
                <foreach collection="list" item="item">
                    WHEN #{item.id} THEN #{item.userName}
                </foreach>
            </if>
        </foreach>
    </trim>
    WHERE id IN
    <foreach collection="list" item="user" open="(" separator="," close=")">
        #{user.id}
    </foreach>
</update>
```

## 🚨 问题 4：参数传递优化

### ❌ 在循环中调用

```java
// ❌ N+1 性能问题
for (Long userId : userIds) {
    User user = userMapper.selectById(userId);  // N 次查询
}
```

### ✅ 用 IN 批量

```java
// ✅ 1 次查询
List<User> users = userMapper.selectBatchIds(userIds);
```

### ✅ 用 Map 接收结果

```java
// ✅ 用 Map 接收（避免反射）
@MapKey("id")
Map<Long, User> getUserMapByIds(@Param("ids") List<Long> ids);

// 使用
Map<Long, User> userMap = userMapper.getUserMapByIds(userIds);
userMap.get(1L);  // O(1) 获取
```

## 🚨 问题 5：分页深分页优化

### ❌ OFFSET 性能差

```sql
-- LIMIT 1000000, 20  扫描 100 万行
SELECT * FROM orders LIMIT 1000000, 20;
```

### ✅ 游标分页

```sql
-- 基于主键的游标分页
SELECT * FROM orders
WHERE id > #{lastId}
  AND user_id = #{userId}
ORDER BY id LIMIT 20;
```

```java
@GetMapping("/page")
public List<Order> page(
    @RequestParam Long userId,
    @RequestParam(required = false) Long lastId
) {
    if (lastId == null) lastId = 0L;
    
    return orderMapper.selectList(
        Wrappers.<Order>lambdaQuery()
            .eq(Order::getUserId, userId)
            .gt(Order::getId, lastId)
            .orderByAsc(Order::getId)
            .last("LIMIT 20")
    );
}
```

## 🚨 问题 6：关联查询优化

### ❌ 多次单条查询

```java
// ❌ N+1
public UserDTO getUserDetail(Long userId) {
    User user = userMapper.selectById(userId);
    List<Order> orders = orderMapper.selectByUserId(userId);
    UserProfile profile = profileMapper.selectById(userId);
    // 3 次查询
    return new UserDTO(user, orders, profile);
}
```

### ✅ 单次复杂查询

```xml
<resultMap id="userDetailMap" type="UserDTO">
    <id column="u_id" property="id"/>
    <result column="user_name" property="userName"/>
    <collection property="orders" ofType="Order">
        <id column="o_id" property="id"/>
        <result column="amount" property="amount"/>
    </collection>
    <association property="profile" javaType="UserProfile">
        <id column="p_user_id" property="userId"/>
        <result column="bio" property="bio"/>
    </association>
</resultMap>

<select id="getUserDetail" resultMap="userDetailMap">
    SELECT 
        u.id AS u_id, u.user_name,
        o.id AS o_id, o.amount,
        p.bio AS bio
    FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
    LEFT JOIN user_profiles p ON u.id = p.user_id
    WHERE u.id = #{userId}
</select>
```

## 🚨 问题 7：大字段处理

### ❌ 一次性查询

```java
// ❌ 查所有字段（包括 TEXT 大字段）
User user = userMapper.selectById(1);
String bio = user.getBio();  // 10KB 字段

// 即使不用 bio，也加载了
```

### ✅ 懒加载

```sql
-- 实体类标记
```

```java
@Data
public class User {
    private Long id;
    private String userName;
    
    // 懒加载字段（延迟到访问时才查询）
    @TableField(value = "`bio`", select = false)
    private String bio;  // 默认不查
}

// 或在 Mapper.xml 中拆分
<select id="selectById" resultType="User">
    SELECT id, user_name, email  -- 不包含 bio
    FROM users WHERE id = #{id}
</select>

<select id="getBio" resultType="string">
    SELECT bio FROM users WHERE id = #{id}
</select>

// 按需加载
User user = userService.getById(1);  // 不查 bio
if (needBio) {
    String bio = userService.getBio(1);  // 按需查
}
```

## 🚨 问题 8：TypeHandler 使用

### 自定义枚举 TypeHandler

```java
// 枚举
public enum Status {
    ACTIVE(1), DISABLED(0);
    
    @JsonValue
    private final int code;
    
    Status(int code) { this.code = code; }
    
    @JsonCreator
    public static Status of(int code) {
        return Arrays.stream(values())
            .filter(s -> s.code == code)
            .findFirst().orElseThrow();
    }
}

// 自定义 TypeHandler
@MappedTypes(Status.class)
public class StatusTypeHandler extends BaseTypeHandler<Status> {
    
    @Override
    public void setNonNullParameter(PreparedStatement ps, int i, Status param, JdbcType jdbcType) {
        ps.setInt(i, param.code);
    }
    
    @Override
    public Status getNullableResult(ResultSet rs, String columnName) {
        return Status.of(rs.getInt(columnName));
    }
    
    // 其他重载...
}

// 注册（application.yml 中或 mybatis.xml 中）
mybatis-plus:
  configuration:
    type-handlers-package: com.example.handler
```

**性能优势：** 避免在 Java 端做 code → enum 的转换（已经在 SQL 返回时直接转）。

## 🚨 问题 9：连接池配置

```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20          # ← 最大连接数（不是越大越好！）
      minimum-idle: 5                # 最小空闲
      connection-timeout: 30000      # 连接超时
      idle-timeout: 600000           # 空闲超时
      max-lifetime: 1800000          # 连接最大寿命
      # ⚠️ maximum-pool-size 不要超过 100
      # 数据库连接数 = (maximum-pool-size × 服务实例数)
      # 一般数据库 max_connections = 500，10 个实例每个 20 连接刚好
      
mybatis-plus:
  configuration:
    # Statement 超时
    default-statement-timeout: 30
    # 默认执行器
    default-executor-type: REUSE    # 执行器复用（性能更好）
```

## 📊 性能优化清单

| 优化项 | 性能提升 | 难度 |
|---|---|---|
| 解决 N+1（JOIN） | 10-100x | ⭐⭐ |
| 批量插入（foreach） | 10-50x | ⭐ |
| 批量更新（IN） | 5-20x | ⭐ |
| 深分页优化（游标） | 10-100x | ⭐⭐ |
| 懒加载大字段 | 2-5x | ⭐ |
| 连接池配置 | 1.5-3x | ⭐ |
| 自定义 TypeHandler | 1.2-2x | ⭐⭐ |
| 覆盖索引 | 2-10x | ⭐⭐ |
| 慢查询索引优化 | 10-100x | ⭐⭐ |

## 🎯 总结

**MyBatis 性能核心问题：**
- ⚠️ **N+1 查询**（最常见，性能杀手）
- ⚠️ **批量操作不当**（循环 vs 批量）
- ⚠️ **慢 SQL**（缺索引、复杂查询）
- ⚠️ **深分页**（OFFSET 大）
- ⚠️ **大字段**（TEXT/BLOB 不该每次都查）

**优化黄金法则：**
- ✅ 一条 SQL 能做的事，绝不用 N 条
- ✅ 批量操作分批（1000/批）
- ✅ 复杂查询用 JOIN 解决 N+1
- ✅ 大字段懒加载
- ✅ 深分页用游标分页
- ✅ 慢查询必有索引支撑

**下一步：** [🔧 MyBatis 与 Spring Boot 集成实战](/12-mybatis/spring-boot) — 完整项目实战