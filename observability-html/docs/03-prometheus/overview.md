---
title: Prometheus 架构
date: 2026-08-15  # date-auto-injected
description: Prometheus 整体架构与核心组件
---

# Prometheus 架构

> **TL;DR**：Prometheus 是**云原生监控的事实标准**。核心架构是"Pull 模型 + TSDB 存储 + PromQL 查询 + Alertmanager 告警"。**2026 年新项目，监控层 80% 选 Prometheus**。

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">Prometheus 架构</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">Pull 模型 · 多维标签 · PromQL · Alertmanager</text>

  <!-- Targets (左) -->
  <text x="80" y="95" text-anchor="middle" font-size="12" font-weight="700" fill="#1e293b">Targets（被采集）</text>

  <rect class="at-hover-card" x="30" y="105" width="100" height="35" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="80" y="128" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">App /metrics</text>

  <rect class="at-hover-card" x="30" y="150" width="100" height="35" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="80" y="173" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">Node Exporter</text>

  <rect class="at-hover-card" x="30" y="195" width="100" height="35" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="80" y="218" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">cAdvisor</text>

  <rect class="at-hover-card" x="30" y="240" width="100" height="35" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="80" y="263" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">Pushgateway</text>

  <!-- 中央 Prometheus Server -->
  <rect class="at-hover-card" x="200" y="100" width="220" height="200" rx="8" fill="#fee2e2" stroke="#dc2626" stroke-width="2"/>
  <text x="310" y="125" text-anchor="middle" font-size="14" font-weight="700" fill="#991b1b">Prometheus Server</text>

  <rect x="215" y="135" width="190" height="30" rx="4" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="310" y="155" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">Retrieval（抓取）</text>

  <rect x="215" y="170" width="190" height="30" rx="4" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="310" y="190" text-anchor="middle" font-size="10" font-weight="700" fill="#047857">TSDB 时序存储</text>

  <rect x="215" y="205" width="190" height="30" rx="4" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="310" y="225" text-anchor="middle" font-size="10" font-weight="700" fill="#1e40af">PromQL 引擎</text>

  <rect x="215" y="240" width="190" height="30" rx="4" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="310" y="260" text-anchor="middle" font-size="10" font-weight="700" fill="#5b21b6">HTTP API + Web UI</text>

  <!-- 抓取箭头 -->
  <line x1="130" y1="122" x2="200" y2="155" stroke="#3b82f6" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="130" y1="167" x2="200" y2="155" stroke="#3b82f6" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="130" y1="212" x2="200" y2="155" stroke="#3b82f6" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="130" y1="257" x2="200" y2="220" stroke="#f59e0b" stroke-width="1.5" marker-end="url(#arr)" stroke-dasharray="4,2"/>
  <text x="165" y="270" font-size="9" fill="#92400e">push</text>

  <!-- Alertmanager -->
  <rect class="at-hover-card" x="460" y="100" width="120" height="50" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="520" y="123" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">Alertmanager</text>
  <text x="520" y="140" text-anchor="middle" font-size="9" fill="#475569">去重 / 路由 / 抑制</text>

  <line x1="420" y1="145" x2="460" y2="125" stroke="#dc2626" stroke-width="1.5" marker-end="url(#arr)"/>

  <!-- 通知目标 -->
  <rect class="at-hover-card" x="460" y="170" width="120" height="35" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="520" y="190" text-anchor="middle" font-size="10" font-weight="700" fill="#047857">Slack / Email</text>

  <rect class="at-hover-card" x="460" y="215" width="120" height="35" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="520" y="235" text-anchor="middle" font-size="10" font-weight="700" fill="#047857">PagerDuty / Webhook</text>

  <line x1="520" y1="150" x2="520" y2="170" stroke="#10b981" stroke-width="1.5" marker-end="url(#arr)"/>
  <line x1="520" y1="205" x2="520" y2="215" stroke="#10b981" stroke-width="1.5" marker-end="url(#arr)"/>

  <!-- 远端存储 -->
  <rect class="at-hover-card" x="460" y="270" width="120" height="35" rx="6" fill="#ede9fe" stroke="#8b5cf6" stroke-width="1.5"/>
  <text x="520" y="290" text-anchor="middle" font-size="10" font-weight="700" fill="#5b21b6">Remote Storage</text>

  <line x1="420" y1="280" x2="460" y2="285" stroke="#8b5cf6" stroke-width="1.5" marker-end="url(#arr)" stroke-dasharray="4,2"/>
  <text x="430" y="275" font-size="9" fill="#5b21b6">remote_write</text>

  <!-- 关键点 -->
  <rect x="30" y="325" width="540" height="140" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="300" y="348" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">关键属性</text>

  <text x="50" y="372" font-size="11" font-weight="600" fill="#1e293b">① 数据模型</text>
  <text x="50" y="390" font-size="10" fill="#475569">metric_name{label1=v1, label2=v2} value timestamp</text>

  <text x="320" y="372" font-size="11" font-weight="600" fill="#1e293b">② 4 种 metric 类型</text>
  <text x="320" y="390" font-size="10" fill="#475569">Counter / Gauge / Histogram / Summary</text>

  <text x="50" y="415" font-size="11" font-weight="600" fill="#1e293b">③ Pull 模型优势</text>
  <text x="50" y="433" font-size="10" fill="#475569">· 服务发现自动扩缩容友好</text>
  <text x="50" y="448" font-size="10" fill="#475569">· 单点故障时易观测（采集失败暴露）</text>

  <text x="320" y="415" font-size="11" font-weight="600" fill="#1e293b">④ 局限</text>
  <text x="320" y="433" font-size="10" fill="#475569">· 短生命周期任务用 Pushgateway</text>
  <text x="320" y="448" font-size="10" fill="#475569">· 高基数（label 爆炸）→ TSDB 压力大</text>
</svg>

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

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [devops](https://java-px.bot.cd/devops/):DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/):K8s 监控
- [kafka](https://java-px.bot.cd/kafka/):日志收集
