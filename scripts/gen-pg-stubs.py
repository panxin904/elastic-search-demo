#!/usr/bin/env python3
"""Generate substantial backfill content for postgresql stubs.

Output: 3-5KB per page, each with proper content per topic.
"""

from pathlib import Path

DOCS = Path("postgresql-html/docs")

# 每个 stub 的完整内容（手工写的，3-5KB）
CONTENT = {
    "01-basics/architecture.md": """---
title: 进程架构
description: PostgreSQL 进程模型与内存结构
---

# PostgreSQL 进程架构

> **TL;DR**：PG 用 **Postmaster + 多 backend 进程**模式，每客户端连接一个 backend。共享内存用 `shared_buffers / wal_buffers / clog`。**理解进程模型是调优和故障排查的基础**。

## 一句话定义

```
PostgreSQL = C/S 架构
  服务端 = 1 个 Postmaster + N 个 backend 子进程 + 多个后台 worker
  客户端 = 通过 TCP/Unix socket 连接
```

## 进程模型

### Postmaster 主进程

```
进程 PID = 1（如 /var/lib/postgresql/data/postmaster.pid 记录）
职责：
  - 监听端口（5432）
  - 接受客户端连接
  - fork backend 子进程
  - 管理共享内存
  - 启动后台 worker（bgwriter / walwriter / autovacuum launcher）
```

### backend 子进程

```
每个客户端连接 = 一个 backend 进程
连接断开 = 进程退出

backend 负责：
  - 解析 SQL
  - 生成执行计划
  - 执行查询
  - 返回结果
```

**进程 vs 线程**：

| 维度 | PG（进程） | MySQL（线程） |
|---|---|---|
| 内存 | 不共享（独立） | 共享（需锁） |
| 上下文切换 | 重 | 轻 |
| 稳定性 | 单连接崩溃不影响其他 | | 线程崩溃可能影响全局 |
| 连接数上限 | 几百（受进程数限制） | 上千 |

> **PG 13+**：改进 fork 性能，1000+ 连接数 OK。

### 后台 Worker 进程

| 进程 | 职责 | 默认数量 |
|---|---|---|
| **bgwriter** | 把脏页写回磁盘 | 1 |
| **walwriter** | 把 WAL 刷盘 | 1 |
| **autovacuum launcher** | autovacuum worker 调度 | 1 |
| **autovacuum worker** | 实际 vacuum | max_workers（默认 3） |
| **stats collector** | 收集统计信息 | 1 |
| **logical replication launcher** | 逻辑复制调度 | 1 |
| **walsender** | 流复制 sender | max_wal_senders |
| **walreceiver** | 流复制 receiver | 每个从库 1 个 |

## 内存结构

### 共享内存（Shared Memory）

```
┌────────────────────────────────────────────────┐
│                Shared Buffers                  │
│  ┌──────────────────────────────────────────┐  │
│  │  shared_buffers（默认 128MB）             │  │
│  │  - 数据页缓存                              │  │
│  │  - 索引页缓存                              │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  wal_buffers（默认 16MB）                 │  │
│  │  - WAL 日志缓冲                            │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  CLOG（Commit Log）                       │  │
│  │  - 事务提交状态                            │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  Lock Manager（锁管理）                    │  │
│  └──────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────┐  │
│  │  FSM（Free Space Map）+ VM（Visibility Map）│  │
│  └──────────────────────────────────────────┘  │
└────────────────────────────────────────────────┘
```

### 每个 backend 的私有内存

```
- work_mem：排序/哈希操作（默认 4MB，可按需调整）
- temp_buffers：临时表（默认 8MB）
- maintenance_work_mem：vacuum / create index（默认 64MB）
```

## 关键配置

```ini
# postgresql.conf

# 1. 共享内存
shared_buffers = '8GB'              # 推荐 25% 物理内存
wal_buffers = '64MB'                # 默认 16MB，写密集型加大

# 2. 后台 worker
bgwriter_delay = '50ms'             # bgwriter 唤醒间隔
bgwriter_lru_maxpages = 400         # 每次最多写 400 页
autovacuum_max_workers = 4          # autovacuum worker 数

# 3. 连接
max_connections = 200               # 最大连接数
superuser_reserved_connections = 3  # 给 superuser 预留

# 4. 内存
work_mem = '64MB'                   # 每操作内存
hash_mem_multiplier = 2.0           # hash join 内存倍数（PG 13+）
maintenance_work_mem = '512MB'      # 维护操作
```

## 实战案例

### 案例：1000 并发系统的进程数调优

**问题**：应用 1000 并发，PG 默认 max_connections=100，后端连接不够。

**方案**：

```ini
# 1. 提高 max_connections（不推荐，因为每连接吃 5-10MB）
max_connections = 300

# 2. 用 PgBouncer 连接池（推荐）
pool_mode = transaction
default_pool_size = 50
# 应用 1000 并发 → PG 后端 50 个连接
```

```sql
-- 查看当前连接数
SELECT count(*) FROM pg_stat_activity;

-- 看每个 backend 状态
SELECT pid, state, query_start, query
FROM pg_stat_activity
WHERE backend_type = 'client backend';
```

## 一句话总结

> **PG 进程模型 = Postmaster + N backend + N worker**。**每连接一个进程 = 内存 5-10MB**，**生产用 PgBouncer 池化**。**shared_buffers 设 25% RAM**，**work_mem 按需调整**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "01-basics/config.md": """---
title: 关键配置参数
description: postgresql.conf 核心参数调优
---

# 关键配置参数

> **TL;DR**：`postgresql.conf` 有 300+ 参数，**生产只需调 10 个核心参数**就能拿到 80% 性能。**调参原则：先用默认 → 监控瓶颈 → 针对性调整**。

## 一句话定义

```
postgresql.conf = PG 主配置文件
                 = 300+ 参数
                 = 90% 时间只动 10 个核心参数
```

## 10 个核心参数

### 1. shared_buffers（共享缓冲）

```ini
shared_buffers = '8GB'    # 默认 128MB
```

**推荐**：**25% 物理内存**（如 32GB 机器 → 8GB）

**效果**：缓存数据页 + 索引页，**命中 = 不读盘**

### 2. effective_cache_size（planner 决策）

```ini
effective_cache_size = '24GB'    # 默认 4GB
```

**推荐**：**50-75% 物理内存**

**作用**：**不是真实内存分配**，而是告诉 planner "OS 文件缓存大约这么多"，影响是否选择索引扫描

### 3. work_mem（操作内存）

```ini
work_mem = '64MB'    # 默认 4MB
```

**适用**：sort / hash join / hash aggregate

**调优**：根据实际查询调，**太大 = 占用过多内存**，**太小 = 临时文件 spill**

### 4. maintenance_work_mem（维护内存）

```ini
maintenance_work_mem = '512MB'    # 默认 64MB
```

**适用**：VACUUM / CREATE INDEX / ALTER TABLE ADD FOREIGN KEY

**调优**：**可以比 work_mem 大很多**（不是并发操作）

### 5. max_connections（最大连接）

```ini
max_connections = 200    # 默认 100
```

**调优**：**不要超过 300**，**配 PgBouncer 池化**

### 6. WAL 相关

```ini
wal_level = replica                  # 流复制需要
wal_compression = on                 # 压缩 WAL
max_wal_size = '4GB'                 # checkpoint 后最大
min_wal_size = '1GB'
wal_keep_size = '1GB'                # 防止从库断连 WAL 撑爆
```

### 7. autovacuum

```ini
autovacuum = on                      # 默认 on
autovacuum_max_workers = 4           # 默认 3
autovacuum_naptime = '60s'           # 默认 60s 检测
```

### 8. checkpoint

```ini
checkpoint_completion_target = 0.9   # 默认 0.5，平滑 checkpoint
max_wal_size = '4GB'                 # 触发 checkpoint
```

### 9. 查询规划器

```ini
random_page_cost = 1.1               # 默认 4，SSD 改成 1.1
effective_io_concurrency = 200       # SSD 推荐 200，HDD 用 2
```

### 10. 日志

```ini
logging_collector = on
log_destination = 'stderr'
log_min_duration_statement = '500ms' # 记录 > 500ms 的 SQL
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on                  # 锁等待日志
log_temp_files = 0                   # 记录所有临时文件
```

## 调参检查清单

```ini
# 1. 内存类
shared_buffers = '25% RAM'           # 8GB
effective_cache_size = '70% RAM'     # 22GB
work_mem = '32-128MB'                # 看并发数调整
maintenance_work_mem = '512MB'

# 2. 存储类（SSD 优化）
random_page_cost = 1.1
effective_io_concurrency = 200
wal_compression = on

# 3. 连接类
max_connections = 200                # 配合 PgBouncer
superuser_reserved_connections = 3

# 4. WAL 类
wal_level = replica
max_wal_size = '4GB'
checkpoint_completion_target = 0.9

# 5. autovacuum
autovacuum_max_workers = 4
autovacuum_naptime = '30s'           # 检测频率提高

# 6. 监控
shared_preload_libraries = 'pg_stat_statements'
log_min_duration_statement = '500ms'
auto_explain.log_min_duration = '1s' # 配合 auto_explain
```

## 查看当前配置

```sql
-- 当前生效的配置
SHOW shared_buffers;
SHOW all;                  -- 所有参数
SELECT * FROM pg_settings;

-- 修改（session 级别）
SET work_mem = '128MB';

-- 修改（持久）
ALTER SYSTEM SET work_mem = '128MB';
SELECT pg_reload_conf();
```

## 配置文件位置

```bash
# 默认位置
/usr/local/pgsql/data/postgresql.conf      # 源码编译
/etc/postgresql/15/main/postgresql.conf   # Debian/Ubuntu
/var/lib/pgsql/data/postgresql.conf       # CentOS

# 配置目录（include_dir）
postgresql.conf 中：
include_dir = 'conf.d'  # 加载 conf.d/*.conf
```

> **生产建议**：**自定义参数放 conf.d/，不动主配置文件**，方便升级。

## 一句话总结

> **调参 80/20**：**shared_buffers 25% RAM + effective_cache_size 70% RAM + work_mem 64MB + 8 个其他参数 = 拿到 80% 性能**。**先用默认 → 监控 → 针对性调整**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "02-data-types/built-in.md": """---
title: 内置类型
description: PostgreSQL 内置类型全景
---

# PostgreSQL 内置类型

> **TL;DR**：PG 内置 **30+ 类型**，比其他 RDBMS（MySQL 20+）丰富。**数值、字符串、时间、布尔是基础**，**JSON / 数组 / UUID / 范围类型是 PG 特色**。

## 一句话定义

```
PG 类型 = 标量类型（数值/字符串/时间）+ 复合类型（数组/JSONB/范围）+ 自定义类型
```

## 数值类型

| 类型 | 大小 | 范围 | 用途 |
|---|---|---|---|
| `smallint` / `int2` | 2 字节 | -32768 ~ 32767 | 小整数（不常用） |
| `integer` / `int4` | 4 字节 | -2.1亿 ~ 2.1亿 | **最常用** |
| `bigint` / `int8` | 8 字节 | ±9.2×10^18 | 大整数（id） |
| `numeric(p, s)` | 变长 | 任意精度 | **金额**（必须用） |
| `real` / `float4` | 4 字节 | 6 位精度 | 浮点数（科学计算） |
| `double precision` / `float8` | 8 字节 | 15 位精度 | 高精度浮点 |
| `smallserial` / `serial2` | 2 字节 | 自增 | 序列 |
| `serial` / `serial4` | 4 字节 | 自增 | **最常用序列** |
| `bigserial` / `serial8` | 8 字节 | 自增 | 大序列 |

```sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  age SMALLINT,
  score INTEGER,
  money NUMERIC(10, 2)         -- 10 位数 + 2 位小数（金额必备）
);
```

> **金额永远用 NUMERIC**，**不要用 FLOAT**（浮点有误差）。

## 字符串类型

| 类型 | 特点 | 推荐 |
|---|---|---|
| `char(n)` | 定长，补空格 | **不推荐**（除非真的定长） |
| `varchar(n)` | 变长，限长 | 推荐（限长） |
| `text` | 无限变长 | **最推荐**（不限长） |

```sql
CREATE TABLE articles (
  code CHAR(10),              -- 定长 10 字符（补空格）
  name VARCHAR(100),          -- 最多 100 字符
  content TEXT                -- 无限长度
);
```

> **PG 没有性能差异**：varchar(n) vs text 性能相同，**统一用 text 即可**。

## 时间类型

| 类型 | 特点 | 推荐 |
|---|---|---|
| `date` | 仅日期 | 生日 |
| `time` | 仅时间 | 不常用 |
| `time with time zone` | 时间 + 时区 | 不常用 |
| `timestamp` | 日期时间 | 不带时区（**避免**） |
| `timestamptz` | 日期时间 + 时区 | **必用** |
| `interval` | 时间间隔 | 业务计算 |

```sql
-- 强烈推荐 timestamptz
CREATE TABLE events (
  occurred_at TIMESTAMPTZ DEFAULT now()
);

-- 当前时间
SELECT now();                    -- 事务开始时间
SELECT current_timestamp;        -- 同 now()
SELECT clock_timestamp();        -- 实际时间（微秒级）
SELECT statement_timestamp();    -- 语句开始时间
```

## 布尔类型

```sql
CREATE TABLE users (
  is_active BOOLEAN DEFAULT true,
  is_deleted BOOLEAN DEFAULT false
);

-- 插入
INSERT INTO users (is_active) VALUES (true), (false), ('yes'), ('no'), ('t'), ('f'), ('1'), ('0');
-- PG 接受多种写法（兼容性好）
```

## UUID 类型

```sql
-- 启用扩展
CREATE EXTENSION pgcrypto;       -- 旧版 PG
-- PG 13+ 自带 gen_random_uuid()

-- 生成 UUID
SELECT gen_random_uuid();
-- 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'

-- 用作主键
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid()
);
```

## JSON / JSONB 类型

| 类型 | 特点 | 推荐 |
|---|---|---|
| `json` | 文本存储，保留格式 | 保留原始 JSON 时用 |
| `jsonb` | 二进制存储，自动解析 | **90% 场景用** |

```sql
CREATE TABLE products (
  data JSONB
);

CREATE INDEX idx_products_data ON products USING GIN (data);

-- 查询
SELECT * FROM products WHERE data @> '{"category": "electronics"}';
```

## 数组类型

```sql
CREATE TABLE articles (
  tags TEXT[]
);

CREATE INDEX idx_articles_tags ON articles USING GIN (tags);

-- 查询
SELECT * FROM articles WHERE tags @> ARRAY['postgres'];
```

## 特殊类型

| 类型 | 用途 |
|---|---|
| `bytea` | 二进制数据（图片、文件） |
| `xml` | XML 文档 |
| `cidr` / `inet` / `macaddr` | IP / MAC 地址 |
| `point` / `line` / `box` / `circle` | 几何类型（基础） |
| `pg_lsn` | WAL 日志序列号 |
| `tsvector` | 全文检索向量 |
| `pg_snapshot` | 事务快照 |

## 类型转换

```sql
-- 显式转换
SELECT '100'::INTEGER;
SELECT CAST('100' AS INTEGER);

-- 隐式转换（PG 保守，避免意外）
SELECT '100' + 200;  -- '300' (自动转 integer)

-- 日期转字符串
SELECT to_char(now(), 'YYYY-MM-DD HH24:MI:SS');

-- 字符串转日期
SELECT '2026-08-09'::DATE;
SELECT to_date('2026-08-09', 'YYYY-MM-DD');
```

## 一句话总结

> **PG 类型比 MySQL 丰富**：**金额 NUMERIC、时间 TIMESTAMPTZ、文本 TEXT、UUID、JSONB、数组**是 6 大常用类型。**金额永远 NUMERIC**，**时间永远 TIMESTAMPTZ**，**JSONB 配 GIN 索引**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "02-data-types/custom.md": """---
title: 自定义类型
description: CREATE TYPE 实战
---

# 自定义类型

> **TL;DR**：`CREATE TYPE` 让 PG 支持**复合类型、枚举、范围**自定义。**复合类型**把多个字段绑成一行，**枚举**限定值集合，**范围**封装"区间"语义。

## 一句话定义

```
PG 自定义类型 = 复合类型（行）/ 枚举（固定集合）/ 范围（区间）/ 基类型（C 扩展）
```

## 复合类型（Composite Type）

**类似"行类型"**：把多个字段绑成一个类型。

```sql
-- 1. 定义复合类型
CREATE TYPE address AS (
  street TEXT,
  city TEXT,
  zip TEXT,
  country TEXT
);

-- 2. 用作表字段
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  home_address address
);

-- 3. 插入
INSERT INTO users (name, home_address) VALUES
  ('Alice', ROW('长安街 1 号', '北京', '100000', '中国'));

-- 4. 查询
SELECT (home_address).city FROM users WHERE id = 1;
-- '北京'

-- 5. 修改
UPDATE users 
SET home_address.city = '上海'    -- 注意语法
WHERE id = 1;
```

**作为函数参数 / 返回值**：

```sql
-- 返回复合类型
CREATE FUNCTION get_user(id INT) RETURNS users AS $$
  SELECT * FROM users WHERE id = $1;
$$ LANGUAGE SQL;

-- 调用
SELECT * FROM get_user(123);
```

## 枚举类型（ENUM）

**固定值集合**：状态字段、类型字段。

```sql
-- 1. 定义枚举
CREATE TYPE order_status AS ENUM (
  'pending', 'paid', 'shipped', 'delivered', 'cancelled'
);

-- 2. 用作表字段
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  status order_status DEFAULT 'pending'
);

-- 3. 插入
INSERT INTO orders (status) VALUES ('paid');
-- 自动校验：无效值报错
INSERT INTO orders (status) VALUES ('invalid');
-- ERROR: invalid input value for enum order_status: 'invalid'

-- 4. 查询
SELECT * FROM orders WHERE status = 'paid';

-- 5. 排序（按定义顺序）
SELECT * FROM orders ORDER BY status;
-- pending → paid → shipped → ...
```

### 添加新枚举值

```sql
-- 在末尾追加
ALTER TYPE order_status ADD VALUE 'returned';

-- 在指定位置插入（PG 9.6+）
ALTER TYPE order_status ADD VALUE 'refunded' BEFORE 'cancelled';
```

### 枚举 vs CHECK 约束

```sql
-- 用 CHECK（灵活但性能差）
CREATE TABLE orders (
  status TEXT CHECK (status IN ('pending', 'paid', 'shipped'))
);

-- 用 ENUM（严格且高效）
CREATE TABLE orders (
  status order_status
);
```

> **枚举优势**：**类型安全、存储紧凑、排序自然**。**CHECK 优势**：**灵活、可以随时改**。

## 范围类型（Range）

PG 内置 6 种范围类型（int4range / numrange / daterange / tsrange / tstzrange），也可自定义：

```sql
-- 自定义 float 范围类型
CREATE TYPE floatrange AS RANGE (
  subtype = float8,
  subtype_diff = float8mi
);

-- 用法
SELECT floatrange(1.0, 9.5, '[]');
```

详见 [range.md](/02-data-types/range)。

## 基类型（Base Type）

**用 C 语言扩展**，是 PG 扩展开发的核心。

```c
// 示例：实现一个复数类型
#include "fmgr.h"

PG_MODULE_MAGIC;

PG_FUNCTION_INFO_V1(complex_in);
PG_FUNCTION_INFO_V1(complex_out);

Datum complex_in(PG_FUNCTION_ARGS) {
  // 解析字符串 "1,2" → complex
}

Datum complex_out(PG_FUNCTION_ARGS) {
  // complex → 字符串 "1,2"
}
```

```sql
-- 注册
CREATE TYPE complex (
  input = complex_in,
  output = complex_out,
  internallength = 16,
  alignment = double
);
```

> **基类型开发门槛高**，**90% 场景用复合 / 枚举 / 范围足够**。

## 实战案例

### 案例 1：电商订单状态枚举

```sql
CREATE TYPE order_status AS ENUM (
  'created', 'paid', 'packed', 'shipped', 'delivered', 'refunded', 'cancelled'
);

CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  status order_status DEFAULT 'created',
  amount NUMERIC(10,2)
);

-- 历史状态迁移（添加 'returned'）
ALTER TYPE order_status ADD VALUE 'returned' AFTER 'delivered';
```

### 案例 2：地址复合类型

```sql
CREATE TYPE address AS (
  street TEXT,
  city TEXT,
  state TEXT,
  zip TEXT,
  country TEXT
);

CREATE TABLE customers (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  shipping_address address,
  billing_address address
);

-- 查北京客户
SELECT * FROM customers 
WHERE (shipping_address).city = '北京';
```

### 案例 3：自定义 IP 段类型

```sql
CREATE TABLE ip_allocations (
  range cidr,
  owner TEXT
);

CREATE INDEX idx_ip_range ON ip_allocations USING SPGIST (range);

-- 查 192.168.1.100 在哪个段
SELECT * FROM ip_allocations 
WHERE range >> '192.168.1.100'::inet;
```

## 一句话总结

> **CREATE TYPE 让 PG 类型系统可扩展**：**复合类型（行）**、**ENUM（枚举）**、**范围（区间）**是 3 大常用自定义类型。**枚举限定值集合** + **复合类型封装结构**，**避免散落的字典表**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "03-tables-and-indexes/brin.md": """---
title: BRIN 索引
description: Block Range 索引（适合时序数据）
---

# BRIN 索引

> **TL;DR**：BRIN（Block Range Index）= **块范围索引**，索引大小只有 B-tree 的 **1/100**。**适合自然有序的大表（时序、日志）**，**查询范围扫描性能接近 B-tree**。

## 一句话定义

```
BRIN = 把表按块（默认 128 个 page = 1MB）分组
     = 每个块记录一组元数据（min/max/sum）
     = 查询时先看元数据，命中范围才深入扫描
```

## 适用场景

```
✓ 时间戳 / 序号单调递增的大表（> 1 亿行）
✓ 日志、事件、监控数据
✓ 数据按物理顺序写入（INSERT 顺序）
✓ 查询多按时间范围扫描

✗ 数据随机分布（不适用）
✗ 需要等值查询 + 大量更新
✗ 小表（< 1000 万行）
```

## 基本使用

```sql
-- 1. 创建 BRIN 索引
CREATE TABLE events (
  id BIGSERIAL,
  occurred_at TIMESTAMPTZ NOT NULL,
  data JSONB
);

CREATE INDEX idx_events_time ON events USING BRIN (occurred_at);

-- 2. 范围查询（用 BRIN）
SELECT * FROM events 
WHERE occurred_at >= '2026-08-01' AND occurred_at < '2026-08-09';

-- EXPLAIN 看
EXPLAIN SELECT * FROM events 
WHERE occurred_at >= '2026-08-01' AND occurred_at < '2026-08-09';

-- Bitmap Heap Scan on events
--   Recheck Cond: ...
--   ->  Bitmap Index Scan on idx_events_time
```

## 关键参数

### pages_per_range

```sql
-- 默认 128 (1MB)
CREATE INDEX idx_events_time ON events USING BRIN (occurred_at) WITH (pages_per_range = 32);
```

**调优**：
- **更小**（如 16）= 更精细，但索引更大、扫描稍慢
- **更大**（如 256）= 更粗，索引更小，但可能漏过滤（需要 recheck）

### autosummarize

```sql
-- PG 11+ 自动总结
ALTER INDEX idx_events_time SET (autosummarize = on);
```

## BRIN vs B-tree

| 维度 | B-tree | BRIN |
|---|---|---|
| 索引大小 | 100% | **1-5%** |
| 查询速度 | 极快 | 快（有 recheck 开销） |
| 等值查询 | ✓ | ✗（不适用） |
| 范围查询 | ✓ | ✓ |
| 排序 | ✓ | ✗ |
| 适用数据 | 任意 | 自然有序 |

## 实战案例

### 案例 1：百亿行日志

```sql
CREATE TABLE app_logs (
  id BIGSERIAL,
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  level TEXT,
  message TEXT
);

-- 1. 按月分区
CREATE TABLE app_logs_2026_08 PARTITION OF app_logs
  FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

-- 2. 每个分区建 BRIN 索引
CREATE INDEX idx_logs_2026_08_ts ON app_logs_2026_08 USING BRIN (ts);

-- 索引大小对比：
-- B-tree: 500 MB
-- BRIN:   5 MB (1%)
```

### 案例 2：监控指标数据

```sql
CREATE TABLE metrics (
  id BIGSERIAL,
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  host TEXT,
  cpu NUMERIC(5,2)
);

-- 查某个时间段的 CPU 数据
CREATE INDEX idx_metrics_ts ON metrics USING BRIN (ts);

SELECT host, avg(cpu) FROM metrics
WHERE ts >= now() - interval '1 hour'
GROUP BY host;
-- BRIN 索引快速定位 1MB 范围，再 GROUP BY
```

### 案例 3：传感器时序

```sql
CREATE TABLE sensor_data (
  sensor_id INT,
  recorded_at TIMESTAMPTZ NOT NULL,
  value NUMERIC
);

-- 按时间建 BRIN
CREATE INDEX idx_sensor_time ON sensor_data USING BRIN (recorded_at);

-- 查最近 1 小时
SELECT * FROM sensor_data
WHERE recorded_at >= now() - interval '1 hour'
  AND sensor_id = 123;

-- 复合查询 = BRIN 粗筛 + 索引细筛
```

## 与分区表配合

**BRIN + RANGE 分区 = 大表最佳组合**：

```sql
-- 1. 按月分区
CREATE TABLE events (...) PARTITION BY RANGE (occurred_at);
CREATE TABLE events_2026_08 PARTITION OF events
  FOR VALUES FROM ('2026-08-01') TO ('2026-09-01');

-- 2. 每分区建 BRIN
CREATE INDEX idx_events_2026_08_brin 
  ON events_2026_08 USING BRIN (occurred_at);

-- 3. 查询：PG 自动 partition pruning + BRIN 块过滤
SELECT * FROM events
WHERE occurred_at >= '2026-08-01' AND occurred_at < '2026-08-02';
-- 只扫 events_2026_08 分区 → BRIN 进一步过滤
```

## 注意事项

### 1. 大量 UPDATE 会失效

```
BRIN 记录每块的 min/max → UPDATE 后可能不再准确
PG 自动 recheck，但性能下降
解决：定期 REINDEX
```

### 2. 顺序写入很重要

```sql
-- ✓ 按时间顺序 INSERT
INSERT INTO events (ts) VALUES 
  ('2026-08-01'), ('2026-08-02'), ('2026-08-03');

-- ✗ 乱序 INSERT（多个 worker 并行写入）
-- BRIN 索引效果差
```

## 一句话总结

> **BRIN = 时序数据的最佳索引**：索引大小只有 B-tree 的 1-5%，**查询范围扫描性能接近 B-tree**。**前提：数据按物理顺序写入**（典型场景：日志、事件、监控）。**配合 RANGE 分区 = 大表最佳方案**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "03-tables-and-indexes/gist.md": """---
title: GiST 索引
description: Generalized Search Tree（多维 + 范围 + 全文）
---

# GiST 索引

> **TL;DR**：GiST（Generalized Search Tree）= **通用搜索树**，适合**多维数据**（几何、范围）和**全文检索**。PostGIS、pg_trgm、tsvector 都基于 GiST。

## 一句话定义

```
GiST = 平衡树 + 多种策略（每种数据类型实现自己的"如何分裂 + 如何查询"）
     = 适合多维 / 范围 / 全文
```

## 适用场景

```
✓ 几何数据（点 / 线 / 面 / 圆）
✓ 范围类型（range）
✓ 全文检索（tsvector）
✓ hstore / ltree（键值对 / 树结构）
✓ IP 地址（inet）

✗ 等值查询（用 B-tree）
✗ 简单排序（用 B-tree）
```

## 基本使用

```sql
-- 几何类型
CREATE TABLE places (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  location POINT
);

CREATE INDEX idx_places_loc ON places USING GIST (location);

-- 查询：某点 10 公里内的所有 places
SELECT * FROM places 
WHERE location <-> point(116.4, 39.9) < 0.1;
```

## 几何查询实战

```sql
-- 创建表
CREATE TABLE stores (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  location POINT
);

-- 附近 5km 的店
CREATE INDEX idx_stores_loc ON stores USING GIST (location);

-- 用 <-> 操作符（按距离排序）
SELECT name, location <-> point(116.4, 39.9) AS distance
FROM stores
ORDER BY location <-> point(116.4, 39.9)
LIMIT 10;

-- 用 <@ 操作符（包含关系）
SELECT * FROM stores
WHERE location <@ box '((116.3, 39.8), (116.5, 40.0))';

-- 范围
SELECT * FROM stores WHERE location @> point(116.4, 39.9);
```

## 范围类型索引

```sql
CREATE TABLE bookings (
  id BIGSERIAL,
  room_id INT,
  period daterange
);

CREATE INDEX idx_bookings_period ON bookings USING GIST (period);

-- 找与新预订冲突的所有预订
SELECT * FROM bookings
WHERE room_id = 1
  AND period && daterange('2026-08-09', '2026-08-11');

-- 排除约束（防重叠）
ALTER TABLE bookings
ADD CONSTRAINT no_overlap EXCLUDE USING GIST (
  room_id WITH =,
  period WITH &&
);
```

## 全文检索

```sql
CREATE TABLE articles (
  id BIGSERIAL,
  title TEXT,
  body TEXT,
  tsv tsvector
);

CREATE INDEX idx_articles_tsv ON articles USING GIST (tsv);

-- 自动填充
UPDATE articles 
SET tsv = to_tsvector('english', title || ' ' || body);

-- 全文查询
SELECT * FROM articles
WHERE tsv @@ to_tsquery('english', 'postgres & performance');
```

## GiST vs GIN

| 维度 | GiST | GIN |
|---|---|---|
| 查询速度 | 较慢（需 recheck） | 快 |
| 写入速度 | 快 | 慢 |
| 索引大小 | 中等 | 大 |
| 多值字段 | 适合 | 更好（倒排） |
| 全文检索 | ✓ | ✓（更优） |
| 多维空间 | ✓ | ✗ |
| 范围类型 | ✓ | ✗ |
| 几何 | ✓ | ✗ |

**选型决策**：

```
要空间 / 范围数据？
├─ 是 → GiST
└─ 否（多值 / JSONB / 数组 / 全文）→ GIN
```

## 实战案例

### 案例 1：附近的人

```sql
CREATE TABLE users (
  id BIGSERIAL,
  name TEXT,
  location POINT
);

CREATE INDEX idx_users_loc ON users USING GIST (location);

-- 查附近 1km 的人
SELECT id, name,
  location <-> point(116.4, 39.9) AS distance
FROM users
WHERE location <-> point(116.4, 39.9) < 0.01  -- 约 1km
ORDER BY distance
LIMIT 20;
```

### 案例 2：会议室预订（防冲突）

```sql
CREATE TABLE room_bookings (
  id BIGSERIAL,
  room_id INT,
  period tstzrange,
  who TEXT
);

CREATE INDEX idx_bookings ON room_bookings USING GIST (room_id, period);

ALTER TABLE room_bookings
ADD CONSTRAINT no_overlap EXCLUDE USING GIST (
  room_id WITH =,
  period WITH &&
);

-- 插入冲突预订会自动报错
INSERT INTO room_bookings (room_id, period, who)
VALUES (1, tstzrange('2026-08-09 10:00', '2026-08-09 12:00'), '张三');

INSERT INTO room_bookings (room_id, period, who)
VALUES (1, tstzrange('2026-08-09 11:00', '2026-08-09 13:00'), '李四');
-- ERROR: conflicting key value violates exclusion constraint
```

### 案例 3：IP 段查询

```sql
CREATE TABLE ip_whitelist (
  range cidr,
  description TEXT
);

CREATE INDEX idx_ip_range ON ip_whitelist USING GIST (range);

-- 192.168.1.100 在哪些白名单里
SELECT * FROM ip_whitelist
WHERE range >> '192.168.1.100'::inet;
```

## 一句话总结

> **GiST = 多维数据的最佳索引**：几何、范围、全文检索、IP 地址。**配 EXCLUDE 约束实现"自动防重叠"**（会议室、IP 段唯一性）。**多维选 GiST，多值（JSONB / 数组）选 GIN**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "03-tables-and-indexes/hash.md": """---
title: Hash 索引
description: PG 10+ 可用的 Hash 索引
---

# Hash 索引

> **TL;DR**：PG 10+ 的 Hash 索引**真正可用**（WAL 记录 + crash-safe + 复制安全）。**但实务中很少用**，因为 B-tree 等值查询也很快。**仅在特定场景下用 Hash**。

## 一句话定义

```
Hash 索引 = 通过哈希函数把键映射到 bucket
          = PG 10+ 真正可用
          = 仅支持等值查询
```

## 何时使用

```
✗ 90% 场景：等值查询用 B-tree（性能相当，能力更强）
✓ 极少数场景：超大数据量等值查询 + 写入频繁
  - 例如：10 亿行的用户 ID 字段
  - B-tree 索引大，Hash 索引更紧凑（PG 11+）
```

## 基本使用

```sql
-- 1. 创建 Hash 索引
CREATE INDEX idx_users_email ON users USING HASH (email);

-- 2. 等值查询（用 Hash）
SELECT * FROM users WHERE email = '[email protected]';

-- 3. EXPLAIN 看
EXPLAIN SELECT * FROM users WHERE email = '[email protected]';
-- Index Scan using idx_users_email on users
```

## Hash vs B-tree

| 维度 | Hash | B-tree |
|---|---|---|
| 等值查询 | ✓ | ✓ |
| 范围查询 | ✗ | ✓ |
| 排序 | ✗ | ✓ |
| 前缀匹配 | ✗ | ✓ |
| 索引大小 | 略小 | 中 |
| 写入性能 | 略快 | 略快 |

## 注意事项

```sql
-- 1. Hash 索引只能 PG 10+（之前版本 crash 后失效）
-- 2. 不能被 UNIQUE 约束自动使用（必须显式 CREATE INDEX）
-- 3. 没有 hash 索引的合并优化
```

## 一句话总结

> **Hash 索引 = B-tree 等值查询的"性能变体"**。**PG 10+ 才真正可用**，但**90% 场景用 B-tree 就够了**。**只有在写密集 + 等值查询 + 不需要排序时才考虑 Hash**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "03-tables-and-indexes/spgist.md": """---
title: SP-GiST 索引
description: Space-Partitioned GiST
---

# SP-GiST 索引

> **TL;DR**：SP-GiST（Space-Partitioned GiST）= **空间分区树**，适合**非平衡数据结构**（IP 前缀、电话号码、地理坐标）。**典型应用：inet 类型索引**。

## 一句话定义

```
SP-GiST = 把搜索空间递归切分
        = 不平衡树（某些分支深、某些浅）
        = 适合 IP / 电话号码 / 地理四叉树
```

## 适用场景

```
✓ inet 类型（IP 前缀）
✓ 电话号码（E.164 格式）
✓ 地理坐标（四叉树）
✓ 字符串前缀（TRIE）
✗ 等值查询（用 B-tree）
✗ 范围查询（用 B-tree 或 GiST）
```

## 基本使用

```sql
-- 1. inet 类型 + SP-GiST
CREATE TABLE ip_logs (
  id BIGSERIAL,
  client_ip INET
);

CREATE INDEX idx_ip_logs_ip ON ip_logs USING SPGIST (client_ip);

-- 查询特定 IP
SELECT * FROM ip_logs WHERE client_ip = '192.168.1.100';
```

## IP 段查询

```sql
CREATE TABLE ip_whitelist (
  cidr CIDR,
  description TEXT
);

CREATE INDEX idx_ip_whitelist ON ip_whitelist USING SPGIST (cidr);

-- 192.168.1.100 在哪些白名单段
SELECT * FROM ip_whitelist 
WHERE cidr >> '192.168.1.100'::inet;
```

## 性能对比

```
-- 10 万行 inet 数据

-- B-tree：
--   = 等值 OK，CIDR 查询需要函数或表达式索引
--   索引大小：100%

-- SP-GiST：
--   = 天然支持 CIDR 的 prefix 查询
--   索引大小：~30%（更紧凑）
```

## 一句话总结

> **SP-GiST = 非平衡树的索引**：适合 IP / 电话号码 / 前缀树。**最实用：inet / cidr 类型**。**B-tree 能搞定就用 B-tree**，**只有 CIDR / 前缀场景才考虑 SP-GiST**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "03-tables-and-indexes/table.md": """---
title: 表与存储
description: PG 物理存储结构
---

# 表与存储

> **TL;DR**：PG 表存储是 **Heap 文件 + FSM + VM + TOAST**。理解这些结构是调优和故障排查的基础。

## 一句话定义

```
Heap 文件 = 1 个或多个 1GB segment
         = 内部按 8KB page 组织
         = 每张表有 oid + relfilenode
```

## Heap 文件结构

```
表 users 的物理文件：
  /var/lib/postgresql/data/base/16384/16385

文件大小：1GB 后自动分 segment
  16385            ← 第 1 个 segment（最多 1GB）
  16385.1          ← 第 2 个 segment
  16385.2          ← 第 3 个 segment
```

**每个 page（8KB）结构**：

```
┌────────────────────────────────────┐
│ Page Header (24 bytes)            │
│  - LSN                             │
│  - Checksum                        │
│  - Free space pointer              │
├────────────────────────────────────┤
│ Item Pointers (4 bytes each)       │
│  指向每个 tuple 的位置             │
├────────────────────────────────────┤
│ Free Space                         │
├────────────────────────────────────┤
│ Tuples (按插入顺序)                │
│  - Tuple Header (23 bytes)        │
│  - NULL bitmap (optional)         │
│  - User data (column values)       │
└────────────────────────────────────┘
```

## TOAST（The Oversized-Attribute Storage Technique）

**超长字段自动外存**：

```sql
-- 字段超过 2KB 自动压缩 + 外存到 TOAST 表
CREATE TABLE articles (
  id BIGSERIAL PRIMARY KEY,
  title TEXT,
  content TEXT                      -- 自动 TOAST
);

-- TOAST 策略
ALTER TABLE articles ALTER COLUMN content SET STORAGE EXTENDED;  -- 压缩 + 外存
ALTER TABLE articles ALTER COLUMN content SET STORAGE EXTERNAL;  -- 只外存
ALTER TABLE articles ALTER COLUMN content SET STORAGE PLAIN;     -- 不处理
ALTER TABLE articles ALTER COLUMN content SET STORAGE MAIN;      -- 不压缩外存
```

**TOAST 触发**：

```
- 行长度 > TOAST_TUPLE_THRESHOLD（默认 2KB）
- 字段值 > 2KB 时压缩 + 切分到多个 TOAST chunk
- TOAST chunk 最大 2KB
- 最大字段值 1GB（TOAST 最大）
```

## FSM + VM

**FSM（Free Space Map）**：记录每个 page 的可用空间

```sql
SELECT * FROM pg_freespace('users');
-- page | free_bytes
-- 0    | 4096
-- 1    | 1024
-- ...
```

**VM（Visibility Map）**：记录哪些 page 的所有 tuple 都被 vacuum 过（对所有人可见）

```sql
SELECT * FROM pg_visibility('users');
```

## FILLFACTOR（页填充因子）

```sql
-- 默认 100（页填满）
ALTER TABLE users SET (fillfactor = 70);
-- 留 30% 空间给 UPDATE（防止页分裂）
```

**适用**：频繁 UPDATE 的字段。

## 实战案例

### 案例：减少 TOAST

```sql
-- 问题：日志表 content TEXT 经常超 2KB，频繁 TOAST 压缩

-- 1. 看 TOAST 占用
SELECT
  pg_size_pretty(pg_relation_size('articles')) AS main,
  pg_size_pretty(pg_relation_size('articles', 'toast')) AS toast,
  pg_size_pretty(pg_total_relation_size('articles')) AS total
FROM pg_class WHERE relname = 'articles';

-- 2. 设置不同的存储策略
ALTER TABLE articles ALTER COLUMN content SET STORAGE MAIN;
-- 只压缩不外存（小数据场景）
```

### 案例：表膨胀诊断

```sql
-- 用 pgstattuple 看 bloat
CREATE EXTENSION pgstattuple;

SELECT * FROM pgstattuple('users');
-- tuple_count | dead_tuple_count | free_space | free_percent
-- 100000      | 50000            | 30MB       | 30%

-- 30% 浪费 = 需要 vacuum 或 pg_repack
```

## 一句话总结

> **PG 表 = Heap + FSM + VM + TOAST**。**Heap 按 8KB page 组织**、**TOAST 自动外存超长字段**、**FSM 追踪可用空间**、**VM 加速 vacuum**。**fillfactor 留空间减少 UPDATE 页分裂**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "04-query/fulltext-search.md": """---
title: 全文检索
description: tsvector / tsquery / GIN
---

# 全文检索

> **TL;DR**：PG 全文检索 = `tsvector`（文档向量）+ `tsquery`（查询）+ `@@` 操作符。**配 GIN 索引后搜索性能从 5s 降到 5ms**，是 PG 中文/英文搜索的标配。

## 一句话定义

```
全文检索 = 把文本拆成词（token）+ 归一化（小写、词干化）+ 建倒排索引
         = 用 GIN 索引 + tsvector + tsquery
```

## 基础使用

### tsvector

```sql
-- 把文本转成文档向量
SELECT to_tsvector('english', 'The quick brown fox jumps over the lazy dog');
-- 'brown':3 'dog':9 'fox':4 'jump':5 'lazy':7 'quick':2

-- 位置：词在原文中的位置
```

### tsquery

```sql
-- 查询表达式
SELECT to_tsquery('english', 'fox & dog');      -- AND
SELECT to_tsquery('english', 'fox | dog');      -- OR
SELECT to_tsquery('english', '!fox');           -- NOT
SELECT to_tsquery('english', 'fox <-> dog');    -- 相邻
```

### @@ 操作符

```sql
-- 文档匹配查询
SELECT to_tsvector('english', 'The fox is quick') 
  @@ to_tsquery('english', 'fox');
-- true

-- 否定
SELECT to_tsvector('english', 'The fox is quick') 
  @@ to_tsquery('english', '!fox');
-- false
```

## 表 + 全文索引

```sql
-- 1. 表 + tsvector 列
CREATE TABLE articles (
  id BIGSERIAL PRIMARY KEY,
  title TEXT,
  body TEXT,
  tsv tsvector
);

-- 2. 填充 tsvector
INSERT INTO articles (title, body, tsv) VALUES
  ('PostgreSQL Intro', 'PostgreSQL is a powerful database', 
   to_tsvector('english', 'PostgreSQL Intro PostgreSQL is a powerful database'));

-- 3. GIN 索引
CREATE INDEX idx_articles_tsv ON articles USING GIN (tsv);

-- 4. 全文查询
SELECT * FROM articles
WHERE tsv @@ to_tsquery('english', 'postgres & powerful');
```

## 自动更新 tsvector（触发器）

```sql
-- 1. 创建函数
CREATE FUNCTION articles_tsv_update() RETURNS TRIGGER AS $$
BEGIN
  NEW.tsv :=
    setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.body, '')), 'B');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. 触发器
CREATE TRIGGER trg_articles_tsv
BEFORE INSERT OR UPDATE ON articles
FOR EACH ROW EXECUTE FUNCTION articles_tsv_update();
```

## 权重 + 排序

```sql
-- 权重：A (title) > B (body)
SELECT title, ts_rank(tsv, to_tsquery('postgres')) AS rank
FROM articles
WHERE tsv @@ to_tsquery('postgres')
ORDER BY rank DESC
LIMIT 10;
```

## 中文检索

```sql
-- 1. 安装 zhparser
CREATE EXTENSION zhparser;

-- 2. 创建文本搜索配置
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR n,v,a,i,e,l,t WITH simple;

-- 3. 用
SELECT to_tsvector('chinese', 'PostgreSQL 是一个强大的数据库');
```

或者用 `pg_jieba`（基于结巴分词）：

```sql
CREATE EXTENSION pg_jieba;
SELECT to_tsvector('jiebacfg', 'PostgreSQL 是一个强大的数据库');
```

## 高亮

```sql
SELECT
  ts_headline('english', body, to_tsquery('postgres & powerful'),
    'MaxFragments=2, MaxWords=20, MinWords=5') AS headline
FROM articles
WHERE tsv @@ to_tsquery('postgres & powerful');
```

## 实战案例

### 案例 1：电商商品搜索

```sql
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  description TEXT,
  search tsvector
);

CREATE INDEX idx_products_search ON products USING GIN (search);

CREATE TRIGGER trg_products_search
BEFORE INSERT OR UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(search, 'public.english_ngram', name, description);

-- 搜索 "iPhone 15"
SELECT *, ts_rank(search, to_tsquery('iPhone 15')) AS rank
FROM products
WHERE search @@ to_tsquery('iPhone 15')
ORDER BY rank DESC
LIMIT 20;
```

### 案例 2：博客文章搜索

```sql
-- A/B/C/D 权重：title (A) / subtitle (B) / body (C) / tag (D)
CREATE FUNCTION posts_tsv_update() RETURNS TRIGGER AS $$
BEGIN
  NEW.search :=
    setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.body, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(array_to_string(NEW.tags, ' '), '')), 'C');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

## 一句话总结

> **PG 全文检索 = tsvector + GIN 索引**。**英文用内置词典**，**中文用 zhparser / pg_jieba**。**配合 ts_rank 排序 + ts_headline 高亮**就是一套完整搜索引擎，**5 行代码**搞定。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "04-query/planner.md": """---
title: 查询规划器
description: EXPLAIN 解读与优化
---

# 查询规划器

> **TL;DR**：PG planner 用 **基于成本的优化器（CBO）**，根据统计信息选最优执行计划。**EXPLAIN** 是解读 plan 的核心工具。

## 一句话定义

```
查询规划器 = 把 SQL 解析 + 优化成最优执行计划
           = 基于成本（cost-based optimization）
           = 输入：SQL + 统计信息
           = 输出：执行计划（Plan Tree）
```

## EXPLAIN 基本使用

```sql
-- 只看计划（不执行）
EXPLAIN SELECT * FROM users WHERE id = 1;

-- 真实执行 + 统计
EXPLAIN ANALYZE SELECT * FROM users WHERE id = 1;

-- 含缓冲命中
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM users WHERE id = 1;
```

## 读取 EXPLAIN 输出

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = '[email protected]';

-- Index Scan using idx_users_email on users
--   (cost=0.42..8.44 rows=1 width=100) (actual time=0.05..0.06 rows=1 loops=1)
--   Index Cond: (email = '[email protected]')
--   Buffers: shared hit=4
-- Planning Time: 0.15 ms
-- Execution Time: 0.08 ms
```

**字段解读**：

| 字段 | 含义 |
|---|---|
| `cost=X..Y` | 估算成本（X = 启动成本，Y = 总成本） |
| `rows=N` | 估算返回行数 |
| `width=N` | 每行平均字节数 |
| `actual time=X..Y` | 真实耗时（ms） |
| `actual rows=N` | 真实返回行数 |
| `loops=N` | 这个节点执行次数 |
| `Buffers: shared hit=N read=M` | 缓存命中 / 磁盘读 |

## 扫描类型

| 节点 | 含义 | 何时使用 |
|---|---|---|
| `Seq Scan` | 全表扫描 | 无索引 / 大量数据 |
| `Index Scan` | 索引扫描 | 等值 + 范围 |
| `Index Only Scan` | 仅索引扫描 | 索引覆盖所有列 |
| `Bitmap Index Scan` | 位图索引扫描 | 多条件 OR |
| `Bitmap Heap Scan` | 位图堆扫描 | Bitmap Index 的下一步 |

```sql
-- ❌ 全表扫描
EXPLAIN SELECT * FROM users WHERE name LIKE '%alice%';
-- Seq Scan on users (cost=0..1500 rows=10) (actual rows=0)
--   Filter: (name ~~ '%alice%')

-- ✓ 索引扫描
EXPLAIN SELECT * FROM users WHERE email = '[email protected]';
-- Index Scan using idx_users_email on users
--   Index Cond: (email = '[email protected]')
```

## JOIN 类型

| 节点 | 含义 | 何时使用 |
|---|---|---|
| `Nested Loop` | 嵌套循环 | 小数据集 / 索引 JOIN |
| `Hash Join` | 哈希连接 | 等值 JOIN，大表 |
| `Merge Join` | 合并连接 | 已排序的大表 JOIN |

```sql
EXPLAIN SELECT * FROM users u
JOIN orders o ON u.id = o.user_id;

-- Hash Join (cost=... rows=...)
--   Hash Cond: (o.user_id = u.id)
--   -> Seq Scan on orders o
--   -> Hash
--        -> Seq Scan on users u
```

## 统计信息

```sql
-- 1. 手动收集
ANALYZE users;

-- 2. 自动收集
-- autovacuum_analyze_scale_factor = 0.1（10% 行变化触发）

-- 3. 看统计信息
SELECT * FROM pg_stats WHERE tablename = 'users';
-- 显示每列的 distinct 值、最常见值、直方图等
```

## 成本因子

```ini
# postgresql.conf

# 影响 planner 决策
seq_page_cost = 1.0            # 顺序扫描单页成本（默认）
random_page_cost = 4.0          # 随机扫描单页成本（默认）
# SSD 推荐 random_page_cost = 1.1

cpu_tuple_cost = 0.01          # 每行处理成本
cpu_index_tuple_cost = 0.005    # 每行索引处理成本
cpu_operator_cost = 0.0025     # 每操作符成本

effective_io_concurrency = 1   # 并发 IO（SSD 推荐 200）
```

## 优化技巧

### 1. 让 planner 选索引

```sql
-- ❌ 表达式包裹让索引失效
WHERE date(created_at) = '2026-08-09'

-- ✅ 等价但能用索引
WHERE created_at >= '2026-08-09' AND created_at < '2026-08-10'
```

### 2. 收集最新统计信息

```sql
-- 大量 INSERT 后
ANALYZE VERBOSE users;

-- 看是否最新
SELECT last_analyze, last_autoanalyze FROM pg_stat_user_tables WHERE relname = 'users';
```

### 3. 强制 JOIN 顺序

```sql
-- 小表驱动大表
SELECT /*+ Leading(small large) */ *
FROM small s
JOIN large l ON s.id = l.small_id;

-- 或 SET
SET join_collapse_limit = 1;
-- planner 会按 SQL 顺序 JOIN
```

### 4. 关闭某些优化

```sql
-- 关闭 Nested Loop
SET enable_nestloop = off;

-- 关闭 Hash Join
SET enable_hashjoin = off;

-- 关闭 Merge Join
SET enable_mergejoin = off;
```

## 一句话总结

> **EXPLAIN ANALYZE 是 DBA 第一工具**：**看扫描类型、JOIN 类型、cost 估算、actual 实际**。**Seq Scan + 大表 = 加索引**。**随机 IO 慢 → random_page_cost 调到 1.1（SSD）**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "04-query/recursive.md": """---
title: 递归 CTE
description: WITH RECURSIVE 实战
---

# 递归 CTE

> **TL;DR**：`WITH RECURSIVE` 是 PG 实现**树形 / 图遍历**的杀手锏。**组织架构、菜单、评论、文件系统、社交关系**全靠它。

## 一句话定义

```
递归 CTE = 基础查询 + 递归部分 UNION ALL
        = 一行行迭代
        = 直到无新行为止
```

## 基本语法

```sql
WITH RECURSIVE cte_name AS (
  -- 非递归部分（基础查询）
  initial_query
  
  UNION ALL  -- 或 UNION
  
  -- 递归部分（引用 cte_name）
  recursive_query
)
SELECT * FROM cte_name;
```

## 案例 1：组织架构树

```sql
-- 数据：employees(id, name, manager_id)
-- 1 (CEO)
-- ├── 2 (CTO, manager=1)
-- │   ├── 4 (Dev1, manager=2)
-- │   └── 5 (Dev2, manager=2)
-- └── 3 (CFO, manager=1)

-- 查 1 的所有下属（无限层）
WITH RECURSIVE subordinates AS (
  -- 基础：CEO
  SELECT id, name, manager_id, 1 AS depth
  FROM employees WHERE id = 1
  
  UNION ALL
  
  -- 递归：subordinates 的下属
  SELECT e.id, e.name, e.manager_id, s.depth + 1
  FROM employees e
  JOIN subordinates s ON e.manager_id = s.id
)
SELECT * FROM subordinates ORDER BY depth, id;
```

## 案例 2：菜单树

```sql
-- 数据：menu_items(id, name, parent_id)
-- 1 (首页)
-- ├── 2 (产品, parent=1)
-- │   ├── 4 (产品A, parent=2)
-- │   └── 5 (产品B, parent=2)
-- └── 3 (关于, parent=1)

WITH RECURSIVE menu AS (
  SELECT id, name, parent_id, 0 AS level, 
         ARRAY[id] AS path
  FROM menu_items WHERE parent_id IS NULL
  
  UNION ALL
  
  SELECT m.id, m.name, m.parent_id, menu.level + 1,
         menu.path || m.id
  FROM menu_items m
  JOIN menu ON m.parent_id = menu.id
)
SELECT * FROM menu;
-- 包含每个节点的层级 + 路径
```

## 案例 3：评论树

```sql
-- 数据：comments(id, content, parent_id, created_at)
WITH RECURSIVE comment_tree AS (
  SELECT id, content, parent_id, created_at, 0 AS depth
  FROM comments WHERE id = 100  -- 根评论
  
  UNION ALL
  
  SELECT c.id, c.content, c.parent_id, c.created_at, t.depth + 1
  FROM comments c
  JOIN comment_tree t ON c.parent_id = t.id
)
SELECT * FROM comment_tree ORDER BY depth, created_at;
```

## 案例 4：图遍历（最短路径）

```sql
-- 数据：edges(from_node, to_node, weight)
-- A -> B (5), B -> C (3), A -> C (10)

WITH RECURSIVE paths(node, total_cost, path) AS (
  -- 起点
  SELECT 'A', 0, ARRAY['A']
  
  UNION ALL
  
  SELECT e.to_node, p.total_cost + e.weight, p.path || e.to_node
  FROM paths p
  JOIN edges e ON e.from_node = p.node
  WHERE NOT (e.to_node = ANY(p.path))  -- 防环
)
SELECT * FROM paths WHERE node = 'C' ORDER BY total_cost LIMIT 1;
-- A -> B -> C (cost=8) < A -> C (cost=10)
```

## 案例 5：JSON 树遍历

```sql
-- 嵌套 JSON 找所有叶子节点
WITH RECURSIVE json_tree AS (
  SELECT 
    '{"a": {"b": 1, "c": {"d": 2}}}'::jsonb AS data,
    ARRAY[]::text[] AS path
  
  UNION ALL
  
  SELECT 
    jsonb_path_query(data, '$.*'),
    path || (key)
  FROM json_tree, jsonb_object_keys(data) AS key
)
SELECT * FROM json_tree;
```

## 防止无限循环

```sql
-- 方法 1：路径数组
WITH RECURSIVE ... AS (
  ...
  UNION ALL
  ...
  -- 检查是否已在路径中
  WHERE NOT (new_node = ANY(path))
)

-- 方法 2：CYCLE 子句（PG 14+）
WITH RECURSIVE ... CYCLE node SET is_cycle USING path
```

## 性能优化

```sql
-- 1. 限制递归深度（防意外无限循环）
WITH RECURSIVE ... AS (
  ...
  UNION ALL
  ...
  WHERE depth < 100  -- 限制 100 层
)

-- 2. 物化递归 CTE（PG 12+）
WITH RECURSIVE ... AS MATERIALIZED (
  ...
)
SELECT ... FROM ...
-- 同名 CTE 只计算一次
```

## 实战案例

### 案例：员工所有下属（含层级路径）

```sql
WITH RECURSIVE emp_tree AS (
  SELECT id, name, manager_id, 0 AS level,
         ARRAY[name]::text[] AS path
  FROM employees WHERE id = 1
  
  UNION ALL
  
  SELECT e.id, e.name, e.manager_id, t.level + 1,
         t.path || e.name
  FROM employees e
  JOIN emp_tree t ON e.manager_id = t.id
  WHERE t.level < 10  -- 防 10 层以上
)
SELECT 
  level,
  repeat('  ', level) || name AS indented_name,
  array_to_string(path, ' → ') AS full_path
FROM emp_tree ORDER BY level, name;
```

## 一句话总结

> **递归 CTE = PG 处理树和图的标准方案**。**组织架构、菜单、评论、文件树、社交网络**全靠它。**关键三段**：**基础查询 + 递归查询 + 终止条件（CYCLE 或 path 检查）**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "05-transaction/deadlock.md": """---
title: 死锁排查
description: deadlock_detected 错误处理
---

# 死锁排查

> **TL;DR**：PG 自动检测死锁 + 回滚较小事务。**应用层需要 retry**。**避免策略**：固定锁顺序、缩短事务、行锁替代表锁。

## 一句话定义

```
死锁 = 两个事务互相等待对方释放锁
     = PG 自动检测
     = 自动回滚代价较小的事务
     = 应用层需要 retry
```

## 死锁检测

```
PG 启动后每 1s 检查一次 wait_queue
如果发现循环依赖 → 选代价小的事务回滚 → 另一事务继续执行
```

## 错误码

```sql
-- 死锁错误
ERROR: deadlock detected
DETAIL: Process 1234 waits for ShareLock on transaction 5678; blocked by process 5678.
HINT: See server log for query details.
CONTEXT: SQL statement "..."
SQLSTATE: 40P01
```

## 应用层 Retry

```java
@Transactional
public void transfer(Long fromId, Long toId, BigDecimal amount) {
    int maxRetries = 3;
    for (int attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            // 业务代码
            accountDao.updateBalance(fromId, amount.negate());
            accountDao.updateBalance(toId, amount);
            return;  // 成功
        } catch (DataAccessException e) {
            if (isDeadlock(e) && attempt < maxRetries) {
                Thread.sleep(50L * attempt);  // 指数 backoff
                continue;  // 重试
            }
            throw e;
        }
    }
}

private boolean isDeadlock(Exception e) {
    return e.getMessage().contains("deadlock detected") 
        || (e.getCause() instanceof SQLException 
            && "40P01".equals(((SQLException) e.getCause()).getSQLState()));
}
```

## 排查死锁

### 启用详细日志

```ini
# postgresql.conf
log_lock_waits = on          # 记录所有锁等待
deadlock_timeout = '1s'      # 死锁检测间隔（默认 1s）
```

### 看死锁日志

```
ERROR:  deadlock detected at 2026-08-09 10:00:00
DETAIL: Process 1234 waits for ShareLock on transaction 5678; 
        blocked by process 5678.
        Process 5678 waits for ShareLock on transaction 1234; 
        blocked by process 1234.
HINT:   See server log for query details.
QUERY:  UPDATE accounts SET balance = balance - 100 WHERE id = 1
```

### pg_stat_activity 查锁等待

```sql
SELECT
  blocked.pid AS blocked_pid,
  blocking.pid AS blocking_pid,
  now() - blocked.query_start AS blocked_duration,
  blocked.query AS blocked_query,
  blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid
JOIN pg_locks kl ON kl.locktype = bl.locktype
  AND kl.pid != bl.pid
  AND kl.granted
  AND kl.relation IS NOT DISTINCT FROM bl.relation
  AND kl.tuple IS NOT DISTINCT FROM bl.tuple
JOIN pg_stat_activity blocking ON blocking.pid = kl.pid
WHERE NOT bl.granted;
```

## 避免死锁的 4 个原则

### 1. 固定锁顺序

```java
// ❌ 错误：顺序不一致
void transfer(Long a, Long b, BigDecimal amount) {
    accountDao.updateBalance(a, amount.negate());  // 先 a
    accountDao.updateBalance(b, amount);          // 后 b
}

// A 转 B 顺序：a, b
// B 转 A 顺序：b, a
// 可能死锁

// ✅ 修复：固定按 id 升序
void transfer(Long a, Long b, BigDecimal amount) {
    Long first = Math.min(a, b);
    Long second = Math.max(a, b);
    accountDao.updateBalance(first, ...);  // 小 id 先
    accountDao.updateBalance(second, ...); // 大 id 后
}
```

### 2. 缩短事务

```java
// ❌ 错误：长事务
@Transactional
public void processOrder(Order order) {
    // 业务逻辑
    orderDao.save(order);
    paymentService.charge(order);  // ← HTTP 调用，10s+
    inventoryService.reduce(order); // ← 又一个 HTTP 调用
    notificationService.send(order); // ← 又一个
}

// ✅ 修复：事务只做 DB 操作
public void processOrder(Order order) {
    saveOrder(order);  // 短事务
    // 事务外做副作用
    asyncExecutor.submit(() -> {
        paymentService.charge(order);
        // ...
    });
}
```

### 3. 行锁替代表锁

```sql
-- ❌ 表锁
LOCK TABLE users IN EXCLUSIVE MODE;

-- ✅ 行锁
SELECT * FROM users WHERE id = 1 FOR UPDATE;
```

### 4. 监控长事务

```ini
# postgresql.conf
idle_in_transaction_session_timeout = '60s'
statement_timeout = '30s'
```

## 实战案例

### 案例 1：转账并发死锁

**场景**：用户 A → B 和 B → A 同时转账

**修复**：

```java
// 固定顺序：先小 id
@Transactional
public void transfer(Long fromId, Long toId, BigDecimal amount) {
    if (fromId > toId) {
        // 调换顺序
        Long tmp = fromId; fromId = toId; toId = tmp;
        amount = amount.negate();
    }
    accountDao.updateBalance(fromId, amount.negate());
    accountDao.updateBalance(toId, amount);
}
```

### 案例 2：批量更新死锁

**场景**：批量 UPDATE 同一表的不同行

**修复**：分批 + SKIP LOCKED

```sql
DO $$
DECLARE
  affected INT;
BEGIN
  LOOP
    UPDATE large_table
    SET status = 'processed'
    WHERE id IN (
      SELECT id FROM large_table
      WHERE status = 'pending'
      LIMIT 1000
      FOR UPDATE SKIP LOCKED
    );
    GET DIAGNOSTICS affected = ROW_COUNT;
    EXIT WHEN affected = 0;
    COMMIT;
    PERFORM pg_sleep(0.1);
  END LOOP;
END $$;
```

## 一句话总结

> **死锁 = 必然会发生，应用必须 retry**。**避免策略**：**固定锁顺序 + 缩短事务 + 行锁替代表锁 + 监控长事务**。**PG 1s 检测一次** + 自动回滚较小事务 + SQLSTATE `40P01`。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "06-advanced/function.md": """---
title: 函数与过程
description: PL/pgSQL 编程
---

# 函数与过程

> **TL;DR**：PG 函数 = SQL 块 + 流程控制 + 变量。**PL/pgSQL** 是默认语言，**SQL 函数**纯函数式，**PL/Python** 等支持多语言。**触发器、批量处理、业务封装**全靠函数。

## 一句话定义

```
函数 (FUNCTION)  = 返回值，可能无副作用
过程 (PROCEDURE) = 无返回值，可有事务控制（PG 11+）
```

## SQL 函数（最纯）

```sql
-- 1. 简单函数
CREATE FUNCTION add(a INT, b INT) RETURNS INT AS $$
  SELECT a + b;
$$ LANGUAGE SQL IMMUTABLE;

-- 2. 调用
SELECT add(1, 2);  -- 3

-- 3. 表函数（返回 SETOF）
CREATE FUNCTION get_active_users() RETURNS SETOF users AS $$
  SELECT * FROM users WHERE is_active = true;
$$ LANGUAGE SQL;

-- 4. 调用
SELECT * FROM get_active_users();
```

**属性**：

| 属性 | 含义 |
|---|---|
| `IMMUTABLE` | 相同输入永远相同输出 |
| `STABLE` | 同一事务内不变 |
| `VOLATILE` | 每次调用可能不同（默认） |

> **IMMUTABLE 函数可以参与表达式索引**。

## PL/pgSQL 函数

```sql
-- 1. 基本函数
CREATE FUNCTION greet(name TEXT) RETURNS TEXT AS $$
DECLARE
  greeting TEXT;
BEGIN
  greeting := 'Hello, ' || name || '!';
  RETURN greeting;
END;
$$ LANGUAGE plpgsql;

-- 2. 调用
SELECT greet('Alice');  -- 'Hello, Alice!'
```

### 变量与流程

```sql
CREATE FUNCTION analyze_user(user_id BIGINT) RETURNS TEXT AS $$
DECLARE
  user_record users%ROWTYPE;
  status TEXT;
BEGIN
  -- 1. 变量赋值
  SELECT * INTO user_record FROM users WHERE id = user_id;
  
  IF NOT FOUND THEN
    RETURN 'User not found';
  END IF;
  
  -- 2. 条件分支
  IF user_record.age >= 18 THEN
    status := 'adult';
  ELSIF user_record.age >= 13 THEN
    status := 'teen';
  ELSE
    status := 'child';
  END IF;
  
  -- 3. 循环
  FOR i IN 1..10 LOOP
    RAISE NOTICE 'Iteration %', i;
  END LOOP;
  
  RETURN status;
END;
$$ LANGUAGE plpgsql;
```

### 异常处理

```sql
CREATE FUNCTION safe_divide(a INT, b INT) RETURNS NUMERIC AS $$
DECLARE
  result NUMERIC;
BEGIN
  result := a::NUMERIC / b;
  RETURN result;
EXCEPTION
  WHEN division_by_zero THEN
    RAISE NOTICE 'Division by zero';
    RETURN NULL;
  WHEN OTHERS THEN
    RAISE EXCEPTION 'Unknown error: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
```

### 游标

```sql
CREATE FUNCTION process_users() RETURNS INT AS $$
DECLARE
  user_rec RECORD;
  total INT := 0;
BEGIN
  FOR user_rec IN SELECT * FROM users WHERE is_active LOOP
    UPDATE orders SET status = 'reviewed' WHERE user_id = user_rec.id;
    total := total + 1;
  END LOOP;
  RETURN total;
END;
$$ LANGUAGE plpgsql;
```

### OUT / INOUT 参数

```sql
CREATE FUNCTION get_user_stats(
  IN user_id BIGINT,
  OUT total_orders INT,
  OUT total_spent NUMERIC
) AS $$
BEGIN
  SELECT count(*), coalesce(sum(amount), 0)
  INTO total_orders, total_spent
  FROM orders WHERE user_id = get_user_stats.user_id;
END;
$$ LANGUAGE plpgsql;

-- 调用（返回 RECORD）
SELECT * FROM get_user_stats(123);
```

## 过程（PROCEDURE）

**PG 11+ 支持事务控制**：

```sql
CREATE PROCEDURE transfer_money(
  from_account BIGINT,
  to_account BIGINT,
  amount NUMERIC
) AS $$
BEGIN
  UPDATE accounts SET balance = balance - amount WHERE id = from_account;
  UPDATE accounts SET balance = balance + amount WHERE id = to_account;
  
  COMMIT;  -- 过程内可以事务控制（函数不行）
END;
$$ LANGUAGE plpgsql;

-- 调用
CALL transfer_money(1, 2, 100);
```

## 多语言函数

### PL/Python

```sql
-- 1. 安装扩展
CREATE EXTENSION plpython3u;

-- 2. 创建函数
CREATE FUNCTION py_upper(text) RETURNS TEXT AS $$
  return args[0].upper()
$$ LANGUAGE plpython3u;

SELECT py_upper('hello');  -- 'HELLO'
```

### PL/Perl

```sql
CREATE EXTENSION plperlu;
CREATE FUNCTION perl_func() RETURNS TEXT AS $$
  return "Perl says hi";
$$ LANGUAGE plperlu;
```

## 函数管理

```sql
-- 1. 查看函数
\df                 -- psql 命令
SELECT * FROM pg_proc WHERE proname = 'add';

-- 2. 修改函数
ALTER FUNCTION add(INT, INT) IMMUTABLE;

-- 3. 删除
DROP FUNCTION add(INT, INT);

-- 4. 函数权限
GRANT EXECUTE ON FUNCTION add(INT, INT) TO app_user;
```

## 实战案例

### 案例 1：触发器函数

```sql
CREATE FUNCTION update_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```

### 案例 2：批量处理函数

```sql
CREATE FUNCTION archive_old_logs(days INT) RETURNS INT AS $$
DECLARE
  cutoff TIMESTAMPTZ := now() - (days || ' days')::INTERVAL;
  deleted INT;
BEGIN
  DELETE FROM logs WHERE created_at < cutoff;
  GET DIAGNOSTICS deleted = ROW_COUNT;
  RETURN deleted;
END;
$$ LANGUAGE plpgsql;

-- 调用
SELECT archive_old_logs(30);  -- 删除 30 天前的日志
```

## 一句话总结

> **PG 函数 = SQL + 流程控制**：**SQL 函数（纯）+ PL/pgSQL（带逻辑）+ 过程（带事务控制）**。**触发器、批量处理、业务封装**都靠函数。**90% 场景用 PL/pgSQL 就够了**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "06-advanced/generated.md": """---
title: Generated 列
description: PG 12+ 计算列
---

# Generated 列

> **TL;DR**：PG 12+ 支持 **GENERATED 列**，自动从其他列计算。**类似 MySQL Generated Column + Oracle 虚列**，但 PG 是 STORED（物理存储）。

## 一句话定义

```
Generated 列 = 表内自动计算列
            = INSERT/UPDATE 时自动更新
            = 可建索引、可直接查
```

## 两种模式

| 模式 | 存储 | 性能 |
|---|---|---|
| `STORED` | 物理存储 | 读快，写稍慢 |
| `VIRTUAL` (PG 18+) | 不存储 | 写快，读时算 |

> **PG 12-17：只有 STORED**。**PG 18+：新增 VIRTUAL**。

## 基本使用

```sql
-- 创建表
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  quantity INT NOT NULL,
  unit_price NUMERIC(10,2) NOT NULL,
  -- Generated 列
  total NUMERIC(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- 插入
INSERT INTO orders (quantity, unit_price) VALUES (3, 99.50);
-- total 自动 = 297.50

-- 查询
SELECT * FROM orders;
-- id | quantity | unit_price | total
-- 1  | 3        | 99.50      | 297.50
```

## 实战案例

### 案例 1：自动金额计算

```sql
CREATE TABLE order_items (
  id BIGSERIAL PRIMARY KEY,
  product_id BIGINT NOT NULL,
  quantity INT NOT NULL CHECK (quantity > 0),
  unit_price NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
  discount NUMERIC(3,2) DEFAULT 0,
  -- Generated：折后总价
  subtotal NUMERIC(10,2) GENERATED ALWAYS AS (
    quantity * unit_price * (1 - discount)
  ) STORED,
  -- Generated：完整字段
  full_label TEXT GENERATED ALWAYS AS (
    product_id::text || ' x ' || quantity::text
  ) STORED
);

-- 索引
CREATE INDEX idx_order_items_subtotal ON order_items (subtotal);
```

### 案例 2：自动拼接全名

```sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  first_name TEXT,
  middle_name TEXT,
  last_name TEXT,
  full_name TEXT GENERATED ALWAYS AS (
    trim(both ' ' from 
      coalesce(first_name, '') || ' ' || 
      coalesce(middle_name, '') || ' ' || 
      coalesce(last_name, '')
    )
  ) STORED
);

-- 插入
INSERT INTO users (first_name, middle_name, last_name) 
VALUES ('张', '三', '丰');
-- full_name 自动 = '张 三 丰'
```

### 案例 3：JSONB 自动字段

```sql
CREATE TABLE events (
  id BIGSERIAL PRIMARY KEY,
  data JSONB NOT NULL,
  -- 从 JSONB 提取
  event_type TEXT GENERATED ALWAYS AS (data->>'type') STORED,
  user_id BIGINT GENERATED ALWAYS AS ((data->>'user_id')::BIGINT) STORED,
  event_ts TIMESTAMPTZ GENERATED ALWAYS AS ((data->>'ts')::TIMESTAMPTZ) STORED
);

CREATE INDEX idx_events_type ON events (event_type);
CREATE INDEX idx_events_user ON events (user_id);
```

## 与视图 / 触发器的对比

```sql
-- 1. 视图（每次查询重算）
CREATE VIEW order_view AS
SELECT id, quantity * unit_price AS total FROM orders;
-- 性能差，不占存储

-- 2. 触发器（写入时算）
CREATE FUNCTION calc_total() RETURNS TRIGGER AS $$
BEGIN
  NEW.total := NEW.quantity * NEW.unit_price;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_orders_total
BEFORE INSERT OR UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION calc_total();
-- 灵活，但手写麻烦

-- 3. Generated 列（推荐）
total NUMERIC GENERATED ALWAYS AS (quantity * unit_price) STORED;
-- 自动、简单、有索引
```

## 限制

```sql
-- ❌ 不能引用其他 Generated 列
CREATE TABLE t (
  a INT,
  b INT GENERATED ALWAYS AS (a * 2) STORED,
  c INT GENERATED ALWAYS AS (b + 1) STORED  -- 报错
);

-- ✅ 必须直接引用基础列
CREATE TABLE t (
  a INT,
  b INT GENERATED ALWAYS AS (a * 2) STORED,
  c INT GENERATED ALWAYS AS (a * 2 + 1) STORED  -- OK
);

-- ❌ 不能用子查询
GENERATED ALWAYS AS ((SELECT max(id) FROM other_table)) STORED  -- 报错

-- ❌ 不能用 volatile 函数
GENERATED ALWAYS AS (random()) STORED  -- 报错
```

## 一句话总结

> **Generated 列 = 物理存储的计算列**：**自动维护、可建索引、读写都好**。**PG 12+ STORED / PG 18+ 新增 VIRTUAL**。**金额、拼接、JSONB 提取字段**都是典型场景。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "06-advanced/trigger.md": """---
title: 触发器
description: BEFORE / AFTER / INSTEAD OF 触发器实战
---

# 触发器

> **TL;DR**：PG 触发器 = **表/视图上自动执行的函数**。**审计日志、自动时间戳、跨表一致性、复杂校验**全靠它。**PG 9+ 支持每语句触发 + 每行触发**。

## 一句话定义

```
触发器 = 表/视图上的"事件钩子"
       = INSERT/UPDATE/DELETE 时自动执行函数
       = BEFORE（修改前）/ AFTER（修改后）/ INSTEAD OF（替代）
```

## 触发器分类

| 维度 | 选项 |
|---|---|
| **时机** | BEFORE / AFTER / INSTEAD OF |
| **范围** | FOR EACH ROW / FOR EACH STATEMENT |
| **事件** | INSERT / UPDATE / DELETE / TRUNCATE |
| **条件** | WHEN（条件触发） |

## 触发器函数

```sql
-- 1. 函数签名
CREATE FUNCTION trg_func() RETURNS TRIGGER AS $$
BEGIN
  -- TG_OP = 'INSERT' / 'UPDATE' / 'DELETE' / 'TRUNCATE'
  -- TG_TABLE_NAME = 表名
  -- NEW.column / OLD.column
  RETURN NEW;  -- INSERT/UPDATE 必须返回 NEW
  -- RETURN OLD;  -- DELETE 必须返回 OLD
  -- RETURN NULL; -- BEFORE + 行触发：跳过本次操作
END;
$$ LANGUAGE plpgsql;

-- 2. 绑定到表
CREATE TRIGGER trg_users_insert
BEFORE INSERT ON users
FOR EACH ROW EXECUTE FUNCTION trg_func();
```

## 实战案例

### 案例 1：自动时间戳

```sql
CREATE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

### 案例 2：审计日志

```sql
CREATE TABLE users_audit (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT,
  operation TEXT,
  old_data JSONB,
  new_data JSONB,
  changed_by TEXT,
  changed_at TIMESTAMPTZ DEFAULT now()
);

CREATE FUNCTION audit_users() RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    INSERT INTO users_audit (user_id, operation, new_data, changed_by)
    VALUES (NEW.id, 'INSERT', to_jsonb(NEW), current_user);
    RETURN NEW;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO users_audit (user_id, operation, old_data, new_data, changed_by)
    VALUES (NEW.id, 'UPDATE', to_jsonb(OLD), to_jsonb(NEW), current_user);
    RETURN NEW;
  ELSIF TG_OP = 'DELETE' THEN
    INSERT INTO users_audit (user_id, operation, old_data, changed_by)
    VALUES (OLD.id, 'DELETE', to_jsonb(OLD), current_user);
    RETURN OLD;
  END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_audit
AFTER INSERT OR UPDATE OR DELETE ON users
FOR EACH ROW EXECUTE FUNCTION audit_users();
```

### 案例 3：软删除

```sql
CREATE FUNCTION soft_delete() RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    UPDATE users SET deleted_at = now() WHERE id = OLD.id;
    RETURN NULL;  -- 阻止真删除
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_soft_delete
BEFORE DELETE ON users
FOR EACH ROW EXECUTE FUNCTION soft_delete();
```

### 案例 4：跨表一致性

```sql
-- 订单表 + 订单日志表
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  status TEXT,
  total NUMERIC
);

CREATE TABLE order_logs (
  id BIGSERIAL PRIMARY KEY,
  order_id BIGINT,
  status TEXT,
  changed_at TIMESTAMPTZ DEFAULT now()
);

CREATE FUNCTION log_order_status() RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status != OLD.status THEN
    INSERT INTO order_logs (order_id, status)
    VALUES (NEW.id, NEW.status);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_orders_status_change
AFTER UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION log_order_status();
```

## INSTEAD OF 触发器（视图）

```sql
-- 1. 创建视图
CREATE VIEW users_view AS
SELECT id, name, email FROM users;

-- 2. 视图不能直接 INSERT，需要 INSTEAD OF
CREATE FUNCTION insert_user_view() RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO users (id, name, email) 
  VALUES (NEW.id, NEW.name, NEW.email);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_view_insert
INSTEAD OF INSERT ON users_view
FOR EACH ROW EXECUTE FUNCTION insert_user_view();

-- 3. 现在可以
INSERT INTO users_view (id, name, email) VALUES (1, 'Alice', '[email protected]');
```

## WHEN 条件触发

```sql
-- 只在 status 变化时触发
CREATE TRIGGER trg_orders_status_change
AFTER UPDATE ON orders
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION log_order_status();
```

> **优化**：WHEN 条件让触发器只在必要时执行，**减少 50%+ 触发次数**。

## 触发器性能

```
BEFORE 触发器 = 修改 NEW（数据预处理）
AFTER 触发器 = 审计 / 跨表一致性
INSTEAD OF  = 视图可写

性能影响：每次 INSERT/UPDATE/DELETE 多一次函数调用
建议：触发器函数保持精简，避免复杂逻辑
```

## 查看触发器

```sql
SELECT 
  trigger_name, 
  event_manipulation, 
  action_timing, 
  action_orientation
FROM information_schema.triggers
WHERE event_object_table = 'users';
```

## 一句话总结

> **触发器 = 表事件钩子**：**BEFORE / AFTER / INSTEAD OF + ROW / STATEMENT + WHEN**。**审计日志、自动时间戳、跨表一致性、软删除、视图可写**都靠它。**PG 触发器支持 WHEN 条件，比 MySQL 灵活**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "06-advanced/upsert.md": """---
title: UPSERT
description: INSERT ON CONFLICT 实战
---

# UPSERT

> **TL;DR**：UPSERT = **不存在则插入，存在则更新**。**PG 用 `INSERT ON CONFLICT` 实现**，比 MySQL `INSERT ... ON DUPLICATE KEY UPDATE` 更标准、更安全。

## 一句话定义

```
UPSERT = INSERT + UPDATE
       = "如果不存在则 INSERT，否则 UPDATE"
       = 单条 SQL 原子操作
```

## 基本语法

```sql
INSERT INTO table (cols) VALUES (...)
ON CONFLICT (conflict_target) DO UPDATE SET ...
[RETURNING ...];
```

## 实战案例

### 案例 1：单条 upsert

```sql
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  name TEXT NOT NULL,
  last_login_at TIMESTAMPTZ,
  login_count INT DEFAULT 0
);

-- upsert
INSERT INTO users (id, name, last_login_at, login_count)
VALUES (123, 'Alice', now(), 1)
ON CONFLICT (id) DO UPDATE SET
  last_login_at = EXCLUDED.last_login_at,
  login_count = users.login_count + 1;
-- 如果 id=123 存在：更新 last_login_at 和 login_count
-- 如果不存在：插入
```

### 案例 2：库存扣减

```sql
CREATE TABLE products (
  id BIGINT PRIMARY KEY,
  stock INT NOT NULL
);

-- 原子扣减
UPDATE products 
SET stock = stock - 1 
WHERE id = 1 AND stock > 0;
-- 返回 1 行 = 成功扣减，0 行 = 库存不足
```

或者用 INSERT ON CONFLICT：

```sql
INSERT INTO products (id, stock) VALUES (1, 99)
ON CONFLICT (id) DO UPDATE SET stock = products.stock - 1
WHERE products.stock > 0
RETURNING stock;
-- 返回新库存；如果 -1 不存在则不操作
```

### 案例 3：计数器自增

```sql
CREATE TABLE counters (
  name TEXT PRIMARY KEY,
  value BIGINT DEFAULT 0
);

-- 计数器 +1
INSERT INTO counters (name, value) VALUES ('page_view', 1)
ON CONFLICT (name) DO UPDATE SET value = counters.value + 1
RETURNING value;
-- 返回新值
```

### 案例 4：批量 upsert

```sql
INSERT INTO products (id, name, price) VALUES
  (1, 'A', 100),
  (2, 'B', 200),
  (3, 'C', 300)
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  price = EXCLUDED.price;
-- 一次性 upsert 3 行
```

## EXCLUDED 关键字

```sql
-- EXCLUDED 引用 INSERT VALUES 中的值
INSERT INTO users (id, name) VALUES (1, 'Alice')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;
-- 等价于：
--   name = 'Alice'
```

## DO NOTHING 模式

```sql
-- 仅在不存在时插入
INSERT INTO users (id, name) VALUES (1, 'Alice')
ON CONFLICT (id) DO NOTHING;
-- 存在则什么都不做（不报错也不更新）
```

## RETURNING 返回值

```sql
INSERT INTO counters (name, value) VALUES ('click', 1)
ON CONFLICT (name) DO UPDATE SET value = counters.value + 1
RETURNING name, value;
-- 返回 {'click', 42}
```

## MERGE（PG 15+）

**PG 15+ 新增标准 SQL MERGE 语法**：

```sql
MERGE INTO products AS t
USING (VALUES (1, 100), (2, 200)) AS s(id, price)
ON t.id = s.id
WHEN MATCHED THEN
  UPDATE SET price = s.price
WHEN NOT MATCHED THEN
  INSERT (id, price) VALUES (s.id, s.price);
```

**vs INSERT ON CONFLICT**：

| 维度 | ON CONFLICT | MERGE |
|---|---|---|
| 标准 | PG 特有 | ANSI SQL |
| 灵活性 | 单表 | 多表 / 复杂条件 |
| 性能 | 优 | 略慢（解析复杂） |
| 推荐 | 简单 upsert | 复杂业务逻辑 |

## 实战案例

### 案例：用户最后登录时间

```sql
CREATE TABLE user_logins (
  user_id BIGINT PRIMARY KEY,
  last_login_at TIMESTAMPTZ NOT NULL,
  login_count INT NOT NULL DEFAULT 1
);

-- 每次登录调用
INSERT INTO user_logins (user_id, last_login_at, login_count)
VALUES (123, now(), 1)
ON CONFLICT (user_id) DO UPDATE SET
  last_login_at = EXCLUDED.last_login_at,
  login_count = user_logins.login_count + 1;
```

### 案例：幂等消息处理

```sql
-- Kafka 消息处理，message_id 幂等
INSERT INTO processed_messages (message_id, processed_at)
VALUES ('msg-12345', now())
ON CONFLICT (message_id) DO NOTHING
RETURNING message_id;
-- 如果 message_id 已处理，返回 0 行（消息被跳过）
-- 如果新消息，返回 1 行（处理）
```

## 一句话总结

> **UPSERT = INSERT ON CONFLICT**：**`ON CONFLICT (key) DO UPDATE SET ... = EXCLUDED.field`**。**EXCLUDED 引用 INSERT 值，DO NOTHING 跳过**。**PG 15+ 新增标准 MERGE**，复杂场景用 MERGE，简单场景用 ON CONFLICT。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "06-advanced/view.md": """---
title: 视图与物化视图
description: VIEW / MATERIALIZED VIEW
---

# 视图与物化视图

> **TL;DR**：视图 = 虚拟表（每次查询重算）。**物化视图 = 物理存储的查询结果**（可建索引、可加速报表 10x+）。

## 一句话定义

```
VIEW             = SQL 查询的"快捷方式"，不存储数据
MATERIALIZED VIEW = 查询结果的"缓存"，物理存储
```

## 普通 VIEW

```sql
-- 1. 创建
CREATE VIEW active_users AS
SELECT * FROM users WHERE is_active = true;

-- 2. 使用
SELECT * FROM active_users;
-- 等同于 SELECT * FROM users WHERE is_active = true

-- 3. 嵌套
CREATE VIEW active_admins AS
SELECT * FROM active_users WHERE role = 'admin';

-- 4. 删除
DROP VIEW active_users;
```

### 视图更新

```sql
-- 默认：只读
-- 简单视图可以 INSERT/UPDATE/DELETE
CREATE VIEW users_summary AS
SELECT id, name FROM users;

-- 可更新
INSERT INTO users_summary (id, name) VALUES (1, 'Alice');
-- 实际 INSERT INTO users
```

### INSTEAD OF 触发器（让任意视图可写）

```sql
CREATE VIEW users_view AS
SELECT id, name, email FROM users;

-- INSTEAD OF 触发器
CREATE FUNCTION insert_user_view() RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO users (id, name, email) 
  VALUES (NEW.id, NEW.name, NEW.email);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_view_insert
INSTEAD OF INSERT ON users_view
FOR EACH ROW EXECUTE FUNCTION insert_user_view();
```

## 物化视图（MATERIALIZED VIEW）

```sql
-- 1. 创建
CREATE MATERIALIZED VIEW daily_sales AS
SELECT
  date_trunc('day', created_at) AS day,
  count(*) AS order_count,
  sum(amount) AS total_amount
FROM orders
GROUP BY day
ORDER BY day;

-- 2. 加索引
CREATE UNIQUE INDEX idx_daily_sales_day ON daily_sales (day);

-- 3. 查询（毫秒级）
SELECT * FROM daily_sales WHERE day >= '2026-08-01';

-- 4. 刷新
REFRESH MATERIALIZED VIEW daily_sales;
-- 阻塞读，全量重建

-- 5. 并发刷新（PG 9.4+）
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_sales;
-- 不阻塞读，但需要 UNIQUE INDEX
```

## 视图 vs 物化视图

| 维度 | VIEW | MATERIALIZED VIEW |
|---|---|---|
| 存储 | 不存 |  | 物理存储 |
| 查询速度 | 实时计算 |  | 快速（已算好） |
| 实时性 | 100% |  | 取决于刷新频率 |
| 索引 | 不能建 |  | 可以 |
| 空间 | 0 |  | 取决于数据量 |

## 实战案例

### 案例 1：日报表

```sql
CREATE MATERIALIZED VIEW daily_sales AS
SELECT
  date_trunc('day', created_at) AS day,
  user_id,
  count(*) AS order_count,
  sum(amount) AS total_amount
FROM orders
WHERE created_at >= '2026-01-01'
GROUP BY day, user_id;

CREATE UNIQUE INDEX idx_daily_sales 
ON daily_sales (day, user_id);

-- pg_cron 定时刷新
SELECT cron.schedule('refresh-daily-sales', '0 1 * * *',
  'REFRESH MATERIALIZED VIEW CONCURRENTLY daily_sales');
```

### 案例 2：实时排行榜

```sql
-- 创建物化视图
CREATE MATERIALIZED VIEW top_products AS
SELECT
  product_id,
  sum(amount) AS total_sales,
  rank() OVER (ORDER BY sum(amount) DESC) AS rnk
FROM orders
WHERE created_at >= now() - interval '7 days'
GROUP BY product_id;

CREATE UNIQUE INDEX idx_top_products ON top_products (product_id);

-- 每 5 分钟刷新（自动）
-- 用 pg_cron 或应用层定时调用 REFRESH
```

### 案例 3：跨表预聚合

```sql
CREATE MATERIALIZED VIEW user_stats AS
SELECT
  u.id,
  u.name,
  count(o.id) AS order_count,
  coalesce(sum(o.amount), 0) AS total_spent,
  max(o.created_at) AS last_order_at
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

CREATE INDEX idx_user_stats_total ON user_stats (total_spent DESC);
```

## 性能优化

```sql
-- 1. 物化视图要 UNIQUE INDEX 才能并发刷新
CREATE UNIQUE INDEX idx_mv_id ON mv (id);

-- 2. 大物化视图分片刷新（PG 13+）
REFRESH MATERIALIZED VIEW CONCURRENTLY mv 
WITH (parallel_workers = 4);

-- 3. 自动刷新（pg_cron）
CREATE EXTENSION pg_cron;
SELECT cron.schedule('refresh-mv', '*/15 * * * *',
  'REFRESH MATERIALIZED VIEW CONCURRENTLY daily_sales');
```

## 一句话总结

> **VIEW = 虚拟表（实时算）、MATERIALIZED VIEW = 缓存表（预计算）**。**报表、排行榜、跨表聚合**用物化视图提速 10x+。**UNIQUE INDEX 是并发刷新的前提**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "07-operations/backup.md": """---
title: 备份与恢复
description: pg_dump / pg_basebackup / PITR
---

# 备份与恢复

> **TL;DR**：PG 备份 = **逻辑备份（pg_dump）+ 物理备份（pg_basebackup）+ WAL archive**。**RPO < 1 分钟、PITR 任意时间点恢复**是 PG 备份的标准能力。

## 一句话定义

```
备份策略 = 全量 + 增量 + WAL archive
        = RPO 取决于 WAL 归档频率
        = RTO 取决于恢复速度
```

## 三种备份方式对比

| 维度 | 逻辑（pg_dump） | 物理（pg_basebackup） | 流复制 |
|---|---|---|---|
| 备份对象 | 逻辑 SQL | 物理文件 | 持续 WAL |
| 恢复速度 | 慢（重建索引） | 快（拷贝文件） | 极快（promote） |
| 跨版本 | ✓ | ✗ | ✗ |
| 跨平台 | ✓ | ✗ | ✗ |
| 粒度 | 单表 / 全库 | 全实例 | 持续 |
| 适用 | 迁移 / 备份 | HA / 容灾 | DR / 读写分离 |

## 1. pg_dump 逻辑备份

```bash
# 全库
pg_dump -h localhost -U postgres -d mydb > backup.sql

# 压缩
pg_dump -h localhost -U postgres -d mydb | gzip > backup.sql.gz

# 自定义格式（并行恢复）
pg_dump -h localhost -U postgres -d mydb -Fc > backup.dump

# 目录格式（并行恢复）
pg_dump -h localhost -U postgres -d mydb -Fd -j 4 -f backup_dir/

# 单表
pg_dump -h localhost -U postgres -d mydb -t users > users.sql

# 仅 schema
pg_dump -h localhost -U postgres -d mydb --schema-only > schema.sql
```

**恢复**：

```bash
# SQL 格式
psql -h localhost -U postgres -d newdb < backup.sql

# 自定义格式
pg_restore -h localhost -U postgres -d newdb backup.dump

# 并行恢复
pg_restore -h localhost -U postgres -d newdb -j 4 backup.dump
```

## 2. pg_basebackup 物理备份

```bash
# 全量备份
pg_basebackup -h localhost -U postgres -D /backup/base -Ft -Xs -P -c fast

# 参数：
# -Ft：tar 格式
# -Xs：流式 WAL
# -P：进度显示
# -c fast：快速 checkpoint
```

**恢复**：

```bash
# 1. 停 PG
pg_ctl stop

# 2. 清空数据目录
rm -rf /var/lib/postgresql/data/*

# 3. 解压备份
tar -xf /backup/base/base.tar -C /var/lib/postgresql/data/
tar -xf /backup/base/wal.tar -C /var/lib/postgresql/wal/

# 4. 启动
pg_ctl start
```

## 3. WAL archive（增量 + PITR）

**配置归档**：

```ini
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /archive/%f'
# 或用 WAL-G / pgbackrest
```

**手动归档**：

```sql
SELECT pg_switch_wal();
-- 强制切换 WAL，立即归档
```

**PITR（Point-in-Time Recovery）**：

```bash
# 1. 恢复基础备份
rm -rf /var/lib/postgresql/data/*
pg_basebackup -h ... -D /var/lib/postgresql/data -Ft -Xs

# 2. 创建恢复配置文件
cat > /var/lib/postgresql/data/recovery.signal << EOF
EOF

cat >> /var/lib/postgresql/data/postgresql.conf << EOF
restore_command = 'cp /archive/%f %p'
recovery_target_time = '2026-08-09 10:00:00'
recovery_target_action = 'pause'
EOF

# 3. 启动
pg_ctl start

# 4. 验证
SELECT pg_is_in_recovery();  -- true 表示在恢复中
SELECT pg_wal_replay_resume();  -- 恢复完成
```

## 4. 工具推荐

### pgBackrest

```bash
# 配置文件
/etc/pgbackrest.conf

[global]
repo1-path=/var/lib/pgbackrest
repo1-cipher-type=aes-256-cbc
repo1-cipher-pass=secret

[mycluster]
pg1-path=/var/lib/postgresql/data

# 全量 + 增量 + WAL
pgbackrest backup --type=full --compress
pgbackrest backup --type=incr --compress

# 恢复
pgbackrest restore --type=time --target="2026-08-09 10:00:00"
```

### Barman

```bash
# barman backup
barman backup mycluster
barman recover mycluster 20260809T100000 /var/lib/postgresql/data
```

### WAL-G

```bash
# 推送 WAL 到 S3
archive_command = 'wal-g wal-push %p --config /etc/walg.json'

# 备份
wal-g backup-push /var/lib/postgresql/data

# 恢复
wal-g backup-fetch /var/lib/postgresql/data BACKUP_NAME
```

## 5. 备份策略

```
生产环境推荐：
  1. 每日全量（pgBackrest full）
  2. 每小时增量（pgBackrest incr）
  3. WAL 持续归档（S3 / NFS）
  4. RPO < 1 分钟
  5. RTO 取决于恢复速度
```

## 实战案例

### 案例 1：误删除整张表

```bash
# 1. 停业务
pg_ctl pause  # 暂停写入

# 2. 从最近的备份恢复到一个新实例
pg_restore -h localhost -d testdb users.dump

# 3. 提取丢失的表
pg_dump -h localhost -d testdb -t users > recovered_users.sql

# 4. 加载到生产
psql -h localhost -d productiondb -f recovered_users.sql
```

### 案例 2：PITR 到误操作前 1 分钟

```bash
# 误操作：DELETE FROM users  -- 删错了

# 1. 找到误操作时间
# 14:30:00 执行 DELETE

# 2. PITR 到 14:29:00
recovery_target_time = '2026-08-09 14:29:00'
```

## 一句话总结

> **PG 备份 = pg_dump（逻辑）+ pg_basebackup（物理）+ WAL archive（PITR）**。**生产推荐 pgBackrest 全量+增量+WAL 到 S3**，**RPO < 1 分钟**。**跨版本迁移用 pg_dump，HA/容灾用 pg_basebackup**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "07-operations/stats.md": """---
title: 统计信息
description: pg_stat / pg_stats 实战
---

# 统计信息

> **TL;DR**：PG 统计信息 = planner 决策的依据。**`pg_stat_*` 视图监控运行时**，**`pg_stats` 看列分布**，**`pg_stat_statements` 看 SQL 性能**。

## 一句话定义

```
统计信息 = PG 自动收集的运行时 / 列分布 / SQL 数据
        = planner 据此选最优执行计划
        = 监控的"眼睛"
```

## pg_stat_user_tables（表级）

```sql
SELECT
  schemaname, relname,
  seq_scan,                -- 顺序扫描次数
  seq_tup_read,            -- 顺序扫描读行数
  idx_scan,                -- 索引扫描次数
  idx_tup_fetch,           -- 索引扫描读取
  n_tup_ins,               -- 累计插入行数
  n_tup_upd,               -- 累计更新行数
  n_tup_del,               -- 累计删除行数
  n_live_tup,              -- 当前活元组数
  n_dead_tup,              -- 当前死元组数
  last_vacuum,             -- 上次手动 vacuum
  last_autovacuum,         -- 上次自动 vacuum
  last_analyze,            -- 上次手动 analyze
  last_autoanalyze         -- 上次自动 analyze
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;
```

**实战 SQL**：

```sql
-- 找需要 vacuum 的表（死元组多）
SELECT relname, n_dead_tup, n_live_tup,
  ROUND(100 * n_dead_tup::numeric / NULLIF(n_live_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY dead_pct DESC;

-- 找未使用的索引（考虑删除）
SELECT schemaname, relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

## pg_stat_user_indexes（索引级）

```sql
SELECT
  schemaname, relname, indexrelname,
  idx_scan,
  idx_tup_read,
  idx_tup_fetch,
  pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## pg_statio_user_indexes（索引 IO）

```sql
SELECT
  schemaname, relname, indexrelname,
  idx_blks_read,           -- 磁盘读
  idx_blks_hit             -- 缓存命中
FROM pg_statio_user_indexes
ORDER BY idx_blks_read DESC;
```

## pg_stat_statements（SQL 级）

```sql
-- 1. 安装
CREATE EXTENSION pg_stat_statements;

-- 2. postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.max = 10000
pg_stat_statements.track = top
pg_stat_statements.track_planning = on
```

**查询最耗资源的 SQL**：

```sql
-- 1. 总耗时 Top 10
SELECT
  substring(query, 1, 100) AS query,
  calls,
  ROUND(total_exec_time::numeric, 2) AS total_ms,
  ROUND(mean_exec_time::numeric, 2) AS mean_ms,
  ROWS
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- 2. 平均耗时 Top 10
SELECT
  substring(query, 1, 100) AS query,
  calls,
  ROUND(mean_exec_time::numeric, 2) AS mean_ms
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 3. 写多读多的 SQL
SELECT
  substring(query, 1, 100) AS query,
  calls,
  shared_blks_read,
  shared_blks_hit,
  ROUND(100 * shared_blks_hit::numeric / NULLIF(shared_blks_hit + shared_blks_read, 0), 2) AS hit_pct
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 10;

-- 4. 重置
SELECT pg_stat_statements_reset();
```

## pg_stats（列分布）

```sql
-- 看每列的统计信息
SELECT
  schemaname, tablename, attname,
  null_frac,              -- NULL 比例
  avg_width,              -- 平均宽度
  n_distinct,             -- distinct 值（-1 表示唯一）
  most_common_vals,       -- 最常见的值
  most_common_freqs,      -- 最常见值的频率
  histogram_bounds        -- 直方图边界
FROM pg_stats
WHERE tablename = 'users';

-- 手动触发统计更新
ANALYZE users;
ANALYZE VERBOSE users;  -- 显示更新内容
```

## pg_stat_activity（实时活动）

```sql
-- 当前所有活动连接
SELECT
  pid, usename, application_name,
  client_addr, backend_start,
  state, query_start, state_change,
  wait_event_type, wait_event,
  substring(query, 1, 100) AS query
FROM pg_stat_activity
WHERE pid != pg_backend_pid()
ORDER BY query_start;

-- 长事务
SELECT pid, xact_start, state, substring(query, 1, 50)
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
  AND state != 'idle'
ORDER BY xact_start;
```

## pg_stat_replication（复制）

```sql
SELECT
  client_addr,
  state,
  sync_state,                       -- async / sync / potential
  sent_lsn, replay_lsn,
  pg_size_pretty(sent_lsn - replay_lsn) AS lag_bytes,
  EXTRACT(EPOCH FROM now() - reply_time) AS lag_seconds
FROM pg_stat_replication;
```

## 一句话总结

> **PG 统计 = 监控的眼睛**：**`pg_stat_user_tables`（表）+ `pg_stat_user_indexes`（索引）+ `pg_stat_statements`（SQL）**。**90% 性能问题从这 3 个视图就能定位**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "07-operations/upgrade.md": """---
title: 版本升级
description: pg_upgrade / 逻辑复制升级
---

# 版本升级

> **TL;DR**：PG 大版本升级有 **3 种方式**：**pg_upgrade 原地升级（5-30 分钟停机）、pg_upgrade --link（秒级停机）、逻辑复制升级（停机 < 1 分钟）**。**生产推荐逻辑复制升级**。

## 一句话定义

```
升级策略 = 大版本升级（13 → 16）+ 零停机
        = 用 pg_upgrade（秒级-分钟级停机）
        = 用逻辑复制（零停机，但需双写）
```

## 三种升级方式对比

| 方式 | 停机时间 | 复杂度 | 数据量限制 |
|---|---|---|---|
| pg_upgrade | 5-30 分钟 | 低 | 无 |
| pg_upgrade --link | 秒级 | 低 | 无（不能回退） |
| 逻辑复制 | < 1 分钟 | 中 | 无（需双倍存储） |
| dump + restore | 数小时 | 低 | 大库慢 |

## 1. pg_upgrade 原地升级

```bash
# 1. 备份
pg_dumpall -h /tmp -f backup.sql

# 2. 停 PG
pg_ctl stop

# 3. 安装新版本（Debian/Ubuntu）
apt install postgresql-16

# 4. 检查升级
/usr/lib/postgresql/16/bin/pg_upgrade \
  --old-datadir=/var/lib/postgresql/13/main \
  --new-datadir=/var/lib/postgresql/16/main \
  --old-bindir=/usr/lib/postgresql/13/bin \
  --new-bindir=/usr/lib/postgresql/16/bin \
  --check

# 5. 执行升级
/usr/lib/postgresql/16/bin/pg_upgrade \
  --old-datadir=/var/lib/postgresql/13/main \
  --new-datadir=/var/lib/postgresql/16/main \
  --old-bindir=/usr/lib/postgresql/13/bin \
  --new-bindir=/usr/lib/postgresql/16/bin

# 6. 启动新版本
pg_ctl -D /var/lib/postgresql/16/main start

# 7. 分析统计
/usr/lib/postgresql/16/bin/vacuumdb --all --analyze-in-stages

# 8. 删除老版本
./delete_old_cluster.sh
```

## 2. pg_upgrade --link 硬链接（秒级停机）

```bash
# 1. 停 PG
pg_ctl stop

# 2. 升级（用硬链接共享文件，不复制）
/usr/lib/postgresql/16/bin/pg_upgrade \
  --old-datadir=/var/lib/postgresql/13/main \
  --new-datadir=/var/lib/postgresql/16/main \
  --old-bindir=/usr/lib/postgresql/13/bin \
  --new-bindir=/usr/lib/postgresql/16/bin \
  --link

# ⚠️ 硬链接后不能回退到老版本
# 老数据和新数据指向同一文件

# 3. 启动
pg_ctl -D /var/lib/postgresql/16/main start
```

> **优势**：**停机时间 < 1 秒**（仅启动新版本进程时间）。

## 3. 逻辑复制升级（零停机）

**适用于**：可接受双倍存储的复杂场景。

```bash
# 1. 老版本（13）作为 PUBLISHER
psql -p 5432 -c "CREATE PUBLICATION pub_upgrade FOR ALL TABLES;"

# 2. 新版本（16）作为 SUBSCRIBER
initdb -D /var/lib/postgresql/16/main
pg_ctl -D /var/lib/postgresql/16/main start

psql -p 5433 -c "CREATE SUBSCRIPTION sub_upgrade 
  CONNECTION 'host=localhost port=5432 dbname=mydb' 
  PUBLICATION pub_upgrade;"

# 3. 等待同步完成
psql -p 5433 -c "SELECT * FROM pg_stat_subscription;"

# 4. 应用切换（停写老版本，启用新版本）
# 4.1 停应用
# 4.2 等同步完成
psql -p 5433 -c "SELECT pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), received_lsn)) FROM pg_stat_subscription;"
-- 应该为 0

# 4.3 切流到新版本
# 修改应用连接端口 5432 → 5433

# 4.4 启用老版本为只读 / 删除
```

## 4. pg_dumpall + restore

```bash
# 1. 备份
pg_dumpall -h /tmp -f backup.sql

# 2. 启动新版本
pg_ctl -D /var/lib/postgresql/16/main start

# 3. 恢复
psql -h /tmp -d postgres -f backup.sql
```

## 升级检查清单

```
1. 扩展兼容性
   - 每个扩展都支持新版本？
   - 比如 PostGIS、pg_partman、pg_cron

2. 配置兼容性
   - 废弃参数（如 background_sleep_delay → pg_sleep）
   - 默认值变化

3. SQL 兼容性
   - 数据类型变化（如 timestamp → timestamptz）
   - 函数废弃

4. 性能变化
   - planner 改进可能让查询变慢或变快
   - 需要重新 ANALYZE

5. 客户端驱动
   - JDBC / psycopg / libpq 升级
```

## 实战案例

### 案例 1：PG 13 → 16 在线升级

```bash
# 1. 检查
/usr/lib/postgresql/16/bin/pg_upgrade --check ...

# 2. 测试升级（用副本）
# 在新机器上跑同样步骤

# 3. 生产升级
# - 选择业务低峰
# - 通知所有依赖方
# - 准备回滚方案（dump）
# - 执行 pg_upgrade
# - 启动新版本
# - 验证应用
```

### 案例 2：逻辑复制升级大库

```bash
# 1. 老库（13）开启逻辑复制
psql -p 5432 -c "ALTER SYSTEM SET wal_level = logical;"

# 2. 重启老库（应用 wal_level）
pg_ctl restart

# 3. 创建 PUBLICATION
psql -p 5432 -c "CREATE PUBLICATION pub FOR ALL TABLES;"

# 4. 新库（16）创建 SUBSCRIPTION
psql -p 5433 -c "CREATE SUBSCRIPTION sub CONNECTION '...' PUBLICATION pub;"

# 5. 等待同步（小时级，取决于数据量）

# 6. 切换
# - 应用停写（5 分钟）
# - 等同步
# - 切流
# - 应用启动
```

## 一句话总结

> **PG 升级 = pg_upgrade（秒级-分钟级）+ 逻辑复制（零停机）**。**生产首选 pg_upgrade --link**，**大库用逻辑复制**。**升级前检查扩展兼容性 + 配置兼容性 + SQL 兼容性**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "08-replication/hot-standby.md": """---
title: Hot Standby 从库查询
description: PostgreSQL 从库只读查询
---

# Hot Standby 从库查询

> **TL;DR**：Hot Standby = **从库应用 WAL 时同时提供只读查询**。**读写分离、查询报表** = 标配能力。

## 一句话定义

```
Hot Standby = 流复制 + 从库可读
            = 实时跟随主库
            = 提供 SELECT（不提供 INSERT/UPDATE）
```

## 启用

```ini
# postgresql.conf（主库）
wal_level = replica
max_wal_senders = 10

# postgresql.conf（从库）
hot_standby = on
hot_standby_feedback = on       # 防止查询冲突
max_standby_streaming_delay = 30s  # 取消冲突查询的最大延迟
```

## 实战配置

```bash
# 1. 主库配置（如前）
wal_level = replica
max_wal_senders = 10
wal_keep_size = '1GB'

# 2. 从库用 pg_basebackup 初始化
pg_basebackup -h primary.db -D /data -U replicator -P -Xs -c fast

# 3. 从库 standby.signal
touch /data/standby.signal

# 4. 从库 postgresql.conf
cat >> /data/postgresql.conf << EOF
primary_conninfo = 'host=primary.db port=5432 user=replicator password=xxx'
hot_standby = on
hot_standby_feedback = on
EOF

# 5. 启动从库
pg_ctl start -D /data

# 6. 验证
psql -c "SELECT pg_is_in_recovery();"
-- t（true 表示在 recovery 模式，只读）
```

## 应用读写分离

```yaml
# Spring Boot 多数据源
spring:
  datasource:
    primary:
      url: jdbc:postgresql://primary.db:6432/mydb
      driver-class-name: org.postgresql.Driver
    replica:
      url: jdbc:postgresql://replica.db:6432/mydb
      driver-class-name: org.postgresql.Driver
```

```java
@Service
public class OrderService {
  @Autowired
  @Qualifier("primaryDataSource")
  private DataSource primaryDs;

  @Autowired
  @Qualifier("replicaDataSource")
  private DataSource replicaDs;

  @Transactional("primaryTransactionManager")
  public void createOrder(Order order) {
    // 写主库
  }

  public List<Order> getOrders(Long userId) {
    // 读从库
    return jdbcTemplate.query(
      "SELECT * FROM orders WHERE user_id = ?", 
      userId
    );
  }
}
```

## 冲突处理

**查询冲突场景**：

```
1. 主库：VACUUM 清理了 dead tuple
2. 从库：还有长查询读到这些 dead tuple
3. 冲突！从库要么取消查询，要么延迟 vacuum
```

**解决策略**：

```ini
# 1. 延迟取消查询
max_standby_streaming_delay = 30s
# 主库 vacuum 延迟 30s 等从库查询完成

# 2. 从库反馈（推荐）
hot_standby_feedback = on
# 从库告诉主库："我这里有长查询，请暂缓 vacuum"

# 3. 监控冲突
SELECT * FROM pg_stat_database_conflicts;
-- conflict_tablespace / conflict_lock / conflict_snapshot
```

## 同步 vs 异步 + Hot Standby

```
异步复制 + Hot Standby：
  - 从库最多滞后几秒
  - 适合读写分离、报表

同步复制 + Hot Standby：
  - 强一致读（理论上）
  - 实际：从库可能还没应用最新的 WAL
  - 需要 synchronous_commit = on（等从库 fsync）
```

## 监控

```sql
-- 主库：看从库延迟
SELECT
  client_addr,
  sent_lsn - replay_lsn AS byte_lag,
  EXTRACT(EPOCH FROM now() - reply_time) AS seconds_lag
FROM pg_stat_replication;

-- 从库：看 replay 进度
SELECT
  pg_last_wal_receive_lsn(),  -- 接收位置
  pg_last_wal_replay_lsn(),   -- replay 位置
  pg_last_xact_replay_timestamp();
```

## 一句话总结

> **Hot Standby = 流复制 + 从库只读查询**。**读写分离必备**。**冲突用 hot_standby_feedback 解决**，**延迟用 max_standby_streaming_delay 控制**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "08-replication/logical.md": """---
title: 逻辑复制
description: PG 10+ 行列级复制
---

# 逻辑复制

> **TL;DR**：逻辑复制 = **行列级复制**（vs 物理复制按 block 复制）。**适用**：跨大版本升级、PG → Kafka、PG → 数仓、读写分离（精确粒度）。

## 一句话定义

```
逻辑复制 = PUBLICATION（发布）+ SUBSCRIPTION（订阅）
        = 按表 / 按操作（INSERT/UPDATE/DELETE）复制
        = 不复制 DDL、不复制 TRUNCATE
        = 解耦复制
```

## 与物理复制的对比

| 维度 | 物理（流复制） | 逻辑 |
|---|---|---|
| 粒度 | 整个实例 | 单表 / 单操作 |
| 跨大版本 | ✗ | ✓ |
| 跨平台 | ✗ | ✓ |
| 不同 schema 名 | ✗ | ✓ |
| SELECT 过滤 | ✗ | ✓（WHERE） |
| 列过滤 | ✗ | ✓ |
| 双向复制 | 难 | ✓ |
| 性能 | 高 | 中 |

## 配置

```ini
# postgresql.conf（源库）
wal_level = logical                    # 必须 logical
max_replication_slots = 10             # 每个订阅 1 个 slot
max_wal_senders = 10                   # 流复制连接数
```

```sql
-- 1. PUBLICATION（源库）
CREATE PUBLICATION pub_orders FOR TABLE orders;
-- 或
CREATE PUBLICATION pub_all FOR ALL TABLES;
-- 或带 WHERE 过滤
CREATE PUBLICATION pub_paid FOR TABLE orders 
  WHERE (status = 'paid');

-- 2. SUBSCRIPTION（目标库）
CREATE SUBSCRIPTION sub_orders
  CONNECTION 'host=source.db port=5432 dbname=mydb user=replicator password=xxx'
  PUBLICATION pub_orders;
```

## 实战案例

### 案例 1：跨大版本升级（PG 13 → 16）

```sql
-- 源库（PG 13）
CREATE PUBLICATION pub_upgrade FOR ALL TABLES;

-- 目标库（PG 16）
CREATE SUBSCRIPTION sub_upgrade
  CONNECTION 'host=old-pg-13.db port=5432 dbname=mydb user=replicator'
  PUBLICATION pub_upgrade;

-- 等待同步
SELECT * FROM pg_stat_subscription;

-- 切换应用连接到新库
-- 删除 SUBSCRIPTION + 老库
```

### 案例 2：PG → Kafka（CDC）

```sql
-- PG 端
CREATE PUBLICATION pub_cdc FOR TABLE orders, users;

-- 用 debezium / kafka-connect-pgsql 订阅
-- 实时流式变更到 Kafka
```

### 案例 3：PG → ClickHouse / 数仓

```sql
-- PG 端
CREATE PUBLICATION pub_dw FOR TABLE orders;
CREATE PUBLICATION pub_dw FOR TABLE users;

-- ClickHouse 端用 MaterializedPostgreSQL 引擎
CREATE TABLE orders_dw (...)
ENGINE = MaterializedPostgreSQL('pg-host:5432', 'mydb', 'orders', 'user', 'password', 'pub_dw');
```

### 案例 4：读写分离（行级过滤）

```sql
-- 只复制已支付订单到分析库
CREATE PUBLICATION pub_paid FOR TABLE orders
  WHERE (status = 'paid');

CREATE SUBSCRIPTION sub_paid
  CONNECTION '...'
  PUBLICATION pub_paid;
```

## 监控

```sql
-- PUBLICATION 端
SELECT * FROM pg_stat_replication;

-- SUBSCRIPTION 端
SELECT
  subname,
  pid,
  received_lsn,
  last_msg_send_time,
  last_msg_replay_time,
  EXTRACT(EPOCH FROM now() - last_msg_replay_time) AS lag_seconds
FROM pg_stat_subscription;
```

## 限制

```sql
-- ❌ DDL 不自动复制
ALTER TABLE orders ADD COLUMN new_col INT;
-- 不会自动同步到订阅端，需要手动 ALTER

-- ❌ TRUNCATE 不自动复制
TRUNCATE orders;
-- 默认不复制（可以用 publish = 'truncate' 启用）

-- ❌ 大事务可能阻塞
-- 大量 INSERT 会阻塞 replication slot

-- ⚠️ Sequence 不自动同步
-- 需要单独处理
```

## 双向复制（multi-master）

```sql
-- A 库（pub_a）
CREATE PUBLICATION pub_a FOR TABLE users WHERE (id % 2 = 0);
-- B 库（pub_b）
CREATE PUBLICATION pub_b FOR TABLE users WHERE (id % 2 = 1);

-- A 订阅 B
CREATE SUBSCRIPTION sub_b
  CONNECTION 'host=B.db ...'
  PUBLICATION pub_b;

-- B 订阅 A
CREATE SUBSCRIPTION sub_a
  CONNECTION 'host=A.db ...'
  PUBLICATION pub_a;

-- ⚠️ 必须用 WHERE 切分，避免冲突
```

## 一句话总结

> **逻辑复制 = 行列级灵活复制**：**跨大版本、跨平台、按表/按列/按 WHERE 过滤**。**PG → Kafka / 数仓**的首选。**DDL 不自动复制**，**TRUNCATE 默认不复制**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "09-connection/jdbc.md": """---
title: JDBC 连接
description: PostgreSQL JDBC 驱动实战
---

# JDBC 连接

> **TL;DR**：PG JDBC 驱动 = `org.postgresql.Driver`。**批量插入开 `rewriteBatchedInserts=true` 性能提升 10x**。**连接池用 HikariCP**。

## 一句话定义

```
JDBC 连接 = org.postgresql.Driver
          + HikariCP / DBCP 连接池
          + 批量插入优化
          + COPY 协议
```

## 基本连接

```java
// 1. 注册驱动（PG JDBC 4.0+ 自动注册）
Class.forName("org.postgresql.Driver");

// 2. 基本连接
String url = "jdbc:postgresql://localhost:5432/mydb";
Connection conn = DriverManager.getConnection(url, "user", "password");

// 3. SSL 连接
String url = "jdbc:postgresql://localhost:5432/mydb?sslmode=require&sslcert=client.crt&sslkey=client.key";

// 4. 带 schema
String url = "jdbc:postgresql://localhost:5432/mydb?currentSchema=myschema";
```

## HikariCP 配置（推荐）

```yaml
spring:
  datasource:
    url: jdbc:postgresql://localhost:6432/mydb
    username: appuser
    password: xxx
    driver-class-name: org.postgresql.Driver
    hikari:
      maximum-pool-size: 50
      minimum-idle: 10
      connection-timeout: 30000
      idle-timeout: 600000
      max-lifetime: 1800000
      pool-name: HikariPool-PG
```

## 批量插入优化

### ❌ 错误方式（慢）

```java
PreparedStatement ps = conn.prepareStatement(
  "INSERT INTO users (name, email) VALUES (?, ?)"
);
for (User u : users) {
  ps.setString(1, u.name);
  ps.setString(2, u.email);
  ps.executeUpdate();  // 每次执行
}
```

### ✅ 正确方式（快 10x）

```yaml
# application.yml
spring:
  datasource:
    hikari:
      data-source-properties:
        rewriteBatchedInserts: true    # 关键！
```

```java
// 批量模式
for (User u : users) {
  ps.setString(1, u.name);
  ps.setString(2, u.email);
  ps.addBatch();                       // 加入批
}
ps.executeBatch();                     // 一次性执行
```

**原理**：`rewriteBatchedInserts=true` 把 1000 个 INSERT 合并成 1 条 multi-row INSERT。

## COPY 协议（最快）

```java
CopyManager copyManager = PGConnection.unwrap(PGConnection.class).getCopyAPI();

try (CopyIn copyIn = copyManager.copyIn(
    "COPY users (name, email) FROM STDIN WITH (FORMAT csv)")) {
    for (User u : users) {
        String row = u.name + "," + u.email + "\n";
        copyIn.writeToCopy(row.getBytes(), 0, row.length());
    }
}
// 100 万行约 5 秒
```

## PG 特有配置

```yaml
spring:
  datasource:
    hikari:
      data-source-properties:
        # 1. 批量插入优化
        rewriteBatchedInserts: true
        
        # 2. Prepared Statement 缓存
        prepareThreshold: 5              # 5 次后缓存
        
        # 3. 默认 fetch 大小
        defaultRowFetchSize: 100
        
        # 4. 字符集
        charset: UTF-8
        
        # 5. 未知类型兼容性
        stringtype: undefined            # varlena 优化
        
        # 6. 取消长查询
        socketTimeout: 30                # 秒
```

## 常见错误

### 1. 连接超时

```
org.postgresql.net.PGTimeoutException
```

**修复**：
```yaml
spring:
  datasource:
    hikari:
      connection-timeout: 30000
```

### 2. SSL 配置

```
PSQLException: SSL error
```

**修复**：
```yaml
spring:
  datasource:
    url: jdbc:postgresql://host:5432/db?sslmode=require
```

### 3. 字符集

```
编码错误 / 乱码
```

**修复**：
```yaml
spring:
  datasource:
    url: jdbc:postgresql://host:5432/db?charset=UTF8
```

### 4. 时区

```yaml
# JVM 默认时区
user.timezone=Asia/Shanghai

# PG 连接时区
jdbc:postgresql://host:5432/db?TimeZone=Asia/Shanghai
```

## 实战案例

### 案例 1：批量插入 100 万行

```java
// 用 rewriteBatchedInserts=true
int batchSize = 1000;
for (int i = 0; i < users.size(); i += batchSize) {
    PreparedStatement ps = conn.prepareStatement(
      "INSERT INTO users (name, email) VALUES (?, ?)"
    );
    int end = Math.min(i + batchSize, users.size());
    for (int j = i; j < end; j++) {
        ps.setString(1, users.get(j).name);
        ps.setString(2, users.get(j).email);
        ps.addBatch();
    }
    ps.executeBatch();
}
// 100 万行约 30 秒

// 用 COPY（更快）
// 100 万行约 5 秒
```

### 案例 2：分页查询

```java
// OFFSET 性能差（深分页）
PreparedStatement ps = conn.prepareStatement(
  "SELECT * FROM users ORDER BY id LIMIT ? OFFSET ?"
);

// 游标分页（推荐）
PreparedStatement ps = conn.prepareStatement(
  "SELECT * FROM users WHERE id > ? ORDER BY id LIMIT ?"
);
ps.setLong(1, lastId);  // 上次最后 id
ps.setInt(2, 20);
```

## 一句话总结

> **JDBC 连接 = HikariCP + rewriteBatchedInserts=true + 必要的 PG 优化参数**。**批量插入从 30s 降到 5s**。**深分页用游标**。**COPY 协议最快**（百万行 5s）。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "09-connection/libpq.md": """---
title: libpq C 库
description: PostgreSQL C API 实战
---

# libpq C 库

> **TL;DR**：libpq = PG 的 **C 语言客户端库**。**所有 PG 客户端（JDBC / psycopg / libpq 本身）都基于或参考 libpq 设计**。

## 一句话定义

```
libpq = PG 的 C API
     = 所有 PG 客户端的基础
     = 异步查询 + COPY 协议
```

## 基本使用

```c
#include <libpq-fe.h>

int main() {
    PGconn *conn = PQconnectdb(
      "host=localhost dbname=mydb user=postgres password=xxx"
    );
    
    if (PQstatus(conn) != CONNECTION_OK) {
        fprintf(stderr, "Connection failed: %s", PQerrorMessage(conn));
        PQfinish(conn);
        return 1;
    }
    
    // 执行查询
    PGresult *res = PQexec(conn, "SELECT id, name FROM users");
    
    if (PQresultStatus(res) != PGRES_TUPLES_OK) {
        fprintf(stderr, "Query failed: %s", PQresultErrorMessage(res));
        PQclear(res);
        PQfinish(conn);
        return 1;
    }
    
    // 处理结果
    int rows = PQntuples(res);
    int cols = PQnfields(res);
    
    for (int i = 0; i < rows; i++) {
        for (int j = 0; j < cols; j++) {
            printf("%s\t", PQgetvalue(res, i, j));
        }
        printf("\n");
    }
    
    PQclear(res);
    PQfinish(conn);
    return 0;
}
```

**编译**：
```bash
gcc app.c -I/usr/include/postgresql -lpq -o app
```

## 参数化查询

```c
// 防止 SQL 注入
PGresult *res = PQexecParams(
    conn,
    "SELECT * FROM users WHERE id = $1 AND status = $2",
    2,                          // 参数个数
    NULL,                       // 参数类型（NULL 让 PG 推断）
    paramValues,                // 参数值
    paramLengths,               // 参数长度
    paramFormats,               // 0 = text, 1 = binary
    0                           // 结果格式
);
```

```c
const char *paramValues[2] = {"123", "active"};
int paramLengths[2] = {3, 6};
int paramFormats[2] = {0, 0};
```

## 异步查询

```c
// 1. 发送
PGresult *res = PQsendQuery(conn, "SELECT pg_sleep(10), now()");
// PQsendQuery 返回 1 表示已发送，立即返回

// 2. 轮询
while (PQisBusy(conn)) {
    // 等待 socket 可读
    int fd = PQsocket(conn);
    fd_set read_fds;
    FD_ZERO(&read_fds);
    FD_SET(fd, &read_fds);
    select(fd + 1, &read_fds, NULL, NULL, NULL);
    
    // 接收数据
    PQconsumeInput(conn);
}

// 3. 获取结果
res = PQgetResult(conn);
```

## COPY 协议

```c
// 1. COPY FROM STDIN
PGresult *res = PQexec(conn, "COPY users (name, email) FROM STDIN");
if (PQresultStatus(res) == PGRES_COPY_IN) {
    // 2. 发送数据
    PQputCopyData(conn, "Alice,[email protected]\n", strlen("Alice,[email protected]\n"));
    PQputCopyData(conn, "Bob,[email protected]\n", strlen("Bob,[email protected]\n"));
    
    // 3. 结束
    PQputCopyEnd(conn, NULL);
    
    // 4. 获取结果
    PGresult *result = PQgetResult(conn);
}

// 100 万行约 5 秒
```

## 事务

```c
// BEGIN
PGresult *res = PQexec(conn, "BEGIN");

// 业务 SQL
PQexec(conn, "INSERT INTO ...");
PQexec(conn, "UPDATE ...");

// COMMIT
res = PQexec(conn, "COMMIT");
```

或用 prepared statement 避免 SQL 注入。

## 大对象（LO）

```c
Oid loid = lo_creat(conn, INV_READ | INV_WRITE);

// 写入
int fd = lo_open(conn, loid, INV_WRITE);
PQlo_export(conn, loid, "/path/to/file");

// 读取
PQlo_import(conn, "/path/to/file");
```

> **现代做法**：用 bytea 字段代替大对象。

## 错误处理

```c
PGresult *res = PQexec(conn, "SELECT bad_col FROM users");

// 状态码
ExecStatusType status = PQresultStatus(res);
switch (status) {
    case PGRES_COMMAND_OK:
        // 非 SELECT 命令成功
        break;
    case PGRES_TUPLES_OK:
        // SELECT 成功
        break;
    case PGRES_FATAL_ERROR:
        // 致命错误
        fprintf(stderr, "%s\n", PQresultErrorMessage(res));
        break;
}
```

## 实战案例

### 案例 1：批量导入 CSV

```c
PGconn *conn = PQconnectdb("host=localhost dbname=mydb");
PGresult *res = PQexec(conn, "COPY users (name, email) FROM STDIN WITH (FORMAT csv)");

FILE *fp = fopen("users.csv", "r");
char buf[8192];

while (fgets(buf, sizeof(buf), fp)) {
    PQputCopyData(conn, buf, strlen(buf));
}

PQputCopyEnd(conn, NULL);
fclose(fp);
PQclear(res);
PQfinish(conn);
```

## 一句话总结

> **libpq = PG 的 C API 基础**：**所有客户端都借鉴它的设计**。**COPY 协议是百万级数据导入的关键**。**实际项目大多用高层封装**（JDBC / psycopg），libpq 主要用于 C/C++ 应用和嵌入式开发。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "09-connection/psycopg.md": """---
title: Psycopg Python 驱动
description: Python 连接 PostgreSQL
---

# Psycopg Python 驱动

> **TL;DR**：Psycopg = PG 最流行的 **Python 驱动**。**Psycopg 3 是新一代**（异步 + 类型注解）。**Django / SQLAlchemy / pandas** 都用它。

## 一句话定义

```
Psycopg = Python 连接 PG 的标准库
        = 同步（psycopg2 / psycopg 3 sync）
        = 异步（psycopg 3 async）
```

## 安装

```bash
# Psycopg 3（推荐）
pip install psycopg[binary,pool]

# Psycopg 2（旧版兼容）
pip install psycopg2-binary
```

## 基本使用

### Psycopg 3（推荐）

```python
import psycopg

# 1. 连接
conn = psycopg.connect(
    "host=localhost dbname=mydb user=postgres password=xxx"
)

# 2. 自动提交模式
conn = psycopg.connect("...", autocommit=True)

# 3. 简单查询
with conn.cursor() as cur:
    cur.execute("SELECT version()")
    row = cur.fetchone()
    print(row[0])

# 4. 参数化查询（防 SQL 注入）
with conn.cursor() as cur:
    cur.execute(
        "SELECT * FROM users WHERE id = %s",
        (123,)
    )
    rows = cur.fetchall()

# 5. 上下文管理（自动关闭）
with psycopg.connect("...") as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT 1")
        print(cur.fetchone())

# 6. 事务
with psycopg.connect("...") as conn:
    with conn.transaction():
        cur = conn.cursor()
        cur.execute("INSERT INTO users ...")
        cur.execute("UPDATE ...")
```

### DictCursor

```python
import psycopg
from psycopg.rows import dict_row

with psycopg.connect("...") as conn:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("SELECT id, name FROM users")
        for row in cur:
            print(row['name'])  # 直接按字段名访问
```

## 连接池

```python
from psycopg_pool import ConnectionPool

# 1. 创建连接池
pool = ConnectionPool(
    "host=localhost dbname=mydb user=postgres password=xxx",
    min_size=2,
    max_size=20,
    timeout=30
)

# 2. 使用
with pool.connection() as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM users WHERE id = %s", (123,))
        row = cur.fetchone()

# 3. 关闭池
pool.close()
```

## 异步

```python
import psycopg
import asyncio

async def main():
    # 异步连接
    conn = await psycopg.AsyncConnection.connect(
        "host=localhost dbname=mydb user=postgres password=xxx"
    )
    
    async with conn.cursor() as cur:
        await cur.execute("SELECT * FROM users WHERE id = %s", (123,))
        row = await cur.fetchone()
        print(row)
    
    await conn.close()

asyncio.run(main())
```

## COPY 协议（最快）

```python
import psycopg

with psycopg.connect("...") as conn:
    with conn.cursor() as cur:
        # 1. 准备 COPY
        with cur.copy("COPY users (name, email) FROM STDIN") as copy:
            # 2. 写入数据
            for user in users:
                copy.write_row((user.name, user.email))
        
        # 100 万行约 5 秒
```

## 类型适配

```python
from psycopg.types.json import Jsonb
from datetime import datetime

with psycopg.connect("...") as conn:
    with conn.cursor() as cur:
        # JSONB
        cur.execute(
            "INSERT INTO events (data) VALUES (%s)",
            (Jsonb({"key": "value"}),)
        )
        
        # datetime
        cur.execute(
            "INSERT INTO events (ts) VALUES (%s)",
            (datetime.now(),)
        )
        
        # UUID
        import uuid
        cur.execute(
            "INSERT INTO users (id) VALUES (%s)",
            (uuid.uuid4(),)
        )
```

## SQLAlchemy 集成

```python
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg://user:pass@host/dbname")

with engine.connect() as conn:
    result = conn.execute("SELECT * FROM users")
    for row in result:
        print(row)
```

## Django 集成

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mydb',
        'USER': 'postgres',
        'PASSWORD': 'xxx',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}
```

## 常见错误

### 1. 连接超时

```python
# 增加 timeout
conn = psycopg.connect("... connect_timeout=10 ...")
```

### 2. SSL 配置

```python
# 强制 SSL
conn = psycopg.connect("... sslmode=require ...")

# 自签证书
conn = psycopg.connect("... sslmode=verify-full sslrootcert=/path/to/ca.crt ...")
```

### 3. 编码问题

```python
# 强制 UTF-8
conn = psycopg.connect("...", client_encoding="UTF8")
```

## 实战案例

### 案例 1：批量导入 100 万行

```python
import psycopg
from psycopg_pool import ConnectionPool

pool = ConnectionPool("...", max_size=5)

users = [(f"user{i}", f"user{i}@example.com") for i in range(1000000)]

with pool.connection() as conn:
    with conn.cursor() as cur:
        with cur.copy("COPY users (name, email) FROM STDIN") as copy:
            for user in users:
                copy.write_row(user)
# 100 万行约 10 秒
```

### 案例 2：流式查询大表

```python
with psycopg.connect("...") as conn:
    with conn.cursor(name="streaming_cursor") as cur:  # 服务端游标
        cur.execute("SELECT * FROM huge_table")
        while True:
            rows = cur.fetchmany(1000)
            if not rows:
                break
            for row in rows:
                process(row)
```

## 一句话总结

> **Psycopg 3 = Python 连接 PG 的现代标准**：**同步 + 异步 + 类型注解 + 连接池**。**COPY 协议批量导入 100 万行 10 秒**。**Django / SQLAlchemy / pandas** 都基于它。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "10-extensions/citus.md": """---
title: Citus 分布式
description: PG 水平扩展方案
---

# Citus 分布式

> **TL;DR**：Citus = PG 的**水平分片扩展**。**10 亿行表拆到 N 个 worker 节点**，**查询自动并行**。**适用**：实时分析、SaaS 多租户、IoT 时序。

## 一句话定义

```
Citus = PG 的分片扩展
     = 1 个协调节点（coordinator）+ N 个工作节点（worker）
     = 自动分片、并行查询
```

## 适用场景

```
✓ SaaS 多租户（每租户独立分片）
✓ 实时分析（千万级实时聚合）
✓ IoT 时序数据
✓ 大表（> 1 亿行）
✓ 高 QPS（> 10 万 QPS）

✗ 强 OLTP（事务一致性受限）
✗ 跨节点 JOIN（性能差）
```

## 安装

```bash
# Ubuntu/Debian
apt install postgresql-15-citus

# 或从源码
# https://github.com/citusdata/citus
```

```sql
-- 所有节点启用扩展
CREATE EXTENSION citus;
```

## 集群部署

```
节点：
  - coordinator（1 个）：接收查询、分发
  - worker（N 个）：存储数据、执行子查询

端口：
  - coordinator: 5432
  - worker: 5432（不同机器）

最小配置：1 coordinator + 2 workers（生产推荐）
```

```sql
-- 1. coordinator 上加 worker 节点
SELECT citus_add_node('worker1.db', 5432);
SELECT citus_add_node('worker2.db', 5432);

-- 2. 看节点列表
SELECT * FROM citus_get_active_worker_nodes();

-- 3. 看集群健康
SELECT * FROM citus_check_cluster_health();
```

## 创建分布式表

```sql
-- 1. 选分布列（高基数 / 高频 JOIN 列）
--    user_id / tenant_id / sensor_id

-- 2. 分布表
SELECT create_distributed_table('events', 'user_id');
-- 自动按 user_id hash 分布到 worker 节点
```

**分布列选择**：

```
✓ user_id（高基数，每行不同）
✓ tenant_id（多租户）
✗ status（低基数，所有行分布不均）
✗ created_at（数据倾斜，老数据集中）
```

## 表类型

### 1. 分布式表

```sql
SELECT create_distributed_table('events', 'user_id');
-- 数据分布到所有 worker
```

### 2. 引用表（Reference Table）

```sql
SELECT create_reference_table('countries');
-- 每个 worker 都有完整副本（小表，用于 JOIN）
```

### 3. 本地表（Local Table）

```sql
-- 只在 coordinator（不分布）
-- 用于管理数据
```

## 实战案例

### 案例 1：SaaS 多租户

```sql
-- 用户表（参考表）
CREATE TABLE tenants (
  id BIGINT PRIMARY KEY,
  name TEXT
);
SELECT create_reference_table('tenants');

-- 订单表（按 tenant_id 分布）
CREATE TABLE orders (
  id BIGSERIAL,
  tenant_id BIGINT NOT NULL,
  amount NUMERIC(10,2),
  created_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (id, tenant_id)
);
SELECT create_distributed_table('orders', 'tenant_id');

-- 索引自动在每个 worker 上创建
CREATE INDEX idx_orders_tenant_created ON orders (tenant_id, created_at);

-- 查询
-- 自动推到对应 worker（shard pruning）
SELECT * FROM orders WHERE tenant_id = 123;
```

### 案例 2：实时分析

```sql
CREATE TABLE events (
  id BIGSERIAL,
  user_id BIGINT,
  event_type TEXT,
  ts TIMESTAMPTZ DEFAULT now()
);
SELECT create_distributed_table('events', 'user_id');

-- 实时聚合（推到 worker 并行执行）
SELECT
  date_trunc('hour', ts) AS hour,
  count(*) AS cnt
FROM events
WHERE ts >= now() - interval '1 day'
GROUP BY hour;
```

### 案例 3：迁移单 PG 到 Citus

```sql
-- 1. 单 PG 实例（已有大表）
-- 2. 部署 Citus 集群
-- 3. 在线迁移
--    a. create_distributed_table（自动分布）
--    b. 数据自动迁移到 worker
--    c. 切换应用到 coordinator
```

## 性能优化

```sql
-- 1. 选好分布列（最重要）
--    避免热点 user_id

-- 2. 用 co-location（关联表用同一分布列）
SELECT create_distributed_table('users', 'user_id');
SELECT create_distributed_table('orders', 'user_id');
-- JOIN 不跨节点

-- 3. 用 reference table（小表）
SELECT create_reference_table('products');

-- 4. 分区大表（组合 Citus + 时间分区）
SELECT create_distributed_table('events', 'user_id');
-- events 按 user_id 分布，按 ts 分区
```

## 监控

```sql
-- 1. 节点状态
SELECT * FROM citus_get_active_worker_nodes();

-- 2. 表分布信息
SELECT
  logical_relid,
  partmethod,
  partkey
FROM pg_dist_partition;

-- 3. 分片位置
SELECT
  shardid,
  shardstate,
  nodename,
  nodeport,
  size
FROM pg_dist_shard_placement
JOIN pg_dist_shard USING (shardid)
LIMIT 10;

-- 4. 集群健康
SELECT * FROM citus_check_cluster_health();
```

## 限制

```
✗ 不支持跨节点事务（Citus 10 之前）
✗ 不支持 cross-shard JOIN（除非 colocation）
✗ 不支持视图（PG 视图可以，但 Citus 不优化）
✗ 节点增减需要 rebalance
```

## 一句话总结

> **Citus = PG 水平扩展方案**：**多租户、实时分析、大表**首选。**colocation（同分布列）让 JOIN 不跨节点**。**生产推荐 1 coordinator + 4-8 workers + sh 2**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "10-extensions/pg_trgm.md": """---
title: pg_trgm 模糊匹配
description: 三元组相似度
---

# pg_trgm 模糊匹配

> **TL;DR**：pg_trgm = **三元组相似度**扩展。**支持 `LIKE '%xxx%'` 模糊匹配 + 拼写错误容忍 + 相似度排序**。**配 GIN 索引后搜索性能从 5s 降到 5ms**。

## 一句话定义

```
pg_trgm = 把字符串拆成 3 字符片段（trigrams）
        = 计算相似度（共享 trigram 数）
        = GIN 索引加速模糊匹配
```

## 三元组原理

```sql
-- 字符串拆成 3 字符片段
SELECT show_trgm('hello');
-- {'  h',' he','hel','ell','llo','lo '}
```

**相似度计算**：

```
两个字符串的 trigrams 集合相似度 = 共享 trigrams / 总 trigrams
```

## 基本使用

```sql
-- 1. 安装
CREATE EXTENSION pg_trgm;

-- 2. 相似度函数
SELECT similarity('hello', 'helo');    -- 0.4（拼错一个字符）
SELECT similarity('hello', 'world');    -- 0.0（完全不同）
SELECT similarity('PostgreSQL', 'Postgres');  -- 0.5

-- 3. 阈值
SELECT set_limit(0.3);  -- 相似度 > 0.3 算匹配
```

## 实战案例

### 案例 1：模糊搜索

```sql
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  name TEXT
);

CREATE INDEX idx_products_name ON products USING GIN (name gin_trgm_ops);

-- 1. 模糊匹配
SELECT * FROM products 
WHERE name % 'Postgres'  -- % = similarity > threshold
LIMIT 10;

-- 2. 相似度排序
SELECT *, similarity(name, 'Postgres') AS sim
FROM products
WHERE name % 'Postgres'
ORDER BY sim DESC
LIMIT 10;

-- 3. 拼写错误容忍（"Postgres" vs "Postgress"）
SELECT * FROM products 
WHERE name % 'Postgress';
-- 能匹配 "Postgres"（相似度 0.66 > 0.3）
```

### 案例 2：邮箱校验（防拼写错误）

```sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email TEXT
);

CREATE INDEX idx_users_email ON users USING GIN (email gin_trgm_ops);

-- 注册时检查相似邮箱（防 "alice@gmial.com" 注册了但 "alice@gmail.com" 已存在）
SELECT email, similarity(email, '[email protected]') AS sim
FROM users
WHERE email % '[email protected]'
ORDER BY sim DESC
LIMIT 5;
```

### 案例 3：搜索建议

```sql
-- 用户输入 "ipone"，推荐 "iPhone"
CREATE EXTENSION pg_trgm;

CREATE TABLE products (name TEXT);
CREATE INDEX idx_products_name ON products USING GIN (name gin_trgm_ops);

-- 推荐最相似
SELECT name, similarity(name, 'ipone') AS sim
FROM products
WHERE name % 'ipone'
ORDER BY sim DESC
LIMIT 5;
-- iPhone, iPhone 15, iPad, ...
```

## 操作符

| 操作符 | 含义 | 例子 |
|---|---|---|
| `%` | similarity > threshold | `name % 'Postgres'` |
| `<%` | similarity < threshold | `name <% 'Postgres'` |
| `%>` | 1 包含 2 | `'Postgres' %> name` |
| `<%>` | 距离（1 - similarity） | `name <%> 'Postgres'` |
| `<<%` | 1 相似 2（按字面量） | `name <<% 'Postgres'` |
| `%>>` | 2 相似 1（按字面量） | `name %>> 'Postgres'` |
| `~` | 正则 | `name ~ '^Post'` |

## 性能优化

```sql
-- 1. 阈值调优
SELECT set_limit(0.4);  -- 更严格
SELECT set_limit(0.2);  -- 更宽松

-- 2. GiST vs GIN
CREATE INDEX idx_name ON products USING GIN (name gin_trgm_ops);
-- GIN：适合读多写少
-- GiST：适合写多读少
CREATE INDEX idx_name ON products USING GIST (name gist_trgm_ops);

-- 3. word_similarity（词级，比 trigram 快）
SELECT word_similarity('Postgres', 'PostgreSQL');
-- 1.0（Postgres 是 PostgreSQL 的子串）
```

## 一句话总结

> **pg_trgm = 模糊搜索利器**：**`%` 操作符 + GIN 索引 = LIKE 模糊匹配提速 1000x**。**搜索建议、邮箱校验、拼写容忍**全靠它。**阈值默认 0.3**，**按需调整**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",

    "10-extensions/timescaledb.md": """---
title: TimescaleDB 时序扩展
description: PG 时序数据库
---

# TimescaleDB 时序扩展

> **TL;DR**：TimescaleDB = PG 的**时序数据库扩展**。**自动分区 + 列式压缩 + 保留策略 + 连续聚合**，**单 PG 实例支持 100 亿行时序数据**。

## 一句话定义

```
TimescaleDB = PG 时序扩展
            = 超表（hypertable）+ chunk（按时间/空间分区）
            = 自动管理、查询语法不变
```

## 与原生分区的对比

| 维度 | 原生分区 | TimescaleDB |
|---|---|---|
| 自动创建分区 | ✗ | ✓ |
| 自动压缩 | ✗ | ✓ |
| 自动保留 | ✗ | ✓ |
| 连续聚合 | ✗ | ✓ |
| 分布式 | ✗ | ✓（多节点） |
| SQL 兼容 | ✓ | ✓ |

## 安装

```bash
# Ubuntu
apt install timescaledb-2-postgresql-15

# 配置
echo "shared_preload_libraries = 'timescaledb'" >> /etc/postgresql/15/main/postgresql.conf
```

```sql
CREATE EXTENSION timescaledb;
```

## 超表（Hypertable）

```sql
-- 1. 创普通表
CREATE TABLE metrics (
  ts TIMESTAMPTZ NOT NULL,
  sensor_id INT NOT NULL,
  cpu NUMERIC(5,2),
  mem NUMERIC(5,2)
);

-- 2. 转超表（按时间分区）
SELECT create_hypertable('metrics', 'ts');

-- 3. 插入数据（应用无感知）
INSERT INTO metrics (ts, sensor_id, cpu, mem) VALUES
  (now(), 1, 80.5, 60.2),
  (now() - interval '1 hour', 1, 75.3, 58.1);
```

## 自动分区

TimescaleDB 自动按时间创建 chunk：

```
metrics chunk:
  - chunk_2026_08_01 (1 天)
  - chunk_2026_08_02
  - chunk_2026_08_03
  ...
默认 chunk_time_interval = 7 days
```

**调整 chunk 大小**：

```sql
SELECT set_chunk_time_interval('metrics', INTERVAL '1 day');
-- 1 天一个 chunk（小数据量）
-- 1 周一个 chunk（大数据量）
```

## 压缩

```sql
-- 1. 启用压缩（按时间降序）
ALTER TABLE metrics SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'sensor_id',
  timescaledb.compress_orderby = 'ts DESC'
);

-- 2. 手动压缩
SELECT compress_chunk(c) FROM show_chunks('metrics') c;

-- 3. 自动压缩策略
SELECT add_compression_policy('metrics', INTERVAL '7 days');
-- 7 天前的 chunk 自动压缩
```

**压缩效果**：

```
压缩前：100 GB
压缩后：5-10 GB（10-20x 压缩）
查询性能：基本不变（列存）
```

## 保留策略

```sql
-- 自动删除 N 天前的数据
SELECT add_retention_policy('metrics', INTERVAL '90 days');
-- 90 天前的 chunk 自动删除
```

## 连续聚合（Continuous Aggregate）

```sql
-- 1. 创建连续聚合
CREATE MATERIALIZED VIEW metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
  time_bucket('1 hour', ts) AS bucket,
  sensor_id,
  avg(cpu) AS avg_cpu,
  max(cpu) AS max_cpu,
  avg(mem) AS avg_mem
FROM metrics
GROUP BY bucket, sensor_id;

-- 2. 自动刷新策略
SELECT add_continuous_aggregate_policy('metrics_hourly',
  start_offset => INTERVAL '1 day',
  end_offset => INTERVAL '1 hour',
  schedule_interval => INTERVAL '1 hour');

-- 3. 查询（实时 + 历史）
SELECT * FROM metrics_hourly
WHERE bucket >= now() - interval '7 days'
ORDER BY bucket DESC;
```

**比 PG 原生物化视图**：

```
✓ 自动刷新（策略）
✓ 历史 chunk + 实时数据
✓ 支持 UPDATE 底层
```

## 实战案例

### 案例 1：监控指标存储

```sql
CREATE TABLE metrics (
  ts TIMESTAMPTZ NOT NULL,
  host TEXT NOT NULL,
  metric TEXT NOT NULL,
  value DOUBLE PRECISION
);

SELECT create_hypertable('metrics', 'ts');

-- 索引
CREATE INDEX idx_metrics_host ON metrics (host, ts DESC);
CREATE INDEX idx_metrics_metric ON metrics (metric, ts DESC);

-- 7 天后压缩
ALTER TABLE metrics SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'host, metric',
  timescaledb.compress_orderby = 'ts DESC'
);
SELECT add_compression_policy('metrics', INTERVAL '7 days');

-- 90 天后删除
SELECT add_retention_policy('metrics', INTERVAL '90 days');
```

### 案例 2：IoT 传感器数据

```sql
CREATE TABLE sensor_data (
  ts TIMESTAMPTZ NOT NULL,
  sensor_id INT NOT NULL,
  temperature NUMERIC(5,2),
  humidity NUMERIC(5,2)
);

-- 按时间和 sensor 分区
SELECT create_hypertable('sensor_data', 'ts', chunk_time_interval => INTERVAL '1 day');

-- 压缩 + 保留
ALTER TABLE sensor_data SET (
  timescaledb.compress,
  timescaledb.compress_segmentby = 'sensor_id',
  timescaledb.compress_orderby = 'ts DESC'
);
SELECT add_compression_policy('sensor_data', INTERVAL '30 days');
SELECT add_retention_policy('sensor_data', INTERVAL '365 days');
```

### 案例 3：金融行情（K线）

```sql
CREATE TABLE stock_prices (
  ts TIMESTAMPTZ NOT NULL,
  symbol TEXT NOT NULL,
  open NUMERIC(10,4),
  high NUMERIC(10,4),
  low NUMERIC(10,4),
  close NUMERIC(10,4),
  volume BIGINT
);

SELECT create_hypertable('stock_prices', 'ts');

-- 连续聚合生成 K 线
CREATE MATERIALIZED VIEW stock_klines_1min
WITH (timescaledb.continuous) AS
SELECT
  time_bucket('1 minute', ts) AS bucket,
  symbol,
  first(open, ts) AS open,
  max(high) AS high,
  min(low) AS low,
  last(close, ts) AS close,
  sum(volume) AS volume
FROM stock_prices
GROUP BY bucket, symbol;
```

## 监控

```sql
-- 1. 超表信息
SELECT * FROM timescaledb_information.hypertables;

-- 2. chunk 列表
SELECT * FROM timescaledb_information.chunks
WHERE hypertable_name = 'metrics';

-- 3. 压缩统计
SELECT * FROM timescaledb_information.compressed_chunk_stats;

-- 4. 策略
SELECT * FROM timescaledb_information.jobs
WHERE application_name LIKE '%Compression%'
   OR application_name LIKE '%Retention%';
```

## 分布式（多节点）

```sql
-- 1. 添加 data node
SELECT add_data_node('tsdb1.db', chunk_time_interval => INTERVAL '1 day');
SELECT add_data_node('tsdb2.db', chunk_time_interval => INTERVAL '1 day');

-- 2. 分布式超表
SELECT create_distributed_hypertable('metrics', 'ts');
```

## 一句话总结

> **TimescaleDB = PG 时序数据库**：**自动分区 + 列式压缩 + 保留策略 + 连续聚合**。**100 亿行单实例可扛**。**应用 SQL 零修改**，**只 CREATE EXTENSION + create_hypertable**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
""",
}


def main():
    total = 0
    for rel_path, content in CONTENT.items():
        path = DOCS / rel_path
        path.write_text(content, encoding="utf-8")
        total += 1
        print(f"  {rel_path:50s} {len(content)//1024}KB")
    print(f"\nTotal generated: {total}")

if __name__ == "__main__":
    main()