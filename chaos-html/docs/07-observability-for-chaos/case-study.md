---
title: 实战案例
---

# 实战案例

## Netflix Chaos + Vizceral

**Vizceral**：Netflix 开源实时流量拓扑图

- 显示服务间流量（线宽代表 QPS）
- Chaos Monkey 注入故障 → Vizceral 实时显示流量转移
- SRE 一眼看出「哪些服务受影响」

**关键洞察**：

- 故障注入是「视觉化」的
- 团队可以「看到」故障传播
- 沟通效率提升（不用看 dashboard）

## Uber Chaos Mesh + M3 + Grafana

**M3**：Uber 自研时序数据库（基于 Cassandra）

- 高吞吐（每秒百万级指标）
- 长时间存储（保留 1 年+）
- 多集群联邦

**集成流程**：

```
Chaos Mesh → 注入故障 → M3 记录指标 → Grafana 显示
```

**自研 Chaos Dashboard**：

- 实验成功率（过去 30 天）
- SLO 影响（实验期间偏离）
- 故障类型分布（柱状图）
- Top 失败实验（列表）

## 阿里 AHAS + ARMS

**AHAS**：阿里云流量防护 + 故障注入

- Sentinel（限流 / 降级 / 熔断）
- 故障注入（CPU / 网络 / 进程）
- 一键启用（无需 K8s）

**ARMS（应用实时监控服务）**：

- APM（应用性能监控）
- 业务监控（订单 / 支付 / 用户）
- 告警 + dashboard

**集成**：混沌实验 → ARMS 自动采集 → 实时展示业务影响

## 字节跳动 Chaos Mesh + 自研 metric

**自研 metric 平台**：

- 基于 Prometheus 扩展（千万级 metric）
- 「实验 vs 基线」对比 dashboard
- 自动判定「稳态偏离度」

**关键工具**：

- Chaos Mesh 注入故障
- 自研 metric 平台记录
- 自研 dashboard 可视化
- PagerDuty 告警联动

## Shopify Black Friday 演练

**2023 Black Friday 演练**：

- 演练前 6 个月：500+ 实验 + 100+ SLO
- 「Chaos Dashboard」显示实验成功率
- 大促日：实时对比「稳态 vs 实测」

**关键工具集成**：

```
Chaos Mesh ──┐
             ├──→ Prometheus ──→ Grafana (稳态 dashboard)
             ├──→ OpenTelemetry ──→ Jaeger (trace 链路)
             └──→ AlertManager ──→ PagerDuty / Slack
```

**实战成果**：

- Black Friday 期间零 P0 故障
- 演练发现的 50+ 问题全部修复
- oncall 应急能力提升 200%

## 与其他站点关系

- **observability**：监控集成
- **chaos/02-chaos-mesh**：Chaos Mesh 案例
- **chaos/06-game-day**：实战游戏日


## ## 实战案例

**Netflix Chaos Monkey + Atlas 集成**：Netflix 内部 Atlas 系统实时采集 50+ SLI，每个服务的 SLO 看板直接展示在 Chaos 控制台，工程师点一个按钮就能观察 kill 后的 SLO 偏离曲线。

**字节跳动 Chaos vs SRE 平台**：通过统一的 A/B 实验组 ID，Chaos 平台知道每个实验影响了多少 error budget，自动生成多维度报告。

**阿里 Ahas + ARMS**：阿里云把 chaos 工程和 SLO 监控结合，对外输出「韧性评分」— 综合服务等级、错误预算、可恢复性给出 0-100 分。


## ## 进阶话题

- **可观测性驱动开发（ODD）**：先写 SLI，再写代码
- **SLO 即代码（SLO as Code）**：用 Sloth/Pyrra 等工具版本化 SLO
- **可观测性 + 韧性双向反馈**：混沌实验反过来校准 SLO 阈值
