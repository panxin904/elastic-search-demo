---
title: Query Profile
category: query
graphNodeId: profile
---

<span class="kg-badge kg-badge-query">查询层</span>

# Query Profile API

## 📌 一句话定义
Profile API 返回查询的**详细执行剖析**（各阶段耗时、Lucene 评分细节），是性能调优的关键工具。

## 🔧 启用 Profile

```http
POST /products/_search
{
  "profile": true,
  "query": { "match": { "name": "机械键盘" } }
}
```

## 📦 响应结构

```json
{
  "took": 5,
  "profile": {
    "shards": [{
      "searches": [{
        "query": [{
          "type": "BooleanQuery",
          "time_in_nanos": 1234567,
          "breakdown": {
            "score":     500000,
            "build_scorer_count": 1,
            "match_count": 5,
            ...
          }
        }],
        "rewrite_time": 234567,
        "collector": [{
          "name": "CancellableCollector",
          "time_in_nanos": 234567
        }]
      }]
    }]
  }
}
```

## 📊 breakdown 字段

| 字段 | 含义 |
|---|---|
| `score` | 评分耗时 |
| `build_scorer_count` | scorer 构建次数 |
| `match_count` | 命中文档数 |
| `create_weight` | 创建权重 |
| `next_doc` | 遍历 doc |
| `advance` | skip 跳过 |

## 🎯 调优典型场景

| 现象 | 优化方向 |
|---|---|
| `next_doc` 占比高 | 索引过大，考虑分片 |
| `score` 占比高 | 减少 `text` 字段 / 用 `constant_score` |
| `rewrite_time` 高 | prefix/wildcard 展开过多 |
| `match_count` 远大于返回 | 改用 `filter` 上下文 |

## 🔗 explain + profile

`explain: true` 与 `profile: true` 可同时开启，前者解释**评分组成**，后者解释**耗时组成**。

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="profile" :height="400" />

## 📚 延伸阅读
- [Query Rewrite](/02-query/rewrite)
- [Explain API](/03-analysis/explain)
- [慢日志](/04-ops/slow-log)
