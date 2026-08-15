---
title: 窗口函数
---

# 🪟 MySQL 窗口函数

> MySQL 8.0 引入的强大功能。可以**不聚合但计算同组信息**，如排名、累计、前后行对比等。

## 🎯 为什么需要窗口函数？

```sql
-- 问题：查询每个用户消费最高的 3 笔订单
-- ❌ 没有窗口函数：复杂的子查询 + JOIN
SELECT o.*
FROM orders o
INNER JOIN (
  SELECT user_id, MAX(amount) AS max_amount
  FROM orders
  GROUP BY user_id
) t ON o.user_id = t.user_id AND o.amount = t.max_amount;

-- ✅ 有窗口函数：一行搞定
SELECT *
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rk
  FROM orders
) t
WHERE rk <= 3;
```

## 📊 窗口函数分类

### 1️⃣ 排名函数

```sql
SELECT
  user_id,
  order_no,
  amount,
  -- 排名函数（注意区别）
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY amount DESC) AS row_num,   -- 1,2,3,4 唯一
  RANK()       OVER (PARTITION BY user_id ORDER BY amount DESC) AS rank_num,   -- 1,2,2,4 跳过
  DENSE_RANK() OVER (PARTITION BY user_id ORDER BY amount DESC) AS dense_num, -- 1,2,2,3 不跳过
  NTILE(4)     OVER (PARTITION BY user_id ORDER BY amount DESC) AS quartile    -- 分 4 组
FROM orders;
```

```
示例数据：
| user_id | amount | ROW_NUMBER | RANK | DENSE_RANK |
|---------|--------|------------|------|------------|
|    1    |  100   |     1      |   1  |     1      |
|    1    |   90   |     2      |   2  |     2      |
|    1    |   90   |     3      |   2  |     2      |
|    1    |   80   |     4      |   4  |     3      |
|    2    |  200   |     1      |   1  |     1      |
```

### 2️⃣ 聚合窗口函数

```sql
SELECT
  user_id,
  order_date,
  amount,
  -- 累计聚合
  SUM(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS running_total,
  AVG(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS running_avg,
  COUNT(*)   OVER (PARTITION BY user_id ORDER BY order_date) AS running_count,
  MAX(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS running_max,
  MIN(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS running_min
FROM orders;

-- 全局聚合（不 PARTITION）
SELECT
  user_id, amount,
  SUM(amount) OVER () AS grand_total,
  AVG(amount) OVER () AS grand_avg
FROM orders;
```

### 3️⃣ 值函数（前后行访问）

```sql
SELECT
  user_id,
  order_date,
  amount,
  -- 前一行
  LAG(amount, 1, 0) OVER (PARTITION BY user_id ORDER BY order_date) AS prev_amount,
  -- 后一行
  LEAD(amount, 1, 0) OVER (PARTITION BY user_id ORDER BY order_date) AS next_amount,
  -- 第一行
  FIRST_VALUE(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS first_amount,
  -- 最后一行
  LAST_VALUE(amount) OVER (PARTITION BY user_id ORDER BY order_date) AS last_amount
FROM orders;
```

### 4️⃣ 分布函数

```sql
SELECT
  user_id, amount,
  -- 累计分布（0-1 之间）
  CUME_DIST() OVER (PARTITION BY user_id ORDER BY amount) AS cumedist,
  -- 百分位排名（0-1 之间）
  PERCENT_RANK() OVER (PARTITION BY user_id ORDER BY amount) AS pct_rank,
  -- 分布到 N 个桶
  NTILE(100) OVER (ORDER BY amount) AS percentile
FROM orders;
```

## 🔧 窗口函数语法

```sql
function_name ([expression]) OVER (
  [PARTITION BY partition_expression]    -- 分组（类似 GROUP BY）
  [ORDER BY sort_expression [ASC|DESC]]  -- 排序
  [window_frame_clause]                   -- 窗口范围
)
```

### 窗口框架（Window Frame）

```sql
SELECT
  order_date, amount,
  AVG(amount) OVER (
    PARTITION BY user_id
    ORDER BY order_date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW  -- 当前行 + 前 2 行
  ) AS avg_3_orders
FROM orders;

-- 框架关键字
-- ROWS / RANGE  : 按行 / 按值范围
-- PRECEDING     : 之前
-- FOLLOWING     : 之后
-- UNBOUNDED     : 无界
-- CURRENT ROW   : 当前行

-- 常用框架：
-- ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW  -- 累计到当前行
-- ROWS BETWEEN 2 PRECEDING AND CURRENT ROW            -- 3 行移动平均
-- ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING   -- 当前到末尾
-- ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING  -- 全组
```

## 🎯 实战案例

### 案例 1：每个用户的累计消费

```sql
SELECT
  user_id,
  order_date,
  amount,
  SUM(amount) OVER (
    PARTITION BY user_id
    ORDER BY order_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS cumulative_amount
FROM orders
ORDER BY user_id, order_date;
```

### 案例 2：移动平均（3 单）

```sql
SELECT
  user_id,
  order_date,
  amount,
  AVG(amount) OVER (
    PARTITION BY user_id
    ORDER BY order_date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) AS moving_avg_3
FROM orders;
```

### 案例 3：Top N per group

```sql
-- 每个类目销量前 10 的商品
SELECT *
FROM (
  SELECT
    category_id,
    product_id,
    sales,
    ROW_NUMBER() OVER (
      PARTITION BY category_id
      ORDER BY sales DESC
    ) AS rk
  FROM products
) t
WHERE rk <= 10;
```

### 案例 4：同比环比

```sql
-- 销售额环比
SELECT
  month,
  amount,
  LAG(amount, 1, 0) OVER (ORDER BY month) AS prev_month,
  ROUND(
    (amount - LAG(amount, 1, 0) OVER (ORDER BY month))
    / LAG(amount, 1, 0) OVER (ORDER BY month) * 100,
    2
  ) AS growth_pct
FROM monthly_sales;
```

### 案例 5：连续登录天数

```sql
SELECT
  user_id,
  login_date,
  -- 计算连续天数分组
  login_date - INTERVAL ROW_NUMBER() OVER (
    PARTITION BY user_id ORDER BY login_date
  ) DAY AS grp
FROM logins;

-- 同 grp 的就是连续登录（再 GROUP BY 取 COUNT）
```

### 案例 6：用户消费分级

```sql
SELECT
  user_id,
  total_amount,
  NTILE(5) OVER (ORDER BY total_amount DESC) AS level
  -- 1=最高消费, 5=最低消费
FROM (
  SELECT user_id, SUM(amount) AS total_amount
  FROM orders
  WHERE created_at >= '2025-01-01'
  GROUP BY user_id
) t;
```

## ⚠️ 窗口函数 vs GROUP BY

| 特性 | GROUP BY | 窗口函数 |
|---|---|---|
| 行数变化 | 聚合后行数减少 | **保留所有行** |
| 聚合粒度 | 全组聚合 | **每行都看全组** |
| 排序 | 自动排序 | ORDER BY 控制 |
| 性能 | 通常更快 | 略慢（计算每行） |
| 适用 | 汇总统计 | 排名、对比、累计 |

## 🎯 总结

**窗口函数核心：**
- ✅ 不减少行数，每行都"看到"组内信息
- ✅ 排名：`ROW_NUMBER()` / `RANK()` / `DENSE_RANK()`
- ✅ 累计：`SUM() OVER (ORDER BY)`
- ✅ 前后行：`LAG()` / `LEAD()`
- ✅ 分布：`NTILE()` / `PERCENT_RANK()`
- ✅ 框架：`ROWS BETWEEN ...`

**下一步：** [📚 常用函数与 CTE](../03-sql/functions) — 函数速查 + CTE 递归查询