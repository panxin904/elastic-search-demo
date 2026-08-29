---
title: SQL 改写 12 招
date: 2026-08-15  # date-auto-injected
---

# ✍️ MySQL SQL 改写 12 招

> 即使索引设计完美，SQL 写法不当也会导致慢查询。掌握这些改写技巧，能**不加索引也能提速 2-10 倍**。

## 1️⃣ 避免 SELECT *

```sql
-- ❌ SELECT *（扫描所有列，可能走不到覆盖索引）
SELECT * FROM users WHERE id = 1;

-- ✅ 只查需要的列
SELECT id, name, email FROM users WHERE id = 1;

-- 性能差距：
-- SELECT * 需要回表取所有列
-- SELECT 指定列 可能是覆盖索引（无需回表）
```

## 2️⃣ 避免在索引列上用函数

```sql
-- ❌ 函数破坏索引
SELECT * FROM orders WHERE DATE(created_at) = '2025-07-18';
SELECT * FROM users WHERE UPPER(name) = 'ZHANGSAN';
SELECT * FROM products WHERE YEAR(created_at) = 2025;

-- ✅ 改写为范围查询
SELECT * FROM orders
WHERE created_at >= '2025-07-18' AND created_at < '2025-07-19';

SELECT * FROM users WHERE name = 'zhangsan';  -- COLLATE 区分大小写

-- ✅ MySQL 8.0+ 用函数索引
CREATE INDEX idx_year_created ON orders((YEAR(created_at)));
```

## 3️⃣ 用 UNION 替代 OR

```sql
-- ❌ OR 拆分了索引
SELECT * FROM users WHERE name = '张三' OR age = 25;
-- 可能两个条件都用不上索引（除非两者都有索引且优化器聪明）

-- ✅ UNION ALL 改写
SELECT * FROM users WHERE name = '张三'
UNION ALL
SELECT * FROM users WHERE age = 25 AND name != '张三';
-- ⚠️ 注意去重：UNION ALL 不去重（可能重复），UNION 去重但慢
```

## 4️⃣ 避免在索引列上做运算

```sql
-- ❌ 列参与运算
SELECT * FROM users WHERE age + 1 = 26;
SELECT * FROM orders WHERE amount * 0.9 > 100;
SELECT * FROM products WHERE SUBSTRING(name, 1, 3) = 'iph';

-- ✅ 改写
SELECT * FROM users WHERE age = 25;
SELECT * FROM orders WHERE amount > 100 / 0.9;
SELECT * FROM products WHERE name LIKE 'iph%';
```

## 5️⃣ 用 EXISTS 替代 IN

```sql
-- ❌ IN 子查询（可能多次执行）
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);

-- ✅ EXISTS（找到就返回）
SELECT * FROM users u
WHERE EXISTS (
  SELECT 1 FROM orders o
  WHERE o.user_id = u.id AND o.amount > 1000
);
```

**特例：** IN 子查询结果是常量列表时，两者差不多

```sql
-- 这种情况 IN 没问题
SELECT * FROM users WHERE id IN (1, 2, 3, 100, 200);
```

## 6️⃣ 用 JOIN 替代子查询

```sql
-- ❌ 子查询
SELECT *
FROM products
WHERE category_id IN (
  SELECT id FROM categories WHERE status = 1
);

-- ✅ JOIN
SELECT p.*
FROM products p
INNER JOIN categories c ON p.category_id = c.id
WHERE c.status = 1;
```

## 7️⃣ 拆分复杂查询

```sql
-- ❌ 一个查询做太多事
SELECT
  user.*,
  (SELECT COUNT(*) FROM orders WHERE user_id = user.id) AS order_count,
  (SELECT SUM(amount) FROM orders WHERE user_id = user.id) AS total
FROM users
WHERE status = 1;

-- ✅ 拆分多个查询
-- 应用层组装
SELECT * FROM users WHERE status = 1;
SELECT user_id, COUNT(*) AS cnt, SUM(amount) AS total
FROM orders
WHERE user_id IN (1, 2, 3, ...)
GROUP BY user_id;
```

## 8️⃣ 优化 LIMIT 深分页

```sql
-- ❌ 深分页（扫描 + 丢弃大量数据）
SELECT * FROM orders ORDER BY id LIMIT 1000000, 20;
-- MySQL 扫描 1000020 行，丢弃前 1000000

-- ✅ 游标分页（基于主键）
SELECT * FROM orders
WHERE id > 1000000
ORDER BY id LIMIT 20;

-- ✅ 延迟关联（先取 id，再 JOIN）
SELECT *
FROM orders o
INNER JOIN (
  SELECT id FROM orders
  ORDER BY created_at DESC
  LIMIT 1000000, 20
) t ON o.id = t.id;
```

## 9️⃣ 用小表驱动大表

```sql
-- ❌ 大表驱动小表
SELECT *
FROM orders o  -- 1000 万行
LEFT JOIN users u ON o.user_id = u.id
WHERE u.status = 1;

-- ✅ 小表驱动大表
SELECT *
FROM users u  -- 1 万行（先过滤）
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.status = 1;
```

## 🔟 避免全表 COUNT

```sql
-- ❌ 全表 COUNT（即使有 WHERE 也可能慢）
SELECT COUNT(*) FROM orders WHERE status = 'paid';
-- InnoDB 不缓存精确行数，每次都扫描

-- ✅ 近似值（如果业务允许）
EXPLAIN SELECT COUNT(*) FROM orders WHERE status = 'paid';
-- rows 是估算值

-- ✅ 用缓存表（推荐）
CREATE TABLE order_count (
  status VARCHAR(20) PRIMARY KEY,
  cnt BIGINT
);
-- 触发器或定时任务维护
SELECT cnt FROM order_count WHERE status = 'paid';
```

## 1️⃣1️⃣ 用 INSERT ... ON DUPLICATE KEY UPDATE

```sql
-- ❌ 先 SELECT 再 INSERT/UPDATE（两次 IO）
-- 应用逻辑：
if (exists) {
  UPDATE ...
} else {
  INSERT ...
}

-- ✅ 一次 IO
INSERT INTO users (id, name, age) VALUES (1, '张三', 26)
ON DUPLICATE KEY UPDATE
  name = VALUES(name),
  age = VALUES(age);
```

## 1️⃣2️⃣ 避免不必要的 ORDER BY

```sql
-- ❌ 不必要的排序
SELECT * FROM users WHERE status = 1 ORDER BY id;

-- ✅ 如果结果集小，不需要排序
SELECT * FROM users WHERE status = 1 LIMIT 10;

-- ✅ 用主键顺序（聚簇索引天然有序）
-- WHERE id > 100 ORDER BY id  -- 索引顺序，无需排序
```

## 🎁 进阶技巧

### 13. JOIN 时指定字段

```sql
-- ❌ SELECT * 触发全列读取
SELECT * FROM users u JOIN orders o ON u.id = o.user_id;

-- ✅ 只查需要的字段（更可能命中覆盖索引）
SELECT u.id, u.name, o.order_no, o.amount
FROM users u
JOIN orders o ON u.id = o.user_id;
```

### 14. 用 STRAIGHT_JOIN 强制 JOIN 顺序

```sql
-- 默认优化器可能选错 JOIN 顺序
-- 强制小表在前
SELECT STRAIGHT_JOIN *
FROM small_table s
JOIN big_table b ON s.id = b.small_id;
```

### 15. 用 DELAYED 优化批量写入（5.6 已移除，了解即可）

```sql
-- 5.6 之前可用，8.0 已删除
INSERT DELAYED INTO logs ...;
-- 不立即写入，适合日志等延迟写入场景
```

### 16. 用 REPLACE INTO 谨慎替代 INSERT

```sql
-- ⚠️ REPLACE 会先删后插，自增 ID 会变化
-- 不推荐在生产环境使用，可能影响外键
REPLACE INTO users (id, name) VALUES (1, '张三');
```

## 🎯 SQL 改写实战案例

### 案例 1：电商首页推荐

```sql
-- ❌ 原 SQL（慢）
SELECT *
FROM products
WHERE category_id IN (1, 2, 3)
  AND status = 1
  AND stock > 0
ORDER BY sales_count DESC
LIMIT 20;

-- 慢的原因：
-- 1. IN (1,2,3) 可能走 range 或 ALL
-- 2. ORDER BY sales_count 需要 filesort

-- ✅ 改写后
-- 加复合索引
CREATE INDEX idx_cat_status_stock_sales ON products(category_id, status, stock, sales_count DESC);

-- SQL 改写（避免 IN）
SELECT *
FROM products
WHERE category_id BETWEEN 1 AND 3
  AND status = 1
  AND stock > 0
ORDER BY sales_count DESC
LIMIT 20;

-- type=range, Extra=Using index condition; Backward index scan
```

### 案例 2：实时数据大屏

```sql
-- ❌ 每次查询都实时聚合（慢）
SELECT
  DATE_FORMAT(created_at, '%H') AS hour,
  COUNT(*) AS cnt,
  SUM(amount) AS total
FROM orders
WHERE created_at >= CURRENT_DATE
GROUP BY HOUR(created_at);

-- ✅ 用预聚合表
CREATE TABLE hourly_sales (
  hour DATETIME PRIMARY KEY,
  cnt INT,
  total DECIMAL(15, 2)
);

-- 定时任务（每 10 分钟）聚合 → 写入 hourly_sales
-- 大屏直接读 hourly_sales，O(1) 速度
SELECT * FROM hourly_sales WHERE hour >= CURRENT_DATE;
```

## 🎯 总结

**SQL 改写 12 招速查：**

| 招数 | 性能提升 | 难度 |
|---|---|---|
| 避免 SELECT * | 2-5x | ⭐ |
| 避免索引列用函数 | 10-100x | ⭐ |
| UNION 替代 OR | 2-10x | ⭐⭐ |
| EXISTS 替代 IN | 2-5x | ⭐ |
| JOIN 替代子查询 | 2-5x | ⭐ |
| 拆分复杂查询 | 2-10x | ⭐⭐ |
| 游标分页 | 10-100x | ⭐⭐ |
| 小表驱动大表 | 2-5x | ⭐ |
| 避免全表 COUNT | 5-50x | ⭐⭐ |
| ON DUPLICATE KEY UPDATE | 1.5-2x | ⭐ |
| 避免不必要 ORDER BY | 1.5-3x | ⭐ |
| STRAIGHT_JOIN | 2-5x | ⭐⭐ |

**下一步：** [📜 binlog 与 relay log](../06-replication/binlog) — 进入主从复制的世界