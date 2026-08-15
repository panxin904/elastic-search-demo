---
title: CKS 安全加固
---

# CKS 安全加固

> **C**ertified **K**ubernetes **S**ecurity **S**pecialist = CKA 升级版（加安全）。

## 📋 考试信息

| 项 | 详情 |
|----|------|
| 前提 | CKA 有效 |
| 时长 | 2 小时 |
| 题目 | ~15-20 道 |
| 费用 | ~$395 |
| 通过 | 67% |
| 通过 CKA 自动 50% off CKS |

## 🎯 CKS 范围

| 比重 | 主题 |
|------|------|
| **15%** | Cluster Setup（API server 鉴权 / 加密） |
| **15%** | Cluster Hardening（PodSecurity / NetworkPolicy） |
| **15%** | System Hardening（OS / SSH） |
| **20%** | Microservice Vulnerabilities（镜像扫描 / 运行时） |
| **20%** | Logging & Monitoring（Falco / Audit） |
| **15%** | TLS / 证书管理 |

## 🔥 高频考点

### 1. API Server 鉴权

```bash
# /etc/kubernetes/manifests/kube-apiserver.yaml
spec:
  containers:
  - command:
    - kube-apiserver
    - --authorization-mode=Node,RBAC          # 必开
    - --enable-admission-plugins=NodeRestriction
    - --anonymous-auth=false
    - --service-account-issuer=https://kubernetes.default.svc
```

### 2. 加密 etcd

```bash
# /etc/kubernetes/encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
    providers:
      - aescbc:
          keys:
            - name: key1
              secret: <base64>
      - identity: {}
```

### 3. PodSecurity 强制

```bash
kubectl label ns prod pod-security.kubernetes.io/enforce=restricted
```

或 PodSecurityAdmission：

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
```

### 4. NetworkPolicy 默认 deny + DNS

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
spec:
  podSelector: {}
  policyTypes: [IngressPolicy, EgressPolicy]
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-dns
spec:
  podSelector: {}
  policyTypes: [EgressPolicy]
  egress:
  - to:
    - namespaceSelector: {}
    - podSelector: { matchLabels: { k8s-app: kube-dns } }
    ports: [{ port: 53, protocol: UDP }, { port: 53, protocol: TCP }]
```

### 5. RBAC 最小权限

```bash
# 不能给 cluster-admin 给普通用户
kubectl create rolebinding alice-read \
  --clusterrole=view \
  --user=alice

# 限制 SA 自动挂 token
# Pod spec:
automountServiceAccountToken: false
```

### 6. Image 沙箱

```yaml
# PodSecurityContext
spec:
  securityContext:
    runAsNonRoot: true
    seccompProfile: { type: RuntimeDefault }
  containers:
  - name: app
    securityContext:
      allowPrivilegeEscalation: false
      privileged: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      capabilities: { drop: [ALL] }
      seccompProfile: { type: RuntimeDefault }
```

### 7. Falco 安装 + 规则

```bash
helm install falco falcosecurity/falco -n falco --create-namespace

# 写规则
cat > /etc/falco/falco_rules.local.yaml <<'EOF'
- rule: Read sensitive file
  condition: open_read and container and fd.name=/etc/shadow
  output: Sensitive file read
  priority: CRITICAL
  tags: [file]
EOF
```

### 8. mTLS（Istio）

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls: { mode: STRICT }
```

### 9. Trivy 镜像扫描

```bash
# 装
brew install trivy

# 扫镜像
trivy image nginx:1.25
trivy image --severity HIGH,CRITICAL myapp:1.0
trivy k8s cluster --report summary
```

### 10. Audit 日志

```bash
# audit-policy.yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: RequestResponse
  namespaces: ["prod"]
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
  verbs: ["create", "update", "delete"]

# 配 apiserver
- --audit-policy-file=/etc/kubernetes/audit-policy.yaml
- --audit-log-path=/var/log/kubernetes/audit.log
```

## 🪜 速记要点

| 主题 | 关键 |
|------|------|
| **API 鉴权** | `--authorization-mode=Node,RBAC` |
| **匿名访问** | `--anonymous-auth=false` |
| **PodSecurity** | `restricted` level |
| **NetworkPolicy** | default-deny + DNS allow |
| **etcd 加密** | `EncryptionConfiguration` |
| **镜像扫描** | Trivy |
| **运行时检测** | Falco |
| **审计** | audit policy + log path |
| **Secret 加密** | etcd 加密 + 不放 git |
| **SSH 加固** | `PermitRootLogin no` / `PasswordAuthentication no` |

## 🛠 实战

```bash
# 1. 装 kind
kind create cluster --name cks-lab

# 2. 装 strict pod admission
kubectl label ns default pod-security.kubernetes.io/enforce=restricted

# 3. 装 Falco
helm install falco falcosecurity/falco -n falco --create-namespace

# 4. 装 Trivy
brew install trivy
trivy image --severity HIGH,CRITICAL nginx:1.25

# 5. 配 NetworkPolicy default-deny
kubectl apply -f default-deny.yaml
```

## 🩹 考场注意

```
CKS 偏"安全加固"实操：
1. 看每题要求（"限制 root"/"加密 Secret"）
2. 改 Pod spec（加 securityContext）
3. 改 namespace label（加 enforcement）
4. 写 NetworkPolicy（allow + default-deny）
5. 配 NetworkPolicy / PodSecurity 时要验证
```

## 🔗 下一步

- [CKA 考试要点](/14-interview/cka)
- [高频面试题](/14-interview/questions)
- [RBAC](/11-security/rbac)