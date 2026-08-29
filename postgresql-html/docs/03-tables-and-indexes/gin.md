---
title: GIN 倒排索引
date: 2026-08-15  # date-auto-injected
description: PostgreSQL 全文检索 / JSONB / 数组的利器
---

# GIN 倒排索引

> **TL;DR**：GIN（Generalized Inverted Index）= 倒排索引，**适合多值字段**（JSONB / 数组 / 全文检索）。**JSONB 查询性能从 5s 降到 5ms，靠的就是 GIN 索引**。

## 一句话定义

```
GIN = 倒排索引，把"值 → 行号"反向映射
     = 适合数组、JSONB、全文检索等多值字段
```

## GIN vs B-tree

| 维度 | B-tree | GIN |
|---|---|---|
| 数据类型 | 标量 | 多值（数组/JSONB/全文） |
| 查询 | col = ? / col > ? | 包含 @> / 元素查询 |
| 写入性能 | 快 | **慢**（多值拆解） |
| 索引大小 | 小 | **大** |
| 适用 | 90% 场景 | JSONB / 全文 / 数组 |

## JSONB + GIN（最常用）

```sql
-- 创建 JSONB 字段
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  data JSONB
);

-- 插入示例
INSERT INTO users (data) VALUES
  ('{"name": "Alice", "tags": ["admin", "user"], "age": 30}'),
  ('{"name": "Bob", "tags": ["user"], "age": 25}');

-- GIN 索引
CREATE INDEX idx_users_data ON users USING GIN (data);

-- JSONB 查询（用 GIN）
SELECT * FROM users 
WHERE data @> '{"tags": ["admin"]}';
-- Index Scan using idx_users_data
```

### 两种 GIN 索引策略

```sql
-- 1. 整个 JSONB 建索引（默认，灵活但慢）
CREATE INDEX idx_users_data ON users USING GIN (data);

-- 支持：data @> '{"tags": ["admin"]}'
-- 支持：data @> '{"age": 30}'
-- 支持：data ? 'tags'

-- 2. jsonb_path_ops（更小更快，但只支持 @>）
CREATE INDEX idx_users_data_path ON users USING GIN (data jsonb_path_ops);

-- 只支持：data @> '{"tags": ["admin"]}'
```

**性能对比**：

| 操作 | 默认 GIN | jsonb_path_ops |
|---|---|---|
| `@>` 查询 | ✓ | ✓ |
| `?` 包含 key | ✓ | ✗ |
| `?\|` 任意 key | ✓ | ✗ |
| `?&` 全部 key | ✓ | ✗ |
| 索引大小 | 大 | **小 30%** |

**推荐**：如果只用 `@>` 查询，用 `jsonb_path_ops`（小 + 快）。

## 数组 + GIN

```sql
CREATE TABLE articles (
  id BIGSERIAL PRIMARY KEY,
  tags TEXT[]
);

CREATE INDEX idx_articles_tags ON articles USING GIN (tags);

-- 查询
SELECT * FROM articles 
WHERE tags @> ARRAY['postgresql'];
-- Index Scan using idx_articles_tags

-- 包含任意一个
SELECT * FROM articles 
WHERE tags && ARRAY['postgres', 'mysql'];
-- Index Scan

-- 包含全部
SELECT * FROM articles 
WHERE tags @> ARRAY['postgres', 'database'];
-- Index Scan
```

## 全文检索 + GIN

```sql
-- 1. 创建列
ALTER TABLE articles ADD COLUMN tsv tsvector;

-- 2. 填充 tsvector
UPDATE articles 
SET tsv = to_tsvector('english', title || ' ' || body);

-- 3. GIN 索引
CREATE INDEX idx_articles_tsv ON articles USING GIN (tsv);

-- 4. 全文查询
SELECT * FROM articles
WHERE tsv @@ to_tsquery('english', 'postgres & performance');
-- Index Scan using idx_articles_tsv

-- 5. 排序（按相关性）
SELECT *, ts_rank(tsv, to_tsquery('postgres')) AS rank
FROM articles
WHERE tsv @@ to_tsquery('postgres')
ORDER BY rank DESC;
```

## 数组元素 GIN 操作符

| 操作符 | 含义 | 例子 |
|---|---|---|
| `@>` | 包含 | `tags @> ARRAY['pg']` |
| `<@` | 被包含 | `ARRAY['pg'] <@ tags` |
| `&&` | 重叠 | `tags && ARRAY['pg', 'mysql']` |
| `=` | 相等 | `tags = ARRAY['pg']` |

## 写入性能权衡

**GIN 索引比 B-tree 慢 2-3 倍**：

```sql
-- 测试：插入 100 万行
INSERT INTO users (data) 
SELECT jsonb_build_object('id', g, 'tags', ARRAY['tag1', 'tag2'])
FROM generate_series(1, 1000000) g;

-- 有 GIN 索引：约 120s
-- 无 GIN 索引：约 40s
```

**缓解方案**：

```sql
-- 1. fastupdate 延迟合并（PG 8.4+）
ALTER INDEX idx_users_data SET (fastupdate = on);

-- 2. 定期 VACUUM（合并 pending list）
VACUUM users;

-- 3. gin_pending_list_limit
SHOW gin_pending_list_limit;  -- 默认 4MB
```

## 实战案例

### 案例 1：商品多标签筛选

```sql
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  tags TEXT[],
  attrs JSONB
);

CREATE INDEX idx_products_tags ON products USING GIN (tags);
CREATE INDEX idx_products_attrs ON products USING GIN (attrs jsonb_path_ops);

-- 查询：标签包含 "postgres" AND 价格 100-500
SELECT * FROM products
WHERE tags @> ARRAY['postgres']
  AND (attrs->>'price')::numeric BETWEEN 100 AND 500;
```

### 案例 2：JSONB 日志字段检索

```sql
CREATE TABLE logs (
  id BIGSERIAL PRIMARY KEY,
  ts TIMESTAMPTZ,
  payload JSONB
);

-- 假设有 1 亿行日志
CREATE INDEX idx_logs_payload ON logs USING GIN (payload jsonb_path_ops);

-- 查询：特定用户 ID
SELECT * FROM logs
WHERE payload @> '{"user_id": 12345}'
ORDER BY ts DESC
LIMIT 10;

-- 不加索引：5s 全表扫描
-- 加 GIN：20ms
```

### 案例 3：全文搜索电商商品

```sql
-- 商品表
CREATE TABLE items (
  id BIGSERIAL PRIMARY KEY,
  title TEXT,
  desc TEXT,
  search tsvector
);

-- 触发器自动更新 search
CREATE TRIGGER trg_items_search
BEFORE INSERT OR UPDATE ON items
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(search, 'public.english_ngram', title, desc);

-- 索引
CREATE INDEX idx_items_search ON items USING GIN (search);

-- 搜索 "iPhone 15"
SELECT * FROM items
WHERE search @@ to_tsquery('chinese', 'iPhone 15')
ORDER BY ts_rank(search, to_tsquery('iPhone 15')) DESC
LIMIT 20;
```

## 何时不用 GIN

```
❌ 等值查询（用 B-tree）
❌ 范围查询（用 B-tree）
❌ 排序（用 B-tree）
❌ 写入极频繁（GIN 慢）
❌ 字段值基数小（如 status ENUM）
```

## 一句话总结

> **GIN = JSONB/数组/全文检索的杀手锏**。**JSONB 用 GIN 后 @> 查询从 5s 降到 5ms**，但**写入慢 2-3 倍 + 索引大**，需要权衡。**jsonb_path_ops 进一步压缩索引 30%**（如果只查 @>）。

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
