---
title: ArgoCD
---

# ArgoCD - GitOps 事实标准

> ArgoCD = k8s 原生 GitOps 工具。UI 强、与 Helm / Kustomize / Jsonnet 无缝集成。

## 🤔 为什么选 ArgoCD

```
Flux CD：
  - 命令行强，UI 弱
  - 资源少，文档薄
  - 适合"让 CI 安静跑"

ArgoCD：
  ✅ 强大 Web UI（看应用状态 / diff / 回滚）
  ✅ 多集群管理（控制面 → 多套集群）
  ✅ 多应用管理（一个 Application = 一组资源）
  ✅ SSO / RBAC / Audit 完善
  ✅ 跟 Helm / Kustomize / plain yaml 都行
  ✅ 跟 Argo Rollouts 集成（蓝绿 / 金丝雀）
```

## 🏗️ 架构

```
[Developer] -push-> [Git Repo] 
                            |
                            v webhook（可选）
                       [ArgoCD] 
                        - 持续对比 Git vs Cluster
                        - 自动 / 手动 sync
                            |
                            v
                       [k8s Cluster]
                       
[Operator] 看着 [Web UI] 看到所有应用状态
```

| 组件 | 作用 |
|------|------|
| **argocd-server** | API + Web UI |
| **argocd-application-controller** | 持续 reconcile |
| **argocd-repo-server** | Git 仓库连接 |
| **argocd-dex-server** | SSO / OAuth |

## 🚀 安装

```bash
# 命名空间
kubectl create namespace argocd

# 装（latest stable）
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 装 CLI
brew install argocd    # macOS
# 或
curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
chmod +x /usr/local/bin/argocd
```

## 🔌 访问 UI

```bash
# 端口转发
kubectl port-forward svc/argocd-server -n argocd 8080:443

# 浏览器
open https://localhost:8080
# ⚠️ 首次登录 admin / 应用名（自动生成）

# 拿初始密码
argocd admin initial-password -n argocd
```

## 🎯 第一个 Application

```yaml
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
      prune: true              # 删 Git 没有的资源
      selfHeal: true           # 改回去 Git 状态
    syncOptions:
      CreateNamespace: true
    retry:
      limit: 5
      backoff:
        duration: 10s
        factor: 2
        maxDuration: 5m
```

```bash
kubectl apply -f application.yaml

# 看
argocd app get web-dev
argocd app list
argocd app history web-dev
```

## 🔄 同步策略

### 自动同步

```yaml
syncPolicy:
  automated:
    prune: true              # 删不在 Git 里的资源
    selfHeal: true           # 集群漂移自动修正
    allowEmpty: false        # 防止清空
```

### 手动同步

```yaml
syncPolicy: {}                # 不写 automated = 手动
```

```bash
argocd app sync web-dev       # 手动同步
```

### 自动化策略

```yaml
syncOptions:
  CreateNamespace: true       # 自动建 ns
  PrunePropagationPolicy: foreground
  PruneLast: true
```

## 🛠 实战

### 1. 看 diff

```bash
# 详细 diff
argocd app diff web-dev

# Web UI：实时显示 Live Manifest vs Target Manifest
```

### 2. 回滚

```bash
# 查历史
argocd app history web-dev
# ID  DATE                  REVISION
# 0   2024-01-15 10:00:00   abc123
# 1   2024-01-15 11:00:00   def456
# 2   2024-01-15 12:00:00   ghi789

# 回滚到指定版本
argocd app rollback web-dev --id 1
```

### 3. 同步窗口

```bash
# 禁止工作时间部署
argocd app set web-dev --sync-window-duration 1h --sync-window-kind deny
```

### 4. 通知

```yaml
metadata:
  annotations:
    notifications.argoproj.io/subscribe.on-sync-succeeded.slack: my-channel
```

## 🔐 同步状态可视化

| 状态 | 含义 |
|------|------|
| **Synced** | Git ↔ Cluster 一致 |
| **OutOfSync** | 集群漂移（被人改了 / Git 改了没 sync） |
| **Unknown** | 连不上 / 仓库解析失败 |
| **Degraded** | 部分资源失败 |

健康：
- **Healthy** = 资源 Running
- **Degraded** = 部分 Pending / Failed
- **Suspended** = 暂停同步

## 🔐 多集群

```yaml
# 加集群
apiVersion: v1
kind: Secret
metadata:
  name: cluster-prod-2
  namespace: argocd
stringData:
  name: prod-2
  server: https://prod-2.kube.example.com
  config: |
    {
      "bearerToken": "xxx"
    }
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-prod-2
data:
  name: prod-2
  server: https://prod-2.kube.example.com
```

UI 上就能看到 + 选为目标集群。

## 🛡 渐进式发布

ArgoCD 配套 **Argo Rollouts** 提供蓝绿 / 金丝雀 / 自动回滚：

```bash
helm install argo-rollouts argo/argo-rollouts -n argo-rollouts
```

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: web
spec:
  replicas: 10
  strategy:
    canary:
      steps:
      - setWeight: 5            # 5% 流量给 v2
      - pause: { duration: 5m } # 5 分钟看指标
      - setWeight: 25
      - pause: { duration: 5m }
      - setWeight: 100
      canaryService: web-canary
      stableService: web-stable
      trafficRouting:
        istio:
          virtualService: { name: web-vs }
```

健康检查失败自动回滚到 v1。

## 🆚 ArgoCD vs Flux CD

| | ArgoCD | Flux CD |
|--|---------|---------|
| UI | 强大 Web UI | 命令行（Web UI 需装 Web 插件） |
| 学习曲线 | 中 | 略陡 |
| 多集群 | 内置 | 需 Multi-Tenant Operator |
| 渐进式发布 | Argo Rollouts | Flagger（类似） |
| 适合 | 大多场景 | 命令行偏好 / GitOps 工具链 |

## 🩹 故障

```bash
# Application 一直 OutOfSync
argocd app get web-dev
# 看 Conditions / Sync Status

# 集群漂移（有人 kubectl apply）
argocd app diff web-dev
# 改 selfHeal: true → 自动 sync

# webhook 不触发
# 检查 repo-server 日志
kubectl logs -n argocd deploy/argocd-repo-server

# secrets 同步（K8s 1.27+）
metadata:
  annotations:
    argocd.argoproj.io/compare-options: IgnoreServerSideDiff
```

## 🛠 实战

```bash
# 1. 装
kubectl create ns argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 2. 端口转发
kubectl port-forward svc/argocd-server -n argocd 8080:443 &

# 3. 登录
argocd login localhost:8080 --insecure
# 输入 admin / 上面拿到的密码

# 4. 加 application
argocd app create web-dev \
  --repo https://github.com/myorg/manifests \
  --path overlays/dev \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace dev \
  --sync-policy automated

# 5. 改 Git 仓库 → 自动同步
# 浏览器看 https://localhost:8080
```

## 🔗 下一步

- [GitOps 思想](/09-cicd/gitops)
- [Tekton / JenkinsX](/09-cicd/tekton)
- [Helm Chart](/06-helm/chart)