---
title: 递归 CTE
description: WITH RECURSIVE 实战
---

# 递归 CTE

> **TL;DR**：`WITH RECURSIVE` 是 PG 实现**树形 / 图遍历**的杀手锏。**组织架构、菜单、评论、文件系统、社交关系**全靠它。

## 一句话定义

```
递归 CTE = 基础查询 + 递归部分 UNION ALL
        = 一行行迭代
        = 直到无新行为止
```

## 基本语法

```sql
WITH RECURSIVE cte_name AS (
  -- 非递归部分（基础查询）
  initial_query
  
  UNION ALL  -- 或 UNION
  
  -- 递归部分（引用 cte_name）
  recursive_query
)
SELECT * FROM cte_name;
```

## 案例 1：组织架构树

```sql
-- 数据：employees(id, name, manager_id)
-- 1 (CEO)
-- ├── 2 (CTO, manager=1)
-- │   ├── 4 (Dev1, manager=2)
-- │   └── 5 (Dev2, manager=2)
-- └── 3 (CFO, manager=1)

-- 查 1 的所有下属（无限层）
WITH RECURSIVE subordinates AS (
  -- 基础：CEO
  SELECT id, name, manager_id, 1 AS depth
  FROM employees WHERE id = 1
  
  UNION ALL
  
  -- 递归：subordinates 的下属
  SELECT e.id, e.name, e.manager_id, s.depth + 1
  FROM employees e
  JOIN subordinates s ON e.manager_id = s.id
)
SELECT * FROM subordinates ORDER BY depth, id;
```

## 案例 2：菜单树

```sql
-- 数据：menu_items(id, name, parent_id)
-- 1 (首页)
-- ├── 2 (产品, parent=1)
-- │   ├── 4 (产品A, parent=2)
-- │   └── 5 (产品B, parent=2)
-- └── 3 (关于, parent=1)

WITH RECURSIVE menu AS (
  SELECT id, name, parent_id, 0 AS level, 
         ARRAY[id] AS path
  FROM menu_items WHERE parent_id IS NULL
  
  UNION ALL
  
  SELECT m.id, m.name, m.parent_id, menu.level + 1,
         menu.path || m.id
  FROM menu_items m
  JOIN menu ON m.parent_id = menu.id
)
SELECT * FROM menu;
-- 包含每个节点的层级 + 路径
```

## 案例 3：评论树

```sql
-- 数据：comments(id, content, parent_id, created_at)
WITH RECURSIVE comment_tree AS (
  SELECT id, content, parent_id, created_at, 0 AS depth
  FROM comments WHERE id = 100  -- 根评论
  
  UNION ALL
  
  SELECT c.id, c.content, c.parent_id, c.created_at, t.depth + 1
  FROM comments c
  JOIN comment_tree t ON c.parent_id = t.id
)
SELECT * FROM comment_tree ORDER BY depth, created_at;
```

## 案例 4：图遍历（最短路径）

```sql
-- 数据：edges(from_node, to_node, weight)
-- A -> B (5), B -> C (3), A -> C (10)

WITH RECURSIVE paths(node, total_cost, path) AS (
  -- 起点
  SELECT 'A', 0, ARRAY['A']
  
  UNION ALL
  
  SELECT e.to_node, p.total_cost + e.weight, p.path || e.to_node
  FROM paths p
  JOIN edges e ON e.from_node = p.node
  WHERE NOT (e.to_node = ANY(p.path))  -- 防环
)
SELECT * FROM paths WHERE node = 'C' ORDER BY total_cost LIMIT 1;
-- A -> B -> C (cost=8) < A -> C (cost=10)
```

## 案例 5：JSON 树遍历

```sql
-- 嵌套 JSON 找所有叶子节点
WITH RECURSIVE json_tree AS (
  SELECT 
    '{"a": {"b": 1, "c": {"d": 2}}}'::jsonb AS data,
    ARRAY[]::text[] AS path
  
  UNION ALL
  
  SELECT 
    jsonb_path_query(data, '$.*'),
    path || (key)
  FROM json_tree, jsonb_object_keys(data) AS key
)
SELECT * FROM json_tree;
```

## 防止无限循环

```sql
-- 方法 1：路径数组
WITH RECURSIVE ... AS (
  ...
  UNION ALL
  ...
  -- 检查是否已在路径中
  WHERE NOT (new_node = ANY(path))
)

-- 方法 2：CYCLE 子句（PG 14+）
WITH RECURSIVE ... CYCLE node SET is_cycle USING path
```

## 性能优化

```sql
-- 1. 限制递归深度（防意外无限循环）
WITH RECURSIVE ... AS (
  ...
  UNION ALL
  ...
  WHERE depth < 100  -- 限制 100 层
)

-- 2. 物化递归 CTE（PG 12+）
WITH RECURSIVE ... AS MATERIALIZED (
  ...
)
SELECT ... FROM ...
-- 同名 CTE 只计算一次
```

## 实战案例

### 案例：员工所有下属（含层级路径）

```sql
WITH RECURSIVE emp_tree AS (
  SELECT id, name, manager_id, 0 AS level,
         ARRAY[name]::text[] AS path
  FROM employees WHERE id = 1
  
  UNION ALL
  
  SELECT e.id, e.name, e.manager_id, t.level + 1,
         t.path || e.name
  FROM employees e
  JOIN emp_tree t ON e.manager_id = t.id
  WHERE t.level < 10  -- 防 10 层以上
)
SELECT 
  level,
  repeat('  ', level) || name AS indented_name,
  array_to_string(path, ' → ') AS full_path
FROM emp_tree ORDER BY level, name;
```

## 一句话总结

> **递归 CTE = PG 处理树和图的标准方案**。**组织架构、菜单、评论、文件树、社交网络**全靠它。**关键三段**：**基础查询 + 递归查询 + 终止条件（CYCLE 或 path 检查）**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
