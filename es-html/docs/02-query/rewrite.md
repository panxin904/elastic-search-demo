---
title: Query Rewrite
date: 2026-08-15  # date-auto-injected
category: query
graphNodeId: rewrite
---

<span class="kg-badge kg-badge-query">查询层</span>

# Query Rewrite

## 📌 一句话定义
Query Rewrite 是 ES 在**真正执行搜索前**，将高层查询转换为**底层 Lucene 查询**的预处理阶段。

## 🔄 重写示例

### prefix → term 集合

`prefix: { user: "ki" ` 会重写为：

```
term: user = "kimchy"
term: user = "king"
term: user = "kirk"
...
```

### wildcard → term 集合

类似 prefix，`wildcard: { user: "ki*" }` 也会展开。

### range → term 集合

`range: { age: { gte: 18, lte: 30 } }` 会按 `age` 的所有 term 重写为多个 term 查询（**对高基数字段慎用**）。

## 📊 重写过程

```java
QueryBuilder.rewrite(QueryShardContext) -> Query
```

`rewrite` 方法返回一个**更优的 Query**，例如 `MatchNoDocsQuery`、`TermQuery`、`BooleanQuery` 等。

## 🎯 何时发生

每次搜索请求**都会**触发 Query Rewrite，是搜索流程的固定阶段：

```
Query 请求
  ↓
Parse (解析)
  ↓
Rewrite (重写)  ← 本节
  ↓
Lucene Query
  ↓
Search
```

## 📌 性能影响

- 展开为大量 term 的查询会**显著变慢**
- 高基数字段避免使用 prefix/wildcard/range，应改用 `keyword` + 复合查询

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="rewrite" :height="400" />

## 📚 延伸阅读
- [Query DSL](/02-query/query-dsl)
- [Query Profile](/02-query/profile)
