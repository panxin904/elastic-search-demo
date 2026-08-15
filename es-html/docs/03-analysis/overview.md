---
title: 分析层 总览
---

# 分析层 Analysis

分析层是 ES "**如何理解文本**" 的机制：把用户输入/文档内容**拆解为标准化的 token**，并据此构建**倒排索引**。

## 🧱 核心组件

| 组件 | 作用 |
|---|---|
| [Analyzer](/03-analysis/analyzer) | 文本分析器（三段式管道） |
| [Tokenizer](/03-analysis/tokenizer) | 切词器（按规则切分） |
| [Token Filter](/03-analysis/token-filter) | 词单元过滤器（小写/同义词） |
| [Char Filter](/03-analysis/char-filter) | 字符过滤器（HTML 去除） |

## 📚 内置与扩展

| 类型 | 说明 |
|---|---|
| [内置分词器](/03-analysis/builtin-analyzers) | standard / english / chinese 等 |
| [IK 分词器](/03-analysis/ik-analyzer) | 中文主流第三方分词器 |
| [pinyin 分词器](/03-analysis/pinyin-analyzer) | 拼音搜索 |
| [自定义分词](/03-analysis/custom-analyzer) | 自由组合三段式 |

## 🔬 底层机制

| 机制 | 说明 |
|---|---|
| [倒排索引](/03-analysis/inverted-index) | term → 文档列表 |
| [BM25](/03-analysis/bm25) | ES 7 默认评分算法 |
| [Explain API](/03-analysis/explain) | 评分明细 |

## 🗺️ 本层在图谱中的位置

<KnowledgeGraph mode="full" :height="500" />
