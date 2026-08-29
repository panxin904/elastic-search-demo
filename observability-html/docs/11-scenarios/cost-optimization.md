---
title: 可观测成本优化
date: 2026-08-15  # date-auto-injected
description: 存储成本 / 采样 / 保留期 / 标签基数
---

# 可观测成本优化

> **TL;DR**：**可观测成本 = 三大开销（Metrics / Logs / Traces）**。**优化策略：Metrics 降采样 + Logs 保留期分层 + Traces tail-based sampling**。**典型节省：50-80% 成本（vs 默认配置）**。**核心原则：保留有价值的，丢弃可重算的**。

## 一句话定义

```
可观测成本 = Metrics 存储（~30%）+ Logs 存储（~50%）+ Traces 存储（~20%）
         = 取决于：保留期 × 标签基数 × 采样率
         = 优化核心：丢弃不需要的，保留有用的
```

## Metrics 成本优化

### 1. 标签基数治理

```yaml
# 杀手：高基数标签
- service: order-api                  # 10 个服务 = 10
- env: prod                          # 3 个环境 = 30
- user_id: "12345"                   # 100w 用户 = 100w × 30 = 3000w 时序
                                      # 一天 100w 时序 × 30 bytes = 30GB/天
                                      # 30 天 = 900GB → 成本爆炸

# 解决：
- user_id → 移到 log / trace，不放 metric label
- bucket histogram → 用 log / quantile，不放全量时序
```

### 2. 降采样 + 长期保留

```yaml
# Prometheus remote_write + downsampling
remote_write:
  - url: http://thanos-receive:19291/api/v1/receive
    write_relabel_configs:
      - source_labels: [__name__]
        regex: 'go_.*|process_.*|node_.*'
        action: drop                  # 删掉 go runtime 指标（高基数）

# Thanos / Cortex 自动降采样
# raw → 5min → 1h 三层
# raw 保留 7d（高分辨率）
# 5min 保留 30d
# 1h 保留 1y
```

### 3. Mimir 块存储压缩

```
Mimir vs Prometheus 本地存储：
  - Mimir：对象存储（S3/GCS），压缩 + 分块，~0.1 美元/GB·月
  - Prometheus 本地：磁盘，~0.5 美元/GB·月
  - 节省：80%
```

## Logs 成本优化

### 1. 保留期分层（ILM）

```yaml
# ES ILM（详细见 elasticsearch-logs.md）
hot: 7d, 50GB shard    # 高频查询
warm: 30d              # 偶尔查询
cold: 90d, freeze      # 几乎不查
delete: 365d

# 成本估算：
# 日均 100GB × 7 天 hot = 700GB（SSD ~0.23/GB·月 = $161）
# 日均 100GB × 30 天 warm = 3000GB（HDD ~0.05/GB·月 = $150）
# 日均 100GB × 90 天 cold = 9000GB（OSS ~0.02/GB·月 = $180）
# 总计 ~$491/月
```

### 2. 采样 + 过滤

```yaml
# Promtail / Vector 端做过滤
pipeline_stages:
  - match:
      selector: '{job="nginx"}'
      stages:
        # 丢弃健康检查日志
        - drop:
            expression: ".*healthcheck.*"
        # 丢弃 2xx 成功请求（保留 4xx/5xx）
        - match:
            selector: '{status="2.."}'
            stages:
              - sampling:
                  rate: 0.01   # 只采样 1%
```

### 3. Loki 替代 ES（成本骤降）

```
ES（默认）：全文索引，每条日志都建倒排索引
  → 100GB/天 × 30天 = 3TB
  → 存储成本 $300-700/月

Loki：只索引标签，不索引内容
  → 100GB/天 × 30天 = 3TB（chunk 高度压缩）
  → 存储成本 $50-150/月
  → 节省 70%

权衡：Loki 全文检索弱（要扫 chunk），但 90% 场景够用
```

## Traces 成本优化

### 1. 采样策略

```yaml
# Head-based sampling（SDK 端决策）
processors:
  probabilistic_sampler:
    sampling_percentage: 10   # 10% 采样

# Tail-based sampling（Collector 端决策，更智能）
processors:
  tail_sampling:
    decision_wait: 10s
    num_traces: 100000
    policies:
      # 错误 100% 保留
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      # 慢请求 100% 保留
      - name: slow
        type: latency
        latency: { threshold_ms: 1000 }
      # 健康请求 5% 采样
      - name: default
        type: probabilistic
        probabilistic: { sampling_percentage: 5 }
```

### 2. 存储分层

```
Tempo / Jaeger:
  - hot: 7d，OSS + 高频查询
  - cold: 30d，对象存储 + 低频查询
  - archive: 1y，对象存储（极冷） + 不查

成本：
  - 100% 采样：100GB/天 × 30天 = 3TB × $0.02 = $60/月
  - 10% 采样：10GB/天 × 30天 = 300GB × $0.02 = $6/月
  - tail-based 5%：~5GB/天 × 30天 = 150GB × $0.02 = $3/月
  - 节省 95%
```

### 3. 协议选择

```
Zipkin → OTLP：
  - OTLP 用 protobuf（更紧凑）
  - HTTP/2 多路复用（更高效）
  - 节省带宽 30-50%
```

## 成本估算（典型 100 服务企业）

```
场景：
  - 100 微服务
  - 日均 QPS 100w
  - 日志 500GB/天
  - Trace 100% 采样 = 200GB/天

默认配置成本：
  - Prometheus: 10 节点 × 1TB × $0.5/GB·月 = $5000/月
  - ES 日志: 15TB × $0.05 = $750/月
  - Jaeger: 6TB × $0.5 = $3000/月
  - 总计: ~$9000/月

优化后：
  - Mimir（标签治理 + 降采样）: ~$500/月
  - Loki（替代 ES + 过滤 90%）: ~$150/月
  - Tempo（tail-based 5% 采样）: ~$30/月
  - 总计: ~$700/月

节省：92%
```

## 一句话总结

> **可观测成本优化 = 标签治理 + 保留分层 + 智能采样**。**90% 节省不牺牲质量**。**生产标配：Mimir + Loki + Tempo + tail-based sampling**。

---

## 关联章节

- [K8s 监控](./k8s-monitor.md)
- [Tracing 基础](../06-tracing/concepts.md)
- [Database 监控](./database-monitor.md)
- [Alertmanager](../08-alerting/alertmanager.md) — 告警也耗资源

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
