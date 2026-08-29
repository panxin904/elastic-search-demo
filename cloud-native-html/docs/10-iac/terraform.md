---
title: Terraform
date: 2026-08-15  # date-auto-injected
---

# Terraform - 基础设施即代码

> HashiCorp 出品，**IaC 事实标准**。声明式描述基础设施 → 计划 → apply。

## 🤔 为什么用 Terraform

```
手点云控制台：
  ❌ 不可复现（10 个环境就要点 10 次）
  ❌ 难审计 / 回滚
  ❌ 易错（漏改 / 配错）
  ❌ 团队协作难

Terraform：
  ✅ 全部基础设施写成 .tf 文件
  ✅ `terraform plan` 预览改了什么
  ✅ `terraform apply` 一键部署
  ✅ 状态存后端（S3 / consul / tfcloud）
  ✅ 团队共享 state（lock）
  ✅ 模块化（module）
```

## 🏗️ 架构

```
┌─────────────┐
│   .tf 文件   │  声明式：想成什么样
└──────┬──────┘
       │ terraform plan
       ▼
┌─────────────┐
│   state     │  当前实际状态
└──────┬──────┘
       │ diff
       ▼
┌────────────────────┐
│  Provider / API    │  AWS / GCP / K8s / Vault
└────────────────────┘
```

| 概念 | 含义 |
|------|------|
| **Resource** | 声明资源（aws_instance / kubernetes_pod） |
| **Provider** | 调哪个 API（AWS / K8s / GitHub） |
| **State** | 当前实际状态（要共享） |
| **Module** | 复用的 .tf 包 |
| **Output** | 输出值（其他 tf 用） |
| **Variable** | 参数 |

## 📜 基础

```hcl
# main.tf
terraform {
  required_version = ">= 1.6"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "myapp" {
  bucket = "myapp-prod-data"

  tags = {
    Environment = "prod"
    Team = "platform"
  }
}

# 变量
variable "region" {
  default = "us-east-1"
}

# 输出
output "bucket_name" {
  value = aws_s3_bucket.myapp.bucket
}

# 模块
module "vpc" {
  source = "./modules/vpc"
  cidr_block = "10.0.0.0/16"
}
```

## 🔧 命令

```bash
terraform init                   # 装 provider / 后端
terraform fmt                   # 格式化
terraform validate              # 语法
terraform plan                  # 看会改什么（干跑）
terraform apply                 # 真改（会确认）
terraform apply -auto-approve   # 跳过确认
terraform destroy              # 全删（生产慎用）
terraform output               # 看 output
terraform state list            # 列 state
terraform state show aws_s3_bucket.myapp

# workspace
terraform workspace new dev
terraform workspace select dev
terraform workspace list

# 格式化 + 安全扫描
terraform fmt -check
tfsec .                        # 静态安全检查
checkov -d .                   # 商业级扫描
```

## 🗃 State 后端

```hcl
# 远程 state（S3）
terraform {
  backend "s3" {
    bucket = "my-tfstate"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "tf-locks"   # 加锁
  }
}

# 远程 state（k8s 也能存）
# 多个环境用不同 key
# dev     → state/dev/terraform.tfstate
# staging → state/staging/terraform.tfstate
# prod    → state/prod/terraform.tfstate
```

## ☁️ 拉 k8s 资源

```hcl
# 装 provider
terraform {
  required_providers {
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.0" }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

# 直接写
resource "kubernetes_namespace" "demo" {
  metadata { name = "demo" }
}

resource "kubernetes_deployment" "web" {
  metadata {
    name      = "web"
    namespace = kubernetes_namespace.demo.metadata[0].name
    labels = { app = "web" }
  }
  spec {
    replicas = 3
    selector {
      match_labels = { app = "web" }
    }
    template {
      metadata { labels = { app = "web" } }
      spec {
        container {
          name  = "web"
          image = "nginx:1.25-alpine"
          port { container_port = 80 }
        }
      }
    }
  }
}
```

## 🔄 完整 CI/CD

```
1. 改 .tf
2. PR → terraform plan (输出 plan 到 PR 评论)
3. merge → terraform apply (CI 自动跑)
4. State 存远端
```

GitHub Actions 例：

```yaml
# .github/workflows/tf-plan.yaml
name: tf-plan
on: [pull_request]
jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: hashicorp/setup-terraform@v2
    - run: terraform init
    - run: terraform plan -no-color
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## 🩹 故障

```bash
# state 损坏
terraform state pull > state.json
# 人工修（小心）
terraform state rm aws_s3_bucket.bad
terraform apply

# 资源被人在控制台删了（state 不同步）
terraform plan                  # 看出 recreate
terraform apply                # 重建

# 锁卡住
terraform force-unlock <id>

# 凭据过期
# 用 IAM Role / OIDC（不存 access key）
```

## 🔐 安全最佳实践

```hcl
# 1. 远端 state（必须）
backend "s3" { ... }

# 2. 加密敏感变量
variable "db_password" {
  type      = string
  sensitive = true
}

# 3. 用 OIDC / IAM Role 替代 static key
provider "aws" {
  assume_role_with_web_identity {
    role_arn = "arn:aws:iam::xxx:role/xxx"
  }
}

# 4. 模块化 + 版本
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"
}

# 5. 远程执行前 dry-run
terraform plan -out=tfplan
terraform apply tfplan
```

## 🆚 vs Ansible / Pulumi / Helm

| | Terraform | Ansible | Pulumi | Helm |
|--|-----------|---------|---------|------|
| 状态 | 声明式 | 过程式 | 声明式 | 模板 |
| 范围 | 全栈（云 / 网络 / DNS / k8s） | 配置管理 | 全栈 | k8s 包 |
| 语言 | HCL | YAML | TS / Python / Go | YAML |
| 适合 | 基础设施 | 配置 / 部署 | 复杂 IaC | 应用包 |

**生产组合**：Terraform 管基础设施，Helm / Kustomize 管应用，ArgoCD 同步。

## 🛠 实战

```bash
# 1. 装
brew install terraform   # macOS
# 或
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo apt-key add -
sudo apt-add-repository "deb [arch=amd64] https://apt.releases.hashicorp.com $(lsb_release -cs) main"
sudo apt update && sudo apt install terraform

# 2. 写
mkdir my-tf && cd my-tf
cat > main.tf <<'EOF'
terraform { required_providers { local = { source = "hashicorp/local" } } }
provider "local" {}
resource "local_file" "hello" { content = "Hello World" filename = "hello.txt" }
EOF

# 3. 跑
terraform init
terraform plan
terraform apply
ls hello.txt
```

## 🔗 下一步

- [Pulumi](/10-iac/pulumi)
- [Helmfile / Kustomize](/10-iac/helmfile)
- [GitOps 思想](/09-cicd/gitops)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud](https://java-px.bot.cd/cloud/):Spring Cloud 微服务
- [linux](https://java-px.bot.cd/linux/):Linux 内核基础
- [devops](https://java-px.bot.cd/devops/):DevOps 流程
