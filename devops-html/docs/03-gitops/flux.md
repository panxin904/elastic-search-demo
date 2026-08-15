---
title: Flux
---

# Flux

Flux 是 CNCF 毕业项目，GitOps 工具集，采用微服务架构（多个 Controller 协同工作）。

## 一句话总结

> **Flux = GitOps-native 框架**。**核心：GitOps Toolkit（多个 CRD Controller）**。**强项：云原生 / GitOps 原则贯彻 / 与 ArgoCD 互补**。**弱项：UI 弱（需 CLI 或外部）/ 多租户需要自己实现**。

---

## GitOps Toolkit（6 个 Controller）

```
Source Controller      拉取 Git/Helm/S3 源
Kustomize Controller   调和 Kustomization
Helm Controller        调和 HelmRelease
Notification Controller  事件通知（Slack / Lark）
Image Reflector / Updater  自动更新镜像 tag
Image Automation Controller  基于策略更新 image
```

## 核心 CRD

```yaml
# GitRepository（源码）
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  url: https://github.com/myorg/my-app-manifests
  ref:
    branch: main
```

```yaml
# Kustomization（应用）
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 10m
  sourceRef:
    kind: GitRepository
    name: my-app
  path: ./overlays/prod
  prune: true
  wait: true
  timeout: 5m
```

```yaml
# HelmRelease（Helm 应用）
apiVersion: helm.toolkit.fluxcd.io/v2
kind: HelmRelease
metadata:
  name: my-app
  namespace: flux-system
spec:
  interval: 5m
  chart:
    spec:
      chart: my-app
      version: "1.2.3"
      sourceRef:
        kind: HelmRepository
        name: my-registry
  values:
    replicaCount: 3
    image:
      tag: v1.2.3
```

## Flux CLI

```bash
# 安装
curl -s https://fluxcd.io/install.sh | sudo bash

# bootstrap（一次性安装 + 接入 Git）
flux bootstrap github \
  --owner=myorg \
  --repository=fleet-infra \
  --branch=main \
  --path=clusters/prod \
  --personal

# 常用命令
flux get sources git
flux get kustomizations
flux get helmreleases
flux reconcile kustomization my-app
flux suspend kustomization my-app
flux resume kustomization my-app
```

## Flux vs ArgoCD 决策

| 维度 | ArgoCD | Flux |
|------|--------|------|
| **架构** | 单体 + UI | 微服务 + CLI |
| **UI** | 强（Web） | 弱（CLI + Grafana） |
| **多租户** | AppProject 原生 | 需要 namespace 隔离 |
| **Helm 集成** | 内置 | Helm Controller |
| **Kustomize** | 内置 | Kustomize Controller |
| **通知** | 弱 | Notification Controller |
| **学习曲线** | 中（概念集中） | 中（多个 CRD） |
| **GitOps 纯粹度** | 高（但有人批评 UI 不够 GitOps） | 极高（GitOps-native） |
| **生态** | Argo Rollouts / Argo Events / Argo Workflows | Flagger（渐进式发布） |

## 通知配置

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta2
kind: Alert
metadata:
  name: on-call
  namespace: flux-system
spec:
  providerRef:
    name: slack
  eventSeverity: error
  eventSources:
    - kind: Kustomization
      name: '*'
```

```yaml
apiVersion: notification.toolkit.fluxcd.io/v1beta1
kind: Provider
metadata:
  name: slack
  namespace: flux-system
spec:
  type: slack
  channel: alerts
  address: https://hooks.slack.com/services/XXX
```

## 关联章节

- **03-gitops/overview**：GitOps 总览
- **03-gitops/argocd**：ArgoCD 对比
- **03-gitops/progressive-delivery**：Flagger 渐进式发布
- **04-release/canary**：金丝雀发布策略

## 一句话总结

> **Flux = GitOps-native 框架**。**何时用：纯 GitOps 团队 / 不需要 UI / 与 Prometheus 深度集成**。**何时不用：需要 UI / 多租户 / 团队习惯 ArgoCD**。
