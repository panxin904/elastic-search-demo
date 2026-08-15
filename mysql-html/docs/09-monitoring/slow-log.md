---
title: 慢查询日志
---

# 🐢 MySQL 慢查询日志

> 慢查询日志是性能优化的"第一道防线"。开启它，定位慢查询，才能进行后续优化。

## 🎯 慢查询日志是什么？

MySQL 记录所有**执行时间超过阈值**的 SQL 到日志文件，是定位慢查询的**最直接手段**。

```
┌──────────┐    查询慢     ┌──────────────┐
│   App    │ ────────────→ │  slow.log     │
└──────────┘               └──────────────┘
                                  ↓
                          性能优化的起点
```

## ⚙️ 开启慢查询日志

### 查看当前配置

```sql
-- 查看慢查询相关变量
SHOW VARIABLES LIKE 'slow_query%';
SHOW VARIABLES LIKE 'long_query_time';

-- 默认配置：
-- slow_query_log        = OFF
-- slow_query_log_file   = /var/log/mysql/slow.log
-- long_query_time       = 10.0 秒
```

### 动态开启

```sql
-- 1. 开启慢查询日志
SET GLOBAL slow_query_log = ON;

-- 2. 设置阈值（建议 1-2 秒）
SET GLOBAL long_query_time = 1;

-- 3. 记录未使用索引的查询（即使很快）
SET GLOBAL log_queries_not_using_indexes = ON;

-- 4. 设置日志文件
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';
```

### 永久配置（my.cnf）

```ini
[mysqld]
# 开启慢查询日志
slow_query_log = ON
slow_query_log_file = /var/log/mysql/slow.log

# 慢查询阈值（秒）
long_query_time = 1

# 记录未使用索引的查询
log_queries_not_using_indexes = ON

# 限制每分钟记录数量（防止日志爆炸）
log_throttle_queries_not_using_indexes = 100

# 慢查询输出方式：FILE / TABLE
log_output = FILE

# 慢查询日志的额外信息
log_slow_admin_statements = ON
log_slow_slave_statements = ON
log_slow_extra = ON  -- 8.0.14+ 记录更多上下文
```

## 📊 慢查询日志格式

### 示例日志

```log
# Time: 2025-07-18T10:23:45.123456Z
# User@Host: appuser[appuser] @  [10.0.0.5]  Id: 12345
# Query_time: 5.234567  Lock_time: 0.000123 Rows_sent: 1000  Rows_examined: 1000000
# Thread_id: 100  Errno: 0  Killed: 0
# Bytes_received: 100  Bytes_sent: 50000
SET timestamp=1752819825;
SELECT * FROM orders WHERE user_id = 100 AND status = 'paid';
```

### 字段说明

| 字段 | 含义 |
|---|---|
| Time | 查询时间 |
| User@Host | 用户和客户端 IP |
| Query_time | 查询耗时（秒） |
| Lock_time | 等待锁的时间 |
| Rows_sent | 返回行数 |
| Rows_examined | 扫描行数 |
| Thread_id | 线程 ID |
| SET timestamp | 时间戳 |

**关键指标：** `Rows_examined / Rows_sent` 比例越大，越需要优化。

## 🔧 慢查询分析工具

### 工具 1：mysqldumpslow（MySQL 自带）

```bash
# 使用率最高的 10 个慢查询
mysqldumpslow -s c -t 10 /var/log/mysql/slow.log

# 按耗时排序
mysqldumpslow -s t -t 10 /var/log/mysql/slow.log

# 按平均耗时排序
mysqldumpslow -s at -t 10 /var/log/mysql/slow.log

# 显示完整 SQL
mysqldumpslow -v /var/log/mysql/slow.log

# 过滤特定 SQL 模式
mysqldumpslow -g "SELECT.*FROM orders" /var/log/mysql/slow.log
```

### 工具 2：pt-query-digest（Percona Toolkit）⭐⭐⭐

```bash
# 安装
yum install percona-toolkit
# 或
apt-get install percona-toolkit

# 完整分析
pt-query-digest /var/log/mysql/slow.log > /tmp/slow_report.txt

# 只看前 10 个
pt-query-digest --limit 10 /var/log/mysql/slow.log

# 分析特定时间范围
pt-query-digest --since '2025-07-18 09:00:00' \
                --until '2025-07-18 10:00:00' \
                /var/log/mysql/slow.log

# 输出为 JSON（用于程序化分析）
pt-query-digest --output json /var/log/mysql/slow.log
```

### pt-query-digest 输出示例

```
# Profile
# Rank Query ID           Response time   Calls R/Call   V/M
# ==== ================== ================ ===== ======= =====
#    1 0xABCD...           1234.5678 65.0%   123 10.0342  2.50 SELECT orders
#    2 0xEFGH...            567.8901 30.0%    50 11.3578  3.20 SELECT users JOIN orders
#    3 0xIJKL...            123.4567  5.0%   200  0.6173  0.50 UPDATE products

# Query 1: 0xABCD... (QPS: 1.23)
# Attribute   pct  total  min    max     avg     95%  stddev  median
# Count         65  123
# Exec time    65   1234s  5s     30s     10s     20s   5s      10s
# Rows sent    ... 
# Row examine  ...
# Query_time distribution
#   100ms  ████ 12
#   1s     ████████████ 80
#   10s+   █████ 31
```

## 🎯 实战案例

### 案例 1：业务反馈接口慢

```bash
# 1. 检查慢查询日志（最近 1 小时）
find /var/log/mysql/slow.log -mmin -60

# 2. 用 pt-query-digest 分析
pt-query-digest --since '1h ago' /var/log/mysql/slow.log

# 3. 发现 Top 1:
#    SELECT * FROM orders WHERE created_at BETWEEN '...' AND '...'
#    - 平均耗时：15 秒
#    - 扫描行数：100 万
#    - 调用次数：50

# 4. EXPLAIN 分析
EXPLAIN SELECT * FROM orders WHERE created_at BETWEEN '...' AND '...';
# type: ALL（没用到索引）

# 5. 加索引
CREATE INDEX idx_created ON orders(created_at);

# 6. 验证
EXPLAIN SELECT * FROM orders WHERE created_at BETWEEN '...' AND '...';
# type: range（用上索引）

# 7. 性能提升：100 倍
```

### 案例 2：定期分析（cron）

```bash
# 每天凌晨分析前一天的慢查询
0 1 * * * pt-query-digest --since '24h ago' /var/log/mysql/slow.log \
  | mail -s "MySQL 慢查询日报" admin@example.com

# 归档慢查询日志（保留 30 天）
0 0 * * * find /var/log/mysql/ -name "slow.log.*" -mtime +30 -delete
```

## 🛠️ 慢查询优化流程

```
┌─────────────────┐
│ 1. 开启慢查询日志  │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 2. pt-query-digest  │
│    找出 Top N      │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 3. EXPLAIN 分析    │
│    看 type/key/rows│
└────────┬────────┘
         ↓
┌─────────────────┐
│ 4. 优化手段         │
│    - 加索引        │
│    - 重写 SQL      │
│    - 改表结构      │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 5. 验证效果        │
│    再跑一遍 EXPLAIN│
└────────┬────────┘
         ↓
┌─────────────────┐
│ 6. 持续监控        │
│    防止新的慢查询   │
└─────────────────┘
```

## 📊 慢查询的常见原因

### 1. 没用到索引

```sql
-- 检查：Rows_examined 很大
-- 解决：加索引
CREATE INDEX idx_xxx ON table_name(column_name);
```

### 2. 索引失效

```sql
-- 常见原因：
-- - WHERE 中用函数
-- - 隐式类型转换
-- - LIKE 以通配符开头
-- - OR 条件没索引
```

### 3. JOIN 慢

```sql
-- 关联字段没索引
SELECT * FROM a JOIN b ON a.id = b.a_id;  -- b.a_id 没索引

-- 解决：加索引
CREATE INDEX idx_a_id ON b(a_id);
```

### 4. 排序慢

```sql
-- ORDER BY 字段没索引
SELECT * FROM orders ORDER BY created_at DESC;
-- Extra: Using filesort

-- 解决：加索引
CREATE INDEX idx_created ON orders(created_at);
```

## 🎯 总结

**慢查询日志核心：**
- ✅ 开启 `slow_query_log = ON`
- ✅ 阈值设 1-2 秒
- ✅ 用 pt-query-digest 分析
- ✅ 定期优化 Top N

**生产环境配置：**
- 阈值：1-2 秒
- 开启未用索引记录
- 限制每分钟记录数
- 归档保留 30 天

**下一步：** [🔬 performance_schema](../09-monitoring/performance-schema) — MySQL 内部观测台