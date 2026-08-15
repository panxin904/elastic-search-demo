---
title: 慢查询定位
---

# 🐌 MySQL 慢查询定位

> 慢查询是性能问题的头号元凶。系统化的慢查询分析流程，能帮你快速定位和优化瓶颈。

## 🎯 慢查询分析的整体流程

```
1. 开启慢查询日志 → 2. 收集慢查询 → 3. 分析工具 → 4. 优化
   (slow_query_log)        (long_query_time)      (pt-query-digest)    (索引/改写)
```

## ⚙️ 开启慢查询日志

### 查看当前配置

```sql
SHOW VARIABLES LIKE 'slow_query%';
SHOW VARIABLES LIKE 'long_query_time';

-- slow_query_log        = OFF (默认关闭)
-- slow_query_log_file   = /var/log/mysql/mysql-slow.log
-- long_query_time       = 10.000000 (默认 10 秒)
```

### 开启慢查询

```sql
-- 动态开启（立即生效，重启失效）
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 2;  -- 2 秒
SET GLOBAL log_queries_not_using_indexes = ON;  -- 记录未用索引的查询
SET GLOBAL slow_query_log_file = '/tmp/mysql-slow.log';
```

### 永久开启（my.cnf）

```ini
[mysqld]
# 开启慢查询日志
slow_query_log = ON
slow_query_log_file = /var/log/mysql/mysql-slow.log
long_query_time = 2

# 记录未使用索引的查询（即使没超过 long_query_time）
log_queries_not_using_indexes = ON

# 管理复制相关（可选）
log_slow_admin_statements = ON
log_slow_slave_statements = ON

# 慢查询日志输出方式（FILE / TABLE）
log_output = FILE
```

### 推荐配置（生产环境）

```ini
[mysqld]
slow_query_log = ON
long_query_time = 1                    # 1 秒（更激进）
log_queries_not_using_indexes = ON
log_throttle_queries_not_using_indexes = 100  # 每分钟最多记录 100 条
slow_query_log_file = /var/log/mysql/slow.log
```

## 📊 慢查询日志格式

### FILE 格式

```log
# Time: 2025-07-18T10:23:45.123456Z
# User@Host: appuser[appuser] @  [10.0.0.5]
# Query_time: 5.234567  Lock_time: 0.000123 Rows_sent: 1000  Rows_examined: 1000000
SET timestamp=1752819825;
SELECT * FROM orders WHERE user_id = 100 AND status = 'paid';
```

### 字段说明

| 字段 | 含义 |
|---|---|
| Query_time | 查询耗时（秒） |
| Lock_time | 等待锁的时间 |
| Rows_sent | 返回给客户端的行数 |
| Rows_examined | 扫描的行数 |
| SET timestamp | 时间戳 |

**关键指标：** `Rows_examined` / `Rows_sent` 比例越大，越需要优化。

## 🔍 分析工具

### 工具 1：mysqldumpslow（MySQL 自带）

```bash
# 使用率最高的 10 个慢查询
mysqldumpslow -s c -t 10 /var/log/mysql/slow.log

# 按耗时排序
mysqldumpslow -s t -t 10 /var/log/mysql/slow.log

# 按平均耗时排序
mysqldumpslow -s at -t 10 /var/log/mysql/slow.log

# 按行扫描数排序
mysqldumpslow -s e -t 10 /var/log/mysql/slow.log

# 显示完整 SQL（不截断）
mysqldumpslow -v /var/log/mysql/slow.log

# 过滤特定模式的查询
mysqldumpslow -g "SELECT * FROM orders" /var/log/mysql/slow.log
```

### 工具 2：pt-query-digest（Percona Toolkit）⭐⭐⭐

**最强大的慢查询分析工具**：

```bash
# 安装 Percona Toolkit
# CentOS/RHEL:
yum install percona-toolkit
# Ubuntu/Debian:
apt-get install percona-toolkit

# 分析慢查询日志
pt-query-digest /var/log/mysql/slow.log

# 输出到文件
pt-query-digest /var/log/mysql/slow.log > /tmp/slow_report.txt

# 只看前 10 个最慢
pt-query-digest --limit 10 /var/log/mysql/slow.log

# 分析最近 1 小时的日志
pt-query-digest --since '1h ago' /var/log/mysql/slow.log

# 分析特定时间范围
pt-query-digest --since '2025-07-18 09:00:00' --until '2025-07-18 10:00:00' /var/log/mysql/slow.log

# 过滤特定数据库
pt-query-digest --filter '$event->{db} eq "mydb"' /var/log/mysql/slow.log
```

### pt-query-digest 输出解读

```
# Profile
# Rank Query ID           Response time   Calls R/Call   V/M
# ==== ================== ================ ===== ======= =====
#    1 0xABCD...           1234.5678 65.0%   123 10.0342  2.50 SELECT orders
#    2 0xEFGH...            567.8901 30.0%    50 11.3578  3.20 SELECT users JOIN orders
#    3 ...

# Query 1: 0xABCD... (QPS: 1.23)
# Attribute   pct  total  min    max     avg     95%  stddev  median
# =========   ===  =====  ====   ====    ====     ==   ======   ======
# Count         65  123
# Exec time    65   1234s  5s     30s     10s     20s   5s      10s
# Lock time     0    0.1s   0      0       0.8ms   ...
# Rows sent    ... 
# Row examine  ...
# Query_time distribution
#   1us
#   10us
#   100us
#   1ms
#   10ms
#   100ms  ████████████ 12
#   1s     ████████████████████ 80
#   10s+   ████████████ 31
# Tables
#    SHOW TABLE STATUS LIKE 'orders'\G
#    SHOW CREATE TABLE orders\G
# EXPLAIN
EXPLAIN SELECT * FROM orders WHERE ...\G
```

## 🔍 实时慢查询分析

### 通过 performance_schema

```sql
-- 8.0+: 查看当前慢查询
SELECT
  DIGEST_TEXT,
  COUNT_STAR AS exec_count,
  AVG_TIMER_WAIT / 1000000000 AS avg_ms,
  SUM_TIMER_WAIT / 1000000000 AS total_ms
FROM performance_schema.events_statements_summary_by_digest
WHERE AVG_TIMER_WAIT > 1000000000  -- 平均超过 1 秒
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 20;

-- 查看特定查询的详细信息
SELECT * FROM performance_schema.events_statements_summary_by_digest
WHERE SCHEMA_NAME = 'mydb'
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;
```

### 通过 information_schema.processlist

```sql
-- 查看当前正在执行的查询
SELECT
  id,
  user,
  host,
  db,
  command,
  TIME,
  state,
  LEFT(info, 100) AS query
FROM information_schema.processlist
WHERE COMMAND != 'Sleep'
  AND TIME > 5  -- 超过 5 秒
ORDER BY TIME DESC;
```

## 🎯 实战案例：定位慢查询

### 案例 1：业务突然变慢

```bash
# 1. 查看当前慢查询
mysql> SHOW PROCESSLIST;
# 看到有大量 SELECT 等待

# 2. 查看慢查询日志（最近 10 分钟）
tail -n 1000 /var/log/mysql/slow.log

# 3. 用 pt-query-digest 分析
pt-query-digest --since '10m ago' /var/log/mysql/slow.log

# 4. 发现问题 SQL：
# SELECT * FROM orders WHERE created_at BETWEEN '...' AND '...';
# 调用 50 次，平均 15 秒，扫描 100 万行

# 5. 用 EXPLAIN 分析
EXPLAIN SELECT * FROM orders WHERE created_at BETWEEN '...' AND '...';
# type: ALL（没用到索引）

# 6. 加索引
CREATE INDEX idx_created ON orders(created_at);

# 7. 验证
EXPLAIN SELECT * FROM orders WHERE created_at BETWEEN '...' AND '...';
# type: range, key: idx_created, rows: 1000
# 性能提升 1000 倍
```

### 案例 2：接口超时

```sql
-- 1. 开启慢查询（临时）
SET GLOBAL long_query_time = 0.5;  -- 记录 0.5 秒以上的

-- 2. 复现接口超时，捕获慢查询

-- 3. 用 pt-query-digest 分析
pt-query-digest --since '5m ago' /var/log/mysql/slow.log

# 4. 发现是 JOIN 慢
# SELECT u.*, o.* FROM users u JOIN orders o ON u.id = o.user_id WHERE u.city = '北京'
# - 主查询扫描 50 万 users（rows_examined）
# - 关联 orders 没索引（Using join buffer）

# 5. 加索引
CREATE INDEX idx_orders_user ON orders(user_id);

# 6. 优化 SQL（避免 SELECT *）
SELECT u.id, u.name, o.order_no, o.amount FROM ...
```

## 🔧 慢查询优化的常见手段

### 1. 加索引（最常用）

```sql
-- 慢查询：WHERE status = 1 AND created_at > '...'
-- 解决：建复合索引
CREATE INDEX idx_status_created ON orders(status, created_at);
```

### 2. 重写 SQL

```sql
-- 慢查询：SELECT * FROM users WHERE DATE(created_at) = '2025-07-18';
-- ❌ 函数破坏索引
-- ✅ 改写
SELECT * FROM users
WHERE created_at >= '2025-07-18' AND created_at < '2025-07-19';
```

### 3. 优化 LIMIT

```sql
-- 慢查询：SELECT * FROM orders LIMIT 1000000, 20;
-- ❌ 深分页
-- ✅ 游标分页
SELECT * FROM orders WHERE id > 1000000 LIMIT 20;
```

### 4. 用 EXPLAIN 验证

```sql
EXPLAIN SELECT ... -- 确认 type、key、rows、Extra 都合理
```

## 🛠️ 慢查询监控体系

### 1. 实时告警（Prometheus）

```yaml
# Prometheus 告警规则
groups:
- name: mysql_slow_query
  rules:
  - alert: MySQLSlowQueriesTooMany
    expr: |
      increase(mysql_global_status_slow_queries[5m]) > 100
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "慢查询过多"
```

### 2. 定期分析（cron）

```bash
# 每天分析前一天慢查询日志
0 1 * * * pt-query-digest /var/log/mysql/slow.log.$(date -d yesterday +\%Y\%m\%d) \
    > /var/log/mysql/slow_report_$(date +\%Y\%m\%d).txt
```

### 3. 自动优化建议

```bash
# 用 pt-query-digest 的 --type 过滤
pt-query-digest --type slowlog --type json --output slow /var/log/mysql/slow.log
```

## 🎯 总结

**慢查询优化流程：**
1. ✅ 开启慢查询日志（生产环境必开）
2. ✅ 用 pt-query-digest 分析（找出 Top N）
3. ✅ 用 EXPLAIN 解读执行计划
4. ✅ 加索引 / 重写 SQL
5. ✅ 验证优化效果
6. ✅ 持续监控

**性能对比：**
| 优化手段 | 性能提升 | 实施难度 |
|---|---|---|
| 加索引 | 10-1000 倍 | ⭐ |
| SQL 改写 | 2-10 倍 | ⭐⭐ |
| 避免 SELECT * | 1.5-3 倍 | ⭐ |
| 游标分页 | 10-100 倍 | ⭐⭐ |

**下一步：** [🎯 索引优化实战](../05-optimization/index-tuning) — 索引选型的艺术