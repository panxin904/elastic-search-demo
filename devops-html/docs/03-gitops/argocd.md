---
title: ArgoCD
date: 2026-08-15  # date-auto-injected
---

# ArgoCD

ArgoCD 是 CNCF 毕业项目，GitOps 领域的标志性工具，自动同步 Git Repo 与 K8s 集群状态。

## 一句话总结

> **ArgoCD = GitOps 事实标准**。**核心：Application CRD + 调和循环 + Web UI**。**强项：UI / 多租户 / 多集群**。**弱项：单点（HA 需要 Workaround）**。

---

## 核心概念

```
Application    单个应用（Git 源 + 目标集群 + 目标 namespace）
AppProject     多应用分组（RBAC + 集群白名单）
Repository     Git/Helm 仓库源
Sync Status    Healthy / Degraded / Suspended / Unknown
Drift          Git 与集群实际状态不一致
```

## Application CRD

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/myorg/my-app-manifests
    targetRevision: HEAD
    path: overlays/prod
    helm:
      valueFiles:
        - values-prod.yaml

  destination:
    server: https://kubernetes.default.svc
    namespace: my-app

  syncPolicy:
    automated:
      prune: true           # 自动删除 Git 不存在的资源
      selfHeal: true        # 自动修复集群漂移
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

  revisionHistoryLimit: 10
```

## 调和循环

```yaml
# 1. Poll Git（默认 3 分钟，可改为 webhook）
# 2. Diff Git vs 集群
# 3. Sync（应用差异）
# 4. 健康检查（Resource Hooks）
```

## Sync Phases

```yaml
# PreSync：先执行（数据库 migration）
# Sync：核心（deployment apply）
# PostSync：后执行（通知 / 缓存预热）
# SyncFail：失败时执行

metadata:
  name: my-app
  annotations:
    argocd.argoproj.io/hook: PreSync
    argocd.argoproj.io/hook-delete-policy: BeforeHookCreation
```

## App of Apps 模式

```yaml
# 父 Application 管所有子 Application
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/myorg/manifests
    path: apps/             # apps/ 目录下每个目录 = 一个子 Application
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
```

```yaml
# apps/my-app/my-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  source:
    repoURL: https://github.com/myorg/manifests
    path: my-app
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app
```

## HA 架构

```yaml
# ArgoCD HA = 多副本 + Redis HA + Repo Server 多副本
spec:
  replicas: 3

# 关键组件：
# - argocd-application-controller（多副本）
# - argocd-repo-server（多副本）
# - argocd-server（多副本）
# - argocd-redis（HA 模式）
```

## 实战案例

```bash
# 安装 ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 端口转发 UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# CLI 登录
argocd login localhost:8080

# 创建应用
argocd app create my-app \
  --repo https://github.com/myorg/manifests \
  --path overlays/prod \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace my-app \
  --sync-policy automated

# 查看状态
argocd app list
argocd app get my-app
argocd app history my-app
```

## 关联章节

- **03-gitops/overview**：GitOps 总览
- **03-gitops/flux**：Flux 对比
- **04-release/canary**：Argo Rollouts 实现的金丝雀
- **04-release/progressive-delivery**：Argo Rollouts 高级用法

## 一句话总结

> **ArgoCD = GitOps 首选**。**何时用：K8s 团队 / 需要 UI / 多租户**。**何时不用：非 K8s 工作负载（VM / Serverless）/ 跨云编排（用 Crossplane）**。


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
