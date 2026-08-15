---
title: 覆盖索引与最左前缀
---

# ✅ 覆盖索引与最左前缀

> 两个最重要的索引优化技巧。可以让查询性能提升 **10 倍甚至 100 倍**。

## 🎯 覆盖索引（Covering Index）

### 什么是覆盖索引？

如果一个索引**包含了查询语句需要的所有字段**，MySQL 就不需要回表查询，直接在索引中拿到结果。

```
普通二级索引（需要回表）：
SELECT name, age, email FROM users WHERE name = '张三';
1. 在 idx_name 找到张三的 id=1
2. 回表：用 id=1 去聚簇索引找 email
3. 返回结果
总共：2 棵树的 IO

覆盖索引（无需回表）：
SELECT name, age FROM users WHERE name = '张三';
1. 在 idx_name_age 中找到 name=张三, age=25（同时拿到！）
2. 直接返回
总共：1 棵树的 IO ✅
```

### 如何创建覆盖索引

```sql
-- 表结构
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  name VARCHAR(50),
  age INT,
  email VARCHAR(100),
  city VARCHAR(50)
);

-- ❌ 普通索引（可能需要回表）
CREATE INDEX idx_name ON users(name);

-- ✅ 覆盖索引：包含查询需要的所有字段
CREATE INDEX idx_name_age ON users(name, age);

-- ✅ 这样查询就不需要回表了
SELECT name, age FROM users WHERE name = '张三';
-- Extra: Using index ✅
```

### 实战：识别覆盖索引

```sql
EXPLAIN SELECT id, name FROM users WHERE name = '张三';
+----+-------------+-------+------+---------------+------+---------+-------+------+-------------+
| id | select_type | table | type | possible_keys | key  | key_len | ref   | rows | Extra       |
+----+-------------+-------+------+---------------+------+---------+-------+------+-------------+
|  1 | SIMPLE      | users | ref  | idx_name      | idx_name | 202 | const | 1 | Using index |  ← 覆盖索引
+----+-------------+-------+------+---------------+------+---------+-------+------+-------------+

EXPLAIN SELECT id, name, email FROM users WHERE name = '张三';
-- Extra: NULL (没有 Using index) ← 需要回表
```

### 覆盖索引的经典应用场景

#### 1. SELECT 列表都在索引中

```sql
-- 假设 orders 表有 (user_id, status, created_at) 复合索引
-- ✅ 完全覆盖，无需回表
SELECT user_id, status, created_at FROM orders WHERE user_id = 100;

-- ❌ 多了 amount 字段，需要回表
SELECT user_id, status, created_at, amount FROM orders WHERE user_id = 100;
```

#### 2. COUNT 查询

```sql
-- 表：users 有 idx_city(city)
-- ❌ 需要回表（COUNT(*) 默认扫描聚簇索引）
SELECT COUNT(*) FROM users WHERE city = '北京';

-- ✅ 用覆盖索引（COUNT 只在索引树内统计）
CREATE INDEX idx_city ON users(city);
SELECT COUNT(*) FROM users WHERE city = '北京';
-- 如果 idx_city 覆盖了 city 字段，InnoDB 会选择最小的索引
-- 可能选 idx_city 而非聚簇索引 → 更快

-- 💡 更激进的优化：用覆盖索引 + 触发器维护计数器
CREATE TABLE user_city_count (
  city VARCHAR(50) PRIMARY KEY,
  cnt BIGINT
);
-- 通过触发器自动维护，查询时直接 SELECT cnt FROM user_city_count WHERE city = ?;
```

#### 3. 分页优化

```sql
-- ❌ 深分页（性能差，要回表大量数据）
SELECT * FROM orders ORDER BY id LIMIT 1000000, 20;

-- ✅ 主键分页（不需回表）+ 覆盖索引
SELECT id, user_id, amount FROM orders
WHERE id > 1000000  -- 上次最后一条的 id
ORDER BY id LIMIT 20;
-- 用 idx_pk 就能完成，无需大量回表
```

#### 4. JOIN 优化

```sql
-- ❌ 大 JOIN，每行都要回表
SELECT o.id, u.name
FROM orders o JOIN users u ON o.user_id = u.id
WHERE o.created_at > '2025-01-01';

-- ✅ 覆盖索引 + JOIN
CREATE INDEX idx_orders_userid_created ON orders(user_id, created_at);
CREATE INDEX idx_users_id_name ON users(id, name);
-- orders 表只需 idx_orders_userid_created
-- users 表只需 idx_users_id_name（覆盖了 name）
```

## 📐 最左前缀原则（Leftmost Prefix）

### 什么是复合索引的最左前缀？

```sql
-- 复合索引
CREATE INDEX idx_a_b_c ON table(a, b, c);
```

**这个索引可以用于以下查询：**

```sql
-- ✅ 全部走索引（最左前缀生效）
WHERE a = 1
WHERE a = 1 AND b = 2
WHERE a = 1 AND b = 2 AND c = 3
WHERE a = 1 AND b = 2 ORDER BY c
WHERE a = 1 ORDER BY b

-- ⚠️ 部分走索引（部分索引）
WHERE a = 1 AND c = 3   -- 只用 a 部分，c 不走索引
WHERE a = 1 AND c = 3 ORDER BY b  -- 排序需 filesort

-- ❌ 不走索引
WHERE b = 2                       -- 跳过了 a
WHERE b = 2 AND c = 3             -- 跳过了 a
WHERE c = 3                       -- 跳过了 a
```

### 原理图解

```
复合索引 (a, b, c) 的 B+Tree 按 a 排序，a 相同时按 b，b 相同时按 c

索引条目（按字典序排列）：
(a=1, b=1, c=1)
(a=1, b=1, c=2)
(a=1, b=2, c=1)  ← a 相同，b 排序
(a=1, b=2, c=3)
(a=2, b=1, c=1)
(a=2, b=3, c=2)
...

查询 WHERE a = 1 AND b = 2 AND c = 3：
  从 (1, 2, ...) 开始，能用索引 ✅

查询 WHERE b = 2：
  没有 a 的前缀信息，无法定位 ❌
```

### 实战：最左前缀设计

```sql
-- 表：orders (id, user_id, status, created_at, amount)

-- 常见查询模式：
-- Q1: WHERE user_id = ?        （按用户查所有订单）
-- Q2: WHERE user_id = ? AND status = ?   （按用户查特定状态）
-- Q3: WHERE user_id = ? AND created_at > ? AND created_at < ?（按用户查时间范围）
-- Q4: WHERE user_id = ? ORDER BY created_at DESC（按用户查最新订单）

-- ✅ 最佳索引设计：把常用过滤字段放前面
CREATE INDEX idx_user_status_created ON orders(user_id, status, created_at);

-- Q1: 用 user_id（最左前缀）
-- Q2: 用 user_id + status
-- Q3: 用 user_id（最左前缀）+ created_at 但会过滤 status
--    ⚠️ status 在中间会限制 created_at 范围扫描
--    💡 可以考虑 (user_id, created_at) 索引
-- Q4: ORDER BY created_at 能用上
```

### 范围查询会"打断"最左前缀

```sql
-- 索引 (a, b, c)
-- ✅ OK
WHERE a = 1 AND b = 2 AND c = 3
-- 三个字段都能用

-- ⚠️ b 是范围查询时，c 无法用索引
WHERE a = 1 AND b > 2 AND c = 3
-- a 和 b 能用索引（b 是范围扫描），但 c 必须在内存中过滤

-- 💡 解决方法：
-- 1. 调整字段顺序，把范围查询字段放后面
-- 2. 拆分索引：(a, b) + (a, c)

-- ❌ 多个范围查询
WHERE a > 1 AND b > 2
-- 只有 a 能用索引，b 必须在内存中过滤
```

### 实战：最左前缀的常见陷阱

#### 1. WHERE 顺序不影响索引

```sql
-- 索引 (a, b)
-- ✅ 都能用索引（MySQL 优化器会自动调整顺序）
WHERE a = 1 AND b = 2
WHERE b = 2 AND a = 1
```

#### 2. 函数 / 表达式破坏索引

```sql
-- 索引 (a)
-- ❌ 不走索引
WHERE a + 1 = 2
WHERE LOWER(a) = 'hello'
WHERE DATE(created_at) = '2025-01-15'

-- ✅ 改写
WHERE a = 1
WHERE LOWER(a) = 'hello'  -- 用函数索引（8.0+）
WHERE created_at >= '2025-01-15' AND created_at < '2025-01-16'
```

#### 3. 隐式类型转换破坏索引

```sql
-- phone 是 VARCHAR，索引在 phone
-- ❌ phone = 13800138000 会做 CAST，可能不走索引
SELECT * FROM users WHERE phone = 13800138000;

-- ✅ 保持类型一致
SELECT * FROM users WHERE phone = '13800138000';
```

#### 4. OR 的"分裂"问题

```sql
-- 索引 (a)
-- ❌ b 没有索引，OR 整体不走索引
WHERE a = 1 OR b = 2

-- ✅ 用 UNION 改写
SELECT * FROM t WHERE a = 1
UNION
SELECT * FROM t WHERE b = 2;
```

## 🏆 实战：复合索引字段顺序决策

**黄金法则：高选择性 + 高频过滤 字段放前面**

```sql
-- 表：orders
-- 字段：user_id (1万不同值), status (5个值), created_at (无数)
-- 查询频率：
--   按 user_id 查：80%
--   按 user_id + status：60%
--   按 user_id + created_at 范围：30%
--   按 status 查：5%

-- ✅ 最佳设计
CREATE INDEX idx_user_status_created ON orders(user_id, status, created_at);

-- 而不是：
-- ❌ status 放前面
CREATE INDEX idx_status_user_created ON orders(status, user_id, created_at);
-- 因为按 status 查的只有 5%，但 user_id 选择性高
```

**决策步骤：**
1. 列出所有查询模式
2. 按频率排序
3. 把高频查询的字段放复合索引前面
4. 范围查询字段放最后
5. 覆盖查询需要的所有字段（覆盖索引）

## 🔍 查看索引使用情况

```sql
-- 查看某查询是否走了索引
EXPLAIN SELECT * FROM orders WHERE user_id = 100 AND status = 'paid';

-- 关键字段：
-- type: const > eq_ref > ref > range > index > ALL
-- key: 实际使用的索引
-- key_len: 索引使用的字节数（判断最左前缀用到几列）
-- rows: 预估扫描行数
-- Extra: Using index（覆盖）/ Using where（过滤）/ Using filesort（排序）
```

## 📊 实际案例：电商订单查询优化

### 场景：订单列表页

```sql
-- 业务查询
SELECT id, user_id, amount, status, created_at
FROM orders
WHERE user_id = ? AND status IN ('paid', 'shipped')
  AND created_at > ?
ORDER BY created_at DESC
LIMIT 20;
```

### 优化前

```sql
-- 只有 idx_user_id（最基础）
EXPLAIN: type=ref, key=idx_user_id, rows=1000, Extra=Using where; Using filesort
-- 问题：
-- 1. status 在内存中过滤（1000 行中可能只有 100 行符合）
-- 2. filesort 需要排序
```

### 优化后

```sql
-- 复合索引：用户 + 状态 + 时间
CREATE INDEX idx_user_status_created ON orders(user_id, status, created_at);
EXPLAIN: type=range, key=idx_user_status_created, rows=100, Extra=Using index condition; Backward index scan
-- 优势：
-- 1. 索引直接在 (user_id, status) 范围扫描 → 精确 100 行
-- 2. created_at 在索引中已排好序 → 无需 filesort（Backward index scan）
-- 3. 索引包含查询所有字段 → 覆盖索引，无需回表
```

## 🎯 总结

**覆盖索引：**
- ✅ 索引包含查询的所有字段 → 无需回表
- ✅ 性能提升 5-10 倍
- ✅ 减少磁盘 IO
- 💡 设计索引时考虑 SELECT 列表

**最左前缀：**
- ✅ 复合索引按字段顺序生效
- ✅ 高频、高选择性字段放前面
- ✅ 范围查询字段放最后
- ⚠️ WHERE 顺序不影响（优化器会调整）

**下一步：** [🔍 索引下推 ICP](../02-index/icp) — MySQL 5.6+ 的隐藏性能优化