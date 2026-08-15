---
title: JSONB 类型
---

# JSONB 类型

> PostgreSQL 的"杀手锏"——既是关系型数据库，又是文档数据库。**JSONB + GIN = 文档 + 索引**。

## 1. JSON vs JSONB

```
JSON：
  - 文本存储
  - 保留空格、键顺序、重复键
  - 不支持索引（只能全表扫描）
  - 适合：保留原始 JSON 格式

JSONB：
  - 二进制存储
  - 去除冗余（空格 / 重复键 / 键顺序）
  - 支持 GIN 索引
  - 适合：查询 + 索引

性能：
  - 写入：JSON 比 JSONB 快（无需处理）
  - 查询：JSONB 比 JSON 快（无需解析）
  - 存储：JSONB 比 JSON 略大（多二进制头）

📌 99% 场景用 JSONB
```

## 2. 基本操作

### 2.1 创建与插入

```sql
-- 创建表
CREATE TABLE products (
  id    BIGSERIAL PRIMARY KEY,
  data  JSONB NOT NULL
);

-- 插入 JSONB
INSERT INTO products (data) VALUES
  ('{"name": "iPhone 15", "price": 7999, "tags": ["phone", "apple"], "specs": {"cpu": "A17", "ram": 8}}'),
  ('{"name": "MacBook Pro", "price": 15999, "tags": ["laptop", "apple"], "specs": {"cpu": "M3", "ram": 16}}');

-- 转换 JSON → JSONB
INSERT INTO products (data)
SELECT '{"key": "value"}'::JSONB;
```

### 2.2 查询操作符

```sql
-- -> 返回 JSONB（嵌套字段保持 JSONB 类型）
SELECT data->'name' FROM products;  -- "iPhone 15"

-- ->> 返回 TEXT（嵌套字段转为文本）
SELECT data->>'name' FROM products;  -- iPhone 15

-- #> 路径查询
SELECT data#>'{specs,cpu}' FROM products;  -- "A17"

-- #>> 路径返回 TEXT
SELECT data#>>'{specs,cpu}' FROM products;  -- A17

-- @> 包含（最常用）
SELECT * FROM products WHERE data @> '{"tags": ["phone"]}';

-- ?  包含键
SELECT * FROM products WHERE data ? 'tags';

-- ?| 包含任一键
SELECT * FROM products WHERE data ?| ARRAY['tags', 'brand'];

-- ?& 包含所有键
SELECT * FROM products WHERE data ?& ARRAY['tags', 'specs'];
```

### 2.3 修改操作

```sql
-- jsonb_set 修改字段
UPDATE products
SET data = jsonb_set(data, '{price}', '6999')
WHERE data->>'name' = 'iPhone 15';

-- jsonb_set 嵌套
UPDATE products
SET data = jsonb_set(data, '{specs,ram}', '16');

-- || 合并 JSONB
UPDATE products
SET data = data || '{"brand": "Apple"}'::JSONB;

-- - 删除键
UPDATE products
SET data = data - 'tags';

-- #- 删除路径
UPDATE products
SET data = data #- '{specs,cpu}';

-- jsonb_strip_nulls 去除 null
SELECT jsonb_strip_nulls(data) FROM products;
```

### 2.4 函数

```sql
-- jsonb_array_length
SELECT jsonb_array_length(data->'tags') FROM products;

-- jsonb_object_keys
SELECT jsonb_object_keys(data->'specs') FROM products;

-- jsonb_pretty
SELECT jsonb_pretty(data) FROM products;

-- jsonb_path_query
SELECT jsonb_path_query(data, '$.specs.*') FROM products;
```

## 3. JSONB 索引（核心）

### 3.1 GIN 索引

```sql
-- 默认 ops（jsonb_ops）：支持 @> / ? / ?| / ?&
CREATE INDEX idx_products_data ON products USING GIN (data);

-- 性能示例
-- 无索引：Seq Scan products （100ms+）
-- 有 GIN：Bitmap Heap Scan （5ms）

EXPLAIN ANALYZE
SELECT * FROM products WHERE data @> '{"tags": ["phone"]}';
```

### 3.2 jsonb_path_ops 索引

```sql
-- 更紧凑，仅支持 @>
CREATE INDEX idx_products_data_path ON products USING GIN (data jsonb_path_ops);

-- 性能：比默认 GIN 索引快 30-50%
-- 体积：约 1/3
-- 限制：只支持 @>，不支持 ? / ?| / ?&
```

### 3.3 表达式索引

```sql
-- 只索引 JSONB 中的某个字段
CREATE INDEX idx_products_name ON products ((data->>'name'));

-- 唯一约束
CREATE UNIQUE INDEX idx_products_unique_name
ON products ((data->>'name'));

-- 多字段复合索引
CREATE INDEX idx_products_brand_price
ON products ((data->>'brand'), ((data->>'price')::NUMERIC));
```

### 3.4 索引选型

```
场景                          推荐索引
─────────────────────────────────────────
@> 包含查询                    jsonb_path_ops GIN
@> + ? + ?| + ?&               默认 GIN（jsonb_ops）
查询具体字段                    B-Tree 表达式索引
组合查询                        多个表达式索引
全文检索                        tsvector + GIN
```

## 4. 性能基准

### 4.1 写入性能

```
100 万行写入：
  - JSON：45s
  - JSONB：55s（多 22%）
  - 原因：JSONB 要解析 + 二进制化
```

### 4.2 查询性能（100 万行）

```
场景：data @> '{"tags": ["phone"]}'
  - 无索引：Seq Scan 850ms
  - GIN jsonb_ops：Bitmap Heap Scan 12ms（70x）
  - GIN jsonb_path_ops：Bitmap Heap Scan 8ms（100x）
```

### 4.3 存储体积

```
100 万行 products 表：
  - JSON：520 MB
  - JSONB：380 MB（更紧凑）
  - 原因：JSONB 去重 + 二进制编码
```

## 5. 与 MongoDB 对比

| 维度 | PostgreSQL JSONB | MongoDB |
|---|---|---|
| 数据模型 | 关系 + 文档（混合） | 纯文档 |
| 索引 | GIN 表达式索引 | B-Tree / 全文 / 地理 |
| 事务 | ACID 完整 | 4.0+ 多文档事务 |
| 查询 | SQL + JSONB 操作符 | MongoDB Query Language |
| 跨表 JOIN | 原生支持 | $lookup（性能差） |
| 学习成本 | 高（SQL + JSONB） | 低（类 JSON） |
| 适合 | 已用 PG + 需要 JSON | 纯文档场景 |

📌 PG JSONB 适合：已有 PG 生态、需要事务、需要 SQL 关联
   MongoDB 适合：纯文档、Schema 灵活、性能极致

## 6. 工程实践

### 6.1 Schema 设计

```sql
-- 方式 1：纯 JSONB（灵活）
CREATE TABLE events (
  id    BIGSERIAL PRIMARY KEY,
  data  JSONB
);

-- 方式 2：关系 + JSONB（推荐）
CREATE TABLE orders (
  id          BIGSERIAL PRIMARY KEY,
  user_id     BIGINT NOT NULL,
  total       NUMERIC(10,2),
  metadata    JSONB,  -- 灵活的附加信息
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 方式 3：JSONB + 部分关系字段
CREATE TABLE products (
  id          BIGSERIAL PRIMARY KEY,
  sku         VARCHAR(32) NOT NULL,
  price       NUMERIC(10,2) NOT NULL,  -- 常用字段
  attributes  JSONB  -- 不常用字段
);
```

### 6.2 查询模式

```sql
-- 模式 1：精确查询
SELECT * FROM products
WHERE data @> '{"brand": "Apple", "tags": ["laptop"]}';

-- 模式 2：范围查询
SELECT * FROM products
WHERE (data->>'price')::NUMERIC BETWEEN 5000 AND 10000;

-- 模式 3：数组包含
SELECT * FROM products
WHERE data->'tags' ? 'phone';

-- 模式 4：路径查询
SELECT * FROM products
WHERE data#>>'{specs,cpu}' = 'M3';

-- 模式 5：JSONB 聚合
SELECT
  data->>'brand' AS brand,
  COUNT(*),
  AVG((data->>'price')::NUMERIC) AS avg_price
FROM products
GROUP BY data->>'brand';
```

### 6.3 索引策略

```sql
-- 必备：JSONB GIN 索引
CREATE INDEX idx_events_data ON events USING GIN (data);

-- 必备：高频字段表达式索引
CREATE INDEX idx_events_user ON events ((data->>'user_id'));

-- 可选：复合索引
CREATE INDEX idx_events_type_time
ON events ((data->>'event_type'), created_at);

-- 注意：避免在 JSONB 字段上建过多索引
-- 索引越多 = 写入越慢
```

## 7. 经典案例

### 7.1 电商商品属性

```sql
-- 不同品类有不同属性
CREATE TABLE products (
  id    BIGSERIAL PRIMARY KEY,
  name  TEXT,
  attrs JSONB  -- {"color": "red", "size": "XL", "material": "cotton"}
);

-- 查询所有红色商品
SELECT * FROM products WHERE attrs @> '{"color": "red"}';

-- 查询红色 + 棉质
SELECT * FROM products WHERE attrs @> '{"color": "red", "material": "cotton"}';
```

### 7.2 用户标签系统

```sql
CREATE TABLE users (
  id     BIGSERIAL PRIMARY KEY,
  name   TEXT,
  tags   JSONB  -- {"interests": ["tech", "music"], "level": "vip"}
);

-- 找出对 tech 感兴趣的 VIP 用户
SELECT * FROM users
WHERE tags @> '{"interests": ["tech"]}'
  AND tags->>'level' = 'vip';
```

### 7.3 审计日志

```sql
CREATE TABLE audit_logs (
  id         BIGSERIAL PRIMARY KEY,
  actor_id   BIGINT,
  action     TEXT,
  payload    JSONB,  -- 操作的完整数据
  created_at TIMESTAMPTZ
);

CREATE INDEX idx_audit_actor ON audit_logs (actor_id);
CREATE INDEX idx_audit_payload ON audit_logs USING GIN (payload);
```

## 8. 常见误区

### 8.1 不建 JSONB 索引

```
问题：
  - SELECT ... WHERE data @> '...' 走全表扫描
  - 数据量 100万+ 性能不可接受

解决：
  - 必须建 GIN 索引
  - jsonb_path_ops 更紧凑更快
```

### 8.2 把所有字段都塞 JSONB

```
问题：
  - 失去类型校验
  - 失去外键约束
  - 查询性能下降

原则：
  - 常用字段：独立列
  - 不常用 + 灵活：JSONB
  - 关键字段（如价格）：独立列 + 索引
```

### 8.3 不理解 @> 顺序

```sql
-- @> 左侧必须包含右侧所有内容
'{"a": 1, "b": 2}'::JSONB @> '{"a": 1}'::JSONB  -- true ✓
'{"a": 1}'::JSONB @> '{"a": 1, "b": 2}'::JSONB  -- false ✗

-- 数组包含语义
'["a", "b", "c"]'::JSONB @> '["a"]'::JSONB  -- true
'["a"]'::JSONB @> '["a", "b", "c"]'::JSONB  -- false
```

## 9. 一句话总结

```
📌 JSONB = PG 的杀手锏，让关系型 + 文档型合体
📌 vs JSON：JSONB 二进制 + 支持索引，99% 场景用 JSONB
📌 索引：GIN（jsonb_ops 默认 / jsonb_path_ops 更快）
📌 操作符：-> / ->> / #> / @> / ? / ?| / ?&
📌 性能：GIN 索引比全表扫描快 70-100x
📌 设计原则：常用字段独立列 + 不常用 JSONB
📌 适合：商品属性 / 用户标签 / 审计日志 / 配置
📌 vs MongoDB：PG JSONB 适合已有 PG + 需要 SQL 关联 + 事务
```

## 10. 参考资料

- PostgreSQL 8.4 JSONB 引入（2009）
- PostgreSQL 12 JSONB 路径操作符
- "PostgreSQL: Up and Running"（O'Reilly）
- PG 官方文档：JSON Types
- 9.4+ JSONB 函数索引最佳实践
- Supabase PG JSONB 案例