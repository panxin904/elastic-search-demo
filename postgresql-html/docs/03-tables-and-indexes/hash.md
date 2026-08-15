---
title: Hash 索引
description: PG 10+ 可用的 Hash 索引
---

# Hash 索引

> **TL;DR**：PG 10+ 的 Hash 索引**真正可用**（WAL 记录 + crash-safe + 复制安全）。**但实务中很少用**，因为 B-tree 等值查询也很快。**仅在特定场景下用 Hash**。

## 一句话定义

```
Hash 索引 = 通过哈希函数把键映射到 bucket
          = PG 10+ 真正可用
          = 仅支持等值查询
```

## 何时使用

```
✗ 90% 场景：等值查询用 B-tree（性能相当，能力更强）
✓ 极少数场景：超大数据量等值查询 + 写入频繁
  - 例如：10 亿行的用户 ID 字段
  - B-tree 索引大，Hash 索引更紧凑（PG 11+）
```

## 基本使用

```sql
-- 1. 创建 Hash 索引
CREATE INDEX idx_users_email ON users USING HASH (email);

-- 2. 等值查询（用 Hash）
SELECT * FROM users WHERE email = '[email protected]';

-- 3. EXPLAIN 看
EXPLAIN SELECT * FROM users WHERE email = '[email protected]';
-- Index Scan using idx_users_email on users
```

## Hash vs B-tree

| 维度 | Hash | B-tree |
|---|---|---|
| 等值查询 | ✓ | ✓ |
| 范围查询 | ✗ | ✓ |
| 排序 | ✗ | ✓ |
| 前缀匹配 | ✗ | ✓ |
| 索引大小 | 略小 | 中 |
| 写入性能 | 略快 | 略快 |

## 注意事项

```sql
-- 1. Hash 索引只能 PG 10+（之前版本 crash 后失效）
-- 2. 不能被 UNIQUE 约束自动使用（必须显式 CREATE INDEX）
-- 3. 没有 hash 索引的合并优化
```

## 哈希冲突与扩容

```sql
-- PG 11+ Hash 索引支持 4 字节哈希（spill 4 个 bucket），避免频繁分裂
-- PG 14+ 进一步优化 hash 索引写性能（METAPAGE 单页记录 spill 链）

-- 查看索引内部结构
CREATE EXTENSION pageinspect;
SELECT * FROM hash_metapage_info(get_raw_page('idx_login_email_hash', 0));
-- 列：magic, version, ntuples, ffactor, bmsize, bmshift, maxbucket, highmask, lowmask, ovflpoint, firstfree, nmaps
```

## 实战案例：写密集用户登录表

```sql
-- 场景：每天 1 亿次 INSERT，用户登录日志按 email 精确查询去重
CREATE TABLE user_login_log (
  id BIGSERIAL PRIMARY KEY,
  email TEXT NOT NULL,
  login_at TIMESTAMPTZ DEFAULT now()
);

-- B-tree 索引：等值查询 ~12ms，索引大小 480MB
CREATE INDEX idx_login_email_btree ON user_login_log USING BTREE (email);

-- Hash 索引：等值查询 ~9ms，索引大小 360MB（PG 13+）
CREATE INDEX idx_login_email_hash ON user_login_log USING HASH (email);
```

**经验**：Hash 索引**只在超大数据量 + 等值查询**且**不依赖范围/排序**时才有微弱优势。多数场景选 B-tree 是安全选择。

## 关联章节

- [B-tree 索引](./btree.md) — 通用索引（90% 场景选它，Hash 的替代品）
- [BRIN 索引](./brin.md) — 时序/物理有序数据（替代 Hash 的大数据量场景）
- [GiST 索引](./gist.md) — 多维数据/全文检索（Hash 不擅长的场景）

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
