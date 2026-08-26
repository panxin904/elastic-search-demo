---
title: Secret 管理
---

# Secret 管理

Secret（密钥 / 凭证 / Token）是 Pipeline 中最敏感的资源。本章梳理 Secret 全生命周期管理。

## 一句话总结

> **Secret 管理 = Vault 化 + OIDC 化 + 轮换化**。**核心：避免明文 + 最小权限 + 自动轮换 + 审计追溯**。

---

## 4 大原则

```
1. 永不提交到 Git
   - Pre-commit hook 检测
   - GitHub Secret Scanning 自动报警

2. 最小权限
   - 每个 Secret 只授予必要权限
   - 短期凭证（OIDC / STS）优于长期

3. 自动轮换
   - 数据库密码 90 天
   - API Token 60 天
   - SSH Key 180 天

4. 完整审计
   - 谁 + 何时 + 用哪个 Secret + 做了什么
   - 失败告警（异常访问）
```

## Secret 类型与方案

| 类型 | 推荐方案 |
|------|----------|
| **数据库密码** | HashiCorp Vault + 动态凭证 |
| **云厂商凭证** | OIDC / IAM Role（推荐）/ 短期 STS |
| **API Token** | Vault / 云厂商 Secret Manager |
| **SSH Key** | HashiCorp Vault SSH 签名 |
| **TLS 证书** | cert-manager + Vault PKI |
| **容器镜像 push** | Image Pull Secret（K8s）/ OIDC |

## HashiCorp Vault 集成

```bash
# Vault 启动（dev 模式）
vault server -dev

# 启用 K8s auth
vault auth enable kubernetes

# 配置 K8s auth
vault write auth/kubernetes/config \
  kubernetes_host="https://k8s-api.example.com"

# 创建 Secret
vault kv put secret/myapp \
  db_password=xxx \
  api_key=yyy
```

```yaml
# Vault Agent Injector（Sidecar 自动注入）
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "myapp"
    vault.hashicorp.com/agent-inject-secret-db: "secret/data/myapp"
    vault.hashicorp.com/agent-inject-template-db: |
      {{- with secret "secret/data/myapp" -}}
      export DB_PASSWORD="{{ .Data.data.db_password }}"
      {{- end }}
spec:
  template:
    metadata:
      annotations:
        vault.hashicorp.com/agent-inject: "true"
    spec:
      serviceAccountName: myapp
      containers:
        - name: myapp
          image: myapp:v1.0
          env:
            - name: DB_PASSWORD
              value: /vault/secrets/db
```

## AWS Secrets Manager

```python
import boto3

client = boto3.client('secretsmanager')

# 读取
response = client.get_secret_value(SecretId='myapp/db')
password = response['SecretString']

# 自动轮换
response = client.rotate_secret(
    SecretId='myapp/db',
    RotationRules={'AutomaticallyAfterDays': 30}
)
```

## K8s Secret（最简方案）

```bash
# 创建
kubectl create secret generic myapp-secret \
  --from-literal=db-password=xxx \
  --from-literal=api-key=yyy

# 使用
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: myapp-secret
        key: db-password
```

```yaml
# External Secrets Operator（从 Vault/AWS 同步）
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: myapp-secret
spec:
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: myapp-secret
  data:
    - secretKey: db-password
      remoteRef:
        key: secret/myapp
        property: db_password
```

## Secret 扫描

```yaml
# GitHub Secret Scanning（自动）
# https://docs.github.com/en/code-security/secret-scanning

# Pre-commit hook（本地拦截）
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

```bash
# gitleaks（CI 拦截）
gitleaks detect --source . --verbose
```

## 轮换策略

```yaml
# 1. 数据库密码
- Vault 动态凭证：自动生成 + 自动撤销
- 传统方案：每 90 天强制轮换 + 应用启动重连

# 2. API Token
- 短期（< 1 小时）：OAuth / OIDC
- 中期（< 90 天）：Token 刷新机制
- 长期（> 90 天）：必须强制轮换

# 3. SSH Key
- 短期：Vault SSH 签名（每次登录新 Key）
- 长期：定期重生成
```

## 关联章节

- **06-best-practices/secure-pipeline**：Pipeline 安全
- **06-best-practices/oidc-federation**：OIDC 联邦
- **security/03-crypto/secret-management** (security)：Secret 管理安全

## 一句话总结

> **Secret 管理 = 全生命周期**。**关键：避免明文 + 短期凭证 + 自动轮换 + 审计追溯**。**推荐：OIDC + Vault + External Secrets Operator**。


<!-- auto-enrich:do-not-edit -->

## 相关阅读

> TODO: 在此补充 3-5 个内部链接（指向同站其他页面）或外部参考。

示例：
- 同站首页
- 进阶话题
- 实战案例
- 参考资料

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
