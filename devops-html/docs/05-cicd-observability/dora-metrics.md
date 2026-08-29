---
title: DORA Metrics
date: 2026-08-15  # date-auto-injected
---

# DORA Metrics

DORA（DevOps Research & Assessment）是 Google 与 DORA 团队发布的研发效能度量框架，4 个核心指标被业界广泛采用。

## 一句话总结

> **DORA = 研发效能的事实标准**。**4 大指标：部署频率 / 变更前置时间 / 变更失败率 / 恢复时间**。**价值：跨团队对比 + 识别瓶颈 + 行业 benchmark**。

---

## 4 大核心指标

```yaml
# 1. Deployment Frequency（部署频率）
# 含义：单位时间内部署到生产的次数
# 行业 benchmark（Accelerate 2023）：
#   - 精英：on-demand（每天多次）
#   - 高：每周到每天
#   - 中：每月到每周
#   - 低：每月以下

# 2. Lead Time for Changes（变更前置时间）
# 含义：commit 到 production 的时间
# 行业 benchmark：
#   - 精英：< 1 小时
#   - 高：1 天 - 1 周
#   - 中：1 周 - 1 月
#   - 低：> 1 月

# 3. Change Failure Rate（变更失败率）
# 含义：导致生产故障的变更比例
# 行业 benchmark：
#   - 精英：0-15%
#   - 高：16-30%
#   - 中：31-45%
#   - 低：46-60%

# 4. Mean Time to Recover / MTTR（恢复时间）
# 含义：从故障到恢复的时间
# 行业 benchmark：
#   - 精英：< 1 小时
#   - 高：< 1 天
#   - 中：< 1 周
#   - 低：> 1 周
```

## 数据采集

```python
# DORA metrics 计算示例（伪代码）
import pandas as pd

# 数据源
deploys = get_deployments()        # 来自 CI/CD 系统
incidents = get_incidents()         # 来自 PagerDuty
commits = get_commits()             # 来自 Git

# 1. Deployment Frequency
deploy_freq = deploys.groupby(deploys.timestamp.dt.date).size()
# 输出：每天 5 次

# 2. Lead Time for Changes
# commit → production 时间差
merged = commits.merge(deploys, on='commit_sha')
lead_time = (merged.deploy_time - merged.commit_time).dt.total_seconds() / 3600
# 输出：中位数 4 小时

# 3. Change Failure Rate
# 假设 100 次部署中 5 次导致 P0/P1 故障
failure_rate = len(incidents) / len(deploys)
# 输出：5%

# 4. MTTR
# 从 incident 开始到恢复
mttr = (incidents.resolved_time - incidents.started_time).dt.total_seconds() / 3600
# 输出：中位数 30 分钟
```

## 工具实现

```yaml
# 1. Four Keys（Google 开源项目）
# GitHub: GoogleCloudPlatform/fourkeys
# 自动采集 4 个指标 + Grafana 看板

# 2. LinearB / Jellyfish
# 商业 SaaS，自带 benchmark

# 3. 自建（Prometheus + Grafana）
# 用 GitHub Actions API + ArgoCD API 采集
```

## 行动映射

```yaml
deployment_frequency_low:
  根因：CI 慢 / 部署复杂 / 团队规模过大
  行动：
    - CI 缓存 + 并行（参考 01-pipeline/best-practices）
    - 拆分大 Pipeline
    - 引入 GitOps 降低部署摩擦
    - 团队拓扑调整（康威定律）

lead_time_long:
  根因：code review 慢 / 测试慢 / PR 过大
  行动：
    - PR 模板 + 拆分
    - 自动化测试覆盖率
    - Code review SLA（24 小时内 first review）
    - Trunk-based development

change_failure_rate_high:
  根因：测试不足 / 灰度不够 / 监控缺位
  行动：
    - 测试金字塔（unit / integration / e2e）
    - 金丝雀发布（04-release/canary）
    - Feature Flag（04-release/feature-flag）
    - SLO 驱动（observability/）

mttr_long:
  根因：回滚复杂 / 监控盲区 / oncall 不熟
  行动：
    - 蓝绿部署（秒级回滚）
    - 完善告警链路
    - RunBook 文档化
    - GameDay 演练
```

## 关联章节

- **05-cicd-observability/overview**：流水线可观测性总览
- **05-cicd-observability/flaky-test**：失败率根因之一
- **05-cicd-observability/pipeline-monitoring**：Pipeline 性能
- **observability/**：SLO 体系

## 一句话总结

> **DORA = 度量研发效能的金标准**。**何时用：团队 / 组织级效能诊断 + 行业 benchmark**。**何时不用：开发者个人绩效（避免副作用）**。


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
