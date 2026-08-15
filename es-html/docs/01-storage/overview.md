---
title: 存储层 总览
---

# 存储层 Storage

存储层是 ES 的"地基"，涉及**数据如何写入、存储、切分、检索**的底层机制。本章按物理-逻辑-机制三个维度组织：

## 📦 数据组织

| 概念 | 层级 | 说明 |
|---|---|---|
| [集群 Cluster](/01-storage/cluster) | 物理 | 由多个节点组成的服务集合 |
| [节点 Node](/01-storage/node) | 物理 | 运行 ES 进程的实例 |
| [索引 Index](/01-storage/index) | 逻辑 | 相似文档的集合 |
| [文档 Document](/01-storage/document) | 逻辑 | 最小数据单元（JSON） |

## ✂️ 切分与副本

| 概念 | 说明 |
|---|---|
| [分片 Shard](/01-storage/shard) | 索引的物理切分单位 |
| [副本 Replica](/01-storage/replica) | 分片的拷贝，提供 HA |
| [段 Segment](/01-storage/segment) | 分片内部的不可变数据文件 |

## 📐 Schema 与元数据

| 概念 | 说明 |
|---|---|
| [映射 Mapping](/01-storage/mapping) | 索引 schema 定义 |
| [字段类型](/01-storage/field-types) | ES 支持的字段类型 |
| [_source 元数据](/01-storage/source) | 文档原始 JSON 存储 |

## ⚡ 写入与恢复

| 概念 | 说明 |
|---|---|
| [Translog](/01-storage/translog) | 事务日志，崩溃恢复 |
| [Refresh](/01-storage/refresh) | 内存缓冲 → segment |

## 🗺️ 本层在图谱中的位置

<KnowledgeGraph mode="full" :height="500" />

## 🔗 关联项目源码

本项目 [`ElasticsearchService.java`](https://github.com/your-repo/blob/main/src/main/java/com/example/esdemo/service/ElasticsearchService.java) 中演示了 `createIndex` / `indexProduct` / `getProduct` 等操作。
