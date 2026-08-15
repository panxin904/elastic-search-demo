---
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
