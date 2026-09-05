---
title: 监控 vs 可观测性
date: 2026-08-15  # date-auto-injected
description: 从传统监控到现代可观测性的范式转变
---

# 监控 vs 可观测性：一次范式转变

> **TL;DR**：监控 = 告诉你系统**已知**的状态（CPU 90%）。可观测性 = 让你能回答系统**未知**的问题（为什么这个用户请求慢了 800ms）。

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">可观测性三大支柱</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">Metrics · Logs · Traces（互补而非替代）</text>

  <!-- Metrics -->
  <rect class="at-hover-card" x="30" y="90" width="170" height="240" rx="8" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="115" y="115" text-anchor="middle" font-size="14" font-weight="700" fill="#1e40af">📊 Metrics</text>
  <text x="115" y="135" text-anchor="middle" font-size="10" fill="#475569">指标 · 聚合数值</text>

  <text x="50" y="165" font-size="10" font-weight="700" fill="#1e293b">形态</text>
  <text x="50" y="180" font-size="10" fill="#334155">数值 + 时间戳 + 标签</text>

  <text x="50" y="205" font-size="10" font-weight="700" fill="#1e293b">工具</text>
  <text x="50" y="220" font-size="9" fill="#475569">Prometheus / InfluxDB</text>
  <text x="50" y="232" font-size="9" fill="#475569">Datadog / CloudWatch</text>

  <text x="50" y="252" font-size="10" font-weight="700" fill="#10b981">+ 低成本 / 适合告警</text>
  <text x="50" y="267" font-size="10" font-weight="700" fill="#10b981">+ 趋势分析 / 容量规划</text>
  <text x="50" y="287" font-size="10" font-weight="600" fill="#dc2626">- 缺上下文（why？）</text>
  <text x="50" y="302" font-size="10" font-weight="600" fill="#dc2626">- 需预设指标</text>

  <text x="50" y="322" font-size="9" fill="#475569" font-style="italic">问「系统是否健康」</text>

  <!-- Logs -->
  <rect class="at-hover-card" x="215" y="90" width="170" height="240" rx="8" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
  <text x="300" y="115" text-anchor="middle" font-size="14" font-weight="700" fill="#047857">📜 Logs</text>
  <text x="300" y="135" text-anchor="middle" font-size="10" fill="#475569">日志 · 离散事件</text>

  <text x="235" y="165" font-size="10" font-weight="700" fill="#1e293b">形态</text>
  <text x="235" y="180" font-size="10" fill="#334155">结构化 / 半结构化文本</text>

  <text x="235" y="205" font-size="10" font-weight="700" fill="#1e293b">工具</text>
  <text x="235" y="220" font-size="9" fill="#475569">ELK / Loki / Splunk</text>
  <text x="235" y="232" font-size="9" fill="#475569">Fluentd / Vector</text>

  <text x="235" y="252" font-size="10" font-weight="700" fill="#10b981">+ 上下文丰富</text>
  <text x="235" y="267" font-size="10" font-weight="700" fill="#10b981">+ 根因定位</text>
  <text x="235" y="287" font-size="10" font-weight="600" fill="#dc2626">- 存储 / 解析成本高</text>
  <text x="235" y="302" font-size="10" font-weight="600" fill="#dc2626">- 高基数爆炸</text>

  <text x="235" y="322" font-size="9" fill="#475569" font-style="italic">问「发生了什么」</text>

  <!-- Traces -->
  <rect class="at-hover-card" x="400" y="90" width="170" height="240" rx="8" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="485" y="115" text-anchor="middle" font-size="14" font-weight="700" fill="#92400e">🔗 Traces</text>
  <text x="485" y="135" text-anchor="middle" font-size="10" fill="#475569">链路 · 因果关系</text>

  <text x="420" y="165" font-size="10" font-weight="700" fill="#1e293b">形态</text>
  <text x="420" y="180" font-size="10" fill="#334155">Span DAG + Context</text>

  <text x="420" y="205" font-size="10" font-weight="700" fill="#1e293b">工具</text>
  <text x="420" y="220" font-size="9" fill="#475569">Jaeger / Zipkin / Tempo</text>
  <text x="420" y="232" font-size="9" fill="#475569">OpenTelemetry SDK</text>

  <text x="420" y="252" font-size="10" font-weight="700" fill="#10b981">+ 跨服务因果</text>
  <text x="420" y="267" font-size="10" font-weight="700" fill="#10b981">+ 延迟分析</text>
  <text x="420" y="287" font-size="10" font-weight="600" fill="#dc2626">- 采样难 / 存储大</text>
  <text x="420" y="302" font-size="10" font-weight="600" fill="#dc2626">- 侵入性（需插桩）</text>

  <text x="420" y="322" font-size="9" fill="#475569" font-style="italic">问「请求经过哪里」</text>

  <!-- 底部关系图 -->
  <rect x="30" y="350" width="540" height="115" rx="6" fill="#f1f5f9" stroke="#cbd5e1"/>
  <text x="300" y="375" text-anchor="middle" font-size="13" font-weight="700" fill="#1e293b">三者关系：互为正交、互补缺失</text>

  <text x="50" y="402" font-size="11" fill="#334155">· Metric 告警 → Log 定位上下文 → Trace 找跨服务瓶颈</text>
  <text x="50" y="422" font-size="11" fill="#334155">· Trace 上的 span 可携带 metric / log 属性（事件嵌入）</text>
  <text x="50" y="442" font-size="11" fill="#334155">· Log 通过 trace_id / span_id 关联到具体链路</text>
  <text x="50" y="458" font-size="10" fill="#475569" font-style="italic">现代可观测性平台（如 Datadog / Grafana Stack）将三者统一</text>
</svg>

## 一句话定义

| 概念 | 定义 | 回答的问题 | 范式 |
|---|---|---|---|
| **Monitoring** | 收集预设指标 + 阈值告警 | "系统现在正常吗？" | 已知问题 |
| **Observability** | 从系统输出推断内部状态的能力 | "为什么用户 A 看到错误 B？" | 未知问题 |

> 可观测性是 monitoring 的**超集**，不是替代品。一个可观测的系统必然包含了所有监控能力。

## 为什么需要范式转变

### 单体时代：监控够用

```
App Server ──→ CPU / 内存 / 磁盘 / 网络
                        ↓
                    Nagios / Zabbix
                        ↓
                   阈值告警（CPU > 80%）
```

**特点**：
- 应用实例少（1-10 个）
- 调用路径短（用户 → 应用 → DB）
- 故障模式已知（磁盘满、CPU 高）
- 阈值告警足够定位问题

### 微服务时代：监控不够了

```
Gateway → Auth → Order → Inventory → Payment → DB
                                    ↓
                                  Kafka
                                    ↓
                                Search
```

**特点**：
- 服务实例多（100-10000 个）
- 调用路径长（5-20 个服务一跳）
- 故障模式未知（某个新部署引入的延迟）
- **阈值告警只能告诉你"有告警"，不能告诉你"为什么"**

> 这就是为什么 Netflix 在 2010 年代初提出"可观测性"概念。**他们不是要替换监控，是要回答监控答不了的问题**。

## 可观测性的三大支柱（后来变四）

```
Metrics（指标）── 数值型时间序列，CPU/内存/QPS/延迟
     ↓
Logs（日志）───── 离散事件，结构化或非结构化
     ↓
Traces（追踪）─── 请求在分布式系统中的完整路径
     ↓
Events（事件）─── 部署/配置变更/业务事件
     ↓
可观测性 = 用这四类信号的关联，回答"为什么"
```

> **注意**：业界对"几大支柱"没有统一标准。Honeycomb / Lightstep 强调"high-cardinality events"，Grafana / OTel 强调"三大支柱 + 事件"，Datadog / NewRelic 商业产品都有自己的营销话术。**不要纠结概念，记住核心：可观测性是"问未知问题的能力"**。

## 实际例子

### 例子 1：传统监控答得了

**问题**：CPU 使用率 95%

**监控**：
```
CPU > 80% 持续 5 分钟 → 告警
```

**可观测性也答得了**（且更详细）：
```
CPU = 95% from container order-service
  + 进程 GC 时间占比 60%
  + 同一时段 order-service 错误率从 0.1% 升到 5%
  + 关联：刚刚的部署 v2.3.1 引入了缓存击穿
```

### 例子 2：只有可观测性答得了

**问题**：用户反馈"搜索结果比平时慢 2 秒"，但监控大盘全绿

**监控答不了**：
- CPU 正常、内存正常、QPS 正常、错误率 0%
- 没有预设的"搜索延迟"阈值告警（搜索服务刚发布）

**可观测性能回答**：
```
1. 拉搜索请求的 trace（按 user_id 过滤）
2. 发现某些 trace 在 ES query 阶段耗时 2.5s
3. 看 ES 日志：慢查询来自新加的 regex 过滤
4. 看 metrics：ES regex query p99 飙到 3s
5. 关联事件：3 小时前的部署启用了新的 regex 功能
```

## 可观测性的四个黄金信号

Google SRE Book 提出的 **Four Golden Signals**：

| 信号 | 含义 | 典型指标 |
|---|---|---|
| **Latency** | 服务一个请求需要多久 | p50 / p95 / p99 / p99.9 |
| **Traffic** | 服务承受多大的流量 | QPS / 并发数 / 字节数 |
| **Errors** | 失败请求的比例 | 错误率 / 5xx 计数 |
| **Saturation** | 服务离饱和还有多远 | CPU 利用率 / 队列长度 / 连接池占用 |

> **简化版**：Latency + Traffic + Errors + Saturation。**任何业务系统，先把这四个信号埋好，再谈可观测性**。

## RED vs USE：两种实践框架

### RED 方法（Weaveworks 提出）

适用对象：**服务**（微服务视角）

```
R - Rate      每秒请求数
E - Errors    每秒错误数
D - Duration  延迟分布（p50/p95/p99）
```

### USE 方法（Brendan Gregg 提出）

适用对象：**资源**（机器视角）

```
U - Utilization  利用率（CPU 70%）
S - Saturation   饱和度（队列长度 100/1000）
E - Errors       错误数（网卡丢包率 0.01%）
```

> **实践建议**：每个服务埋 RED 信号，每个机器埋 USE 信号。两者**互补**，不是二选一。

## 可观测性的成本陷阱

可观测性 ≠ 越多越好。

**三类成本**：

| 成本类型 | 典型场景 | 控制方法 |
|---|---|---|
| **采集成本** | 每请求一个 span × 100w QPS × 30 天 | 采样（tail-based / head-based） |
| **存储成本** | Prometheus TSDB / ES 索引 | 降采样、标签治理、TTL |
| **认知成本** | 告警风暴 / 大盘太多 / 指标爆炸 | 黄金信号优先、告警分级 |

> **黄金法则**：能回答"为什么"的最少信号集。**不要让开发者为了省事就埋所有指标**，那是另一种灾难。

## 工具生态速览

| 类别 | 开源代表 | 商业代表 |
|---|---|---|
| Metrics | Prometheus / VictoriaMetrics / Thanos | Datadog / NewRelic |
| Logs | Loki / ELK / ClickHouse | Splunk / Sumo Logic |
| Traces | Jaeger / Tempo / Zipkin | Honeycomb / Lightstep |
| Profiling | Pyroscope / Parca / async-profiler | Datadog Continuous Profiler |
| 全栈 | Grafana + OTel Collector | Datadog / Dynatrace |

> **2024 之后趋势**：**OpenTelemetry** 统一采集层 + **Grafana** 统一可视化层 + 各家存储后端（Prometheus / Loki / Tempo / Mimir / Pyroscope）的组合成为主流。

## 与 DevOps / SRE 的关系

```
可观测性 → 是 → SRE 的核心能力
         ↓
   故障定位（MTTR ↓）
         ↓
   容量规划（cost ↓）
         ↓
   性能优化（latency ↓）
         ↓
   SLA 兑现（user satisfaction ↑）
```

**SRE 三角**：
```
SLI（指标）= latency 99% < 200ms
SLO（目标）= 99% 的请求 latency < 200ms
Error Budget = 1% = 每月可"烧" 432 分钟
```

> 可观测性让 SLI 可测量，SLO 可验证，Error Budget 可消耗。**没有可观测性，SRE 就是空话**。

## 一句话总结

> **监控告诉你系统是不是坏了，可观测性告诉你为什么坏。**

2026 年的系统，没有可观测性 = 盲人摸象。补上可观测性 = 拥有 X 光机。

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>