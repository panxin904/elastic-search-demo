---
title: Chart 结构
---

# Helm Chart 结构

> Helm = k8s 包管理。Chart = 一组打好的 k8s manifest 模板。

## 🤔 为什么需要 Helm

```
❌ 裸 yaml：
  - 多个环境（dev / staging / prod）改 N 个值
  - 升级难（滚动？回滚？）
  - 多个资源组合应用要挨个 apply
  - 没有版本概念

✅ Helm：
  - 模板 + values（参数化）
  - 一次 install / upgrade / rollback
  - Release 版本管理
  - 仓库（artifact hub / chartmuseum）
```

## 📁 Chart 目录

```
myapp/
├── Chart.yaml          # 元信息
├── values.yaml         # 默认配置
├── templates/          # 模板目录（k8s manifest）
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── _helpers.tpl     # 模板辅助函数（文件名 _ 开头被忽略）
│   └── NOTES.txt        # 装完显示的提示
├── charts/             # 依赖（chart-of-charts）
├── .helmignore         # 忽略规则
└── README.md
```

## 📜 Chart.yaml

```yaml
apiVersion: v2
name: myapp
description: My web app
type: application
version: 1.2.3          # Chart 版本（SemVer）
appVersion: "2.0.1"     # 应用版本（仅展示）
icon: https://example.com/logo.png
maintainers:
  - name: Alice
    email: alice@example.com
keywords:
  - web
  - demo
dependencies:
  - name: postgresql
    version: 15.1.0
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

## 📜 values.yaml

```yaml
# 默认配置（用户可覆盖）

replicaCount: 2

image:
  repository: nginx
  tag: "1.25-alpine"
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 80

ingress:
  enabled: false
  className: nginx
  host: chart-example.local

resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    cpu: 500m
    memory: 256Mi

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

postgresql:
  enabled: true
  auth:
    username: myapp
    password: secret
    database: myapp
```

## 📜 templates/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: APP_FULLNAME
  labels:    # labels helper
spec:
  replicas: REPLICA_COUNT
  selector:
    matchLabels: SELECTOR_LABELS
  template:
    metadata:
      labels: TEMPLATE_LABELS
    spec:
      containers:
        - name: APP_NAME
          image: "IMAGE:IMAGE_TAG"
          imagePullPolicy: IMAGE_PULL_POLICY
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /
              port: http
          readinessProbe:
            httpGet:
              path: /
              port: http
          resources:
            LIMITS_AND_REQUESTS
```

## 🪜 模板函数

| 函数 | 作用 |
|------|------|
| `\{\{- .Values.x \}\}` | 渲染 value |
| `\{\{- .Chart.Name \}\}` | Chart 名 |
| `\{\{- .Release.Name \}\}` | Release 名 |
| `\{\{- include "template" . \}\}` | 包含子模板 |
| `\{\{- default "fallback" .Values.x \}\}` | 默认值 |
| `\{\{- toYaml .Values.x \| nindent 4 \}\}` | 渲染 yaml + 缩进 |
| `\{\{- quote .Values.x \}\}` | 加引号 |
| `\{\{- upper .Values.x \}\}` / `\{\{- lower \}\}` | 大小写 |
| `\{\{- b64enc "secret" \}\}` | base64 编码 |
| `\{\{- tpl "..." . \}\}` | 模板字符串 |

## 🛠 实战

### 1. 创建 Chart

```bash
helm create myapp
cd myapp
# 编辑 Chart.yaml / values.yaml / templates/

# 渲染模板看实际输出
helm template myapp ./myapp
helm template myapp ./myapp --set replicaCount=3

# 语法检查
helm lint ./myapp

# 干跑
helm install myapp ./myapp --dry-run --debug
```

### 2. 渲染单一文件

```bash
helm template myapp ./myapp --show-only templates/deployment.yaml
```

### 3. 安装

```bash
helm install release-name ./myapp
helm install release-name ./myapp -f my-values.yaml
helm install release-name ./myapp --set replicaCount=5
helm install release-name ./myapp --set-string database.password=xxx
```

### 4. 升级 / 回滚

```bash
# 升级
helm upgrade release-name ./myapp

# 看历史
helm history release-name

# 回滚
helm rollback release-name 1
```

### 5. 删除

```bash
helm uninstall release-name
helm uninstall release-name --keep-history    # 保留历史
```

## 🆚 Helm 2 vs Helm 3

| | Helm 2 | Helm 3 |
|--|--------|--------|
| Tiller | 需要（集群侧服务） | **不再需要**（client-only） |
| CRD 升级 | 限制 | 全支持 |
| Chart repo | 复杂 | 简单 |
| Release 命名 | 需指定 | 可省略 |
| 库（library） | helm2 维护 | helm3 推荐 |

**只用 Helm 3**。

## 🔗 下一步

- [template / values](/06-helm/template)
- [Chart 仓库](/06-helm/repository)
- [Helmfile / Kustomize](/10-iac/helmfile)