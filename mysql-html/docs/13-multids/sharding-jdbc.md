---
title: ShardingSphere-JDBC 实战
---

# 🌊 ShardingSphere-JDBC 分库分表实战

> Apache ShardingSphere 是**国产最优秀的分库分表中间件**，提供数据分片、读写分离、分布式事务一站式解决方案。

## 🎯 ShardingSphere 是什么？

```
┌─────────────────────────────────────┐
│         Application                  │
└─────────────┬───────────────────────┘
               │ JDBC
┌─────────────▼───────────────────────┐
│     ShardingSphere-JDBC              │
│  ┌──────────────────────────────┐   │
│  │  数据分片                     │   │
│  │  读写分离                     │   │
│  │  分布式事务                   │   │
│  │  数据加密                     │   │
│  │  影子库压测                   │   │
│  └──────────────────────────────┘   │
└─────────────┬───────────────────────┘
               │ JDBC
┌─────────────▼───────────────────────┐
│          Multiple MySQL              │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐│
│  │ ds0  │ │ ds1  │ │ ds2  │ │ ds3  ││
│  └──────┘ └──────┘ └──────┘ └──────┘│
└─────────────────────────────────────┘
```

## 🚀 快速开始（Spring Boot 3）

### 1. 添加依赖

```xml
<dependency>
    <groupId>org.apache.shardingsphere</groupId>
    <artifactId>shardingsphere-jdbc-core-spring-boot-starter</artifactId>
    <version>5.4.1</version>
</dependency>
```

### 2. application.yml 配置

```yaml
spring:
  shardingsphere:
    # 数据源配置
    datasource:
      names: ds0,ds1,ds2,ds3
      ds0:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://mysql-0:3306/order_db
        username: app_user
        password: xxx
      ds1:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://mysql-1:3306/order_db
        username: app_user
        password: xxx
      ds2:
        jdbc-url: jdbc:mysql://mysql-2:3306/order_db
        username: app_user
        password: xxx
      ds3:
        jdbc-url: jdbc:mysql://mysql-3:3306/order_db
        username: app_user
        password: xxx
    
    # 分片规则
    rules:
      sharding:
        # 表分片规则
        tables:
          orders:
            # 实际数据节点：ds{0..3}.orders_{0..3}  (16 个分片)
            actual-data-nodes: ds$->{0..3}.orders_$->{0..3}
            table-strategy:
              standard:
                sharding-column: user_id
                sharding-algorithm-name: orders_inline
            key-generate-strategy:
              snowflake:
                column: id
                key-generator-name: snowflake
        
        # 库分片规则
        binding-tables:
          - orders, order_items  # 绑定表，相同分片键
        
        # 广播表（小表，每个分片都有）
        broadcast-tables:
          - config_table
        
        # 分片算法
        sharding-algorithms:
          orders_inline:
            type: INLINE
            props:
              # 复合表达式：库 + 表
              algorithm-expression: ds$->{user_id % 4}.orders_$->{(user_id / 4) % 4}
        
        # 分布式 ID
        key-generators:
          snowflake:
            type: SNOWFLAKE
            props:
              worker-id: 1
```

### 3. 业务代码（无需改！）

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    public boolean createOrder(Order order) {
        // ✅ 应用代码完全无感
        // ShardingSphere 自动根据 user_id 路由到正确的库和表
        return orderMapper.insert(order) > 0;
    }
    
    public Order getById(Long orderId) {
        return orderMapper.selectById(orderId);
    }
    
    public List<Order> getByUserId(Long userId) {
        // 走单分片（按 user_id 路由）
        return orderMapper.selectList(
            Wrappers.<Order>lambdaQuery().eq(Order::getUserId, userId)
        );
    }
    
    // 全表扫描：性能差（不推荐）
    public List<Order> getAllOrders() {
        return orderMapper.selectList(null);
        // SQL: 实际会广播到所有分片，合并结果
    }
}
```

## 📊 核心概念详解

### 1. 数据分片策略

```yaml
# 标准分片：精确分片键 = 分片
sharding-column: user_id

# 复合分片：多个分片键
sharding-columns: user_id,order_id

# 范围分片
sharding-algorithm-name: range_alg
```

### 2. 分片算法

```yaml
# 行表达式分片（最常用）
type: INLINE
algorithm-expression: ds$->{user_id % 4}

# 取模分片
type: MOD
sharding-count: 4

# 哈希取模分片
type: HASH_MOD
sharding-count: 4

# 范围分片
type: RANGE

# 自定义分片
type: CLASS_BASED
props:
  strategy: standard
  algorithmClassName: com.example.MyShardingAlgorithm
```

### 3. 绑定表（避免笛卡尔积）

```yaml
# orders 和 order_items 必须在同一分片
binding-tables:
  - orders, order_items
```

**自动效果：**
```sql
-- 没有绑定表
SELECT * FROM orders o JOIN order_items i ON o.id = i.order_id;
-- 实际执行：4 × 4 = 16 个 JOIN

-- 绑定表后
-- 实际执行：4 个 JOIN（性能提升 4 倍）
```

### 4. 广播表（小表全局同步）

```yaml
broadcast-tables:
  - config_table
  - sys_dict
```

**适用：**
- 配置表（每分片都存一份）
- 字典表（商品分类、地区）
- 系统表

**自动效果：**
```sql
-- 写入
UPDATE config_table SET value = 'new' WHERE key = 'site_name';
-- 实际：广播到所有分片

-- 读取
SELECT * FROM config_table WHERE key = 'site_name';
-- 实际：随机选一个分片读取
```

## 📚 进阶：读写分离 + 分库分表

```yaml
spring:
  shardingsphere:
    rules:
      readwrite-splitting:
        data-sources:
          # 主库
          write-db:
            type: Static
            props:
              write-data-source-name: master
              read-data-source-names: slave1,slave2
            load-balancers:
              type: ROUND_ROBIN  # 轮询负载均衡
      
      sharding:
        # 分片规则
        tables:
          orders:
            actual-data-nodes: ds$->{0..3}.orders_$->{0..3}
            table-strategy:
              standard:
                sharding-column: user_id
                sharding-algorithm-name: orders_inline
```

## 🎯 实战：分库分表完整示例

### 案例：订单系统

**需求：**
- 订单表数据量大（> 1 亿行）
- 按 user_id 分库分表
- order_items 与 orders 绑定
- 字典表全局共享

**分片设计：**
```
4 个库 × 4 张表 = 16 个分片
单分片数据：< 5000 万行

user_id 路由：
- 库：user_id % 4
- 表：(user_id / 4) % 4
```

**配置：**
```yaml
sharding-algorithms:
  orders_inline:
    type: INLINE
    props:
      algorithm-expression: ds$->{user_id % 4}.orders_$->{(user_id / 4) % 4}
```

**实际数据分布：**
- user_id=1: ds0.orders_0（因为 1%4=0, (1/4)%4=0）
- user_id=4: ds0.orders_1（因为 4%4=0, (4/4)%4=1）
- user_id=5: ds1.orders_1（因为 5%4=1, (5/4)%4=1）

## 🔧 高级特性

### 1. 分布式 ID

```yaml
# Snowflake 算法
key-generators:
  snowflake:
    type: SNOWFLAKE
    props:
      worker-id: 1
      max-vibration-offset: 1
      max-tolerate-time-difference-milliseconds: 10

# 表配置
key-generate-strategy:
  snowflake:
    column: id
    key-generator-name: snowflake
```

```java
// 插入时自动生成 ID
orderMapper.insert(order);
// 生成的 ID 是全局唯一的雪花 ID
```

### 2. 分布式序列

```yaml
key-generators:
  db_sequence:
    type: SNOWFLAKE  # 或自定义
    props:
      max-tolerate-time-difference-milliseconds: 1000

# 序列定义
sequences:
  order_seq:
    type: SNOWFLAKE
    props:
      increment: 1
```

### 3. 数据脱敏

```yaml
spring:
  shardingsphere:
    rules:
      encrypt:
        tables:
          user:
            columns:
              - name: phone
                cipher-column: encrypted_phone
                encryptor: aes_encryptor
              - name: id_card
                cipher-column: encrypted_id_card
                encryptor: aes_encryptor
    
    encryptors:
      aes_encryptor:
        type: AES
        props:
          aes-key-value: 1234567890abcdef
```

**自动效果：**
```sql
-- 插入
INSERT INTO user (phone, id_card) VALUES ('13800138000', '110101199001011234');
-- 实际：自动加密后写入 encrypted_phone / encrypted_id_card

-- 读取
SELECT * FROM user WHERE id = 1;
-- 实际：自动解密，显示原始数据
```

### 4. 影子库（压测用）

```yaml
spring:
  shardingsphere:
    rules:
      shadow:
        data-sources:
          shadow-data-source:
            production-data-source-name: ds0
            shadow-data-source-name: ds0_shadow
        tables:
          orders:
            data-source-names: ds0,ds0_shadow
            shadow-data-source-names: ds0_shadow
            shadow-algorithm-names: simple-hint-algorithm
```

**效果：**
```java
// 正常请求：走 ds0（生产）
// 带 hint 的请求：走 ds0_shadow（压测）
HintManager hintManager = HintManager.getInstance();
hintManager.setDatabaseShardingValue("shadow");
try {
    // 这次操作会路由到 shadow 库
    orderMapper.insert(order);
} finally {
    hintManager.close();
}
```

## 🛠️ 常见问题

### 问题 1：跨分片 JOIN

```java
// ❌ 跨分片 JOIN（性能差）
SELECT * FROM orders o JOIN users u ON o.user_id = u.id;
// 实际：16 个分片两两 JOIN

// ✅ 绑定表（必须在同一分片）
binding-tables:
  - orders, order_items  # OK

// ❌ 跨表跨分片（拆查询）
```

### 问题 2：分页查询

```java
// ❌ 全分片扫描 + 内存排序
SELECT * FROM orders ORDER BY id LIMIT 20;
// 实际：从 16 个分片各查 20 条，合并后排序取 20

// ✅ 用 ES / ShardingSphere 5.x 的归并查询
// ShardingSphere 5.x 支持 ORDER BY + LIMIT（需要配置文件）
```

### 问题 3：事务

```java
// ❌ 跨分片事务（默认不支持）
@Transactional
public void createOrder(Order order, OrderItem item) {
    orderMapper.insert(order);  // 分片 1
    itemMapper.insert(item);     // 同一个分片（绑定表）→ OK
}

// ✅ 跨分片事务用 Seata
// 详见 [🔄 分布式事务](/13-multids/transaction)
```

## 🎯 总结

**ShardingSphere 选型：**
- ✅ **分库分表 + 事务**：ShardingSphere-JDBC
- ✅ **高性能 + 高可用**：ShardingSphere-Proxy
- ✅ **从 Sharding-JDBC 迁移**：平滑升级

**配置原则：**
- ✅ 单分片数据 < 5000 万行
- ✅ 单分片大小 < 500 GB
- ✅ 分片数 = 2^N（便于扩容）
- ✅ 绑定表一定要声明
- ✅ 字典表用广播表

**性能优化：**
- ✅ 复合索引覆盖分片键
- ✅ 绑定表避免笛卡尔积
- ✅ 减少跨分片查询
- ✅ 业务上避免不带分片键的查询

**下一步：** [🔀 分片策略与扩容](/13-multids/sharding-strategy) — 分片键选择 / 扩容方案


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
