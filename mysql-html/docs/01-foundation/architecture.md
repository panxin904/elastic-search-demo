---
title: 体系结构
---

# ⚙️ MySQL 体系结构

> 理解 MySQL 是怎么运行的，是掌握所有高级特性的基础。

## 🏛️ MySQL 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Client Connections                    │
│              (JDBC / mysql client / ProxySQL)            │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  Connection Layer                        │
│   连接器（认证 / 权限校验 / 连接管理 / 最大连接数）       │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                  SQL Layer (核心)                        │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  查询缓存 │  │  解析器   │  │  优化器   │  │  执行器  │   │
│  │ (8.0删) │  │ (词法+语法)│  │ (执行计划)│  │(调用引擎)│   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│               Storage Engine Layer                        │
│                                                          │
│   InnoDB │ MyISAM │ MEMORY │ CSV │ Archive │ ...        │
│   (数据读写、索引、事务)                                │
└─────────────────────────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
         ┌────▼────┐         ┌─────▼─────┐
         │  .ibd   │         │  binlog    │
         │(数据+索引)│        │ (Server 层)│
         └─────────┘         └────────────┘
```

## 📦 各层职责详解

### 1️⃣ 连接层（Connection Layer）

负责与客户端建立连接、权限验证、连接管理：

```sql
-- 查看当前连接
SHOW PROCESSLIST;
-- 或
SELECT * FROM information_schema.PROCESSLIST;

-- 查看连接数配置
SHOW VARIABLES LIKE 'max_connections';           -- 最大连接数
SHOW VARIABLES LIKE 'wait_timeout';              -- 非交互超时（秒）
SHOW VARIABLES LIKE 'interactive_timeout';        -- 交互超时（秒）
```

**关键配置：**
- `max_connections=151`：默认 151，生产建议 1000+
- `wait_timeout=28800`：默认 8 小时
- `thread_cache_size=9`：线程缓存，避免频繁创建销毁

### 2️⃣ SQL 层（SQL Layer）

#### 2.1 查询缓存（Query Cache）⚠️ MySQL 8.0 已移除

```sql
-- MySQL 5.7 才有用，8.0 已删除
SHOW VARIABLES LIKE 'query_cache_type';
-- 0 = 关闭，1 = 开启（默认），2 = 按需
```

> 💡 **为什么 8.0 删除？** 因为只要表上有任何更新，所有相关缓存全部失效，命中率极低，反而成为性能瓶颈。

#### 2.2 解析器（Parser）

将 SQL 文本转换为解析树（AST），验证语法：

```sql
-- 查看解析错误示例
SELECT * FROMM users;  -- ❌ 语法错误
-- ERROR 1064 (42000): You have an error in your SQL syntax
```

#### 2.3 优化器（Optimizer）

决定 SQL 的执行计划，是 MySQL 的"大脑"：

```sql
-- 查看优化器选择的执行计划
EXPLAIN SELECT * FROM users WHERE name = '张三' AND age > 20;
```

**优化器的工作：**
- 选择使用哪个索引（idx_name vs idx_age）
- 决定 JOIN 的顺序（驱动表 vs 被驱动表）
- 决定子查询是否转为 JOIN
- 决定使用哪种排序算法

#### 2.4 执行器（Executor）

调用存储引擎接口，返回结果：

```sql
-- 查看执行器统计
SHOW STATUS LIKE 'Handler_read%';
-- Handler_read_first = 全索引扫描次数
-- Handler_read_key   = 使用索引次数
-- Handler_read_next  = 读取下一行次数
-- Handler_read_prev  = 读取上一行次数
-- Handler_read_rnd   = 随机读次数（应尽量低）
-- Handler_read_rnd_next = 下一随机读次数
```

### 3️⃣ 存储引擎层（Storage Engine Layer）

**MySQL 独特的设计**：查询处理与数据存储分离，是"插件式"架构。

```sql
-- 查看支持的引擎
SHOW ENGINES;

-- 查看当前库使用的引擎
SHOW VARIABLES LIKE 'default_storage_engine';
-- 默认 InnoDB（MySQL 5.6+）
```

## 🔄 SQL 执行流程详解

以 `SELECT * FROM users WHERE id = 1` 为例：

```
1. 连接器
   ├─ 客户端建立连接（TCP 三次握手）
   ├─ 验证用户名密码
   └─ 读取用户权限到内存（之后所有操作以此为准）

2. 查询缓存（8.0 已删除）
   └─ 不再检查

3. 解析器
   ├─ 词法分析：SELECT, *, FROM, users, WHERE, id, =, 1
   ├─ 语法分析：构建 AST
   └─ 检查表 users、列 id 是否存在

4. 优化器
   ├─ 选择索引（这里选 PRIMARY）
   ├─ 计算成本
   └─ 生成执行计划

5. 执行器
   ├─ 调用 InnoDB 接口读取 id=1 的行
   ├─ 检查权限（虽然优化器阶段查过，这里再查一次）
   └─ 返回结果

6. 返回结果
   └─ 客户端收到响应
```

## 🧠 Binlog：Server 层的日志

Binlog（归档日志）是 **Server 层** 实现的，所有引擎共用，记录所有数据变更。

```sql
-- 查看 binlog 状态
SHOW VARIABLES LIKE 'log_bin';             -- ON 表示开启
SHOW VARIABLES LIKE 'binlog_format';       -- ROW / STATEMENT / MIXED
SHOW BINARY LOGS;                          -- 查看所有 binlog 文件

-- 查看 binlog 内容（ROW 格式）
SHOW BINLOG EVENTS IN 'binlog.000001' LIMIT 10;
```

**Binlog 的三大作用：**
1. **主从复制**：从库读取主库的 binlog 重放
2. **数据恢复**：基于时间点恢复（如 `mysqlbinlog --start-datetime`）
3. **审计**：追踪所有数据变更

## 💾 关键文件结构

```
/var/lib/mysql/
├── ibdata1                    # 系统表空间（共享）
├── ib_logfile0, ib_logfile1   # InnoDB redo log（重要！）
├── binlog.000001               # Binlog 文件
├── mysql/                      # 系统库
├── yourdb/                     # 业务库
│   ├── db.opt                  # 库配置（字符集）
│   ├── users.frm               # 表结构（旧版本）
│   └── users.ibd               # 表数据 + 索引（InnoDB）
└── my.cnf                      # 配置文件（通常在 /etc/mysql/）
```

## 🔑 关键配置参数（生产推荐）

```ini
# /etc/mysql/my.cnf

[mysqld]
# 连接数
max_connections = 1000
max_user_connections = 800

# 字符集
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# 默认存储引擎
default-storage-engine = InnoDB

# 默认隔离级别
transaction-isolation = REPEATABLE-READ

# SQL 模式（严格）
sql_mode = 'STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION,ONLY_FULL_GROUP_BY'

# 慢查询
slow_query_log = ON
long_query_time = 1
log_queries_not_using_indexes = ON

# Binlog
log_bin = mysql-bin
binlog_format = ROW
expire_logs_days = 7

# 临时表
tmp_table_size = 64M
max_heap_table_size = 64M
```

## 📊 性能监控 SQL

```sql
-- 1. 当前连接数
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Threads_running';      -- 活跃连接

-- 2. QPS / TPS
SHOW STATUS LIKE 'Questions';             -- 总查询次数
SHOW STATUS LIKE 'Com_commit';
SHOW STATUS LIKE 'Com_rollback';

-- 3. 缓冲池命中率（应 > 99%）
SHOW STATUS LIKE 'Innodb_buffer_pool_read_requests';
SHOW STATUS LIKE 'Innodb_buffer_pool_reads';
-- 命中率 = 1 - (reads / read_requests)

-- 4. 慢查询数量
SHOW STATUS LIKE 'Slow_queries';
```

## 🎯 总结

| 层 | 作用 | 关键组件 |
|---|---|---|
| **连接层** | 客户端连接管理 | 连接器 / 权限校验 |
| **SQL 层** | SQL 解析与优化 | 解析器 / 优化器 / 执行器 |
| **存储引擎层** | 数据存储与检索 | InnoDB / MyISAM / Memory |
| **文件系统** | 持久化数据 | .ibd / .frm / binlog / redo log |

理解了这个分层架构，你就理解了为什么 MySQL 的性能调优是**多层的**：
- 连接层：连接数 / 超时
- SQL 层：索引 / 查询重写 / 缓存
- 引擎层：Buffer Pool / 事务隔离
- 文件系统：磁盘 IO / 文件系统选择

**下一步：** [🔧 存储引擎 InnoDB/MyISAM](../01-foundation/storage-engine) — 深入理解 InnoDB 的内部机制

<!-- svg-injected:do-not-edit -->

![wal architecture](/wal-architecture.svg)
