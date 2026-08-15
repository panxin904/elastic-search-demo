---
title: GitOps 思想
---

# GitOps 思想

> **Git = 唯一事实源**。集群状态、配置、变更全部从 Git 仓库里读，集群 = Git 仓库的"反映"。

## 🤔 为什么需要 GitOps

```
传统 CD：
  - 开发者 push → CI build → 手动 cd prod → 手动改 yaml
  ❌ 易错（手改 / 漏改）
  ❌ 难以回滚（找不到改了什么）
  ❌ 难审计（谁改了 / 改了什么 / 何时）
  ❌ 环境漂移（生产跟预发不一致）

GitOps：
  ✅ Git 是唯一事实源（Git = 生产）
  ✅ 改集群 = 提 PR（任何修改都有 PR 记录）
  ✅ 自动同步（Git 改了 → 集群自动同步）
  ✅ 自动漂移检测（集群 ≠ Git → 报警）
  ✅ 一键回滚（git revert 即可）
```

## 🏗️ 核心组件

```
[Developer] ─push──► [Git Repo] ─webhook──► [GitOps Controller]
                                                      │
                                                      ▼
                                                  [k8s Cluster]
                                                  (自动 reconcile)
```

- **Git 仓库** = manifest + 配置文件 + helm values + kustomize
- **CI** = 测试 + 构建镜像
- **GitOps Controller** = 持续同步 Git → 集群（ArgoCD / Flux）

## 🔄 推送 vs 拉取

| | Push（CI 推） | Pull（ArgoCD 拉） |
|--|----------------|---------------------|
| 谁改集群 | CI | ArgoCD |
| 集群可访问 | 集群需暴露 / 公网 | Git 仓库可访问（更安全） |
| 漂移检测 | ❌ | ✅ 自动 |
| 失败回滚 | CI 失败 | 自动 |
| 推荐度 | 老式 | **现代** |

## 🌟 GitOps 四原则

1. **声明式**：所有配置写成 yaml / helm
2. **版本化**：所有变更进 Git（带 commit / review）
3. **自动应用**：CI / ArgoCD 自动同步
4. **软件代理**：集群用 operator 持续 reconcile

## 🚀 主流工具

| 工具 | 风格 |
|------|------|
| **ArgoCD** | k8s 原生，UI 强，GitOps 事实标准 |
| **Flux CD** | GitOps Toolkit，更轻，更云原生 |
| **Argo Rollouts** | ArgoCD 配套，进阶发布策略 |
| **Jenkins X** | Jenkins + GitOps（复杂） |

## 🩻 实际项目布局

```
myapp/
├── apps/
│   ├── web/                    # 微服务 1
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── kustomization.yaml
│   └── api/                    # 微服务 2
├── infrastructure/             # 基础设施（naming 关注）
│   ├── namespaces/
│   │   ├── dev.yaml
│   │   ├── prod.yaml
│   ├── ingress/
│   └── certs/
├── overlays/                   # kustomize 覆盖
│   ├── dev/
│   │   ├── kustomization.yaml
│   │   └── patch-replicas.yaml
│   └── prod/
└── README.md
```

## 🛠 ArgoCD 流程

```bash
# 装
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 端口转发 UI
kubectl port-forward svc/argocd-server -n argocd 8080:443
# 浏览器 https://localhost:8080

# 装应用
argocd app create web \
  --repo https://github.com/myorg/myapp \
  --path apps/web/overlays/prod \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace prod \
  --sync-policy automated
```

详见 [ArgoCD](/09-cicd/argocd)。

## 🆚 GitOps vs CI/CD

| | GitOps | 传统 CI/CD |
|--|--------|------------|
| 状态来源 | Git | CI pipeline |
| 集群访问 | 拉（inbound） | 推（outbound） |
| 漂移检测 | ✅ 自动 | ❌ |
| 回滚 | git revert | 重新跑 CI |
| 审计 | git history | CI 日志 |
| 适合 | k8s / 声明式 | 任何环境 |

**GitOps 是 CI/CD 的升级版**（专对声明式基础设施）。

## 🔄 渐进式发布（Argo Rollouts）

传统 Deployment 是「立即切」；Argo Rollouts 支持：

- 蓝绿（blue-green）
- 金丝雀（canary：1% → 10% → 50% → 100%）
- 自动回滚（指标变差自动停）
- A/B 测试

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp
spec:
  strategy:
    canary:
      steps:
      - setWeight: 5
      - pause: { duration: 5m }
      - setWeight: 25
      - pause: { duration: 5m }
      - setWeight: 100
```

## 🛠 实战

### 1. 用 ArgoCD 同步 dev 命名空间

```bash
# 1. Git 仓库
git clone https://github.com/myorg/manifests.git
cd manifests
mkdir -p overlays/dev apps/web/base

# 2. 写 kustomize
cat > apps/web/base/kustomization.yaml <<EOF
resources:
- deployment.yaml
- service.yaml
commonLabels:
  app: web
EOF

# 3. dev 覆盖
cat > overlays/dev/kustomization.yaml <<EOF
namespace: dev
resources:
- ../../apps/web/base
patches:
- patch-replicas.yaml
EOF

# 4. push
git add . && git commit -m "init" && git push

# 5. ArgoCD Application
kubectl apply -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: web-dev
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/manifests
    targetRevision: main
    path: overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: dev
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
EOF

# 6. 自动同步：改 Git → 自动 apply
```

## 🔗 下一步

- [ArgoCD](/09-cicd/argocd)
- [Tekton / JenkinsX](/09-cicd/tekton)
- [Chart 结构](/06-helm/chart)