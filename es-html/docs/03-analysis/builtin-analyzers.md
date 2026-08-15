---
title: 内置分词器
category: analysis
graphNodeId: builtin-analyzers
---

<span class="kg-badge kg-badge-analysis">分析层</span>

# 内置分词器

ES 自带的常用分词器，开箱即用。

## 📚 主流内置 Analyzer

| Analyzer | Tokenizer + Filter | 适用 |
|---|---|---|
| `standard`（默认） | standard + lowercase | 通用 |
| `simple` | letter + lowercase | 简单西文 |
| `whitespace` | whitespace | 按空格 |
| `keyword` | keyword | 整段作为 1 token |
| `english` | standard + lowercase + stop + porter_stem | 英文 |
| `chinese` | standard + ... | **基础中文**（效果差） |
| `pattern` | pattern + lowercase/folding | 正则分词 |
| `snowball` | standard + snowball | 多语言词干 |
| `fingerprint` | 标准 + dedup | 指纹去重 |

## 🔧 standard analyzer (默认)

```http
POST /_analyze
{ "analyzer": "standard", "text": "The 2 QUICK Brown-Foxes." }
```

输出：
```json
["the", "2", "quick", "brown", "foxes"]
```

## 🔧 english analyzer

```http
POST /_analyze
{ "analyzer": "english", "text": "The foxes are running quickly" }
```

输出：
```json
["fox", "run", "quickli"]   // porter_stem 词干提取
```

## 🔧 keyword analyzer

不分词，整段作为 1 个 token：

```http
POST /_analyze
{ "analyzer": "keyword", "text": "Hello World" }
```

输出：
```json
["Hello World"]
```

## ⚠️ 内置 chinese 的局限

```http
POST /_analyze
{ "analyzer": "chinese", "text": "中华人民共和国" }
```

按**单字**切分（**实际不推荐**用于中文生产）：

```json
["中", "华", "人", "民", "共", "和", "国"]
```

> 💡 **中文生产环境推荐 IK / pinyin / 自研分词**

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="builtin-analyzers" :height="400" />

## 📚 延伸阅读
- [Analyzer 分析器](/03-analysis/analyzer)
- [IK 分词器](/03-analysis/ik-analyzer)
