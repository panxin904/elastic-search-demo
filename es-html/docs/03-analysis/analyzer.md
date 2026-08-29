---
title: Analyzer 分析器
date: 2026-08-15  # date-auto-injected
category: analysis
graphNodeId: analyzer
---

<span class="kg-badge kg-badge-analysis">分析层</span>

# Analyzer 分析器

## 📌 一句话定义
Analyzer 是**将文本转换为 token 流**的处理管道，由**三段式**组成：Char Filter → Tokenizer → Token Filter。

## 🔄 三段式管道

```
原始文本
  ↓
[Char Filter]      ← 字符级预处理：去除 HTML、字符映射
  ↓
[Tokenizer]        ← 按规则切分为 token
  ↓
[Token Filter]     ← 词单元级处理：小写、停用词、同义词
  ↓
最终 token stream
```

## 🔧 实际示例

输入：`"Mechanical Keyboard, RGB!"` (经过 `standard` analyzer)

| 阶段 | 输出 |
|---|---|
| Char Filter | (无变化) |
| Tokenizer | `["Mechanical", "Keyboard", "RGB"]` |
| Token Filter (lowercase) | `["mechanical", "keyboard", "rgb"]` |

## 📌 何时使用

| 时机 | 说明 |
|---|---|
| **索引时** | 文档写入时分词，构建倒排索引 |
| **查询时** | query string 分词后查倒排索引 |
| **测试时** | `_analyze` API 验证效果 |

## 🔧 在 Mapping 中指定

```json
{
  "properties": {
    "name": {
      "type": "text",
      "analyzer": "ik_max_word"   // 索引时使用
    }
  }
}
```

### 索引和查询使用不同分析器

```json
{
  "properties": {
    "name": {
      "type": "text",
      "analyzer": "ik_max_word",     // 索引时
      "search_analyzer": "ik_smart"  // 查询时
    }
  }
}
```

## 🧪 测试 Analyzer

```http
POST /_analyze
{
  "analyzer": "ik_max_word",
  "text": "机械键盘"
}
```

返回：
```json
{
  "tokens": [
    { "token": "机械",  "start_offset": 0 },
    { "token": "键盘",  "start_offset": 2 },
    { "token": "机械键盘", "start_offset": 0 }
  ]
}
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="analyzer" :height="400" />

## 📚 延伸阅读
- [Tokenizer](/03-analysis/tokenizer)
- [Token Filter](/03-analysis/token-filter)
- [Char Filter](/03-analysis/char-filter)
- [内置分词器](/03-analysis/builtin-analyzers)
