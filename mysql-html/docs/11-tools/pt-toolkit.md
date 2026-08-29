---
title: pt-toolkit 工具集
date: 2026-08-15  # date-auto-injected
---

# 🔧 Percona Toolkit 工具集

> Percona Toolkit（原 Maatkit）是 MySQL DBA 的瑞士军刀，包含 30+ 工具，用于性能分析、数据校验、运维管理。**DBA 必备**。

## 🎯 Percona Toolkit 是什么？

Percona Toolkit 是 Percona 公司维护的 MySQL 高级命令行工具集，几乎所有大型互联网公司的 DBA 都在用。

```bash
# 安装
yum install percona-toolkit    # CentOS/RHEL
apt-get install percona-toolkit # Ubuntu/Debian
```

## 🌟 核心工具

### 1. pt-query-digest ⭐⭐⭐

**最常用**：慢查询分析神器

```bash
# 分析慢查询日志
pt-query-digest /var/log/mysql/slow.log

# 输出到文件
pt-query-digest /var/log/mysql/slow.log > /tmp/slow_report.txt

# 分析最近 1 小时
pt-query-digest --since '1h ago' /var/log/mysql/slow.log

# 分析特定时间范围
pt-query-digest --since '2025-07-18 09:00:00' \
                --until '2025-07-18 10:00:00' \
                /var/log/mysql/slow.log

# 通过 processlist 分析
pt-query-digest --processlist h=localhost,u=root,p=xxx

# 按时间过滤
pt-query-digest --filter '$event->{arg} =~ m/SELECT/' /var/log/mysql/slow.log
```

**输出解读：**
```
# Profile
# Rank Query ID           Response time   Calls R/Call
# ==== ================== ================ ===== =======
#    1 0xABCD...           1234.5678 65.0%   123 10.0342
#    2 0xEFGH...            567.8901 30.0%    50 11.3578

# Query 1: ...
# Attribute   pct  total  min    max     avg
# =========   ===  =====  ====   ====    ====
# Exec time    65   1234s  5s     30s     10s
# Rows examine  ... 100万
```

### 2. pt-online-schema-change ⭐⭐⭐

**在线 DDL**：不锁表修改表结构

```bash
# 添加列
pt-online-schema-change \
  --alter "ADD COLUMN new_col VARCHAR(100)" \
  --execute \
  --host=127.0.0.1 --user=root --password=xxx \
  D=mydb,t=users

# 添加索引
pt-online-schema-change \
  --alter "ADD INDEX idx_email (email)" \
  --execute \
  --host=127.0.0.1 --user=root --password=xxx \
  D=mydb,t=users

# 修改列
pt-online-schema-change \
  --alter "MODIFY COLUMN name VARCHAR(200) NOT NULL" \
  --execute \
  --host=127.0.0.1 --user=root --password=xxx \
  D=mydb,t=users

# 原理：
# 1. 创建新表（_new 后缀）
# 2. 在原表上创建触发器
# 3. 增量同步数据到新表
# 4. 切换表名
# 5. 删除旧表
```

### 3. pt-table-checksum ⭐⭐⭐

**数据一致性校验**：主从数据是否一致

```bash
# 校验主从一致性
pt-table-checksum \
  --host=master_host --user=root --password=xxx \
  --replicate=mydb.checksums \
  mydb

# 只校验特定表
pt-table-checksum --tables=users,orders mydb

# 输出：
# TS ERRORS DIFFS ROWS CHUNKS SKIPPED TABLE
# 09-28T10:00:00 0 0 1000 1 0 mydb.users
# 09-28T10:00:01 0 1 5000 5 0 mydb.orders  ← 有差异！

# 查看具体差异
pt-table-sync --print --replicate=mydb.checksums h=master_host,u=root,p=xxx
```

### 4. pt-table-sync

**数据同步修复**：修复主从不一致

```bash
# 查看需要修复的 SQL
pt-table-sync --print --replicate=mydb.checksums \
  h=master_host,u=root,p=xxx

# 执行修复
pt-table-sync --execute --replicate=mydb.checksums \
  h=slave_host,u=root,p=xxx

# 同步特定表
pt-table-sync --execute --sync-to-master h=slave_host \
  D=mydb,t=users,u=root,p=xxx
```

### 5. pt-kill

**杀慢查询**

```bash
# 杀查询超过 10 秒的连接
pt-kill --busy-time 10 --host=127.0.0.1 --user=root --password=xxx

# 杀特定用户的查询
pt-kill --match-user "app_user" --busy-time 30

# 杀特定查询模式
pt-kill --match-info "SELECT.*FROM huge_table" --busy-time 60

# 打印但不杀（dry run）
pt-kill --busy-time 10 --print
```

### 6. pt-archiver

**数据归档**：清理旧数据

```bash
# 归档 1 年前的数据到另一个库
pt-archiver \
  --source h=127.0.0.1,D=mydb,t=orders \
  --dest h=127.0.0.1,D=mydb_archive,t=orders \
  --where "created_at < '2024-01-01'" \
  --limit 1000 --commit-each

# 删除旧数据（不归档）
pt-archiver --source h=127.0.0.1,D=mydb,t=logs \
  --where "created_at < '2024-01-01'" \
  --purge
```

### 7. pt-show-grants

**查看和规范化用户权限**

```bash
# 查看所有用户权限
pt-show-grants --host=127.0.0.1 --user=root --password=xxx

# 输出为标准 SQL 格式
pt-show-grants --host=127.0.0.1 --user=root --password=xxx > grants.sql
```

### 8. pt-duplicate-key-checker

**查找重复索引**

```bash
pt-duplicate-key-checker --host=127.0.0.1 --user=root --password=xxx mydb
# 输出：
# mydb.users
# # idx_name is a left-prefix of idx_name_age
# # Key definitions:
# #   KEY `idx_name` (`name`),
# #   KEY `idx_name_age` (`name`,`age`),
# # Column List:
# #   `name`
# # To remove this duplicate index, execute:
# ALTER TABLE mydb.users DROP INDEX idx_name;
```

### 9. pt-slave-find

**查找主从架构的所有从库**

```bash
pt-slave-find --host=master_host --user=root --password=xxx
```

### 10. pt-heartbeat

**监控主从延迟**

```bash
# 监控从库延迟
pt-heartbeat --host=slave_host --user=root --password=xxx \
  --master-server-id=1 --update \
  --daemonize

# 记录到数据库（需要创建 heartbeat 表）
```

## 🔧 工具集全景

### 性能分析类

| 工具 | 用途 |
|---|---|
| pt-query-digest | 慢查询分析 ⭐ |
| pt-index-usage | 索引使用分析 |
| pt-pmp | 显示堆栈跟踪 |
| pt-mext | 关联系统状态 |

### 运维变更类

| 工具 | 用途 |
|---|---|
| pt-online-schema-change | 在线 DDL ⭐ |
| pt-table-sync | 数据同步 |
| pt-archiver | 数据归档 |
| pt-online-pt-online-schema-change | pt-osc 包装 |

### 数据一致性类

| 工具 | 用途 |
|---|---|
| pt-table-checksum | 一致性校验 ⭐ |
| pt-table-sync | 修复不一致 ⭐ |
| pt-slave-find | 查找从库 |

### 监控类

| 工具 | 用途 |
|---|---|
| pt-kill | 杀慢查询 |
| pt-heartbeat | 延迟监控 |
| pt-mysql-summary | 状态摘要 |
| pt-deadlock-logger | 死锁记录 |

## 🛠️ 实战案例

### 案例 1：分析并优化慢查询

```bash
# 1. 分析慢查询
pt-query-digest /var/log/mysql/slow.log > /tmp/slow_report.txt

# 2. 找出 Top 1
# SELECT * FROM orders WHERE user_id = 100  → 平均 15 秒

# 3. 用 pt-online-schema-change 加索引
pt-online-schema-change \
  --alter "ADD INDEX idx_user (user_id)" \
  --execute \
  h=127.0.0.1,u=root,p=xxx \
  D=mydb,t=orders

# 4. 验证
EXPLAIN SELECT * FROM orders WHERE user_id = 100;
# type: ref, key: idx_user  ✅
```

### 案例 2：主从数据校验

```bash
# 1. 在主库创建校验库
mysql -h master -e "CREATE DATABASE IF NOT EXISTS percona;"

# 2. 校验
pt-table-checksum \
  --replicate=percona.checksums \
  --host=master --user=root --password=xxx \
  mydb

# 3. 如果有差异
pt-table-sync --execute --replicate=percona.checksums \
  h=master_host,u=root,p=xxx \
  --sync-to-master h=slave_host
```

### 案例 3：在线修改大表

```bash
# 修改 1 亿行的表，不锁表
pt-online-schema-change \
  --alter "ADD COLUMN new_col INT DEFAULT 0" \
  --execute --alter-foreign-keys-method auto \
  --host=127.0.0.1 --user=root --password=xxx \
  D=mydb,t=huge_table

# 过程：
# 1. 创建 _new 临时表
# 2. 增量复制数据（按主键分块）
# 3. 应用变更到 _new 表
# 4. 创建触发器同步增量
# 5. 原子切换表名
# 6. 删除旧表
```

## 🎯 总结

**Percona Toolkit 核心工具：**

| 工具 | 用途 | 频率 |
|---|---|---|
| pt-query-digest | 慢查询分析 | ⭐⭐⭐ |
| pt-online-schema-change | 在线 DDL | ⭐⭐⭐ |
| pt-table-checksum | 数据校验 | ⭐⭐ |
| pt-table-sync | 数据同步 | ⭐⭐ |
| pt-kill | 杀慢查询 | ⭐⭐ |
| pt-archiver | 数据归档 | ⭐ |

**安装：**
```bash
yum install percona-toolkit
# 或
apt-get install percona-toolkit
```

**使用建议：**
- 慢查询：每天分析一次
- 数据校验：每周一次
- DDL：所有大表变更都用 pt-osc
- 杀慢查询：用 cron 定期运行

**下一步：** [📋 SQL 速查表](../11-tools/cheatsheet) — 30+ SQL 模板速查