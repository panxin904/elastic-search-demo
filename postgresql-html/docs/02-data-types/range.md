---
title: Range 范围类型
date: 2026-08-15  # date-auto-injected
description: PostgreSQL 原生范围类型详解
---

# Range 范围类型

> **TL;DR**：PG 提供**原生范围类型**（int4range / int8range / numrange / tsrange / daterange），把"开始 + 结束 + 是否包含边界"封装成一个值。**会议室预订、连续时间段、IP 段**这些场景比单独存 start/end 列更优雅且查询更快。

## 一句话定义

```
Range 类型 = [start, end) 区间值，自带边界控制、空检查、重叠检测
```

## 6 种内置范围类型

| 类型 | 元素 | 例子 |
|---|---|---|
| int4range | int | `int4range(1, 10)` |
| int8range | bigint | `int8range(100, 1000000)` |
| numrange | numeric | `numrange(1.5, 9.99)` |
| tsrange | timestamp | `tsrange('2026-08-09 09:00', '2026-08-09 18:00')` |
| tstzrange | timestamptz | `tstzrange(now(), now() + interval '1 hour')` |
| daterange | date | `daterange('2026-08-01', '2026-08-31')` |

## 边界表示法

```
[lo, hi]   闭区间（包含两端）
[lo, hi)   左闭右开（PG 默认）
(lo, hi]   左开右闭
(lo, hi)   开区间
```

```sql
-- 默认左闭右开
SELECT int4range(1, 10);              -- '[1,11)'  ← PG 实际是离散值
-- 实际：包含 1,2,...,10

-- 显式指定
SELECT int4range(1, 10, '[]');        -- '[1,10]'
SELECT int4range(1, 10, '(]');        -- '(1,10]'
```

## 基本使用

### 表设计与插入

```sql
-- 1. 会议室预订场景
CREATE TABLE room_bookings (
  id BIGSERIAL PRIMARY KEY,
  room_id INT,
  booking_period daterange,
  who TEXT
);

-- 2. 插入
INSERT INTO room_bookings (room_id, booking_period, who) VALUES
  (1, daterange('2026-08-09', '2026-08-10'), '张三'),
  (1, '[2026-08-10,2026-08-12)', '李四'),  -- 字面量
  (1, daterange('2026-08-15', NULL, '[]'), '王五');  -- 无限区间

-- 3. 无界（unbounded）
SELECT daterange(NULL, '2026-08-09');         -- 之前到 8-9
SELECT daterange('2026-08-09', NULL);         -- 8-9 之后
SELECT daterange(NULL, NULL);                 -- 全部
```

### 访问元素

```sql
SELECT
  lower(booking_period) AS start_date,  -- 下界
  upper(booking_period) AS end_date,    -- 上界（注意 daterange 是离散）
  lower_inc(booking_period),            -- 下界是否包含
  upper_inc(booking_period),            -- 上界是否包含
  isempty(booking_period)               -- 是否空
FROM room_bookings;
```

> **陷阱**：daterange 是离散类型，upper 显示的是"下一个值"。`daterange('2026-08-09', '2026-08-10')` 实际是 8-9 当天，upper 显示 '2026-08-10' 是因为"下一个边界"。

### 边界控制函数

```sql
-- 1. 包含下界/上界
SELECT int4range(1, 10, '[]');           -- '[1,11)'   包含 1 和 10（实际显示 11）
SELECT int4range(1, 10, '(]');           -- '(1,11)'   不包含 1

-- 2. 修改边界
SELECT int4range(1, 10) - int4range(5, 7);  -- '{[1,5),[7,11)}'
```

## 查询操作符（最重要的部分）

### 核心操作符

| 操作符 | 含义 | 例子 | 应用 |
|---|---|---|---|
| `@>` | 包含 | `r @> x` | x 在 r 内 |
| `<@` | 被包含 | `x <@ r` | x 在 r 内 |
| `&&` | 重叠 | `r1 && r2` | 有交集 |
| `-|-` | 相邻 | `r1 -|- r2` | 无缝连接 |
| `<<` | 严格在左 | `r1 << r2` | r1 完全在 r2 左侧 |
| `>>` | 严格在右 | `r1 >> r2` | r1 完全在 r2 右侧 |
| `&<` | 不延伸右 | `r1 &< r2` | r1 在 r2 左侧或紧邻 |
| `&>` | 不延伸左 | `r1 &> r2` | r1 在 r2 右侧或紧邻 |
| `=` | 相等 | `r1 = r2` | 一样 |

### 实战查询

```sql
-- 1. 检查重叠（会议室预订冲突检测）
SELECT * FROM room_bookings 
WHERE room_id = 1
  AND booking_period && daterange('2026-08-09', '2026-08-11');

-- 2. 包含某个时间点
SELECT * FROM room_bookings 
WHERE booking_period @> '2026-08-10'::date;

-- 3. 被某个范围包含
SELECT * FROM room_bookings 
WHERE booking_period <@ daterange('2026-08-01', '2026-08-31');

-- 4. 找空闲时间（重叠的反面）
SELECT * FROM room_bookings 
WHERE room_id = 1
  AND NOT (booking_period && daterange('2026-08-09', '2026-08-15'));
```

## 范围函数

```sql
-- 1. 交集 / 并集 / 差集
SELECT int4range(1, 10) * int4range(5, 15);   -- '[5,11)'  交集
SELECT int4range(1, 10) + int4range(8, 15);   -- '[1,15)'  并集
SELECT int4range(1, 10) - int4range(5, 7);    -- '{[1,5),[7,11)}'  差集

-- 2. 长度（仅对连续类型）
SELECT upper(r) - lower(r) FROM (
  VALUES (daterange('2026-08-01', '2026-08-10'))) v(r);

-- 3. 是否包含 / 空
SELECT int4range(1, 1, '[]');           -- 非空 [1,1]
SELECT isempty(int4range(1, 1, '[]'));   -- false
SELECT isempty(int4range(1, 1, '[)'));   -- true（空区间）

-- 4. 规范化（合并重叠）
SELECT range_merge(int4range(1,5), int4range(3,8));  -- '[1,9)'
```

## 索引

```sql
-- 1. GiST 索引（默认，推荐）
CREATE INDEX idx_bookings_period ON room_bookings USING GIST (booking_period);

-- 2. SP-GiST 索引（适合静态数据）
CREATE INDEX idx_bookings_spgist ON room_bookings USING SPGIST (booking_period);

-- 3. btree 索引（只能对标量列，不推荐）

-- 4. 排除约束（防重叠预订）
ALTER TABLE room_bookings 
ADD CONSTRAINT no_overlap 
EXCLUDE USING GIST (
  room_id WITH =, 
  booking_period WITH &&
);
-- 同一房间不可有重叠预订（数据库级强约束）
```

**排除约束**：PG 独家特性，**用 GiST 索引 + EXCLUDE 实现任意两行不重叠**，是 PostgreSQL 杀手锏。

## 实战案例

### 案例 1：会议室预订系统

```sql
-- 1. 表
CREATE TABLE room_bookings (
  id BIGSERIAL PRIMARY KEY,
  room_id INT NOT NULL,
  period daterange NOT NULL,
  booked_by TEXT NOT NULL,
  EXCLUDE USING GIST (
    room_id WITH =,
    period WITH &&
  )
);

-- 2. 插入会冲突的预订会报错
INSERT INTO room_bookings (room_id, period, booked_by)
VALUES (1, daterange('2026-08-09', '2026-08-11'), '张三');

INSERT INTO room_bookings (room_id, period, booked_by)
VALUES (1, daterange('2026-08-10', '2026-08-12'), '李四');
-- ERROR: conflicting key value violates exclusion constraint "no_overlap"
```

### 案例 2：IP 段管理

```sql
CREATE TABLE ip_ranges (
  cidr CIDR,
  owner TEXT,
  allocated_at TIMESTAMPTZ,
  valid_period tstzrange
);

CREATE INDEX idx_ip_ranges_cidr ON ip_ranges USING GIST (cidr);
CREATE INDEX idx_ip_ranges_period ON ip_ranges USING GIST (valid_period);

-- 查 192.168.1.100 在哪个 IP 段里
SELECT * FROM ip_ranges 
WHERE cidr >> '192.168.1.100'::inet;

-- 查 2026-08-09 10:00 时刻活跃的 IP 段
SELECT * FROM ip_ranges 
WHERE valid_period @> '2026-08-09 10:00'::timestamptz;
```

### 案例 3：会员有效期

```sql
CREATE TABLE memberships (
  user_id BIGINT,
  period daterange NOT NULL,
  level TEXT,
  EXCLUDE USING GIST (
    user_id WITH =,
    period WITH &&
  )
);

-- 查 2026-08-09 仍然有效的会员
SELECT * FROM memberships 
WHERE user_id = 123
  AND period @> '2026-08-09'::date;

-- 续费：拼接两个区间
UPDATE memberships 
SET period = range_merge(period, daterange('2026-12-01', '2027-03-01'))
WHERE user_id = 123;
```

### 案例 4：价格区间查询

```sql
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  price_range numrange
);

-- 查找 100-500 元区间内的商品
SELECT * FROM products
WHERE price_range @> numrange(100, 500);
-- 包含 [100, 500] 完整范围
```

## 自定义范围类型

```sql
-- 1. 定义新类型
CREATE TYPE floatrange AS RANGE (
  subtype = float8,
  subtype_diff = float8mi
);

-- 2. 用
CREATE TABLE measurements (
  id BIGSERIAL,
  val floatrange
);

SELECT floatrange(1.0, 9.5, '[]');
```

## 数组 vs Range vs JSONB

| 场景 | 推荐类型 |
|---|---|
| 多个独立标签 | 数组 |
| 连续区间（时间/价格/IP） | Range |
| 嵌套异构数据 | JSONB |
| 几何（点/线/面） | PostGIS |

## 一句话总结

> **Range 类型 = 连续区间的最佳表达**：会议室预订、IP 段、会员有效期、价格区间。**配 GiST 索引 + EXCLUDE 约束实现"自动防重叠"**，是 PostgreSQL 的独家杀手锏。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [mysql](https://java-px.bot.cd/mysql/):MySQL 对比
- [clickhouse](https://java-px.bot.cd/clickhouse/):ClickHouse OLAP
- [system-design](https://java-px.bot.cd/system-design/):数据库选型
