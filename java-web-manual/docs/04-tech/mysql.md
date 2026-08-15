---
title: MySQL
---

# MySQL

MySQL 是 Java Web 开发中最常用的关系型数据库。

## 索引原理

```
B+ 树索引结构:
         [8]
        /   \
    [3,5]   [10,15]
    / | \    /  |  \
  [1][4][6] [9][12][18]

非叶子节点存键值+指针，叶子节点存完整数据（聚簇索引）
或主键值（二级索引 → 回表）
```

## 索引类型

| 类型 | 说明 | 使用场景 |
|---|---|---|
| 主键索引 | 唯一、非空、聚簇 | 每表必须有 |
| 唯一索引 | 唯一、允许空 | 手机号、用户名 |
| 普通索引 | 加速查询 | 高频查询字段 |
| 联合索引 | 多列组合 | 多条件查询 |
| 全文索引 | 文本搜索 | 文章内容搜索 |

## Explain 分析 SQL

```sql
EXPLAIN SELECT * FROM t_order WHERE user_id = 100;
```

关键字段：

| 字段 | 含义 |
|---|---|
| type | 访问类型：ALL(全表) < index < range < ref < eq_ref < const(最优) |
| key | 实际使用的索引 |
| rows | 预估扫描行数 |
| Extra | Using index(覆盖索引，好) / Using filesort(需优化) / Using temporary(需优化) |

## 常见优化

```sql
-- ❌ 隐式类型转换，不走索引
SELECT * FROM t_user WHERE phone = 13800000000;
-- ✅ 字符串字段用字符串查询
SELECT * FROM t_user WHERE phone = '13800000000';

-- ❌ 左模糊不走索引
SELECT * FROM t_user WHERE username LIKE '%张三';
-- ✅ 右模糊走索引
SELECT * FROM t_user WHERE username LIKE '张三%';
```

## 图谱关联

<KnowledgeGraph mode="neighbor" focusNodeId="mysql" :height="400" />
