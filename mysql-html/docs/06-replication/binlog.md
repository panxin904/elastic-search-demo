---
title: binlog 与 relay log
date: 2026-08-15  # date-auto-injected
---

# 📜 MySQL binlog 与 relay log

> 主从复制的核心是 binlog。理解 binlog 的格式、写入、读取过程，是掌握主从复制和高可用的基础。

## 🎯 什么是 binlog？

**binlog（Binary Log）** 是 MySQL Server 层实现的二进制日志，记录所有**修改数据的 SQL**（不记录 SELECT）。

```
┌──────────────────────────────────┐
│        MySQL Server                │
│                                   │
│   ┌──────────────────────┐        │
│   │  binlog 文件          │ ← 记录所有数据变更
│   │  binlog.000001        │
│   │  binlog.000002        │
│   └──────────────────────┘        │
│          ▲                         │
│          │ 写入                     │
│   ┌──────┴───────┐                │
│   │ InnoDB        │                │
│   │ (数据 + 索引) │                │
│   └──────────────┘                │
└──────────────────────────────────┘
```

## 📊 binlog 的三大作用

1. **主从复制**：从库读取主库的 binlog，重放 SQL
2. **数据恢复**：基于时间点恢复（Point-in-Time Recovery）
3. **审计**：追踪所有数据变更

## 🎬 binlog 的三种格式

### STATEMENT（基于 SQL）

```sql
SET GLOBAL binlog_format = 'STATEMENT';

-- binlog 内容示例
UPDATE users SET name = '张三' WHERE id = 1;
-- 记录的就是这条 SQL
```

**优点：**
- ✅ binlog 文件小（只记录 SQL）
- ✅ 可读性好

**缺点：**
- ❌ 非确定性函数（NOW()、UUID()）可能导致主从不一致
- ❌ 某些 DDL 不安全

### ROW（基于行）⭐ 推荐

```sql
SET GLOBAL binlog_format = 'ROW';

-- binlog 内容示例（不是 SQL，是行变更）
-- Table: users
-- @1=1 (id)
-- @2='张三' (name)
-- @3='zhangsan@x.com' (email)
-- WHERE: id = 1 SET name='张三' email='...'
```

**优点：**
- ✅ 严格一致（不会因函数导致不一致）
- ✅ 安全（每行变更都有记录）

**缺点：**
- ❌ binlog 文件大（大量 UPDATE 时）
- ❌ 不可直接读（需要 mysqlbinlog 解析）

### MIXED（混合）

```sql
SET GLOBAL binlog_format = 'MIXED';

-- 自动选择 STATEMENT 或 ROW
-- 大多数情况用 STATEMENT，特殊情况用 ROW
```

## ⚙️ binlog 配置

```ini
[mysqld]
# 开启 binlog（主库必须开启）
log_bin = /var/log/mysql/mysql-bin

# binlog 格式
binlog_format = ROW

# 单个 binlog 文件最大大小（默认 1GB）
max_binlog_size = 512M

# binlog 保留天数（默认 0 = 永久保留）
expire_logs_days = 7

# 同步 binlog 次数（用于事务持久性）
sync_binlog = 1  # 每次事务提交都同步到磁盘（最安全，性能略差）

# binlog 缓存大小（每个会话）
binlog_cache_size = 1M
```

```sql
-- 查看 binlog 配置
SHOW VARIABLES LIKE 'binlog%';

-- 查看 binlog 文件列表
SHOW BINARY LOGS;

-- 查看当前写入的 binlog
SHOW MASTER STATUS;
-- File: mysql-bin.000001
-- Position: 1234
```

## 📖 查看 binlog 内容

### 命令行工具 mysqlbinlog

```bash
# 查看 binlog 内容（文本格式）
mysqlbinlog /var/log/mysql/mysql-bin.000001

# 只看某个数据库
mysqlbinlog --database=mydb /var/log/mysql/mysql-bin.000001

# 按时间过滤
mysqlbinlog --start-datetime="2025-07-18 09:00:00" \
           --stop-datetime="2025-07-18 10:00:00" \
           /var/log/mysql/mysql-bin.000001

# 按 position 过滤
mysqlbinlog --start-position=1234 --stop-position=5678 /var/log/mysql/mysql-bin.000001

# ROW 格式需要 -v 显示具体行变更
mysqlbinlog -v /var/log/mysql/mysql-bin.000001
```

### SQL 命令查看

```sql
-- 查看 binlog 事件
SHOW BINLOG EVENTS IN 'mysql-bin.000001' LIMIT 10;

-- 查看指定 position
SHOW BINLOG EVENTS IN 'mysql-bin.000001' FROM 1234 LIMIT 10;
```

## 🔄 relay log（中继日志）

**relay log 是从库特有的**，用于暂存从主库接收的 binlog。

```
主库                                从库
┌──────────┐                       ┌──────────────────┐
│  binlog   │ ──── 网络传输 ────→  │  relay log        │
└──────────┘                       │  (暂存 binlog)     │
                                  └─────────┬────────┘
                                            │ SQL 线程重放
                                            ▼
                                  ┌──────────────────┐
                                  │  InnoDB (数据)    │
                                  └──────────────────┘
```

```sql
-- 查看 relay log 配置
SHOW VARIABLES LIKE 'relay_log%';

-- relay_log = /var/log/mysql/relay-bin
-- relay_log_info_repository = TABLE
```

## 🔄 主从复制流程

### 完整流程

```
Master                                          Slave
┌────────────────────┐                       ┌────────────────────┐
│ 1. 客户端执行 SQL    │                       │                    │
│    ↓                │                       │                    │
│ 2. 写 binlog         │                       │                    │
│    ↓                │                       │                    │
│ 3. fsync binlog      │                       │                    │
│    ↓                │                       │                    │
│ 4. 返回客户端成功    │                       │                    │
└────────────────────┘                       └────────────────────┘
                                                          ↑
                                              5. IO 线程拉取 binlog
                                              ↓
                                          ┌────────────────────┐
                                          │ 6. 写入 relay log    │
                                          └────────────────────┘
                                              ↓
                                          7. SQL 线程重放 SQL
                                              ↓
                                          8. 写入从库数据
```

## 🎯 复制模式

### 异步复制（默认）

```sql
-- 主库写入 binlog 后立即返回成功，不等待从库确认
-- 性能最好，但可能丢数据（主库宕机时从库还没收到 binlog）
```

### 半同步复制

```sql
-- 安装半同步插件
INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';
INSTALL PLUGIN rpl_semi_sync_slave SONAME 'semisync_slave.so';

-- 启用（主库）
SET GLOBAL rpl_semi_sync_master_enabled = ON;
-- 启用（从库）
SET GLOBAL rpl_semi_sync_slave_enabled = ON;

-- 至少等待 N 个从库确认
SET GLOBAL rpl_semi_sync_master_wait_for_slave_count = 1;

-- 主库提交后，等待至少 1 个从库收到 binlog 才返回
-- 性能略差，但数据更安全
```

### 组复制（MGR，MySQL 8.0+）

详见 [🌐 MGR 组复制](../07-ha/mgr)

## 🛠️ binlog 运维

### 清理过期 binlog

```sql
-- 自动清理（根据 expire_logs_days）
SET GLOBAL expire_logs_days = 7;

-- 手动清理
PURGE BINARY LOGS BEFORE '2025-07-01';
PURGE BINARY LOGS TO 'mysql-bin.000010';

-- 谨慎：删除前确认从库已经消费了这些 binlog
```

### 查看 binlog 大小

```sql
SELECT
  log_name,
  size / 1024 / 1024 AS size_mb
FROM performance_schema.log_status
WHERE log_name LIKE '%bin%';
```

### 监控 binlog 写入性能

```sql
SHOW STATUS LIKE 'Binlog%';
-- Binlog_cache_use      = 使用 binlog 缓存的事务数
-- Binlog_cache_disk_use = 缓存溢出写到磁盘的事务数
-- Binlog_stmt_cache_use = STATEMENT 格式缓存使用

-- ⚠️ Binlog_cache_disk_use > 0 说明 binlog_cache_size 太小
```

## ⚠️ binlog 的坑

### 1. 主从不一致

```sql
-- STATEMENT 格式下，非确定性函数导致主从不一致
-- 主库：UPDATE users SET updated_at = NOW() WHERE id = 1;
-- 从库重放时 NOW() 是不同的时间！

-- 解决：用 ROW 格式（推荐）
SET GLOBAL binlog_format = 'ROW';
```

### 2. binlog 暴涨

```sql
-- ❌ 大批量 UPDATE 产生海量 binlog
UPDATE huge_table SET status = 1 WHERE ...;
-- binlog 暴涨，磁盘 IO 飙升

-- ✅ 分批更新
UPDATE huge_table SET status = 1 WHERE id BETWEEN 1 AND 10000;
-- 每批 commit
```

### 3. 误删 binlog

```sql
-- ⚠️ 千万别手动删除 binlog 文件！
-- 如果从库还在用，删了会导致从库无法同步

-- ✅ 用 PURGE 命令（MySQL 会检查从库状态）
PURGE BINARY LOGS BEFORE '2025-07-01';
```

## 🎯 总结

**binlog 核心：**
- ✅ 记录所有数据变更（不包括 SELECT）
- ✅ 三种格式：STATEMENT / ROW / MIXED，推荐 ROW
- ✅ 主从复制的核心
- ✅ 数据恢复的基石

**配置最佳实践：**
- 主库：`binlog_format=ROW`、`sync_binlog=1`
- 保留 7-14 天的 binlog（足够从库恢复）
- 半同步复制减少数据丢失风险

**下一步：** [🔄 主从同步原理](../06-replication/replication) — 深入理解复制过程


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

<!-- svg-injected:do-not-edit -->

## 图示：CDC 变更数据捕获全链路

![CDC 变更数据捕获全链路](/cdc-flow.svg)
