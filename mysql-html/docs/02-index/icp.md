---
title: 索引下推 ICP
date: 2026-08-15  # date-auto-injected
---

# 🔍 索引下推 ICP

> **Index Condition Pushdown（ICP）** 是 MySQL 5.6 引入的优化，可以让查询**减少 50% 以上的回表次数**。

![Mysql Icp Flow](/mysql-icp-flow.svg)

## 🤔 优化前的问题

在 ICP 出现之前，MySQL 处理这样的查询：

```sql
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  name VARCHAR(50),
  age INT,
  city VARCHAR(50),
  KEY idx_name (name)  -- 只有 name 索引，没有 age
);

SELECT * FROM users WHERE name LIKE '张%' AND age = 25;
```

**ICP 之前的执行过程：**

```
1. 在 idx_name 中找到所有 name LIKE '张%' 的记录
   → 假设找到 1000 条（张三、张三丰、张飞、张...）
   ↓

2. 用这 1000 条记录的 id，逐一去聚簇索引回表
   → 1000 次回表！
   ↓

3. 在聚簇索引读取完整数据后，再用 age = 25 过滤
   → 只过滤掉了 990 条，浪费 990 次 IO
   ↓

4. 返回最终 10 条结果
```

**问题：** 大量回表后发现不符合 age 条件，IO 浪费严重。

## ✨ ICP 优化后

**MySQL 5.6+ 引入了 ICP：把 WHERE 条件下推到存储引擎层**，在回表前就过滤。

```
ICP 优化后的执行过程：

1. 在 idx_name 中找到所有 name LIKE '张%' 的记录
   → 1000 条
   ↓

2. 🔥 ICP：在 idx_name 中检查 age 条件
   → 存储引擎从索引中直接读取 age 字段
   → 过滤后只剩 10 条
   ↓

3. 只用这 10 条的 id 去聚簇索引回表
   → 10 次回表（vs 之前 1000 次）
   ↓

4. 返回最终 10 条结果
```

**性能提升：** 1000 次回表 → 10 次回表，**快 100 倍！**

## 🔬 ICP 的工作原理

### 核心：把过滤条件下推到存储引擎

```
SQL 层                                    存储引擎层
┌──────────────────────┐                ┌──────────────────────┐
│ SELECT * FROM users   │                │ InnoDB                 │
│ WHERE name LIKE '张%' │                │                       │
│   AND age = 25        │                │ 1. 在 idx_name 中查找  │
│                       │ ──── 条件 ────▶│    name LIKE '张%'     │
│                       │                │ 2. ICP: 检查 age=25   │
│                       │                │    （不需要回表！）    │
│                       │                │ 3. 返回符合的 id       │
│                       │ ◀─── 结果 ────│                       │
│ 4. 用 id 回表取完整数据 │                │                       │
│ 5. 返回结果            │                │                       │
└──────────────────────┘                └──────────────────────┘
```

### ICP 的限制

```sql
-- ❌ ICP 不生效：WHERE 条件中有非索引字段
SELECT * FROM users WHERE name LIKE '张%' AND email = 'a@b.com';
-- email 不在 idx_name 中 → ICP 无法下推

-- ❌ ICP 不生效：主键查询（不需要回表）
SELECT * FROM users WHERE id = 100;

-- ✅ ICP 生效：所有 WHERE 字段都在索引中
SELECT * FROM users WHERE name LIKE '张%' AND age = 25;
-- name 在 idx_name 中（key），age 在二级索引的叶子节点中（需要覆盖）
-- 等等，age 必须在索引中才能 ICP 下推
```

**关键条件：** 索引必须包含 WHERE 条件中**除了范围匹配字段之外的**所有字段。

```sql
-- 索引 (name, age)
-- ✅ ICP 生效：name 用于查找，age 可在索引中过滤
SELECT * FROM users WHERE name LIKE '张%' AND age = 25;

-- 索引 (name, age)
-- ⚠️ 部分 ICP：name LIKE '张%' 是范围，age = 25 还能用 ICP
SELECT * FROM users WHERE name = '张三' AND age = 25;
```

## 🎯 ICP 实战案例

### 案例 1：LIKE + 范围优化

```sql
-- 表：orders (id, user_id, amount, status, created_at)
CREATE INDEX idx_status_created ON orders(status, created_at);

-- 查询：查找已支付(status='paid')的最近 7 天的订单
SELECT * FROM orders
WHERE status = 'paid' AND created_at > '2025-01-01';
```

**ICP 之前：**
```
1. 在 idx_status_created 找到 status='paid' → 100 万条
2. 全部回表 → 100 万次 IO
3. 在内存中过滤 created_at
```

**ICP 之后：**
```
1. 在 idx_status_created 找到 status='paid' AND created_at > '2025-01-01'
   → 索引中直接比较 created_at（不需要回表！）
   → 假设只剩 5 万条
2. 5 万次回表
性能提升：20 倍
```

### 案例 2：范围查询 + 过滤

```sql
CREATE INDEX idx_price ON products(price);
-- 注意：索引里只有 price

-- 查询：价格 100-1000 且 库存 > 0 的商品
SELECT * FROM products WHERE price BETWEEN 100 AND 1000 AND stock > 0;
```

**ICP 之前：**
```
1. 在 idx_price 找到 price BETWEEN 100 AND 1000 → 5 万条
2. 全部回表 → 5 万次 IO
3. 在内存中过滤 stock > 0
```

**ICP 之后：**
```
1. 在 idx_price 找到 price BETWEEN 100 AND 1000
2. ICP 检查 stock > 0（stock 不在索引中...）
```

**等等！** ICP 要求字段在索引中才能下推。如果 stock 不在 idx_price 中，ICP 就不能下推。

**解决方法：创建覆盖索引**

```sql
CREATE INDEX idx_price_stock ON products(price, stock);
-- 现在 stock 也在索引中，ICP 可以下推
```

### 案例 3：ICP + MRR 联合优化

```sql
-- ICP 通常和 MRR（Multi-Range Read）配合使用
-- ICP 先过滤，MRR 再排序回表

CREATE INDEX idx_status ON orders(status);
SELECT * FROM orders WHERE status = 'paid' LIMIT 100;
```

**执行过程（ICP + MRR）：**
```
1. ICP：在 idx_status 找到 status='paid' 且符合其他条件（如有）
2. MRR：把符合条件的主键 id 收集起来排序
3. 按排序后的 id 顺序回表（顺序 IO 比随机 IO 快得多）
```

## ⚙️ ICP 配置

```sql
-- 查看 ICP 状态（默认 ON）
SHOW VARIABLES LIKE 'optimizer_switch'\G
-- index_condition_pushdown = on

-- 临时关闭 ICP（测试对比性能）
SET optimizer_switch = 'index_condition_pushdown=off';

-- 重新开启
SET optimizer_switch = 'index_condition_pushdown=on';
```

## 🔍 如何判断 ICP 是否生效？

### 方法 1：EXPLAIN 看 Extra

```sql
EXPLAIN SELECT * FROM users WHERE name LIKE '张%' AND age = 25;
```

| Extra 值 | 含义 |
|---|---|
| `Using where` | SQL 层过滤（ICP 没生效或没机会） |
| `Using index condition` | **ICP 生效** ✅ |
| `Using index` | 覆盖索引（不需要回表） |

### 方法 2：OPTIMIZER_TRACE

```sql
SET optimizer_trace = 'enabled=on';

-- 执行查询
SELECT * FROM users WHERE name LIKE '张%' AND age = 25;

-- 查看 trace
SELECT * FROM information_schema.optimizer_trace\G
```

trace 中会显示：
```json
{
  "join_execution": {
    "select#": 1,
    "steps": [
      {
        "index_condition_pushdown": "true"  ← ICP 生效
      }
    ]
  }
}
```

## 📊 ICP 性能对比示例

```sql
-- 测试表：100 万行
CREATE TABLE test_icp (
  id BIGINT PRIMARY KEY,
  a INT,  -- 范围 1-100
  b INT,  -- 范围 1-10000
  c INT,
  KEY idx_a (a)
);

-- 查询
SELECT COUNT(*) FROM test_icp WHERE a BETWEEN 1 AND 5 AND b > 5000;
```

| ICP 状态 | 扫描行数 | 耗时 |
|---|---|---|
| OFF | 100000（全表扫描 + 后置过滤） | ~500ms |
| ON（仅 a 索引） | 50000（a 过滤） + 全过滤 | ~200ms |
| ON + 覆盖索引 (a, b) | 50000 + ICP 过滤 b | ~20ms |

**ICP + 覆盖索引 = 性能最佳组合！**

## ⚠️ ICP 不生效的情况

```sql
-- 1. ICP 默认开启，但有些情况不会生效：

-- 用了非索引字段
SELECT * FROM t WHERE idx_col = 1 AND non_idx_col = 'x';
-- non_idx_col 不在索引中 → ICP 无法下推

-- 主键查询（不需要回表）
SELECT * FROM t WHERE id = 1;

-- 覆盖索引（不需要回表）
SELECT idx_col FROM t WHERE idx_col = 1;
-- Extra: Using index，没有 ICP 必要

-- 索引覆盖了所有需要的字段
-- ICP 已经"无机会"发挥
```

## 🧪 实操：对比 ICP 前后性能

```sql
-- 准备测试数据
CREATE TABLE perf_test (
  id BIGINT PRIMARY KEY,
  category TINYINT,      -- 1-10
  status TINYINT,         -- 1-5
  price INT,
  name VARCHAR(50),
  KEY idx_cat (category)
);

-- 插入 100 万行随机数据
-- ...

-- 测试查询
SELECT * FROM perf_test WHERE category = 5 AND status = 2 AND price > 1000;

-- 关闭 ICP 测试
SET optimizer_switch = 'index_condition_pushdown=off';
SELECT BENCHMARK(10, (SELECT COUNT(*) FROM perf_test WHERE category = 5 AND status = 2 AND price > 1000));

-- 开启 ICP 测试
SET optimizer_switch = 'index_condition_pushdown=on';
SELECT BENCHMARK(10, (SELECT COUNT(*) FROM perf_test WHERE category = 5 AND status = 2 AND price > 1000));
```

## 📊 ICP vs MRR 对比

| 特性 | ICP | MRR |
|---|---|---|
| 作用 | **减少回表次数** | **优化回表顺序** |
| 原理 | 存储引擎层提前过滤 | 主键排序后批量回表 |
| 触发条件 | 索引包含 WHERE 字段 | 范围扫描多行 |
| 配合 | 减少回表量 | 优化 IO 顺序 |

**两者经常一起使用：**
```
ICP 过滤掉大部分 → MRR 排序剩余 id → 顺序回表 → 返回结果
```

## 🎯 总结

**ICP 的精髓：**
- ✅ 把 WHERE 条件下推到存储引擎层
- ✅ 在索引中提前过滤，减少回表次数
- ✅ 通常减少 **50% 以上**的 IO
- ✅ 默认开启，无需配置

**ICP 生效的关键：**
- WHERE 条件的所有字段都要在**同一个索引**中
- 否则 ICP 无法下推，必须回表过滤

**最佳实践：**
- 创建覆盖索引（包含 WHERE 字段）
- 复合索引按最左前缀原则设计
- 用 EXPLAIN 验证 Extra = `Using index condition`

**下一步：** [📊 EXPLAIN 解读](../05-optimization/explain) — 12 个字段全解析，系统化看懂查询计划