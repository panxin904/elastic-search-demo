---
title: GitOps 总览
date: 2026-08-15  # date-auto-injected
---

# GitOps 总览

GitOps 用 Git 作为"基础设施与应用的唯一真相源"，任何变更都必须通过 PR/MR 走 Git 流程。本章梳理 GitOps 范式与两大主流工具。

## GitOps 四大原则

```
1. 声明式 (Declarative)
   整个系统用声明式文件描述（K8s Manifest / Helm / Kustomize）

2. 版本化 + 不可变 (Versioned & Immutable)
   Git 历史就是完整审计日志，可以回滚到任意时刻

3. 自动拉取 (Pulled Automatically)
   Agent 自动 watch Git 与实际状态，diff 后自动 sync

4. 持续调和 (Continuously Reconciled)
   Agent 周期性检查，确保实际状态始终收敛到声明状态
```

## Pull vs Push 模型

```
传统 CI/CD (Push 模型)
  CI 系统 build →  ssh kubectl apply →  集群
  问题：CI 需要集群凭证、安全边界模糊、回滚需手动

GitOps (Pull 模型)
  Git Repo →  ArgoCD Agent (in cluster) →  调和 K8s API
  优势：Agent 不需要外网凭证、随时回滚（git revert）、审计天然
```

## ArgoCD vs Flux 横向对比

| 维度 | ArgoCD | Flux |
|------|--------|------|
| **架构** | 单体应用 + UI | 微服务（Source Controller / Kustomize Controller / Helm Controller / Notification Controller） |
| **UI** | 强（Web UI + CLI） | 弱（纯 CLI，可接 Grafana） |
| **多租户** | App Project 原生支持 | 需手动 Namespace 隔离 |
| **Sync 策略** | 手动 / 自动 / 差异修正 | 自动（strict / recreate / prune） |
| **Helm 支持** | 内置 | Helm Controller |
| **Kustomize 支持** | 内置 | Kustomize Controller |
| **应用模型** | Application CRD（应用 = 1 个 Git 源 + 1 个集群 + 1 个 namespace） | Kustomization / HelmRelease（更细粒度） |
| **学习曲线** | 中（概念集中） | 中高（多个 Controller） |
| **最佳场景** | 团队需要 UI / 多租户 | GitOps-native 团队 / 大规模 |

## 核心工作流

```yaml
# ArgoCD Application 示例
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
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

## GitOps 落地 3 阶段

```
Phase 1: 影子模式（Shadow）
  - ArgoCD 同步一份 manifest，但 kubectl apply 仍由 CI 控制
  - 验证 ArgoCD 工作流，零风险

Phase 2: 双写模式（Dual-write）
  - CI 部署到 staging，ArgoCD 部署到 prod
  - 验证生产可靠性，逐步迁移

Phase 3: 纯 GitOps（Pure GitOps）
  - CI 只构建镜像 + 更新 manifest repo
  - ArgoCD 全权负责所有环境的部署
```

## 常见陷阱

1. **Secret 管理**：GitOps 反对把 Secret 提交到 Git，必须用 Sealed Secrets / External Secrets Operator / SOPS
2. **多环境配置**：用 Kustomize overlays / Helm values 多环境，不要硬编码 namespace
3. **Image tag 不确定**：CI 推镜像后必须更新 manifest 的 image tag，常用方案是 `kustomize edit set image` 或 ArgoCD Image Updater
4. **Drift 处理**：开发者用 kubectl 改了东西，ArgoCD selfHeal 会自动回滚；需要团队文化认同"Git 是唯一真相源"

## 关联章节

- **04-release** → Argo Rollouts 实现的蓝绿 / 金丝雀
- **05-cicd-observability** → ArgoCD 自身可观测性
- **06-best-practices/oidc-federation** → ArgoCD 如何 OIDC 登录


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

<!-- svg-injected:do-not-edit -->

## 图示：Kubernetes 集群架构

![Kubernetes 集群架构](/k8s-architecture.svg)
