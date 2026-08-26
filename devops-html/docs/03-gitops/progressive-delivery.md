---
title: 渐进式发布
---

# 渐进式发布

渐进式发布（Progressive Delivery）= 金丝雀 + 蓝绿 + A/B 测试的自动化实现。本章梳理主流工具 Flagger 与 Argo Rollouts。

## 一句话总结

> **渐进式发布 = 自动化的金丝雀/蓝绿/A/B**。**核心工具：Flagger（Flux 生态）+ Argo Rollouts（ArgoCD 生态）**。**价值：发布自动化 + 自动回滚 + 度量驱动决策**。

---

## Flagger（Flux 生态）

```yaml
# Canary 资源
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: my-app
  namespace: my-app
spec:
  provider: istio
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app

  metricTemplate:
    - name: request-success-rate
      provider: prometheus
      query: |
        sum(rate(istio_requests_total{destination_service=~"my-app.*",response_code!~"5.."}[2m]))
        /
        sum(rate(istio_requests_total{destination_service=~"my-app.*"}[2m]))

  analysis:
    interval: 30s
    threshold: 5       # 连续 5 次失败就回滚
    maxWeight: 50      # 最大 50% 流量
    stepWeight: 5      # 每步 5%
    steps:
      - setWeight: 5
      - pause: { duration: 2m }
      - setWeight: 25
      - pause: { duration: 2m }
      - setWeight: 50
```

## Argo Rollouts（ArgoCD 生态）

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 5
  strategy:
    canary:
      canaryService: my-app-canary
      stableService: my-app-stable
      trafficRouting:
        istio:
          virtualService:
            name: my-app-vsvc
      steps:
        - setWeight: 5
        - pause: { duration: 10m }
        - setWeight: 25
        - pause: { duration: 10m }
        - setWeight: 50
        - pause: { duration: 10m }

      analysis:
        templates:
          - templateName: success-rate
        args:
          - name: service-name
            value: my-app

---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: success-rate
spec:
  metrics:
    - name: success-rate
      interval: 30s
      successCondition: result >= 0.95
      failureLimit: 3
      provider:
        prometheus:
          query: |
            sum(rate(http_requests_total{service="my-app",code!~"5.."}[2m]))
            /
            sum(rate(http_requests_total{service="my-app"}[2m]))
```

## Flagger vs Argo Rollouts

| 维度 | Flagger | Argo Rollouts |
|------|---------|---------------|
| **生态** | Flux | ArgoCD |
| **Provider** | Istio / Linkerd / App Mesh / Nginx / Gloo / Contour | Istio / Nginx / ALB / SMI |
| **CRD** | Canary | Rollout / AnalysisTemplate |
| **配置复杂度** | 中（YAML 多） | 低（可视化插件强） |
| **实验功能** | A/B 测试 | A/B 测试 + 蓝绿 + 金丝雀 |
| **Kubectl 插件** | 无 | 有（argo-rollouts kubectl plugin） |
| **活跃度** | 中 | 高 |

## 度量驱动决策

```yaml
# 度量维度（决定发布是否继续）
- request-success-rate: 成功率 > 95%
- request-duration-p99: P99 延迟 < 500ms
- error-budget: 错误预算未耗尽
- custom-metrics: 业务指标（CTR / 转化率）

# 失败响应
- 自动 abort（停止发布）
- 自动回滚（切回 stable）
- 通知 oncall
```

## 关联章节

- **04-release/overview**：发布策略总览
- **04-release/canary**：金丝雀原理
- **03-gitops/argocd**：ArgoCD + Argo Rollouts 完整链路

## 一句话总结

> **渐进式发布 = 工具化的发布策略**。**何时用：关键服务 / 用户可感知的变更 / 算法更新**。**何时不用：内部工具 / 后台 job / 一次性脚本**。


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
