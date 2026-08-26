---
title: 统计信息
description: pg_stat / pg_stats 实战
---

# 统计信息

> **TL;DR**：PG 统计信息 = planner 决策的依据。**`pg_stat_*` 视图监控运行时**，**`pg_stats` 看列分布**，**`pg_stat_statements` 看 SQL 性能**。

## 一句话定义

```
统计信息 = PG 自动收集的运行时 / 列分布 / SQL 数据
        = planner 据此选最优执行计划
        = 监控的"眼睛"
```

## pg_stat_user_tables（表级）

```sql
SELECT
  schemaname, relname,
  seq_scan,                -- 顺序扫描次数
  seq_tup_read,            -- 顺序扫描读行数
  idx_scan,                -- 索引扫描次数
  idx_tup_fetch,           -- 索引扫描读取
  n_tup_ins,               -- 累计插入行数
  n_tup_upd,               -- 累计更新行数
  n_tup_del,               -- 累计删除行数
  n_live_tup,              -- 当前活元组数
  n_dead_tup,              -- 当前死元组数
  last_vacuum,             -- 上次手动 vacuum
  last_autovacuum,         -- 上次自动 vacuum
  last_analyze,            -- 上次手动 analyze
  last_autoanalyze         -- 上次自动 analyze
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
```

**实战 SQL**：

```sql
-- 找需要 vacuum 的表（死元组多）
SELECT relname, n_dead_tup, n_live_tup,
  ROUND(100 * n_dead_tup::numeric / NULLIF(n_live_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY dead_pct DESC;

-- 找未使用的索引（考虑删除）
SELECT schemaname, relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

## pg_stat_user_indexes（索引级）

```sql
SELECT
  schemaname, relname, indexrelname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch,
  pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## pg_statio_user_indexes（索引 IO）

```sql
SELECT
  schemaname, relname, indexrelname,
  idx_blks_read,           -- 磁盘读
  idx_blks_hit             -- 缓存命中
FROM pg_statio_user_indexes
ORDER BY idx_blks_read DESC;
```

## pg_stat_statements（SQL 级）

```sql
-- 1. 安装
CREATE EXTENSION pg_stat_statements;

-- 2. postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = top
pg_stat_statements.track_planning = on
```

**查询最耗资源的 SQL**：

```sql
-- 1. 总耗时 Top 10
SELECT
  substring(query, 1, 100) AS query,
  calls,
  ROUND(total_exec_time::numeric, 2) AS total_ms,
  ROUND(mean_exec_time::numeric, 2) AS mean_ms,
  ROWS
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- 2. 平均耗时 Top 10
SELECT
  substring(query, 1, 100) AS query,
  calls,
  ROUND(mean_exec_time::numeric, 2) AS mean_ms
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 3. 写多读多的 SQL
SELECT
  substring(query, 1, 100) AS query,
  calls,
  shared_blks_read,
  shared_blks_hit,
  ROUND(100 * shared_blks_hit::numeric / NULLIF(shared_blks_hit + shared_blks_read, 0), 2) AS hit_pct
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 10;

-- 4. 重置
SELECT pg_stat_statements_reset();
```

## pg_stats（列分布）

```sql
-- 看每列的统计信息
SELECT
  schemaname, tablename, attname,
  null_frac,              -- NULL 比例
  avg_width,              -- 平均宽度
  n_distinct,             -- distinct 值（-1 表示唯一）
  most_common_vals,       -- 最常见的值
  most_common_freqs,      -- 最常见值的频率
  histogram_bounds        -- 直方图边界
FROM pg_stats
WHERE tablename = 'users';

-- 手动触发统计更新
ANALYZE users;
ANALYZE VERBOSE users;  -- 显示更新内容
```

## pg_stat_activity（实时活动）

```sql
-- 当前所有活动连接
SELECT
  pid, usename, application_name,
  client_addr, backend_start,
  state, query_start, state_change,
  wait_event_type, wait_event,
  substring(query, 1, 100) AS query
FROM pg_stat_activity
WHERE pid != pg_backend_pid()
ORDER BY query_start;

-- 长事务
SELECT pid, xact_start, state, substring(query, 1, 50)
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND state != 'idle'
ORDER BY xact_start;
```

## pg_stat_replication（复制）

```sql
SELECT
  client_addr,
  state,
  sync_state,                       -- async / sync / potential
  sent_lsn, replay_lsn,
  pg_size_pretty(sent_lsn - replay_lsn) AS lag_bytes,
  EXTRACT(EPOCH FROM now() - reply_time) AS lag_seconds
FROM pg_stat_replication;
```

## 一句话总结

> **PG 统计 = 监控的眼睛**：**`pg_stat_user_tables`（表）+ `pg_stat_user_indexes`（索引）+ `pg_stat_statements`（SQL）**。**90% 性能问题从这 3 个视图就能定位**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
