---
title: Loki 概览
date: 2026-08-15  # date-auto-injected
description: Grafana Labs 的日志聚合系统
---

# Loki 概览

> **TL;DR**：Loki = **Grafana Labs 2018 开源的日志聚合系统**，**设计哲学：只索引标签，不索引内容**。**类似 Prometheus 但 for logs**。**架构：Promtail（采集）+ Loki（存储 + 查询）+ Grafana（可视化）**。**优势：成本极低（vs ES 索引全文）+ 与 Prometheus 标签对齐**。

## 一句话定义

```
Loki = Grafana Labs 开源日志聚合系统
     = 设计灵感来自 Prometheus
     = 只索引 labels（标签），不索引 content（日志原文）
     = 通过 LogQL 查询（类似 PromQL）
     = 存储：chunk + object store（S3 / GCS / MinIO / 本地磁盘）
```

## 与 ELK 对比

| 维度 | Loki | ELK（Elasticsearch） |
|---|---|---|
| 出品 | Grafana Labs | Elastic |
| 索引 | 只索引 labels | 全文倒排索引 |
| 存储成本 | 极低（不索引原文） | 高（每条日志都建索引） |
| 查询能力 | LogQL（标签 + 行过滤） | Lucene KQL（全文检索强） |
| 全文检索 | 弱（要扫 chunk） | 强 |
| 聚合能力 | 中（受限于扫描量） | 强 |
| 适用 | 监控日志 / 结构化日志 | 全文检索 / 复杂查询 |
| 部署 | 单二进制 / 微服务 | ES 集群 |

## 架构

```
┌──────────┐  push   ┌──────────────────────────────────────┐
│ Promtail │ ──────▶ │  Loki                                │
│  (agent) │         │  ┌──────────┐ ┌──────────┐ ┌─────┐  │
└──────────┘         │  │ Distributor│ │ Ingester│ │Querier│ │
                     │  └──────┬───┘ └──────┬───┘ └──┬──┘  │
┌──────────┐  push   │         │             │        │     │
│  Docker  │ ──────▶ │         ▼             ▼        ▼     │
│  driver  │         │  ┌──────────────────────────────────┐ │
└──────────┘         │  │  Storage (chunks + index)        │ │
                     │  │  - Local FS / S3 / GCS / MinIO   │ │
┌──────────┐  push   │  │  - Index: BoltDB / TSDB          │ │
│  Syslog  │ ──────▶ │  └──────────────────────────────────┘ │
└──────────┘         └──────────┬───────────────────────────┘
                               │ query (LogQL)
                               ▼
                          ┌──────────┐
                          │ Grafana  │
                          └──────────┘
```

## 核心组件

### 1. Distributor

```
接收客户端 push 的日志流
  - 验证 / 限流
  - 按 tenant 分流
  - 转发到 Ingester
```

### 2. Ingester

```
把日志流写入 chunk（默认 24h 一个 chunk）
  - 流式压缩（gzip）
  - 内存 → 定期 flush 到对象存储
  - 同一 label 流的日志聚合到同一 chunk
```

### 3. Querier

```
处理 LogQL 查询
  - 扫描匹配的 chunk
  - 应用 LogQL 过滤
  - 合并 / 排序
```

### 4. Storage

```
Chunk 存储：S3 / GCS / MinIO / 本地磁盘
Index 存储：BoltDB（单实例）/ TSDB（多副本）
```

## 部署模式

### 单二进制模式（开发）

```bash
# 一行启动
loki -config.file=/etc/loki/local-config.yaml
```

### 微服务模式（生产）

```yaml
# docker-compose
services:
  loki:
    image: grafana/loki:2.9.0
    command: -config.file=/etc/loki/config.yaml
  promtail:
    image: grafana/promtail:2.9.0
    command: -config.file=/etc/promtail/config.yaml
  minio:
    image: minio/minio
    command: server /data
```

## 标签设计（核心）

```
Loki 的标签 = 唯一可索引字段
           = 决定查询效率
           = 设计原则：低基数 + 业务维度

良好标签：
  - job: "order-api"
  - env: "prod"
  - service: "order"
  - level: "error|warn|info"

禁用标签：
  - user_id: 高基数
  - request_id: 高基数
  - timestamp: 完全禁忌
  - message: 全文，应该过滤而非标签
```

## 实战案例：Loki 部署 + Promtail

```yaml
# loki config
auth_enabled: false

server:
  http_listen_port: 3100

common:
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory

schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

limits_config:
  retention_period: 744h   # 31 天
  ingestion_rate_mb: 10
  ingestion_burst_size_mb: 20

ruler:
  storage:
    type: local
    local:
      directory: /loki/rules
```

## 一句话总结

> **Loki = Prometheus 式的日志系统**。**只索引 labels，不索引 content**。**优势：成本低 + 与 Prometheus 标签对齐**。**适用：监控日志 / 结构化日志**。

---

## 关联章节

- [LogQL 查询](../05-loki/logql.md)
- [Pipeline 处理](../05-loki/pipeline.md)
- [Loki 最佳实践](../05-loki/best-practice.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>
