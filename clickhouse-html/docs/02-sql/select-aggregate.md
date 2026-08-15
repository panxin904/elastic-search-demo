---
title: SELECT 与聚合查询
description: ClickHouse 聚合函数全集 + TOP 20 / 分位数 / 高基数 UV 实战
---

# SELECT 与聚合查询

## 基础查询

```sql
SELECT
  user_id,
  count() AS event_count,
  min(event_time) AS first_event,
  max(event_time) AS last_event
FROM events
WHERE event_date = '2024-01-01'
GROUP BY user_id
HAVING event_count > 10
ORDER BY event_count DESC
LIMIT 100
```

## 聚合函数全集

### 计数类

```sql
SELECT
  count(),                      -- 总行数
  countIf(event_type = 'click'), -- 条件计数
  countDistinct(user_id),        -- 不同值数量
  uniq(user_id),                 -- 近似不同值（HyperLogLog，1.6% 误差）
  uniqExact(user_id),            -- 精确不同值
  uniqCombined(user_id),         -- 混合（精度+性能）
  uniqCombined64(URL)            -- 64 位（支持更大基数）
FROM events
```

**性能排序**：`uniq` > `uniqCombined` > `uniqExact` > `countDistinct`，精度相反。

### 求和 / 均值 / 极值

```sql
SELECT
  sum(amount),
  avg(amount),
  min(amount),
  max(amount),
  any(amount),         -- 任一非 0 值
  anyLast(amount),     -- 最后一个值
  argMax(user_id, amount),  -- amount 最大时的 user_id
  argMin(user_id, amount)
FROM orders
```

### 分位数（中位数 / P95 / P99）

```sql
SELECT
  quantile(0.5)(latency_ms),           -- 中位数
  quantile(0.95)(latency_ms),          -- P95
  quantile(0.99)(latency_ms),          -- P99
  quantiles(0.5, 0.9, 0.95, 0.99)(latency_ms),  -- 多分位
  quantileExact(0.5)(latency_ms),      -- 精确
  quantileTiming(0.95)(latency_ms)     -- 时间类专用
FROM events
```

## TOP N 查询（高频）

```sql
-- TOP 10 用户（按事件数）
SELECT user_id, count() AS cnt
FROM events
GROUP BY user_id
ORDER BY cnt DESC
LIMIT 10

-- 使用 view 函数优化
SELECT * FROM (
  SELECT user_id, count() AS cnt
  FROM events
  GROUP BY user_id
)
WHERE cnt > 100
ORDER BY cnt DESC
LIMIT 10
```

**TOP N 优化**：用 `topK(N)` 函数一次性返回前 N 个：

```sql
SELECT topK(10)(user_id), topK(10)(country) FROM events
```

## 高基数 UV 统计（杀手锏）

### 方法 1：`uniq`（HyperLogLog，1.6% 误差）

```sql
SELECT uniq(user_id) AS uv FROM events WHERE event_date = '2024-01-01'
-- 性能：1 亿行 < 100ms
```

### 方法 2：`groupBitmapState` + RoaringBitmap（精确 + 性能）

```sql
-- 创建物化视图
CREATE MATERIALIZED VIEW events_uv_mv
ENGINE = AggregatingMergeTree()
ORDER BY (event_date, event_type)
AS SELECT
  event_date,
  event_type,
  groupBitmapState(user_id) AS uv_bitmap
FROM events
GROUP BY event_date, event_type;

-- 查询 UV
SELECT
  event_date,
  event_type,
  bitmapCardinality(groupBitmapMergeState(uv_bitmap)) AS uv
FROM events_uv_mv
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-07'
GROUP BY event_date, event_type
ORDER BY event_date, event_type

-- 10 亿行 UV 查询 < 1s（精确）
```

## 实战：电商订单分析

```sql
-- GMV / 订单数 / 客单价
SELECT
  toDate(order_time) AS dt,
  count() AS order_count,
  uniq(user_id) AS buyer_count,
  sum(amount) AS gmv,
  sum(amount) / count() AS avg_order_value
FROM orders
WHERE order_time >= today() - INTERVAL 30 DAY
GROUP BY dt

-- 各品类 TOP 10
SELECT
  category,
  sum(amount) AS cat_gmv,
  count() AS cat_orders
FROM orders o
JOIN products p ON o.product_id = p.id
WHERE order_time >= today() - INTERVAL 7 DAY
GROUP BY category
ORDER BY cat_gmv DESC
LIMIT 10

-- 用户复购率（购买 ≥ 2 次的用户占比）
SELECT
  countIf(order_count >= 2) / count() AS repurchase_rate
FROM (
  SELECT user_id, count() AS order_count
  FROM orders
  WHERE order_time >= today() - INTERVAL 30 DAY
  GROUP BY user_id
)
```

## GROUP BY 优化

### 内存限制

ClickHouse 默认 `max_bytes_before_external_group_by = 0`（OOM 风险），**强烈建议设置**：

```xml
<max_bytes_before_external_group_by>10000000000</max_bytes_before_external_group_by>  <!-- 10 GB -->
<max_memory_usage>50000000000</max_memory_usage>  <!-- 50 GB -->
```

超过限制时自动 spill 到磁盘（性能下降但避免 OOM）。

### 特殊聚合

```sql
-- groupArray（聚合为数组）
SELECT groupArray(user_id) FROM events WHERE event_date = '2024-01-01'

-- groupUniqArray（去重数组）
SELECT groupUniqArray(10)(user_id) FROM events

-- groupArraySample（采样数组）
SELECT groupArraySample(1000)(user_id) FROM events
```

## SAMPLE 抽样

```sql
-- 1% 抽样（快速近似查询）
SELECT count() FROM events SAMPLE 0.01

-- 按 token 抽样（可重现抽样）
SELECT count() FROM events SAMPLE 1/10

-- 必须先在表中配置采样键
CREATE TABLE events (
  event_date Date,
  user_id UInt64,
  event_type String
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (user_id, event_type)
SAMPLE BY user_id  -- 采样键必须是 ORDER BY 前缀
```

## 下一步

- 学习 JOIN 类型：见 [join.md](./join.md)
- 学习窗口函数：见 [window-functions.md](./window-functions.md)
