---
title: ShardingSphere 实战
---

# 🌊 ShardingSphere 实战

> Apache ShardingSphere 是国产最优秀的分库分表中间件，提供数据分片、读写分离、分布式事务等一站式解决方案。

## 🎯 ShardingSphere 是什么？

```
┌─────────────────────────────────────┐
│           Application                │
└──────────────┬──────────────────────┘
               │ JDBC / Proxy
┌──────────────▼──────────────────────┐
│      ShardingSphere-JDBC / Proxy    │
│  ┌──────────────────────────────┐   │
│  │  数据分片                     │   │
│  │  读写分离                     │   │
│  │  分布式事务                   │   │
│  │  数据加密                     │   │
│  │  影子库                       │   │
│  └──────────────────────────────┘   │
└──────────────┬──────────────────────┘
               │ JDBC
┌──────────────▼──────────────────────┐
│         Multiple MySQL              │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐│
│  │ ds0  │ │ ds1  │ │ ds2  │ │ ds3  ││
│  └──────┘ └──────┘ └──────┘ └──────┘│
└─────────────────────────────────────┘
```

## 📦 ShardingSphere 两种模式

### 1. ShardingSphere-JDBC（嵌入式）

```
应用进程内集成，性能最好
┌────────────────────────────┐
│  Application                │
│  ┌──────────────────────┐  │
│  │  ShardingSphere-JDBC  │  │
│  │  (jar 包，进程内)      │  │
│  └──────────────────────┘  │
└────────────┬───────────────┘
             │ JDBC
       ┌─────▼─────┐
       │   MySQL   │
       └───────────┘
```

### 2. ShardingSphere-Proxy（代理）

```
独立部署的服务，对应用透明
┌──────────┐       ┌──────────────────┐       ┌───────────┐
│   App    │ ────→ │ ShardingSphere-Proxy│ ────→ │   MySQL   │
└──────────┘       └──────────────────┘       └───────────┘
                  (独立部署，像访问 MySQL 一样)
```

## 🚀 ShardingSphere-JDBC 实战

### 1. 添加依赖

```xml
<!-- Spring Boot Starter -->
<dependency>
  <groupId>org.apache.shardingsphere</groupId>
  <artifactId>shardingsphere-jdbc-core-spring-boot-starter</artifactId>
  <version>5.4.1</version>
</dependency>
```

### 2. 配置文件

```yaml
# application.yml
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
      # ... ds2, ds3 同上

    # 分片规则
    rules:
      sharding:
        # 表的分片规则
        tables:
          orders:
            actual-data-nodes: ds$->{0..3}.orders_$->{0..3}
            # 真实表：ds0.orders_0, ds0.orders_1, ...
            table-strategy:
              standard:
                # 分片列
                sharding-column: user_id
                # 分片算法
                sharding-algorithm-name: orders_inline

        # 库的分布
        binding-tables:
          - orders

        # 广播表（每个库都有一份）
        broadcast-tables:
          - config_table

    # 分片算法
    sharding-algorithms:
      orders_inline:
        type: INLINE
        props:
          algorithm-expression: ds$->{user_id % 4}.orders_$->{(user_id / 4) % 4}
```

### 3. 使用（应用代码无需改）

```java
// 应用代码和普通 JDBC / MyBatis 完全一样
@Repository
public interface OrderMapper {
    @Insert("INSERT INTO orders (id, user_id, amount) VALUES (#{id}, #{userId}, #{amount})")
    void insert(Order order);

    @Select("SELECT * FROM orders WHERE user_id = #{userId}")
    List<Order> selectByUserId(Long userId);
}

// ShardingSphere 自动：
// 1. 解析 SQL
// 2. 根据 user_id 计算分片（库 + 表）
// 3. 路由到正确的物理表
// 4. 合并结果
```

## 📊 分片算法详解

### 1. INLINE 算法（最常用）

```yaml
# 取模分片
algorithm-expression: t_order_$->{order_id % 8}

# 范围分片
algorithm-expression: t_order_$->{order_id / 1000}

# 复合表达式（多列）
algorithm-expression: ds_$->{user_id % 4}.t_order_$->{order_id % 8}
```

### 2. 自定义算法

```java
// 实现 StandardShardingAlgorithm 接口
public class MyShardingAlgorithm implements StandardShardingAlgorithm<Long> {

    @Override
    public String doSharding(Collection<String> availableTargetNames,
                             PreciseShardingValue<Long> shardingValue) {
        // 自定义分片逻辑
        long value = shardingValue.getValue();
        int suffix = (int) (value % availableTargetNames.size());
        return availableTargetNames.stream()
            .filter(name -> name.endsWith("_" + suffix))
            .findFirst().orElse(null);
    }
}
```

```yaml
sharding-algorithms:
  custom_alg:
    type: CLASS_BASED
    props:
      strategy: standard
      algorithmClassName: com.example.MyShardingAlgorithm
```

## 🔧 高级功能

### 1. 读写分离

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
              write-data-source-name: ds-master
              read-data-source-names: ds-slave-0,ds-slave-1
            load-balancers:
              type: ROUND_ROBIN  # 轮询
```

### 2. 数据加密

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

### 3. 分布式事务（SEATA）

```java
// 用 @GlobalTransactional 注解
@GlobalTransactional
public void createOrder(OrderDTO dto) {
    // 1. 写订单库（分片 0）
    orderMapper.insert(dto);

    // 2. 写库存库（分片 1）
    inventoryMapper.decrease(dto);

    // 3. 写账户库（分片 2）
    accountMapper.debit(dto);

    // SEATA 保证要么都成功，要么都回滚
}
```

### 4. 绑定表（避免笛卡尔积）

```yaml
# 关联查询的表，绑定到同一个分片
spring:
  shardingsphere:
    rules:
      sharding:
        binding-tables:
          - orders, order_items  # orders 和 order_items 必须在同一分片
```

### 5. 广播表（每个库都一份）

```yaml
# 配置表、商品分类等小表，每个分片都存一份
spring:
  shardingsphere:
    rules:
      sharding:
        broadcast-tables:
          - config_table
          - dict_table
```

## 📈 性能数据

```
单库 MySQL：
- QPS：~5000
- 写 TPS：~2000

ShardingSphere-JDBC（4 库 8 表 = 32 分片）：
- QPS：~100000（20x）
- 写 TPS：~40000（20x）
- 延迟增加：< 1ms（JDBC 进程内性能损耗极小）
```

## 🛠️ 运维管理

### 1. 弹性扩容

```sql
-- ShardingSphere 提供弹性扩容工具
-- 4 库 8 表 → 4 库 16 表（数据迁移）

-- 步骤：
-- 1. 创建新分片（ds0.orders_8 ~ ds3.orders_15）
-- 2. 数据迁移（按分片规则重新分布）
-- 3. 修改分片规则
-- 4. 灰度切流
```

### 2. 数据一致性校验

```sql
-- ShardingSphere 提供校验工具
-- 验证分片数据是否一致

-- 用 pt-table-checksum 校验
pt-table-checksum --host=master --databases=order_db_0
```

### 3. 慢查询定位

```yaml
# 开启慢查询日志
spring:
  shardingsphere:
    props:
      sql-show: true  # 打印实际执行的 SQL（包含分片路由）
```

```bash
# 日志输出示例
Actual SQL: ds0 ::: SELECT * FROM orders_0 WHERE user_id = 100
Actual SQL: ds1 ::: SELECT * FROM orders_1 WHERE user_id = 100
# 可以看到每个分片实际执行的 SQL
```

## 🎯 总结

**ShardingSphere 核心特性：**
- ✅ 数据分片（水平/垂直）
- ✅ 读写分离
- ✅ 分布式事务
- ✅ 数据加密
- ✅ 弹性扩容

**两种模式选择：**
- JDBC（嵌入式）：性能好，适合 Java 应用
- Proxy（代理）：对应用透明，适合多语言

**分片键选择：**
- 高频查询字段
- 业务核心字段
- 数据分布均匀

**下一步：** [🐱 MyCat 中间件](../10-sharding/mycat) — 老牌分库分表方案