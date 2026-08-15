---
title: NetworkPolicy
---

# NetworkPolicy - 东西向流量隔离

> 默认 k8s 集群内所有 Pod 互通。NetworkPolicy = 集群内的"防火墙"。

## 🤔 为什么需要 NetworkPolicy

```
默认行为：
  - 所有 Pod 互通
  - 所有 namespace 互通
  - 所有 Node 也能访问 Pod（Service 范围）

生产需要：
  - 前端 → 后端 ✅
  - 后端 → 数据库 ✅
  - 别人 → 数据库 ❌
  - 别人 → Redis ❌
  - Pod → metadata server ❌
```

## 📜 基础 manifest

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-isolation
  namespace: prod
spec:
  # 选择此 NP 应用到哪些 Pod
  podSelector:
    matchLabels:
      app: postgres

  # 入口：哪些流量能进来
  policyTypes:
  - IngressPolicy
  - EgressPolicy

  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api              # 只允许 api Pod 访问
    - namespaceSelector:
        matchLabels:
          ns: prod             # 且只允许 prod ns
    ports:
    - port: 5432
      protocol: TCP
```

## 🔀 流量方向

| 类型 | 含义 |
|------|------|
| `IngressPolicy` | 入口流量（谁可以访问我） |
| `EgressPolicy` | 出口流量（我可以访问谁） |

| 行为 | 含义 |
|------|------|
| 默认 allow | 没有匹配 NP 规则 → 放行（默认行为） |
| `policyTypes` 列出 + 有规则 | 命中规则才放，其他全部拒绝 |
| 多个 NP 累加 | OR 关系（任一放行即放） |

⚠️ **注意**：NP 是"白名单 + 黑名单"，**列出 policyTypes 即拒绝一切未列出的**。

## 🛠 实战

### 1. 拒绝所有 Pod 互通（默认 deny）

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: prod
spec:
  podSelector: {}               # 选所有 Pod
  policyTypes:
  - IngressPolicy
  - EgressPolicy
  # 不写任何规则 → 全部拒绝
```

### 2. 允许某 Pod 互访

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-to-db
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
  - IngressPolicy
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: api
    ports:
    - port: 5432
```

### 3. 允许 DNS（重要！）

```yaml
# 所有 Pod 都需要 DNS，否则连 apiserver 都连不上
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
spec:
  podSelector: {}
  policyTypes:
  - EgressPolicy
  egress:
  - to:
    - namespaceSelector: {}     # kube-system
    - podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - port: 53
      protocol: UDP
    - port: 53
      protocol: TCP
```

### 4. 同 namespace 内允许（默认 deny 之后）

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-intra-ns
spec:
  podSelector: {}
  policyTypes:
  - IngressPolicy
  ingress:
  - from:
    - podSelector: {}            # 同 ns 内所有 Pod
```

### 5. 允许 Ingress Controller 进入

```yaml
ingress:
- from:
  - namespaceSelector:
      matchLabels:
        kubernetes.io/metadata.name: ingress-nginx
```

## 🧪 验证

```bash
# 装网络插件
# Calico / Cilium / Weave Net（k8s 自带 NetworkPolicy 资源定义，但不实现）
# 必须装一个 CNI 才能让 NP 生效

# 装测试工具
kubectl run nettest --rm -it --image=alpine --restart=Never -- sh

# 在 nettest 容器内
nc -z <target-svc> 5432
# 通 → 没阻止；不通 → 阻止
```

## 🩹 故障

```bash
# 服务突然不通
# 1. 是不是新加了 NetworkPolicy
kubectl get networkpolicy -A
# 2. 是不是 CNI 没实现 NP（k8s 自带只定义）
kubectl -n kube-system get pods | grep -E 'calico|cilium|weave'
# 3. 测试
kubectl run nettest --rm -it --image=alpine --restart=Never -- nc -zv <svc> <port>
```

## 🆚 NetworkPolicy vs 服务网格

| | NetworkPolicy | Istio AuthorizationPolicy |
|--|---------------|---------------------------|
| 层级 | L3/L4（IP/port） | L7（HTTP header / path） |
| 性能开销 | 极低 | 中（sidecar 拦截） |
| 配置 | k8s 自带 CRD | 需装 Istio |
| 适合 | 简单隔离 | 细粒度 / 多协议 |

## 🔗 下一步

- [Service 三种类型](/04-k8s-service/service)
- [Istio 核心](/08-service-mesh/istio)
- [RBAC](/11-security/rbac)