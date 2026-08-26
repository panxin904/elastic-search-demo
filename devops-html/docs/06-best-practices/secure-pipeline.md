---
title: 安全 Pipeline
---

# 安全 Pipeline

CI/CD Pipeline 本身是攻击面最大的目标之一（拥有生产部署权限）。本章梳理 Pipeline 全链路的 8 大安全措施。

## 一句话总结

> **Pipeline 安全 = SLSA + 最小权限 + 可审计**。**核心：Secret 管理 / OIDC 联邦 / SBOM / 镜像签名 / 制品完整性**。

---

## 8 大安全措施

```
1. Secret 管理（HashiCorp Vault / AWS Secrets Manager）
2. OIDC 联邦（消除 long-lived Secret）
3. SBOM 生成（CycloneDX / SPDX）
4. 镜像签名（Cosign / Notary）
5. 依赖扫描（Snyk / Trivy / npm audit）
7. SLSA Level 3（来源可追溯）
8. 最小权限 Runner（专用 runner 隔离）
```

## 1. Secret 管理

```yaml
# ❌ 反模式：Secret 明文写在 YAML
env:
  AWS_ACCESS_KEY: AKIAIOSFODNN7EXAMPLE
  AWS_SECRET_KEY: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# ✅ 正确：使用 Secret Manager
env:
  AWS_ROLE_ARN: arn:aws:iam::123456789012:role/GitHubActionsRole
  # AWS 自动生成临时凭证，无 long-lived Secret
```

## 2. OIDC 联邦

```yaml
# GitHub Actions OIDC
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/GitHubActionsRole
      aws-region: us-east-1
```

```json
// IAM Role Trust Policy
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:sub": "repo:myorg/myapp:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

```yaml
# GitLab CI OIDC
deploy:
  id_tokens:
    GITLAB_OIDC_TOKEN:
      aud: https://vault.example.com
  script:
    - export VAULT_TOKEN=$(vault login -method=oidc role=my-role)
    - vault kv get -format=json secret/myapp
```

## 3. SBOM 生成

```yaml
# GitHub Actions 生成 SBOM
- name: Generate SBOM
  uses: anchore/sbom-action@v0
  with:
    format: cyclonedx-json
    artifact-name: sbom.json

# 上传到 Dependency Track / Grype
- uses: anchore/scan-action@v3
  with:
    sbom: sbom.json
    fail-build: true
    severity-cutoff: high
```

## 4. 镜像签名（Cosign）

```bash
# 构建并签名
cosign sign --key cosign.key myapp:v1.0.0

# 部署前验证
cosign verify --key cosign.pub myapp:v1.0.0

# K8s 强制验证（policy-controller）
kubectl apply -f - <<EOF
apiVersion: policy.sigstore.dev/v1beta1
kind: ClusterImagePolicy
metadata:
  name: my-policy
spec:
  images:
    - glob: "registry.example.com/**"
  authorities:
    - keyless:
        url: https://fulcio.sigstore.dev
        identities:
          - issuer: "https://token.actions.githubusercontent.com"
            subject: "https://github.com/myorg/*"
EOF
```

## 5. 依赖扫描

```yaml
# Snyk
- uses: snyk/actions/node@master
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
  with:
    args: --severity-threshold=high

# Trivy（容器 + IaC）
- uses: aquasecurity/trivy-action@master
  with:
    image-ref: myapp:v1.0.0
    severity: 'CRITICAL,HIGH'
    exit-code: '1'
    ignore-unfixed: true

# npm audit
- run: npm audit --audit-level=high
```

## 6. Pipeline 自身加固

```yaml
# 1. PR 触发（不能直接 push main）
on:
  pull_request:
  push:
    branches: [main]

# 2. 限制环境变量可见性
env:
  PUBLIC_VAR: value       # 暴露给 fork PR
  SECRET_VAR: ${{ secrets.X }}  # 不暴露给 fork PR

# 3. 第三方 action 锁定版本
- uses: actions/checkout@v4.1.7  # 不用 @v4（防止供应链攻击）
  # 或 hash
- uses: actions/checkout@8e5e7c5c8b36f4fa9bb1e0a5e9a8c8b8b8b8b8b8
```

## 7. SLSA Level 3

```yaml
# SLSA = Supply-chain Levels for Software Artifacts
# Level 3 要求：
# - 构建过程可追溯
# - 构建环境隔离
# - 产物签名 + provenance

# GitHub Actions 自动生成 provenance
- uses: actions/attest-build-provenance@v1
  with:
    subject-name: myapp
    subject-digest: sha256:abc...
```

## 8. 最小权限 Runner

```yaml
# 1. 自托管 Runner 隔离网络
runs-on: [self-hosted, isolated, prod-deploy]

# 2. 不同环境用不同 Runner
- production: 仅部署，不能访问源码
- staging: 可访问源码，可部署 staging
- ci: 可访问所有仓库

# 3. Runner 定期轮换 Token
```

## 关联章节

- **06-best-practices/secrets-management**：Secret 管理深度
- **06-best-practices/oidc-federation**：OIDC 联邦
- **04-network/tls-pki** (security)：TLS / PKI

## 一句话总结

> **Pipeline 安全 = 8 大措施闭环**。**优先级：Secret 管理 → OIDC → SBOM → 签名 → 依赖扫描 → SLSA → Runner 隔离**。


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

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
