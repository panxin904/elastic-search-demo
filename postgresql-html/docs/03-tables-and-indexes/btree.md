---
title: B-tree 索引
description: PostgreSQL 默认索引类型详解
---

# B-tree 索引

> **TL;DR**：B-tree 是 PG **默认索引类型**（CREATE INDEX 默认就是 B-tree）。适合**等值查询 + 范围查询 + 排序**。**90% 场景用 B-tree 就对了**。

## 一句话定义

```
B-tree（平衡树）= 多路搜索树，每个节点可存多个键值，支持等值/范围/前缀查询
```

## B-tree 的特性

```
✓ 等值查询：WHERE col = 'xxx'
✓ 范围查询：WHERE col > 100 AND col < 200
✓ 前缀匹配：WHERE col LIKE 'abc%'
✓ 排序加速：ORDER BY col
✗ 不支持：函数包裹（WHERE func(col) = 'xxx'）
✗ 不支持：JSONB 内部查询（用 GIN）
✗ 不支持：几何/全文（用 GIST/GIN）
```

## 基本使用

```sql
-- 默认就是 B-tree
CREATE INDEX idx_users_email ON users (email);

-- 等值查询
SELECT * FROM users WHERE email = '[email protected]';
-- Index Scan using idx_users_email

-- 范围查询
SELECT * FROM users WHERE created_at >= '2026-01-01' AND created_at < '2026-02-01';
-- Index Scan using idx_users_created_at

-- 排序
SELECT * FROM users ORDER BY created_at DESC LIMIT 20;
-- Index Scan Backward using idx_users_created_at
```

## 复合索引（最强大特性）

**多列联合索引**：列顺序至关重要。

```sql
-- 索引定义（A, B, C）
CREATE INDEX idx_orders ON orders (user_id, status, created_at);
```

**能用索引的查询**：

```sql
-- ✓ 全列等值
WHERE user_id = 1 AND status = 'paid' AND created_at = '2026-08-09'

-- ✓ 部分列等值（用前缀）
WHERE user_id = 1 AND status = 'paid'

-- ✓ 前缀列 + 后列范围
WHERE user_id = 1 AND status = 'paid' AND created_at >= '2026-08-01'

-- ✓ 排序也能用
ORDER BY user_id, status, created_at
```

**不能用索引的查询**：

```sql
-- ✗ 跳过前缀列
WHERE status = 'paid'  -- 没用，缺 user_id

-- ✗ 前缀列范围 + 后列等值（PG 9.x 之前）
WHERE user_id > 100 AND status = 'paid'  -- 9.6+ 部分能用

-- ✗ 反向列顺序
WHERE status = 'paid' AND user_id = 1  -- 不会用索引
```

**列顺序的选择**：

```
原则：
1. 高选择性（distinct 值多）的列放前面
2. 等值查询的列放前面
3. 范围查询的列放最后

例子：
  WHERE user_id = ? AND status = ? AND created_at > ?
  → (user_id, status, created_at) ← user_id 选择性 > status
```

## 包含列索引（Index Only Scan）

```sql
-- 创建包含索引
CREATE INDEX idx_orders_covering
  ON orders (user_id, status)
  INCLUDE (created_at, amount);

-- 查询
SELECT user_id, status, created_at, amount
FROM orders
WHERE user_id = 123 AND status = 'paid'
ORDER BY created_at DESC;

-- → Index Only Scan（不回表，索引里就有所有字段）
```

> **PG 11+**：INCLUDE 关键字。**比"把所有列都放进索引"省空间**，因为 INCLUDE 列不进 B-tree 排序。

## 表达式索引

```sql
-- 对表达式建索引
CREATE INDEX idx_users_lower_email ON users (lower(email));

-- 查询能用
SELECT * FROM users WHERE lower(email) = '[email protected]';
-- Index Scan using idx_users_lower_email
```

**实战场景**：

```sql
-- 1. URL 域名查询
CREATE INDEX idx_url_domain ON urls (substring(url from 'https?://([^/]+)'));
SELECT * FROM urls WHERE substring(url from 'https?://([^/]+)') = 'example.com';

-- 2. JSONB 字段
CREATE INDEX idx_users_data_name ON users ((data->>'name'));
SELECT * FROM users WHERE data->>'name' = 'Alice';

-- 3. 日期字段转换
CREATE INDEX idx_events_date ON events ((created_at::date));
SELECT * FROM events WHERE created_at::date = '2026-08-09';
```

## 部分索引（过滤索引）

```sql
-- 只索引"活跃"用户（95% 都不活跃，省 95% 空间）
CREATE INDEX idx_active_users_email
  ON users (email)
  WHERE status = 'active';

-- 查询能用
SELECT * FROM users WHERE status = 'active' AND email = '[email protected]';
-- Index Scan using idx_active_users_email

-- 普通查询不能用（缺 status 过滤）
SELECT * FROM users WHERE email = '[email protected]';
-- Seq Scan
```

**适用场景**：
- 软删除（`WHERE deleted_at IS NULL`）
- 状态过滤（`WHERE status = 'active'`）
- 分区数据（`WHERE region = 'us-east'`）

## 索引膨胀与 REINDEX

**索引也会膨胀**：

```sql
-- 1. 看索引膨胀（用 pgstattuple 扩展）
CREATE EXTENSION pgstattuple;
SELECT * FROM pgstatindex('idx_users_email');

-- 2. 重建索引（锁表，影响读写）
REINDEX INDEX idx_users_email;
-- 或
REINDEX INDEX CONCURRENTLY idx_users_email;  -- 不锁表（PG 12+）
```

**何时重建**：

```
✓ 索引页数膨胀 > 50%
✓ 删除大量数据后
✓ 表 bloat 后

✗ 不需要经常重建（PG autovacuum 会维护）
```

## NULL 排序与索引

```sql
-- 默认 B-tree 中 NULL 在最后（ASC）/ 最前（DESC）
CREATE INDEX idx_users_score ON users (score);  -- score NULL 时索引中位置

-- NULLS FIRST / NULLS LAST
CREATE INDEX idx_users_score ON users (score NULLS FIRST);
```

## 实战案例

### 案例 1：联合索引挽救慢查询

**问题**：

```sql
SELECT * FROM orders 
WHERE user_id = 123 
  AND status IN ('paid', 'shipped') 
ORDER BY created_at DESC 
LIMIT 20;

-- 耗时 5s
```

**修复**：

```sql
CREATE INDEX idx_orders_user_status_created
  ON orders (user_id, status, created_at DESC);

-- 耗时 0.05s
```

### 案例 2：避免回表（Index Only Scan）

**问题**：

```sql
SELECT user_id, status, created_at FROM orders 
WHERE user_id = 123;
-- Index Scan + Heap Fetch（500ms）

-- 走 Heap 是因为要查 created_at，但 created_at 不在索引里
```

**修复**：

```sql
CREATE INDEX idx_orders_covering
  ON orders (user_id, status) INCLUDE (created_at);

-- Index Only Scan（5ms）
```

### 案例 3：避免函数包裹索引失效

**问题**：

```sql
SELECT * FROM users WHERE date(created_at) = '2026-08-09';
-- Seq Scan（即使有 idx_created_at 索引）

-- 因为 date(created_at) 是函数，索引失效
```

**修复**：

```sql
CREATE INDEX idx_users_created_at_date ON users ((date(created_at)));

-- 或者重写 SQL 用范围：
SELECT * FROM users 
WHERE created_at >= '2026-08-09' AND created_at < '2026-08-10';
-- 用 idx_created_at 索引
```

## 索引监控

```sql
-- 1. 看每个索引使用情况
SELECT
  schemaname, relname, indexrelname,
  idx_scan,        -- 被扫描次数
  idx_tup_read,    -- 读取行数
  idx_tup_fetch    -- 命中行数
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- 2. 找未使用的索引（可考虑删除）
SELECT
  schemaname, relname, indexrelname,
  pg_size_pretty(pg_relation_size(indexrelid)) AS size,
  idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;

-- 3. 看表上的索引数（太多要清理）
SELECT
  schemaname, relname,
  pg_size_pretty(pg_relation_size(relid)) AS table_size,
  pg_size_pretty(pg_indexes_size(relid)) AS indexes_size
FROM pg_stat_user_tables
ORDER BY pg_indexes_size DESC
LIMIT 20;
```

## 选型决策

```
要建索引？
├─ SELECT 频繁 + 写入少 → 必建
├─ 写入频繁 + SELECT 少 → 慎建（索引拖慢写入）
└─ 看 idx_scan 决定，0 扫描 = 没用的索引

用什么类型？
├─ 等值 + 范围 + 排序 → B-tree（默认）
├─ JSONB / 数组 / 全文 → GIN
├─ 几何 / 范围 / 全文搜索 → GIST
└─ 大数据量 + 时间序列 → BRIN
```

## 一句话总结

> **B-tree 是 PG 默认索引，90% 场景适用**。**复合索引列顺序是关键**（高选择性 + 等值在前），**INCLUDE 实现 Index Only Scan**避免回表，**表达式索引解决函数包裹失效**，**部分索引省 95% 空间**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>