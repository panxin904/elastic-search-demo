---
title: Java SDK 速查
---

<span class="kg-badge kg-badge-query">Java</span>

# Java SDK 速查

> **54 个** Java Client 代码片段，按 **12 大类** 整理。所有代码段均内建 RestHighLevelClient / New Client 切换按钮。
> 💡 **想看企业级落地？** → [📚 使用场景与最佳实践](/05-tools/scenarios)（8 个场景：日志分析 / 全文搜索 / 时序监控 / 电商搜索 / 向量 RAG / 地理位置 / 安全审计 / 实时报表）

## ☕ 分类索引

按 **12 大类** 整理，共 **54 个** Java Client 代码片段（点击代码右上角切换按钮可切换 RestHighLevelClient 版本）：

| 分类 | 数量 | 包含 |
|---|---|---|
| 🔌 **客户端初始化** | 2 | 创建 / Basic Auth |
| ⚙️ **高级配置** | 5 | 连接池 + 超时 / Sniffer / 自定义 JSON Mapper / Ping / Info |
| 📝 **CRUD 操作** | 5 | 创建索引 / 索引 / 获取 / 删除 / 更新 |
| 🔍 **搜索查询** | 4 | Match / Bool / Highlight / Search After |
| 🔎 **搜索进阶** | 7 | Count / Exists / Multi Get / Update by Query / Delete by Query / Field Collapse / Multi Search |
| 📊 **聚合分析** | 2 | Terms + Metrics / Date Histogram |
| 📦 **批量操作** | 4 | Bulk / Reindex / Scroll / PIT + Search After |
| 🔄 **Ingest Pipeline** | 3 | 创建 Pipeline / Simulate / 写入时使用 |
| 🗂️ **索引管理** | 7 | Settings / Mapping / Delete / Close+Open / Shrink / Force Merge |
| 💾 **Snapshot 管理** | 4 | Repository / 创建 / 恢复 / 列表删除 |
| 🔀 **别名管理** | 4 | 添加 / 原子切换 / 写入别名 / 查询 |
| 🛠️ **高级特性** | 7 | 异步 + Listener / Cat Indices / Tasks / Painless / Refresh / 健康 |

<EsJavaSnippets />

## 📦 Maven 依赖说明

上方默认配置对应本项目 ES **7.17.10** 版本。升级 ES 版本时同步更新：

| ES 版本 | elasticsearch-java 版本 |
|---|---|
| 7.17.x | 7.17.10 |
| 8.x | 8.x.x |

> ⚠️ 版本必须严格对应，否则编译失败。

## 🆚 RestHighLevelClient 对比

> **RestHighLevelClient（简称 RHLC）** 是 ES 7.x 时代的主力 Java 客户端（groupId: `org.elasticsearch.client`），
> 大量存量 7.x 项目仍在广泛使用。7.15 起官方标记为 **deprecated**，8.x 完全移除。
> **新项目请使用 `co.elastic.clients:elasticsearch-java`（上方默认）。**
>
> 每个代码段右上角均提供 **切换按钮**，一键切换为 RestHighLevelClient 版本，
> 同时下方列出关键差异，方便对照迁移。

## 🎯 学习路径

1. **入门**：先看 **🔌 客户端初始化** → 学会创建 client
2. **CRUD**：**📝 CRUD 操作** → 配合 [本项目源码](https://github.com/your-repo/blob/main/src/main/java/com/example/esdemo/service/ElasticsearchService.java) 对照阅读
3. **搜索**：**🔍 搜索查询** → 学习 build pattern（lambda builder）
4. **聚合**：**📊 聚合分析** → 实战业务报表
5. **生产化**：**📦 批量操作 + ⚙️ 高级** → 处理大数据量、模板化、安全等

## 🛠️ Builder Pattern 用法提示

```java
// ES Java Client 几乎所有 API 都用 lambda builder 风格
SearchRequest.of(s -> s
    .index("products")
    .query(q -> q.match(m -> m.field("name").query("机械键盘")))
    .from(0)
    .size(20)
);
```

- `s -> s` 内可链式调用所有配置项
- 自动补全方便（IDE 会列出所有可用方法）
- 配置文件 (json) 可通过 `withJson(InputStream)` 加载

## 🔗 关联工具

- **[🚀 调试器](/05-tools/curl-client)** — 看到 DSL 后实际验证再写 Java
- **[📚 DSL 速查](/05-tools/dsl)** — Java API 与 DSL 一一对应
- **[📊 集群仪表板](/05-tools/dashboard)** — 用 health 接口验证集群可用

## 🔗 关联文档

- [本项目 ElasticsearchService.java](https://github.com/your-repo/blob/main/src/main/java/com/example/esdemo/service/ElasticsearchService.java)
- [Java Client 官方文档](https://www.elastic.co/guide/en/elasticsearch/client/java-api-client/current/introduction.html)
- [Match Query](/02-query/match)
- [聚合 Aggregation](/02-query/aggregation)
