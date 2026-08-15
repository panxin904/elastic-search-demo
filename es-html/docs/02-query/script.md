---
title: Script Query
category: query
graphNodeId: script
---

<span class="kg-badge kg-badge-query">查询层</span>

# Script Query

## 📌 一句话定义
Script Query 使用 **Painless 脚本**（ES 内置安全语言）做查询与计算。

## 🔧 基本 Script Query

```http
POST /products/_search
{
  "query": {
    "script": {
      "script": {
        "source": "doc['price'].value * doc['stock'].value > 10000"
      }
    }
  }
}
```

> 查找 `price × stock > 10000` 的商品。

## 🔧 参数化脚本

```http
POST /products/_search
{
  "query": {
    "script": {
      "script": {
        "source": "doc['price'].value > params.threshold",
        "params": { "threshold": 500 }
      }
    }
  }
}
```

## 🔧 在聚合中使用 Script

```http
POST /products/_search
{
  "size": 0,
  "aggs": {
    "discounted_total": {
      "sum": {
        "script": {
          "source": "doc['price'].value * (1 - doc['discount'].value)"
        }
      }
    }
  }
}
```

## 🛡️ Painless 特性

| 维度 | 说明 |
|---|---|
| 性能 | 编译后接近原生 Java 速度 |
| 沙箱 | 强制白名单，禁止反射、文件 I/O |
| 学习曲线 | 简单，类 Java 语法 |
| 默认语言 | `painless`（也可 `expression` / `mustache`） |

## ⚠️ 性能陷阱

- 脚本中**不要**用 `_source`（慢），尽量用 `doc['field']`（内存访问）
- 高频调用的脚本**预编译**（`script_id` / 存为 stored script）
- 复杂业务逻辑放**应用层**，ES 脚本只做简单计算

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="neighbor" focus-node-id="script" :height="400" />

## 📚 延伸阅读
- [聚合 Aggregation](/02-query/aggregation)
