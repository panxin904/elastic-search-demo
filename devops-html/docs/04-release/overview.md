---
title: 发布策略总览
---

# 发布策略总览

发布策略决定"新版本如何从 0% 流量到 100% 流量"。选错策略会导致服务中断、用户体验下降、回滚困难。本章梳理 5 种主流策略的原理与适用场景。

## 5 大发布策略对比

| 策略 | 风险 | 回滚速度 | 资源成本 | 适用场景 |
|------|------|----------|----------|----------|
| **蓝绿 (Blue-Green)** | 低 | 秒级 | 2x 资源 | 大版本 / 数据库 schema 变更 |
| **金丝雀 (Canary)** | 中 | 分钟级 | 1.1-1.5x | 算法更新 / 性能优化 / A/B 实验 |
| **灰度 (Gray)** | 中 | 分钟级 | 1.1-1.5x | 用户分群 / 内部测试 |
| **Feature Flag** | 极低 | 秒级 | 1x | 新功能试用 / 多变体 |
| **影子流量 (Shadow)** | 极低 | N/A | 1.2-1.5x | 性能压测 / 模型对比 |

## 蓝绿部署 (Blue-Green)

```yaml
# K8s Service 切流量
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  selector:
    app: my-app
    version: blue   # 切到 green 就是改这一行
  ports:
    - port: 80
      targetPort: 8080
```

**原理**：同时部署 blue（旧）+ green（新）两套环境，Router / Service Mesh 切流量；回滚 = 切回 blue。

**优势**：秒级回滚（DNS / LB 切换）；两套环境完全隔离。
**劣势**：资源 2 倍；数据库 schema 变更需要兼容（双写 / 灰度迁移）；不适合有状态服务。

## 金丝雀发布 (Canary)

```yaml
# Argo Rollouts Canary 步骤
strategy:
  canary:
    steps:
      - setWeight: 5      # 5% 流量到新版本
      - pause: { duration: 10m }
      - setWeight: 25
      - pause: { duration: 10m }
      - setWeight: 50
      - pause: { duration: 10m }
      - setWeight: 100
```

**原理**：新版本先接 5% 流量，观察 SLO / 错误率；逐步 25% → 50% → 100%；任一步骤失败立即回滚。

**优势**：风险渐进可控；适合"算法更新 / 性能优化"等用户可感知的变更。
**劣势**：需要 Service Mesh（Istio / Linkerd）或 Ingress Controller（Nginx / Traefik）支持按权重路由。

## Feature Flag

```typescript
// LaunchDarkly / Unleash / 自建 FeatureFlag
if (featureFlags.isEnabled('new-checkout', { userId: req.user.id })) {
  return newCheckoutFlow(req);
} else {
  return legacyCheckoutFlow(req);
}
```

**原理**：代码里内置开关，配置中心动态开启 / 关闭 / 灰度用户。

**优势**：秒级生效，不需要重新部署；支持用户分群（A/B / 内部用户）；代码与配置解耦。
**劣势**：长期遗留的"死代码"需要定期清理；Flag 体系需要治理（owner / 过期时间）。

## 影子流量 (Shadow Traffic)

```yaml
# Istio VirtualService 影子流量
http:
- route:
  - destination:
      host: my-app-v1
  mirror:
    host: my-app-v2
    mirrorPercent: 100
```

**原理**：复制一份生产流量到新版本，新版本只接收请求不返回响应（响应被丢弃）。

**优势**：用真实流量压测新版本，零用户影响；适合"性能对比 / 模型推理延迟对比"。
**劣势**：新版本必须保证幂等（同一个请求可能执行两次）；需要 Sidecar / Mesh 支持。

## 回滚机制设计

```
回滚 = (1) 流量切换 + (2) 数据库回退 + (3) 配置回退 + (4) 通知

1. 流量切换
   - 蓝绿：秒级（改 Service selector）
   - 金丝雀：分钟级（Argo Rollouts abort）
   - Feature Flag：秒级（关开关）

2. 数据库回退
   - 兼容性：旧版本代码必须能读新版本 schema
   - 反向迁移：DB migration 必须有 down()
   - 双写期：新旧版本都写新 schema 一段时间

3. 配置回退
   - Helm values 回滚到上一个 Git commit
   - ArgoCD 自动同步

4. 通知
   - 失败时自动 @oncall
   - Slack / PagerDuty 集成
```

## 关联章节

- **01-pipeline** → 发布由哪个 Pipeline 触发
- **03-gitops/argocd** → Argo Rollouts 实现的金丝雀
- **05-cicd-observability/dora-metrics** → 发布频率作为 DORA 度量
