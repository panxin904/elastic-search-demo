---
title: EXPLAIN 解读
date: 2026-08-15  # date-auto-injected
---

# 📊 MySQL EXPLAIN 解读

> **EXPLAIN 是 MySQL 性能调优的"听诊器"**。学会看 EXPLAIN 输出，就能诊断 90% 的慢查询问题。

## 🚀 EXPLAIN 基础

```sql
-- 基础用法
EXPLAIN SELECT * FROM users WHERE id = 1;

-- 详细分析（MySQL 8.0.18+）
EXPLAIN ANALYZE SELECT * FROM users WHERE id = 1;

-- 传统格式输出
EXPLAIN FORMAT=TRADITIONAL SELECT * FROM users WHERE id = 1;

-- JSON 格式（程序化分析）
EXPLAIN FORMAT=JSON SELECT * FROM users WHERE id = 1;
```

## 📋 EXPLAIN 输出字段详解

### 完整示例

```sql
EXPLAIN SELECT u.id, u.name, o.amount
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
WHERE u.city = '北京' AND o.created_at > '2025-01-01'
ORDER BY o.created_at DESC
LIMIT 10;
```

```
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-----------------------------+
| id | select_type | table | type  | possible_keys | key     | key_len | ref   | rows | Extra                       |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-----------------------------+
|  1 | SIMPLE      | u     | ref   | idx_city       | idx_city | 203    | const |  500 | NULL                        |
|  1 | SIMPLE      | o     | ref   | idx_user_created | idx_user_created | 9 | u.id |   10 | Using where; Backward index scan |
+----+-------------+-------+-------+---------------+---------+---------+-------+------+-----------------------------+
```

### 1. id（执行顺序）

```sql
-- id 相同：执行顺序从上到下
-- id 不同：id 大的先执行（嵌套子查询）
-- id NULL：UNION 结果
```

### 2. select_type（查询类型）

| select_type | 含义 |
|---|---|
| SIMPLE | 简单查询（无 UNION / 子查询） |
| PRIMARY | 最外层查询 |
| SUBQUERY | 子查询 |
| DERIVED | 派生表（FROM 子查询） |
| UNION | UNION 第二个及之后的查询 |
| UNION RESULT | UNION 结果 |

```sql
EXPLAIN SELECT * FROM (SELECT * FROM users) AS derived_u;
-- select_type = DERIVED
```

### 3. table（访问的表）

- 显示这一行访问的表名
- `<derived2>` 表示派生表（id=2 的派生）
- `<union1,2>` 表示 UNION 结果（来自 id=1 和 id=2）

### 4. type（访问类型）⭐⭐⭐

**最重要的字段！从最优到最差排序：**

| type | 含义 | 性能 |
|---|---|---|
| **system** | 表只有一行（系统表） | ⭐⭐⭐⭐⭐ |
| **const** | 主键 / 唯一索引等值，最多 1 行 | ⭐⭐⭐⭐⭐ |
| **eq_ref** | JOIN 时主键 / 唯一索引等值 | ⭐⭐⭐⭐ |
| **ref** | 非唯一索引等值 | ⭐⭐⭐ |
| **ref_or_null** | ref + NULL 值 | ⭐⭐⭐ |
| **range** | 范围扫描（BETWEEN、IN、>） | ⭐⭐⭐ |
| **index** | 全索引扫描 | ⭐⭐ |
| **ALL** | 全表扫描 | ⭐ ❌ |

```sql
-- ❌ ALL（最差）
EXPLAIN SELECT * FROM users WHERE name LIKE '%张%';
-- type: ALL

-- ✅ const（最好）
EXPLAIN SELECT * FROM users WHERE id = 1;
-- type: const

-- ✅ ref（常用）
EXPLAIN SELECT * FROM users WHERE name = '张三';
-- type: ref（前提：name 有索引）

-- ⚠️ index（全索引扫描）
EXPLAIN SELECT id FROM users;
-- type: index（扫描整个索引树，比 ALL 好但仍需优化）
```

### 5. possible_keys（可能用到的索引）

```sql
-- 显示可能用到的索引，但不一定会用
-- 如果为 NULL，说明没有可用索引
```

### 6. key（实际用到的索引）⭐⭐

```sql
-- 如果为 NULL，表示没有用索引（需要优化！）
EXPLAIN SELECT * FROM users WHERE name = '张三' AND age = 25;
-- key: idx_name_age（如果建了复合索引）
-- key: NULL（没建索引）
```

### 7. key_len（索引使用字节数）

```sql
-- 表示索引使用的字节数，可判断复合索引用到了几列

-- 复合索引 (name(50), age, city(20))
-- VARCHAR(50) utf8mb4: 50 × 4 + 2 = 202 字节
-- INT: 4 字节
-- VARCHAR(20) utf8mb4: 20 × 4 + 2 = 82 字节

EXPLAIN SELECT * FROM users WHERE name = '张三' AND age = 25;
-- key_len = 202 + 4 = 206（只用了 name + age，没用 city）
```

**字符集字节计算：**
- latin1：1 字节/字符
- utf8：3 字节/字符
- utf8mb4：4 字节/字符
- VARCHAR 额外 +2 字节（长度）
- NULL 列额外 +1 字节

### 8. ref（索引的哪一列被使用）

```sql
-- 显示索引的哪一列被使用了，常量值还是某个列

EXPLAIN SELECT * FROM users u JOIN orders o ON u.id = o.user_id;
-- ref: o.user_id（用的是 orders 表的 user_id 列）

EXPLAIN SELECT * FROM users WHERE name = '张三';
-- ref: const（用的是常量 '张三'）
```

### 9. rows（预估扫描行数）⭐

```sql
-- MySQL 预估需要扫描的行数
-- ⚠️ 这是估算值，不一定准确，但能反映大致规模

-- 理想值：rows 越小越好
-- type=ALL 时 rows 是全表行数
-- type=index 时 rows 是索引行数
-- type=range 时 rows 是范围内的行数
```

### 10. filtered（按表条件过滤的行百分比）

```sql
-- 表示存储引擎返回的行中，经过 WHERE 过滤后的百分比
-- filtered × rows = 实际参与 JOIN 的行数

-- 例：rows=1000, filtered=10%
-- 实际参与：1000 × 10% = 100 行
```

### 11. Extra（额外信息）⭐⭐⭐

**第二个最重要的字段，包含关键优化线索：**

| Extra 值 | 含义 | 优化建议 |
|---|---|---|
| `Using index` | 覆盖索引，无需回表 | ✅ 最佳 |
| `Using where` | 在存储引擎返回后用 WHERE 过滤 | 通常 OK |
| `Using index condition` | ICP 生效 | ✅ 好 |
| `Using temporary` | 使用临时表（GROUP BY / ORDER BY） | ⚠️ 需优化 |
| `Using filesort` | 文件排序（不能用索引排序） | ⚠️ 需优化 |
| `Using join buffer` | JOIN 缓冲（关联字段没索引） | ⚠️ 需优化 |
| `Impossible WHERE` | WHERE 永远为 false | 优化 SQL |
| `Select tables optimized away` | 优化器已优化（如 MIN/MAX） | ✅ 完美 |
| `Range checked for each record` | 范围检查（没好的索引） | ⚠️ 需加索引 |

```sql
-- ❌ Using filesort（文件排序）
EXPLAIN SELECT * FROM users ORDER BY name LIMIT 10;
-- Extra: Using filesort
-- 修复：给 name 加索引

-- ❌ Using temporary（临时表）
EXPLAIN SELECT city, COUNT(*) FROM users GROUP BY city;
-- Extra: Using temporary
-- 修复：给 city 加索引

-- ✅ Using index（覆盖索引）
EXPLAIN SELECT id, name FROM users WHERE name = '张三';
-- Extra: Using index
```

## 🎯 EXPLAIN 解读流程

### 实战：诊断慢查询

```sql
-- 1. 找到慢查询
SELECT * FROM mysql.slow_log WHERE start_time > '2025-07-18' LIMIT 10;

-- 2. 用 EXPLAIN 分析
EXPLAIN SELECT * FROM orders
WHERE user_id = 100
  AND status = 'paid'
  AND created_at > '2025-01-01'
ORDER BY created_at DESC
LIMIT 20;
```

**解读顺序：**
1. **type**：是不是 ALL（最差）？
2. **key**：有没有用索引？
3. **rows**：扫描行数是否合理？
4. **Extra**：有没有 filesort / temporary？

```
type=ALL, key=NULL, rows=1000000, Extra=Using filesort
→ ❌ 全表扫描 + 文件排序，性能很差
→ ✅ 加索引：(user_id, status, created_at)
```

## 🔍 EXPLAIN ANALYZE（MySQL 8.0.18+）

```sql
-- 实际执行查询并显示真实耗时
EXPLAIN ANALYZE SELECT * FROM users WHERE city = '北京';

-- 输出示例：
-- -> Filter: (users.city = '北京')  (cost=1024 rows=500) (actual time=2.5..15.3 rows=500)
--     -> Index range scan on idx_city using idx_city  (cost=512 rows=500) (actual time=0.8..10.2 rows=500)

-- 关键信息：
-- - actual time: 实际耗时（毫秒）
-- - rows: 实际扫描行数（vs 估算）
-- - loops: 循环次数
```

## 📊 优化前后对比示例

### 优化前

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 100 ORDER BY created_at DESC LIMIT 10;
+----+-------------+--------+-------+---------------+---------+---------+------+-------+-----------------------------+
| id | select_type | table  | type  | possible_keys | key     | key_len | ref  | rows  | Extra                       |
+----+-------------+--------+-------+---------------+---------+---------+------+-------+-----------------------------+
|  1 | SIMPLE      | orders | ALL   | NULL          | NULL    | NULL    | NULL | 100万 | Using where; Using filesort |
+----+-------------+--------+-------+---------------+---------+---------+------+-------+-----------------------------+

-- 问题：
-- 1. type=ALL → 全表扫描
-- 2. key=NULL → 没用索引
-- 3. rows=100万 → 扫描所有数据
-- 4. Using filesort → 文件排序
```

### 优化后

```sql
-- 加索引
CREATE INDEX idx_user_created ON orders(user_id, created_at DESC);

EXPLAIN SELECT * FROM orders WHERE user_id = 100 ORDER BY created_at DESC LIMIT 10;
+----+-------------+--------+-------+---------------+---------------+---------+------+-------+----------------------------------+
| id | select_type | table  | type  | possible_keys | key           | key_len | ref  | rows  | Extra                            |
+----+-------------+--------+-------+---------------+---------------+---------+------+-------+----------------------------------+
|  1 | SIMPLE      | orders | ref   | idx_user_created | idx_user_created | 9 | const |   10 | Backward index scan; Using where |
+----+-------------+--------+-------+---------------+---------------+---------+------+-------+----------------------------------+

-- 改进：
-- 1. type=ref → 索引查找
-- 2. key=idx_user_created → 用上索引
-- 3. rows=10 → 只扫描 10 行
-- 4. Backward index scan → 索引天然有序，无需 filesort
```

## 🎯 EXPLAIN 解读速查表

| 字段 | 关注点 | 优化目标 |
|---|---|---|
| type | 不要 ALL / index | 至少 range，最好 ref/const |
| key | 不要 NULL | 必须用到索引 |
| rows | 越小越好 | 接近实际返回数 |
| Extra | 避免 filesort/temporary | 争取 Using index |

## 🎯 总结

**EXPLAIN 核心三看：**
- **type**：访问类型（ALL = 全表扫描 ❌）
- **key**：实际使用的索引（NULL = 没用到 ❌）
- **Extra**：是否有 filesort / temporary

**优化优先级：**
1. 加索引（解决 type=ALL）
2. 调整索引顺序（解决 type=range 但 rows 多）
3. 用覆盖索引（解决回表）
4. 调整 SQL（解决 filesort / temporary）

**下一步：** [🐌 慢查询定位](../05-optimization/slow-query) — 开启慢查询日志，系统化排查性能瓶颈