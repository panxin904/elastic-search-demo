---
title: 视图与物化视图
description: VIEW / MATERIALIZED VIEW
---

# 视图与物化视图

> **TL;DR**：视图 = 虚拟表（每次查询重算）。**物化视图 = 物理存储的查询结果**（可建索引、可加速报表 10x+）。

## 一句话定义

```
VIEW             = SQL 查询的"快捷方式"，不存储数据
MATERIALIZED VIEW = 查询结果的"缓存"，物理存储
```

## 普通 VIEW

```sql
-- 1. 创建
CREATE VIEW active_users AS
SELECT * FROM users WHERE is_active = true;

-- 2. 使用
SELECT * FROM active_users;
-- 等同于 SELECT * FROM users WHERE is_active = true

-- 3. 嵌套
CREATE VIEW active_admins AS
SELECT * FROM active_users WHERE role = 'admin';

-- 4. 删除
DROP VIEW active_users;
```

### 视图更新

```sql
-- 默认：只读
-- 简单视图可以 INSERT/UPDATE/DELETE
CREATE VIEW users_summary AS
SELECT id, name FROM users;

-- 可更新
INSERT INTO users_summary (id, name) VALUES (1, 'Alice');
-- 实际 INSERT INTO users
```

### INSTEAD OF 触发器（让任意视图可写）

```sql
CREATE VIEW users_view AS
SELECT id, name, email FROM users;

-- INSTEAD OF 触发器
CREATE FUNCTION insert_user_view() RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO users (id, name, email) 
  VALUES (NEW.id, NEW.name, NEW.email);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_view_insert
INSTEAD OF INSERT ON users_view
FOR EACH ROW EXECUTE FUNCTION insert_user_view();
```

## 物化视图（MATERIALIZED VIEW）

```sql
-- 1. 创建
CREATE MATERIALIZED VIEW daily_sales AS
SELECT
  date_trunc('day', created_at) AS day,
  count(*) AS order_count,
  sum(amount) AS total_amount
FROM orders
GROUP BY day
ORDER BY day;

-- 2. 加索引
CREATE UNIQUE INDEX idx_daily_sales_day ON daily_sales (day);

-- 3. 查询（毫秒级）
SELECT * FROM daily_sales WHERE day >= '2026-08-01';

-- 4. 刷新
REFRESH MATERIALIZED VIEW daily_sales;
-- 阻塞读，全量重建

-- 5. 并发刷新（PG 9.4+）
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_sales;
-- 不阻塞读，但需要 UNIQUE INDEX
```

## 视图 vs 物化视图

| 维度 | VIEW | MATERIALIZED VIEW |
|---|---|---|
| 存储 | 不存 |  | 物理存储 |
| 查询速度 | 实时计算 |  | 快速（已算好） |
| 实时性 | 100% |  | 取决于刷新频率 |
| 索引 | 不能建 |  | 可以 |
| 空间 | 0 |  | 取决于数据量 |

## 实战案例

### 案例 1：日报表

```sql
CREATE MATERIALIZED VIEW daily_sales AS
SELECT
  date_trunc('day', created_at) AS day,
  user_id,
  count(*) AS order_count,
  sum(amount) AS total_amount
FROM orders
WHERE created_at >= '2026-01-01'
GROUP BY day, user_id;

CREATE UNIQUE INDEX idx_daily_sales 
ON daily_sales (day, user_id);

-- pg_cron 定时刷新
SELECT cron.schedule('refresh-daily-sales', '0 1 * * *',
  'REFRESH MATERIALIZED VIEW CONCURRENTLY daily_sales');
```

### 案例 2：实时排行榜

```sql
-- 创建物化视图
CREATE MATERIALIZED VIEW top_products AS
SELECT
  product_id,
  sum(amount) AS total_sales,
  rank() OVER (ORDER BY sum(amount) DESC) AS rnk
FROM orders
WHERE created_at >= now() - interval '7 days'
GROUP BY product_id;

CREATE UNIQUE INDEX idx_top_products ON top_products (product_id);

-- 每 5 分钟刷新（自动）
-- 用 pg_cron 或应用层定时调用 REFRESH
```

### 案例 3：跨表预聚合

```sql
CREATE MATERIALIZED VIEW user_stats AS
SELECT
  u.id,
  u.name,
  count(o.id) AS order_count,
  coalesce(sum(o.amount), 0) AS total_spent,
  max(o.created_at) AS last_order_at
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

CREATE INDEX idx_user_stats_total ON user_stats (total_spent DESC);
```

## 性能优化

```sql
-- 1. 物化视图要 UNIQUE INDEX 才能并发刷新
CREATE UNIQUE INDEX idx_mv_id ON mv (id);

-- 2. 大物化视图分片刷新（PG 13+）
REFRESH MATERIALIZED VIEW CONCURRENTLY mv 
WITH (parallel_workers = 4);

-- 3. 自动刷新（pg_cron）
CREATE EXTENSION pg_cron;
SELECT cron.schedule('refresh-mv', '*/15 * * * *',
  'REFRESH MATERIALIZED VIEW CONCURRENTLY daily_sales');
```

## 一句话总结

> **VIEW = 虚拟表（实时算）、MATERIALIZED VIEW = 缓存表（预计算）**。**报表、排行榜、跨表聚合**用物化视图提速 10x+。**UNIQUE INDEX 是并发刷新的前提**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


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
