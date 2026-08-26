---
title: 慢查询分析
description: pg_stat_statements + auto_explain + EXPLAIN
---

# 慢查询分析

> **TL;DR**：PG 慢查询分析的**三大武器**：`pg_stat_statements`（全局统计）、`auto_explain`（自动记录）、`EXPLAIN ANALYZE`（具体计划）。**生产环境 90% 慢查询靠这 3 个工具就能定位**。

## 一句话定义

```
慢查询分析 = 找出执行慢的 SQL + 分析为什么慢 + 优化索引/重写 SQL
```

## 三大武器

### 1. pg_stat_statements（全局统计）

**作用**：自动记录所有 SQL 的执行时间、调用次数、IO 等。

```sql
-- 1. 安装扩展
CREATE EXTENSION pg_stat_statements;

-- 2. 配置 postgresql.conf
shared_preload_libraries = 'pg_stat_statements'

# 推荐配置
pg_stat_statements.max = 10000
pg_stat_statements.track = top       # top-level SQL（去掉参数值）
pg_stat_statements.track_utility = on
pg_stat_statements.track_planning = on   # PG 13+，记录规划时间
pg_stat_statements.save = on         # 跨重启保留
```

**重启 PG 后生效**。

#### 查最慢的 SQL

```sql
-- 1. 总耗时 Top 10
SELECT
  substring(query, 1, 100) AS query,
  calls,
  ROUND(total_exec_time::numeric, 2) AS total_ms,
  ROUND(mean_exec_time::numeric, 2) AS mean_ms,
  ROUND((100 * total_exec_time / sum(total_exec_time) over ())::numeric, 2) AS pct
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- 2. 平均耗时 Top 10
SELECT
  substring(query, 1, 100) AS query,
  calls,
  ROUND(mean_exec_time::numeric, 2) AS mean_ms,
  shared_blks_hit + shared_blks_read AS total_blocks
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 3. 缓存命中率最低的
SELECT
  substring(query, 1, 100) AS query,
  calls,
  ROUND((100 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0))::numeric, 2) AS hit_pct,
  shared_blks_read AS disk_reads
FROM pg_stat_statements
ORDER BY disk_reads DESC
LIMIT 10;

-- 4. 临时文件使用最多（可能是 hash join spill）
SELECT
  substring(query, 1, 100) AS query,
  calls,
  temp_blks_read + temp_blks_written AS temp_blocks
FROM pg_stat_statements
WHERE temp_blks_read + temp_blks_written > 0
ORDER BY temp_blocks DESC
LIMIT 10;
```

> **生产经验**：如果某个 SQL 占总时间 30%+，**几乎一定是问题**。从那里开始优化。

### 2. auto_explain（自动记录慢查询）

**作用**：自动把执行计划记录到 PG 日志（不需要手动 EXPLAIN）。

```ini
# postgresql.conf
shared_preload_libraries = 'pg_stat_statements,auto_explain'

# 自动记录超过 1s 的查询
auto_explain.log_min_duration = '1s'
auto_explain.log_analyze = on           # 实际执行统计
auto_explain.log_buffers = on           # 缓冲命中
auto_explain.log_format = 'json'        # JSON 格式易解析
auto_explain.log_nested_statements = on
auto_explain.sample_rate = 1.0          # 全量记录
```

**日志输出**：

```
LOG: duration: 1823.456 ms  plan:
Query Text: SELECT * FROM orders WHERE user_id = $1
Sort  (cost=100..120 rows=1000 width=200) (actual time=1800..1820 rows=1000 loops=1)
  Sort Key: created_at DESC
  ->  Seq Scan on orders  (cost=0..90 rows=1000 width=200) (actual time=0.1..900 rows=1000 loops=1)
        Filter: (user_id = $1)
        Rows Removed by Filter: 999000
        Buffers: shared hit=30 read=5000
Planning Time: 0.2 ms
Execution Time: 1823.4 ms
```

> **亮点**：能立刻看到 "Seq Scan" + "Rows Removed by Filter: 999000"，**全表扫描 + 99.9% 行被过滤 = 加索引**。

### 3. EXPLAIN ANALYZE（手动分析）

**作用**：对单条 SQL 给出**真实执行计划**。

```sql
-- 基本 EXPLAIN
EXPLAIN SELECT * FROM orders WHERE user_id = 123;

-- EXPLAIN ANALYZE（真实执行）
EXPLAIN (ANALYZE, BUFFERS, TIMING, VERBOSE) 
SELECT * FROM orders WHERE user_id = 123;
```

**关键参数**：

| 参数 | 作用 |
|---|---|
| `ANALYZE` | 真实执行 SQL（会修改数据时用事务回滚） |
| `BUFFERS` | 显示共享缓冲命中 |
| `TIMING` | 每个节点耗时 |
| `VERBOSE` | 显示完整 schema 信息 |
| `FORMAT JSON` | JSON 输出（便于程序解析） |

**读取 EXPLAIN 输出**：

```
Sort  (cost=100..120 rows=1000) (actual time=1800..1820 rows=1000)
  Sort Key: created_at DESC
  Buffers: shared hit=30 read=5000
  
→ 重点看：
  - actual time = 真实执行时间
  - rows = 实际返回行数（vs 估算 rows）
  - Buffers = IO 数量
  - Seq Scan / Index Scan = 扫描方式
```

## 实战案例

### 案例 1：某接口 5s 超时

```sql
-- 1. pg_stat_statements 找出问题 SQL
SELECT substring(query, 1, 100), calls, mean_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC LIMIT 5;

-- 返回：
-- SELECT * FROM orders WHERE ... | 1234 | 4832.5
```

```sql
-- 2. EXPLAIN 看计划
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE user_id = 123 AND status = 'paid'
ORDER BY created_at DESC LIMIT 20;

-- 返回：
-- Limit (cost=...) (actual time=4832..4832 rows=20)
--   -> Sort (actual time=4832..4832)
--         Sort Key: created_at DESC
--         -> Seq Scan on orders (actual rows=500000)
--               Filter: ((user_id = 123) AND (status = 'paid'))
--               Rows Removed by Filter: 499980
--               Buffers: shared hit=10 read=20000

-- 3. 诊断：全表扫描 50 万行，过滤 99.9% → 缺索引
```

**修复**：

```sql
-- 加复合索引
CREATE INDEX idx_orders_user_status_created 
  ON orders (user_id, status, created_at DESC);

-- EXPLAIN 重跑
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE user_id = 123 AND status = 'paid'
ORDER BY created_at DESC LIMIT 20;

-- 返回：
-- Limit (actual time=0.05..0.1 rows=20)
--   -> Index Scan using idx_orders_user_status_created
--        Buffers: shared hit=5

-- 性能提升 48000 倍（4832ms → 0.1ms）
```

### 案例 2：缓存命中率低

```sql
-- pg_stat_statements 看缓存命中
SELECT
  substring(query, 1, 100),
  calls,
  shared_blks_read AS disk_reads,
  ROUND((100 * shared_blks_hit::numeric / 
         NULLIF(shared_blks_hit + shared_blks_read, 0))::numeric, 2) AS hit_pct
FROM pg_stat_statements
ORDER BY disk_reads DESC LIMIT 5;
```

**优化**：

```sql
-- 1. 看数据库整体缓存命中率
SELECT
  sum(blks_hit) / NULLIF(sum(blks_hit + blks_read), 0) AS db_cache_hit_ratio
FROM pg_stat_database;

-- 期望 > 99%

-- 2. 调大 shared_buffers
shared_buffers = '8GB'    # 默认 128MB，生产推荐 25% RAM

-- 3. 调大 effective_cache_size（planner 决策用）
effective_cache_size = '24GB'  # 推荐 50-75% RAM
```

### 案例 3：临时文件爆炸

```sql
-- 找用临时文件的 SQL
SELECT
  query,
  calls,
  temp_blks_written * 8192 / calls AS avg_temp_bytes
FROM pg_stat_statements
WHERE temp_blks_written > 0
ORDER BY temp_blks_written DESC LIMIT 5;
```

**原因**：
- Hash Join spill 到磁盘
- Sort 排序超过 `work_mem`

**修复**：

```ini
# 1. 调大 work_mem（默认值 4MB 偏小）
work_mem = '64MB'

# 2. 重写 SQL 避免大排序
#    用索引避免排序
#    用 LIMIT 限制结果集

# 3. 增加 hash_mem_multiplier（PG 13+）
hash_mem_multiplier = 2.0  # hash join 内存倍数
```

## 优化套路

### 第一招：加索引

```sql
-- 1. 看哪些表缺索引
SELECT
  schemaname, relname,
  seq_scan,           -- 顺序扫描次数
  seq_tup_read,
  idx_scan,           -- 索引扫描次数
  n_live_tup
FROM pg_stat_user_tables
WHERE seq_scan > 1000
ORDER BY seq_tup_read DESC;

-- 高 seq_scan + seq_tup_read → 加索引
```

### 第二招：覆盖索引

```sql
-- 索引包含所有查询字段（避免回表）
CREATE INDEX idx_orders_covering
  ON orders (user_id, status)
  INCLUDE (created_at, amount);

-- 查询只用索引
EXPLAIN SELECT user_id, status, created_at, amount
FROM orders WHERE user_id = 123 AND status = 'paid';

-- → Index Only Scan（不读表）
```

### 第三招：分页优化

```sql
-- ❌ OFFSET 越大越慢
SELECT * FROM orders 
ORDER BY id 
LIMIT 20 OFFSET 1000000;  -- 扫 100 万行

-- ✅ 游标分页
SELECT * FROM orders 
WHERE id > 1000000  -- 上次最大 id
ORDER BY id 
LIMIT 20;
```

### 第四招：避免函数包裹索引列

```sql
-- ❌ 函数让索引失效
SELECT * FROM users WHERE date(created_at) = '2026-08-09';

-- ✅ 等价但能用索引
SELECT * FROM users 
WHERE created_at >= '2026-08-09' AND created_at < '2026-08-10';
```

### 第五招：JOIN 顺序优化

```sql
-- 统计信息收集
ANALYZE users;
ANALYZE orders;

-- 强制 JOIN 顺序（小表驱动大表）
SELECT /*+ Leading(u o) */ *
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active';
```

## 常用监控 SQL

```sql
-- 1. 当前运行的查询（看谁在慢）
SELECT
  pid,
  now() - query_start AS duration,
  state,
  wait_event_type,
  wait_event,
  substring(query, 1, 100)
FROM pg_stat_activity
WHERE state != 'idle'
  AND query NOT LIKE '%pg_stat_activity%'
ORDER BY duration DESC;

-- 2. 长时间事务
SELECT
  pid,
  now() - xact_start AS xact_duration,
  state,
  substring(query, 1, 100)
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_duration DESC
LIMIT 10;

-- 3. 锁等待
SELECT
  blocked.pid AS blocked_pid,
  blocking.pid AS blocking_pid,
  blocked.query AS blocked_query,
  blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid
JOIN pg_locks kl ON kl.locktype = bl.locktype
  AND kl.database IS NOT DISTINCT FROM bl.database
  AND kl.relation IS NOT DISTINCT FROM bl.relation
  AND kl.page IS NOT DISTINCT FROM bl.page
  AND kl.tuple IS NOT DISTINCT FROM bl.tuple
  AND kl.transactionid IS NOT DISTINCT FROM bl.transactionid
  AND kl.pid != bl.pid
  AND kl.granted
JOIN pg_stat_activity blocking ON blocking.pid = kl.pid
WHERE NOT bl.granted;
```

## 一句话总结

> **慢查询分析三件套**：`pg_stat_statements` 全局找问题 SQL，`auto_explain` 自动记录，`EXPLAIN ANALYZE` 详细诊断。**90% 慢查询是缺索引 + 全表扫描**，加索引能从 5s 降到 0.1s。

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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 对比
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
- [system-design](https://java-px.bot.cd/system-design/):数据库选型
