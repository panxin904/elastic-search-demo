---
title: 窗口函数
date: 2026-08-15  # date-auto-injected
description: ClickHouse 窗口函数全集 + 用户留存 / 漏斗 / 排名实战
---

# 窗口函数

ClickHouse v20.x 后支持完整的 SQL 窗口函数（标准 SQL:2003）。

## 基础语法

```sql
SELECT
  user_id,
  event_time,
  amount,
  row_number() OVER (PARTITION BY user_id ORDER BY event_time) AS rn,
  rank() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rk,
  sum(amount) OVER (PARTITION BY user_id) AS user_total,
  avg(amount) OVER (PARTITION BY user_id ORDER BY event_time
                    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moving_avg
FROM events
```

## 排序函数

```sql
SELECT
  user_id,
  amount,
  row_number() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rn,
  rank() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rk,
  dense_rank() OVER (PARTITION BY user_id ORDER BY amount DESC) AS drk,
  percent_rank() OVER (PARTITION BY user_id ORDER BY amount) AS prk
FROM orders
```

| 函数 | 说明 |
|---|---|
| `row_number()` | 1, 2, 3, ...（无重复） |
| `rank()` | 1, 2, 2, 4（重复 + 跳号） |
| `dense_rank()` | 1, 2, 2, 3（重复 + 不跳号） |
| `percent_rank()` | (rank - 1) / (total_rows - 1) |

## 聚合窗口函数

```sql
SELECT
  user_id,
  event_date,
  amount,
  sum(amount) OVER (PARTITION BY user_id) AS user_total,
  sum(amount) OVER (PARTITION BY user_id ORDER BY event_date
                   ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_total,
  avg(amount) OVER (PARTITION BY user_id ORDER BY event_date
                   RANGE BETWEEN INTERVAL 7 DAY PRECEDING AND CURRENT ROW) AS moving_avg_7d,
  max(amount) OVER (PARTITION BY user_id ORDER BY event_date
                   ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS max_7d
FROM orders
```

**窗口帧 (Frame)**：

| 类型 | 说明 |
|---|---|
| `ROWS BETWEEN n PRECEDING AND m FOLLOWING` | 物理行窗口 |
| `RANGE BETWEEN INTERVAL n DAY PRECEDING AND CURRENT ROW` | 逻辑范围（按时间） |
| `GROUPS BETWEEN ...` | 组窗口 |

## 分析函数

```sql
-- 同比 / 环比
SELECT
  event_date,
  amount,
  lagInFrame(amount, 1) OVER (ORDER BY event_date) AS prev_day,
  lagInFrame(amount, 7) OVER (ORDER BY event_date) AS prev_week,
  amount / lagInFrame(amount, 1) OVER (ORDER BY event_date) - 1 AS day_over_day,
  amount / lagInFrame(amount, 7) OVER (ORDER BY event_date) - 1 AS week_over_week
FROM daily_sales

-- 累计
SELECT
  event_date,
  sum(amount) OVER (ORDER BY event_date) AS cumulative
FROM daily_sales
```

| 函数 | 说明 |
|---|---|
| `lagInFrame(x, n)` | 前 n 行 |
| `leadInFrame(x, n)` | 后 n 行 |
| `first_value(x)` | 分区第一个值 |
| `last_value(x)` | 分区最后一个值 |
| `nth_value(x, n)` | 分区第 n 个值 |

## 实战：用户留存分析

```sql
-- D1 / D7 / D30 留存
WITH
  toDate(event_time) AS dt
SELECT
  user_id,
  min(dt) AS signup_date,
  max(dt) AS last_active,
  dateDiff('day', min(dt), max(dt)) AS active_days
FROM events
WHERE event_date >= '2024-01-01'
GROUP BY user_id

-- cohort 留存（按注册月分组，看后续月份的活跃率）
SELECT
  toMonth(first_event) AS cohort_month,
  dateDiff('month', first_event, event_date) AS month_offset,
  uniq(user_id) AS active_users
FROM (
  SELECT user_id, min(toDate(event_time)) AS first_event
  FROM events
  GROUP BY user_id
) t1
JOIN events e ON t1.user_id = e.user_id
GROUP BY cohort_month, month_offset
ORDER BY cohort_month, month_offset
```

## 实战：漏斗分析

```sql
-- 注册 → 实名 → 首次下单 → 复购 漏斗
WITH funnel AS (
  SELECT
    user_id,
    max(event_type = 'register') AS is_register,
    max(event_type = 'verify') AS is_verify,
    max(event_type = 'first_order') AS is_first_order,
    max(event_type = 'repurchase') AS is_repurchase
  FROM events
  WHERE event_date >= '2024-01-01'
  GROUP BY user_id
)
SELECT
  sum(is_register) AS step1_register,
  sum(is_register * is_verify) AS step2_verify,
  sum(is_register * is_verify * is_first_order) AS step3_first_order,
  sum(is_register * is_verify * is_first_order * is_repurchase) AS step4_repurchase,
  step2_verify / step1_register AS conversion_1to2,
  step3_first_order / step2_verify AS conversion_2to3,
  step4_repurchase / step3_first_order AS conversion_3to4
FROM funnel
```

## 实战：用户活跃排名

```sql
-- 各国家 TOP 10 活跃用户
SELECT *
FROM (
  SELECT
    country,
    user_id,
    count() AS event_count,
    row_number() OVER (PARTITION BY country ORDER BY count() DESC) AS rn
  FROM events
  WHERE event_date >= today() - INTERVAL 30 DAY
  GROUP BY country, user_id
)
WHERE rn <= 10
ORDER BY country, rn
```

## CTE（公共表表达式）

ClickHouse 支持标准 CTE（v21.x+）：

```sql
WITH
  daily_active AS (
    SELECT event_date, uniq(user_id) AS dau
    FROM events
    WHERE event_date >= today() - INTERVAL 30 DAY
    GROUP BY event_date
  ),
  daily_new AS (
    SELECT
      toDate(first_event_time) AS signup_date,
      uniq(user_id) AS new_users
    FROM users
    GROUP BY signup_date
  )
SELECT
  a.event_date,
  a.dau,
  n.new_users,
  a.dau / n.new_users AS ratio
FROM daily_active a
LEFT JOIN daily_new n ON a.event_date = n.signup_date
```

## 窗口函数性能

### 物化（避免重复计算）

```sql
-- 创建宽表（每行带累计指标）
CREATE MATERIALIZED VIEW user_cumulative_mv
ENGINE = SummingMergeTree()
ORDER BY (user_id, event_date)
AS SELECT
  user_id,
  event_date,
  sum(amount) AS daily_amount,
  sum(amount) AS cumulative_amount  -- 由下游查询计算
FROM orders
GROUP BY user_id, event_date
```

### PARTITION BY 优化

确保 `PARTITION BY` 用最低基数维度，避免数据倾斜：

```sql
-- ✅ 好：按 user_id 分区
SELECT *, row_number() OVER (PARTITION BY user_id ORDER BY event_time)
FROM events

-- ❌ 差：按 city 分区（数据倾斜）
SELECT *, row_number() OVER (PARTITION BY city ORDER BY event_time)
FROM events
```

## 下一步

- 学习 JOIN：见 [join.md](./join.md)
- 学习表引擎：见 [03-table-engine/overview.md](../03-table-engine/overview.md)
