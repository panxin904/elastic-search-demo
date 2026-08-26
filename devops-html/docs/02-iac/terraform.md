---
title: Terraform
---

# Terraform

HashiCorp 推出的 IaC 工具，使用 HCL（HashiCorp Configuration Language）声明基础设施。是 IaC 行业事实标准。

## 一句话总结

> **Terraform = IaC 事实标准**。**核心：HCL + Provider 生态 + State 管理**。**强项：多云 / 模块化 / State 协作**。**弱项：HCL 不通用 / 状态管理复杂 / 商业化后部分功能需付费**。

---

## 核心模型

```
Provider       云厂商适配器（AWS / GCP / K8s / GitHub）
Resource       基础设施资源（aws_instance, kubernetes_pod）
Data Source    只读查询（aws_ami, data "terraform_remote_state"）
State          真实资源 ↔ 代码映射（terraform.tfstate）
Module         复用的资源集合
```

## 完整示例：AWS EC2

```hcl
terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
  backend "s3" {
    bucket = "myorg-tfstate"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
    dynamodb_table = "tfstate-lock"
  }
}

provider "aws" {
  region = "us-east-1"
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t3.medium"

  tags = {
    Name        = "web-${var.environment}"
    Environment = var.environment
  }
}

output "instance_ip" {
  value = aws_instance.web.public_ip
}
```

## Module 设计

```hcl
# modules/vpc/main.tf
resource "aws_vpc" "main" {
  cidr_block = var.cidr_block
}

resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.cidr_block, 8, count.index)
  availability_zone = data.aws_availability_zones.available.names[count.index]
}
```

```hcl
# 使用 module
module "vpc" {
  source      = "./modules/vpc"
  cidr_block  = "10.0.0.0/16"
  environment = var.environment
}
```

## State 管理

```bash
# 远程 State（S3 + DynamoDB Lock）
terraform {
  backend "s3" {
    bucket         = "myorg-tfstate"
    key            = "prod/vpc.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-lock"   # 防止并发
    encrypt        = true
  }
}

# 操作
terraform init      # 初始化（下载 provider / 配置 backend）
terraform plan      # 预览变更
terraform apply     # 执行
terraform destroy   # 销毁
terraform import    # 把现有资源导入 State
```

## State 协作

```hcl
# 跨项目共享数据
data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = "myorg-tfstate"
    key    = "shared/vpc.tfstate"
    region = "us-east-1"
  }
}

resource "aws_subnet" "app" {
  vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id
}
```

## 常用工作流

```bash
# 1. 工作区（多环境隔离）
terraform workspace new staging
terraform workspace new prod
terraform workspace select prod

# 2. 变量文件
terraform.tfvars
terraform.tfvars.staging
terraform.tfvars.prod

# 3. tfsec（安全扫描）
tfsec .

# 4. drift detection（生产建议定期 plan）
terraform plan -detailed-exitcode
```

## 关联章节

- **02-iac/pulumi**：Pulumi（编程语言 IaC）
- **02-iac/ansible**：Ansible（配置管理）
- **02-iac/terraform-vs-pulumi**：详细对比
- **03-gitops**：State 后端用 GitOps 模式管理

## 一句话总结

> **Terraform = 多云 IaC 的标准答案**。**何时用：多云 / 大规模基础设施 / 团队熟悉 HCL**。**何时不用：纯 K8s（用 Helm/Kustomize）/ 简单脚本（用 Pulumi/Python）**。


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
