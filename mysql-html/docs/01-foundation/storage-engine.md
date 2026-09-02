---
title: 存储引擎
date: 2026-08-15  # date-auto-injected
---

# 🔧 MySQL 存储引擎

> MySQL 的**插件式架构**让你可以为每张表选择不同的存储引擎。理解各引擎特性是选型的第一步。

## 📊 引擎全景对比

| 引擎 | 事务 | 锁粒度 | MVCC | 索引 | 适用场景 | 默认 |
|---|---|---|---|---|---|---|
| **InnoDB** | ✅ | 行锁 | ✅ | B+Tree / 全文 / 空间 | **通用 OLTP**（推荐） | ✅ MySQL 5.6+ |
| **MyISAM** | ❌ | 表锁 | ❌ | B+Tree / 全文 | 只读 / 报表（**已过时**） | ❌ |
| **MEMORY** | ❌ | 表锁 | ❌ | Hash / B+Tree | 临时表 / 缓存 | ❌ |
| **CSV** | ❌ | 表锁 | ❌ | 无 | 数据交换（导入导出） | ❌ |
| **Archive** | ❌ | 行锁 | ❌ | 无 | 日志归档（只插入） | ❌ |
| **Blackhole** | ❌ | - | ❌ | - | 主从复制的"黑洞"节点 | ❌ |
| **NDB (Cluster)** | ✅ | 行锁 | ❌ | Hash | MySQL Cluster 分布式 | ❌ |
| **TokuDB** | ✅ | 行锁 | ✅ | Fractal Tree | 高写入压缩（已被 Percona 收购，MariaDB 仍可用） | ❌ |

## 🏆 InnoDB：默认且推荐的引擎

### 核心特性

```
InnoDB 架构（简化）

┌─────────────────────────────────────┐
│            InnoDB 内存               │
│  ┌─────────────────────────────┐    │
│  │     Buffer Pool (缓冲池)     │    │
│  │  ┌──────────┬──────────┐     │    │
│  │  │ 数据页    │ 索引页    │     │    │
│  │  └──────────┴──────────┘     │    │
│  └─────────────────────────────┘    │
│  ┌────────┐  ┌────────┐  ┌────────┐ │
│  │Redo Log│  │Undo Log│  │Change  │ │
│  │ Buffer │  │ Buffer │  │ Buffer │ │
│  └────────┘  └────────┘  └────────┘ │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│         InnoDB 磁盘                   │
│  ┌──────────────┐  ┌──────────────┐  │
│  │ System       │  │ User         │  │
│  │ Tablespace   │  │ Tablespace   │  │
│  │ (ibdata1)    │  │ (table.ibd)  │  │
│  └──────────────┘  └──────────────┘  │
│  ┌──────────────────────────────┐    │
│  │  Redo Log Files (ib_logfile*) │    │
│  └──────────────────────────────┘    │
└─────────────────────────────────────┘
```

### InnoDB 关键参数

```ini
[mysqld]
# ===== 内存相关 =====
innodb_buffer_pool_size = 16G          # 缓冲池（核心！建议物理内存 60-80%）
innodb_buffer_pool_instances = 8       # 缓冲池实例数（建议 = CPU 核数）
innodb_buffer_pool_chunk_size = 128M   # 动态调整时的块大小

# ===== 日志相关 =====
innodb_log_file_size = 4G              # redo log 大小（影响恢复速度）
innodb_log_files_in_group = 2          # redo log 文件数（默认 2）
innodb_log_buffer_size = 16M           # redo log 缓冲区

# ===== IO 相关 =====
innodb_io_capacity = 2000              # 磁盘 IO 能力（SSD 设 2000-5000）
innodb_io_capacity_max = 4000
innodb_flush_neighbors = 0             # SSD 关闭邻页刷新

# ===== 文件格式 =====
innodb_file_per_table = ON             # 每个表独立 .ibd 文件（推荐）
innodb_file_format = Barracuda         # 支持 DYNAMIC / COMPRESSED 行格式
innodb_default_row_format = DYNAMIC
```

### InnoDB 文件结构

```
数据库目录：/var/lib/mysql/mydb/

mydb/
├── users.frm          # 表结构（8.0 已合并到 .ibd）
├── users.ibd          # 表数据 + 索引（独立表空间模式）
│
├── orders.frm
├── orders.ibd
└── ...
```

### 关键概念

#### Buffer Pool LRU 算法

![InnoDB Buffer Pool LRU](/mysql-innodb-buffer-pool-lru.svg)

#### Buffer Pool（缓冲池）⭐⭐⭐

InnoDB **最重要的内存区域**，缓存磁盘上的数据页和索引页。

```sql
-- 查看 Buffer Pool 大小
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';

-- 查看 Buffer Pool 状态
SHOW STATUS LIKE 'Innodb_buffer_pool%';
-- Innodb_buffer_pool_pages_total  = 总页数
-- Innodb_buffer_pool_pages_free   = 空闲页数
-- Innodb_buffer_pool_pages_data   = 数据页数

-- 计算命中率（应 > 99%）
SELECT
  (1 - (SHOW STATUS LIKE 'Innodb_buffer_pool_reads' FROM dual)
       / (SHOW STATUS LIKE 'Innodb_buffer_pool_read_requests' FROM dual)
  ) * 100 AS hit_rate;
```

**LRU 优化算法：**
- 默认长度 128MB（`innodb_buffer_pool_size` 较小时会压缩）
- 分为 young 区（5/8）和 old 区（3/8）
- 防止全表扫描污染缓存

#### Redo Log（重做日志）⭐⭐

保证事务持久性（**D** in ACID）。即使宕机，也能恢复已提交的事务。

```sql
SHOW VARIABLES LIKE 'innodb_log%';
-- innodb_log_file_size = 单个 redo log 大小
-- innodb_log_files_in_group = 2（固定）
-- 总 redo log = log_file_size × log_files_in_group
```

**WAL（Write-Ahead Logging）原则：** 事务提交前，先写 redo log，再写数据文件。

#### Undo Log（回滚日志）

用于事务回滚 + MVCC 实现。每次 UPDATE/DELETE 都生成 undo 记录。

```sql
-- 查看 undo log 大小
SHOW STATUS LIKE 'Innodb_undo%';
```

#### Change Buffer（写缓冲）

对**非唯一二级索引**的写操作，先缓存在内存，再异步合并到磁盘。减少随机 IO。

## 🗑️ MyISAM：已过时的引擎

```sql
-- 创建 MyISAM 表（仅作演示，生产请用 InnoDB）
CREATE TABLE old_logs (
  id INT PRIMARY KEY,
  msg VARCHAR(200)
) ENGINE=MyISAM;
```

**MyISAM 的特点：**
- ❌ 不支持事务
- ❌ 只支持表锁（写时锁全表）
- ✅ 全文索引（InnoDB 5.6+ 也支持）
- ✅ COUNT(*) 很快（维护了行数）
- ✅ 空间函数
- ❌ 崩溃后恢复困难（损坏概率高）

**何时考虑 MyISAM：** 几乎没有。MySQL 5.6 之前默认是 MyISAM，但 5.6+ 都是 InnoDB。

## 💨 MEMORY 引擎

数据存在内存中（重启丢失），适合临时表。

```sql
CREATE TABLE session_cache (
  session_id VARCHAR(32) PRIMARY KEY,
  data JSON,
  expire_at BIGINT
) ENGINE=MEMORY;

-- 默认使用 HASH 索引
SHOW INDEX FROM session_cache;
```

**注意：**
- 数据在内存，重启丢失
- 表级锁
- 最大大小由 `max_heap_table_size` 控制

## 🎯 引擎选型决策树

```
你的应用是什么类型？
│
├── OLTP（高并发读写）
│   └── InnoDB ✅
│
├── OLAP（只读分析）
│   ├── 数据量大：ClickHouse / StarRocks
│   └── 数据量小：InnoDB + 列存引擎
│
├── 临时数据 / 缓存
│   └── MEMORY（但 Redis 更专业）
│
├── 日志归档（只插入）
│   └── Archive（高压缩比）
│
└── 数据导入导出
    └── CSV（直接编辑文本）
```

## 🔧 实战：查看当前数据库的引擎使用

```sql
-- 查看每个表的引擎
SELECT
  table_schema AS db,
  table_name AS 'table',
  engine,
  table_rows,
  ROUND((data_length + index_length) / 1024 / 1024, 2) AS size_mb
FROM information_schema.tables
WHERE table_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
ORDER BY engine, size_mb DESC;

-- 查看 InnoDB 状态
SHOW ENGINE INNODB STATUS\G
```

## ⚙️ 切换表引擎

```sql
-- 单表转换
ALTER TABLE mytable ENGINE = InnoDB;

-- 批量转换（生成 SQL）
SELECT CONCAT('ALTER TABLE ', table_name, ' ENGINE=InnoDB;')
FROM information_schema.tables
WHERE engine = 'MyISAM'
  AND table_schema = 'mydb';
```

## 🎯 总结

| 场景 | 推荐引擎 |
|---|---|
| **99% 的业务** | **InnoDB**（别想了） |
| 临时计算 / 缓存 | MEMORY（但建议 Redis） |
| 日志归档 | Archive（5:1+ 压缩） |
| 数据导入导出 | CSV（Excel 友好） |

**下一步：** [📊 数据类型](../01-foundation/data-types) — 整数、浮点、字符串、时间、JSON 怎么选