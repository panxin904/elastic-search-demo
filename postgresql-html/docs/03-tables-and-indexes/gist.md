---
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
