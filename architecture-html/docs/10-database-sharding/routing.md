---
title: 路由 / 扩容
---
# 分库分表的路由与扩容

## 1. 路由核心

```
应用 → 路由层 → 实际 shard
```

**目标**：给定 sharding key，定位到具体 shard。

## 2. 路由方式

### 2.1 客户端路由

应用代码（@Sharding-JDBC / 业务自己算）：

```java
public class OrderDao {
  public void insert(Order order) {
    int shard = (int) (order.userId % 16);
    String table = "t_order_" + shard;
    // 根据 sharding 规则路由
  }
}
```

**优**：简单，零中间件。
**缺**：语言绑定；分库规则改动需改代码 + 重发布。

### 2.2 代理层路由

```
应用 → ShardingSphere-Proxy / MyCat → 后端 shard
```

**优**：语言无关，集中管理。
**缺**：Proxy 单点 / 性能瓶颈 / 部署运维复杂。

### 2.3 数据库原生

TiDB / CockroachDB 自动分片，对应用透明。

**优**：零改造。
**缺**：迁移成本高。

## 3. 路由策略

### 3.1 取模（mod）

```java
int shard = (int) (userId % 16);
```

**优**：分布均匀。
**缺**：扩容难（4 → 8 库需要数据迁移）。

### 3.2 范围（range）

```java
if (orderId < 1000_000) shard = 0;
else if (orderId < 2000_000) shard = 1;
```

**优**：扩容简单（加新范围）。
**缺**：分布可能不均。

### 3.3 一致性 Hash

```java
int hash = (int) (userId ^ (userId >>> 16));
int node = hash & (shardCount - 1);
```

**优**：扩缩容只影响相邻节点。
**缺**：实现复杂，节点少时倾斜。

## 4. 扩容：2 步迁移

### 步骤 1：双写

```java
// 写老库 + 写新库
public void update(Order order) {
  oldDB.update(order);   // 老库
  newDB.update(order);   // 新库（异步）
}
```

### 步骤 2：迁历史数据

```sql
-- 按 ID 范围分批迁
INSERT INTO new_db.orders
SELECT * FROM old_db.orders
WHERE id BETWEEN ? AND ?;
```

```java
// 按页迁
public void migrate(int from, int to) {
  while (true) {
    var page = oldDB.paginate(from, to, 1000);
    if (page.isEmpty()) break;
    newDB.batchInsert(page);
    from += 1000;
  }
}
```

### 步骤 3：切读

```java
// 1. 优先读新库
// 2. 新库没有 → fallback 老库
public Order getOrder(Long id) {
  Order o = newDB.get(id);
  if (o == null) o = oldDB.get(id);
  return o;
}
```

### 步骤 4：切写（关老库）

```java
public void update(Order order) {
  newDB.update(order);
  // oldDB.update(order)  // 注释掉
}
```

### 步骤 5：清理老库

```sql
-- 数据一致后，老库只读 / drop table
DROP TABLE old_db.orders;
```

## 5. 双写一致性

**双写**两库不原子 → 某库失败 → 数据不一致。

**解决**：
- 异步双写 + 定时对账
- 分布式事务（XA / Seata）
- 事件驱动：写老库 → 发消息 → 消费写新库

```java
@Transactional
public void createOrder(Order order) {
  oldDB.insert(order);  // 主库
  kafkaTemplate.send("order-migration", order);  // 消息驱动迁到新库
}
```

## 6. 灰度切流

```java
// 按 user_id 范围灰度
public DataSource route(Long userId) {
  if (userId < 100_000) return newDB;     // 1% 灰度
  return oldDB;
}
```

观察 1 周 → 全量切。

## 7. 实战：Sharding-JDBC 路由

```yaml
spring:
  shardingsphere:
    rules:
      sharding:
        tables:
          t_order:
            actual-data-nodes: ds${0..3}.t_order_${0..3}
            table-strategy:
              sharding-column: order_id
              sharding-algorithm-name: hash-mod
        sharding-algorithms:
          hash-mod:
            type: MOD
            props:
              sharding-count: 16
```

## 8. 实战：扩容案例

**业务**：订单表 8 亿行，1 个 DB 性能不足
**方案**：
1. 16 → 32 分片
2. 双写（old 16 + new 16）
3. 迁历史数据
4. 切读
5. 切写
6. 清理

**关键**：
- 灰度（1% → 10% → 50% → 100%）
- 监控（延迟 / 错误率 / 慢查询）
- 回滚方案（保留老库 30 天）

## 9. 选型

| 场景 | 方案 |
|------|------|
| < 1 亿行 | 不分库，先优化 |
| 1-10 亿 | Sharding-JDBC + 取模 |
| 10-100 亿 | Sharding-Proxy + 范围分片 |
| > 100 亿 | TiDB / 分布式 SQL |
| 时间序列 | 按时间 range + 冷热分层 |

## 🔗 下一步
- [水平 / 垂直拆分](/10-database-sharding/strategy)
- [分布式 ID](/10-database-sharding/id)
