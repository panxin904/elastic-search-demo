---
title: 主从同步原理
date: 2026-08-15  # date-auto-injected
---

# 🔄 MySQL 主从同步原理

> 主从复制是 MySQL 实现读写分离、扩展读能力、高可用的基础。深入理解同步原理，是排查复制延迟和搭建高可用集群的前提。

## 🎯 主从架构

### 基本架构

```
                     ┌──────────┐
                     │  Client  │
                     └─────┬────┘
                           │
              ┌────────────┴────────────┐
              │                          │
              ▼                          ▼
        ┌──────────┐               ┌──────────┐
        │  Master  │ ◄─── 复制 ───► │  Slave 1 │
        │  (主库)   │               │  (从库)  │
        │  R/W     │               │  R       │
        └──────────┘               └──────────┘
              │                          ▲
              │                          │
              └──────────────────────────┘
                     复制
```

### 一主多从

```
                       ┌──────────┐
                       │  Master  │
                       └─────┬────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │  Slave1  │   │  Slave2  │   │  Slave3  │
        │  (读)    │   │  (读)    │   │  (备份)  │
        └──────────┘   └──────────┘   └──────────┘
```

### 级联复制

```
        Master
          │
          ▼
        Slave1 (中继节点)
          │
    ┌─────┴─────┐
    ▼           ▼
  Slave2     Slave3
```

## 🔄 复制流程详解

### 三步走：dump → relay → replay

```
Master                                              Slave
┌─────────────────────┐                       ┌─────────────────────┐
│                     │                       │                     │
│  1. SQL 执行        │                       │  3. IO Thread      │
│     ↓              │                       │     dump 线程       │
│  2. 写 binlog        │ ──── binlog ────→   │     拉取 binlog      │
│                     │                       │     写到 relay log   │
│                     │                       │          ↓           │
│                     │                       │  4. SQL Thread      │
│                     │                       │     重放 SQL        │
│                     │                       │     写入数据         │
└─────────────────────┘                       └─────────────────────┘
```

### Master 端（dump 线程）

```sql
-- 查看 Master 状态
SHOW MASTER STATUS;
-- File: mysql-bin.000001
-- Position: 1234
-- Binlog_Do_DB: mydb
-- Binlog_Ignore_DB:

-- 查看连接上来的 Slave
SHOW SLAVE HOSTS;
-- 每个 Slave 一行
```

### Slave 端（两个线程）

```sql
-- 查看 Slave 状态
SHOW SLAVE STATUS\G

-- 关键字段：
-- Master_Log_File       = 正在读的 binlog 文件
-- Read_Master_Log_Pos    = 正在读的 position
-- Relay_Log_File         = relay log 文件
-- Relay_Log_Pos          = relay log position
-- Seconds_Behind_Master  = 复制延迟（秒）
-- Slave_IO_Running       = IO 线程状态
-- Slave_SQL_Running      = SQL 线程状态
```

## ⚙️ 搭建主从复制

### 1. 主库配置（my.cnf）

```ini
[mysqld]
server-id = 1                           # 主库 ID（唯一）
log_bin = /var/log/mysql/mysql-bin      # 开启 binlog
binlog_format = ROW                      # binlog 格式
binlog_do_db = mydb                      # 只记录 mydb 的变更（可选）
expire_logs_days = 7                     # binlog 保留 7 天

# 半同步复制（可选，提升数据安全）
plugin-load = "rpl_semi_sync_master=semisync_master.so"
rpl_semi_sync_master_enabled = ON
```

### 2. 从库配置（my.cnf）

```ini
[mysqld]
server-id = 2                           # 从库 ID（唯一）
relay_log = /var/log/mysql/relay-bin    # 开启 relay log
read_only = ON                          # 只读（防止误写）
log_slave_updates = ON                  # 从库 binlog 也记录（用于级联）

# 半同步复制
plugin-load = "rpl_semi_sync_slave=semisync_slave.so"
rpl_semi_sync_slave_enabled = ON
```

### 3. 创建复制用户

```sql
-- 在主库执行
CREATE USER 'repl_user'@'192.168.1.%' IDENTIFIED BY 'StrongP@ss!';
GRANT REPLICATION SLAVE ON *.* TO 'repl_user'@'192.168.1.%';
FLUSH PRIVILEGES;
```

### 4. 备份主库并恢复到从库

```bash
# 1. 主库加读锁
mysql> FLUSH TABLES WITH READ LOCK;

# 2. 记录 binlog 位置
mysql> SHOW MASTER STATUS;
# File: mysql-bin.000003
# Position: 456789

# 3. 备份（另开终端）
mysqldump --single-transaction --master-data=2 mydb > mydb.sql

# 4. 备份传到从库
scp mydb.sql slave:/tmp/

# 5. 解锁
mysql> UNLOCK TABLES;
```

```bash
# 6. 从库恢复
mysql -u root -p < /tmp/mydb.sql

# 7. 配置复制
mysql> CHANGE MASTER TO
    MASTER_HOST='192.168.1.10',
    MASTER_USER='repl_user',
    MASTER_PASSWORD='StrongP@ss!',
    MASTER_LOG_FILE='mysql-bin.000003',
    MASTER_LOG_POS=456789;

# 8. 启动复制
mysql> START SLAVE;

# 9. 查看状态
mysql> SHOW SLAVE STATUS\G
-- Slave_IO_Running: Yes
-- Slave_SQL_Running: Yes
-- Seconds_Behind_Master: 0
```

### 5. 使用 GTID（推荐，MySQL 5.6+）

```sql
-- 主库配置
[mysqld]
gtid_mode = ON
enforce_gtid_consistency = ON

-- 从库配置（更简单，无需指定 binlog position）
mysql> CHANGE MASTER TO
    MASTER_HOST='192.168.1.10',
    MASTER_USER='repl_user',
    MASTER_PASSWORD='StrongP@ss!',
    MASTER_AUTO_POSITION = 1;  -- 自动定位

mysql> START SLAVE;
```

**GTID 优势：**
- ✅ 自动定位 binlog position（崩溃恢复更容易）
- ✅ 一致性保证更强
- ✅ 故障切换更简单

## 🔍 复制模式详解

### 基于 binlog position（旧方式）

```
Master: binlog.000003, position=456789
Slave:  从这个位置开始拉取
```

**缺点：**
- 需要手动指定 position
- 故障切换时容易出错

### 基于 GTID（推荐）

```
每个事务有一个全局唯一 ID：GTID = source_id:transaction_id
例：3E11FA47-71CA-11E1-9E33-C80AA9429562:1-5
```

**优势：**
- 全局唯一，自动定位
- 故障切换更容易
- 支持一致性读

## 🛠️ 常用运维命令

### 查看复制状态

```sql
-- 查看所有从库状态
SHOW SLAVE STATUS\G

-- 关键指标：
-- Seconds_Behind_Master: 延迟秒数（0 = 实时同步）
-- Slave_IO_Running: IO 线程（Yes/No）
-- Slave_SQL_Running: SQL 线程（Yes/No）
-- Last_IO_Error: 最近 IO 错误
-- Last_SQL_Error: 最近 SQL 错误
```

### 启动 / 停止复制

```sql
-- 启动
START SLAVE;

-- 启动 IO 线程
START SLAVE IO_THREAD;

-- 启动 SQL 线程
START SLAVE SQL_THREAD;

-- 停止
STOP SLAVE;

-- 停止特定线程
STOP SLAVE IO_THREAD;
STOP SLAVE SQL_THREAD;
```

### 跳过错误（谨慎）

```sql
-- 跳过 1 个错误
SET GLOBAL sql_slave_skip_counter = 1;
START SLAVE;

-- ⚠️ 只用于跳过确定可跳过的错误（如重复键）
-- 否则会导致主从不一致
```

### 重新指向主库

```sql
-- 切换到新主库
STOP SLAVE;
CHANGE MASTER TO
  MASTER_HOST='new_master_ip',
  MASTER_USER='repl_user',
  MASTER_PASSWORD='StrongP@ss!',
  MASTER_AUTO_POSITION = 1;  -- GTID 模式
START SLAVE;
```

### 重置复制

```sql
-- 完全重置（清除所有复制状态）
STOP SLAVE;
RESET SLAVE;
RESET MASTER;  -- 主库执行
```

## 🎯 复制过滤规则

```sql
-- 主库：只记录指定数据库的 binlog
binlog_do_db = mydb1          # 只记录
binlog_ignore_db = mysql      # 忽略

-- 从库：只重放指定的 relay log
replicate_do_db = mydb1
replicate_ignore_db = test

-- ⚠️ 过滤规则容易导致主从不一致
-- 推荐：不设置过滤，需要过滤在应用层做
```

## 🔄 多源复制（MySQL 5.7+）

```
Master1 ───┐
           ├──→ Slave (聚合)
Master2 ───┘
```

```sql
-- 配置多个复制源
CHANGE MASTER TO
  MASTER_HOST='master1',
  MASTER_PORT=3306,
  MASTER_USER='repl_user',
  MASTER_PASSWORD='StrongP@ss!',
  MASTER_AUTO_POSITION = 1 FOR CHANNEL 'master1';

CHANGE MASTER TO
  MASTER_HOST='master2',
  MASTER_PORT=3306,
  MASTER_USER='repl_user',
  MASTER_PASSWORD='StrongP@ss!',
  MASTER_AUTO_POSITION = 1 FOR CHANNEL 'master2';

START SLAVE FOR CHANNEL 'master1';
START SLAVE FOR CHANNEL 'master2';
```

## ⚠️ 主从复制的常见问题

### 1. 复制延迟

```sql
-- 查看延迟
SHOW SLAVE STATUS\G
-- Seconds_Behind_Master: 30

-- 常见原因：
-- 1. 主库大事务
-- 2. 从库性能差
-- 3. 网络慢
-- 4. 单线程复制（MySQL 5.6 之前）

-- 解决：
-- 1. 拆分大事务
-- 2. 升级从库硬件
-- 3. 改善网络
-- 4. 升级到 MySQL 5.7+（多线程复制）
```

### 2. 主从不一致

```sql
-- ⚠️ 复制不能保证 100% 一致
-- 异步复制下，主库宕机时可能丢失未同步的数据

-- 验证一致性（用 pt-table-checksum）
pt-table-checksum --host=master_host --user=root
```

### 3. SQL 线程错误

```sql
-- 查看错误
SHOW SLAVE STATUS\G
-- Last_SQL_Error: Could not execute Write_rows event...

-- 常见原因：
-- 1. 主库有数据，从库没有（INSERT 冲突）
-- 2. 主库无数据，从库有（DELETE 时找不到）
-- 3. 表结构不一致（ALTER 失败）

-- 解决：
-- 1. 检查并修复不一致
-- 2. 重新初始化从库
```

## 🎯 总结

**主从复制核心：**
- ✅ 基于 binlog + relay log
- ✅ Master dump → Slave IO Thread → Slave SQL Thread
- ✅ GTID 模式比 position 模式更可靠
- ✅ 半同步复制减少数据丢失

**配置要点：**
- 主库：`log_bin=ON`、`binlog_format=ROW`
- 从库：`read_only=ON`、`server-id` 唯一
- 网络：使用专用网络、避免跨地域

**下一步：** [⏱️ 主从延迟排查](../06-replication/lag) — 解决复制延迟问题


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

## 图示：MySQL 主从复制原理

![MySQL 主从复制原理](/mysql-replication.svg)
