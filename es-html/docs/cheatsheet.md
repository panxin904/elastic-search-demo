---
title: 速查表
date: 2026-08-29  # date-auto-injected
---

# 📋 ES 速查表

> 60+ 高频 ES 命令速查，支持分类过滤和关键词搜索（Cmd+F 即可）。

## 🏗️ 索引操作

| 场景 | 命令 |
|------|------|
| 创建索引 | `PUT /my_index` |
| 删除索引 | `DELETE /my_index` |
| 查看索引 | `GET /my_index/_settings` |
| 关闭/打开 | `POST /my_index/_close` / `_open` |
| 索引别名 | `POST /_aliases` |

## 📝 文档操作

| 场景 | 命令 |
|------|------|
| 索引文档 | `PUT /my_index/_doc/1` |
| 获取文档 | `GET /my_index/_doc/1` |
| 更新文档 | `POST /my_index/_update/1` |
| 删除文档 | `DELETE /my_index/_doc/1` |
| 批量操作 | `POST /_bulk` |

## 🔍 查询操作

| 场景 | 命令 |
|------|------|
| Match 查询 | `GET /my_index/_search {"query":{"match":{"title":"foo"}}}` |
| Term 查询 | `{"query":{"term":{"status":"active"}}}` |
| Bool 查询 | `{"query":{"bool":{"must":[...]}}}` |
| Range 查询 | `{"range":{"age":{"gte":18,"lte":30}}}` |
| Aggregation | `{"aggs":{"by_cat":{"terms":{"field":"category"}}}}` |
| 分页 | `?from=0&size=10` 或 `search_after` |

## 🧪 分析相关

| 场景 | 命令 |
|------|------|
| 测试分析器 | `POST /my_index/_analyze` |
| 查看 Mapping | `GET /my_index/_mapping` |
| 重建索引 | `POST /_reindex` |
| 索引模板 | `PUT /_index_template/my_template` |
| 别名切换 | `POST /_aliases {"actions":[{"add":{"index":"new","alias":"my"}}]}` |

## ⚙️ 运维命令

| 场景 | 命令 |
|------|------|
| 集群健康 | `GET /_cluster/health` |
| 节点状态 | `GET /_cat/nodes?v` |
| 分片分配 | `GET /_cat/shards?v` |
| 慢日志 | `GET /my_index/_settings`（含 `index.search.slowlog`） |
| 快照 | `PUT /_snapshot/my_backup/snap_1` |
| ILM | `GET /_ilm/policy` |


## 📱 手机扫码继续阅读

<ClientOnly>
  <QrShare />
</ClientOnly>
