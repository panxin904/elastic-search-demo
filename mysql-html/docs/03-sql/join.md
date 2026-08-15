---
title: JOIN 七种用法
---

# 🔗 MySQL JOIN 七种用法

> 多表查询的核心是 JOIN。理解 7 种 JOIN 的差异和性能特征，是写出高效 SQL 的基础。

## 📊 七种 JOIN 全景图

```
表 A          表 B
┌─────┐      ┌─────┐
│     │      │     │
│  ●  │      │  ●  │  ← INNER JOIN（交集）
│     │      │     │
└─────┘      └─────┘

┌─────┐      ┌─────┐
│     │      │  ●  │
│  ●●●│──────│● ● │  ← LEFT JOIN + INNER JOIN
│     │      │  ●  │
└─────┘      └─────┘

┌─────┐      ┌─────┐
│  ●  │      │     │
│●●●─│──    │     │  ← LEFT EXCLUDING JOIN
│     │      │     │
└─────┘      └─────┘

... 共 7 种
```

## 1️⃣ INNER JOIN（内连接）

**返回两表都匹配的记录**（交集）

```sql
SELECT
  u.id,
  u.name,
  o.order_no,
  o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE o.created_at >= '2025-01-01';
```

```
users 表：        orders 表：
┌────┬──────┐    ┌────┬──────────┬────────┐
│ id │ name │    │ id │ user_id  │ amount │
├────┼──────┤    ├────┼──────────┼────────┤
│  1 │ 张三 │    │  1 │    1     │  100   │
│  2 │ 李四 │    │  2 │    1     │  200   │
│  3 │ 王五 │    │  3 │    2     │  150   │
│  4 │ 赵六 │    │  4 │    5     │  300   │  ← user_id=5 在 users 中不存在
└────┴──────┘    └────┴──────────┴────────┘

INNER JOIN 结果（只保留两表都有的）：
┌────┬──────┬──────────┬────────┐
│ id │ name │ order_no │ amount │
├────┼──────┼──────────┼────────┤
│  1 │ 张三 │    1     │  100   │
│  1 │ 张三 │    2     │  200   │
│  2 │ 李四 │    3     │  150   │
└────┴──────┴──────────┴────────┘
```

**性能特征：**
- ✅ 驱动表选择很重要（小表驱动大表）
- ✅ 关联字段加索引
- ⚠️ 数据量大时性能下降明显

## 2️⃣ LEFT JOIN（左连接）

**返回左表全部，右表无匹配填 NULL**（左表全集 + 右表交集）

```sql
-- 查所有用户，包括没有下过单的
SELECT
  u.id,
  u.name,
  IFNULL(COUNT(o.id), 0) AS order_count,
  IFNULL(SUM(o.amount), 0) AS total_spent
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.status = 1
GROUP BY u.id, u.name
ORDER BY total_spent DESC
LIMIT 100;
```

```
LEFT JOIN 结果（users 全集）：
┌────┬──────┬──────────┬────────┐
│ id │ name │ order_id │ amount │
├────┼──────┼──────────┼────────┤
│  1 │ 张三 │    1     │  100   │
│  1 │ 张三 │    2     │  200   │
│  2 │ 李四 │    3     │  150   │
│  3 │ 王五 │   NULL   │  NULL  │  ← 没有订单也保留
│  4 │ 赵六 │   NULL   │  NULL  │
└────┴──────┴──────────┴────────┘
```

## 3️⃣ RIGHT JOIN（右连接）

**返回右表全部，左表无匹配填 NULL**（基本不用，交换表顺序用 LEFT JOIN 即可）

```sql
-- 与 LEFT JOIN 等价（交换表顺序）
SELECT *
FROM orders o
RIGHT JOIN users u ON o.user_id = u.id;

-- 等价于
SELECT *
FROM users u
LEFT JOIN orders o ON u.id = o.user_id;
```

💡 **建议：** 统一用 LEFT JOIN，保持代码一致性。

## 4️⃣ FULL OUTER JOIN（全外连接）

**返回两表全部，无匹配填 NULL**

```sql
-- ❌ MySQL 不支持 FULL OUTER JOIN
SELECT * FROM A FULL OUTER JOIN B ON ...;
-- ERROR: syntax error

-- ✅ 用 UNION 模拟
SELECT * FROM A LEFT JOIN B ON ...
UNION
SELECT * FROM A RIGHT JOIN B ON ...;
```

## 5️⃣ LEFT EXCLUDING JOIN（左排除连接）

**返回左表有但右表没有的记录**

```sql
-- 查所有"没有下过单"的用户
SELECT u.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id IS NULL;
```

```
结果：
┌────┬──────┐
│ id │ name │
├────┼──────┤
│  3 │ 王五 │
│  4 │ 赵六 │
└────┴──────┘
```

**⚠️ 性能陷阱：** 如果 LEFT JOIN 返回 100 万行，再 WHERE id IS NULL 过滤很慢。优化：

```sql
-- ✅ 改用 NOT EXISTS（更快）
SELECT u.*
FROM users u
WHERE NOT EXISTS (
  SELECT 1 FROM orders o WHERE o.user_id = u.id
);

-- ✅ 或 NOT IN（注意 NULL 陷阱）
SELECT u.*
FROM users u
WHERE u.id NOT IN (SELECT user_id FROM orders WHERE user_id IS NOT NULL);
```

## 6️⃣ RIGHT EXCLUDING JOIN（右排除连接）

**返回右表有但左表没有的记录**

```sql
-- 查"有用户ID但用户不存在"的孤儿订单（数据不一致）
SELECT o.*
FROM users u
RIGHT JOIN orders o ON u.id = o.user_id
WHERE u.id IS NULL;
```

## 7️⃣ FULL OUTER EXCLUDING JOIN（全排除连接）

**返回两表都独有的记录**（MySQL 不支持，用 UNION 模拟）

```sql
SELECT * FROM users u LEFT JOIN orders o ON u.id = o.user_id WHERE o.id IS NULL
UNION
SELECT * FROM users u RIGHT JOIN orders o ON u.id = o.user_id WHERE u.id IS NULL;
```

## ⚡ JOIN 性能优化

### 1. 小表驱动大表

```sql
-- ✅ 小表 users（1万行）驱动大表 orders（1000万行）
SELECT *
FROM users u          -- 1万行
LEFT JOIN orders o   -- 1000万行
  ON u.id = o.user_id;

-- ⚠️ 反过来性能差
SELECT *
FROM orders o         -- 1000万行
LEFT JOIN users u    -- 1万行
  ON o.user_id = u.id;
```

**原理：** JOIN 时，先遍历驱动表，对每行去被驱动表查找。驱动表小 = 外层循环少。

### 2. 关联字段必须建索引

```sql
-- ❌ orders.user_id 没索引 → 每次都全表扫描 users
SELECT * FROM orders o JOIN users u ON o.user_id = u.id;

-- ✅ 添加索引
CREATE INDEX idx_orders_userid ON orders(user_id);
```

### 3. 用 EXPLAIN 看 JOIN 顺序

```sql
EXPLAIN SELECT *
FROM orders o JOIN users u ON o.user_id = u.id;
```

看 `table` 列：第一行是被驱动表，第二行是驱动表。优化器会自动选择，但可以用 `STRAIGHT_JOIN` 强制顺序。

```sql
-- 强制驱动顺序（小表在前）
SELECT STRAIGHT_JOIN *
FROM users u          -- 强制为驱动表
LEFT JOIN orders o
  ON u.id = o.user_id;
```

### 4. 避免 JOIN 太多表

```sql
-- ❌ JOIN 7-8 张表
SELECT *
FROM a
JOIN b ON ...
JOIN c ON ...
JOIN d ON ...
JOIN e ON ...
JOIN f ON ...
JOIN g ON ...
JOIN h ON ...;

-- ✅ 拆成多个简单查询，应用层组装
```

**经验法则：** 超过 4-5 张表的 JOIN 建议拆分。

### 5. 用 EXISTS 替代 IN

```sql
-- ❌ IN 子查询
SELECT * FROM users
WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);

-- ✅ EXISTS（利用索引，更快）
SELECT * FROM users u
WHERE EXISTS (
  SELECT 1 FROM orders o
  WHERE o.user_id = u.id AND o.amount > 1000
);
```

### 6. JOIN 替代子查询

```sql
-- ❌ 子查询（可能执行多次）
SELECT *
FROM products
WHERE category_id IN (
  SELECT id FROM categories WHERE status = 1
);

-- ✅ JOIN（优化器可以更好地优化）
SELECT p.*
FROM products p
INNER JOIN categories c ON p.category_id = c.id
WHERE c.status = 1;
```

## 🔥 JOIN 实战案例

### 案例 1：查询每个用户的最近一笔订单

```sql
-- ❌ 错误：每用户子查询
SELECT u.id, u.name,
  (SELECT order_no FROM orders WHERE user_id = u.id ORDER BY created_at DESC LIMIT 1) AS last_order
FROM users u;

-- ✅ 正确：JOIN + 窗口函数（MySQL 8.0）
SELECT u.id, u.name, o.order_no, o.created_at
FROM users u
INNER JOIN (
  SELECT user_id, order_no, created_at,
         ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at DESC) AS rn
  FROM orders
) o ON u.id = o.user_id AND o.rn = 1;

-- ✅ 兼容 MySQL 5.7：JOIN + GROUP BY
SELECT u.id, u.name, o.order_no, o.created_at
FROM users u
INNER JOIN orders o ON u.id = o.user_id
INNER JOIN (
  SELECT user_id, MAX(created_at) AS max_created
  FROM orders
  GROUP BY user_id
) t ON o.user_id = t.user_id AND o.created_at = t.max_created;
```

### 案例 2：连续 7 天都有下单的活跃用户

```sql
SELECT DISTINCT user_id
FROM orders o1
WHERE created_at >= '2025-01-01'
  AND EXISTS (
    SELECT 1 FROM orders o2
    WHERE o2.user_id = o1.user_id
      AND o2.created_at >= o1.created_at
      AND o2.created_at < o1.created_at + INTERVAL 7 DAY
    GROUP BY DATE(o2.created_at)
    HAVING COUNT(DISTINCT DATE(o2.created_at)) >= 7
  );
```

### 案例 3：订单 + 用户 + 商品 三表 JOIN

```sql
SELECT
  o.order_no,
  u.name AS user_name,
  p.name AS product_name,
  oi.quantity,
  oi.price,
  o.amount,
  o.status,
  o.created_at
FROM orders o
INNER JOIN users u ON o.user_id = u.id
INNER JOIN order_items oi ON o.id = oi.order_id
INNER JOIN products p ON oi.product_id = p.id
WHERE o.created_at >= '2025-01-01'
  AND o.status = 'paid'
ORDER BY o.created_at DESC
LIMIT 20;

-- 💡 优化：覆盖索引
CREATE INDEX idx_orders_user_created ON orders(user_id, created_at);
CREATE INDEX idx_orderitems_order ON order_items(order_id);
CREATE INDEX idx_products_id_name ON products(id, name);  -- 覆盖 name
```

## 📊 7 种 JOIN 速查表

| JOIN 类型 | SQL 语法 | 返回结果 |
|---|---|---|
| INNER JOIN | `A JOIN B ON ...` | A ∩ B（交集） |
| LEFT JOIN | `A LEFT JOIN B ON ...` | A 全集 + B 交集 |
| RIGHT JOIN | `A RIGHT JOIN B ON ...` | B 全集 + A 交集 |
| FULL OUTER JOIN | ❌ MySQL 不支持 | A ∪ B（并集） |
| LEFT EXCLUDING JOIN | `A LEFT JOIN B ON ... WHERE B.id IS NULL` | A - B（A 独有） |
| RIGHT EXCLUDING JOIN | `A RIGHT JOIN B ON ... WHERE A.id IS NULL` | B - A（B 独有） |
| FULL EXCLUDING JOIN | UNION 模拟 | A ⊕ B（对称差） |

## 🎯 总结

**JOIN 核心原则：**
- ✅ 小表驱动大表
- ✅ 关联字段必须建索引
- ✅ 用覆盖索引避免回表
- ✅ 用 EXPLAIN 看 JOIN 顺序
- ✅ 不超过 4-5 张表的 JOIN
- ✅ EXISTS 优于 IN 子查询
- ✅ 统一用 LEFT JOIN（不用 RIGHT）

**下一步：** [🪟 窗口函数](../03-sql/window-functions) — MySQL 8.0 强大功能，排名 / 累计 / 前后行访问