---
title: 流水线可观测性 总览
date: 2026-08-15  # date-auto-injected
---

# 流水线可观测性 总览

CI/CD 流水线本身的"运行状态 / 性能 / 失败率"决定研发效能。本章梳理 4 大度量体系：DORA / Flow / Flaky Test / Pipeline 监控。

## 4 大度量体系

```
1. DORA Metrics（Google DevOps Research & Assessment）
   - 部署频率 (Deployment Frequency)
   - 变更前置时间 (Lead Time for Changes)
   - 变更失败率 (Change Failure Rate)
   - 恢复时间 (Mean Time to Recover / MTTR)
   用途：团队 / 组织级效能对比，对标行业精英/普通/低绩效

2. Flow Metrics（Actionable Agile / Accelerate）
   - Flow Velocity（流速）
   - Flow Time（流时间）
   - Flow Load / WIP（在制品）
   - Flow Distribution（流分布：特性 / 缺陷 / 风险 / 债务）
   用途：项目级瓶颈识别

3. SPACE Framework（ACM / Microsoft Research）
   - Satisfaction & well-being
   - Performance
   - Activity
   - Communication & collaboration
   - Efficiency & flow
   用途：开发者个人效能，避免单维度度量的副作用

4. Pipeline Operational Metrics
   - Pipeline duration（P50 / P90 / P99）
   - Pipeline success rate（按分支 / 按服务）
   - Cache hit rate
   - Flaky test rate
   - Queue time（等待 runner 时间）
   用途：流水线本身的健康度
```

## 4 个核心指标的工程意义

```yaml
# DORA 4 个指标如何驱动改进行动
deployment_frequency:
  low  → 团队交付慢 → 优化 CI 缓存、拆分大 Pipeline
  high → 团队成熟，能小步快跑
  
lead_time_for_changes:
  long → 需求到上线慢 → 拆分需求、缩短 code review、自动化测试
  short → 需求响应快
  
change_failure_rate:
  high → 质量差 → 加强测试覆盖、引入金丝雀、Feature Flag
  low  → 质量稳定
  
mttr:
  long → 故障恢复慢 → 完善回滚机制、增强可观测性
  short → 故障自愈能力强
```

## 数据采集方案

| 数据源 | 采集方式 | 关键指标 |
|--------|----------|----------|
| **GitHub Actions** | gh API + Actions Insights API | workflow run duration / conclusion |
| **GitLab CI** | GitLab API + Prometheus exporter | pipeline duration / status |
| **Jenkins** | Jenkins Metrics Plugin + Prometheus | job duration / queue time |
| **ArgoCD** | ArgoCD Metrics (Prometheus) | sync status / drift count / app health |
| **PagerDuty / Opsgenie** | Webhook → DataDog / 自建 | incident count / MTTR |
| **Git** | Git log 解析 | commit-to-deploy 时间差 |

## 看板设计原则

```yaml
# 推荐分层看板
level_1_executive_dashboard:
  - dora_metrics_4_scorecards
  - team_comparison_radar
  
level_2_team_dashboard:
  - pipeline_duration_p50_p90
  - flaky_test_top_10
  - deploy_frequency_trend
  
level_3_engineer_dashboard:
  - my_pr_cycle_time
  - my_pipelines_failed_reasons
  - my_flaky_tests
```

## 常见误区

1. **过度追求 DORA 数字**：把"部署频率"当 KPI 会导致"凑数部署"（拆分 commit、频繁无意义发布）
2. **忽略开发者体验**：SPACE 中 Satisfaction 最重要，单纯度量 Velocity 会导致 burnout
3. **数字成摆设**：DORA 数字必须驱动行动（找到瓶颈 → 改进 → 度量效果），否则只是装饰品
4. **跨团队直接对比**：不同业务复杂度差异大，对比前需要标准化（按业务规模 / 团队规模归一化）

## 关联章节

- **03-gitops** → ArgoCD 指标作为可观测性数据源
- **05-cicd-observability/dora-metrics** → 4 个指标的深度细节
- **05-cicd-observability/flaky-test** → Flaky Test 的根因分析
- **observability/** → 流水线产品（SLO / 告警 / 看板）的可观测性


<!-- auto-enrich:do-not-edit -->

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
