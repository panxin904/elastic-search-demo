---
title: Char Filter
date: 2026-08-15  # date-auto-injected
category: analysis
graphNodeId: char-filter
---

<span class="kg-badge kg-badge-analysis">分析层</span>

# Char Filter

## 📌 一句话定义
Char Filter 是 Analyzer 三段式的**第一段**，在分词**之前**对**原始字符流**做预处理。

## 📚 内置 Char Filter

| Filter | 作用 |
|---|---|
| `html_strip` | 去除 HTML 标签 |
| `mapping` | 字符映射（替换特定字符） |
| `pattern_replace` | 正则替换 |

## 🔧 html_strip 示例

```json
{
  "settings": {
    "analysis": {
      "char_filter": {
        "my_html_strip": {
          "type": "html_strip",
          "escaped_tags": ["b", "i"]    // 保留 <b><i>
        }
      },
      "analyzer": {
        "my_html": {
          "char_filter": ["my_html_strip"],
          "tokenizer": "standard"
        }
      }
    }
  }
}
```

输入：`"<p>Hello <b>World</b></p>"`
输出：`["Hello", "World"]`

## 🔧 mapping 字符映射

```json
{
  "char_filter": {
    "my_mapping": {
      "type": "mapping",
      "mappings": [
        "à => a",
        "é => e",
        "ü => u"
      ]
    }
  }
}
```

## 🔧 pattern_replace 正则

```json
{
  "char_filter": {
    "phone_format": {
      "type": "pattern_replace",
      "pattern": "(\\d{3})\\d{4}(\\d{4})",
      "replacement": "$1****$2"
    }
  }
}
```

> 💡 可用于**手机号脱敏**、统一日期格式等。

## 🔄 与 Token Filter 的区别

| 维度 | Char Filter | Token Filter |
|---|---|---|
| 处理对象 | **原始字符** | **已切词的 token** |
| 作用阶段 | 分词前 | 分词后 |
| 典型场景 | 去 HTML、字符替换 | 小写、停用词 |

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="char-filter" :height="400" />

## 📚 延伸阅读
- [Analyzer 分析器](/03-analysis/analyzer)
- [Token Filter](/03-analysis/token-filter)
