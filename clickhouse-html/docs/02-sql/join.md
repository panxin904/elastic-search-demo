---
title: JOIN 类型
description: ClickHouse 各种 JOIN 类型 + ASOF JOIN 实战 + JOIN 性能优化
---

# JOIN 类型

ClickHouse 支持的 JOIN 类型比 MySQL 少，但每种都有明确适用场景。

## JOIN 类型清单

```sql
SELECT
  a.*,
  b.user_name
FROM events a
[INNER | LEFT | RIGHT | FULL | CROSS | ASOF] JOIN users b
ON a.user_id = b.id
[ANY | ALL | SEMI | ANTI]  -- JOIN 策略
[JOIN STRICTNESS]            -- 严格度
```

### JOIN 策略

| 策略 | 说明 |
|---|---|
| **ALL** | 默认，返回所有匹配（行数 = 左 × 匹配右） |
| **ANY** | 左表的每一行最多匹配右表一行（取首个匹配） |
| **ASOF** | 最近匹配（时间序列模糊匹配） |
| **SEMI** | 左半连接，右表去重 |
| **ANTI** | 左反连接，右表没匹配才返回 |

### JOIN 严格度

| 严格度 | 说明 |
|---|---|
| `ALL` | 默认 |
| `ANY` | 与 `ANY JOIN` 语义重叠 |

## INNER JOIN

```sql
-- 事件关联用户
SELECT
  e.event_id,
  e.event_type,
  u.user_name,
  u.country
FROM events e
INNER JOIN users u ON e.user_id = u.id
WHERE e.event_date = '2024-01-01'
```

## LEFT JOIN

```sql
-- 找出没有下单的用户
SELECT
  u.id,
  u.user_name
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE o.id = 0  -- 注意：ClickHouse 中 0 是默认"无匹配"
```

## ASOF JOIN（时间序列模糊匹配）

**场景**：股票 K 线匹配成交、订单匹配价格快照、用户行为匹配最近的画像。

```sql
-- 订单成交价匹配当时的行情快照
SELECT
  o.order_id,
  o.symbol,
  o.price AS order_price,
  q.bid_price AS market_bid,
  q.ask_price AS market_ask
FROM orders o
ASOF JOIN quotes q
  ON o.symbol = q.symbol
  AND o.order_time >= q.quote_time  -- 必须有不等式条件
WHERE o.order_time >= '2024-01-01 00:00:00'
```

**ASOF JOIN 规则**：
- 必须有等值条件（`=`）和不等值条件（`>=` 或 `<=`）
- 右表是「时序表」，左表是「事件表」
- 匹配右表中**最后一个**满足不等值条件的行

## SEMI / ANTI JOIN

```sql
-- SEMI：找在 users 表中存在的事件（去重）
SELECT e.* FROM events e
SEMI JOIN users u ON e.user_id = u.id

-- ANTI：找不在 users 表中的事件（异常数据）
SELECT e.* FROM events e
ANTI JOIN users u ON e.user_id = u.id
```

## 字典 JOIN（Dictionary）

Dictionary 是 ClickHouse 的「本地 Map」，比 JOIN 快 10-100x：

```sql
-- 创建字典
CREATE DICTIONARY users_dict (
  id UInt64,
  user_name String,
  country String
)
PRIMARY KEY id
SOURCE(CLICKHOUSE(DB 'mydb' TABLE 'users'))
LIFETIME(MIN 300 MAX 600)
LAYOUT(HASHED())

-- 查询（不需要 JOIN 语法）
SELECT
  event_id,
  dictGet('users_dict', 'user_name', user_id) AS user_name,
  dictGet('users_dict', 'country', user_id) AS country
FROM events
WHERE event_date = '2024-01-01'
```

详见 [dictionary.md](./dictionary.md)。

## JOIN 性能优化

### 1. 大小表 JOIN（小表放右）

```sql
-- ✅ 好：users 是小表（百万级）
SELECT * FROM events JOIN users ON event.user_id = user.id

-- ❌ 差：events 大表 × users 小表，结果集巨大
```

### 2. 限制 JOIN 表数

ClickHouse **JOIN ≤ 8 张表**性能较好，超过会显著退化。如果需要 JOIN 多表，建议：
- 预 JOIN 成宽表（用物化视图）
- 用星型模型（事实表 + 多个维度表）
- 改用 StarRocks / Doris（JOIN 优化更强）

### 3. JOIN 顺序

ClickHouse 的 JOIN 优化器较弱，建议**手动指定顺序**：

```sql
-- 小表在前（手动指定）
SELECT * FROM small_table s JOIN big_table b ON s.id = b.id
```

### 4. 使用 `prewhere`（大幅加速）

```sql
SELECT
  e.event_id,
  u.user_name
FROM events e
PREWHERE e.event_date = '2024-01-01'  -- 先过滤，再 JOIN
JOIN users u ON e.user_id = u.id
```

## 实战：电商订单 + 用户 + 商品三表 JOIN

```sql
-- 订单宽表查询
SELECT
  o.order_id,
  u.user_name,
  u.country,
  p.product_name,
  p.category,
  o.amount,
  o.order_time
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id
WHERE o.order_time >= today() - INTERVAL 7 DAY
  AND u.country IN ('US', 'UK', 'JP')
ORDER BY o.order_time DESC
LIMIT 1000
```

**性能提示**：如果这种查询是热点，用 `JOIN` 物化视图预聚合：

```sql
CREATE MATERIALIZED VIEW order_wide_mv
ENGINE = MergeTree()
PARTITION BY toYYYYMM(order_time)
ORDER BY (order_id, order_time)
AS SELECT
  o.order_id,
  u.user_name,
  u.country,
  p.product_name,
  p.category,
  o.amount,
  o.order_time
FROM orders o
JOIN users u ON o.user_id = u.id
JOIN products p ON o.product_id = p.id
```

## JOIN 类型决策表

| 场景 | 推荐 JOIN 类型 |
|---|---|
| 维度关联（小表） | Dictionary + dictGet |
| 维度关联（大表） | INNER JOIN |
| 时序模糊匹配 | ASOF JOIN |
| 找出异常数据 | ANTI JOIN |
| 找出存在数据 | SEMI JOIN |
| 多维度（> 4 表） | 预 JOIN 物化视图 |

## 下一步

- 学习窗口函数：见 [window-functions.md](./window-functions.md)
