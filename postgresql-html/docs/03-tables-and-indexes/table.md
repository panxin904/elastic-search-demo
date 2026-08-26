---
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


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
