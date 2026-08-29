---
title: performance_schema
date: 2026-08-15  # date-auto-injected
---

# 🔬 MySQL performance_schema

> performance_schema 是 MySQL 5.5+ 提供的**内置性能监控框架**，可以观测到 MySQL 内部的运行细节，是定位深层次问题的利器。

## 🎯 performance_schema 是什么？

performance_schema 是 MySQL **引擎级的监控框架**，在存储引擎层采集性能数据。

```
┌──────────────────────────────────┐
│       MySQL Server                │
│                                  │
│   ┌──────────────────────────┐   │
│   │  performance_schema       │   │
│   │  (性能监控引擎)          │   │
│   └──────────────────────────┘   │
│            ↓                       │
│   采集各种性能数据                  │
│   - 语句执行                        │
│   - 锁等待                          │
│   - IO 统计                          │
│   - 内存使用                        │
│   - 连接信息                        │
└──────────────────────────────────┘
            ↓
   通过 SQL 查询这些数据
```

## 🚀 快速启用

```sql
-- 查看是否启用
SHOW VARIABLES LIKE 'performance_schema';

-- 默认 ON（MySQL 5.6.6+）
-- performance_schema = ON

-- 主要配置项
SHOW VARIABLES LIKE 'performance_schema%';
```

## 📊 核心表分类

### 1. 语句事件（最常用）

```sql
-- 查看最耗时的 SQL（按总时间排序）
SELECT
  digest_text,
  count_star AS exec_count,
  sum_timer_wait / 1000000000 AS total_ms,
  avg_timer_wait / 1000000 AS avg_ms,
  max_timer_wait / 1000000 AS max_ms
FROM performance_schema.events_statements_summary_by_digest
WHERE schema_name = 'mydb'
ORDER BY sum_timer_wait DESC
LIMIT 20;
```

### 2. 锁等待

```sql
-- 查看当前锁等待
SELECT
  t.trx_id,
  t.trx_state,
  t.trx_started,
  TIMESTAMPDIFF(SECOND, t.trx_started, NOW()) AS duration_sec,
  t.trx_query,
  GROUP_CONCAT(DISTINCT lw.blocking_trx_id) AS blocking_trx_ids
FROM information_schema.innodb_trx t
LEFT JOIN performance_schema.data_lock_waits lw
  ON t.trx_id = lw.waiting_trx_id
GROUP BY t.trx_id;
```

### 3. IO 统计

```sql
-- 查看表 IO 统计
SELECT
  object_schema,
  object_name,
  count_read,
  count_write,
  count_fetch,
  count_insert,
  count_update,
  count_delete,
  sum_timer_read / 1000000000 AS read_seconds
FROM performance_schema.table_io_waits_summary_by_table
WHERE object_schema = 'mydb'
ORDER BY count_read + count_write DESC
LIMIT 20;

-- 查看文件 IO
SELECT
  file_name,
  count_read,
  count_write,
  sum_number_of_bytes_read / 1024 / 1024 AS read_mb,
  sum_number_of_bytes_write / 1024 / 1024 AS write_mb
FROM performance_schema.file_io_by_event_name
ORDER BY read_mb + write_mb DESC
LIMIT 10;
```

### 4. 索引使用

```sql
-- 查看索引使用情况
SELECT
  object_schema,
  object_name,
  index_name,
  count_star AS rows_read,
  sum_timer_wait / 1000000000 AS total_ms
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'mydb'
  AND index_name IS NOT NULL
ORDER BY count_star DESC;
```

## 🎯 实战案例

### 案例 1：定位慢 SQL

```sql
-- 找出最耗时的 20 个 SQL
SELECT
  schema_name,
  digest_text,
  count_star AS exec_count,
  ROUND(avg_timer_wait / 1000000, 2) AS avg_ms,
  ROUND(max_timer_wait / 1000000, 2) AS max_ms,
  ROUND(sum_timer_wait / 1000000, 2) AS total_ms,
  sum_rows_examined,
  sum_rows_sent
FROM performance_schema.events_statements_summary_by_digest
WHERE schema_name IS NOT NULL
ORDER BY sum_timer_wait DESC
LIMIT 20;
```

### 案例 2：定位锁等待

```sql
-- 查看谁在等待谁
SELECT
  waiting_trx_id,
  waiting_pid,
  waiting_query,
  blocking_trx_id,
  blocking_pid,
  blocking_query
FROM performance_schema.data_lock_waits
LIMIT 20;

-- 更详细的信息
SELECT
  t.trx_id,
  t.trx_state,
  t.trx_started,
  TIMESTAMPDIFF(SECOND, t.trx_started, NOW()) AS waited_sec,
  t.trx_mysql_thread_id,
  t.trx_query,
  lw.blocking_trx_id,
  lw.blocking_trx_mysql_thread_id
FROM information_schema.innodb_trx t
INNER JOIN performance_schema.data_lock_waits lw
  ON t.trx_id = lw.waiting_trx_id;
```

### 案例 3：查找未使用的索引

```sql
-- 找出从不被使用的索引（考虑删除）
SELECT
  object_schema,
  object_name,
  index_name
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'mydb'
  AND index_name IS NOT NULL
  AND count_star = 0
  AND index_name != 'PRIMARY'
ORDER BY object_name, index_name;
```

### 案例 4：IO 热点表

```sql
-- 找出 IO 最多的表
SELECT
  object_schema,
  object_name,
  count_read + count_write AS total_io,
  ROUND((sum_timer_read + sum_timer_write) / 1000000, 2) AS total_ms
FROM performance_schema.table_io_waits_summary_by_table
WHERE object_schema NOT IN ('mysql', 'sys')
ORDER BY total_io DESC
LIMIT 20;
```

### 案例 5：连接来源统计

```sql
-- 查看每个主机的连接数
SELECT
  host,
  current_connections,
  total_connections
FROM performance_schema.host_cache
ORDER BY total_connections DESC
LIMIT 20;
```

## 🔧 配置和优化

### 启用更详细的监控

```sql
-- 启用事件收集（默认 ON）
UPDATE performance_schema.setup_instruments
SET enabled = 'YES'
WHERE name LIKE 'statement/%';

UPDATE performance_schema.setup_instruments
SET enabled = 'YES'
WHERE name LIKE 'wait/%';

UPDATE performance_schema.setup_instruments
SET enabled = 'YES'
WHERE name LIKE 'memory/%';
```

### 控制 performance_schema 内存

```sql
-- 查看 performance_schema 内存使用
SHOW ENGINE PERFORMANCE_SCHEMA STATUS\G
```

```ini
# my.cnf 配置
[mysqld]
performance_schema = ON
performance_schema_max_table_instances = 12500
performance_schema_max_statement_stack = 10
```

## 📊 常用表速查

| 表名 | 用途 |
|---|---|
| events_statements_summary_by_digest | SQL 统计（最常用） |
| events_waits_summary_global_by_event_name | 等待事件统计 |
| table_io_waits_summary_by_table | 表 IO 统计 |
| table_io_waits_summary_by_index_usage | 索引使用统计 |
| data_lock_waits | 锁等待 |
| file_io_by_event_name | 文件 IO |
| host_cache | 连接信息 |
| memory_summary_global_by_event_name | 内存使用 |
| setup_instruments | 监控项配置 |
| setup_consumers | 消费者配置 |

## 🎯 完整排查流程

```sql
-- 1. 找出最耗时的 SQL
SELECT digest_text, sum_timer_wait
FROM performance_schema.events_statements_summary_by_digest
ORDER BY sum_timer_wait DESC LIMIT 10;

-- 2. 查看该 SQL 的执行统计
SELECT * FROM performance_schema.events_statements_summary_by_digest
WHERE digest_text LIKE '%SELECT%FROM orders%';

-- 3. 查看是否有锁等待
SELECT * FROM performance_schema.data_lock_waits LIMIT 10;

-- 4. 查看 IO 情况
SELECT * FROM performance_schema.table_io_waits_summary_by_table
WHERE object_name = 'orders';

-- 5. 查看索引使用
SELECT * FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_name = 'orders';
```

## 🛠️ 与 sys schema 结合使用

MySQL 5.7+ 自带 **sys schema**，是基于 performance_schema 的封装，提供更友好的视图：

```sql
-- 查看最耗时的 SQL（sys schema 简化版）
SELECT * FROM sys.statement_analysis
ORDER BY total_latency DESC
LIMIT 10;

-- 查看未使用的索引
SELECT * FROM sys.schema_unused_indexes;

-- 查看冗余索引
SELECT * FROM sys.schema_redundant_indexes;

-- 查看全表扫描
SELECT * FROM sys.tables_with_full_table_scans;

-- 查看 IO 热点表
SELECT * FROM sys.io_global_by_file_by_bytes
ORDER BY total DESC LIMIT 10;
```

## 🎯 总结

**performance_schema 核心：**
- ✅ MySQL 内置性能监控
- ✅ 采集引擎级数据
- ✅ 零侵入（不需修改应用）
- ✅ 详细到每个 SQL 的资源消耗

**常用查询：**
- `events_statements_summary_by_digest`：SQL 统计
- `data_lock_waits`：锁等待
- `table_io_waits_summary_by_*`：IO 统计
- `sys.*` 视图：更易用

**下一步：** [📊 Prometheus + mysqld_exporter](../09-monitoring/prometheus) — 生产级监控方案