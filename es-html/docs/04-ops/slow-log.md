---
title: 慢日志
date: 2026-08-15  # date-auto-injected
category: ops
graphNodeId: slow-log
---

<span class="kg-badge kg-badge-ops">运维层</span>

# 慢日志 Slow Log

## 📌 一句话定义
慢日志记录**慢查询**与**慢索引**到专用日志文件，是性能问题的**第一手线索**。

## 🔧 启用与配置

### 索引级慢日志

```http
PUT /products/_settings
{
  "index.search.slowlog.threshold.query.warn":   "10s",
  "index.search.slowlog.threshold.query.info":    "5s",
  "index.search.slowlog.threshold.query.debug":   "2s",
  "index.search.slowlog.threshold.query.trace":   "500ms",
  "index.search.slowlog.threshold.fetch.warn":   "1s",
  "index.search.slowlog.threshold.fetch.info":    "500ms",
  "index.indexing.slowlog.threshold.index.warn":  "10s",
  "index.indexing.slowlog.threshold.index.info":  "5s"
}
```

| 级别 | 含义 |
|---|---|
| `warn` | 重要告警 |
| `info` | 普通 |
| `debug` | 调试 |
| `trace` | 详细跟踪 |

## 📁 日志文件

| 文件 | 内容 |
|---|---|
| `*_index_search_slowlog.log` | 慢搜索 |
| `*_index_indexing_slowlog.log` | 慢索引 |
| `logs/elasticsearch_index_search_slowlog.json` | JSON 格式 |

## 📦 慢日志条目示例

```json
{
  "@timestamp": "2026-07-13T10:00:00.000Z",
  "took": "1.2s",
  "took_millis": 1200,
  "total_shards": 5,
  "types": "doc",
  "stats": [],
  "search_type": "QUERY_THEN_FETCH",
  "total_hits": 1234,
  "query": {
    "bool": {
      "must": [
        { "match": { "name": "机械键盘" } }
      ]
    }
  }
}
```

## 🔧 通过模板全局应用

```http
PUT /_index_template/slowlog
{
  "index_patterns": ["*"],
  "template": {
    "settings": {
      "index.search.slowlog.threshold.query.warn": "10s",
      "index.indexing.slowlog.threshold.index.warn": "10s"
    }
  }
}
```

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="slow-log" :height="400" />

## 📚 延伸阅读
- [Query Profile](/02-query/profile)
- [监控 Cerebro](/04-ops/monitoring)
