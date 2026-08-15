---
title: 分库分表策略
---
# 分库分表策略

## 1. 为什么分库分表

```
单库单表：
  ✅ 简单（事务、关联查询）
  ❌ 单机性能瓶颈（CPU / 内存 / IO / 网络）
  ❌ 单点故障
  ❌ 数据量爆炸（亿级）
```

**分库分表**：水平拆分（拆行）+ 垂直拆分（拆列）。

## 2. 垂直拆分 vs 水平拆分

### 垂直拆分（按列）

```
单表 user（30 列）
  ↓ 拆
user_basic(id, name, email)            ← 高频查询
user_profile(id, address, bio)         ← 低频查询
user_security(id, password_hash, mfa)   ← 安全查询
```

**适用**：列冷热差异大，字段数多。
**优点**：DDL 简单，单表小。
**缺点**：单行 join 跨表（拆库后 join 难）。

### 水平拆分（按行）

```
单表 orders（10 亿行）
  ↓ 按 user_id % 4
orders_0  (0, 4, 8, ...)  ← shard 0
orders_1  (1, 5, 9, ...)  ← shard 1
orders_2  (2, 6, 10, ...)
orders_3  (3, 7, 11, ...)
```

**适用**：单表数据量爆炸。
**优点**：单表小（几亿 → 几千万），查询快。
**缺点**：跨 shard 聚合复杂。

## 3. 水平拆分策略

### 3.1 按 ID 取模

```java
int shard = (int) (orderId % 4);
String table = "orders_" + shard;
jdbcTemplate.update("INSERT INTO " + table + " ...");
```

**优点**：简单，平均分布。
**缺点**：扩容困难（4 库改 8 库 = 数据迁移）。

### 3.2 按 ID 范围（range）

```
shard 0: 0 - 999,999
shard 1: 1,000,000 - 1,999,999
shard 2: 2,000,000 - 2,999,999
```

**优点**：扩容简单（增加 shard 3: 3M+）。
**缺点**：分布不均（按业务量分），热点。

### 3.3 一致性 Hash

```
hash(userId) % 2^32 → 落到环上 → 找到下一个节点
```

**优点**：扩缩容只影响相邻节点。
**缺点**：实现复杂，节点少时倾斜。

### 3.4 按时间（range on time）

```
orders_2024Q1
orders_2024Q2
orders_2024Q3
orders_2024Q4
```

**适用**：时间序列数据（订单 / 日志）。
**优点**：归档冷热分层。

## 4. 路由策略

### 应用层路由（推荐）

```java
@DataSourceRouter
public class RoutingDataSource {
  public DataSource route(Long userId) {
    int shard = (int) (userId % 4);
    return dataSources.get("ds_" + shard);
  }
}
```

**Sharding-JDBC**：成熟方案
**TSharding**：当当开源
**MyCat**：老牌，活跃社区
**ShardingSphere**：Apache 顶级项目

### 中间件层（proxy）

```
应用 → Proxy（解析 SQL 改写 + 路由） → 后端 DB
```

代表：**MyCat**、**MaxScale**、**ProxySQL**、**Citus**（PG）。

**优点**：应用零改造。
**缺点**：Proxy 单点 / 性能瓶颈。

### 数据库层（native sharding）

- **TiDB**：原生分布式 SQL（PingCAP）
- **CockroachDB**：分布式 PG
- **Citus**（PG 扩展）：Citus extension
- **PolarDB**（阿里云）：云原生
- **TiDB / OceanBase**：原生水平扩展

**优点**：无应用改造。
**缺点**：迁移成本高，与传统 SQL 兼容性问题。

## 5. ShardingSphere 实战

```xml
<dependency>
  <groupId>org.apache.shardingsphere</groupId>
  <artifactId>shardingsphere-jdbc-core-spring-boot-starter</artifactId>
  <version>5.4.0</version>
</dependency>
```

```yaml
# application.yml
spring:
  shardingsphere:
    datasource:
      names: ds0,ds1,ds2,ds3
      ds0:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://db0:3306/order_0
      ds1:
        jdbc-url: jdbc:mysql://db1:3306/order_1
    rules:
      sharding:
        tables:
          t_order:
            actual-data-nodes: ds${0..3}.t_order_${0..3}
            database-strategy:
              sharding-column: user_id
              sharding-algorithm-name: mod
        sharding-algorithms:
          mod:
            type: MOD
            props:
              sharding-count: 16
```

## 6. 拆分后的挑战

### 全局唯一 ID

不能 auto_increment（每库独立）→ 用 **分布式 ID**：
- 雪花算法（Snowflake）：Twitter 开源
- UUID v7（时间排序）
- 美团 Leaf / 滴滴 Tinyid

### 跨库 join

```
order 表在 order_db
user 表在 user_db
关联：order JOIN user → 跨库 → 慢

解决：
1. 冗余字段（order 表存 user_name，避免 join）
2. 数据仓库（同步到 ES / Hive 统一查询）
3. 应用层组装（先查 user 再查 order）
```

### 跨库事务

```
跨库事务 = 分布式事务（见 07-distributed-tx/）
```

### 数据迁移

- 全量：双写（双写 DB + 校验），停写老库 → 全切
- 增量：订阅 binlog → 同步到新库
- 灰度：按 user_id 范围灰度

## 7. 何时分库分表

| 数据量 | 建议 |
|--------|------|
| < 100 万行 | 单库单表 |
| 100 万 - 1000 万 | 考虑分表（垂直或水平） |
| 1000 万 - 1 亿 | 必分表（水平） |
| > 1 亿 | 必分库 + 分表 |

**先优化**：索引、SQL、缓存 → 再分库分表（不到万不得已不分）。

## 8. 实战选型

| 场景 | 选 |
|------|-----|
| 初期 / 中小规模 | ShardingSphere-JDBC |
| 大规模 / 互联网 | ShardingSphere-Proxy / MyCat |
| 强一致 + 高扩展 | TiDB / CockroachDB（分布式 SQL） |
| 历史数据 / 日志 | 按时间 range + 冷热分层 |
| 多语言 / 难改造 | 代理层（MyCat / ProxySQL） |

## 🔗 下一步
- [路由 / 扩容](/10-database-sharding/routing)
- [分布式 ID](/10-database-sharding/id)
- [CAP 定理](/03-ha-theory/cap)
