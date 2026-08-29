---
title: 查询规划器
date: 2026-08-15  # date-auto-injected
description: EXPLAIN 解读与优化
---

# 查询规划器

> **TL;DR**：PG planner 用 **基于成本的优化器（CBO）**，根据统计信息选最优执行计划。**EXPLAIN** 是解读 plan 的核心工具。

## 一句话定义

```
查询规划器 = 把 SQL 解析 + 优化成最优执行计划
           = 基于成本（cost-based optimization）
           = 输入：SQL + 统计信息
           = 输出：执行计划（Plan Tree）
```

## EXPLAIN 基本使用

```sql
-- 只看计划（不执行）
EXPLAIN SELECT * FROM users WHERE id = 1;

-- 真实执行 + 统计
EXPLAIN ANALYZE SELECT * FROM users WHERE id = 1;

-- 含缓冲命中
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM users WHERE id = 1;
```

## 读取 EXPLAIN 输出

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = '[email protected]';

-- Index Scan using idx_users_email on users
--   (cost=0.42..8.44 rows=1 width=100) (actual time=0.05..0.06 rows=1 loops=1)
--   Index Cond: (email = '[email protected]')
--   Buffers: shared hit=4
-- Planning Time: 0.15 ms
-- Execution Time: 0.08 ms
```

**字段解读**：

| 字段 | 含义 |
|---|---|
| `cost=X..Y` | 估算成本（X = 启动成本，Y = 总成本） |
| `rows=N` | 估算返回行数 |
| `width=N` | 每行平均字节数 |
| `actual time=X..Y` | 真实耗时（ms） |
| `actual rows=N` | 真实返回行数 |
| `loops=N` | 这个节点执行次数 |
| `Buffers: shared hit=N read=M` | 缓存命中 / 磁盘读 |

## 扫描类型

| 节点 | 含义 | 何时使用 |
|---|---|---|
| `Seq Scan` | 全表扫描 | 无索引 / 大量数据 |
| `Index Scan` | 索引扫描 | 等值 + 范围 |
| `Index Only Scan` | 仅索引扫描 | 索引覆盖所有列 |
| `Bitmap Index Scan` | 位图索引扫描 | 多条件 OR |
| `Bitmap Heap Scan` | 位图堆扫描 | Bitmap Index 的下一步 |

```sql
-- ❌ 全表扫描
EXPLAIN SELECT * FROM users WHERE name LIKE '%alice%';
-- Seq Scan on users (cost=0..1500 rows=10) (actual rows=0)
--   Filter: (name ~~ '%alice%')

-- ✓ 索引扫描
EXPLAIN SELECT * FROM users WHERE email = '[email protected]';
-- Index Scan using idx_users_email on users
--   Index Cond: (email = '[email protected]')
```

## JOIN 类型

| 节点 | 含义 | 何时使用 |
|---|---|---|
| `Nested Loop` | 嵌套循环 | 小数据集 / 索引 JOIN |
| `Hash Join` | 哈希连接 | 等值 JOIN，大表 |
| `Merge Join` | 合并连接 | 已排序的大表 JOIN |

```sql
EXPLAIN SELECT * FROM users u
JOIN orders o ON u.id = o.user_id;

-- Hash Join (cost=... rows=...)
--   Hash Cond: (o.user_id = u.id)
--   -> Seq Scan on orders o
--   -> Hash
--        -> Seq Scan on users u
```

## 统计信息

```sql
-- 1. 手动收集
ANALYZE users;

-- 2. 自动收集
-- autovacuum_analyze_scale_factor = 0.1（10% 行变化触发）

-- 3. 看统计信息
SELECT * FROM pg_stats WHERE tablename = 'users';
-- 显示每列的 distinct 值、最常见值、直方图等
```

## 成本因子

```ini
# postgresql.conf

# 影响 planner 决策
seq_page_cost = 1.0            # 顺序扫描单页成本（默认）
random_page_cost = 4.0          # 随机扫描单页成本（默认）
# SSD 推荐 random_page_cost = 1.1

cpu_tuple_cost = 0.01          # 每行处理成本
cpu_index_tuple_cost = 0.005    # 每行索引处理成本
cpu_operator_cost = 0.0025     # 每操作符成本

effective_io_concurrency = 1   # 并发 IO（SSD 推荐 200）
```

## 优化技巧

### 1. 让 planner 选索引

```sql
-- ❌ 表达式包裹让索引失效
WHERE date(created_at) = '2026-08-09'

-- ✅ 等价但能用索引
WHERE created_at >= '2026-08-09' AND created_at < '2026-08-10'
```

### 2. 收集最新统计信息

```sql
-- 大量 INSERT 后
ANALYZE VERBOSE users;

-- 看是否最新
SELECT last_analyze, last_autoanalyze FROM pg_stat_user_tables WHERE relname = 'users';
```

### 3. 强制 JOIN 顺序

```sql
-- 小表驱动大表
SELECT /*+ Leading(small large) */ *
FROM small s
JOIN large l ON s.id = l.small_id;

-- 或 SET
SET join_collapse_limit = 1;
-- planner 会按 SQL 顺序 JOIN
```

### 4. 关闭某些优化

```sql
-- 关闭 Nested Loop
SET enable_nestloop = off;

-- 关闭 Hash Join
SET enable_hashjoin = off;

-- 关闭 Merge Join
SET enable_mergejoin = off;
```

## 一句话总结

> **EXPLAIN ANALYZE 是 DBA 第一工具**：**看扫描类型、JOIN 类型、cost 估算、actual 实际**。**Seq Scan + 大表 = 加索引**。**随机 IO 慢 → random_page_cost 调到 1.1（SSD）**。

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
