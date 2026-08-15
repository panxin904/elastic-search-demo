---
title: 金丝雀发布
---

# 金丝雀发布 (Canary)

金丝雀发布源自矿井的金丝雀比喻：新版本先接小比例流量（5%），观察无异常后逐步扩大（25% → 50% → 100%）。

## 一句话总结

> **金丝雀 = 渐进式放量**。**核心：小流量试错 + 监控驱动 + 自动回滚**。**适用：算法更新 / 性能优化 / 用户可感知的变更**。**代价：需要 Service Mesh / Ingress 支持按权重路由**。

---

## 工作流

```
T0: v1.0 = 100%（生产）
T1: v2.0 = 5%（观察 10 分钟）
T2: v2.0 = 25%（观察 10 分钟）
T3: v2.0 = 50%（观察 10 分钟）
T4: v2.0 = 100%（v1.0 退役）
```

## Istio VirtualService 实现

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: my-app
spec:
  hosts:
    - my-app
  http:
    - route:
        - destination:
            host: my-app
            subset: v1
          weight: 95
        - destination:
            host: my-app
            subset: v2
          weight: 5
---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: my-app
spec:
  host: my-app
  subsets:
    - name: v1
      labels: { version: v1 }
    - name: v2
      labels: { version: v2 }
```

## Argo Rollouts 实现

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 5
        - pause: { duration: 10m }
        - setWeight: 25
        - pause: { duration: 10m }
        - setWeight: 50
        - pause: { duration: 10m }
        - setWeight: 100
      canaryService: my-app-canary
      stableService: my-app-stable
      trafficRouting:
        istio:
          virtualService:
            name: my-app-vsvc
```

## Nginx Ingress 实现（按 Header）

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "5"
    nginx.ingress.kubernetes.io/canary-by-header: "X-Canary"
    nginx.ingress.kubernetes.io/canary-by-header-value: "always"
spec:
  rules:
    - host: my-app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app-stable
                port:
                  number: 80
```

```bash
# 内部测试
curl -H "X-Canary: always" https://my-app.example.com
```

## 自动回滚条件

```yaml
# Argo Rollouts Analysis
analysis:
  templates:
    - templateName: error-rate
  args:
    - name: service-name
      value: my-app

---
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate
spec:
  metrics:
    - name: error-rate
      interval: 30s
      successCondition: result < 0.01   # 错误率 < 1%
      failureLimit: 3                   # 连续 3 次失败回滚
      provider:
        prometheus:
          query: |
            sum(rate(http_requests_total{service="{{args.service-name}}",code=~"5.."}[2m]))
            /
            sum(rate(http_requests_total{service="{{args.service-name}}"}[2m]))
```

## 度量选择

```yaml
# 必备：技术指标
- error_rate: HTTP 5xx 比例
- p99_latency: P99 延迟
- throughput: QPS（不应下降过多）

# 高级：业务指标
- ctr: 点击率（推荐系统）
- conversion_rate: 转化率（电商）
- retention: 留存（功能上线）

# 来源
- Prometheus（最常用）
- DataDog
- 自建 metrics API
```

## 关联章节

- **04-release/overview**：5 大发布策略
- **04-release/blue-green**：蓝绿对比
- **03-gitops/progressive-delivery**：渐进式发布工具
- **04-release/feature-flag**：Feature Flag 互补

## 一句话总结

> **金丝雀 = 发布策略的事实标准**。**何时用：算法 / 性能 / 用户可感知的变更**。**何时不用：内部工具 / 后台 job / 一次性脚本（蓝绿或滚动更简单）**。
