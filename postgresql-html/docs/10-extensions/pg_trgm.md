---
title: pg_trgm 模糊匹配
description: 三元组相似度
---

# pg_trgm 模糊匹配

> **TL;DR**：pg_trgm = **三元组相似度**扩展。**支持 `LIKE '%xxx%'` 模糊匹配 + 拼写错误容忍 + 相似度排序**。**配 GIN 索引后搜索性能从 5s 降到 5ms**。

## 一句话定义

```
pg_trgm = 把字符串拆成 3 字符片段（trigrams）
        = 计算相似度（共享 trigram 数）
        = GIN 索引加速模糊匹配
```

## 三元组原理

```sql
-- 字符串拆成 3 字符片段
SELECT show_trgm('hello');
-- {'  h',' he','hel','ell','llo','lo '}
```

**相似度计算**：

```
两个字符串的 trigrams 集合相似度 = 共享 trigrams / 总 trigrams
```

## 基本使用

```sql
-- 1. 安装
CREATE EXTENSION pg_trgm;

-- 2. 相似度函数
SELECT similarity('hello', 'helo');    -- 0.4（拼错一个字符）
SELECT similarity('hello', 'world');    -- 0.0（完全不同）
SELECT similarity('PostgreSQL', 'Postgres');  -- 0.5

-- 3. 阈值
SELECT set_limit(0.3);  -- 相似度 > 0.3 算匹配
```

## 实战案例

### 案例 1：模糊搜索

```sql
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  name TEXT
);

CREATE INDEX idx_products_name ON products USING GIN (name gin_trgm_ops);

-- 1. 模糊匹配
SELECT * FROM products 
WHERE name % 'Postgres'  -- % = similarity > threshold
LIMIT 10;

-- 2. 相似度排序
SELECT *, similarity(name, 'Postgres') AS sim
FROM products
WHERE name % 'Postgres'
ORDER BY sim DESC
LIMIT 10;

-- 3. 拼写错误容忍（"Postgres" vs "Postgress"）
SELECT * FROM products 
WHERE name % 'Postgress';
-- 能匹配 "Postgres"（相似度 0.66 > 0.3）
```

### 案例 2：邮箱校验（防拼写错误）

```sql
CREATE TABLE users (
  id BIGSERIAL PRIMARY KEY,
  email TEXT
);

CREATE INDEX idx_users_email ON users USING GIN (email gin_trgm_ops);

-- 注册时检查相似邮箱（防 "alice@gmial.com" 注册了但 "alice@gmail.com" 已存在）
SELECT email, similarity(email, '[email protected]') AS sim
FROM users
WHERE email % '[email protected]'
ORDER BY sim DESC
LIMIT 5;
```

### 案例 3：搜索建议

```sql
-- 用户输入 "ipone"，推荐 "iPhone"
CREATE EXTENSION pg_trgm;

CREATE TABLE products (name TEXT);
CREATE INDEX idx_products_name ON products USING GIN (name gin_trgm_ops);

-- 推荐最相似
SELECT name, similarity(name, 'ipone') AS sim
FROM products
WHERE name % 'ipone'
ORDER BY sim DESC
LIMIT 5;
-- iPhone, iPhone 15, iPad, ...
```

## 操作符

| 操作符 | 含义 | 例子 |
|---|---|---|
| `%` | similarity > threshold | `name % 'Postgres'` |
| `<%` | similarity < threshold | `name <% 'Postgres'` |
| `%>` | 1 包含 2 | `'Postgres' %> name` |
| `<%>` | 距离（1 - similarity） | `name <%> 'Postgres'` |
| `<<%` | 1 相似 2（按字面量） | `name <<% 'Postgres'` |
| `%>>` | 2 相似 1（按字面量） | `name %>> 'Postgres'` |
| `~` | 正则 | `name ~ '^Post'` |

## 性能优化

```sql
-- 1. 阈值调优
SELECT set_limit(0.4);  -- 更严格
SELECT set_limit(0.2);  -- 更宽松

-- 2. GiST vs GIN
CREATE INDEX idx_name ON products USING GIN (name gin_trgm_ops);
-- GIN：适合读多写少
-- GiST：适合写多读少
CREATE INDEX idx_name ON products USING GIST (name gist_trgm_ops);

-- 3. word_similarity（词级，比 trigram 快）
SELECT word_similarity('Postgres', 'PostgreSQL');
-- 1.0（Postgres 是 PostgreSQL 的子串）
```

## 一句话总结

> **pg_trgm = 模糊搜索利器**：**`%` 操作符 + GIN 索引 = LIKE 模糊匹配提速 1000x**。**搜索建议、邮箱校验、拼写容忍**全靠它。**阈值默认 0.3**，**按需调整**。

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
