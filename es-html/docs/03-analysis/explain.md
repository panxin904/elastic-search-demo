---
title: Explain API
date: 2026-08-15  # date-auto-injected
category: analysis
graphNodeId: explain
---

<span class="kg-badge kg-badge-analysis">分析层</span>

# Explain API

## 📌 一句话定义
Explain API 返回**每个文档的具体评分组成**，帮助你理解"为什么这个文档排在这个位置"。

## 🔧 启用 Explain

```http
POST /products/_search
{
  "explain": true,
  "query": {
    "match": { "name": "机械键盘" }
  }
}
```

## 📦 响应

```json
{
  "hits": {
    "hits": [{
      "_id": "p001",
      "_score": 0.8630463,
      "_explanation": {
        "value": 0.8630463,
        "description": "weight(name:机械 in 0) [PerFieldSimilarity], result of:",
        "details": [
          {
            "value": 0.8630463,
            "description": "score(freq=1.0), computed as boost * ...",
            "details": [
              { "value": 0.6931472, "description": "boost" },
              { "value": 0.43152311, "description": "idf, computed as log(1 + (N - n + 0.5) / (n + 0.5))" },
              { "value": 0.5, "description": "tf, computed as freq / (freq + k1 * (1 - b + b * dl / avgdl))" }
            ]
          }
        ]
      }
    }]
  }
}
```

## 📊 关键字段解读

| 字段 | 含义 |
|---|---|
| `value` | 该子表达式的评分 |
| `description` | 描述计算方式 |
| `details` | 嵌套子项 |
| `boost` | 手动加权 |
| `idf` | 逆文档频率 |
| `tf` | 词频归一化值 |

## 🎯 使用场景

| 场景 | 作用 |
|---|---|
| 排查"为什么这条不相关" | 看评分细节 |
| 验证 boost 效果 | 比较前后评分 |
| 调试同义词 | 看 query expansion |
| 优化相关性 | 找到高/低分的具体原因 |

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="explain" :height="400" />

## 📚 延伸阅读
- [BM25](/03-analysis/bm25)
- [Boost 相关度](/02-query/boost)
- [Query Profile](/02-query/profile)
