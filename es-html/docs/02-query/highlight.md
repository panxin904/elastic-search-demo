---
title: Highlight
date: 2026-08-15  # date-auto-injected
category: query
graphNodeId: highlight
---

<span class="kg-badge kg-badge-query">查询层</span>

# Highlight 高亮

## 📌 一句话定义
Highlight 在搜索结果中**标记匹配的关键字**，通常用 `<em>` 标签包裹。

## 🔧 基本用法

```http
POST /products/_search
{
  "query": { "match": { "name": "机械键盘" } },
  "highlight": {
    "fields": {
      "name": {}
    }
  }
}
```

返回：
```json
{
  "hits": [{
    "_source": { "name": "机械键盘 RGB 背光" },
    "highlight": {
      "name": ["<em>机械</em><em>键盘</em> RGB 背光"]
    }
  }]
}
```

## ⚙️ 自定义标签

```json
{
  "highlight": {
    "pre_tags":  ["<b class='hl'>"],
    "post_tags": ["</b>"],
    "fields": {
      "name": {}
    }
  }
}
```

## 📐 高亮类型

| 类型 | 适用字段 | 性能 |
|---|---|---|
| `unified`（默认） | 全部 | 高（需 term vectors / offsets） |
| `plain` | 全部 | 中（需存储 position） |
| `fvh` (fast vector highlighter) | 大量文本 | 快（需 term_vector: with_positions_offsets） |
| `postings` | 全部 | 极快（需 index_options: offsets） |

```json
{
  "highlight": {
    "fields": {
      "name": { "type": "unified", "fragment_size": 100, "number_of_fragments": 3 }
    }
  }
}
```

| 参数 | 含义 |
|---|---|
| `fragment_size` | 每个片段字符数 |
| `number_of_fragments` | 返回几个片段 |
| `no_match_size` | 无匹配时的返回长度 |

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="highlight" :height="400" />

## 📚 延伸阅读
- [Match Query](/02-query/match)
- [BM25 相关度](/03-analysis/bm25)
