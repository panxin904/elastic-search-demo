---
title: Term Query
date: 2026-08-15  # date-auto-injected
category: query
graphNodeId: term
---

<span class="kg-badge kg-badge-query">查询层</span>

# Term Query

## 📌 一句话定义
Term Query **不做分词**，精确匹配**已索引的 term**，适用于 `keyword`、数值、日期等精确字段。

## 🔧 基本用法

```http
POST /products/_search
{
  "query": {
    "term": {
      "category": "电脑外设"
    }
  }
}
```

## 📊 match vs term 对比

| 维度 | match | term |
|---|---|---|
| 是否分词查询 | ✅ 是 | ❌ 否 |
| 适用字段 | `text` | `keyword` / 数值 / 日期 |
| 查询字符串 | "机械键盘" → tokens | 完整字符串作为 1 个 term |
| 大小写敏感 | 由 analyzer 决定 | **始终敏感** |

## 🎯 terms Query（多值）

```http
POST /products/_search
{
  "query": {
    "terms": {
      "category": ["电脑外设", "电脑配件", "手机配件"]
    }
  }
}
```

任一命中即可（SQL `IN`）。

## 🔍 常见应用场景

| 场景 | 用法 |
|---|---|
| 状态过滤 | `term: { status: "active" }` |
| 精确 ID 查询 | `term: { _id: "p001" }` |
| 数值范围/精确 | `term: { stock: 100 }` |
| 多标签 | `terms: { tags: [...] }` |

> ⚠️ **常见错误**：对 `text` 字段用 term 查中文会查不到（因为 text 已被分词成多个 token）

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="term" :height="400" />

## 📚 延伸阅读
- [Match Query](/02-query/match)
- [Bool Query](/02-query/bool)
- [Range Query](/02-query/range)
