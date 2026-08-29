---
title: Token Filter
date: 2026-08-15  # date-auto-injected
category: analysis
graphNodeId: token-filter
---

<span class="kg-badge kg-badge-analysis">分析层</span>

# Token Filter

## 📌 一句话定义
Token Filter 是 Analyzer 三段式的**第三段**，对 tokenizer 输出的 token 流做**进一步处理**。

## 📚 常用 Token Filter

| Filter | 作用 |
|---|---|
| `lowercase` | 转小写 |
| `uppercase` | 转大写 |
| `stop` | 去除停用词（the, a, an, of 等） |
| `synonym` | 同义词替换 |
| `snowball` | 词干提取（running → run） |
| `stemmer` | 词形归并 |
| `asciifolding` | é → e（去除变音符） |
| `ngram` / `edge_ngram` | N-gram 切分 |
| `length` | 过滤掉长度不达标的 token |
| `unique` | 去重 |

## 🔧 lowercase 示例

```json
{
  "settings": {
    "analysis": {
      "analyzer": {
        "my_lower": {
          "tokenizer": "standard",
          "filter": ["lowercase"]
        }
      }
    }
  }
}
```

输入：`"Hello World"`
输出：`["hello", "world"]`

## 🔧 synonym 同义词

```json
{
  "settings": {
    "analysis": {
      "filter": {
        "my_synonym": {
          "type": "synonym",
          "synonyms": [
            "笔记本, 笔电, laptop",
            "机械键盘, 机械, 红轴, 茶轴, 青轴"
          ]
        }
      },
      "analyzer": {
        "my_synonym_analyzer": {
          "tokenizer": "ik_max_word",
          "filter": ["my_synonym", "lowercase"]
        }
      }
    }
  }
}
```

> ⚠️ 同义词在**索引时和查询时**都要加，否则 query 时不会展开同义词匹配。

## 🔧 stop 停用词

```json
{
  "filter": {
    "my_stop": {
      "type": "stop",
      "stopwords": ["的", "了", "和", "是"]   // 中文停用词表
    }
  }
}
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="token-filter" :height="400" />

## 📚 延伸阅读
- [Analyzer 分析器](/03-analysis/analyzer)
- [Tokenizer](/03-analysis/tokenizer)
