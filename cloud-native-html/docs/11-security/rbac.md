---
title: RBAC 权限
date: 2026-08-15  # date-auto-injected
---

# RBAC - 基于角色的访问控制

> 谁（用户 / ServiceAccount）能对什么资源做什么动作。k8s 的"权限系统"。

![Kubernetes RBAC 鉴权流程](/k8s-rbac-flow.svg)

## 🤔 为什么需要 RBAC

```
默认：
  - cluster-admin 能做任何事
  - 普通 ServiceAccount 没权限

生产：
  - 开发者只读自己的 ns
  - CI 账号能 apply / rollout
  - 监控系统只读 metrics
  - 数据库账号只管 secret
```

## 🧬 核心概念

```
┌──────────────┐
│   Subject    │   谁（User / Group / ServiceAccount）
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   Role /     │   权限集合（哪些动词 + 哪些资源）
│ ClusterRole  │
└──────┬───────┘
       │
       ▼ 通过 Binding 授权
┌──────────────┐
│  Resource    │   资源（Pod / Service / Deployment …）
└──────────────┘
```

| 概念 | 作用 |
|------|------|
| **Subject** | User / Group / ServiceAccount |
| **Role** | 命名空间内权限 |
| **ClusterRole** | 集群范围权限 |
| **RoleBinding** | 把 Role 绑给 Subject（ns 范围） |
| **ClusterRoleBinding** | 绑给 Subject（集群范围） |

## 📜 Role 示例

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer
  namespace: dev
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log", "services"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "patch"]
# 禁 create / delete
```

```yaml
# ClusterRole（跨 ns）
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring-reader
rules:
- apiGroups: [""]
  resources: ["nodes", "nodes/metrics", "pods", "services"]
  verbs: ["get", "list", "watch"]
- nonResourceURLs: ["/metrics", "/healthz"]
  verbs: ["get"]
```

## 📜 RoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: alice-dev
  namespace: dev
subjects:
- kind: User
  name: alice
  apiGroup: rbac.authorization.k8s.io
- kind: Group
  name: dev-team
  apiGroup: rbac.authorization.k8s.io
- kind: ServiceAccount
  name: my-app
  namespace: dev
roleRef:
  kind: Role
  name: developer
  apiGroup: rbac.authorization.k8s.io
```

## 🛡️ ServiceAccount（Pod 身份）

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app
  namespace: prod
```

```yaml
# Pod 引用
spec:
  serviceAccountName: my-app
  automountServiceAccountToken: false   # 推荐关（不挂载 token）
```

Pod 内 `/var/run/secrets/kubernetes.io/serviceaccount/` 有 token（用 API 时鉴权）。

## 🔐 内置 ClusterRole

| Role | 权限 |
|------|------|
| `cluster-admin` | 一切 |
| `admin` | ns 内几乎一切 |
| `edit` | ns 内读写大部分 |
| `view` | ns 内只读 |

```bash
# 把 alice 绑成 cluster-admin（慎用）
kubectl create clusterrolebinding alice-admin \
  --clusterrole=cluster-admin \
  --user=alice

# alice 只能读 dev ns
kubectl create rolebinding alice-dev \
  --clusterrole=view \
  --user=alice \
  --namespace=dev
```

## 🔧 检查权限

```bash
# 看自己能不能做
kubectl auth can-i create pods
kubectl auth can-i create pods --as alice --namespace dev
kubectl auth can-i '*' '*' --as system:serviceaccount:default:my-app
kubectl auth can-i list nodes --as alice --all-namespaces

# 看谁能做
kubectl auth reconcile -f my-rbac.yaml
```

## 🪛 实战

### 1. CI 专用 ServiceAccount

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ci-deployer
  namespace: prod
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: ci-deployer
  namespace: prod
rules:
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "patch"]
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: ci-deployer
  namespace: prod
subjects:
- kind: ServiceAccount
  name: ci-deployer
  namespace: prod
roleRef:
  kind: Role
  name: ci-deployer
  apiGroup: rbac.authorization.k8s.io
```

### 2. 默认禁用 SA 自动挂载

```yaml
# /etc/kubernetes/准入控制
--enable-admission-plugins=NodeRestriction,ServiceAccount
# 但 PodSecurity / 严格模式更好
```

## 🆚 RBAC vs ABAC

| | RBAC | ABAC |
|--|------|------|
| 模型 | 角色 + 权限 | 基于属性 / 上下文 |
| 简单 | ✅ | ❌ |
| 灵活 | 中 | 极高 |
| 性能 | 快 | 慢（每次评估） |
| 主流 | k8s 默认 | Open Policy Agent (OPA) |

## 🩹 故障

```bash
# Forbidden 错误
kubectl get pods
# Error from server (Forbidden): pods is forbidden
# User "system:serviceaccount:default:my-app" cannot list pods

# 解决：建 Role + RoleBinding

# 调试
kubectl auth can-i list pods --as system:serviceaccount:default:my-app -n default

# 看谁有权限
kubectl get rolebinding -A
kubectl get clusterrolebinding
```

## 🛠 实战

```bash
# 看所有 Role / RoleBinding
kubectl get role,rolebinding -A
kubectl get clusterrole,clusterrolebinding

# 看特定 SA 能干啥
kubectl auth can-i list pods --as system:serviceaccount:dev:my-app -n dev

# 自动生成 RBAC（用 --reconcile）
kubectl auth reconcile -f my-role.yaml

# 实战
# 1. 建 SA
kubectl create sa ci-deployer -n prod
# 2. 建 Role + Binding（yaml）
# 3. 验证
kubectl auth can-i patch deployments --as system:serviceaccount:prod:ci-deployer -n prod
```

## 🔗 下一步

- [Secret 管理](/11-security/secret)
- [NetworkPolicy + PodSecurity](/11-security/policy)
- [Falco 运行时检测](/11-security/falco)