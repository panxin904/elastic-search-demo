---
layout: home
title: Observability 知识图谱
date: 2026-08-27  # date-auto-injected
hero:
  name: Observability
  text: 现代可观测性深度图谱
  tagline: Metrics · Logs · Traces · Profiling · OpenTelemetry · Prometheus · Grafana · SRE 三件套
  actions:
    - theme: brand
      text: 🏛️ 进入基础入门
      link: /01-foundations/observability-vs-monitoring
    - theme: alt
      text: 📈 跳转 Prometheus
      link: /03-prometheus/overview
    - theme: alt
      text: 🌐 OpenTelemetry
      link: /02-opentelemetry/overview
    - theme: alt
      text: 🌍 实战场景
      link: /11-scenarios/k8s-monitor
features:
  - title: 🏛️ 可观测性基础
    details: 从监控到可观测性的范式转变、四支柱（Metrics/Logs/Traces/Events）、信号类型、SLI/SLO/Error Budget 三件套。
    link: /01-foundations/observability-vs-monitoring
    linkText: 监控 vs 可观测性
  - title: 🌐 OpenTelemetry 全景
    details: CNCF 顶级项目，统一 metrics/logs/traces 三大信号的采集与传输。SDK / OTLP / Collector / 自动埋点一站式讲解。
    link: /02-opentelemetry/overview
    linkText: OTel 是什么
  - title: 📈 Prometheus + PromQL
    details: 云原生监控的事实标准，Pull 模型 + PromQL 强大查询 + Recording Rule + Alerting Rule。Exporter 生态覆盖 100+ 中间件。
    link: /03-prometheus/promql
    linkText: PromQL 详解
  - title: 📊 Grafana 可视化
    details: 业界最流行的监控可视化平台。Dashboard 设计原则、模板变量联动、Annotation 标注、Alerting 告警一条龙。
    link: /04-grafana/dashboard
    linkText: Dashboard 设计
  - title: 📜 Loki 日志聚合
    details: Grafana 系日志系统，类 PromSQL 的 LogQL、与 Prometheus 同款标签模型、低成本对象存储。
    link: /05-loki/overview
    linkText: Loki 架构
  - title: 🔗 全链路追踪
    details: Jaeger / Tempo / Zipkin 三大追踪系统对比，OTLP 协议选型，Span/Trace/Context Propagation。
    link: /06-tracing/concepts
    linkText: Trace / Span 概念
  - title: 🌲 ELK / EFK 经典栈
    details: ES + Fluentd/Filebeat + Kibana 经典日志方案，集群部署、索引生命周期、Pipeline 解析。
    link: /07-elk-efk/elasticsearch-logs
    linkText: ES 作日志存储
  - title: 🚨 告警与值班
    details: Alertmanager 告警分组/抑制/静默，告警分级 P0/P1/P2，On-call 值班与故障复盘。
    link: /08-alerting/alertmanager
    linkText: Alertmanager
  - title: 🧪 应用埋点方法
    details: RED 方法（Rate/Error/Duration）、USE 方法（Utilization/Saturation/Errors）、JVM/K8s/业务指标实战。
    link: /09-app-instrumentation/red-method
    linkText: RED 方法
  - title: 🔥 持续剖析
    details: Continuous Profiling 持续剖析定位 CPU/内存/锁热点。Go pprof / Java async-profiler / Pyroscope 三大工具实战。
    link: /10-profiling/continuous-profiling
    linkText: Continuous Profiling
  - title: 🌍 K8s 全栈监控
    details: ServiceMonitor + PrometheusRule + Grafana 完整 yaml 实战，覆盖 Nacos / MySQL / Redis / Kafka 全套中间件。
    link: /11-scenarios/k8s-monitor
    linkText: K8s 实战案例
  - title: 💸 监控成本优化
    details: 降采样、标签治理、存储分层、冷热数据分离。把 Prometheus 存储成本砍掉 70% 的实战经验。
    link: /11-scenarios/cost-optimization
    linkText: 成本优化
---

<script setup>
// WhyThisGraph 数据：原写在 :prop="..." 里会触发 Vue 编译错误（多行 YAML 数组），
// 改为 script setup 形式。
const painPoints = [
      "单体时代（CPU/内存/磁盘）vs 微服务时代（调用链/性能瓶颈）监控差异？",
      "Metrics / Logs / Traces 三件套怎么选型（Prometheus / Loki / Jaeger）？",
      "OpenTelemetry（OTel） Collector / SDK / Exporter 怎么部署？",
      "SLO / SLI / Error Budget 怎么设计与度量？",
      "告警风暴怎么治理？告警分级 + 抑制 + 路由？"
    ]
const goals = [
      "可观测性基础（Metrics / Logs / Traces 三件套）",
      "Metrics 体系（Prometheus / VictoriaMetrics / Grafana Mimir）",
      "Logs 体系（Loki / ELK / ClickHouse）",
      "Traces 体系（Jaeger / Tempo / OpenTelemetry）",
      "SLO / SLI / Error Budget 工程实践",
      "告警治理 + AIOps"
    ]
const relatedSites = [
      { site: "devops", path: "/05-cicd-observability/sre", label: "SRE 实践" },
      { site: "cloud-native", path: "/05-observability/prometheus", label: "Prometheus" },
      { site: "kafka", path: "/01-basics/architecture", label: "Kafka 架构" },
      { site: "es", path: "/01-storage/overview", label: "ES 日志存储" },
      { site: "clickhouse", path: "/01-storage/index-design", label: "ClickHouse 日志" }
    ]
</script>

<ClientOnly>
  <WhyThisGraph
    :pain-points="painPoints"
    :goals="goals"
    :related-sites="relatedSites"
    title="🎯 为什么写这个图谱？"
  />
</ClientOnly>


# Observability · 现代可观测性深度图谱

> **本站点定位**：补完「开发 → 上线 → 运维」链路中**运行期**这一环。
> 中间件站（kafka / redis / es / mysql / postgresql）只讲"怎么用"，本站讲"用了之后怎么观测"。

## 为什么需要可观测性

| 时代 | 关注点 | 工具 |
|---|---|---|
| 单体时代 | 服务器 CPU / 内存 / 磁盘 | Nagios / Zabbix |
| 微服务时代 | 服务调用链 / 性能瓶颈 | Prometheus / Jaeger / ELK |
| 云原生 + AI 时代 | 全栈信号 + 自动发现 | OpenTelemetry + Grafana + Pyroscope |

**核心范式转变**：从"监控已知"（CPU 高了告警）到"观测未知"（为什么这个用户请求慢了 800ms）。

## 11 大主题 · 47 个知识节点

```
01-foundations (4)  · 可观测性基础
02-opentelemetry (5)· OpenTelemetry 全景
03-prometheus (5)   · Prometheus + PromQL
04-grafana (5)      · Grafana 可视化
05-loki (4)         · Loki 日志聚合
06-tracing (5)      · 全链路追踪
07-elk-efk (4)      · ELK / EFK 经典栈
08-alerting (4)     · 告警与值班
09-app-instrumentation (5) · 应用埋点
10-profiling (4)    · 持续剖析
11-scenarios (4)    · 实战场景
```

## 与其他站点的关系

- **cloud-native / K8s** ↔ observability：K8s 跑起来之后如何观测
- **ai / LLM** ↔ observability：LLM 应用的 token / 成本 / latency 监控
- **kafka / redis / es / mysql / postgresql** ↔ observability：每个中间件都有自己的 exporter / 埋点
- **system-design** ↔ observability：分布式系统的"可观测性"是 CAP 之外的重要非功能性需求

## 阅读路径建议

- **运维 / SRE**：01 → 03 → 04 → 05 → 08 → 11
- **后端开发**：01 → 02 → 03 → 06 → 09 → 10
- **架构师 / 平台工程**：01 → 02 → 04 → 08 → 11

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>

## 📚 相关阅读（跨站导航）

<!-- xlink-injected:do-not-edit -->

按主题跨站推荐：

- [devops](https://java-px.bot.cd/devops/)：DevOps 监控
- [cloud-native](https://java-px.bot.cd/cloud-native/)：K8s 监控
- [kafka](https://java-px.bot.cd/kafka/)：日志收集
- [es](https://java-px.bot.cd/es/)：日志存储
- [java](https://java-px.bot.cd/java-web-manual/)：Java APM


## 💬 评论与反馈

有问题或建议？欢迎在下方评论。

<ClientOnly>
  <GiscusComment />
</ClientOnly>
