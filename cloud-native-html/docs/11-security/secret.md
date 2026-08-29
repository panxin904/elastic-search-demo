---
title: Secret 管理
---

# Secret 管理

> k8s Secret 默认**只 base64**，不加密。生产需要：加密、轮换、外部存储。

## 🤔 为什么需要 Secret 管理

```
❌ k8s Secret 默认：
  - etcd 里 base64 编码（可轻易解码）
  - 没有自动轮换
  - 没有审计

生产需要：
  - 加密 + 访问控制
  - 自动轮换
  - 集中管理
  - 审计
```

## 🛠 k8s 加密（最低限度）

### EncryptionConfiguration

```yaml
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
              secret: <base64-encoded-32-byte-key>
      - identity: {}
```

```bash
# 生成 key
head -c 32 /dev/urandom | base64

# 改 apiserver 启动参数
# --encryption-provider-config=/etc/kubernetes/encryption-config.yaml
sudo systemctl restart kube-apiserver

# 已有 Secret 不会被加密！要重新写：
kubectl get secrets --all-namespaces -o json | kubectl apply -f -

# 验证
kubectl get secret my-secret -o jsonpath='{.data.password}' | base64 -d
```

## 🏢 外部 Secret 管理

生产推荐：Secret 不进 etcd。

| 工具 | 特点 |
|------|------|
| **HashiCorp Vault** | 业界标准，动态密钥、租约 |
| **AWS Secrets Manager** | AWS 集成 |
| **GCP Secret Manager** | GCP 集成 |
| **Azure Key Vault** | Azure 集成 |
| **External Secrets Operator** | k8s 同步外部 secret |

### External Secrets Operator

```bash
# 装
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  --namespace external-secrets --create-namespace
```

```yaml
# SecretStore（连接 Vault）
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: prod
spec:
  provider:
    vault:
      server: https://vault.example.com
      path: secret/data/db
      version: v2
      auth:
        kubernetes:
          mountPath: kubernetes
          role: myapp
          serviceAccountRef:
            name: my-app
```

```yaml
# ExternalSecret（同步到 k8s Secret）
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-cred
  namespace: prod
spec:
  secretStoreRef:
    name: vault-backend
  target:
    name: db-cred
  data:
  - secretKey: password
    remoteRef:
      key: postgres-password
    property: password
```

```bash
# 看同步状态
kubectl get externalsecret db-cred -n prod
# 同步周期默认 1h（refreshInterval）
```

## 🛡 Vault 实战

### 装 Vault（生产 helm）

```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm install vault hashicorp/vault \
  --namespace vault --create-namespace
```

### 写 Secret

```bash
# 启用 kv-v2
vault secrets enable -path=secret kv-v2

# 写
vault kv put secret/myapp/db username=myapp password=secret

# 读
vault kv get secret/myapp/db
```

### k8s Auth Method

```bash
# Vault 端：开 k8s auth
vault auth enable kubernetes

vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc"

# 绑 role
vault write auth/kubernetes/role/myapp \
  bound_service_account_names=my-app \
  bound_service_account_namespaces=prod \
  policies=myapp-read
```

### 应用端：CSI / Sidecar 注入

```yaml
# Vault Agent Injector（自动注入 sidecar）
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "myapp"
    vault.hashicorp.com/agent-image: "hashicorp/vault:1.15"
    vault.hashicorp.com/db-config: |
      template: |
        {{- with secret "secret/data/myapp/db" -}}
        {{ .Data.data | toJSON }}
        {{- end }}
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
```

Pod 启动时 Vault Agent 注入 sidecar，把 secret 写到 `/vault/secrets/db`。

## 🔐 AWS Secrets Manager（生产托管）

```bash
# 写
aws secretsmanager create-secret \
  --name myapp/db \
  --secret-string '{"username":"myapp","password":"secret"}'

# 通过 ESO 同步
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-sm
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets
```

## 🔄 Secret 轮换

```bash
# Vault
vault write -f secret/myapp/db password=new-password

# k8s 自动同步
# ESO 定期轮询 / Vault Agent sidecar 监听

# 强制同步
kubectl annotate externalsecret db-cred force-sync=true --overwrite
```

## ⚠️ 不要

```yaml
# ❌ 写死 secret
env:
- name: DB_PASSWORD
  value: "secret123"

# ❌ Secret 在 git
git add .env
git commit -m "add secrets"

# ❌ 共享 token
# 给 100 个 pod 同一个 SA
```

## 🛠 实战

```bash
# 1. 装 External Secrets
helm install external-secrets external-secrets/external-secrets -n external-secrets --create-namespace

# 2. 配 SecretStore（Vault 为例）
# 写 secret-store.yaml 应用

# 3. 写 ExternalSecret
# 写 external-secret.yaml 应用

# 4. 验证同步
kubectl get externalsecret
# SYNCED 状态 = OK

# 5. 应用里引用
envFrom:
- secretRef:
    name: db-cred
```

## 🆚 方案对比

| | k8s Secret (加密) | Vault | AWS SM | ESO |
|--|-------------------|-------|--------|-----|
| 加密 | ✅（apiserver） | ✅ | ✅ | 取决于后端 |
| 动态轮换 | ❌ | ✅ | ✅ | ✅ |
| 租约 / TTL | ❌ | ✅ | ✅ | ✅ |
| 适合 | 小 / 测试 | 通用 | AWS | 多后端 |

## 🔗 下一步

- [RBAC](/11-security/rbac)
- [NetworkPolicy + PodSecurity](/11-security/policy)
- [Falco 运行时检测](/11-security/falco)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud](https://java-px.bot.cd/cloud/):Spring Cloud 微服务
- [linux](https://java-px.bot.cd/linux/):Linux 内核基础
- [devops](https://java-px.bot.cd/devops/):DevOps 流程
