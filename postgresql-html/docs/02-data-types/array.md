---
title: 数组类型
description: PostgreSQL 原生数组类型详解
---

# 数组类型

> **TL;DR**：PG 是少数**原生支持数组**的 RDBMS（其他如 MySQL 需要字符串拆分）。数组字段用 GIN 索引后**元素查询从 5s 降到 5ms**，是 PG 标签/多值场景的杀手锏。

## 一句话定义

```
PG 数组 = 任意基础类型的一维/多维有序集合，元素可重复
```

## 基本使用

### 声明与初始化

```sql
-- 1. 创建带数组字段的表
CREATE TABLE articles (
  id BIGSERIAL PRIMARY KEY,
  title TEXT,
  tags TEXT[],
  scores NUMERIC[3][4]            -- 多维数组
);

-- 2. 多种初始化方式
INSERT INTO articles (title, tags) VALUES
  ('PostgreSQL 入门', ARRAY['PostgreSQL', '数据库', '入门']),
  ('Redis 实战', '{"Redis", "缓存", "实战"}'),  -- 字符串字面量
  ('空数组', '{}');

-- 3. 多维数组
INSERT INTO articles VALUES (3, '矩阵', ARRAY[1.0, 2.0], ARRAY[[1,2],[3,4]]);
```

### 查询与修改

```sql
-- 1. 访问（PG 数组下标从 1 开始）
SELECT tags[1] FROM articles WHERE id = 1;        -- 'PostgreSQL'
SELECT tags[1:2] FROM articles WHERE id = 1;     -- 切片 ['PostgreSQL', '数据库']

-- 2. 长度
SELECT array_length(tags, 1) FROM articles WHERE id = 1;  -- 3

-- 3. 包含元素
SELECT * FROM articles WHERE 'PostgreSQL' = ANY(tags);
SELECT * FROM articles WHERE 'PostgreSQL' = ALL(tags);  -- 所有元素都是（不太实用）

-- 4. 重叠（任一匹配）
SELECT * FROM articles WHERE tags && ARRAY['PostgreSQL', 'Redis'];

-- 5. 包含全部
SELECT * FROM articles WHERE tags @> ARRAY['PostgreSQL'];
SELECT * FROM articles WHERE tags <@ ARRAY['PostgreSQL', '数据库', '入门', 'extra'];

-- 6. 追加元素
UPDATE articles 
SET tags = tags || '新标签'      -- 末尾追加
WHERE id = 1;

UPDATE articles 
SET tags = ARRAY['置顶'] || tags -- 开头插入
WHERE id = 1;

-- 7. 删除元素
UPDATE articles 
SET tags = array_remove(tags, '入门')
WHERE id = 1;

-- 8. 去重
UPDATE articles 
SET tags = ARRAY(SELECT DISTINCT unnest(tags))
WHERE id = 1;
```

## 数组操作符

| 操作符 | 含义 | 例子 |
|---|---|---|
| `=` | 数组相等 | `tags = ARRAY['a', 'b']` |
| `<>` | 不等 | `tags <> '{}'` |
| `@>` | 包含 | `tags @> ARRAY['a']` |
| `<@` | 被包含 | `ARRAY['a'] <@ tags` |
| `&&` | 重叠（有任一相同元素） | `tags && ARRAY['a']` |
| `\|\|` | 拼接 | `tags \|\| ARRAY['b']` |
| `ANY()` | 任一元素满足 | `'a' = ANY(tags)` |

## 数组函数

```sql
-- 1. unnest：数组 → 行集
SELECT unnest(tags) FROM articles WHERE id = 1;
-- PostgreSQL
-- 数据库
-- 入门

-- 2. array_agg：行集 → 数组（聚合的逆操作）
SELECT user_id, array_agg(order_id ORDER BY created_at) FROM orders
GROUP BY user_id;

-- 3. array_length：数组长度
SELECT array_length(tags, 1) FROM articles;

-- 4. array_append / array_prepend
SELECT array_append(tags, '尾') FROM articles;
SELECT array_prepend('头', tags) FROM articles;

-- 5. array_cat：拼接
SELECT array_cat(ARRAY[1,2], ARRAY[3,4]);  -- {1,2,3,4}

-- 6. array_remove / array_replace
SELECT array_remove(ARRAY[1,2,3,2], 2);  -- {1,3}

-- 7. array_position：元素位置
SELECT array_position(ARRAY['a','b','c'], 'b');  -- 2

-- 8. array_to_string / string_to_array：数组 ↔ 字符串
SELECT array_to_string(tags, ',') FROM articles;  -- 'PostgreSQL,数据库,入门'
SELECT string_to_array('a,b,c', ',');  -- {a,b,c}
```

## 数组索引（GIN）

```sql
-- 1. 创建 GIN 索引
CREATE INDEX idx_articles_tags ON articles USING GIN (tags);

-- 2. @> 查询用索引
SELECT * FROM articles WHERE tags @> ARRAY['PostgreSQL'];
-- Index Scan using idx_articles_tags

-- 3. && 查询也用索引
SELECT * FROM articles WHERE tags && ARRAY['PostgreSQL', 'Redis'];
-- Index Scan

-- 4. 单元素查询用 ANY
SELECT * FROM articles WHERE 'PostgreSQL' = ANY(tags);
-- Index Scan using idx_articles_tags
```

**性能对比**（百万行表）：

| 查询 | 无索引 | GIN 索引 |
|---|---|---|
| `tags @> ARRAY['x']` | 5000ms | 5ms |
| `tags && ARRAY['x', 'y']` | 5000ms | 10ms |

> **结论**：**数组字段必须建 GIN 索引**，否则查询性能极差。

## 多维数组

```sql
-- 1. 声明
CREATE TABLE matrix (
  m INT[][]
);

INSERT INTO matrix VALUES 
  (ARRAY[[1,2,3],[4,5,6]]);

-- 2. 访问
SELECT m[1][2] FROM matrix;  -- 2
SELECT m[1:2][1:1] FROM matrix;  -- 切片 {{1},{4}}

-- 3. 多维 GIN（少见）
CREATE INDEX idx_matrix ON matrix USING GIN (m);
```

> **注意**：多维数组不能跨维度索引，**实战用得少**，通常用 JSONB 替代。

## 数组 vs JSONB

| 维度 | 数组 | JSONB |
|---|---|---|
| 元素类型 | 必须同 | 可异构 |
| 嵌套 | 不支持 | 支持 |
| 索引 | GIN | GIN |
| 查询能力 | `&&`、`@>`、`ANY` | `->`、`@>`、`?` |
| 适用 | 简单标签列表 | 复杂嵌套结构 |

**选型决策**：

```
数据是简单同构列表（如 tags）？
├─ 是 → 用数组
└─ 否（嵌套 / 异构）→ 用 JSONB
```

## 实战案例

### 案例 1：商品多标签筛选

```sql
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  tags TEXT[]
);

CREATE INDEX idx_products_tags ON products USING GIN (tags);

-- 查找同时有"electronics"和"laptop"标签的商品
SELECT * FROM products 
WHERE tags @> ARRAY['electronics', 'laptop'];

-- 查找任一标签匹配的商品
SELECT * FROM products 
WHERE tags && ARRAY['electronics', 'furniture'];
```

### 案例 2：用户多角色权限

```sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  roles TEXT[]
);

-- 用户有任一指定角色
SELECT * FROM users WHERE 'admin' = ANY(roles);

-- 用户同时拥有多个角色
SELECT * FROM users WHERE roles @> ARRAY['admin', 'editor'];

-- 给用户加角色
UPDATE users SET roles = roles || 'moderator' WHERE id = 1;
```

### 案例 3：日志标签聚合

```sql
-- 错误日志表
CREATE TABLE error_logs (
  id BIGSERIAL PRIMARY KEY,
  level TEXT,
  tags TEXT[],  -- ['http', 'api', 'timeout']
  message TEXT,
  created_at TIMESTAMPTZ
);

-- 找所有 'timeout' 错误，按 tag 出现次数排序
SELECT 
  unnest(tags) AS tag,
  count(*) AS cnt
FROM error_logs
WHERE tags && ARRAY['timeout'] AND created_at > now() - interval '1 hour'
GROUP BY tag
ORDER BY cnt DESC;
```

## 数组最佳实践

### 1. 数组长度不要过大

```sql
-- ❌ 单字段存 1000+ 元素（违反第一范式）
-- ✅ 拆到子表
CREATE TABLE article_tags (
  article_id BIGINT,
  tag TEXT,
  PRIMARY KEY (article_id, tag)
);
```

> **经验**：**数组元素 ≤ 20** 是好实践；超过 1000 应该拆表。

### 2. 数组不能是 NOT NULL 元素

```sql
-- ❌ 数组本身可空，但元素没有 NOT NULL 约束
tags TEXT[] NOT NULL  -- 数组本身不能为 NULL

-- ❌ 元素可以 NULL
INSERT INTO articles (tags) VALUES (ARRAY[NULL, 'a']);  -- 允许
```

### 3. 数组里不能存复杂类型

```sql
-- ❌ 数组里不能放数组
-- tags TEXT[][]  -- 二维，可以
-- tags TEXT[][][]  -- 三维，可以
-- tags INT[][]  -- 但不能放复合类型数组

-- ✅ 复杂结构用 JSONB
data JSONB
```

## 一句话总结

> **PG 数组 = 简单多值场景的最佳选择**：标签、角色、权限。**配 GIN 索引后查询性能提升 1000x**。**元素 ≤ 20、避免复杂嵌套、不要违反第一范式**。

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
