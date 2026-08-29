---
title: MyBatis 常见坑与最佳实践
date: 2026-08-15  # date-auto-injected
---

# ⚠️ MyBatis 常见坑与最佳实践

> 总结 MyBatis / MyBatis-Plus 开发中最常见的 10 个坑，以及 12 条企业级最佳实践。

## 🚨 10 个常见坑

### 坑 1：${} 字符串拼接（SQL 注入风险）

```java
// ❌ SQL 注入风险
@Select("SELECT * FROM users WHERE name = '${name}'")
User findByName(String name);
// 攻击：name = "' OR '1'='1" → 查所有数据

// ✅ 用 #{}（参数化）
@Select("SELECT * FROM users WHERE name = #{name}")
User findByName(String name);
// 自动加预编译，参数化查询

// ⚠️ ${} 仅用于动态表名/列名（不能参数化的部分）
@Select("SELECT * FROM ${tableName} WHERE id = #{id}")
User findById(@Param("tableName") String table, @Param("id") Long id);
// 必须自己确保 tableName 是安全的（如白名单）
```

### 坑 2：N+1 查询问题

```java
// ❌ 经典 N+1
List<User> users = userMapper.selectList(null);  // 1 次
for (User u : users) {
    List<Order> orders = orderMapper.selectByUserId(u.getId());  // N 次
}

// ✅ 一条 JOIN 解决
<select id="getUserWithOrders" resultMap="userWithOrdersMap">
    SELECT u.*, o.* FROM users u
    LEFT JOIN orders o ON u.id = o.user_id
</select>

// ✅ 批量 IN
List<User> users = userMapper.selectList(null);
List<Long> ids = users.stream().map(User::getId).collect(toList());
Map<Long, List<Order>> orderMap = orderMapper.selectByUserIds(ids)
    .stream().collect(groupingBy(Order::getUserId));

// ✅ MyBatis-Plus 的 @RelationField（自动 join）
```

### 坑 3：循环单条插入

```java
// ❌ 1000 次网络往返
for (User user : users) {
    userMapper.insert(user);
}

// ✅ MyBatis foreach 批量（1 次）
<insert id="batchInsert">
    INSERT INTO user (name, email) VALUES
    <foreach collection="list" item="user" separator=",">
        (#{user.name}, #{user.email})
    </foreach>
</insert>

// ✅ MyBatis-Plus 的 saveBatch（自动分批 1000/批）
userService.saveBatch(users);
```

### 坑 4：深分页（OFFSET 太大）

```sql
-- ❌ LIMIT 1000000, 20  扫描 100 万行
SELECT * FROM orders LIMIT 1000000, 20;

-- ✅ 游标分页（基于主键）
SELECT * FROM orders
WHERE id > #{lastId}
ORDER BY id LIMIT 20;
```

### 坑 5：SQL 注入 through MyBatis $

```java
// ❌ 动态 ORDER BY（看似安全，实则有风险）
@Select("SELECT * FROM users ORDER BY ${orderBy}")
List<User> findAll(@Param("orderBy") String orderBy);
// 如果 orderBy = "id; DROP TABLE users;" → 灾难
// 攻击：orderBy = "(SELECT CASE WHEN (SELECT 1 FROM users LIMIT 1)=1 THEN SLEEP(5) ELSE 0 END)"

// ✅ 白名单
public List<User> findAll(String orderBy) {
    // 白名单
    Set<String> allowed = Set.of("id", "user_name", "created_at");
    if (!allowed.contains(orderBy)) orderBy = "id";
    return userMapper.findAll(orderBy);
}
```

### 坑 6：忘记加分页（深分页）

```java
// ❌ 全表扫描（生产事故）
@GetMapping("/list")
public List<User> list() {
    return userMapper.selectList(null);  // 100 万行
}

// ✅ 强制分页
@GetMapping("/page")
public IPage<User> page(@RequestParam(defaultValue = "1") Integer pageNum,
                        @RequestParam(defaultValue = "10") Integer pageSize) {
    return userMapper.selectPage(new Page<>(pageNum, pageSize), null);
}
```

### 坑 7：事务边界错误

```java
// ❌ 在循环里提交事务（性能差）
@Transactional
public void batchProcess(List<User> users) {
    for (User user : users) {
        userService.save(user);  // 每条都是独立事务
    }
}

// ✅ 一个事务批量处理
@Transactional
public void batchProcess(List<User> users) {
    userService.saveBatch(users);  // 一次 commit
}

// ✅ 大批量分批处理（避免大事务）
public void batchProcess(List<User> users) {
    int batchSize = 500;
    int total = users.size();
    for (int i = 0; i < total; i += batchSize) {
        List<User> batch = users.subList(i, Math.min(i + batchSize, total));
        userService.saveBatch(batch);
    }
}
```

### 坑 8：ResultMap 与 resultType 混用

```xml
<!-- ❌ 字段映射不正确（应该用 resultMap） -->
<select id="selectById" parameterType="long" resultType="User">
    SELECT id, user_name AS userName FROM users WHERE id = #{id}
</select>
<!-- 问题：后续新增列时容易忘记加 AS -->

<!-- ✅ 用 resultMap 统一管理 -->
<resultMap id="userMap" type="User">
    <id column="id" property="id"/>
    <result column="user_name" property="userName"/>
    <!-- 其他映射 -->
</resultMap>

<select id="selectById" parameterType="long" resultMap="userMap">
    SELECT id, user_name FROM users WHERE id = #{id}
</select>
```

### 坑 9：MP 的 `selectCount` 全表扫描

```java
// ❌ 看似加了条件，实际全表扫
long count = userMapper.selectCount(null);  // SELECT COUNT(*) FROM users

// ✅ 加条件（如果有）
long count = userMapper.selectCount(
    Wrappers.<User>lambdaQuery().eq(User::getStatus, 1)
);
```

### 坑 10：动态表名 SQL 注入

```java
// ❌ 动态表名拼接（注入风险）
@Select("SELECT * FROM orders_" + tableSuffix + " WHERE id = #{id}")
User findById(String id, String tableSuffix);

// ✅ 白名单 + 强制数字
public User findById(String id, String tableSuffix) {
    // 强校验（只允许数字后缀）
    if (!tableSuffix.matches("\\d{6}")) {  // yyyyMM
        throw new IllegalArgumentException("Invalid table suffix");
    }
    return userMapper.findById(id, tableSuffix);
}
```

## 🏆 12 条最佳实践

### 1. 统一使用 Lambda 表达式（类型安全）

```java
// ✅ Lambda（推荐）
Wrappers.<User>lambdaQuery()
    .eq(User::getStatus, 1)
    .like(User::getUserName, "张")
    .list();

// ❌ 字符串字段名（编译期不检查，重构易出错）
new QueryWrapper<User>()
    .eq("status", 1)
    .like("user_name", "张")
    .list();
```

### 2. 用 IService 而不是直接调用 BaseMapper

```java
// ✅ 推荐：Service 层统一封装
public class UserServiceImpl extends ServiceImpl<UserMapper, User>
    implements UserService {
    
    public boolean createUser(UserDTO dto) {
        // ✅ 走 saveBatch（自动分批）
        return saveBatch(Collections.singletonList(toEntity(dto)));
    }
}

// ❌ 不推荐：业务层直接用 Mapper
public class UserService {
    @Autowired private UserMapper userMapper;
    
    public boolean createUser(UserDTO dto) {
        // 错失了 MP 的批量能力
        return userMapper.insert(toEntity(dto)) > 0;
    }
}
```

### 3. 用 `@Transactional(rollbackFor = Exception.class)`

```java
// ✅ 推荐：明确指定回滚异常
@Transactional(rollbackFor = Exception.class)
public void businessMethod() {
    // 只要有异常就回滚（包括 checked exception）
}

// ⚠️ 默认：只回滚 RuntimeException
@Transactional  // 没有 rollbackFor
public void riskyMethod() {
    // IOException 不会回滚！
}
```

### 4. 不在事务里做远程调用

```java
// ❌ 事务里远程调用（长事务，数据库连接占用）
@Transactional
public void processOrder(Order order) {
    orderService.save(order);
    paymentService.charge(order);  // 远程调用（3 秒）
    notificationService.send(order);  // 又一个远程调用（5 秒）
}
// 事务持续 8 秒，期间数据库连接被占用

// ✅ 拆分事务 + 异步补偿
public void processOrder(Order order) {
    orderService.save(order);  // 事务1
    
    // 异步处理（自己 final 字段注入）
    CompletableFuture.runAsync(() -> {
        paymentService.charge(order);
    });
}
```

### 5. 用 DTO 而非 Entity 直接传输

```java
// ❌ 直接用 Entity 当 API 返回值
@GetMapping("/list")
public List<User> list() {
    return userService.list();  // 返回包含 password 等敏感字段
}

// ✅ 用 DTO 隔离
@GetMapping("/list")
public List<UserDTO> list() {
    return userService.list().stream().map(this::toDTO).collect(toList());
}
```

### 6. 用 BeanUtils.copyProperties（注意坑）

```java
// ⚠️ BeanUtils 不复制集合，需要手动处理
BeanUtils.copyProperties(dto, entity);  // 复制基本字段
BeanUtils.copyProperties(dto.getOrderItems(), entity.getOrderItems());  // ❌ 不起作用

// ✅ 自己写转换方法
private User toEntity(UserDTO dto) {
    User user = new User();
    BeanUtils.copyProperties(dto, user);
    return user;
}

// 或用 MapStruct
@Mapper
public interface UserConvert {
    UserDTO toDTO(User user);
    User toEntity(UserDTO dto);
}
```

### 7. 批量操作要分批（防大事务）

```java
// ❌ 大事务
@Transactional
public void batchInsert(List<User> users) {
    userMapper.batchInsert(users);  // 100 万行，事务巨大
}

// ✅ 分批
@Transactional
public void batchInsert(List<User> users) {
    int batchSize = 1000;
    for (int i = 0; i < users.size(); i += batchSize) {
        userMapper.batchInsert(
            users.subList(i, Math.min(i + batchSize, users.size()))
        );
        // ✅ Spring 自动在方法结束 commit（也可手动）
    }
}
```

### 8. 乐观锁防并发

```java
// ✅ 库存扣减
Product p = productService.getById(1);
if (p.getStock() < orderQty) throw new RuntimeException("库存不足");
p.setStock(p.getStock() - orderQty);
productService.updateById(p);  // 自动加 WHERE version = ?

// ✅ 极端并发用原子 SQL
@Update("UPDATE products SET stock = stock - #{qty} WHERE id = #{id} AND stock >= #{qty}")
int decreaseStock(@Param("id") Long id, @Param("qty") Integer qty);
// 返回 0 说明库存不足
```

### 9. 慢查询监控

```java
@Intercepts(@Signature(type = StatementHandler.class, method = "prepare", args = {Connection.class}))
public class SlowSqlInterceptor implements Interceptor {
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return invocation.proceed();
        } finally {
            long cost = System.currentTimeMillis() - start;
            if (cost > 200) {
                // 异步记录（不阻塞 SQL）
                ThreadPoolTaskExecutor.execute(() -> logSlow(cost, getSql()));
            }
        }
    }
}
```

### 10. 不要在 MyBatis 里做业务校验

```java
// ❌ 业务逻辑放 Mapper（难维护）
@Select("SELECT * FROM users WHERE email = #{email} AND status = 1 AND deleted = 0")
User findActiveByEmail(String email);

// ✅ 业务逻辑在 Service
public User findActiveByEmail(String email) {
    User user = userMapper.findByEmail(email);  // 只查邮箱
    if (user == null) throw new NotFoundException();
    if (user.getStatus() != 1 || user.getDeleted() != 0) throw new IllegalStateException();
    return user;
}
```

### 11. 复杂动态 SQL 用 XML，不用注解

```java
// ⚠️ 注解适合简单 SQL
@Select("SELECT * FROM users WHERE status = #{status}")
User findByStatus(Integer status);

// ✅ 复杂 SQL 用 XML
<select id="search" resultType="User">
    SELECT * FROM users
    <where>
        <if test="keyword != null">AND name LIKE #{keyword}</if>
        <if test="status != null">AND status = #{status}</if>
        <if test="minAge != null">AND age >= #{minAge}</if>
        <choose>
            <when test="orderBy == 'name'">ORDER BY name</when>
            <otherwise>ORDER BY id DESC</otherwise>
        </choose>
    </where>
</select>
```

### 12. 定期 code review 和性能测试

```java
// ✅ 用 JMH 做微基准测试
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.MILLISECONDS)
public class UserMapperBenchmark {
    
    @Benchmark
    public void testSelectById(Blackhole bh) {
        bh.consume(userMapper.selectById(1L));
    }
    
    public static void main(String[] args) throws Exception {
        new Runner(opt).run();
    }
}
```

## 🚨 常见报错及解决

### 报错 1：Invalid bound statement

```
org.apache.ibatis.binding.BindingException: 
  Invalid bound statement (not found): UserMapper.selectById
```

**原因：** XML 没编译到 classpath  
**解决：**
```xml
<!-- pom.xml -->
<build>
    <resources>
        <resource>
            <directory>src/main/resources</directory>
        </resource>
    </resources>
</build>
```

### 报错 2：Table 'xxx' doesn't exist

**原因：** `@TableName` 写错了表名（MySQL 大小写敏感）  
**解决：**
```java
@TableName("users")  // 不是 `Users`（虽然 Windows 不敏感）
```

### 报错 3：Too many connections

**原因：** Hikari 连接池过大 + 长事务  
**解决：**
```yaml
hikari:
  maximum-pool-size: 20  # 不要超过 MySQL max_connections / 实例数
```

### 报错 4：Lock wait timeout exceeded

**原因：** MySQL 行锁被长事务持有  
**解决：**
```sql
-- 查看锁等待
SELECT * FROM information_schema.innodb_trx;
-- 杀长事务
KILL <trx_id>;
```

## 🎯 总结

**MyBatis 开发避坑清单：**
- ✅ 永远用 `#{param}` 而非 `${param}`
- ✅ JOIN / 批量 IN 解决 N+1
- ✅ 批量操作要分批（1000/批）
- ✅ 游标分页处理深分页
- ✅ 动态字段加白名单
- ✅ 强制分页参数
- ✅ 大事务拆分
- ✅ 用 DTO 隔离 Entity
- ✅ 严格事务边界
- ✅ 乐观锁防并发

**代码质量检查清单：**
- ✅ Entity 用 `@TableName`, `@TableId`
- ✅ 复杂查询用 XML
- ✅ 简单查询用 MP
- ✅ Lambda 表达式（类型安全）
- ✅ 事务明确 rollbackFor
- ✅ 慢查询监控
- ✅ SQL 注入防护
- ✅ 连接池合理配置

**下一步：** [⚙️ MyBatis 缓存机制](/12-mybatis/cache) — 一级/二级缓存的正确使用


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
