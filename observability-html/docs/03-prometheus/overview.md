---
title: Prometheus 架构
description: Prometheus 整体架构与核心组件
---

# Prometheus 架构

> **TL;DR**：Prometheus 是**云原生监控的事实标准**。核心架构是"Pull 模型 + TSDB 存储 + PromQL 查询 + Alertmanager 告警"。**2026 年新项目，监控层 80% 选 Prometheus**。

## 一句话定义

```
Prometheus = 开源时序数据库 + 拉取式 metrics 采集 + PromQL 查询 + 告警引擎
```

## 核心架构

```
┌────────────────────────────────────────────────┐
│                                                │
│   ┌─────────┐    pull (HTTP)    ┌──────────┐  │
│   │Targets  │ ←──────────────── │          │  │
│   │Exporter │                   │Prometheus│  │
│   │Apps     │                   │  Server  │  │
│   └─────────┘                   │          │  │
│       ↑                         │  ┌─────┐ │  │
│       │ push gateway            │  │TSDB │ │  │
│       │ (短期 job)              │  └─────┘ │  │
│   ┌─────────┐                   │          │  │
│   │Pushgw   │ ──push──→         │          │  │
│   └─────────┘                   └────┬─────┘  │
│                                     │         │
│                  ┌──────────────────┼──────┐  │
│                  ↓                  ↓      ↓  │
│          ┌──────────┐       ┌──────────┐  ┌──────────┐
│          │ Grafana  │       │Alertmgr  │  │ Long-term│
│          │ (查询)   │       │(告警)    │  │ Storage  │
│          └──────────┘       └──────────┘  └──────────┘
└────────────────────────────────────────────────┘
```

## 核心组件

### 1. Prometheus Server

**职责**：核心服务，负责抓取、存储、查询。

**架构**：

```
┌──────────────────────────────────────┐
│      Prometheus Server               │
│  ┌────────┐  ┌──────────┐  ┌──────┐ │
│  │Retrieval│  │Storage   │  │Query │ │
│  │(抓取)  │  │(TSDB)    │  │(查询)│ │
│  └────────┘  └──────────┘  └──────┘ │
│  ┌────────┐  ┌──────────┐            │
│  │HTTP    │  │Rule      │            │
│  │API     │  │(告警规则)│            │
│  └────────┘  └──────────┘            │
└──────────────────────────────────────┘
```

### 2. Exporters

**职责**：把第三方系统的指标转换成 Prometheus 格式。

| Exporter | 目标系统 |
|---|---|
| node_exporter | Linux 机器（CPU / 内存 / 磁盘 / 网络） |
| mysqld_exporter | MySQL |
| redis_exporter | Redis |
| kafka_exporter | Kafka |
| elasticsearch_exporter | Elasticsearch |
| postgres_exporter | PostgreSQL |
| blackbox_exporter | HTTP / TCP / ICMP 探测 |

> **Exporter 生态**：100+ 种，覆盖几乎所有主流中间件。

### 3. Pushgateway

**职责**：给短期 Job 提供 push 接口。

**适用场景**：
- 批处理任务（Spark / Flink Job）
- 一次性脚本

**不适用场景**：
- 长期运行的服务（用 Pull 模型）

### 4. Alertmanager

**职责**：处理告警去重、分组、路由、静默、通知。

```
Prometheus → 告警 → Alertmanager
                          ↓
                  ┌───────┼───────┐
                  ↓       ↓       ↓
              邮件    Slack    PagerDuty
              短信    钉钉      OpsGenie
              Webhook 飞书      飞书
```

### 5. Grafana

**职责**：可视化（虽然不是 Prometheus 的一部分，但 99% 配套使用）。

## Pull vs Push 模型

### Pull（Prometheus 默认）

```
Prometheus → 主动拉 → Exporter
       ←──────────────
       暴露 /metrics 端点
```

**优点**：
- 中心化控制（谁来抓、抓什么频率）
- 自动发现（新服务上线自动被抓）
- 健康检查（拉不到 = 服务下线）

**缺点**：
- 需要暴露端口（防火墙问题）
- 不适合短期 Job

### Push

```
App → 主动推 → Pushgateway → Prometheus 拉
```

**适用**：短期 Job（< 1 分钟）

## 存储：TSDB

**TSDB（Time Series Database）** = 时序数据库。

**Prometheus 自带 TSDB**：

```
存储结构：
/prometheus-data/
├── chunks/      # 压缩后的样本块
├── wal/         # Write-Ahead Log（防止崩溃丢数据）
├── queries/     # 查询缓存
└── meta.json    # 元数据
```

**特点**：
- 每 2 小时生成一个 block
- block 不可变（append-only）
- 后台 compaction（合并小块）
- 默认保留 15 天（生产建议 30 天）

### 远程存储（Remote Storage）

**问题**：本地存储不够（30 天 × 1000 实例 × 10000 指标 = TB 级）

**解决**：Prometheus 把样本发到远程存储。

```
Prometheus → remote_write → 远程存储
              ├─ Thanos（基于 S3）
              ├─ Cortex / Mimir（多租户）
              ├─ VictoriaMetrics（高性能）
              └─ 商业：InfluxDB Cloud / Datadog
```

**好处**：水平扩展 + 长期保存 + 跨 Prometheus 联邦查询。

## PromQL（已专文详解）

见 [PromQL 详解](/03-prometheus/promql)。

## 告警：Alertmanager 流程

```
Prometheus 评估规则
     ↓ 触发
Prometheus → Alertmanager
     ↓
   去重（同一告警 5 分钟内只发一次）
     ↓
   分组（按 service + severity）
     ↓
   路由（不同团队 → 不同接收器）
     ↓
   抑制（如果 P0 触发，屏蔽 P3）
     ↓
   静默（维护窗口屏蔽）
     ↓
   通知（Slack / 邮件 / PageDuty）
```

## 部署模式

### 单实例（开发环境）

```yaml
# docker-compose.yaml
prometheus:
  image: prom/prometheus:v2.54.1
  ports:
  - "9090:9090"
  volumes:
  - ./prometheus.yml:/etc/prometheus/prometheus.yml
  command:
  - '--config.file=/etc/prometheus/prometheus.yml'
```

### Prometheus Operator（K8s 生产环境）

**问题**：手写 prometheus.yml 难维护（多团队、多 namespace）。

**答案**：用 Prometheus Operator 管理 CRD。

```
ServiceMonitor CRD → Operator 监听 → 重载 prometheus.yml
PrometheusRule   → Operator 监听 → 重新加载 rules
```

### 联邦（Federation）

**场景**：多个 Prometheus 实例，跨数据中心查询。

```
Prometheus (DC1) ─┐
Prometheus (DC2) ─┤─→ Global Prometheus
Prometheus (DC3) ─┘
```

## 核心配置示例

```yaml
# prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: prod-us-east-1

scrape_configs:
  # Prometheus 自身
  - job_name: prometheus
    static_configs:
    - targets: ['localhost:9090']

  # node_exporter（机器监控）
  - job_name: node
    file_sd_configs:
    - files: ['/etc/prometheus/targets/nodes/*.json']
      refresh_interval: 30s

  # 应用监控（K8s 自动发现）
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
    - role: pod
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
      action: keep
      regex: true
    - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
      action: replace
      target_label: __metrics_path__
      regex: (.+)

alerting:
  alertmanagers:
  - static_configs:
    - targets: ['alertmanager:9093']

rule_files:
  - "/etc/prometheus/rules/*.yml"
```

## 高可用（HA）

### 方案 1：双 Prometheus + Thanos

```
Prometheus (active) ──┐
Prometheus (active) ──┤──→ Thanos Sidecar ──→ S3 / GCS
   同一 targets 双重抓取           ↓
                              Query / Store
```

**缺点**：存储 2 倍（每个都存）

### 方案 2：Mimir / Cortex（多租户）

```
Prometheus ──→ remote_write → Mimir / Cortex（统一存储 + 多租户）
                                     ↓
                              Query Frontend
```

**优点**：存储不重复 + 多租户 + 长保留

## 选型决策

```
1. 单实例 Prometheus 够用吗？
├─ 指标数 < 1000 万 + 保留 < 30 天 → 单实例
└─ 不够 → 走 remote storage

2. 多 Prometheus 实例需要联邦吗？
├─ 跨数据中心查询 → Federation
└─ 只是高可用 → 双实例 + Thanos

3. 商业方案还是开源？
├─ 预算紧 → Prometheus + 任意后端
└─ 预算足 → Datadog / Grafana Cloud
```

## 一句话总结

> **Prometheus = Pull + TSDB + PromQL + Alertmanager 四件套**。
> 中小规模直接用，规模大了上 Thanos / Mimir。**2026 年事实标准，新项目直接选它**。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

<!-- svg-injected:do-not-edit -->

## 图示：Prometheus 监控架构

![Prometheus 监控架构](/prometheus-architecture.svg)
