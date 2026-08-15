---
title: 混沌工程的可观测性
---

# 混沌工程的可观测性

## 核心思想

混沌工程的「**稳态假设**」和「**实验验证**」都依赖可观测性。没有可观测性，混沌实验就是「**盲目破坏**」。

**可观测性三支柱**：

- **Metrics（指标）**：聚合数值（CPU / 错误率 / QPS），用于稳态判读
- **Logs（日志）**：离散事件（异常堆栈），用于根因定位
- **Traces（追踪）**：请求链路（跨服务），用于性能瓶颈

**混沌实验的三层观测**：

```
              ┌─ 业务指标 ──────────────── 业务稳态
混沌实验 ─────┤  系统指标 ──────────────── 系统稳态
              └─ 资源指标 ──────────────── 资源稳态
```

**与 observability 站的关系**：

- observability/03-prometheus：稳态指标采集
- observability/06-tracing：故障链路分析
- observability/08-alerting：实验失败告警
- observability/11-scenarios：混沌场景的指标设计

**核心问题**：

1. **稳态如何度量？** → 业务指标 + 系统指标 + 滑动窗口
2. **故障影响多大？** → 错误率 + P99 延迟 + 影响时长
3. **如何判定实验成败？** → Probe + SLO 对比 + 时间窗口
4. **如何自动终止？** → SLO breach 阈值 + 自动 chaos kill
5. **如何复盘？** → 时间线 + dashboard 截图 + trace 归档

## 稳态假设度量

**稳态度量设计五要素**：

**1. 业务指标（KBI, Key Business Indicators）**：

- 电商：订单成功率 / 支付成功率 / 加购转化率
- 视频：缓冲率 / 卡顿率 / 首帧时间
- 金融：交易成功率 / 清算时效

**2. 系统指标（SLI, Service Level Indicators）**：

- 可用性：成功率 = 成功请求 / 总请求
- 延迟：P50 / P95 / P99
- 吞吐：QPS / TPS
- 错误：错误率 / 5xx 比例

**3. 资源指标**：

- CPU / 内存 / 磁盘 / 网络
- K8s：Pod 重启 / OOM / 节点状态

**4. 滑动窗口（Sliding Window）**：

- 不是「瞬时值」，而是「窗口期聚合」
- 常见窗口：1 分钟 / 5 分钟 / 15 分钟
- Prometheus：`rate(metric[5m])` 或 `avg_over_time(metric[5m])`

**5. 稳态区间**：

- 不是「单点值」，而是「区间 + 时间窗口 + 偏离容忍度」
- 示例：订单成功率稳态 = [99.5%, 99.9%]，持续 5 分钟

**Prometheus 查询示例**：

```promql
# 订单成功率（5 分钟窗口）
sum(rate(order_success_total[5m]))
/ sum(rate(order_total[5m]))

# P99 延迟
histogram_quantile(0.99,
  sum(rate(http_request_duration_seconds_bucket{app="order-service"}[5m])) by (le))

# 错误率（5xx）
sum(rate(http_requests_total{status=~"5..",app="order-service"}[5m]))
/ sum(rate(http_requests_total{app="order-service"}[5m]))

# Pod 重启次数（异常信号）
increase(kube_pod_container_status_restarts_total[5m])
```

**稳态对比 Dashboard**：

```
┌─────────────────────────────┐
│  实验前稳态 (过去 7 天)        │
│  - 订单成功率: 99.72% ± 0.05% │
│  - P99 延迟: 800ms ± 50ms    │
│  - 错误率: 0.05% ± 0.01%     │
└─────────────────────────────┘

┌─────────────────────────────┐
│  实验中（实时）                │
│  - 订单成功率: 99.45% ↓       │
│  - P99 延迟: 1200ms ↑         │
│  - 错误率: 0.42% ↑            │
│  判定: 偏离稳态（但仍可接受）   │
└─────────────────────────────┘

┌─────────────────────────────┐
│  实验后（恢复期）              │
│  - 订单成功率: 99.71% (恢复)   │
│  - P99 延迟: 850ms (恢复)     │
│  - 错误率: 0.06% (恢复)       │
│  恢复时间: 35 秒              │
└─────────────────────────────┘
```

**稳态异常检测算法**：

1. **阈值法**：metric > threshold 报警
2. **同比/环比**：与过去 N 天同时段对比（季节性）
3. **3-sigma 法**：超出均值 ± 3σ 视为异常
4. **机器学习**：Prophet / LSTM 等时间序列异常检测
5. **CUSUM**：累积和算法（检测微小持续偏移）

## SLO 反馈环

**SLO（Service Level Objective）** 是「**稳态假设的工程化表达**」。

**SLO 三要素**：

- **SLI**（指标）：订单成功率 / 延迟
- **SLO**（目标）：99.5% / P99 < 1s
- **Error Budget**（错误预算）：1 - SLO = 0.5%（可「消耗」的错误）

**混沌实验 + SLO 的反馈环**：

```
       ┌────────────────────────────────┐
       │  SLO 定义（业务承诺）             │
       │  订单成功率 ≥ 99.5%              │
       │  P99 延迟 ≤ 1.5s                 │
       └────────────────┬───────────────┘
                        ▼
       ┌────────────────────────────────┐
       │  稳态采集（实时）                 │
       │  当前成功率 = 99.7%               │
       └────────────────┬───────────────┘
                        ▼
       ┌────────────────────────────────┐
       │  混沌实验（注入故障）             │
       │  pod-kill 1 个 / 30s             │
       └────────────────┬───────────────┘
                        ▼
       ┌────────────────────────────────┐
       │  SLO 对比（实验后）              │
       │  当前成功率 = 99.45%              │
       │  偏离 = 0.25%（可接受）           │
       │  判定: 实验成功                  │
       └────────────────┬───────────────┘
                        ▼
       ┌────────────────────────────────┐
       │  持续验证（每周 cron）            │
       │  累计实验 = 52 次                  │
       │  SLO breach = 1 次（2%）          │
       │  → 触发改进流程                   │
       └────────────────────────────────┘
```

**Error Budget 与混沌实验**：

- 每月 Error Budget = 0.5% × 30 天 = 0.5% × 月请求量
- 混沌实验消耗 Error Budget？**是的**
- 「**混沌日**」：消耗 0.1% 预算做实验
- 「**大促窗口**」：冻结实验（保护预算）

**Google SRE Book 的 Error Budget 政策**：

- 100% SLO 太严格 → 不允许任何故障 → 无韧性验证
- 99% SLO 太宽松 → 无 Error Budget 概念 → 无实验文化
- 推荐：**99.9%（3 个 9）— 99.99%（4 个 9）**

**SLO 工具**：

- **Prometheus + sloth**：SLO 定义 + Error Budget 计算
- **OpenSLO**：SLO 标准（跨平台）
- **Nobl9**：SLO 平台（SaaS）
- **Sloth**：SLO 自动生成 Prometheus rules

**Sloth SLO 定义示例**：

```yaml
service: order-service
slos:
  - name: availability
    objective: 99.5
    description: "订单成功率 SLO"
    sli:
      events:
        error_query: sum(rate(http_requests_total{status=~"5..",app="order-service"}[5m]))
        total_query: sum(rate(http_requests_total{app="order-service"}[5m]))
    alerting:
      page_alert:
        burnrate: 14.4
        for: 2m
      ticket_alert:
        burnrate: 1
        for: 1h
```

**Burn Rate（燃烧速率）**：

- 1× burn rate：30 天耗尽预算
- 14.4× burn rate：2 天耗尽预算（page alert）
- Google 推荐的多窗口 burn rate 报警：
  - 5 分钟窗口 × 14.4 倍率（短期爆发）
  - 30 分钟窗口 × 6 倍率（中期）
  - 1 小时窗口 × 3 倍率（缓慢泄漏）
  - 6 小时窗口 × 1 倍率（长期）

## 实战案例

**案例 1：Netflix Chaos + Vizceral（实时流量可视化）**

- Vizceral：Netflix 开源流量拓扑图
- Chaos Monkey 注入故障 → Vizceral 实时显示流量转移
- SRE 一眼看出「哪些服务受影响」

**案例 2：Uber Chaos Mesh + M3 + Grafana**

- M3：Uber 自研时序数据库
- Chaos Mesh 注入 → M3 记录指标 → Grafana 显示
- 自研「Chaos Dashboard」：实验成功率 + SLO 影响

**案例 3：阿里 AHAS + ARMS（应用实时监控服务）**

- AHAS：流量防护 + 故障注入
- ARMS：APM + 业务监控
- 集成：混沌实验 → ARMS 自动采集 → 实时展示业务影响

**案例 4：字节跳动 Chaos Mesh + 自研 metric 平台**

- 自研 metric 平台（基于 Prometheus 扩展）
- 「实验 vs 基线」对比 dashboard
- 自动判定「稳态偏离度」

**案例 5：Shopify Black Friday 演练（2023）**

- 演练前 6 个月：500+ 实验 + 100+ SLO
- 「Chaos Dashboard」显示实验成功率
- 大促日：实时对比「稳态 vs 实测」

**关键工具集成模式**：

```
Chaos Mesh ──┐
             │
             ├──→ Prometheus ──→ Grafana (稳态 dashboard)
             │
             ├──→ OpenTelemetry ──→ Jaeger / Tempo (trace 链路)
             │
             └──→ AlertManager ──→ PagerDuty / Slack
```

**OpenTelemetry 集成**：

- 自动注入 trace 上下文到 chaos 实验
- 「故障发生时的 trace」直接对比「稳态 trace」
- 快速定位「哪个 span 耗时增加」

**真实案例（故障排查）**：

- 现象：订单服务 P99 延迟突增 500ms
- 稳态对比：实验前 800ms → 实验中 1300ms
- Trace 分析：
  - 网关 → 订单服务：延迟增加 200ms（重试）
  - 订单服务 → Redis：延迟增加 150ms（连接池）
  - 订单服务 → MySQL：延迟增加 150ms（慢查询）
- 结论：Pod kill 导致连接池重建 + 缓存击穿
- 改进：连接池预热 + 缓存预加载

## 自动化与告警

**混沌实验告警三阶段**：

**1. 实验启动告警**：

- Slack #chaos-game-day：「实验 redis-failover-001 已启动，预计 30s」
- PagerDuty：低优先级（仅 oncall 可见）

**2. 实验进行中告警**：

- SLO 偏离 → Prometheus AlertManager
- 异常增长 → 自动 trace 截图

**3. 实验结束告警**：

- 成功：Slack 通知「实验成功，稳态偏离 < 阈值」
- 失败：PagerDuty high + 写入 Jira incident

**自动终止条件**：

```yaml
# chaos-experiment.yaml
spec:
  duration: "30s"
  auto_termination:
    - condition: "order_success_rate < 95"
      action: "kill_chaos"
      notification: "pagerduty:high"
    - condition: "p99_latency > 3000"
      action: "kill_chaos"
      notification: "slack:#chaos-game-day"
```

**Prometheus AlertManager 规则**：

```yaml
groups:
- name: chaos-experiment
  rules:
  - alert: ChaosExperimentFailing
    expr: |
      sum(rate(order_success_total[1m]))
      / sum(rate(order_total[1m])) < 0.95
      and on(namespace) kube_chaos_active{name="redis-failover-001"} == 1
    for: 30s
    labels:
      severity: critical
    annotations:
      summary: "混沌实验 {{ $labels.name }} 触发 SLO breach"
      description: "订单成功率降至 {{ $value }}，自动终止混沌"
```

**自动化运行（Grafana 集成）**：

```yaml
# chaos-cron.yaml
apiVersion: chaos-mesh.org/v1alpha1
kind: Schedule
metadata:
  name: weekly-resilience-test
spec:
  schedule: "0 14 * * 1"  # 每周一 14:00
  type: Schedule
  historyLimit: 10
  concurrencyPolicy: Forbid
  workflow: e2e-resilience-validation
```

**实验结果归档**：

- Chaos Mesh 自动生成：实验 ID / 故障类型 / 时长 / 影响 / SLO 偏离
- 写入 Loki（日志）+ Prometheus（指标）+ S3（截图）
- 90 天后自动归档到冷存储

**实验成功标准（自动判定）**：

```python
def judge_experiment(result):
    # 稳态偏离 < 阈值
    steady_state_deviation = abs(result.observed - result.baseline)
    if steady_state_deviation > THRESHOLD:
        return "FAIL"
    # 恢复时间 < 预期
    if result.recovery_time > EXPECTED_RTO:
        return "FAIL"
    # 无雪崩
    if result.max_error_rate > MAX_ERROR_RATE:
        return "FAIL"
    return "PASS"
```

**与 SLO 平台集成（sloth + PromQL）**：

- Sloth 自动生成 SLO Prometheus rules
- AlertManager 路由混沌相关告警到专用频道
- 与 incident.io / FireHydrant 集成：自动开 incident

**长期观测（Chaos Maturity）**：

- 月度实验数 / 失败率 / SLO breach 关联
- 「韧性指数」（Resilience Index）：综合分数
- 团队排名 + 改进跟踪

**关键 Dashboard（推荐）**：

```
┌─ 实时实验（活跃 chaos）
│  - redis-failover-001 运行中（30s/60s）
│  - 当前偏离: 0.3%（阈值 0.5%）
│
├─ 稳态对比（实验 vs 基线）
│  - 订单成功率: 99.45% vs 99.72%
│  - P99: 1200ms vs 800ms
│
├─ 历史实验
│  - 本周: 12 次 / 10 成功 / 2 失败
│  - 月度: 52 次 / 90% 成功率
│
└─ Error Budget
   - 本月剩余: 65%
   - 实验消耗: 5%
   - 真实故障消耗: 30%
```

## 与其他站点的关系

- **observability**：稳态指标 / trace / log → 引用 observability/03-prometheus + observability/06-tracing
- **devops**：告警联动 → 引用 devops/05-cicd-observability
- **system-design**：SLO 设计 → 引用 system-design/08-availability
- **design-pattern**：熔断器指标 → 引用 design-pattern/05-architectural-patterns
- **architecture**：服务网格可观测性 → 引用 architecture/05-microservices

**学习路径**：

- 入门：observability/01-foundations → chaos/01-foundations
- 工具：observability/03-prometheus → chaos/02-chaos-mesh
- 实战：observability/06-tracing → chaos/07-observability-for-chaos
- 进阶：observability/11-scenarios → chaos/06-game-day