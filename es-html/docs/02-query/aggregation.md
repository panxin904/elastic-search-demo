---
title: 聚合 Aggregation
date: 2026-08-15  # date-auto-injected
category: query
graphNodeId: aggregation
---

<span class="kg-badge kg-badge-query">查询层</span>

# 聚合 Aggregation

## 📌 一句话定义
聚合用于对搜索结果进行**统计分析**，是 ES 实现 BI/报表能力的核心。

## 🧱 三大聚合族系

| 族系 | 作用 | 示例 |
|---|---|---|
| **Metric** | 单值/多值数值计算 | `avg`, `sum`, `min`, `max`, `cardinality` |
| **Bucket** | 按条件分桶 | `terms`, `date_histogram`, `range` |
| **Pipeline** | 对聚合结果再聚合 | `derivative`, `moving_avg`, `bucket_script` |

## 🔧 Metric 聚合

```http
POST /products/_search
{
  "size": 0,
  "aggs": {
    "avg_price":   { "avg":     { "field": "price" } },
    "max_stock":   { "max":     { "field": "stock" } },
    "uniq_cats":   { "cardinality": { "field": "category" } }
  }
}
```

## 🔧 Bucket 聚合

```http
POST /products/_search
{
  "size": 0,
  "aggs": {
    "by_category": {
      "terms": { "field": "category", "size": 10 }
    }
  }
}
```

返回每个 category 的文档数。

## 🔧 嵌套聚合 (Sub-Aggregation)

```http
POST /products/_search
{
  "size": 0,
  "aggs": {
    "by_category": {
      "terms": { "field": "category" },
      "aggs": {
        "avg_price":  { "avg": { "field": "price" } },
        "price_range": {
          "range": {
            "field": "price",
            "ranges": [
              { "to": 100 },
              { "from": 100, "to": 500 },
              { "from": 500 }
            ]
          }
        }
      }
    }
  }
}
```

## 🔧 Date Histogram (时间分桶)

```json
{
  "aggs": {
    "sales_over_time": {
      "date_histogram": {
        "field": "created_at",
        "calendar_interval": "day"
      }
    }
  }
}
```

`calendar_interval`: `minute` / `hour` / `day` / `week` / `month` / `quarter` / `year`
`fixed_interval`: `30m` / `2h`

## 🔧 Pipeline 聚合

```json
{
  "aggs": {
    "by_month": {
      "date_histogram": { "field": "ts", "calendar_interval": "month" },
      "aggs": {
        "sales": { "sum": { "field": "amount" } }
      }
    },
    "trend": {
      "derivative": { "buckets_path": "by_month>sales" }
    }
  }
}
```

![Es Doc Values](/es-doc-values.svg)

## ⚠️ 聚合性能

- `size: 0` 设置：只返回聚合，不返回 hits
- `terms` 聚合的 `size` 限制 bucket 数
- 字段必须具有 `doc_values`（默认开启）

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="aggregation" :height="400" />

## 📚 延伸阅读
- [Script Query](/02-query/script)
- [字段类型 keyword](/01-storage/field-types)
