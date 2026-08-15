---
title: 窗口函数
description: PostgreSQL 强大的分析函数
---

# 窗口函数

> **TL;DR**：窗口函数 = **对一组相关行计算值**，但不合并成单行（GROUP BY 会合并）。**SQL 报表 Top N、排名、累计、移动平均**全靠它。**PG 窗口函数是 ANSI SQL 标准最完整实现**。

## 一句话定义

```
窗口函数 = 在结果集的"窗口"（一组相关行）上计算值
         = 类似 GROUP BY 但不合并行
```

## 与 GROUP BY 的区别

```sql
-- 数据
-- user_id | score
-- 1       | 90
-- 1       | 85
-- 2       | 95

-- GROUP BY：合并行
SELECT user_id, avg(score) FROM scores GROUP BY user_id;
-- user_id | avg
-- 1       | 87.5
-- 2       | 95.0
-- （3 行 → 2 行）

-- 窗口函数：不合并行
SELECT user_id, score, avg(score) OVER (PARTITION BY user_id) AS user_avg
FROM scores;
-- user_id | score | user_avg
-- 1       | 90    | 87.5
-- 1       | 85    | 87.5
-- 2       | 95    | 95.0
-- （3 行 → 3 行，但每行多了 user_avg）
```

## 基本语法

```sql
function_name(args) OVER (
  [PARTITION BY expr]      -- 分组（类似 GROUP BY 的列）
  [ORDER BY expr]          -- 窗口内排序
  [frame_clause]           -- 窗口帧（ROWS / RANGE BETWEEN ... AND ...）
)
```

## 排名函数（最常用）

### ROW_NUMBER / RANK / DENSE_RANK

```sql
SELECT
  user_id, score,
  ROW_NUMBER() OVER (ORDER BY score DESC) AS row_num,
  RANK()       OVER (ORDER BY score DESC) AS rank,
  DENSE_RANK() OVER (ORDER BY score DESC) AS dense_rank
FROM scores;
```

| 分数 | row_num | rank | dense_rank |
|---|---|---|---|
| 100 | 1 | 1 | 1 |
| 90 | 2 | 2 | 2 |
| 90 | 3 | 2 | 2 |
| 80 | 4 | 4 | 3 |

> **区别**：
> - ROW_NUMBER()：严格递增（1, 2, 3, 4）
> - RANK()：并列跳号（1, 2, 2, 4）
> - DENSE_RANK()：并列不跳号（1, 2, 2, 3）

### Top N per group（分组 Top N）

```sql
-- 每个用户消费金额 Top 3
WITH ranked AS (
  SELECT
    user_id, amount, created_at,
    ROW_NUMBER() OVER (
      PARTITION BY user_id ORDER BY amount DESC
    ) AS rn
  FROM orders
)
SELECT * FROM ranked WHERE rn <= 3;
```

### NTILE（分桶）

```sql
-- 把用户按消费金额分 4 档
SELECT
  user_id, total_amount,
  NTILE(4) OVER (ORDER BY total_amount DESC) AS bucket
FROM user_totals;
-- bucket = 1（前 25%）/ 2 / 3 / 4（后 25%）
```

## 聚合窗口函数

任何聚合函数都可以作窗口：

```sql
SELECT
  order_id, user_id, amount, created_at,
  SUM(amount)   OVER w AS running_total,
  AVG(amount)   OVER w AS running_avg,
  MAX(amount)   OVER w AS running_max,
  COUNT(*)      OVER w AS running_count
FROM orders
WINDOW w AS (PARTITION BY user_id ORDER BY created_at);

-- 每个用户的累计销售额、累计平均、最大单、累计单数
```

## 偏移函数

### LAG / LEAD（前/后一行）

```sql
-- 计算每日销量环比
SELECT
  date, daily_sales,
  LAG(daily_sales, 1)  OVER (ORDER BY date) AS prev_day,
  LEAD(daily_sales, 1) OVER (ORDER BY date) AS next_day,
  daily_sales - LAG(daily_sales, 1) OVER (ORDER BY date) AS diff
FROM daily_stats;

-- 默认 LAG 找不到前一行返回 NULL，可以指定默认值
LAG(daily_sales, 1, 0) OVER (ORDER BY date)  -- 第一天返回 0
```

### FIRST_VALUE / LAST_VALUE / NTH_VALUE

```sql
SELECT
  user_id, score, created_at,
  FIRST_VALUE(score) OVER (
    PARTITION BY user_id ORDER BY created_at
  ) AS first_score,
  LAST_VALUE(score) OVER (
    PARTITION BY user_id ORDER BY created_at
    RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  ) AS last_score
FROM scores;
```

> **注意**：LAST_VALUE 默认窗口帧只到当前行，**需要加 `UNBOUNDED FOLLOWING` 才能看到最后一行的真实值**。

## 窗口帧（Frame）

**窗口帧** = 在排序后的窗口里再选一个子集。

```sql
-- 移动平均（最近 3 天）
SELECT
  date, daily_sales,
  AVG(daily_sales) OVER (
    ORDER BY date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ) AS ma_3day
FROM daily_stats;

-- ROWS / RANGE 区别：
-- ROWS：物理行（前后各 N 行）
-- RANGE：值范围（同日期的多行算一起）
```

**常用帧模式**：

```sql
-- 1. 累计和
SUM(amount) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)

-- 2. 移动平均（最近 7 天）
AVG(value) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)

-- 3. 中心化平均（前后各 3 天）
AVG(value) OVER (ORDER BY date ROWS BETWEEN 3 PRECEDING AND 3 FOLLOWING)

-- 4. 当前 + 后 1
SUM(amount) OVER (ORDER BY date ROWS BETWEEN CURRENT ROW AND 1 FOLLOWING)
```

## 实战案例

### 案例 1：用户留存分析

```sql
-- 计算 N 日留存率
WITH cohort AS (
  SELECT
    user_id,
    date_trunc('week', created_at) AS cohort_week,
    date_trunc('week', login_at) AS login_week
  FROM user_logins
)
SELECT
  cohort_week,
  COUNT(DISTINCT CASE WHEN login_week = cohort_week THEN user_id END) AS week_0,
  COUNT(DISTINCT CASE WHEN login_week = cohort_week + interval '1 week' THEN user_id END) AS week_1,
  -- ...
FROM cohort
GROUP BY cohort_week;
```

### 案例 2：商品销量 Top 10 + 累计占比

```sql
WITH ranked AS (
  SELECT
    product_id, SUM(amount) AS total,
    ROW_NUMBER() OVER (ORDER BY SUM(amount) DESC) AS rn,
    SUM(SUM(amount)) OVER () AS grand_total,
    SUM(SUM(amount)) OVER (ORDER BY SUM(amount) DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_total
  FROM orders
  GROUP BY product_id
)
SELECT
  product_id, total,
  ROUND(100.0 * cum_total / grand_total, 2) AS cum_pct
FROM ranked
WHERE rn <= 10;
```

### 案例 3：会话去时间分桶

```sql
-- 用户连续 7 天登录 = 活跃用户
WITH dates AS (
  SELECT
    user_id,
    login_date,
    login_date - INTERVAL (ROW_NUMBER() OVER (
      PARTITION BY user_id ORDER BY login_date
    ) - 1) DAY AS grp
  FROM (SELECT DISTINCT user_id, login_date::date FROM user_logins) t
)
SELECT user_id, MIN(login_date), MAX(login_date), COUNT(*) AS days
FROM dates
GROUP BY user_id, grp
HAVING COUNT(*) >= 7;
```

### 案例 4：行转列 + 累计

```sql
-- 每月销售额 + 同比环比
SELECT
  month, sales,
  LAG(sales, 12) OVER (ORDER BY month) AS yoy_prev,  -- 12 个月前
  LAG(sales, 1) OVER (ORDER BY month) AS mom_prev,   -- 上月
  ROUND(100.0 * (sales - LAG(sales, 12) OVER (ORDER BY month)) 
        / NULLIF(LAG(sales, 12) OVER (ORDER BY month), 0), 2) AS yoy_pct
FROM monthly_sales;
```

## 性能优化

### 1. 给 ORDER BY 列建索引

```sql
-- 窗口函数 ORDER BY 的列应该建索引
CREATE INDEX idx_orders_user_created ON orders (user_id, created_at);

-- 窗口查询
SELECT user_id, created_at, amount,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at)
FROM orders;
-- → Index Scan，避免外排
```

### 2. 减少窗口帧范围

```sql
-- ❌ 大窗口帧 = 慢
AVG(value) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)

-- ✅ 限制窗口大小
AVG(value) OVER (ORDER BY date ROWS BETWEEN 7 PRECEDING AND CURRENT ROW)
```

### 3. 用 CTE 复用窗口

```sql
-- 同一个窗口定义用 WINDOW 子句复用
SELECT
  date, value,
  AVG(value) OVER w AS avg_7,
  SUM(value) OVER w AS sum_7
FROM data
WINDOW w AS (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW);
```

## 一句话总结

> **窗口函数 = SQL 分析报表的瑞士军刀**：ROW_NUMBER / RANK 排名、LAG / LEAD 同比环比、SUM / AVG 累计移动平均、NTILE 分桶。**核心三段：PARTITION BY 分组 + ORDER BY 排序 + frame_clause 帧**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>