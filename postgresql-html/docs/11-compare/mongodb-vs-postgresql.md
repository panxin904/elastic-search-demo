---
title: MongoDB vs PostgreSQL
date: 2026-08-15  # date-auto-injected
description: 文档型 vs 关系型数据库对比
---

# MongoDB vs PostgreSQL

> **TL;DR**：MongoDB 是**文档型 NoSQL**，PG 是**关系型 RDBMS**。**PG 11+ 加 JSONB 后已能覆盖 MongoDB 80% 场景**。**选 MongoDB 主要为了水平扩展**（分片 + 副本集），**选 PG 是为了一致性 + SQL + 生态**。

## 一句话定义

```
MongoDB  = BSON 文档存储，无 schema，原生分布式
PG       = 关系型 + JSONB，"SQL + 文档" 双模
```

## 整体对比

| 维度 | MongoDB | PostgreSQL |
|---|---|---|
| 数据模型 | 文档（BSON/JSON） | 表 + JSONB |
| Schema | 灵活（无强制） | 严格 + 灵活（JSONB 无约束） |
| 一致性 | 默认弱一致（可调） | 强一致（ACID） |
| 水平扩展 | 原生（分片集群） | 复杂（Citus 扩展 / 手动分区） |
| 事务 | 4.0+ 多文档 ACID | 全 ACID |
| JOIN | `$lookup`（性能差） | 完整 SQL JOIN |
| 索引 | B-tree + 全文 + 地理 | B-tree + GIN + GiST + BRIN |
| 生态 | 文档型生态 | RDBMS 完整生态 |
| 适用 | 灵活 schema / 大量写入 / 分布式 | 强一致 / 复杂查询 / 混合数据 |

## 数据模型对比

### 存储方式

```javascript
// MongoDB：文档（BSON）
db.users.insertOne({
  _id: ObjectId("..."),
  name: "Alice",
  email: "[email protected]",
  tags: ["admin", "user"],
  address: {
    city: "Beijing",
    zip: "100000"
  },
  created_at: ISODate("2026-08-09T10:00:00Z")
});
```

```sql
-- PostgreSQL：关系表 + JSONB
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  tags TEXT[],
  address JSONB,                  -- 嵌套对象用 JSONB
  created_at TIMESTAMPTZ DEFAULT now()
);

INSERT INTO users (name, email, tags, address)
VALUES (
  'Alice', '[email protected]',
  ARRAY['admin', 'user'],
  '{"city": "Beijing", "zip": "100000"}'
);
```

### Schema 灵活性

```javascript
// MongoDB：每个文档可以不同 schema
db.users.insertMany([
  { name: "Alice", email: "[email protected]" },      // 没 tags
  { name: "Bob", phone: "12345", tags: ["user"] }    // 没 email，有 phone
]);
```

```sql
-- PostgreSQL：传统字段强制 schema，JSONB 字段灵活
-- 必填字段约束
name TEXT NOT NULL
email TEXT NOT NULL

-- 灵活字段用 JSONB
extra JSONB  -- 任意字段都放这里
```

**实战对比**：

```javascript
// MongoDB 查询
db.users.find({ 
  "address.city": "Beijing",
  tags: "admin"
});
```

```sql
-- PostgreSQL 查询
SELECT * FROM users
WHERE address->>'city' = 'Beijing'
  AND 'admin' = ANY(tags);

-- 加 GIN 索引后性能等同
CREATE INDEX idx_users_address ON users USING GIN (address);
CREATE INDEX idx_users_tags ON users USING GIN (tags);
```

## 一致性与事务

### MongoDB 一致性

```
默认：读本地副本（可能读到旧数据）
可选：writeConcern majority + readConcern majority（强一致）
```

```javascript
// MongoDB 事务（4.0+）
const session = client.startSession();
session.startTransaction();
try {
  await accounts.updateOne(
    { _id: fromId }, 
    { $inc: { balance: -amount } },
    { session }
  );
  await accounts.updateOne(
    { _id: toId }, 
    { $inc: { balance: amount } },
    { session }
  );
  await session.commitTransaction();
} catch (e) {
  await session.abortTransaction();
}
session.endSession();
```

### PostgreSQL 一致性

```sql
-- 默认全 ACID
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

> **核心区别**：PG 默认强一致，MongoDB 默认最终一致（需要显式开启）。

## 水平扩展

### MongoDB 分片集群（原生）

```
              ┌──────────┐
              │ mongos   │  ← 路由
              └────┬─────┘
        ┌──────────┼──────────┐
        ↓          ↓          ↓
   Shard 1    Shard 2    Shard 3    ← 每个分片是副本集
   (Replica)  (Replica)  (Replica)
```

```javascript
// 配置分片
sh.enableSharding("mydb");
db.users.createIndex({ user_id: "hashed" });
sh.shardCollection("mydb.users", { user_id: "hashed" });

// 自动按 user_id hash 分片
```

### PostgreSQL 水平扩展（需要 Citus）

```sql
-- 安装 Citus 扩展
CREATE EXTENSION citus;

-- 选择分布列
SELECT create_distributed_table('users', 'user_id');

-- 自动按 user_id hash 分布到 worker 节点
```

或用**逻辑复制 + 应用层路由**。

> **MongoDB 优势**：原生分片，运维简单。**PG 劣势**：水平扩展需引入 Citus 或复杂架构。

## JOIN 能力

### MongoDB `$lookup`（弱）

```javascript
db.orders.aggregate([
  { $lookup: {
      from: "users",
      localField: "user_id",
      foreignField: "_id",
      as: "user_info"
  }}
]);
// 性能：百万级开始卡
```

### PG 标准 JOIN（强）

```sql
SELECT o.*, u.name, u.email
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.created_at >= '2026-08-01';

-- 性能：百万级毫秒返回
```

> **PG 优势**：JOIN 是 RDBMS 的看家本领，**优化器成熟**，**复杂 JOIN 性能是 MongoDB 的 10-100x**。

## 索引能力

### MongoDB

```javascript
// 单字段索引
db.users.createIndex({ email: 1 });

// 复合索引
db.users.createIndex({ status: 1, created_at: -1 });

// 文本索引
db.articles.createIndex({ content: "text" });

// 地理索引
db.stores.createIndex({ location: "2dsphere" });
```

### PG（更丰富）

```sql
-- B-tree（默认）
CREATE INDEX idx_users_email ON users (email);

-- GIN（JSONB / 数组 / 全文）
CREATE INDEX idx_users_data ON users USING GIN (data);

-- GiST（几何 / 范围 / 全文）
CREATE INDEX idx_stores_geo ON stores USING GIST (location);

-- BRIN（大数据量 + 时间序列）
CREATE INDEX idx_logs_created ON logs USING BRIN (created_at);

-- 部分索引
CREATE INDEX idx_active_users ON users (email) WHERE status = 'active';
```

> **PG 优势**：**6+ 种索引类型**（B-tree / GIN / GiST / SP-GiST / BRIN / Hash），**针对不同场景优化**。

## 聚合能力

### MongoDB 聚合管道

```javascript
db.orders.aggregate([
  { $match: { created_at: { $gte: ISODate("2026-08-01") } } },
  { $group: {
      _id: "$user_id",
      total: { $sum: "$amount" },
      count: { $sum: 1 }
  }},
  { $sort: { total: -1 } },
  { $limit: 10 }
]);
```

### PG 等价 SQL

```sql
SELECT
  user_id,
  SUM(amount) AS total,
  COUNT(*) AS count
FROM orders
WHERE created_at >= '2026-08-01'
GROUP BY user_id
ORDER BY total DESC
LIMIT 10;
```

> **PG 优势**：SQL 标准 + 优化器成熟，**同等语义下 PG 通常更快**。

## 何时选 MongoDB

```
✓ 业务 schema 不确定（快速迭代）
✓ 大量分布式写入（千万级/秒）
✓ 文档型数据天然匹配（如 CMS / IoT）
✓ 不需要复杂 JOIN
✓ 团队熟悉 JS / Python 生态
```

## 何时选 PG

```
✓ 强一致要求（金融 / 订单）
✓ 复杂查询（多表 JOIN + 窗口函数）
✓ 混合数据（关系 + JSON + 地理 + 向量）
✓ 已有 RDBMS 生态
✓ 不想被一家公司绑定（MongoDB Inc. vs 全球 PG 社区）
```

## 实战：MongoDB → PG 迁移

```javascript
// MongoDB 数据
db.users.find()
```

```sql
-- PG 表
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT,
  data JSONB  -- 兜底字段
);

-- 用 mongo_fdw 或 ETL 工具迁移
-- 或用 mongosh + pgloader 组合
```

**迁移考虑**：

| 维度 | MongoDB | PG 迁移 |
|---|---|---|
| 数据导入 | mongodump / mongoexport | COPY / pgloader |
| 应用改造 | 大量 | 大量（驱动力 + API） |
| 运维 | ops manager | pgBackrest / barman |
| 生态绑定 | MongoDB Inc. | 多家 PG 公司 |

## 一句话总结

> **MongoDB = 灵活 schema + 原生分片**，适合大规模写入和 schema 不确定的场景。**PG = 强一致 + SQL + 丰富索引**，适合复杂查询和事务需求。**JSONB + GIN 已能覆盖 MongoDB 80% 场景**，**选 MongoDB 主要为分片**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 对比
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
- [system-design](https://java-px.bot.cd/system-design/):数据库选型
