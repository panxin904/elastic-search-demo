---
title: 数据类型
date: 2026-08-15  # date-auto-injected
description: ClickHouse 完整数据类型系统：基础 / 数值 / 字符串 / 时间 / 复合 / 特殊类型
---

# 数据类型

ClickHouse 的类型系统比 MySQL/PG 更丰富，特别是复合类型（Array / Tuple / Map / Nested）和特殊类型（Enum / LowCardinality / Nullable）。

## 数值类型

| 类型 | 大小 | 范围 | 备注 |
|---|---|---|---|
| **UInt8** | 1 字节 | 0 ~ 255 | 默认 UNSIGNED |
| **UInt16** | 2 字节 | 0 ~ 65535 | |
| **UInt32** | 4 字节 | 0 ~ 4.29e9 | |
| **UInt64** | 8 字节 | 0 ~ 1.84e19 | |
| **Int8** | 1 字节 | -128 ~ 127 | |
| **Int16** | 2 字节 | -32768 ~ 32767 | |
| **Int32** | 4 字节 | -2.15e9 ~ 2.15e9 | |
| **Int64** | 8 字节 | -9.22e18 ~ 9.22e18 | |
| **Float32** | 4 字节 | IEEE 754 单精度 | 不建议存钱 |
| **Float64** | 8 字节 | IEEE 754 双精度 | |
| **Decimal(P, S)** | 4/8/16 字节 | 高精度小数 | P = 精度, S = 小数位数 |

**注意**：
- UInt 比 Int 性能更好（无需符号位处理），业务允许就用 UInt。
- 浮点数比较请用 `>= x - 0.0001 AND <= x + 0.0001`。

## 字符串类型

| 类型 | 说明 |
|---|---|
| **String** | 任意长度字符串（替代 VARCHAR/TEXT/BLOB） |
| **FixedString(N)** | 定长字符串（N 字节，不足补 0） |
| **LowCardinality(String)** | 低基数字符串（字典编码，10x 压缩 + 10x 查询快） |

**LowCardinality 是杀手锏**：列基数 < 1 万时（如 status、country、category），性能比普通 String 提升 10-50x。

```sql
-- 推荐
CREATE TABLE events (
  status LowCardinality(String),
  country LowCardinality(String)
)

-- 不推荐（基数 < 10000 但没用 LowCardinality）
CREATE TABLE events (
  status String,  -- 浪费
  country String
)
```

## 时间类型

| 类型 | 大小 | 范围 | 精度 |
|---|---|---|---|
| **Date** | 2 字节 | 1970-01-01 ~ 2149-06-06 | 天 |
| **Date32** | 4 字节 | 1900-01-01 ~ 2299-12-31 | 天 |
| **DateTime** | 4 字节 | 1970-01-01 ~ 2105-12-31 | 秒（无时区） |
| **DateTime64(P)** | 8 字节 | 1900-01-01 ~ 2299-12-31 | P = 精度（毫秒/微秒/纳秒） |

**注意**：
- `DateTime` 不带时区（按服务器时区存储），多机房部署需要统一时区或使用 `DateTime64(3, 'UTC')`。
- `DateTime64(3)` = 毫秒精度，`DateTime64(6)` = 微秒精度，`DateTime64(9)` = 纳秒精度。

## 布尔类型

ClickHouse **没有 BOOLEAN** 类型，用 `UInt8` 代替（0 = false，1 = true）：

```sql
CREATE TABLE users (
  is_active UInt8 DEFAULT 0,
  is_vip UInt8 DEFAULT 0
)

INSERT INTO users (id, is_active, is_vip) VALUES (1, 1, 0)

SELECT * FROM users WHERE is_active = 1
```

## UUID

```sql
CREATE TABLE events (
  event_id UUID
)

INSERT INTO events VALUES (generateUUIDv4())
```

## 枚举类型

枚举类型底层是 `Int8`/`Int16`，适合固定取值集合：

```sql
CREATE TABLE orders (
  status Enum8('pending' = 1, 'paid' = 2, 'shipped' = 3, 'delivered' = 4, 'cancelled' = 5)
)

INSERT INTO orders (id, status) VALUES (1, 'paid')

-- 按数值排序（实际是 Int8 排序）
SELECT status, count() FROM orders GROUP BY status
```

## 复合类型

### Array

```sql
CREATE TABLE events (
  tags Array(String),
  scores Array(Float64)
)

INSERT INTO events VALUES (['tech', 'ai', 'database'], [9.5, 8.7])

-- 查询数组包含某元素
SELECT * FROM events WHERE has(tags, 'ai')

-- 数组展开（ARRAY JOIN）
SELECT tag FROM events ARRAY JOIN tags AS tag
```

### Tuple

```sql
CREATE TABLE events (
  point Tuple(Float64, Float64)  -- (longitude, latitude)
)

INSERT INTO events VALUES (116.4, 39.9)
```

### Map

```sql
CREATE TABLE events (
  props Map(String, String)
)

INSERT INTO events VALUES ({'browser': 'chrome', 'os': 'mac'})

-- 查询
SELECT props['browser'] FROM events
SELECT * FROM events WHERE props['os'] = 'mac'
```

### Nested（嵌套表）

```sql
CREATE TABLE users (
  id UInt64,
  name String,
  phones Nested(
    type String,
    number String
  )
)

INSERT INTO users VALUES (1, 'Alice', ['mobile', 'work'], ['138...', '010-...'])

SELECT
  name,
  phone.type,
  phone.number
FROM users
ARRAY JOIN phones AS phone
```

## Nullable 类型

`Nullable(T)` 允许 `null` 值，但**会影响性能**（增加额外列 + null bitmap）：

```sql
CREATE TABLE events (
  user_id UInt64,
  -- 不推荐（user_id 应该是必填）
  user_id_nullable Nullable(UInt64)
)
```

**建议**：用业务默认值替代 `Nullable`（如 `0 = 未登录`、`'' = 未填写`）。

## JSON 类型（v24.x 新增）

ClickHouse v24.x 引入 `JSON` 类型，动态子列：

```sql
CREATE TABLE events (
  data JSON
)

INSERT INTO events VALUES ('{"name": "Alice", "age": 25, "tags": ["tech", "ai"]}')

-- 自动推断子列
SELECT
  data.name,
  data.age,
  data.tags
FROM events
```

## Domain 类型（IPv4 / IPv6）

ClickHouse 提供专门的 IP 地址类型：

```sql
CREATE TABLE access_logs (
  ip IPv4
)

INSERT INTO access_logs VALUES ('192.168.1.1')

-- IP 转数字
SELECT ip, IPv4NumToString(ip) FROM access_logs
```

## 类型选择 checklist

| 业务字段 | 推荐类型 | 备注 |
|---|---|---|
| 整数 ID | UInt64 | 主键默认 |
| 状态（有限集合） | Enum8 或 LowCardinality(String) | 二选一 |
| 国家/城市 | LowCardinality(String) | 低基数 |
| 时间戳 | DateTime64(3) 或 DateTime | 视精度需求 |
| 布尔值 | UInt8（0/1） | 不用 Boolean |
| 金额 | Decimal(18, 2) | 不用 Float64 |
| 文本（长） | String | |
| 文本（短/枚举） | LowCardinality(String) | |
| 标签数组 | Array(String) 或 Array(LowCardinality(String)) | |
| KV 数据 | Map(String, String) | 灵活但性能低 |
| JSON 数据 | JSON（v24+）或 String + JSON 函数 | |

## 下一步

- 学习 SQL 聚合：见 [02-sql/select-aggregate.md](../02-sql/select-aggregate.md)
