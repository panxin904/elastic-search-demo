---
title: SP-GiST 索引
date: 2026-08-15  # date-auto-injected
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

## 四叉树应用：地理坐标

```sql
-- 场景：附近的人 / 外卖派单 — 用 SP-GiST + point 四叉树
CREATE TABLE restaurants (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  location POINT  -- (longitude, latitude)
);

CREATE INDEX idx_rest_loc ON restaurants USING SPGIST (location);

-- 查某点 1km 范围内的餐厅（用 PostGIS 表达更精准，SP-GiST 仅前缀匹配场景）
SELECT * FROM restaurants
ORDER BY location <-> point(116.4, 39.9)
LIMIT 20;
-- <-> 是 KD-tree 距离，但 SP-GiST 也可选用 cube + distance
```

## 实战案例：CDN 边缘节点白名单

```sql
-- 场景：100 万条 CDN 节点 IP 段，需要快速判断用户 IP 是否在某个白名单段
CREATE TABLE cdn_whitelist (
  cidr CIDR NOT NULL,
  region TEXT,
  enabled BOOLEAN DEFAULT true
);

-- SP-GiST 是首选：天然支持 CIDR prefix 查询
CREATE INDEX idx_cdn_whitelist_spgist ON cdn_whitelist USING SPGIST (cidr);

-- 查询：用户 IP 192.168.50.123 命中哪些白名单段
EXPLAIN ANALYZE
SELECT * FROM cdn_whitelist
WHERE cidr >> '192.168.50.123'::inet AND enabled = true;
-- Index Scan using idx_cdn_whitelist_spgist (cost=0.14..8.42 rows=4) (actual time=0.05..0.06 rows=2)
```

**经验**：如果只是偶尔按精确 IP 查，B-tree 反而更快；只有大量 prefix 包含查询时 SP-GiST 优势才体现出来。

## 关联章节

- [B-tree 索引](./btree.md) — 默认选择
- [GiST 索引](./gist.md) — 多维空间数据（PostGIS）
- [BRIN 索引](./brin.md) — 时序/物理有序数据

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
