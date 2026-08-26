---
title: 读写分离实战
---

# 📖 MySQL 读写分离实战

> 主从复制最常见的应用就是读写分离。通过将读流量分散到从库，大幅提升系统的读吞吐能力。

## 🎯 为什么需要读写分离？

```
单库架构的问题：

┌──────────┐
│  MySQL   │  ← 所有读写都在这里
│          │  ← 高并发下 CPU / IO / 锁 压力大
└──────────┘
     ↑
     │ 100% 流量
     │
  ┌─────────┐
  │  App    │
  └─────────┘
```

```
读写分离后：

┌──────────┐  ← 写入（INSERT/UPDATE/DELETE）
│  Master  │
└──────────┘
     │
     │ 复制
     ▼
┌──────────┐  ← 读（SELECT）
│  Slave 1 │
├──────────┤
│  Slave 2 │
├──────────┤
│  Slave 3 │
└──────────┘
     ↑
     │ 70-80% 流量
     │
  ┌─────────┐
  │  App    │
  └─────────┘
```

**收益：**
- 读能力线性扩展（1 主 3 从 = 3 倍读能力）
- 写不影响读（读写分离）
- 减少主库压力

## ⚙️ 读写分离的实现方式

### 方式 1：应用层实现（最常用）

```java
// 1. 配置多个数据源
@Configuration
public class DataSourceConfig {

    @Bean
    @Primary
    public DataSource masterDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:mysql://master:3306/mydb")
            .username("app_user")
            .password("xxx")
            .build();
    }

    @Bean
    public DataSource slaveDataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:mysql://slave1:3306/mydb")
            .username("app_user")
            .password("xxx")
            .build();
    }

    // 多个从库（负载均衡）
    @Bean
    public DataSource slave2DataSource() {
        return DataSourceBuilder.create()
            .url("jdbc:mysql://slave2:3306/mydb")
            .username("app_user")
            .password("xxx")
            .build();
    }
}
```

```java
// 2. 动态数据源路由
public class DynamicDataSource extends AbstractRoutingDataSource {
    @Override
    protected Object determineCurrentLookupKey() {
        return DataSourceContext.getDataSourceType();  // "master" / "slave"
    }
}

// 3. 使用 ThreadLocal 标记当前用哪个数据源
public class DataSourceContext {
    private static final ThreadLocal<String> CONTEXT = new ThreadLocal<>();
    public static void setDataSourceType(String type) { CONTEXT.set(type); }
    public static String getDataSourceType() { return CONTEXT.get(); }
    public static void clear() { CONTEXT.remove(); }
}
```

```java
// 4. 用 AOP 或注解切换数据源
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface ReadOnly {
    // 标记该方法走从库
}

// 切面
@Aspect
@Component
public class DataSourceAspect {
    @Before("@annotation(readOnly)")
    public void setSlave(readOnly readOnly) {
        DataSourceContext.setDataSourceType("slave");
    }

    @After("@annotation(readOnly)")
    public void clearSlave(readOnly readOnly) {
        DataSourceContext.clear();
    }
}
```

```java
// 5. 使用示例
@Service
public class OrderService {
    // 默认读主库
    public void createOrder(OrderDTO dto) {
        orderMapper.insert(dto);
    }

    // 显式读从库
    @ReadOnly
    public List<Order> listOrders(Long userId) {
        return orderMapper.selectByUserId(userId);
    }
}
```

### 方式 2：使用中间件（推荐生产环境）

#### ProxySQL

```sql
-- ProxySQL 配置读写分离
INSERT INTO mysql_servers (hostgroup_id, hostname, port) VALUES
  (0, 'master', 3306),
  (1, 'slave1', 3306),
  (1, 'slave2', 3306),
  (1, 'slave3', 3306);

-- 写操作 → hostgroup 0（主库）
INSERT INTO mysql_query_rules (rule_id, active, match_digest, destination_hostgroup) VALUES
  (1, 1, '^SELECT.*FOR UPDATE$', 0),
  (2, 1, '^SELECT', 1);  -- 其他 SELECT → 从库
```

#### MyCat / ShardingSphere

```yaml
# application.yml（Spring Boot + ShardingSphere）
spring:
  shardingsphere:
    datasource:
      names: master, slave0
      master:
        url: jdbc:mysql://master:3306/mydb
      slave0:
        url: jdbc:mysql://slave:3306/mydb
    rules:
      readwrite-splitting:
        data-sources:
          prds:
            static-strategies:
              read-data-source-names: slave0
              write-data-source-names: master
```

## 🎯 读写分离的关键问题

### 问题 1：主从延迟导致读到旧数据

```sql
-- T1: 用户刚下订单（写入主库）
INSERT INTO orders (id, user_id, status) VALUES (1, 100, 'pending');
-- binlog 还没传到从库

-- T2: 用户立即查询订单（从从库读）
SELECT * FROM orders WHERE id = 1;
-- ❌ 读不到（从库还没同步）
```

**解决方案：**

```java
// 方案 A：强制读主库（关键业务）
@Service
public class OrderService {
    @Transactional
    public Order getOrderFresh(Long orderId) {
        // 关键路径：强制读主库
        return orderMapper.selectById(orderId);
    }
}

// 方案 B：等待延迟追上
public Order getOrderAfterSync(Long orderId) {
    // 重试直到读到
    for (int i = 0; i < 30; i++) {
        Order order = orderMapper.selectById(orderId);
        if (order != null) return order;
        Thread.sleep(100);
    }
    throw new RuntimeException("从库延迟过大");
}

// 方案 C：读不到时 fallback 到主库
public Order getOrderWithFallback(Long orderId) {
    try {
        // 先试从库
        Order order = slaveOrderMapper.selectById(orderId);
        if (order != null) return order;
    } catch (Exception e) {
        // 从库读不到，从主库读
        log.warn("从库读不到，fallback 到主库", e);
    }
    return masterOrderMapper.selectById(orderId);
}
```

### 问题 2：主从切换时数据丢失

```sql
-- 异步复制下，主库宕机时可能丢数据
-- 解决：用半同步复制
SET GLOBAL rpl_semi_sync_master_enabled = ON;
SET GLOBAL rpl_semi_sync_master_wait_for_slave_count = 1;
```

### 问题 3：多个从库如何分配读流量？

```java
// 方案 A：随机分配
public DataSource getRandomSlave(List<DataSource> slaves) {
    int idx = ThreadLocalRandom.current().nextInt(slaves.size());
    return slaves.get(idx);
}

// 方案 B：权重分配（从库性能不同）
// Slave1: 4 权重, Slave2: 2 权重, Slave3: 1 权重

// 方案 C：延迟优先（选延迟最低的从库）
// 通过 SHOW SLAVE STATUS 实时获取延迟

// 方案 D：连接池（最小连接数优先）
```

## 📊 读写分离的最佳实践

### 1. 强制读主库的场景

```java
// ✅ 写入后立即读取
public void createOrder(OrderDTO dto) {
    Long orderId = orderMapper.insert(dto);  // 写主库
    Order order = orderMapper.selectById(orderId);  // 强制读主库
}

// ✅ 金融场景（不能读到旧数据）
public BigDecimal getAccountBalance(Long userId) {
    return accountMapper.selectBalance(userId);  // 强制读主库
}

// ✅ 库存扣减
public boolean decreaseStock(Long productId, int quantity) {
    // 库存敏感，必须读主库
    int current = stockMapper.selectStock(productId);
    if (current < quantity) return false;
    return stockMapper.updateStock(productId, current - quantity) > 0;
}
```

### 2. 读从库的场景

```java
// ✅ 列表查询（允许最终一致性）
public List<Order> listOrders(Long userId) {
    return orderMapper.selectByUserId(userId);  // 读从库
}

// ✅ 报表分析（实时性要求低）
public List<OrderStats> dailyStats() {
    return orderMapper.selectDailyStats();  // 读从库
}

// ✅ 搜索查询（性能优先）
public List<Product> searchProducts(String keyword) {
    return productMapper.searchByName(keyword);  // 读从库
}
```

### 3. 从库健康检查

```java
@Component
public class SlaveHealthChecker {

    @Scheduled(fixedRate = 5000)  // 每 5 秒检查
    public void checkHealth() {
        for (DataSource slave : slaves) {
            try {
                long delay = getSlaveDelay(slave);
                if (delay > 60) {  // 延迟超过 60 秒
                    log.warn("从库 {} 延迟 {} 秒，标记为不健康", slave, delay);
                    // 从负载均衡池中移除
                    healthySlaves.remove(slave);
                } else {
                    healthySlaves.add(slave);
                }
            } catch (Exception e) {
                log.error("从库 {} 不健康", slave, e);
                healthySlaves.remove(slave);
            }
        }
    }
}
```

## 📈 性能提升数据

```
典型场景：电商网站

优化前：
- 单库 MySQL
- QPS 上限：~5000
- 读延迟：10ms
- 写延迟：20ms

读写分离后（1 主 3 从）：
- 写 QPS：~2000
- 读 QPS：~15000（每从库 5000）
- 读延迟：8ms
- 写延迟：15ms
```

## 🎯 总结

**读写分离核心：**
- ✅ 写主库，读从库
- ✅ 应用层或中间件实现
- ✅ 强制读主库处理关键路径
- ✅ 监控从库延迟

**中间件选择：**
- 简单场景：应用层（Spring AbstractRoutingDataSource）
- 生产环境：ProxySQL / MyCat / ShardingSphere

**最佳实践：**
- 延迟敏感业务：强制读主库
- 报表/列表：读从库
- 从库故障：自动摘除 + 主库 fallback

**下一步：** [🏗️ MHA 故障切换](../07-ha/mha) — 主库宕机后如何自动切换


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
