---
title: 高基数 UV 统计
description: RoaringBitmap + groupBitmap 实战：精确 UV / 留存 / 多维去重
---

# 高基数 UV 统计

高基数 UV（亿级用户）是 OLAP 经典难题，本章用 ClickHouse RoaringBitmap 解决。

## UV 统计方案对比

| 方案 | 精度 | 性能 | 内存 | 适用 |
|---|---|---|---|---|
| **countDistinct** | 精确 | 慢（O(N)） | 高 | 小数据（< 千万行） |
| **uniq**（HyperLogLog） | 1.6% 误差 | 快 | 低 | 中等（千万-亿级） |
| **uniqCombined64** | 1.6% 误差 | 快 | 低 | 同上 |
| **groupBitmapState**（RoaringBitmap） | 精确 | 极快 | 中 | 任意规模（推荐） |
| **AggregateFunction** | 精确 | 极快 | 中 | 任意规模（推荐） |

**结论**：高基数精确 UV → RoaringBitmap（`groupBitmapState`）。

## RoaringBitmap 原理

RoaringBitmap 是压缩位图，每个用户 ID 分配一个 bit：

- 用户 100 万 → 第 100 万位 = 1
- 1000 万用户 → 1.25 MB（1000 万 / 8）
- 自带高效合并（OR / AND / XOR）

ClickHouse 内置 RoaringBitmap 实现：

- `groupBitmapState` / `groupBitmapMerge`
- `bitmapCardinality`（计算基数）
- `bitmapAnd` / `bitmapOr` / `bitmapXor`

## 基础 UV 统计

```sql
-- 单次查询 UV（精确）
SELECT bitmapCardinality(groupBitmapState(user_id)) AS uv
FROM events
WHERE event_date = '2024-01-15'

-- 等价（但更慢）
SELECT uniqExact(user_id) FROM events WHERE event_date = '2024-01-15'
```

**性能对比**：
- 1 亿行：`groupBitmapState` ≈ 100ms，`uniqExact` ≈ 30s
- 10 亿行：`groupBitmapState` ≈ 500ms，`uniqExact` OOM

## 物化视图：实时 UV

```sql
-- 1. 源表（明细）
CREATE TABLE events (
  event_time DateTime,
  event_date Date,
  user_id UInt64,
  event_type LowCardinality(String),
  country LowCardinality(String)
)
ENGINE = MergeTree()
PARTITION BY event_date
ORDER BY (event_time, user_id)

-- 2. 物化视图表
CREATE TABLE events_uv_mv_table (
  event_date Date,
  event_type LowCardinality(String),
  country LowCardinality(String),
  uv_bitmap AggregateFunction(groupBitmap, UInt64),
  pv_count AggregateFunction(count)
)
ENGINE = AggregatingMergeTree()
PARTITION BY event_date
ORDER BY (event_date, event_type, country)

-- 3. 物化视图
CREATE MATERIALIZED VIEW events_uv_mv TO events_uv_mv_table AS
SELECT
  event_date,
  event_type,
  country,
  groupBitmapState(user_id) AS uv_bitmap,
  countState() AS pv_count
FROM events
GROUP BY event_date, event_type, country

-- 4. 查询 UV
SELECT
  event_date,
  bitmapCardinality(merge(uv_bitmap)) AS uv,
  sumMerge(pv_count) AS pv
FROM events_uv_mv_table
WHERE event_date BETWEEN '2024-01-01' AND '2024-01-07'
GROUP BY event_date
```

## 多维 UV 组合

```sql
-- UV 按事件类型 + 国家
SELECT
  event_type,
  country,
  bitmapCardinality(merge(uv_bitmap)) AS uv
FROM events_uv_mv_table
WHERE event_date = today()
GROUP BY event_type, country
ORDER BY uv DESC

-- 总 UV（跨事件类型）
SELECT bitmapCardinality(merge(uv_bitmap)) AS total_uv
FROM events_uv_mv_table
WHERE event_date = today()

-- UV 交叉（同时做过 A 和 B 的用户数）
WITH bitmap_a AS (
  SELECT groupBitmapState(user_id) AS uv
  FROM events
  WHERE event_date = today() AND event_type = 'A'
),
bitmap_b AS (
  SELECT groupBitmapState(user_id) AS uv
  FROM events
  WHERE event_date = today() AND event_type = 'B'
)
SELECT bitmapCardinality(bitmapAnd(a.uv, b.uv)) AS uv_a_and_b
FROM bitmap_a a, bitmap_b b
```

## UV 计算口径对比

```sql
-- 口径 1：累计 UV（历史去重）
SELECT bitmapCardinality(groupBitmapState(user_id)) AS total_uv
FROM events

-- 口径 2：当日 UV（按天去重）
SELECT bitmapCardinality(merge(uv_bitmap)) AS today_uv
FROM events_uv_mv_table
WHERE event_date = today()

-- 口径 3：7 日活跃 UV
SELECT bitmapCardinality(merge(uv_bitmap)) AS weekly_uv
FROM events_uv_mv_table
WHERE event_date BETWEEN today() - 6 AND today()

-- 口径 4：当月 UV
SELECT bitmapCardinality(merge(uv_bitmap)) AS monthly_uv
FROM events_uv_mv_table
WHERE event_date BETWEEN toStartOfMonth(today()) AND today()
```

## 实战：D1 / D7 / D30 留存

```sql
-- 留存 bitmap（每个 cohort 的活跃 bitmap）
CREATE TABLE retention_cohort (
  cohort_date Date,
  user_id UInt64,
  active_dates AggregateFunction(groupBitmap, Date)
)
ENGINE = AggregatingMergeTree()
ORDER BY cohort_date

CREATE MATERIALIZED VIEW retention_cohort_mv TO retention_cohort AS
SELECT
  min(event_date) AS cohort_date,
  user_id,
  groupBitmapState(event_date) AS active_dates
FROM events
GROUP BY user_id

-- D1 留存：注册日的用户中，第二天活跃的比例
WITH new_users AS (
  SELECT user_id FROM retention_cohort WHERE cohort_date = '2024-01-15'
)
SELECT
  countIf(d1_active) / count() AS d1_retention,
  countIf(d7_active) / count() AS d7_retention
FROM (
  SELECT
    n.user_id,
    bitmapContains(merge(r.active_dates), toDate('2024-01-16')) AS d1_active,
    bitmapContains(merge(r.active_dates), toDate('2024-01-22')) AS d7_active
  FROM new_users n
  JOIN retention_cohort r ON n.user_id = r.user_id
  WHERE r.cohort_date = '2024-01-15'
  GROUP BY n.user_id
)
```

## 性能基准

```text
数据量：       10 亿事件
UV（精确）：    500ms（groupBitmapState）
UV（近似）：    50ms（uniq）
7 日留存：      1s（基于 bitmap cohort 表）
维度组合 UV：  100ms-1s（取决于维度基数）
```

**内存开销**：1000 万用户 × 64-bit ID = 100 MB（RoaringBitmap 压缩到 ~10 MB）

## 实战：多平台用户合并（Union / Intersect）

```sql
-- Web + iOS + Android 三端 UV 总和（跨平台去重）
WITH web_users AS (SELECT groupBitmapState(user_id) AS uv FROM web_events),
ios_users AS (SELECT groupBitmapState(user_id) AS uv FROM ios_events),
android_users AS (SELECT groupBitmapState(user_id) AS uv FROM android_events)
SELECT
  bitmapCardinality(bitmapOr(w.uv, bitmapOr(i.uv, a.uv))) AS total_uv,
  bitmapCardinality(bitmapAnd(w.uv, i.uv)) AS web_ios_overlap,
  bitmapCardinality(w.uv) AS web_uv,
  bitmapCardinality(i.uv) AS ios_uv,
  bitmapCardinality(a.uv) AS android_uv
FROM web_users w, ios_users i, android_users a
```

## 大厂实践

### 字节跳动

- 抖音 UV：Bitmap + 物化视图预聚合
- 留存：bitmap cohort 表
- 高基数（用户 + 内容）：bitmap + SAMPLE 抽样

### B 站

- 用户行为去重：bitmap + 弹幕反垃圾
- 多维 UV：bitmap 维度交叉

### 京东

- 订单用户画像：bitmap + 实时画像
- 高基数活动用户：bitmap cardinality

## 下一步

- 学习实时数仓：见 [realtime-warehouse.md](./realtime-warehouse.md)
- 学习生态集成：见 [05-ecosystem/overview.md](../05-ecosystem/overview.md)
