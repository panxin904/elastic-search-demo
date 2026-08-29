---
title: Match Query
date: 2026-08-15  # date-auto-injected
category: query
graphNodeId: match
---

<span class="kg-badge kg-badge-query">查询层</span>

# Match Query

## 📌 一句话定义
Match Query 对查询文本**先分词再匹配**，是 `text` 字段**全文检索**的标准查询。

## 🔧 基本用法

```http
POST /products/_search
{
  "query": {
    "match": {
      "name": "机械键盘"
    }
  }
}
```

执行过程：
1. `机械键盘` → analyzer → tokens：`机械`、`键盘`
2. 任一 token 命中即返回（默认 `operator: or`）

## ⚙️ operator 参数

| 值 | 行为 |
|---|---|
| `or`（默认） | 任一 token 命中 |
| `and` | **所有 token** 都必须命中 |

```json
{ "match": { "name": { "query": "机械键盘", "operator": "and" } } }
```

## 🎯 minimum_should_match

```json
{ "match": { "name": { "query": "机械 键盘 RGB 蓝牙", "minimum_should_match": "75%" } } }
```

控制至少匹配多少比例的 token。

## 🔍 match_phrase (短语匹配)

```json
{ "match_phrase": { "name": "机械 键盘" } }
```

要求 token **按原顺序相邻**出现。

## 🔍 match_phrase_prefix (前缀匹配)

```json
{ "match_phrase_prefix": { "name": "机" } }
```

适合自动补全（**性能较差**，生产慎用）。

## 🔗 对应源码

本项目 `searchProductsByName`：

```java
.query(q -> q.match(m -> m.field("name").query(nameQuery)))
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="match" :height="400" />

## 📚 延伸阅读
- [Term Query](/02-query/term)
- [Bool Query](/02-query/bool)
- [Boost 相关度](/02-query/boost)
