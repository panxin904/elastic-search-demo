---
title: 分布式存储
---

# 📊 分布式存储

> 当单库**扛不住**写入或查询时，需要把数据**拆分到多个节点**存储。

## 🎯 为什么需要分布式存储？

| 单机 DB 瓶颈 | 量化指标 |
|---|---|
| **连接数** | MySQL 默认 151，最大 16384 |
| **QPS** | 单机 5000 ~ 30000 |
| **存储容量** | 单机磁盘有限（TB 级）|
| **主从延迟** | 读写分离后从库延迟秒级 |

**典型案例：** 淘宝双 11、12306 春运 → 单机无法承载

## 📐 拆分策略

### 1. 垂直拆分（按业务）

```
原库：电商系统
  ┌──────────────────────────────────┐
  │ 用户表、订单表、商品表、库存表、     │
  │ 支付表、评论表、活动表、营销表...   │
  └──────────────────────────────────┘

拆分后：
  用户库（user_db）      订单库（order_db）
  ┌─────────────┐       ┌─────────────┐
  │ users       │       │ orders      │
  │ addresses   │       │ order_items │
  └─────────────┘       └─────────────┘

  商品库（product_db）    支付库（pay_db）
  ┌─────────────┐       ┌─────────────┐
  │ products    │       │ payments    │
  │ categories  │       │ refunds     │
  └─────────────┘       └─────────────┘
```

| 优点 | 缺点 |
|---|---|
| 简单清晰 | 单表仍可能过大 |
| 业务解耦 | 跨库 JOIN 难 |
| 不同库独立优化 | 分布式事务 |

### 2. 水平拆分（分库分表 Sharding）

**同一张表的数据拆分到多个数据库 / 表**

```
原表：orders（单表 10 亿行）

按 user_id 分 4 库 8 表：
  order_db_0           order_db_1
    orders_0  (uid%8=0)   orders_4  (uid%8=4)
    orders_1  (uid%8=1)   orders_5  (uid%8=5)
    orders_2  (uid%8=2)   orders_6  (uid%8=6)
    orders_3  (uid%8=3)   orders_7  (uid%8=7)
  order_db_2           order_db_3
    ...
```

## 🔑 分片键（Sharding Key）选择

| 选择标准 | 示例 |
|---|---|
| **高频查询字段** | 用户系统按 user_id |
| **均匀分布** | 不要用性别 / 省份等低基数字段 |
| **稳定性** | 不要用会频繁修改的字段 |

**分片算法：**

| 算法 | 原理 | 优点 | 缺点 |
|---|---|---|---|
| **取模** | `hash(key) % N` | 均匀 | 扩容需数据迁移 |
| **范围** | 按 ID / 时间分片 | 范围查询快 | 可能热点 |
| **一致性 Hash** | 哈希环 + 虚拟节点 | 扩容迁移少 | 实现复杂 |
| **地理** | 按地域分库 | 减少延迟 | 跨地域复杂 |

**取模分片的扩容难题：**

```
原：2 库 → uid % 2
新：4 库 → uid % 4
→ 75% 的数据需要迁移
```

**一致性 Hash：**

```
哈希环：0 → 2^32

       DB0
        ↑
   /    │    \
  /     │     \
 0 ──────────── 2^32
  \     │     /
   \    │    /
       DB1
       
新增 DB2：仅 DB0 → DB2 之间的数据迁移
```

## 🛠️ 分库分表中间件

### 客户端代理（JDBC 层）

| 中间件 | 语言 | 特点 |
|---|---|---|
| **ShardingSphere-JDBC** | Java | Apache 顶级，轻量 |
| **TSharding** | Java | 当当网 |
| **Ctrip DAL** | Java | 携程 |

**ShardingSphere-JDBC 集成示例：**

```yaml
# application.yml
spring:
  shardingsphere:
    datasource:
      names: ds0,ds1
      ds0:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://127.0.0.1:3306/order_db_0
      ds1:
        jdbc-url: jdbc:mysql://127.0.0.1:3306/order_db_1
    rules:
      sharding:
        tables:
          orders:
            actual-data-nodes: ds$->{0..1}.orders_$->{0..3}
            database-strategy:
              standard:
                sharding-column: user_id
                sharding-algorithm-name: db-mod
            table-strategy:
              standard:
                sharding-column: order_id
                sharding-algorithm-name: table-mod
```

### 代理层（独立部署）

| 中间件 | 特点 |
|---|---|
| **ShardingSphere-Proxy** | Apache，MySQL 协议兼容 |
| **MyCat** | 阿里，Cobar 演化 |
| **Cobar** | 阿里经典（已停止维护）|
| **MaxScale** | MariaDB |
| **ProxySQL** | MySQL |

### 内存数据库（NoSQL）

| 数据库 | 类型 | 特点 |
|---|---|---|
| **Redis** | KV | 高性能缓存 |
| **MongoDB** | 文档 | 灵活的 schema |
| **HBase** | 列式 | 海量数据（PB 级）|
| **Cassandra** | 列式 | AP 分布式 |
| **TiDB** | HTAP | 兼容 MySQL |

## 📐 数据迁移方案

### 1. 双写方案（推荐）

```
阶段 1：新旧库并行写入
  写入 → ┬→ 旧库
         └→ 新库（按新规则）

阶段 2：历史数据迁移
  全量：旧库 → DataX → 新库
  增量：监听 Binlog → 新库

阶段 3：切读
  读取：新库
  写入：双写（验证）

阶段 4：收尾
  写入：新库
  停止旧库写入
```

### 2. 停机迁移（不推荐）

- 简单但业务受损
- 仅适合小型项目

### 3. Binlog 增量同步

工具：
- **Canal**（阿里）
- **Debezium**
- **Maxwell**

```
MySQL → Binlog → Canal → Kafka → 新库消费者 → INSERT
```

## ⚠️ 分库分表常见问题

### 1. 跨库 JOIN

**原 SQL：**
```sql
SELECT * FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.user_id = 123;
```

**问题：** orders 在 ds0，users 在 user_db（独立库）

**解决：**
- **全局表**（每个库都冗余一份）
- **ER 表**（绑定子表到父表所在库）
- **应用层 JOIN**（查询两次，内存合并）
- **数据冗余**（订单表冗余用户名）

### 2. 跨库分页

```sql
SELECT * FROM orders ORDER BY id LIMIT 100000, 20;
```

**每个分片查一遍** → 内存合并 → 重新排序分页

### 3. 跨库事务

**前文所述分布式事务方案**

### 4. 扩容（2 库 → 4 库）

**难点：** hash(oldKey) % 2 ≠ hash(oldKey) % 4

**方案：**
- **平滑扩容**：先双写新旧库，再迁移数据，最后切读
- **一致性 Hash**：扩容只需迁移少量数据
- **预分区**：开始就分 32 库 32 表，未来逻辑分

### 5. 主键避重

**分库后不能用 DB 自增**

**解决：** 分布式 ID（Snowflake / 号段 / UUID）

## 📊 读写分离

```
客户端 → 写 → Master（主库）
                  ↓ Binlog 同步
       ← 读 ← Slave0（从库）
       ← 读 ← Slave1（从库）
       ← 读 ← Slave2（从库）
```

| 实现 | 工具 |
|---|---|
| **应用层** | Spring 抽象路由 + ThreadLocal |
| **中间件** | MyCat / ShardingSphere-Proxy / ProxySQL |
| **客户端** | MyBatis 拦截器 |

**主从延迟问题：**
- 写后立即读可能读不到（从库延迟）
- **解决：** 读主库 / 强制走主 / 缓存兜底

## 📊 分库分表最佳实践

| 项目 | 建议 |
|---|---|
| **分片数** | 初期按 2 年增长预估（16 库 64 表）|
| **分片键** | 高频查询字段，且基数大 |
| **避免热点** | 不要按状态分（已支付订单占比 95%）|
| **预留扩容** | 一致性 Hash / 逻辑分片 |
| **全局唯一 ID** | Snowflake / Leaf |
| **数据迁移** | 双写 + Binlog |

## 🎓 面试高频问题

| 问题 | 关键点 |
|---|---|
| 分库分表方案？| 垂直拆分（按业务）+ 水平拆分（按字段）|
| 分片算法？| 取模 / 范围 / 一致性 Hash |
| 扩容方案？| 双写 + Binlog 同步 + 切读 |
| 跨库 JOIN 解决？| 全局表 / ER 表 / 应用层 JOIN |
| 跨库分页？| 查所有分片 → 内存合并 → 再分页 |
| 读写分离延迟？| 读主库 / 强制走主 / 业务兜底 |

---

- 上一章：[💬 分布式消息](/07-distributed/distributed-mq)
- 下一章：[🔄 分布式协调](/07-distributed/distributed-coordination)