---
title: Elasticsearch 日志存储
description: ES 作为日志后端 + ILM + Index Template
---

# Elasticsearch 日志存储

> **TL;DR**：ES 作为日志后端 = **倒排索引 + 全文检索 + 聚合分析**。**ES 8 默认按 ILM 自动管理索引生命周期**：**hot（写入）→ warm（只读）→ cold（冻结）→ delete（删除）**。**关键配置：shard 数 / replica 数 / mapping 字段类型 / ILM 策略**。**日均日志 < 100GB 推荐 ES，> 1TB 推荐 ClickHouse 或 Loki**。

## 一句话定义

```
Elasticsearch（ES）= 分布式搜索 + 分析引擎
                  = Lucene 内核 + 倒排索引
                  = 适合全文检索 + 多维聚合
                  = 日志场景：通常用 ES（中等规模）或 ClickHouse（日志超大规模）

核心概念：
  - Index（索引）= 一组文档的集合（≈ MySQL 表）
  - Document（文档）= 一条日志（JSON）
  - Mapping（映射）= 字段类型定义
  - Shard（分片）= 索引的物理分片
  - Replica（副本）= 分片的副本（高可用）
```

## ES 集群架构

```
┌─────────────────────────────────────────────────┐
│  Master 节点（× 3，奇数，避免脑裂）             │
│  - 集群状态 / 元数据 / 分片分配                │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│  Data 节点（× N）                              │
│  - 实际存储索引分片                             │
│  - 处理读写请求                                │
│  - 推荐配置：SSD + 大内存 + 多核                │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│  Coordinating 节点（× 2+）                     │
│  - 接收客户端请求                              │
│  - 转发到 data 节点                            │
│  - 合并结果                                    │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│  Ingest 节点（可选）                            │
│  - 数据预处理（pipeline）                       │
│  - 字段提取 / 富化 / 类型转换                   │
└─────────────────────────────────────────────────┘
```

## Index Template（索引模板）

```yaml
# 自动应用：所有 app-logs-* 索引都用这个 mapping
PUT _index_template/app-logs-template
{
  "index_patterns": ["app-logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,           # 初始 shard 数
      "number_of_replicas": 1,          # 副本数（生产推荐 1-2）
      "refresh_interval": "5s",         # 写入刷新频率
      "index.codec": "best_compression" # 压缩
    },
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date",
          "format": "strict_date_optional_time||epoch_millis"
        },
        "service":     { "type": "keyword" },  # 精确匹配，不过滤
        "env":         { "type": "keyword" },
        "level":       { "type": "keyword" },
        "message":     { "type": "text" },      # 全文检索
        "trace_id":    { "type": "keyword" },
        "span_id":     { "type": "keyword" },
        "user_id":     { "type": "keyword" },
        "host":        { "type": "keyword" },
        "http.method": { "type": "keyword" },
        "http.status": { "type": "integer" },
        "duration_ms": { "type": "float" }
      }
    },
    "aliases": {
      "app-logs": {}   # 别名，所有 app-logs-* 都可查
    }
  }
}
```

## 字段类型选型

| 数据特征 | ES 类型 | 原因 |
|---|---|---|
| 唯一 ID（user_id, order_id） | `keyword` | 精确匹配，不过滤 |
| 状态码（status, level） | `keyword` | 聚合统计 |
| 时间戳 | `date` | 时间范围查询 |
| 整数/浮点 | `integer`, `float` | 范围查询 |
| 日志原文 | `text` + `keyword` 多字段 | 全文检索 + 聚合 |
| JSON 嵌套对象 | `object` / `nested` | 复杂结构 |
| IP 地址 | `ip` | CIDR 查询 |
| 经纬度 | `geo_point` | 地理查询 |

```yaml
# text + keyword 多字段（既可全文又可聚合）
"message": {
  "type": "text",
  "fields": {
    "keyword": {
      "type": "keyword",
      "ignore_above": 256  # 超长截断
    }
  }
}
```

## ILM（Index Lifecycle Management）

```yaml
# 日志 ILM 策略：7 天 hot → 30 天 warm → 90 天 cold → 365 天 delete
PUT _ilm/policy/logs-lifecycle
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_primary_shard_size": "50gb",  # shard 大于此 rollover
            "max_age": "1d"                     # 或超过 1 天
          },
          "set_priority": { "priority": 100 }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "forcemerge": { "max_num_segments": 1 },  # 合并 segment
          "set_priority": { "priority": 50 }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "freeze": {},                              # 冻结索引（省内存）
          "set_priority": { "priority": 0 }
        }
      },
      "delete": {
        "min_age": "365d",
        "actions": { "delete": {} }
      }
    }
  }
}

# 给模板关联 ILM 策略
PUT _index_template/app-logs-template
{
  "index_patterns": ["app-logs-*"],
  "template": { ... },
  "priority": 500,
  "_meta": {
    "managed_by": "ops-team",
    "ilm_policy": "logs-lifecycle"
  }
}
```

## Filebeat 采集配置

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/app/*.log
    parsers:
      - ndjson:
          target: ""           # 解析 JSON 到根
          overwrite_keys: true
          add_error_key: true
    fields:
      env: prod
    fields_under_root: true

processors:
  - add_host_metadata: ~       # 自动加 host.* 字段
  - add_cloud_metadata: ~      # 自动加 cloud.* 字段
  - timestamp:                 # 解析 @timestamp
      field: time
      layouts:
        - '2006-01-02T15:04:05.000Z'
        - '2006-01-02 15:04:05'
      test:
        - '2026-08-09 14:23:45'

output.elasticsearch:
  hosts: ["https://elasticsearch:9200"]
  username: "filebeat_writer"
  password: "${ES_PASSWORD}"
  index: "app-logs-%{+yyyy.MM.dd}"   # 按天 rollover
  ssl.certificate_authorities: ["/etc/ca.crt"]

setup.template.name: "app-logs"
setup.template.pattern: "app-logs-*"
setup.ilm.enabled: true
setup.ilm.policy: "logs-lifecycle"
```

## 查询语法

### KQL（Kibana Query Language）

```kql
# 基础
service: "order-api" AND level: "error"

# 范围
@timestamp >= "2026-08-09" AND @timestamp < "2026-08-10"
http.status: [500 TO 599]

# 通配
host.name: web-*
message: *exception*

# 嵌套字段
error.stack_trace: "NullPointerException"

# 组合
service: "order-api" AND level: "error" AND NOT message: "TimeoutException"
```

### DSL（Domain Specific Language）

```json
GET app-logs/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "service": "order-api" } },
        { "range": { "@timestamp": { "gte": "now-1h" } } },
        { "match": { "level": "error" } }
      ],
      "must_not": [
        { "match_phrase": { "message": "TimeoutException" } }
      ]
    }
  },
  "aggs": {
    "errors_by_service": {
      "terms": { "field": "service.keyword" }
    },
    "errors_over_time": {
      "date_histogram": {
        "field": "@timestamp",
        "fixed_interval": "1m"
      }
    }
  }
}
```

## 性能优化

### 1. Shard 规划

```
经验值：单个 shard 30-50GB 为佳
       日均 100GB / 50GB = 2 shards
       保留 30 天 = 总数据 3TB，需要 ~100 shards
       3 节点 × 5 shards/node = 15 shards → 不够
       需要更多 data 节点或更长 rollover 周期

公式：
  shards = 日均 GB × 保留天数 / 单 shard 大小（GB）
        = 100 × 30 / 50 = 60 shards
```

### 2. Mapping 优化

```yaml
# 关闭无用字段索引
"dynamic": "strict"   # 严格模式，未定义字段报错（推荐生产用）
# 或
"dynamic": false       # 动态字段不入索引（节省存储）

# 不需要分词的字段用 keyword（节省 CPU）
- keyword (精确 + 聚合)
- 不要用 text（全文分词浪费 CPU）
```

### 3. 写入优化

```yaml
# bulk API 批量写入（推荐每批 5-15MB）
curl -X POST "es:9200/app-logs/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @logs.ndjson

# 调整 refresh_interval（日志场景可以放宽）
"refresh_interval": "30s"   # 默认 1s，放宽到 30s 减少 segment 数量
```

## 一句话总结

> **ES = 分布式搜索 + 分析引擎**。**日志场景：单 shard 30-50GB + ILM 4 阶段（hot/warm/cold/delete）**。**字段类型：ID/状态码用 keyword，原文用 text + keyword 多字段**。**中等规模（日均 <100GB）首选 ES，超大规模考虑 ClickHouse / Loki**。

---

## 关联章节

- [Kibana](./kibana.md) — ES 上的可视化
- [Filebeat](./filebeat.md) — 轻量日志采集
- [Fluentd](./fluentd.md) — 替代 Filebeat
- [Grafana Dashboard](../04-grafana/dashboard.md) — ES 数据源对接

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
