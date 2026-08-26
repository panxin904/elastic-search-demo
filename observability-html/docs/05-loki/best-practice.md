---
title: Loki 最佳实践
description: 标签设计 / 存储优化 / 性能调优
---

# Loki 最佳实践

> **TL;DR**：**Loki 最佳实践 = 标签设计（低基数）+ 存储分层（hot/warm/cold）+ 写入优化（batch）+ 查询优化（缩小时间窗）**。**核心原则：标签决定成本，原文不索引**。**实战：单集群可承载日均 1TB 日志**。

## 一句话定义

```
Loki 最佳实践 = 标签设计 + 存储优化 + 写入优化 + 查询优化
             = 核心：让标签有意义但不爆量
             = 让 chunk 压缩率高
             = 让查询扫描范围小
```

## 标签设计（最重要）

### 良好实践

```yaml
labels:
  # 业务维度（必加）
  job: "order-api"           # 服务名
  env: "prod"                # 环境
  cluster: "prod-cn-north"   # 集群
  namespace: "ecommerce"     # K8s namespace

  # 关键状态（必加）
  level: "error|warn|info"   # 日志级别（低基数）
  service: "order"           # 业务服务

  # 来源（必加）
  source: "app|nginx|system"

  # 不要的：
  # ❌ user_id, request_id, order_id (高基数)
  # ❌ ip（除非 NAT 后唯一）
  # ❌ timestamp, datetime
  # ❌ message（应该 LogQL filter）
```

### 标签数量控制

```
每个日志流的标签建议 5-10 个
每条日志流的标签基数总和 < 10000
例：job × env × level = 20 × 3 × 3 = 180 个时间序列，可接受
```

## 存储优化

### 1. 存储分层

```yaml
# 短期：本地磁盘（hot）
# 长期：S3/GCS/MinIO（warm/cold）

common:
  storage:
    s3:
      s3: s3://cn-north-1/loki-chunks
      s3forcepathstyle: true
      access_key_id: xxx
      secret_access_key: xxx

schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: s3
      schema: v13
      index:
        prefix: index_
        period: 24h
```

### 2. 压缩

```yaml
# Chunk 默认 gzip 压缩（80%+ 压缩率）
# 进一步启用 LZ4（更快压缩）

limits_config:
  ingestion_rate_mb: 10      # 限制每租户速率
  ingestion_burst_size_mb: 20
  reject_old_samples: true
  reject_old_samples_max_age: 168h
```

### 3. Retention（保留期）

```yaml
limits_config:
  retention_period: 744h   # 31 天
  # 超期自动删除

compactor:
  working_directory: /loki/compactor
  compaction_interval: 10m
  retention_enabled: true
  retention_delete_delay: 2h
  delete_request_store: filesystem
```

## 写入优化

### 1. Promtail batch

```yaml
# promtail 配置
clients:
  - url: http://loki:3100/loki/api/v1/push
    batchwait: 1s          # 等待新日志的最长时间
    batchsize: 1048576     # 1MB 触发 batch
    backoff_config:
      min_period: 500ms
      max_period: 5m
```

### 2. 多租户

```yaml
# Loki 多租户隔离（auth_enabled: true）
# 每个应用/团队一个 tenant
# 限流独立（防止一个团队打爆）

auth_enabled: true

# tenant 通过 X-Scope-OrgID header 传递
```

## 查询优化

### 1. 缩小时间窗口

```logql
# 错误：查询全量
{job="nginx"} |= "error"

# 正确：限定时间窗
{job="nginx"} |= "error" [5m]
```

### 2. 利用标签

```logql
# 错误：扫描所有日志流
{job=~".+"} |= "500"

# 正确：用标签缩小范围
{job="nginx", level="error"} |= "500"
```

### 3. 控制返回行数

```logql
# LogQL 加 limit
{job="nginx"} |= "500" | limit 100
```

### 4. Metric query 用 rate

```logql
# 错误：count 然后 rate（无法计算）
count_over_time({job="nginx"} |= "500" [5m])

# 正确：用 rate
sum(rate({job="nginx"} |= "500" [5m]))
```

## 监控 Loki 自身

```promql
# Loki 写入速率
loki_distributor_lines_received_total

# Loki 摄入速率
loki_ingester_chunk_bytes_received_total

# Loki 查询延迟
loki_request_duration_seconds_bucket{path="/loki/api/v1/query"}

# 当前租户活跃 series 数
loki_ingester_active_series
```

## 一句话总结

> **Loki 最佳实践 = 标签低基数 + 存储分层 + 写入 batch + 查询窄范围**。**标签设计决定成本**。**新项目首选 Loki（监控日志）/ ES（全文检索）**。

---

## 关联章节

- [Loki 概览](../05-loki/overview.md)
- [LogQL 查询](../05-loki/logql.md)
- [Pipeline 处理](../05-loki/pipeline.md)

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
