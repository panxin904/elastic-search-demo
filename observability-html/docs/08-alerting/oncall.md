---
title: On-call 文化与值班
date: 2026-08-15  # date-auto-injected
description: PagerDuty / OpsGenie / 值班轮转
---

# On-call 文化与值班

> **TL;DR**：On-call 不是"出了问题叫醒你"，而是 **24×7 服务的工程责任体系**。**核心：轮转表（rotation schedule）+ 升级链（escalation policy）+ 响应 SLO（5min/15min/30min）+ 事后复盘（postmortem）**。**Google SRE 实践：每人每月 on-call 时间不超过 25%**。

## 一句话定义

```
On-call = 7×24 服务保障机制
       = 轮转（rotation）+ 升级（escalation）+ 响应 SLO + 复盘（postmortem）
       = 不是惩罚机制，是高可用服务的工程责任
       = 工具：PagerDuty / OpsGenie / 飞书 / 钉钉
```

## On-call 核心要素

### 1. 轮转表（Rotation Schedule）

```yaml
# PagerDuty 轮转示例
schedule:
  name: backend-primary
  rotation_length: 1 week       # 一周一换
  users:
    - alice
    - bob
    - carol
    - dave
  handoff_time: "Monday 10:00"  # 周一上午 10 点交接
  time_zone: Asia/Shanghai

# 推荐：3-4 人轮转，避免单人 burnout
# Google SRE 实践：每周最多 6 小时 call（团队规模 6-8 人）
```

### 2. 升级链（Escalation Policy）

```yaml
# PagerDuty 升级策略
escalation_policy:
  name: backend-prod
  levels:
    - level: 1
      delay: 5                   # 5 分钟没响应
      targets: [backend-primary] # 找当前值班人
    - level: 2
      delay: 5                   # 再 5 分钟没响应
      targets: [backend-secondary] # 升级到二级值班
    - level: 3
      delay: 5
      targets: [engineering-manager] # 升级到经理
    - level: 4
      delay: 10
      targets: [vp-engineering]  # 最后 VP

# 关键：每级 delay 都要有，不能跳过
# 实战：很多团队 Level 2 没配，导致关键人永远被打
```

### 3. 响应 SLO

```
P0（critical）：5 分钟内响应，30 分钟内止血
P1（high）：   15 分钟内响应，4 小时内解决
P2（medium）： 4 小时内响应，下个工作日解决
P3（low）：    下个工作日响应

响应 SLO 必须公开 + 度量
月度统计 on-call 触达率 / 解决时长
```

## 主流 On-call 工具对比

| 工具 | 特点 | 适用 |
|---|---|---|
| **PagerDuty** | 业界标准 / 集成最丰富 | 中大型团队 |
| **OpsGenie** | Atlassian 旗下 / 价格便宜 | 中型团队 |
| **飞书告警** | 国内合规 / 集成 IM | 国内企业 |
| **钉钉告警** | 阿里云生态 | 阿里云客户 |
| **自研** | 完全可控 / 维护成本高 | 大型平台 |

## 实战案例：电商 on-call 配置

```yaml
# PagerDuty Services + Escalation

service: order-service-prod
escalation_policy: order-service-policy
  levels:
    - 5min: backend-oncall-primary
    - 10min: backend-oncall-secondary + frontend-oncall
    - 15min: tech-lead
    - 20min: vp-engineering

service: payment-service-prod
escalation_policy: payment-policy
  levels:
    - 0min:  payments-oncall-primary     # 资金问题立即升级
    - 5min:  payments-oncall-secondary
    - 10min: cto                           # 资金问题直接 CTO

service: data-pipeline-prod
escalation_policy: data-policy
  levels:
    - 30min: data-eng-primary              # 数据问题不紧急
    - 2h:    data-eng-secondary
    - 8h:    data-eng-manager
```

## 值班人健康保障

```
Google SRE 关键指标：
  - 单人 on-call 不超过团队 25% 时间
  - 每周 on-call 实际工作量 ≤ 6 小时（含处理告警）
  - call 后必须补休半天或一天
  - 触发率超过月均 5 次/人 → 重新审视告警分级

防护机制：
  1. 告警分级：P0/P1 < 月均 5 次/人
  2. 告警疲劳预警：单周 > 10 次告警 → 强制升级问题
  3. Sleep budget：on-call 夜间被打 → 下班早走 2 小时
  4. 轮转公平：每月 on-call 时长统计 + 公开
```

## Postmortem（事后复盘）

```markdown
# Postmortem: [故障标题]
## 元信息
- Date: 2026-08-09 14:23 ~ 14:51
- Duration: 28 minutes
- Severity: P1
- Author: @alice
- Reviewer: @tech-lead

## 摘要（用户视角）
订单 API 在 28 分钟内返回 50% 错误率，影响约 12% 用户下单失败

## 时间线
- 14:23 - 监控系统检测到错误率 spike
- 14:25 - on-call @alice 收到 PagerDuty 告警
- 14:30 - alice 在 #incident channel 拉 incident commander
- 14:35 - 定位到 payment-gateway 连接池耗尽
- 14:42 - 重启 payment-gateway 服务
- 14:51 - 错误率恢复 0.1%，宣告恢复

## 根因（Root Cause）
payment-gateway v2.3 升级引入 bug：连接泄漏
新版本未做连接释放 → 池子 30 分钟内打满

## 影响（Impact）
- 12% 用户（~8400 人）下单失败
- 损失 GMV 约 ¥180,000
- 已自动给受影响用户发放 ¥20 补偿券

## 修复（Resolution）
1. 短期：回滚到 v2.2
2. 长期：增加连接池监控指标 + 单元测试覆盖连接释放路径

## 教训（Lessons Learned）
1. 升级时缺少连接池压力测试
2. 告警阈值设得偏高（连接池使用率 90% 才告警）
3. Runbook 没有"连接池耗尽"场景的处理步骤

## 行动项（Action Items）
- [ ] 增加连接池压测（owner: @bob, due: 2026-08-16）
- [ ] 调整告警阈值为 70%（owner: @alice, due: 2026-08-12）
- [ ] 完善 Runbook（owner: @carol, due: 2026-08-20）
```

## Blameless Culture（不追责文化）

```
Postmortem 核心原则：
  1. 不追责个人 → 追责流程和系统
  2. 假设人会犯错 → 系统应该有兜底
  3. 公开所有事故 → 团队学习机会
  4. 行动项必须 owner + due → 闭环

反例：
  "是 alice 没仔细测试导致的" → ✗ 追责个人
正例：
  "我们的部署流程没有要求压力测试" → ✓ 改流程
```

## 一句话总结

> **On-call = 轮转 + 升级 + SLO + 复盘**。**工具：PagerDuty / OpsGenie**。**核心：告警分级（≤5 次/人/月）+ 健康保障（≤6h/周）+ 不追责文化**。**Postmortem 必写 + 行动项必闭环**。

---

## 关联章节

- [Alertmanager](../08-alerting/alertmanager.md) — 告警如何路由到 on-call
- [告警分级](../08-alerting/severity.md) — P0/P1/P2/P3 标准
- [SLI/SLO](../01-foundations/sli-slo.md) — SLO 决定 on-call 频率
- [告警疲劳治理](../08-alerting/silence.md) — silence 与降噪

---

🏠 <a href="https://java-px.bot.cd/" target="_blank">返回门户首页</a>