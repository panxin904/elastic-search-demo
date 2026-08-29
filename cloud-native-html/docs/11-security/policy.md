---
title: NetworkPolicy + PodSecurity
---

# NetworkPolicy + PodSecurity - 深度防御

> 默认 k8s 集群内所有 Pod 互通 + 所有容器权限大。生产必须纵深防御。

## 🤔 为什么需要

```
❌ 默认行为：
  - 所有 Pod 互通（任意 ns）
  - 所有 Pod 可访问 kube-apiserver
  - 所有容器以 root 跑
  - 可挂载 hostPath
  - 可使用特权

✅ 纵深防御：
  - NetworkPolicy 限流量
  - PodSecurity / OPA 限容器行为
  - RBAC 限 API
  - Secret 管理 限凭据
```

## 🌐 NetworkPolicy

详见 [NetworkPolicy](/04-k8s-service/network-policy)。要点：

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-isolation
spec:
  podSelector:
    matchLabels: { app: db }
  policyTypes: [Ingress, Egress]
  ingress:
  - from:
    - podSelector: { matchLabels: { app: api } }
    ports: [{ port: 5432 }]
  egress:
  - to:
    - namespaceSelector: { matchLabels: { ns: kube-system } }
    - podSelector: { matchLabels: { k8s-app: kube-dns } }
    ports: [{ port: 53, protocol: UDP }]
```

⚠️ **必须装支持 NP 的 CNI**（Calico / Cilium / Weave）。k8s 自带只定义，不实现。

## 🛡 PodSecurity

### PodSecurityStandards（v1.25+ 内置）

```bash
# 在 namespace 上贴标签
kubectl label namespace prod pod-security.kubernetes.io/enforce=restricted
kubectl label namespace prod pod-security.kubernetes.io/audit=baseline
kubectl label namespace prod pod-security.kubernetes.io/warn=baseline
```

| Profile | 含义 |
|---------|------|
| `privileged` | 不限制 |
| `baseline` | 防常见漏洞（最小限制） |
| `restricted` | 严格（最安全的默认） |

### Pod SecurityContext

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure
spec:
  securityContext:
    runAsNonRoot: true                # 禁 root
    runAsUser: 1000                   # 强制非 root UID
    runAsGroup: 3000
    fsGroup: 2000
    fsGroupChangePolicy: OnRootMismatch
    supplementalGroups: [1001]
    seccompProfile:
      type: RuntimeDefault
    sysctls:
    - name: net.core.somaxconn
      value: "1024"
      unsafe: false
  containers:
  - name: app
    image: myapp:1.0
    securityContext:
      allowPrivilegeEscalation: false # 禁 setuid
      privileged: false              # 禁特权
      readOnlyRootFilesystem: true     # 根 FS 只读
      runAsNonRoot: true
      runAsUser: 1000
      capabilities:
        drop: [ALL]                   # 全部丢
        add: [NET_BIND_SERVICE]       # 只加需要的
      seccompProfile:
        type: RuntimeDefault
    volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
  - name: tmp
    emptyDir: {}
```

## 📦 OPA / Gatekeeper（更细粒度）

### Pod Security Admission（v1.25+ 默认）

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: PodSecurity
  configuration:
    apiVersion: pod-security.admission.config.k8s.io/v1beta1
    kind: PodSecurityConfiguration
    defaults:
      enforce: restricted
      enforce-version: latest
    exemptions:
      usernames: [system:serviceaccount:kube-system:cluster-autoscaler]
```

### OPA Gatekeeper（外部 policy 引擎）

```bash
# 装
helm install gatekeeper oci://openpolicyagent/gatekeeper \
  --namespace gatekeeper --create-namespace
```

```yaml
# ConstraintTemplate（规则模板）
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8scontainterlimits
spec:
  crd:
    spec:
      names:
        kind: K8sContainerLimits
  targets:
  - rego: |
      package main
      violation[{"msg": msg}] {
        container := input.review.object.spec.containers[_]
        not container.resources.limits.memory
        msg := sprintf("container %v 必须设 memory limits", [container.name])
      }
---
# Constraint（具体规则）
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sContainerLimits
metadata:
  name: must-set-limits
spec:
  match:
    kinds:
    - apiGroups: [""]
      kinds: ["Pod"]
  parameters: {}
```

## 🪜 Falco 运行时检测

详见 [Falco 运行时检测](/11-security/falco)。

## 🔐 Seccomp / AppArmor / SELinux

### Seccomp

```yaml
securityContext:
  seccompProfile:
    type: RuntimeDefault       # 默认白名单
    # type: Localhost           # 自定义（spec 里写）
    # type: Unconfined         # 不限制
```

### AppArmor（Ubuntu）

```yaml
apiVersion: v1
kind: Pod
metadata:
  annotations:
    container.apparmor.security.beta.kubernetes.io/app: runtime/default
spec:
  containers:
  - name: app
    image: myapp
```

### SELinux（RHEL）

```bash
# 在 Pod 跑命令（不推荐，仅特殊场景）
securityContext:
  seLinuxOptions:
    user: "1000"
    role: "system_r"
    type: "container_t"
```

## 🛡 runtime class（gVisor / Kata）

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: gvisor
handler: runsc
---
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      runtimeClassName: gvisor    # 用沙箱隔离
```

| Runtime | 隔离级别 | 性能开销 |
|---------|----------|----------|
| runc | 普通 | 0% |
| gVisor | 应用级沙箱 | ~10% |
| Kata Containers | VM 级 | ~30% |

## 🩹 故障

```bash
# Pod 失败：forbidden
kubectl describe pod
# Events: failed due to "violates PodSecurity "restricted:"

# 解决：
# 1. 临时放宽
kubectl label ns prod pod-security.kubernetes.io/enforce=baseline
# 2. 改 Pod 满足 restricted
#   - runAsNonRoot: true
#   - 不 hostPath
#   - 不 privileged
#   - readOnlyRootFilesystem: true
```

## 🆚 vs 其他方案

| | PodSecurity | OPA Gatekeeper | Kyverno |
|--|-------------|-----------------|---------|
| 复杂度 | 内置 | 中 | 中 |
| 策略语言 | 内置 3 个 level | Rego | YAML |
| 自定义 | ❌ | ✅ Rego 强大 | ✅ YAML 易 |
| 推荐 | 简单项目 | 复杂合规 | 简单合规 |

**生产推荐**：PodSecurity（baseline）+ Kyverno（业务规则）。

## 🛠 实战

```yaml
# 加 restricted 到 prod ns
apiVersion: v1
kind: Namespace
metadata:
  name: prod
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
```

```yaml
# 写符合 restricted 的 Pod
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure
  namespace: prod
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        seccompProfile: { type: RuntimeDefault }
      containers:
      - name: app
        image: myapp:1.0
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities: { drop: [ALL] }
        resources:
          requests: { cpu: 100m, memory: 128Mi }
          limits:   { cpu: 500m, memory: 256Mi }
        volumeMounts:
        - { name: tmp, mountPath: /tmp }
      volumes:
      - { name: tmp, emptyDir: {} }
```

## 🔗 下一步

- [RBAC](/11-security/rbac)
- [Secret 管理](/11-security/secret)
- [Falco 运行时检测](/11-security/falco)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud](https://java-px.bot.cd/cloud/):Spring Cloud 微服务
- [linux](https://java-px.bot.cd/linux/):Linux 内核基础
- [devops](https://java-px.bot.cd/devops/):DevOps 流程
