---
title: 全文检索
date: 2026-08-15  # date-auto-injected
description: tsvector / tsquery / GIN
---

# 全文检索

> **TL;DR**：PG 全文检索 = `tsvector`（文档向量）+ `tsquery`（查询）+ `@@` 操作符。**配 GIN 索引后搜索性能从 5s 降到 5ms**，是 PG 中文/英文搜索的标配。

## 一句话定义

```
全文检索 = 把文本拆成词（token）+ 归一化（小写、词干化）+ 建倒排索引
         = 用 GIN 索引 + tsvector + tsquery
```

## 基础使用

### tsvector

```sql
-- 把文本转成文档向量
SELECT to_tsvector('english', 'The quick brown fox jumps over the lazy dog');
-- 'brown':3 'dog':9 'fox':4 'jump':5 'lazy':7 'quick':2

-- 位置：词在原文中的位置
```

### tsquery

```sql
-- 查询表达式
SELECT to_tsquery('english', 'fox & dog');      -- AND
SELECT to_tsquery('english', 'fox | dog');      -- OR
SELECT to_tsquery('english', '!fox');           -- NOT
SELECT to_tsquery('english', 'fox <-> dog');    -- 相邻
```

### @@ 操作符

```sql
-- 文档匹配查询
SELECT to_tsvector('english', 'The fox is quick') 
  @@ to_tsquery('english', 'fox');
-- true

-- 否定
SELECT to_tsvector('english', 'The fox is quick') 
  @@ to_tsquery('english', '!fox');
-- false
```

## 表 + 全文索引

```sql
-- 1. 表 + tsvector 列
CREATE TABLE articles (
  id BIGSERIAL PRIMARY KEY,
  title TEXT,
  body TEXT,
  tsv tsvector
);

-- 2. 填充 tsvector
INSERT INTO articles (title, body, tsv) VALUES
  ('PostgreSQL Intro', 'PostgreSQL is a powerful database', 
   to_tsvector('english', 'PostgreSQL Intro PostgreSQL is a powerful database'));

-- 3. GIN 索引
CREATE INDEX idx_articles_tsv ON articles USING GIN (tsv);

-- 4. 全文查询
SELECT * FROM articles
WHERE tsv @@ to_tsquery('english', 'postgres & powerful');
```

## 自动更新 tsvector（触发器）

```sql
-- 1. 创建函数
CREATE FUNCTION articles_tsv_update() RETURNS TRIGGER AS $$
BEGIN
  NEW.tsv :=
    setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.body, '')), 'B');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. 触发器
CREATE TRIGGER trg_articles_tsv
BEFORE INSERT OR UPDATE ON articles
FOR EACH ROW EXECUTE FUNCTION articles_tsv_update();
```

## 权重 + 排序

```sql
-- 权重：A (title) > B (body)
SELECT title, ts_rank(tsv, to_tsquery('postgres')) AS rank
FROM articles
WHERE tsv @@ to_tsquery('postgres')
ORDER BY rank DESC
LIMIT 10;
```

## 中文检索

```sql
-- 1. 安装 zhparser
CREATE EXTENSION zhparser;

-- 2. 创建文本搜索配置
CREATE TEXT SEARCH CONFIGURATION chinese (PARSER = zhparser);
ALTER TEXT SEARCH CONFIGURATION chinese ADD MAPPING FOR n,v,a,i,e,l,t WITH simple;

-- 3. 用
SELECT to_tsvector('chinese', 'PostgreSQL 是一个强大的数据库');
```

或者用 `pg_jieba`（基于结巴分词）：

```sql
CREATE EXTENSION pg_jieba;
SELECT to_tsvector('jiebacfg', 'PostgreSQL 是一个强大的数据库');
```

## 高亮

```sql
SELECT
  ts_headline('english', body, to_tsquery('postgres & powerful'),
    'MaxFragments=2, MaxWords=20, MinWords=5') AS headline
FROM articles
WHERE tsv @@ to_tsquery('postgres & powerful');
```

## 实战案例

### 案例 1：电商商品搜索

```sql
CREATE TABLE products (
  id BIGSERIAL PRIMARY KEY,
  name TEXT,
  description TEXT,
  search tsvector
);

CREATE INDEX idx_products_search ON products USING GIN (search);

CREATE TRIGGER trg_products_search
BEFORE INSERT OR UPDATE ON products
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(search, 'public.english_ngram', name, description);

-- 搜索 "iPhone 15"
SELECT *, ts_rank(search, to_tsquery('iPhone 15')) AS rank
FROM products
WHERE search @@ to_tsquery('iPhone 15')
ORDER BY rank DESC
LIMIT 20;
```

### 案例 2：博客文章搜索

```sql
-- A/B/C/D 权重：title (A) / subtitle (B) / body (C) / tag (D)
CREATE FUNCTION posts_tsv_update() RETURNS TRIGGER AS $$
BEGIN
  NEW.search :=
    setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
    setweight(to_tsvector('english', coalesce(NEW.body, '')), 'B') ||
    setweight(to_tsvector('english', coalesce(array_to_string(NEW.tags, ' '), '')), 'C');
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

## 一句话总结

> **PG 全文检索 = tsvector + GIN 索引**。**英文用内置词典**，**中文用 zhparser / pg_jieba**。**配合 ts_rank 排序 + ts_headline 高亮**就是一套完整搜索引擎，**5 行代码**搞定。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
