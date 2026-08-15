---
title: OIDC 联邦
---

# OIDC 联邦（CI/CD ↔ 云厂商）

OIDC 联邦让 CI/CD Pipeline（GitHub / GitLab）无需 long-lived Secret 就能访问云厂商（AWS / GCP / Azure），是现代 Secret 管理的最佳实践。

## 一句话总结

> **OIDC 联邦 = 无长期凭证的云访问**。**核心：JWT Token 交换临时 STS**。**优势：消除长期 Secret / 自动过期 / 细粒度权限**。

---

## 为什么需要 OIDC 联邦

```
传统方式（❌ 危险）
  GitHub Secret 中存 AWS_ACCESS_KEY
  问题：
  - Secret 泄露 = 永久凭证泄露
  - 权限过大（无法按 repo / branch 限制）
  - 轮换困难（需要手动更新）

OIDC 联邦（✅ 推荐）
  GitHub Actions → 申请 JWT → 换 AWS STS（1 小时有效）
  优势：
  - 无 long-lived Secret
  - 按 repo / branch / tag 精确控制
  - 自动过期
```

## GitHub Actions → AWS OIDC

```yaml
# 1. AWS 创建 OIDC Provider（一次性）
# IAM → Identity providers → Add provider
# Provider URL: token.actions.githubusercontent.com
# Audience: sts.amazonaws.com

# 2. 创建 IAM Role（Trust Policy 限制 repo/branch）
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:myorg/myapp:ref:refs/heads/main"
        }
      }
    }
  ]
}

# 3. Pipeline 使用
permissions:
  id-token: write   # 必须
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123:role/GitHubActionsRole
      aws-region: us-east-1
  - run: aws s3 ls   # 已认证
```

## GitLab CI → Vault OIDC

```yaml
# GitLab 生成 OIDC Token
deploy:
  id_tokens:
    GITLAB_OIDC_TOKEN:
      aud: https://vault.example.com
  script:
    - |
      export VAULT_TOKEN=$(vault login -method=oidc -token-only \
        role=my-role \
        jwt=$GITLAB_OIDC_TOKEN)
    - vault kv get secret/myapp
```

```hcl
# Vault Role 配置
vault write auth/oidc/role/my-role \
  bound_audiences="https://vault.example.com" \
  user_claim="user_email" \
  policies="my-policy" \
  ttl=1h \
  max_ttl=4h
```

## GitHub Actions → GCP

```yaml
- id: auth
  uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: projects/123/locations/global/workloadIdentityPools/github/providers/github
    service_account: github-actions@myorg.iam.gserviceaccount.com
```

## GitHub Actions → Azure

```yaml
- uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
    enable-OIDC: true
```

## 多云 / 多账号最佳实践

```yaml
# 1. 不同环境不同 Role
permissions:
  id-token: write

steps:
  - if: github.ref == 'refs/heads/main'
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::PROD:role/Deploy
  - if: github.ref == 'refs/heads/develop'
    uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::STAGING:role/Deploy

# 2. 跨账号（生产部署）
# main → Prod Account
# develop → Staging Account

# 3. GitOps 风格（OIDC + ArgoCD）
# CI 不直接部署，只更新 manifest
# ArgoCD 用 OIDC 拉取 secret
```

## 权限最小化设计

```yaml
# IAM Role Policy（生产部署）
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage"
      ],
      "Resource": "arn:aws:ecr:us-east-1:123:repository/myapp"
    },
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster"
      ],
      "Resource": "arn:aws:eks:us-east-1:123:cluster/prod"
    }
  ]
}
```

## 常见误区

```
❌ 误区 1：OIDC 就能 100% 安全
✅ 正确：OIDC 消除了 long-lived Secret，但仍需 Trust Policy 限制

❌ 误区 2：Trust Policy 写宽（repo:* 任何分支）
✅ 正确：精确到 repo + branch（如 main）

❌ 误区 3：OIDC Role 给 AdministratorAccess
✅ 正确：最小权限（只给必要的 Action + Resource）

❌ 误区 4：OIDC Token 缓存复用
✅ 正确：每次 pipeline 重新申请，TTL 1 小时
```

## 关联章节

- **06-best-practices/secure-pipeline**：Pipeline 安全
- **06-best-practices/secrets-management**：Secret 管理
- **02-auth/oidc** (security)：OIDC 协议深度

## 一句话总结

> **OIDC 联邦 = 现代 Secret 管理的最佳实践**。**何时用：CI/CD 访问云资源 / 需要细粒度权限 / 想消除 long-lived Secret**。
