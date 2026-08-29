---
title: EXPLAIN 详解
date: 2026-08-15  # date-auto-injected
---

# EXPLAIN 详解

> 看懂执行计划，慢查询不再黑盒。**EXPLAIN ANALYZE 是 DBA 的眼睛**。

## 1. 为什么需要 EXPLAIN？

```
SQL 性能问题排查：
  - SQL 跑了 10s，不知道慢在哪
  - 加了索引但没生效
  - 不知道是否用了索引

EXPLAIN 告诉你：
  - 用了什么扫描方式（Seq / Index / Bitmap）
  - 用了哪些索引
  - 估算多少行
  - 实际多少行
  - 每步耗时

📌 90% 的慢查询能用 EXPLAIN 定位
```

## 2. EXPLAIN 基础

### 2.1 三种格式

```sql
-- 文本（默认）
EXPLAIN SELECT * FROM users WHERE id = 1;

-- JSON（结构化，方便程序解析）
EXPLAIN (FORMAT JSON) SELECT * FROM users WHERE id = 1;

-- YAML
EXPLAIN (FORMAT YAML) SELECT * FROM users WHERE id = 1;
```

### 2.2 ANALYZE 实际执行

```sql
-- ANALYZE：实际执行 SQL，输出真实耗时
EXPLAIN ANALYZE SELECT * FROM users WHERE id = 1;

-- 注意：会真的执行 SQL（不是事务回滚）
-- 如果是 UPDATE/DELETE，必须在事务里：

BEGIN;
EXPLAIN ANALYZE DELETE FROM users WHERE id = 1;
ROLLBACK;  -- 不提交
```

### 2.3 其他参数

```sql
-- VERBOSE：输出更多信息（列名、schema 等）
EXPLAIN (VERBOSE) SELECT * FROM users;

-- BUFFERS：显示缓冲区使用
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM users WHERE id = 1;

-- TIMING：每节点耗时（默认开）
EXPLAIN (ANALYZE, TIMING) SELECT * FROM users WHERE id = 1;

-- COSTS：显示成本估算（默认开，关闭显示真实行数）
EXPLAIN (ANALYZE, COSTS OFF) SELECT * FROM users;
```

## 3. 执行计划结构

```
执行计划是树形结构：
  ┌─────────────────────────┐
  │ Limit (cost=...)        │
  │   ->  Sort (cost=...)   │
  │        ->  Hash Join    │
  │             ->  Seq Scan on orders │
  │             ->  Hash    │
  │                  ->  Seq Scan on users │
  └─────────────────────────┘

阅读顺序：从内到外 / 从下到上
最里层：先执行
最外层：最后执行
```

## 4. 常见节点类型

### 4.1 扫描方式（最重要）

```sql
-- Seq Scan：全表扫描
EXPLAIN SELECT * FROM users WHERE email = 'a@b.com';
--  小表无所谓，大表必优化
--  cost=N rows=M 估算

-- Index Scan：索引扫描（读取索引 + 回表）
EXPLAIN SELECT * FROM users WHERE id = 1;
--  Index Scan using users_pkey on users
--  cost=N rows=1

-- Index Only Scan：覆盖索引（不回表，最快）
EXPLAIN SELECT id FROM users WHERE id = 1;
--  Index Only Scan using users_pkey on users
--  cost=N rows=1

-- Bitmap Index Scan + Bitmap Heap Scan：位图扫描
EXPLAIN SELECT * FROM users WHERE age BETWEEN 20 AND 30;
--  Bitmap Heap Scan
--    ->  Bitmap Index Scan on idx_users_age
--  中等选择性（0.1% - 10%）适用
```

### 4.2 连接方式

```sql
-- Nested Loop：嵌套循环（小数据集）
EXPLAIN SELECT * FROM users u JOIN orders o ON u.id = o.user_id;
--  Nested Loop
--    ->  Seq Scan on orders
--    ->  Index Scan using users_pkey on users

-- Hash Join：哈希连接（大数据集）
--  Nested Loop
--    ->  Seq Scan on orders
--    ->  Hash
--         ->  Seq Scan on users

-- Merge Join：归并连接（已排序）
--  Merge Join
--    ->  Index Scan on users
--    ->  Index Scan on orders
```

### 4.3 排序与聚合

```sql
-- Sort：排序
EXPLAIN SELECT * FROM users ORDER BY created_at DESC;
--  Sort  (cost=N rows=M)
--    Sort Key: created_at DESC
--    ->  Seq Scan on users

-- 优化：建索引
CREATE INDEX idx_users_created_at ON users (created_at DESC);

-- Aggregate：聚合
EXPLAIN SELECT COUNT(*) FROM users;
--  Aggregate
--    ->  Seq Scan on users

-- HashAggregate：哈希聚合（GROUP BY）
EXPLAIN SELECT country, COUNT(*) FROM users GROUP BY country;
--  HashAggregate
--    Group Key: country
--    ->  Seq Scan on users
```

### 4.4 物化节点

```sql
-- Materialize：物化（缓存中间结果）
EXPLAIN SELECT * FROM (SELECT * FROM users WHERE age > 18) t WHERE id < 100;
--  Materialize
--    ->  Seq Scan on users

-- CTE（公用表）：PostgreSQL 默认物化 CTE（优化器隔离）
EXPLAIN WITH t AS (SELECT * FROM users) SELECT * FROM t WHERE id = 1;
--  CTE Scan on t
--    CTE t
--      ->  Seq Scan on users
--  PG 12+ 可用 NOT MATERIALIZED 修饰符
```

## 5. 实战案例

### 5.1 全表扫描

```sql
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'tom@example.com';

-- 结果：
-- Seq Scan on users  (cost=N rows=1) (actual time=0.05..15.23 rows=0 loops=1)
--   Filter: (email = 'tom@example.com')
--   Rows Removed by Filter: 100000
-- Planning Time: 0.1 ms
-- Execution Time: 15.5 ms

-- 优化：
CREATE INDEX idx_users_email ON users (email);

-- 再查：
-- Index Scan using idx_users_email on users  (actual time=0.02..0.03 rows=1)
--  Execution Time: 0.05 ms
```

### 5.2 索引失效

```sql
-- ❌ 索引失效（对索引列用函数）
EXPLAIN SELECT * FROM users WHERE LOWER(email) = 'tom@example.com';
--  Seq Scan on users

-- ✅ 优化：函数索引
CREATE INDEX idx_users_lower_email ON users (LOWER(email));

-- 或 PG 14+ 表达式索引（推荐）
-- CREATE INDEX idx_users_email_ci ON users (email) WHERE email IS NOT NULL;
```

### 5.3 估算不准

```sql
-- EXPLAIN ANALYZE 显示 rows=10000，实际 1000000
-- 优化器估算 100 倍偏差
-- 通常是统计信息过时

-- 解决：ANALYZE 表
ANALYZE users;

-- 或增加采样率
ALTER TABLE users SET (STATISTICS 1000);
ANALYZE users;
```

### 5.4 嵌套循环变慢

```sql
EXPLAIN ANALYZE
SELECT * FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.created_at > '2024-01-01';

-- Hash Join  ←  应该是这个
--   Hash Cond: (o.user_id = u.id)
--   ->  Index Scan on orders ...
--   ->  Hash
--        ->  Seq Scan on users

-- 如果是 Nested Loop + Seq Scan users → 慢
-- 优化：users.id 主键已建
--  检查 work_mem 设置
SET work_mem = '64MB';

-- 或强制使用 Hash Join
SET enable_nestloop = off;
```

## 6. 关键指标解读

### 6.1 cost（成本估算）

```
cost=123.45..678.90
  - 123.45：启动成本（找到第一行）
  - 678.90：总成本（找到所有行）
  - 单位：磁盘页读取估算
  - 不等于实际耗时，但可比较

对比 cost 高低：
  - Hash Join cost=1000
  - Nested Loop cost=5000
  → Hash Join 更便宜
```

### 6.2 actual time

```
actual time=0.05..15.23 rows=1000 loops=1
  - 0.05：第一行返回时间（毫秒）
  - 15.23：所有行返回时间
  - rows：实际返回行数
  - loops：循环次数

注意：actual time 是节点自己的耗时，不包含子节点
     实际总耗时 = 所有节点累加（包含重复）
```

### 6.3 Buffers

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM users WHERE id = 1;

-- Buffers: shared hit=4 read=8
--   shared hit：从 shared_buffers 命中（内存）
--   shared read：从磁盘读（产生 I/O）
--   shared dirtied：脏页
--   shared written：写盘

-- shared read 太多 → 增加 shared_buffers
-- shared hit 低 → 索引失效或表太大
```

## 7. 慢查询排查清单

```
1. EXPLAIN ANALYZE 跑一遍
2. 看 cost 高还是 actual time 高
3. 检查扫描方式（Seq Scan 是否有必要）
4. 估算 vs 实际 rows 偏差 > 10x → ANALYZE
5. 检查索引是否生效（WHERE / JOIN / ORDER BY 列）
6. Buffers：shared read 太多 → 加内存
7. 临时文件：sort / hash 落盘 → 加大 work_mem
8. 嵌套循环层级 > 3 → 检查 JOIN 顺序
9. 物化节点太多 → 检查 CTE 设计
10. 总结：建索引 + ANALYZE + 调整参数 + 改 SQL
```

## 8. 经典案例

### 8.1 count 慢

```sql
-- ❌ 慢：COUNT(*) 在大表上
EXPLAIN ANALYZE SELECT COUNT(*) FROM events;
--  Aggregate  (actual time=N rows=1)
--    ->  Seq Scan on events  ← 全表扫描

-- ✅ 优化：覆盖索引 + 统计
-- 方案 1：用估算值（pg_class.reltuples）
SELECT reltuples::bigint AS estimate
FROM pg_class WHERE relname = 'events';

-- 方案 2：物化视图 + 定时刷新
CREATE MATERIALIZED VIEW events_count AS
SELECT date_trunc('day', created_at) AS day, COUNT(*)
FROM events
GROUP BY 1;

-- 方案 3：触发器维护计数表
CREATE TABLE event_counts (count BIGINT);
INSERT INTO event_counts VALUES (0);
CREATE FUNCTION update_count() RETURNS trigger AS $$
BEGIN
  UPDATE event_counts SET count = count + 1;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 8.2 排序慢

```sql
-- ❌ 慢：内存不足，sort 落盘
EXPLAIN ANALYZE
SELECT * FROM events ORDER BY created_at DESC LIMIT 20;

-- Sort Method: external merge Disk: 200MB  ← 落盘！

-- ✅ 优化：建索引
CREATE INDEX idx_events_created_at ON events (created_at DESC);

-- 或增加 work_mem
SET work_mem = '256MB';
```

### 8.3 JOIN 慢

```sql
-- ❌ 慢：Nested Loop + 大量数据
EXPLAIN ANALYZE
SELECT * FROM big_table_a a JOIN big_table_b b ON a.id = b.a_id;

-- ✅ 优化：Hash Join
SET enable_nestloop = off;

-- 或加统计信息
ANALYZE big_table_a;
ANALYZE big_table_b;
```

## 9. 调优工具

```
内置：
  - EXPLAIN / EXPLAIN ANALYZE
  - pg_stat_statements（统计 SQL 执行）
  - auto_explain（自动记录慢查询）

外部：
  - pgAdmin 4（图形化 EXPLAIN）
  - explain.dalibo.com（在线可视化）
  - pgwatch2（监控）
  - pg_stat_monitor（更细的统计）
```

## 10. 一句话总结

```
📌 EXPLAIN = 看清 SQL 执行计划的工具，DBA 的核心技能
📌 三种格式：TEXT（默认）/ JSON（程序解析）/ YAML
📌 必加 ANALYZE 才能看到实际耗时
📌 节点类型：扫描（Seq/Index/Bitmap）/ JOIN（NL/Hash/Merge）/ Sort/Aggregate
📌 关键指标：cost（成本估算）/ actual time（真实耗时）/ Buffers（I/O）
📌 优化路径：EXPLAIN → 看扫描 → 建索引 → ANALYZE → 调参 → 改 SQL
📌 工具：explain.dalibo.com / pgAdmin 可视化
📌 90% 慢查询用 EXPLAIN 就能定位
```

## 11. 参考资料

- PostgreSQL 官方文档：Performance Tips
- "PostgreSQL Query Optimization"（2024）
- "Use The Index, Luke"（Markus Winand）
- explain.dalibo.com 可视化工具
- pg_stat_statements 文档
- "PostgreSQL 性能调优实战"（CSDN）


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 对比
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
- [system-design](https://java-px.bot.cd/system-design/):数据库选型
