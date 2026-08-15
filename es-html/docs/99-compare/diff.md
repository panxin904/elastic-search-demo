---
title: ES 7 vs ES 8 差异
---

# Elasticsearch 7.x 与 8.x 主要差异

本页聚焦从 7.x 升级到 8.x 时**最关键的差异点**，供升级决策参考。

> 💡 本站主要讲 ES 7.17（搭配 [elastic-search-demo](https://github.com/your-repo) 项目使用 7.17.10）。如需了解 8.x 新特性请参考 [官方升级指南](https://www.elastic.co/guide/en/elasticsearch/reference/current/migrating-8.0.html)。

## 📊 总览对比

| 维度 | ES 7.x | ES 8.x |
|---|---|---|
| 默认安全 | 需手动启用 | **默认开启** HTTPS + 认证 |
| JDK 要求 | JDK 8/11/17 | **JDK 17+** |
| Java Client | `co.elastic.clients:elasticsearch-java` | 同上，但 API 更严格 |
| REST Client | `RestHighLevelClient`（已废弃） | **强制使用 Java API Client** |
| 索引创建 | 自动 + 手动 | **默认不再自动创建**（需手动） |
| 默认 mapping | `include_type_name: true` | `false`（**彻底移除 mapping type**） |
| 节点角色 | node.master/data/ingest | 同 7.x，但**默认配置更严格** |
| ILM | 支持 | 同 7.x，**更细粒度** |
| Search | 7.x 全部支持 | 新增 **knn search** (8.0+) |
| TSDB | 无 | 8.0+ 内置 |
| Transform | 基础 | 增强 + GA |

## 🔐 1. 安全：默认开启

ES 7.x：
```yaml
# 需手动开启
xpack.security.enabled: true
```

ES 8.x：
- **默认开启**，无认证则**不能启动**
- 自动生成 HTTP CA + TLS
- 内置 `elastic` 超级用户

```bash
# 8.x 启动后查看初始密码
./bin/elasticsearch-reset-password -u elastic
```

> ⚠️ 从 7.x 升级到 8.x 时，安全配置将**自动开启**！需要提前准备证书。

## 📦 2. Java Client 迁移

### 7.x（推荐 - 与本项目一致）

```xml
<dependency>
  <groupId>co.elastic.clients</groupId>
  <artifactId>elasticsearch-java</artifactId>
  <version>7.17.10</version>
</dependency>
```

### 8.x

```xml
<dependency>
  <groupId>co.elastic.clients</groupId>
  <artifactId>elasticsearch-java</artifactId>
  <version>8.x.x</version>
</dependency>
```

API 主要变化：
- 部分包名从 `co.elastic.clients.elasticsearch._types` 微调
- `RestClient` 底层 HTTP 客户端从 `apache httpclient` 改为 `elasticsearch-java` 内置

## 🚫 3. Mapping Type 彻底移除

ES 7.x：保留 `_doc` type（兼容旧 API）<br>
ES 8.x：**完全移除 type 概念**

```http
# 7.x 仍可写
PUT /products/_doc/p001

# 8.x 同样，但旧 API 已废弃
PUT /products/_doc/p001
```

## 🔍 4. KNN Search (8.0+)

ES 8.0 内置 **k-近邻搜索**，适合向量检索场景。

```http
PUT /products
{
  "mappings": {
    "properties": {
      "embedding": {
        "type": "dense_vector",
        "dims": 768
      }
    }
  }
}

POST /products/_search
{
  "knn": {
    "field": "embedding",
    "query_vector": [0.1, 0.2, ...],
    "k": 10,
    "num_candidates": 100
  }
}
```

## 📈 5. TSDB (8.0+)

时间序列数据库模式，**指标场景**性能大幅提升。

```http
PUT /metrics
{
  "settings": { "index.mode": "time_series" },
  "mappings": {
    "properties": {
      "@timestamp": { "type": "date" },
      "metric":     { "type": "long", "time_series_metric": "gauge" }
    }
  }
}
```

## 🆕 6. 其他新特性

| 特性 | 引入版本 | 说明 |
|---|---|---|
| **Composable Index Template** | 7.8 | 7.x 已支持，8.x 完善 |
| **PIT (Point In Time)** | 7.10 | 8.x 配合 search_after 推荐 |
| **Runtime fields** | 7.11 | 8.x 性能更优 |
| **Vector search (knn)** | 8.0 | 新增 |
| **TSDB** | 8.0 | 新增 |
| **Text structure API** | 7.13 | 7.x 已有 |
| **Geo-line** | 7.13 | 8.x GA |

## 📋 升级决策

| 场景 | 建议 |
|---|---|
| 新项目 | 直接上 **8.x**（最新稳定） |
| 在用 7.x 7.17+ | 评估升级 8.x（兼容性较好） |
| 仍在 7.x 7.0-7.16 | 升级到 **7.17** 再考虑 8.x |
| 在用 6.x 或更早 | 需先升级到 7.x |

## ⚠️ 升级注意事项

1. **JDK 17+**（8.x 强制）
2. **TLS 证书** 准备（8.x 默认 HTTPS）
3. **API Client** 重新编译（包名变化）
4. **REST API** 检查废弃 API（`_type`, `_doc/_create` 等）
5. **索引兼容性**：8.x 可读 7.x 索引，**写需要先升级**（reindex）
6. **测试**先在 staging 环境跑全套回归

## 🔗 关联项目

本站点配套 [elastic-search-demo](https://github.com/your-repo) Java 项目使用 ES 7.17.10。该项目如未来升级 8.x，主要变更点：
- `pom.xml` 中 `elasticsearch.version` 改为 8.x
- Java Client API 升级到 8.x 版本
- 添加 TLS 证书配置 + 用户认证
- 移除 `_type` 相关代码（如有）

## 🗺️ 在图谱中的位置

<KnowledgeGraph mode="full" :height="500" />
