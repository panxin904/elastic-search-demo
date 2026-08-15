---
title: Helmfile / Kustomize
---

# Helmfile / Kustomize - 渐进式 k8s 配置

> 不创建新格式，而是**对已有 helm chart 叠加配置**。Kustomize 内置 kubectl；Helmfile 声明式 release。

## 🤔 为什么用

```
裸 Helm：
  - values 一坨
  - 多环境用不同 values 文件

Kustomize：
  ✅ kubectl 内置（不用装）
  ✅ patch 而非覆盖（合并 base + overlay）
  ✅ 跨环境复用

Helmfile：
  ✅ 一次跑多个 helm release
  ✅ values 复用 / 跨环境
  ✅ 适合 GitOps（声明式 release 列表）
```

## 🆚 vs 选型

| | Kustomize | Helmfile | Helm |
|--|-----------|----------|------|
| 哲学 | patch / 合并 | 多 release 声明 | 模板渲染 |
| 内置 | kubectl 内置 | 独立工具 | 独立工具 |
| 配合 | kustomize + ArgoCD | helmfile + ArgoCD | Helm + kubectl |
| 适合 | 已有 yaml 想分环境 | 多 helm release | 单 chart |

## 📜 Kustomize

### 目录结构

```
myapp/
├── base/                      # 基础资源
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
└── overlays/                  # 环境
    ├── dev/
    │   ├── kustomization.yaml
    │   ├── patch-replicas.yaml
    │   └── patch-configmap.yaml
    └── prod/
        ├── kustomization.yaml
        └── patch-replicas.yaml
```

### base/kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml
- configmap.yaml

commonLabels:
  app: myapp
  managed-by: kustomize
```

### overlays/dev/kustomization.yaml

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

namespace: dev
namePrefix: dev-

resources:
- ../../base

# patch（JSON patch）
patches:
- target:
    kind: Deployment
    name: myapp
  patch: |-
    - op: replace
      path: /spec/replicas
      value: 1
    - op: replace
      path: /spec/template/spec/containers/0/resources/limits/cpu
      value: "200m"
```

### overlays/dev/patch-replicas.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: myapp
        resources:
          requests:
            cpu: 50m
            memory: 64Mi
```

### 用法

```bash
# 看渲染结果
kubectl kustomize overlays/dev/

# 应用
kubectl apply -k overlays/dev/

# 删
kubectl delete -k overlays/dev/
```

## 🪜 高级 Kustomize

### Image 改 tag

```yaml
images:
- name: myapp
  newName: registry.example.com/myapp
  newTag: 1.2.0
```

### 引用其他 chart

```yaml
# 用 helm + kustomize
helmCharts:
- name: postgres
  repo: https://charts.bitnami.com/bitnami
  version: 15.0.0
  releaseName: db
  namespace: dev
  valuesInline:
    auth:
      username: myapp
      password: secret
```

### 远程资源

```yaml
# 从 git 拉
resources:
- github.com/myorg/manifests//base?ref=v1.0.0
```

## 📜 Helmfile

### 安装

```bash
# macOS
brew install helmfile

# Linux
curl -fsSL https://raw.githubusercontent.com/helmfile/helmfile/master/scripts/install.sh | bash
```

### helmfile.yaml

```yaml
repositories:
- name: bitnami
  url: https://charts.bitnami.com/bitnami
- name: ingress-nginx
  url: https://kubernetes.github.io/ingress-nginx

releases:
# PostgreSQL
- name: db
  namespace: db
  chart: bitnami/postgresql
  version: 15.0.0
  values:
  - persistence:
      size: 10Gi
  - auth:
      username: myapp
      password: secret
      database: myapp

# Redis
- name: cache
  namespace: cache
  chart: bitnami/redis
  version: 18.0.0
  values:
  - persistence:
      size: 2Gi

# Ingress
- name: nginx
  namespace: ingress
  chart: ingress-nginx/ingress-nginx
  version: 4.7.0
  values:
  - controller:
      service:
        type: LoadBalancer
```

### 多环境

```yaml
# helmfile.yaml
environments:
  default:
    values:
      - environment: dev
  prod:
    values:
      - environment: prod
        replicas: 5
```

### 用法

```bash
# 默认环境
helmfile apply

# 指定环境
helmfile -e prod apply

# 同步
helmfile sync

# diff
helmfile diff

# 销毁
helmfile destroy
```

## 🔧 实战

### Kustomize 渐进式发布

```bash
# 1. kustomization
cd overlays/prod
kustomize edit set image myapp=registry.example.com/myapp:2.0.0
git commit -am "bump myapp to 2.0.0"

# 2. 推送 → ArgoCD 同步
git push
# 集群自动更新
```

### Helmfile 一次跑多 release

```bash
helmfile apply
# 装了 5 个 release → DB / Cache / App / Ingress / Prometheus
# 一次性（也适合 CI / ArgoCD）
```

## 🆚 vs ArgoCD

ArgoCD 不是 IaC 工具，是**同步器**。它从 Git 读任何格式（Helm / Kustomize / raw）然后 apply 到集群。

| 工具 | 角色 |
|------|------|
| Kustomize | 配置格式（叠加 / patch） |
| Helmfile | 多 helm release 声明式列表 |
| Terraform | 云基础设施（管云资源） |
| ArgoCD | GitOps 同步（管 K8s 资源） |

**生产组合**：Terraform 管云 → Ansible / Helmfile 装应用 → ArgoCD 持续同步。

## 🔗 下一步

- [Terraform](/10-iac/terraform)
- [Pulumi](/10-iac/pulumi)
- [GitOps 思想](/09-cicd/gitops)