---
title: Vacuum 与 autovacuum
date: 2026-08-15  # date-auto-injected
description: PostgreSQL MVCC 垃圾回收机制
---

# Vacuum 与 Autovacuum

> **TL;DR**：PostgreSQL 用 MVCC 实现事务隔离，更新/删除的"旧版本"留在表里，**vacuum 把死元组（dead tuples）清理掉**。autovacuum 是后台自动清理守护进程。**不调优 autovacuum = 表膨胀 + 查询变慢 + 事务回卷（XID wraparound）**。

## 一句话定义

| 概念 | 含义 |
|---|---|
| **MVCC** | 多版本并发控制，每次 UPDATE/DELETE 不立即删除旧版本 |
| **Dead tuple** | 被 UPDATE/DELETE 标记但仍占空间的旧版本 |
| **VACUUM** | 回收 dead tuple 占用的空间，可重用 |
| **VACUUM FULL** | 把表重写，**真正回收**空间（锁表） |
| **autovacuum** | 后台守护进程，自动触发 VACUUM/ANALYZE |
| **Freeze** | 把元组的 xmin 标记为"非常旧"，防止 XID 回卷 |
| **XID wraparound** | 32 位事务 ID 用尽后会丢数据，必须防止 |

## 为什么需要 Vacuum

PG 用 MVCC 实现高并发：

```sql
-- 表 users 有 100 万行
UPDATE users SET name = 'new' WHERE id = 1;
-- 旧版本（name='old'）没有被删除，而是标记为 dead
-- 新版本（name='new'）被插入

-- 表占用的空间 ≠ 实际有效数据量
-- 可能 100 万行 → 物理上 200 万行（活的 + 死的）
```

**不 vacuum 的后果**：

| 时间 | 问题 | 现象 |
|---|---|---|
| 短期 | 表膨胀（bloat） | 同样的数据量占用 5x 磁盘空间 |
| 中期 | 查询变慢 | 索引扫描要跳过的 dead tuple 越来越多 |
| 长期 | XID 接近回卷点 | PG 进入保护模式，强制 vacuum |
| 极端 | XID 回卷 | **数据丢失** |

## VACUUM vs VACUUM FULL

| 维度 | VACUUM | VACUUM FULL |
|---|---|---|
| 空间回收 | 标记可重用，**不归还**磁盘 | 重写表，**真正归还**磁盘 |
| 锁 | 不锁表 | 排他锁（AccessExclusive） |
| 执行时间 | 快 | 慢（重写整个表） |
| 适合场景 | 日常清理 | 表膨胀严重时 |

```sql
-- 普通 vacuum（推荐）
VACUUM (VERBOSE, ANALYZE) users;

-- 强制 vacuum（即使被禁用也跑）
VACUUM (VERBOSE, ANALYZE, FORCE) users;

-- 真正回收空间（业务低峰）
VACUUM FULL users;  -- ⚠️ 锁表，会阻塞读写
```

> **生产经验**：日常靠 autovacuum，**不要手动跑 VACUUM FULL**。bloat 实在严重，用 pg_repack 工具在线重建。

## Autovacuum 调优

### 关键参数

```ini
# postgresql.conf

# 1. 是否启用（默认 on）
autovacuum = on

# 2. 触发阈值（默认 50）
#    当 dead tuples 超过 50 + 表行数 × 0.2 时触发
autovacuum_vacuum_threshold = 50
autovacuum_vacuum_scale_factor = 0.2

# 3. 成本限制（防止 vacuum 占满 IO）
autovacuum_vacuum_cost_limit = 200       # 默认 200
autovacuum_vacuum_cost_delay = 20ms      # 默认 20ms

# 4. 工作进程数
autovacuum_max_workers = 3              # 默认 3，生产可调到 4-6

# 5. vacuum 触发频率
autovacuum_naptime = 60s                # 默认 60s 检测一次

# 6. 是否自动 ANALYZE
autovacuum_analyze_threshold = 50
autovacuum_analyze_scale_factor = 0.1
```

### 高频小表调优（推荐）

很多生产 PG 表是"小但更新频繁"，默认参数会导致 vacuum 永远不触发。

```sql
-- 针对特定表的调优（override 全局参数）
ALTER TABLE users SET (
  autovacuum_vacuum_scale_factor = 0.05,    -- 5% 死元组就触发
  autovacuum_analyze_scale_factor = 0.025,  -- 2.5% 行数变化就 analyze
  autovacuum_vacuum_cost_limit = 1000       -- 这个表的 vacuum 可以跑快一点
);
```

### 监控 autovacuum

```sql
-- 1. 看 autovacuum 是否在工作
SELECT datname, usename, pid, state, query_start, wait_event_type
FROM pg_stat_activity
WHERE query LIKE '%autovacuum%';

-- 2. 看每个表的 vacuum 统计
SELECT
  schemaname, relname,
  n_live_tup, n_dead_tup,
  last_vacuum, last_autovacuum,
  last_analyze, last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;

-- 3. 死元组占比超过 10% 报警
SELECT
  schemaname, relname,
  n_dead_tup::float / NULLIF(n_live_tup, 0) AS dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY dead_ratio DESC;
```

## Freeze 与 XID Wraparound

**为什么需要 freeze**：

PG 的事务 ID（XID）是 32 位 int，**最大 2^31 ≈ 21 亿**。如果一直不 freeze，XID 会从 0 → 2^31 → 重置为 0，**等于"穿越回过去"**，原本"未来"的事务会变成"过去"，数据丢失。

```sql
-- 查看当前 XID 距离耗尽还有多远
SELECT
  age(datfrozenxid) AS oldest_xid_age,
  current_setting('autovacuum_freeze_max_age') AS freeze_max_age,
  age(datfrozenxid)::float / current_setting('autovacuum_freeze_max_age')::float AS pct_toward_wraparound
FROM pg_database;

-- pct_toward_wraparound > 0.75 就要警觉
-- > 0.9 PG 进入保护模式，强制 vacuum
```

**freeze 的工作原理**：

```sql
-- autovacuum 周期性地 freeze 很旧的元组
-- 把它们的 xmin 设为 2（特殊值，表示"对所有事务可见"）
-- 这样这些元组不再占用 XID 空间
```

### 监控告警

```sql
-- 1. 找最老的 XID
SELECT relname, age(relfrozenxid) AS xid_age
FROM pg_class
WHERE relkind = 'r'
ORDER BY age(relfrozenxid) DESC
LIMIT 10;

-- 2. 数据库级别
SELECT datname, age(datfrozenxid) FROM pg_database;
```

> **告警阈值**：单个表的 `age(relfrozenxid) > 200,000,000`（2 亿）就要警惕。超过 5 亿 PG 会进入只读保护模式。

## 表膨胀（Bloat）诊断与治理

### 用 pgstattuple 估算 bloat

```sql
-- 1. 安装扩展
CREATE EXTENSION pgstattuple;

-- 2. 看单表 bloat
SELECT * FROM pgstattuple('users');

-- 返回：
-- table_len | tuple_count | tuple_len | dead_tuple_count | dead_tuple_len | free_space | free_percent
-- 100MB    | 100000      | 30MB      | 50000            | 15MB           | 30MB       | 30%
-- 意味着：30% 磁盘空间浪费
```

### 用 pgstattuple 找 bloat 表

```sql
-- 找 bloat 严重的表（生产推荐用这个 SQL）
WITH bloat AS (
  SELECT
    schemaname || '.' || tablename AS table_name,
    pg_size_pretty(pg_relation_size(schemaname || '.' || tablename)) AS size,
    ROUND(100 * (pg_relation_size(schemaname || '.' || tablename)::numeric
          - pg_relation_size(schemaname || '.' || tablename, 'main')::numeric)
          / NULLIF(pg_relation_size(schemaname || '.' || tablename)::numeric, 0), 2) AS bloat_pct
  FROM pg_tables
  WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
)
SELECT * FROM bloat WHERE bloat_pct > 50 ORDER BY bloat_pct DESC;
```

### 在线回收（pg_repack）

```bash
# 安装
apt install postgresql-15-repack

# 在线重整表（不锁表）
pg_repack -t public.users -d mydb

# 在线重整索引
pg_repack -i public.users_pkey -d mydb
```

> **何时用 pg_repack**：表膨胀 > 50% 且业务不能停。pg_repack 通过触发器+新建表的方式在线重整。

## 实战案例

### 案例 1：电商订单表 bloat 治理

**问题**：订单表每天 100 万 UPDATE，几周后 bloat 率达 70%。

**调优**：

```sql
-- 1. 降低 autovacuum 触发阈值
ALTER TABLE orders SET (
  autovacuum_vacuum_scale_factor = 0.02,   -- 2% 死元组就触发
  autovacuum_analyze_scale_factor = 0.01,
  autovacuum_vacuum_cost_limit = 2000
);

-- 2. 增加 autovacuum 工作进程
-- postgresql.conf
autovacuum_max_workers = 6

-- 3. 监控
SELECT relname, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables
WHERE relname = 'orders';
```

**效果**：bloat 率从 70% 降到 15%，查询 p99 延迟从 800ms 降到 200ms。

### 案例 2：XID 接近 wraparound

**告警**：监控显示 `pct_toward_wraparound = 0.92`。

**应急**：

```sql
-- 1. 找到最老的表，强制 freeze
vacuumdb --freeze --all -d mydb

-- 2. 如果还不行，手工强制 vacuum 特定表
VACUUM (FREEZE, VERBOSE) huge_table;

-- 3. 临时关闭 autovacuum 防止冲突（生产环境慎用）
ALTER SYSTEM SET autovacuum = off;
SELECT pg_reload_conf();
VACUUM (FREEZE) huge_table;
ALTER SYSTEM SET autovacuum = on;
SELECT pg_reload_conf();
```

## 一句话总结

> **autovacuum 是 PG 运维第一要务**：不调优会表膨胀 + 变慢 + 极端 XID 回卷丢数据。**默认参数不够**，高频更新表必须单独调（scale_factor=0.02）。严重 bloat 用 pg_repack 在线回收。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 对比
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
- [system-design](https://java-px.bot.cd/system-design/):数据库选型
