---
title: 索引优化实战
date: 2026-08-15  # date-auto-injected
---

# 🎯 MySQL 索引优化实战

> 索引选型是 MySQL 性能优化的核心。选对了索引，查询性能提升 **10-100 倍**；选错了，再多的调优也是徒劳。

## 🎯 索引选型的黄金法则

### 1. 选择性高的字段优先

```sql
-- 计算选择性（不重复值 / 总行数）
SELECT
  COUNT(DISTINCT column_name) / COUNT(*) AS selectivity
FROM table_name;

-- 选择性 > 0.1 的字段适合建索引
-- 选择性 < 0.01 的字段（如性别、状态）建索引效果差
```

### 2. 经常查询的字段

```sql
-- WHERE、JOIN、ORDER BY、GROUP BY 中频繁使用的字段
-- 分析查询日志，找出高频查询
pt-query-digest /var/log/mysql/slow.log | grep -A 5 "WHERE"
```

### 3. 复合索引遵循最左前缀

```sql
-- 复合索引 (a, b, c)
-- ✅ WHERE a = ?
-- ✅ WHERE a = ? AND b = ?
-- ❌ WHERE b = ? (跳过了 a)
```

## 🏆 实战：常见查询的索引设计

### 案例 1：用户表

```sql
CREATE TABLE users (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  email VARCHAR(100) NOT NULL,
  phone CHAR(11),
  status TINYINT NOT NULL DEFAULT 1,
  city VARCHAR(50),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  last_login_at DATETIME
);

-- 常见查询：
-- Q1: WHERE username = ? (登录)
-- Q2: WHERE email = ? (找回密码)
-- Q3: WHERE phone = ? (手机号登录)
-- Q4: WHERE city = ? AND status = 1 (同城活跃用户)
-- Q5: WHERE created_at > ? ORDER BY created_at DESC (新注册用户)
-- Q6: ORDER BY last_login_at DESC LIMIT 100 (活跃用户列表)

-- ✅ 索引设计
CREATE UNIQUE INDEX uk_username ON users(username);
CREATE UNIQUE INDEX uk_email ON users(email);
CREATE UNIQUE INDEX uk_phone ON users(phone);
CREATE INDEX idx_city_status ON users(city, status);
CREATE INDEX idx_created ON users(created_at);
CREATE INDEX idx_last_login ON users(last_login_at);
```

### 案例 2：订单表

```sql
CREATE TABLE orders (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_no VARCHAR(32) NOT NULL,
  user_id BIGINT UNSIGNED NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'pending',
  amount DECIMAL(10, 2) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  paid_at DATETIME,
  shipped_at DATETIME
);

-- 常见查询：
-- Q1: WHERE order_no = ? (订单详情)
-- Q2: WHERE user_id = ? ORDER BY created_at DESC (用户订单列表)
-- Q3: WHERE status = 'paid' AND created_at > ? (待发货订单)
-- Q4: WHERE user_id = ? AND status = 'paid' (用户已支付订单)
-- Q5: WHERE created_at BETWEEN ? AND ? (时间范围统计)

-- ✅ 索引设计
CREATE UNIQUE INDEX uk_order_no ON orders(order_no);

-- 🔥 核心索引：用户订单列表（按时间倒序）
CREATE INDEX idx_user_created ON orders(user_id, created_at DESC);

-- 状态 + 时间（待发货、已完成等）
CREATE INDEX idx_status_created ON orders(status, created_at DESC);

-- 时间范围统计
CREATE INDEX idx_created ON orders(created_at);
```

### 案例 3：商品表

```sql
CREATE TABLE products (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  category_id INT NOT NULL,
  brand_id INT NOT NULL,
  price DECIMAL(10, 2) NOT NULL,
  stock INT NOT NULL DEFAULT 0,
  status TINYINT NOT NULL DEFAULT 1,
  sales_count INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 常见查询：
-- Q1: WHERE category_id = ? AND status = 1 (某分类的在售商品)
-- Q2: WHERE brand_id = ? AND status = 1 (某品牌的在售商品)
-- Q3: WHERE name LIKE 'iPhone%' (前缀搜索)
-- Q4: WHERE price BETWEEN ? AND ? AND status = 1 (价格区间)
-- Q5: WHERE status = 1 ORDER BY sales_count DESC LIMIT 20 (热门商品)

-- ✅ 索引设计
CREATE INDEX idx_category_status ON products(category_id, status);
CREATE INDEX idx_brand_status ON products(brand_id, status);

-- 前缀索引（节省空间）
CREATE INDEX idx_name_prefix ON products(name(20));

-- 价格区间 + 状态
CREATE INDEX idx_status_price ON products(status, price);

-- 热门排序（status 在前过滤，sales_count 排序）
CREATE INDEX idx_status_sales ON products(status, sales_count DESC);
```

## 🔥 高级索引技巧

### 1. 覆盖索引（最常用）

```sql
-- 场景：查询订单列表只需要几个字段
SELECT id, order_no, amount, status, created_at
FROM orders
WHERE user_id = ? AND status = 'paid'
ORDER BY created_at DESC
LIMIT 20;

-- ✅ 索引包含所有查询字段
CREATE INDEX idx_user_status_created ON orders(user_id, status, created_at DESC);

-- 💡 如果还要显示 user_name（来自 users 表）
-- 1. 把 user_name 冗余到 orders 表（反范式）
-- 2. 或用 JOIN + 覆盖索引
```

### 2. 前缀索引（长字符串优化）

```sql
-- URL 太长（200 字符），不需要全索引
CREATE INDEX idx_url_prefix ON logs(url(50));
-- 索引前 50 个字符

-- 测试前缀长度的选择性
SELECT
  COUNT(DISTINCT LEFT(url, 50)) / COUNT(*) AS sel_50,
  COUNT(DISTINCT LEFT(url, 30)) / COUNT(*) AS sel_30,
  COUNT(DISTINCT LEFT(url, 20)) / COUNT(*) AS sel_20
FROM logs;

-- 选择性接近 1.0 的最小前缀长度
```

### 3. 函数索引（MySQL 8.0+）

```sql
-- 场景：经常查询 UPPER(name) 或 DATE(created_at)

-- 创建函数索引
CREATE INDEX idx_upper_name ON users((UPPER(name)));
SELECT * FROM users WHERE UPPER(name) = 'ZHANGSAN';
-- 用上 idx_upper_name

-- 表达式索引
CREATE INDEX idx_year_created ON orders((YEAR(created_at)));
SELECT * FROM orders WHERE YEAR(created_at) = 2025;
```

### 4. 多值索引（MySQL 8.0.17+）

```sql
-- 场景：tags 是 JSON 数组
ALTER TABLE products ADD INDEX idx_tags((CAST(tags AS CHAR(50) ARRAY)));

-- 查询数组中包含 '手机'
SELECT * FROM products
WHERE '手机' MEMBER OF (tags);
-- 用上多值索引
```

### 5. 隐藏索引（调试用）

```sql
-- 创建一个索引但让优化器看不到它，用于测试删除索引的影响
CREATE INDEX idx_test ON users(city) INVISIBLE;

-- 启用
ALTER TABLE users ALTER INDEX idx_test VISIBLE;

-- 隐藏
ALTER TABLE users ALTER INDEX idx_test INVISIBLE;
```

## ⚠️ 索引的代价

### 写入性能

```sql
-- 每多一个索引，写入就更慢
-- 数据量 100 万行：
--   无索引：INSERT 1ms
--   1 个索引：INSERT 1.5ms
--   5 个索引：INSERT 5ms
--   10 个索引：INSERT 15ms

-- 💡 不要盲目加索引，定期清理无用索引
```

### 磁盘空间

```sql
-- 查看表的索引大小
SELECT
  table_name,
  index_name,
  stat_value * @@innodb_page_size / 1024 / 1024 AS size_mb
FROM mysql.innodb_index_stats
WHERE database_name = 'mydb'
  AND stat_name = 'size';
```

### 优化器负担

```sql
-- 索引太多，优化器反而变慢
-- 建议：每张表不超过 5-7 个索引
```

## 📊 索引使用情况分析

### 查看未使用的索引

```sql
-- 8.0+: performance_schema
SELECT
  object_schema,
  object_name,
  index_name
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE index_name IS NOT NULL
  AND index_name != 'PRIMARY'
  AND count_star = 0
ORDER BY object_schema, object_name;

-- 这些是"僵尸索引"，可以考虑删除
ALTER TABLE users DROP INDEX idx_unused;
```

### 查看索引效率

```sql
-- 查看索引使用频率
SELECT
  object_schema,
  object_name,
  index_name,
  count_star AS rows_read,
  sum_timer_wait / 1000000000 AS total_ms
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE index_name IS NOT NULL
  AND count_star > 0
ORDER BY count_star DESC
LIMIT 20;
```

## 🎯 索引优化案例

### 案例 1：商品搜索优化

```sql
-- 需求：商品列表页
-- 筛选：分类 + 状态 + 价格区间
-- 排序：销量降序
-- 分页：每页 20

SELECT id, name, price, sales_count
FROM products
WHERE category_id = 1
  AND status = 1
  AND price BETWEEN 100 AND 1000
ORDER BY sales_count DESC
LIMIT 20;

-- ❌ 错误索引
CREATE INDEX idx_category ON products(category_id);
-- type=ref, 但 price 是范围扫描，需要在内存中过滤

-- ✅ 正确索引（满足所有筛选 + 排序）
CREATE INDEX idx_cat_status_price_sales ON products(category_id, status, price, sales_count DESC);

-- Extra: Using index condition; Backward index scan
```

### 案例 2：用户消息列表优化

```sql
-- 需求：消息列表，按时间倒序
-- 筛选：当前用户 + 未读 + 未删除

SELECT id, content, created_at
FROM messages
WHERE user_id = 100
  AND is_read = 0
  AND is_deleted = 0
ORDER BY created_at DESC
LIMIT 20;

-- 消息量可能很大（千万级），索引很重要
-- ✅ 复合索引
CREATE INDEX idx_user_read_deleted_created ON messages(user_id, is_read, is_deleted, created_at DESC);
```

### 案例 3：订单统计报表优化

```sql
-- 需求：按月统计销售额
-- 频繁做 GROUP BY + 聚合

SELECT
  DATE_FORMAT(created_at, '%Y-%m') AS month,
  COUNT(*) AS order_count,
  SUM(amount) AS total
FROM orders
WHERE status = 'paid'
  AND created_at BETWEEN '2024-01-01' AND '2025-12-31'
GROUP BY DATE_FORMAT(created_at, '%Y-%m');

-- ✅ 索引支持范围扫描
CREATE INDEX idx_status_created ON orders(status, created_at);

-- 💡 高频报表考虑：预聚合表 + Transform
CREATE TABLE monthly_sales (
  month VARCHAR(7) PRIMARY KEY,
  order_count INT,
  total DECIMAL(15, 2)
);
-- 后台定时任务聚合 → 查询直接读预聚合表
```

## 🎯 索引优化清单

| ✅ 优化项 | 实施难度 | 效果 |
|---|---|---|
| 高频 WHERE 字段建索引 | ⭐ | 高 |
| 复合索引满足最左前缀 | ⭐⭐ | 高 |
| 覆盖索引避免回表 | ⭐⭐ | 高 |
| 删除冗余索引 | ⭐ | 中 |
| 删除未使用的索引 | ⭐ | 中 |
| 函数索引 / 表达式索引 | ⭐⭐ | 中 |
| 调整索引字段顺序 | ⭐⭐ | 高 |

## 🎯 总结

**索引设计原则：**
- ✅ 选择性高的字段优先
- ✅ 复合索引满足最左前缀
- ✅ 覆盖索引避免回表
- ✅ 范围查询字段放最后
- ✅ 排序字段在索引中（避免 filesort）
- ✅ 定期清理无用索引

**避免：**
- ❌ 在低选择性字段建索引（性别、状态）
- ❌ 每张表超过 5-7 个索引
- ❌ 在频繁更新的字段建太多索引

**下一步：** [✍️ SQL 改写 12 招](../05-optimization/sql-rewrite) — 不加索引也能提速的 SQL 改写技巧