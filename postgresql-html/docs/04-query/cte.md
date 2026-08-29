---
title: CTE 公用表表达式
date: 2026-08-15  # date-auto-injected
---

# CTE 公用表表达式

> WITH 子句 + 临时命名结果集，让 SQL 像写代码一样可读。**CTE 是 SQL 的"局部变量"**。

## 1. 什么是 CTE？

```
CTE（Common Table Expression）：
  - WITH 子句定义的临时结果集
  - 后续 SELECT 可以引用
  - 生命周期：当前查询内

基本语法：
  WITH cte_name AS (
    SELECT ...
  )
  SELECT * FROM cte_name;

优势：
  - 可读性：复杂查询拆成多个 CTE
  - 重用：同一 CTE 多次引用
  - 递归：支持递归 CTE（树形 / 图形遍历）
  - 维护：分层组织，每个 CTE 一个职责

📌 MySQL 8.0+ 才有 CTE
   PG 8.4+ 就支持 CTE（2010 年）
   PG 是 CTE 的发源地之一
```

## 2. 基本用法

### 2.1 单个 CTE

```sql
-- 高消费用户
WITH high_value AS (
  SELECT user_id, SUM(amount) AS total
  FROM orders
  WHERE status = 'paid'
  GROUP BY user_id
  HAVING SUM(amount) > 10000
)
SELECT u.name, h.total
FROM users u
JOIN high_value h ON u.id = h.user_id
ORDER BY h.total DESC;
```

### 2.2 多个 CTE（逗号分隔）

```sql
WITH
  active_users AS (
    SELECT id, name FROM users WHERE last_login > NOW() - INTERVAL '30 days'
  ),
  recent_orders AS (
    SELECT user_id, amount FROM orders
    WHERE created_at > NOW() - INTERVAL '7 days'
  ),
  user_stats AS (
    SELECT a.id, a.name, COALESCE(SUM(r.amount), 0) AS recent_total
    FROM active_users a
    LEFT JOIN recent_orders r ON r.user_id = a.id
    GROUP BY a.id, a.name
  )
SELECT * FROM user_stats
WHERE recent_total > 1000
ORDER BY recent_total DESC
LIMIT 100;
```

### 2.3 CTE 中使用 DML

```sql
-- CTE 中可以 INSERT/UPDATE/DELETE
-- 一次完成多步操作

WITH moved_users AS (
  UPDATE users
  SET status = 'archived'
  WHERE last_login < NOW() - INTERVAL '1 year'
  RETURNING id, name
)
INSERT INTO user_archive (user_id, user_name, archived_at)
SELECT id, name, NOW() FROM moved_users;
```

## 3. 递归 CTE

### 3.1 树形查询

```sql
-- 员工-经理关系
CREATE TABLE employees (
  id       INT PRIMARY KEY,
  name     TEXT,
  manager_id INT REFERENCES employees(id)
);

-- 递归：找出某员工的所有下属
WITH RECURSIVE org_tree AS (
  -- 基础查询：起点
  SELECT id, name, manager_id, 0 AS depth
  FROM employees
  WHERE id = 1  -- CEO

  UNION ALL

  -- 递归查询：下属
  SELECT e.id, e.name, e.manager_id, t.depth + 1
  FROM employees e
  JOIN org_tree t ON e.manager_id = t.id
)
SELECT * FROM org_tree ORDER BY depth;
```

### 3.2 图遍历

```sql
-- 查找两个节点间的路径
WITH RECURSIVE path AS (
  SELECT
    start_node AS node,
    ARRAY[start_node] AS visited,
    0 AS distance
  FROM nodes
  WHERE id = 1

  UNION ALL

  SELECT
    e.end_node,
    p.visited || e.end_node,
    p.distance + e.weight
  FROM edges e
  JOIN path p ON e.start_node = p.node
  WHERE e.end_node <> ALL(p.visited)  -- 防止环
)
SELECT * FROM path ORDER BY distance;
```

### 3.3 数字序列

```sql
-- 生成 1-100 的序列
WITH RECURSIVE nums AS (
  SELECT 1 AS n
  UNION ALL
  SELECT n + 1 FROM nums WHERE n < 100
)
SELECT * FROM nums;
```

### 3.4 日期序列

```sql
-- 生成最近 30 天的日期
WITH RECURSIVE dates AS (
  SELECT CURRENT_DATE - INTERVAL '29 days' AS d
  UNION ALL
  SELECT d + INTERVAL '1 day' FROM dates WHERE d < CURRENT_DATE
)
SELECT d FROM dates;
```

## 4. 物化 vs 非物化

### 4.1 PG 12 之前：默认物化

```sql
-- PG 默认：CTE 被物化（优化器视为独立单元）
WITH t AS (SELECT * FROM big_table)
SELECT * FROM t WHERE id = 1;
-- 执行：先完整执行 SELECT * FROM big_table，存为 t，再查 t

-- 优点：CTE 内只执行一次
-- 缺点：可能错失优化机会（如谓词下推）
```

### 4.2 PG 12+：可控制

```sql
-- NOT MATERIALIZED：不物化，CTE 内联到主查询
WITH t AS NOT MATERIALIZED (SELECT * FROM big_table)
SELECT * FROM t WHERE id = 1;
-- 执行：直接把 t 替换为子查询，谓词下推到 big_table
-- 适用于：CTE 只用一次 + 主查询有过滤条件

-- MATERIALIZED（默认）：物化
WITH t AS MATERIALIZED (SELECT * FROM big_table)
SELECT count_1 FROM t, other_table
WHERE t.id = other_table.t_id;
-- 适用于：CTE 用多次，或聚合结果
```

### 4.3 性能对比

```sql
-- ❌ 慢：CTE 物化 + 主查询过滤（PG 12 之前常见问题）
WITH recent_orders AS (
  SELECT * FROM orders WHERE created_at > '2024-01-01'
)
SELECT * FROM recent_orders WHERE user_id = 1001;
-- 实际执行：扫全 orders，再过滤时间，再过滤 user

-- ✅ 优化：NOT MATERIALIZED
WITH recent_orders AS NOT MATERIALIZED (
  SELECT * FROM orders WHERE created_at > '2024-01-01'
)
SELECT * FROM recent_orders WHERE user_id = 1001;
-- 实际执行：直接下推 user_id = 1001 + 时间过滤
```

## 5. 工程实践

### 5.1 复杂报表

```sql
-- 月度销售报表
WITH
  monthly_sales AS (
    SELECT
      DATE_TRUNC('month', created_at) AS month,
      user_id,
      SUM(amount) AS sales
    FROM orders
    WHERE status = 'paid'
    GROUP BY 1, 2
  ),
  monthly_total AS (
    SELECT month, SUM(sales) AS total
    FROM monthly_sales
    GROUP BY month
  ),
  top_users AS (
    SELECT
      month,
      user_id,
      sales,
      ROW_NUMBER() OVER (PARTITION BY month ORDER BY sales DESC) AS rk
    FROM monthly_sales
  )
SELECT
  mt.month,
  mt.total,
  tu.user_id,
  u.name,
  tu.sales AS user_sales,
  ROUND(tu.sales / mt.total * 100, 2) AS pct
FROM monthly_total mt
JOIN top_users tu ON mt.month = tu.month
JOIN users u ON u.id = tu.user_id
WHERE tu.rk <= 10
ORDER BY mt.month DESC, tu.rk;
```

### 5.2 数据迁移

```sql
-- 把老表数据迁移到新表
WITH
  old_data AS (
    SELECT * FROM legacy_orders WHERE migrated = FALSE LIMIT 1000
  ),
  inserted AS (
    INSERT INTO new_orders (user_id, amount, created_at)
    SELECT user_id, amount, created_at FROM old_data
    RETURNING legacy_id
  ),
  updated AS (
    UPDATE legacy_orders
    SET migrated = TRUE
    WHERE id IN (SELECT legacy_id FROM inserted)
    RETURNING id
  )
SELECT COUNT(*) FROM updated;
```

### 5.3 权限控制

```sql
-- 用 CTE 模拟复杂权限
WITH
  accessible_orders AS (
    SELECT o.*
    FROM orders o
    JOIN user_permissions p ON p.user_id = o.user_id
    WHERE p.user_id = current_user_id()
      AND p.can_view = TRUE
  )
SELECT * FROM accessible_orders;
```

## 6. CTE vs 子查询

| 维度 | CTE | 子查询 |
|---|---|---|
| 可读性 | 优（命名 + 分层） | 差（嵌套深） |
| 重用 | 同 CTE 可多次引用 | 需重复写 |
| 递归 | 支持 | 不支持 |
| 性能 | 可控（NOT MATERIALIZED） | 通常内联 |
| 优化器 | PG 12+ 可控 | 通常内联 |

📌 复杂查询用 CTE，简单查询用子查询
   递归必须 CTE

## 7. 经典案例

### 7.1 树形菜单

```sql
-- 多级分类树
WITH RECURSIVE category_tree AS (
  SELECT id, name, parent_id, 0 AS depth, name::TEXT AS path
  FROM categories
  WHERE parent_id IS NULL

  UNION ALL

  SELECT c.id, c.name, c.parent_id, t.depth + 1,
         t.path || ' > ' || c.name
  FROM categories c
  JOIN category_tree t ON c.parent_id = t.id
)
SELECT * FROM category_tree ORDER BY path;
```

### 7.2 用户推荐（共同好友）

```sql
-- 找出用户 A 的"好友的好友"（二度关系）
WITH RECURSIVE
  friends AS (
    SELECT friend_id FROM friendships WHERE user_id = 1001
  ),
  friends_of_friends AS (
    SELECT f2.friend_id
    FROM friendships f2
    JOIN friends f ON f.friend_id = f2.user_id
    WHERE f2.friend_id != 1001
      AND f2.friend_id NOT IN (SELECT friend_id FROM friends)
  )
SELECT u.id, u.name, COUNT(*) AS mutual_count
FROM friends_of_friends fof
JOIN users u ON u.id = fof.friend_id
JOIN friendships f1 ON f1.user_id = 1001 AND f1.friend_id = fof.friend_id
GROUP BY u.id, u.name
ORDER BY mutual_count DESC
LIMIT 20;
```

## 8. 性能陷阱

### 8.1 物化误用

```sql
-- ❌ CTE 用了 3 次，但每次都能下推
WITH t AS (SELECT * FROM big_table WHERE filter1 = 'X')
SELECT * FROM t WHERE filter2 = 'Y';  -- 只用一次，本应内联

-- ✅ PG 12+：NOT MATERIALIZED
WITH t AS NOT MATERIALIZED (SELECT * FROM big_table WHERE filter1 = 'X')
SELECT * FROM t WHERE filter2 = 'Y';
```

### 8.2 递归深度

```sql
-- 递归 CTE 默认无限，可能栈溢出
WITH RECURSIVE t AS (... UNION ALL ...)
SELECT * FROM t;

-- 实际场景：树深度有限，但需要兜底
-- PG 14+：CYCLE 检测
WITH RECURSIVE t AS (
  SELECT ... FROM employees WHERE id = 1
  UNION ALL
  SELECT ... FROM employees e JOIN t ON e.manager_id = t.id
) CYCLE id SET is_cycle USING path
SELECT * FROM t WHERE NOT is_cycle;
```

### 8.3 多次引用

```sql
-- CTE 用 2+ 次时，物化才划算
WITH t AS (SELECT ... 聚合 ...)
SELECT * FROM t
UNION ALL
SELECT * FROM t
WHERE ...;
-- t 只算 1 次
```

## 9. 一句话总结

```
📌 CTE = WITH 子句 + 临时命名结果集，SQL 的"局部变量"
📌 优势：可读、可重用、支持递归
📌 递归 CTE：树形查询、图遍历、序列生成
📌 物化控制：PG 12+ 用 NOT MATERIALIZED 让谓词下推
📌 DML 可用 CTE：INSERT/UPDATE/DELETE 一次完成多步
📌 适合：复杂报表 / 数据迁移 / 树形查询 / 权限过滤
📌 性能：合理用 CTE 能极大提升可读性，性能可控
📌 vs 子查询：复杂场景选 CTE，递归只能用 CTE
```

## 10. 参考资料

- PostgreSQL 8.4 CTE 引入
- PostgreSQL 12 CTE 物化控制
- PostgreSQL 14 CYCLE 检测
- "SQL 性能优化"（PG 中文社区）
- Hacker News 关于 CTE vs 子查询的讨论
- WITH RECURSIVE 官方文档


<!-- auto-enrich:do-not-edit -->

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
