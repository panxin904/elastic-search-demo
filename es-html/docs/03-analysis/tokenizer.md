---
title: Tokenizer 分词器
date: 2026-08-15  # date-auto-injected
category: analysis
graphNodeId: tokenizer
---

<span class="kg-badge kg-badge-analysis">分析层</span>

# Tokenizer 分词器

## 📌 一句话定义
Tokenizer 是 Analyzer 三段式中的**第二段**，负责将文本**按特定规则切分为 token**。

## 📚 常见 Tokenizer

| Tokenizer | 规则 | 适用 |
|---|---|---|
| `standard` | Unicode 文本分割 | 通用（默认） |
| `letter` | 按非字母字符分 | 西方语言 |
| `whitespace` | 按空格分 | 不做语义处理 |
| `lowercase` | 按非字母分 + 转小写 | 简化场景 |
| `keyword` | 不分词，整段作为 1 个 token | keyword 字段 |
| `ngram` | 滑动窗口 N-gram | 前缀补全 |
| `pattern` | 正则分词 | 自定义场景 |
| `ik_smart` / `ik_max_word` | 中文智能/细粒度 | 中文 |

## 🔧 示例：standard

输入：`"The 2 QUICK Brown-Foxes."`

输出：
```
[ "The", "2", "QUICK", "Brown", "Foxes" ]
```

## 🔧 示例：ik_max_word vs ik_smart

输入：`"中华人民共和国国歌"`

| Tokenizer | 输出 |
|---|---|
| `ik_max_word`（细粒度） | `中华, 中华人民, 中华人民共和国, 华人, 人民, 共和国, 国歌` |
| `ik_smart`（智能） | `中华人民共和国, 国歌` |

> 💡 `ik_max_word` 索引时用（提高召回），`ik_smart` 查询时用（提高精度）

## 🔧 N-gram Tokenizer (前缀补全)

```json
{
  "settings": {
    "analysis": {
      "analyzer": {
        "my_ngram": {
          "tokenizer": {
            "type": "ngram",
            "min_gram": 2,
            "max_gram": 3,
            "token_chars": ["letter", "digit"]
          }
        }
      }
    }
  }
}
```

输入：`"apple"`
输出：`["ap", "app", "pp", "ppl", "pl", "ple"]`

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="tokenizer" :height="400" />

## 📚 延伸阅读
- [Analyzer 分析器](/03-analysis/analyzer)
- [IK 分词器](/03-analysis/ik-analyzer)
- [内置分词器](/03-analysis/builtin-analyzers)
