---
title: 流水线监控
date: 2026-08-15  # date-auto-injected
---

# 流水线监控

CI/CD Pipeline 本身的运行状态监控：duration / success rate / queue time / cache hit rate。

## 一句话总结

> **Pipeline 监控 = Pipeline 自身的 SRE**。**核心指标：duration / success rate / queue time / cache hit rate**。**价值：发现瓶颈 + SLA 保障 + 成本优化**。

---

## 4 大核心指标

```yaml
# 1. Pipeline Duration
# 关键路径耗时（PR 到反馈）
p50: 5 分钟
p90: 15 分钟
p99: 30 分钟
目标：p90 < 10 分钟

# 2. Success Rate（按分支 / 服务）
main: > 95%
feature: > 80%（允许新代码有问题）
目标：main > 95%

# 3. Queue Time（等待 runner 时间）
p90: < 1 分钟
目标：< 30 秒
瓶颈信号：runner 不足

# 4. Cache Hit Rate
dep cache: > 90%
docker cache: > 80%
目标：> 85%
```

## Prometheus 采集

```yaml
# GitHub Actions Exporter
# https://github.com/cpanato/github_actions_exporter
scrape_configs:
  - job_name: github-actions
    static_configs:
      - targets: ['github-actions-exporter:9101']
```

```promql
# Pipeline duration p90
histogram_quantile(0.9,
  rate(github_actions_workflow_duration_seconds_bucket{workflow="CI"}[5m])
)

# Success rate
sum(rate(github_actions_workflow_completed_total{conclusion="success"}[1h]))
/
sum(rate(github_actions_workflow_completed_total[1h]))
```

## ArgoCD 指标

```promql
# 同步状态
argocd_app_sync_status{namespace="argocd"}

# 漂移检测（Git vs 实际）
argocd_app_sync_status{sync_status="OutOfSync"}

# 健康状态
argocd_app_health_status{health_status="Healthy"}
```

## Jenkins 指标

```yaml
# Prometheus Plugin（自动暴露）
# /prometheus/ 端点

# 关键指标
- jenkins_job_duration_seconds
- jenkins_job_result_total
- jenkins_queue_size
- jenkins_node_executors_available
```

## GitLab CI 指标

```yaml
# GitLab Prometheus exporter
# https://docs.gitlab.com/ee/administration/monitoring/prometheus/

# 关键指标
- gitlab_ci_pipeline_duration_seconds
- gitlab_ci_pipeline_status
- gitlab_ci_runner_jobs
```

## 告警规则

```yaml
# alertmanager rules
groups:
  - name: pipeline
    rules:
      - alert: PipelineSlow
        expr: |
            histogram_quantile(0.9,
              rate(github_actions_workflow_duration_seconds_bucket[5m])
            ) > 600
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Pipeline duration p90 > 10 minutes"

      - alert: PipelineFailureSpike
        expr: |
            sum(rate(github_actions_workflow_completed_total{conclusion="failure"}[1h]))
            /
            sum(rate(github_actions_workflow_completed_total[1h]))
            > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pipeline failure rate > 10%"

      - alert: RunnerQueueLong
        expr: github_actions_runner_queue_duration_seconds > 60
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Runner queue > 60 seconds"
```

## 优化行动

```yaml
duration_high:
  行动：
    - 启用 cache（依赖 + Docker layer）
    - 并行 job
    - 拆分大 Pipeline
    - 升级 runner（更快 CPU / IO）

success_rate_low:
  行动：
    - 治理 Flaky Test
    - 增加 retry
    - 修复根本性 bug（可能是依赖问题）

queue_time_long:
  行动：
    - 增加 runner 数量
    - 优化 job 调度（大 job 拆小）
    - 自建 runner

cache_hit_low:
  行动：
    - 检查 cache key 是否过细
    - 检查 cache 失效原因
    - 增大 cache 容量
```

## 关联章节

- **05-cicd-observability/overview**：可观测性总览
- **05-cicd-observability/dora-metrics**：DORA 度量
- **05-cicd-observability/flaky-test**：失败率根因
- **observability/**：通用可观测性体系

## 一句话总结

> **Pipeline 监控 = Pipeline SRE**。**目标：duration p90 < 10min / success > 95% / queue < 30s / cache > 85%**。**工具：各平台 Exporter + Prometheus + 告警**。


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
