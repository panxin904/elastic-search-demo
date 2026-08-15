---
title: 聚簇索引 vs 二级索引
---

# 📑 聚簇索引 vs 二级索引

> InnoDB 的特殊设计：**数据即索引，索引即数据**。理解这个区别，你就理解了为什么 InnoDB 主键如此重要。

## 🏛️ 聚簇索引（Clustered Index）

### 定义

聚簇索引的**叶子节点直接存储完整的数据行**，数据按主键顺序物理存储。

```
聚簇索引的 B+Tree：

                ┌─────────────┐
                │  Root        │  [10 | 20 | 30]
                └─┬──────┬─────┘
                  │      │
        ┌─────────▼─┐  ┌─▼──────────┐
        │ Internal   │  │ Internal   │  [30 | 40 | 50]
        └─┬──┬──┬───┘  └─┬──┬──┬───┘
          │  │  │        │  │  │
       ┌──▼──▼──▼──┐  ┌──▼──▼──▼──┐
       │ Leaf 页1   │  │ Leaf 页2   │
       │ ┌────────┐  │  │ ┌────────┐  │
       │ │id=10   │  │  │ │id=30   │  │
       │ │name=张三│  │  │ │name=王五│  │
       │ │age=25  │  │  │ │age=30  │  │
       │ ├────────┤  │  │ ├────────┤  │
       │ │id=11   │  │  │ │id=31   │  │
       │ │name=李四│  │  │ │name=赵六│  │
       │ │age=28  │  │  │ │age=35  │  │
       │ └────────┘  │  │ └────────┘  │
       └──────────────┘  └──────────────┘

💡 叶子节点 = 完整的数据行（不是指针！）
```

### InnoDB 聚簇索引的特点

- ✅ **每张表只能有一个聚簇索引**
- ✅ InnoDB 的数据文件（.ibd）本身就是按聚簇索引组织的
- ✅ 数据按主键顺序物理存储 → 范围查询极快
- ✅ 主键查询极快（直接定位到数据）

### 聚簇索引的选择规则

```sql
-- 1. 有主键：用主键
-- 2. 没有主键：用第一个非空唯一索引
-- 3. 都没有：InnoDB 自动生成一个隐藏的 row_id（6 字节）
```

```sql
-- 检查表的聚簇索引信息
SELECT
  table_name,
  index_name,
  column_name,
  seq_in_index
FROM information_schema.statistics
WHERE table_schema = DATABASE()
  AND index_name = 'PRIMARY';
```

## 🌿 二级索引（Secondary Index）

### 定义

二级索引的**叶子节点存储「索引字段值 + 主键值」**，不存储完整数据。

```
二级索引 idx_name 的 B+Tree：

                ┌─────────────┐
                │  Root        │  [李 | 王]
                └─┬──────┬─────┘
                  │      │
        ┌─────────▼─┐  ┌─▼──────────┐
        │ Internal   │  │ Internal   │  [张 | 周]
        └─┬──┬──┬───┘  └─┬──┬──┬───┘
          │  │  │        │  │  │
       ┌──▼──▼──▼──┐  ┌──▼──▼──▼──┐
       │ Leaf 页1   │  │ Leaf 页2   │
       │ ┌────────┐  │  │ ┌────────┐  │
       │ │name=张三│  │  │ │name=王五│  │
       │ │id=1    │  │  │ │id=3    │  │  ← 只有 name + 主键 id
       │ ├────────┤  │  │ ├────────┤  │
       │ │name=李四│  │  │ │name=赵六│  │
       │ │id=2    │  │  │ │id=4    │  │
       │ └────────┘  │  │ └────────┘  │
       └──────────────┘  └──────────────┘

💡 叶子节点 = 索引字段值 + 主键值（不存完整数据！）
```

### 为什么这样设计？

- ✅ 节省空间（不重复存数据）
- ✅ 插入新数据时，只需更新聚簇索引，二级索引同步更新
- ⚠️ 查询非索引字段时需要"回表"

## 🔄 回表（Bookmark Lookup）

```sql
-- 假设表 users 有聚簇索引(id) 和二级索引(name)
SELECT * FROM users WHERE name = '张三';
```

**执行过程：**

```
1. 在二级索引 idx_name 中查找 name='张三'
   → 找到 id=1
   ↓

2. 用 id=1 去聚簇索引查找完整数据
   → 找到完整行（name='张三', age=25, ...）
   ↓

3. 返回结果

总共：2 棵树的 IO，最坏情况 6 次磁盘 IO
```

**回表的代价：**
- 每条记录多一次聚簇索引查询
- 如果二级索引命中 1000 条记录 → 1000 次回表 → 慢！

## 🎯 覆盖索引：避免回表

**如果二级索引已经包含查询需要的所有字段，就不需要回表了！**

```sql
-- 表结构
CREATE TABLE users (
  id BIGINT PRIMARY KEY,
  name VARCHAR(50),
  age INT,
  email VARCHAR(100)
);

-- 创建覆盖索引（包含 name 和 age）
CREATE INDEX idx_name_age ON users(name, age);

-- ✅ 覆盖索引：不需要回表
SELECT name, age FROM users WHERE name = '张三';
-- 在 idx_name_age 中就能拿到 name + age，直接返回 ✅

-- ❌ 需要回表
SELECT name, age, email FROM users WHERE name = '张三';
-- 在 idx_name_age 中只有 name + age，没有 email → 回表查 email
```

**判断是否覆盖：**

```sql
-- 用 EXPLAIN 看 Extra 列
EXPLAIN SELECT name, age FROM users WHERE name = '张三';
-- Extra: Using index ✅ 覆盖索引
-- Extra: NULL    ❌ 需要回表
```

## 🎨 索引的物理存储

```
.ibd 文件结构（InnoDB 表空间文件）：

┌────────────────────────────────────┐
│        Tablespace Header           │
├────────────────────────────────────┤
│                                    │
│  Segment 1: 聚簇索引               │
│  ┌──────────────────────────┐      │
│  │ Leaf Node Segment         │ ← 数据行
│  │ - Page 1 (16KB)          │
│  │ - Page 2 (16KB)          │
│  │ - Page 3 (16KB)          │
│  └──────────────────────────┘      │
│  ┌──────────────────────────┐      │
│  │ Non-leaf Node Segment    │ ← 内部节点
│  └──────────────────────────┘      │
│                                    │
│  Segment 2: 二级索引 idx_name      │
│  ┌──────────────────────────┐      │
│  │ Leaf Node Segment         │ ← name + id
│  └──────────────────────────┘      │
│                                    │
│  Segment 3: 二级索引 idx_age       │
│  ┌──────────────────────────┐      │
│  │ Leaf Node Segment         │ ← age + id
│  └──────────────────────────┘      │
│                                    │
└────────────────────────────────────┘
```

## 🎯 主键设计的最佳实践

### 1. 使用自增主键（推荐）

```sql
CREATE TABLE orders (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  -- 自增 ID 是顺序的，插入时：
  -- 1. 永远在最后一页写入
  -- 2. 不会触发页分裂
  -- 3. 磁盘 IO 是顺序的，性能最佳
  user_id BIGINT NOT NULL,
  amount DECIMAL(10, 2)
) ENGINE=InnoDB;
```

### 2. 避免 UUID 作为主键（性能差）

```sql
-- ❌ UUID 主键
CREATE TABLE bad_uuid (
  id CHAR(36) PRIMARY KEY,  -- 'a3f5b8c9-1234-5678-...'
  name VARCHAR(50)
);

-- 问题：
-- 1. UUID 是随机的，插入时随机写到不同页 → 大量页分裂
-- 2. UUID 36 字节，比 INT 大 9 倍 → 索引页能容纳的 key 少 → 树更高
-- 3. 二级索引叶子节点 = UUID(36字节) + 主键(36字节) = 72 字节
--    比自增主键（4-8 字节）大很多

-- ✅ 如果必须用 UUID
CREATE TABLE better_uuid (
  id BINARY(16) PRIMARY KEY,           -- 16 字节二进制
  uuid CHAR(36) NOT NULL,
  UNIQUE KEY uk_uuid (uuid)             -- 用普通唯一索引存储 UUID
);
```

### 3. 联合主键的坑

```sql
-- ❌ 多字段联合主键
CREATE TABLE order_items (
  order_id BIGINT,
  product_id BIGINT,
  quantity INT,
  PRIMARY KEY (order_id, product_id)
);

-- 问题：
-- 1. 二级索引叶子节点 = (order_id, product_id) + 主键(order_id, product_id) = 重复！
-- 2. 占用空间大
-- 3. 性能差

-- ✅ 推荐：使用自增主键 + 唯一索引
CREATE TABLE order_items (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  order_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity INT,
  UNIQUE KEY uk_order_product (order_id, product_id)
);
```

### 4. 主键不要太长

```sql
-- ❌ 主键太长（如 VARCHAR(100)）
CREATE TABLE bad_pk (
  id VARCHAR(100) PRIMARY KEY  -- 100 字节
);

-- 问题：
-- 1. 所有二级索引都要存这个主键 → 所有索引都变大
-- 2. 索引页能容纳的 key 少 → 树更高 → IO 更多

-- 建议：
-- - 主键尽量小：INT (4B) / BIGINT (8B)
-- - 业务字段做唯一索引即可，不必做主键
```

## 🔍 实战：查看索引使用情况

```sql
-- 查看某个查询是否走了索引
EXPLAIN SELECT * FROM users WHERE name = '张三';
-- type=ref、key=idx_name → 用了二级索引
-- Extra=NULL → 需要回表

-- 查看是否覆盖索引
EXPLAIN SELECT name, age FROM users WHERE name = '张三';
-- type=ref、key=idx_name_age
-- Extra=Using index → 覆盖索引，无需回表 ✅
```

## 📊 聚簇索引 vs 二级索引 对比

| 特性 | 聚簇索引 | 二级索引 |
|---|---|---|
| 数量 | 每表 1 个 | 多个 |
| 叶子节点 | 完整数据行 | 索引字段 + 主键 |
| 大小 | 数据本身 | 通常比聚簇索引小 |
| 范围查询 | 极快（数据连续） | 需要回表多次 |
| INSERT | 性能好（顺序） | 需同步更新 |
| UPDATE 主键 | 昂贵（行移动） | 索引也要更新 |
| 唯一性 | 必须唯一 | 可不唯一 |

## 🎯 总结

**聚簇索引：**
- ✅ 数据按主键物理存储
- ✅ 叶子节点 = 完整数据行
- ✅ 主键查询极快，范围查询也快
- ⚠️ 更新主键代价高（行移动）

**二级索引：**
- ✅ 叶子节点 = 索引字段 + 主键
- ⚠️ 需要回表（除非覆盖索引）
- 💡 设计为覆盖索引可大幅提升性能

**主键设计黄金法则：**
1. 用自增 BIGINT UNSIGNED
2. 不要用 UUID / 业务字段做主键
3. 主键要小（影响所有二级索引大小）
4. 单字段主键优于联合主键

**下一步：** [✅ 覆盖索引与最左前缀](../02-index/covering) — 索引优化的两大利器