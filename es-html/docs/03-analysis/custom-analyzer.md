---
title: 自定义分词
date: 2026-08-15  # date-auto-injected
category: analysis
graphNodeId: custom-analyzer
---

<span class="kg-badge kg-badge-analysis">分析层</span>

# 自定义分词器

## 📌 一句话定义
自定义分词器是在索引 settings 中**自由组合** Char Filter、Tokenizer、Token Filter，形成专属文本处理管道。

## 🔧 完整示例：HTML 清理 + IK + 同义词

```http
PUT /products
{
  "settings": {
    "analysis": {
      "char_filter": {
        "my_html_strip": {
          "type": "html_strip"
        }
      },
      "tokenizer": {
        "my_tokenizer": {
          "type": "ik_max_word"
        }
      },
      "filter": {
        "my_synonym": {
          "type": "synonym",
          "synonyms": [
            "笔记本, 笔电, laptop",
            "机械键盘, 红轴, 茶轴, 青轴"
          ]
        },
        "my_pinyin": {
          "type": "pinyin",
          "keep_full_pinyin": true,
          "keep_first_letter": true
        }
      },
      "analyzer": {
        "my_full_analyzer": {
          "type": "custom",
          "char_filter":  ["my_html_strip"],
          "tokenizer":    "my_tokenizer",
          "filter":       ["lowercase", "my_synonym"]
        },
        "my_search_analyzer": {
          "type": "custom",
          "tokenizer": "ik_smart",
          "filter":    ["lowercase", "my_synonym"]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "name": {
        "type": "text",
        "analyzer": "my_full_analyzer",
        "search_analyzer": "my_search_analyzer"
      }
    }
  }
}
```

## 🔧 测试自定义分词

```http
POST /products/_analyze
{
  "analyzer": "my_full_analyzer",
  "text": "<p>笔记本 机械键盘</p>"
}
```

## 🧪 调试技巧

| 工具 | 用途 |
|---|---|
| `_analyze` | 测试当前索引的分词效果 |
| `tokens` API | 查看 token 的 offset / position |
| `_settings` | 查看已注册 analyzer |

## ⚠️ 自定义 analyzer 的限制

- 创建索引后**无法修改** analyzer 组合（需 reindex）
- 索引时和查询时必须用**一致的分析规则**，否则结果异常

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="custom-analyzer" :height="400" />

## 📚 延伸阅读
- [Analyzer 分析器](/03-analysis/analyzer)
- [Char Filter](/03-analysis/char-filter)
- [Tokenizer](/03-analysis/tokenizer)
- [Token Filter](/03-analysis/token-filter)
