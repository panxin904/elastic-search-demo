---
title: Dictionary 字典
description: ClickHouse Dictionary 完整指南：原理 / 创建 / 维护 / 实战
---

# Dictionary 字典

Dictionary 是 ClickHouse 的核心特性，本质是**内存中的本地 Map**，提供毫秒级 KV 查询。

## 原理

```text
┌──────────────────┐
│  External Source │  MySQL / PostgreSQL / ClickHouse / MongoDB / Redis / HTTP
└──────────────────┘
         │
         │ 定期拉取（lifetime）
         ▼
┌──────────────────┐
│  ClickHouse      │
│  Dictionary      │  内存中，按 primary key 索引
│  (HASHED/FLAT)   │  分布在所有节点的本地内存
└──────────────────┘
         ▲
         │ dictGet()
         │
┌──────────────────┐
│  SELECT 查询      │
└──────────────────┘
```

**核心特性**：
- 内存存储：每节点保存全量字典（适合百万级数据）
- 定期更新：按 `LIFETIME` 自动刷新
- 多种数据源：MySQL / PG / ClickHouse / Redis / MongoDB / HTTP / 文件
- 多种布局：`HASHED` / `FLAT` / `CACHE` / `COMPLEX_KEY_HASHED`

## 创建字典

### 从 MySQL 加载

```sql
CREATE DICTIONARY users_dict (
  id UInt64,
  user_name String,
  country String DEFAULT 'unknown',
  age UInt8 DEFAULT 0,
  vip_level UInt8 DEFAULT 0
)
PRIMARY KEY id
SOURCE(MYSQL(
  HOST 'mysql-host'
  PORT 3306
  USER 'readonly'
  PASSWORD 'xxx'
  DB 'production'
  TABLE 'users'
))
LIFETIME(MIN 300 MAX 600)  -- 5-10 分钟更新一次
LAYOUT(HASHED())
```

### 从 ClickHouse 加载

```sql
CREATE DICTIONARY users_dict (
  id UInt64,
  user_name String,
  country String
)
PRIMARY KEY id
SOURCE(CLICKHOUSE(
  DB 'mydb'
  TABLE 'users'
  USER 'default'
  PASSWORD ''
))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED())
```

### 从 Redis 加载

```sql
CREATE DICTIONARY user_meta_dict (
  user_id UInt64,
  meta String
)
PRIMARY KEY user_id
SOURCE(REDIS(
  HOST 'redis-host'
  PORT 6379
  STORAGE_TYPE 'hashmap'
))
LIFETIME(MIN 60 MAX 300)
LAYOUT(COMPLEX_KEY_HASHED())
```

### 从文件加载

```sql
-- TSV 文件
CREATE DICTIONARY country_dict (
  country_code String,
  country_name String
)
PRIMARY KEY country_code
SOURCE(FILE(PATH '/opt/dictionaries/country.tsv' FORMAT 'TabSeparated'))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED())

-- /opt/dictionaries/country.tsv 内容：
-- CN	China
-- US	United States
-- JP	Japan
```

## 字典布局（LAYOUT）

| Layout | 内存 | 性能 | 适用 |
|---|---|---|---|
| **FLAT** | 最少 | 快 | 大字典（百万级），顺序读 |
| **HASHED** | 中 | 快 | 默认选项，KV 查询 |
| **HASHED_ARRAY** | 中 | 快 | 多 key |
| **COMPLEX_KEY_HASHED** | 中 | 快 | 复合主键 |
| **SPARSE_HASHED** | 较少 | 中 | 大字典（千万级） |
| **CACHE** | 极少 | 中 | 远程字典，本地缓存 |
| **SSD_CACHE** | 极少 | 中 | 超大字典 + 本地 SSD |

## 查询字典

### `dictGet`（核心函数）

```sql
-- 基础查询
SELECT
  event_id,
  dictGet('users_dict', 'user_name', user_id) AS user_name,
  dictGet('users_dict', 'country', user_id) AS country
FROM events
WHERE event_date = '2024-01-01'

-- 带默认值
SELECT
  dictGet('users_dict', 'user_name', user_id, 'unknown') AS user_name

-- 多字段查询
SELECT
  dictGet('users_dict', ('user_name', 'country'), user_id) AS fields
```

### `dictHas`（检查存在）

```sql
SELECT
  countIf(dictHas('users_dict', user_id)) AS known_users,
  countIf(NOT dictHas('users_dict', user_id)) AS unknown_users
FROM events
WHERE event_date = '2024-01-01'
```

## 字典维护

### 手动更新

```sql
SYSTEM RELOAD DICTIONARY users_dict
```

### 监控字典状态

```sql
SELECT * FROM system.dictionaries FORMAT Vertical

-- 关键字段
name: users_dict
status: LOADED
element_count: 1000000
bytes_allocated: 52428800
last_successful_update_time: 2024-01-15 12:00:00
```

## 实战：用户画像补全

```sql
-- 创建字典（从 MySQL）
CREATE DICTIONARY user_profile_dict (
  user_id UInt64,
  user_name String,
  country LowCardinality(String),
  age UInt8,
  gender LowCardinality(String),
  vip_level UInt8,
  register_date Date
)
PRIMARY KEY user_id
SOURCE(MYSQL(...))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED())

-- 查询时补全
SELECT
  e.event_id,
  e.event_type,
  dictGet('user_profile_dict', 'user_name', e.user_id) AS user_name,
  dictGet('user_profile_dict', 'country', e.user_id) AS country,
  dictGet('user_profile_dict', 'age', e.user_id) AS age,
  e.amount
FROM events e
WHERE e.event_date >= today() - INTERVAL 7 DAY
LIMIT 1000
```

## 实战：商品维度补全

```sql
CREATE DICTIONARY products_dict (
  product_id UInt64,
  product_name String,
  category LowCardinality(String),
  brand String,
  price Decimal(18, 2)
)
PRIMARY KEY product_id
SOURCE(CLICKHOUSE(DB 'mydb' TABLE 'products'))
LIFETIME(MIN 600 MAX 1800)
LAYOUT(HASHED())

-- 订单分析
SELECT
  o.order_id,
  dictGet('products_dict', 'product_name', o.product_id) AS product_name,
  dictGet('products_dict', 'category', o.product_id) AS category,
  o.amount
FROM orders o
WHERE o.order_date >= today() - INTERVAL 30 DAY
```

## 字典 vs JOIN 性能对比

| 维度 | Dictionary | JOIN |
|---|---|---|
| 性能（10 亿行 × 百万字典） | 100ms | 30s |
| 内存占用 | 每节点 N GB（字典大小） | 0 |
| 实时性 | 有延迟（LIFETIME） | 实时 |
| 适用场景 | 维度表（百万级） | 大表 JOIN |

**经验法则**：维度表 < 1000 万行 → Dictionary；否则 → JOIN。

## 下一步

- 学习表引擎：见 [03-table-engine/overview.md](../03-table-engine/overview.md)
