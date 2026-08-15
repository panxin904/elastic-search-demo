---
title: B+Tree 原理
---

# 🌳 B+Tree 索引原理

> **索引的本质：减少磁盘 IO 次数**。理解 B+Tree，你就理解了为什么索引这么快。

## 🤔 为什么需要索引？

```
全表扫描：1 亿行 = 100,000,000 次磁盘 IO ≈ 1000 秒（HDD）
B+Tree 索引：树高度 3-4 层 = 3-4 次磁盘 IO ≈ 0.03 秒
```

**提升 3 万倍以上！**

## 🌳 B+Tree 的结构

```
                  ┌─────────────────────────┐
                  │   Root（根节点）          │  ← 内存中
                  │   [17 | 35]              │
                  └────┬──────────┬──────────┘
                       │          │
              ┌────────▼──┐  ┌────▼─────────┐
              │ Internal  │  │ Internal     │  ← 内存中
              │ [10|17|25] │  │ [35|45|55]    │
              └─┬──┬──┬───┘  └─┬──┬──┬───────┘
                │  │  │        │  │  │
         ┌──────▼┐ ┌▼──▼─┐ ┌──▼┐ ┌▼──┐ ┌▼──┐
         │Leaf 5-10│ │Leaf│ │Leaf│ │Leaf│ │Leaf│  ← 磁盘上
         │data│ptr│ │... │ │...│ │...│ │... │
         └───────┘ └────┘ └────┘ └────┘ └────┘
              ↓
         叶子节点之间有指针相连（范围查询优化）
```

### 关键特征

1. **平衡树**：所有叶子节点在同一层
2. **多路搜索**：每个节点有 N 个 key 和 N+1 个子节点指针
3. **数据只在叶子**：非叶子节点只存 key 和指针
4. **叶子链表**：叶子节点之间用指针相连，支持范围查询

## 📏 为什么是 B+Tree 而不是 B-Tree？

| 特性 | B-Tree | B+Tree |
|---|---|---|
| 数据存储位置 | 所有节点 | **只在叶子** |
| 叶子节点连接 | 无 | **链表指针** |
| 范围查询 | 需中序遍历 | 顺着链表扫 |
| 磁盘 IO | 更多（每次可能跨节点） | 更少（叶子连续） |
| 单点查询 | 差不多 | 差不多 |

**B+Tree 的优势：**
- 范围查询极快（叶子链表）
- 每个非叶子节点能容纳更多 key（因为不存数据）
- 树更矮，IO 更少

## 📐 B+Tree 的核心参数

```sql
-- InnoDB 页大小（默认 16KB）
SHOW VARIABLES LIKE 'innodb_page_size';

-- B+Tree 高度估算（用 PerfCalculator 计算器）
-- https://your-site/perf-calc
```

**关键公式：**
```
扇出（fanout）= 索引页大小 / 每条记录大小
叶子节点数 = 总记录数 / 每页记录数
树高度 ≈ log(fanout)(叶子节点数) + 1
```

**示例：1 亿行数据，主键 INT（4 字节）+ 指针（4 字节）：**
- 每页可容纳约 16KB / 14B ≈ 1170 条索引项
- 叶子节点数 = 1亿 / 1170 ≈ 8.5 万
- 树高度 = log(1170)(8.5万) ≈ 2.2 + 1 = **3 层**

3 次磁盘 IO 就能找到 1 亿行中的任意一行！

## 🔍 查询过程

### 等值查询：`WHERE id = 100`

```
1. 读根节点 [17|35]，比较 100 > 35 → 走最右子树
   ↓ 1 次 IO
2. 读中间节点 [35|45|55|65|75|85|95|105|...]，找到 100 的位置
   ↓ 1 次 IO
3. 读叶子节点，找到 id=100 的数据
   ↓ 1 次 IO
总计：3 次 IO ✅
```

### 范围查询：`WHERE id BETWEEN 100 AND 200`

```
1-3. 同上，找到 id=100 的叶子节点
4. 顺着叶子链表向右扫，直到 id=200
总计：3 + N 次 IO（N = 范围内记录数）
```

## 📊 InnoDB 的 B+Tree 索引类型

### 聚簇索引（Clustered Index）

```sql
-- 主键自动创建聚簇索引
CREATE TABLE users (
  id BIGINT PRIMARY KEY,  -- 聚簇索引
  name VARCHAR(100)
);

-- 数据按主键顺序物理存储
-- 叶子节点 = 完整的数据行（不是指针）
```

### 二级索引（Secondary Index）

```sql
-- 普通索引
CREATE INDEX idx_name ON users(name);

-- 叶子节点 = 索引字段值 + 主键值（不是数据指针）
-- 查找到后需要"回表"到聚簇索引拿数据
```

**回表（Bookmark Lookup）：**
```
1. 在 idx_name 中找到 name='张三' → 得到 id=42
2. 用 id=42 去聚簇索引找完整数据
总计：2 棵树的 IO，最坏情况 6 次 IO
```

**优化：覆盖索引（Covering Index）**

```sql
-- 索引包含所有查询字段，无需回表
CREATE INDEX idx_name_age ON users(name, age);

SELECT name, age FROM users WHERE name = '张三';
-- 直接在 idx_name_age 中就能拿到 name + age，无需回表 ✅
```

## ⚙️ B+Tree 插入与删除

### 插入（导致页分裂）

```
插入 id=23

1. 找到叶子节点 [20|30]，插入 [20|23|30]
2. 页满了 → 页分裂（Page Split）
   - 创建新页
   - 一半数据留在原页，一半移到新页
   - 在父节点添加指针
3. 父节点也可能满了 → 继续分裂（级联）
4. 极端情况：根节点分裂 → 树高度 +1
```

**页分裂的危害：**
- 磁盘 IO 翻倍
- 空间利用率下降（每页约半满）
- 插入性能波动

**优化：**
- 使用自增主键（顺序插入，避免随机分裂）
- 设置合理的 `innodb_fill_factor`

### 删除（合并页）

```
删除 id=23

1. 找到叶子节点 [20|23|30]，删除 23 → [20|30]
2. 页使用率 < 阈值 → 合并相邻页
3. 父节点指针同步调整
```

**MERGE_THRESHOLD：**
- 默认 50%（页使用率 < 50% 触发合并）
- 可调整 `innodb_merge_threshold`

## 🎯 索引设计的核心原则

### 1. 选择性高的字段优先

```sql
-- 选择性 = 不重复值 / 总行数
-- 性别（男/女）选择性差 ❌（值只有 2 个）
-- 用户 ID 选择性好 ✅（每行不同）

-- 查看某列的选择性
SELECT
  COUNT(DISTINCT column_name) / COUNT(*) AS selectivity
FROM table_name;
```

### 2. 经常查询的字段建索引

```sql
-- WHERE、JOIN、ORDER BY、GROUP BY 中频繁使用的字段
CREATE INDEX idx_xxx ON table_name(column_name);
```

### 3. 复合索引遵循最左前缀

```sql
-- 复合索引 (a, b, c) 可用于：
-- WHERE a = ?
-- WHERE a = ? AND b = ?
-- WHERE a = ? AND b = ? AND c = ?
-- WHERE a = ? ORDER BY b
-- ❌ 不能跳过 a：WHERE b = ?
-- ❌ 不能跳过 a：WHERE b = ? AND c = ?
```

### 4. 避免冗余索引

```sql
-- 已有 idx(a, b) 时，idx(a) 是冗余的
-- 已有 idx(a) 时，主键索引也是冗余的（除非需要覆盖主键列）
```

## 🧮 用 PerfCalculator 估算你的 B+Tree 高度

转到 [🧮 性能计算器](../11-tools/perf-calculator) → 「B+Tree 高度」标签页，输入你的数据量和扇出，立即看到树高度和总节点数估算。

## ⚠️ 索引失效的常见情况

```sql
-- ❌ 在索引列上使用函数
SELECT * FROM users WHERE DATE(created_at) = '2025-01-15';
-- ✅ 改写
SELECT * FROM users WHERE created_at >= '2025-01-15' AND created_at < '2025-01-16';

-- ❌ 隐式类型转换
SELECT * FROM users WHERE phone = 13800138000;  -- phone 是 VARCHAR
-- ✅
SELECT * FROM users WHERE phone = '13800138000';

-- ❌ LIKE 以通配符开头
SELECT * FROM users WHERE name LIKE '%张%';
-- ✅ 全文索引或前缀匹配
SELECT * FROM users WHERE name LIKE '张%';

-- ❌ OR 前后有一列没索引
SELECT * FROM users WHERE indexed_col = 1 OR non_indexed_col = 'x';
-- ✅ 用 UNION 改写
SELECT * FROM users WHERE indexed_col = 1
UNION
SELECT * FROM users WHERE non_indexed_col = 'x';
```

## 🎯 总结

**B+Tree 的精髓：**
- ✅ 多路平衡树，树高度低（通常 3-4 层）
- ✅ 叶子节点链表，支持高效范围查询
- ✅ 聚簇索引数据即索引，二级索引需回表
- ✅ 顺序插入性能好（自增主键）
- ❌ 随机插入易页分裂
- ❌ 大字段（TEXT/BLOB）不能建索引

**下一步：** [📑 聚簇索引 vs 二级索引](../02-index/clustered) — 深入 InnoDB 的索引存储模型