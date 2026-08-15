---
title: Chart 仓库
---

# Helm Chart 仓库

> Chart 仓库 = 集中分发 Helm Chart 的地方。类似 Docker Hub for images。

## 🤔 为什么需要仓库

```
本地 Chart（./myapp）：
  - 只有本地可用
  - 团队 / 跨集群共享困难

Chart 仓库：
  - 团队 / 公司内共享
  - 版本管理
  - 类似 npm registry / Docker Hub
```

## 📚 主流仓库

| 仓库 | 特点 |
|------|------|
| **Artifact Hub** | CNCF 官方聚合（k8s 旗下） |
| **Bitnami Charts** | 老牌，chart 数量最多 |
| **Helm Stable** | Helm 官方仓库（已并入 Artifact Hub） |
| **ChartMuseum** | 自建仓库服务端 |
| **Harbor** | 自带 Chart 仓库的镜像服务 |
| **OCI Registry** | 把 Chart 存到镜像仓库（如 GHCR / Docker Hub） |

## 🔧 helm 仓库命令

```bash
# 加仓库
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add stable https://charts.helm.sh/stable    # 已归档
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

# 更新索引
helm repo update

# 列出已加仓库
helm repo list

# 找 Chart
helm search repo nginx
helm search hub nginx       # 在 Artifact Hub 找

# 看 Chart 信息
helm show chart bitnami/nginx
helm show all bitnami/nginx
helm show values bitnami/nginx   # 默认 values
```

## 🌐 Artifact Hub

```bash
# 装 helm-search-plugin（更全的搜索）
helm search hub mysql

# 直接装
helm install my-mysql oci://registry-1.docker.io/bitnamicharts/mysql
```

地址：https://artifacthub.io

## 🏗 自建 ChartMuseum

```bash
# 用 helm 装
helm repo add chartmuseum https://chartmuseum.github.io/charts
helm install my-repo chartmuseum/chartmuseum \
  --set persistence.enabled=true \
  --set persistence.size=8Gi

# 推送 Chart
helm plugin install https://github.com/chartmuseum/helm-push
helm push ./myapp-1.0.0.tgz chartmuseum   # 或 OCI 推送

# 用
helm repo add my-repo http://chartmuseum.local
helm install myapp my-repo/myapp
```

## 🐳 OCI Registry（Chart as Container）

Helm 3 支持把 Chart 当 OCI artifact 推送到镜像仓库。

```bash
# 登录
helm registry login ghcr.io -u alice -p <token>

# 打包 + 推送
helm chart save ./myapp oci://ghcr.io/myorg/charts/myapp:1.0.0

# 推送
helm chart push oci://ghcr.io/myorg/charts/myapp:1.0.0

# 装（必须先 helm registry login）
helm install myapp oci://ghcr.io/myorg/charts/myapp --version 1.0.0

# 列
helm chart list oci://ghcr.io/myorg/charts

# 拉
helm chart pull oci://ghcr.io/myorg/charts/myapp:1.0.0
```

**好处**：不需要单独搭 ChartMuseum，复用现有 OCI 仓库（GHCR / Harbor / ECR）。

## 🔐 仓库认证

```bash
# helm 默认读 ~/.config/helm/registry/config.json

# 登录
helm registry login ghcr.io -u alice -p <token>

# 登出
helm registry logout ghcr.io
```

## 📋 实战

### 1. 用现成 Chart

```bash
# 加仓库
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# 看可用版本
helm search repo nginx --versions
# NAME            CHART VERSION  APP VERSION  DESCRIPTION
# bitnami/nginx    15.0.0         1.25.1       Chart for the nginx server
# bitnami/nginx    14.0.0         1.25.0       ...

# 装指定版本
helm install my-nginx bitnami/nginx --version 15.0.0

# 自定义 values
helm install my-nginx bitnami/nginx --set service.type=LoadBalancer

# 干跑 + 输出渲染结果
helm install my-nginx bitnami/nginx --dry-run --debug
```

### 2. 推 Chart 到私有仓库

```bash
# 1. helm registry login
helm registry login harbor.example.com -u alice -p xxx

# 2. 打包
helm package ./myapp -d ./dist
# 生成 dist/myapp-1.0.0.tgz

# 3. 推送
helm push ./dist/myapp-1.0.0.tgz oci://harbor.example.com/charts

# 4. 装
helm install myapp oci://harbor.example.com/charts/myapp --version 1.0.0
```

### 3. 用 ChartMuseum 自建

```bash
# 装
helm install cm chartmuseum/chartmuseum \
  --set env.open.SHOWING_CHARTS=true \
  --set persistence.enabled=true \
  --set persistence.size=10Gi

# 推送（先装 helm-push plugin）
helm plugin install https://github.com/chartmuseum/helm-push
helm push ./myapp-1.0.0.tgz cm

# 用
helm repo add my-cm http://chartmuseum.local
helm install myapp my-cm/myapp
```

## 🆚 仓库方案对比

| | ChartMuseum | OCI Registry | Artifact Hub |
|--|------------|--------------|---------------|
| 协议 | HTTP + index.yaml | OCI distribution | OCI distribution |
| 部署 | 需要一个 Pod | 复用 OCI | SaaS / 自托管 |
| 适用 | 传统仓库 | 已有 OCI 基础设施 | 公网搜索 |
| 索引 | helm-push | OCI tags | 自动爬取 |

## 🔗 下一步

- [Chart 结构](/06-helm/chart)
- [template / values](/06-helm/template)
- [ArgoCD](/09-cicd/argocd)