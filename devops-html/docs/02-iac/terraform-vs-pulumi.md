---
title: Terraform vs Pulumi
---

# Terraform vs Pulumi

两个 IaC 工具的详细对比，帮团队选择合适的方案。

## 一句话总结

> **Terraform = 生态成熟 / HCL DSL**；**Pulumi = 编程语言 / 测试友好**。**决策点：团队编程能力 + 生态需求 + 测试要求**。

---

## 11 个维度对比

| 维度 | Terraform | Pulumi | 推荐场景 |
|------|-----------|--------|----------|
| **语言** | HCL（DSL） | TS / Python / Go / Java | Pulumi 适合编程团队 |
| **学习曲线** | 低 | 中 | Terraform 适合新手 |
| **类型系统** | 弱 | 强（IDE 补全） | Pulumi 适合大型项目 |
| **Provider 生态** | 3000+ | 150+ | Terraform 多云首选 |
| **State** | 多种 backend（S3/Terraform Cloud） | Pulumi Service / 本地 | Terraform 更灵活 |
| **复用** | Module + Registry | NPM / PyPI + 任意语言 | Pulumi 更通用 |
| **测试** | terratest（外置） | 原生 unit test | Pulumi 强 |
| **Plan/Preview** | terraform plan | pulumi preview | 都优秀 |
| **工具链** | terraform CLI | pulumi CLI + 语言工具 | Pulumi 用 IDE 工具 |
| **CI/CD 集成** | 简单（plan + apply） | 简单 | 都优秀 |
| **社区规模** | 大 | 中 | Terraform 文档丰富 |

## 代码示例对比

```hcl
# Terraform：创建 S3 bucket
resource "aws_s3_bucket" "logs" {
  bucket = "myorg-logs-${var.environment}"

  tags = {
    Environment = var.environment
    Owner       = "platform"
  }
}

# 创建多个 bucket（for_each）
resource "aws_s3_bucket" "logs" {
  for_each = toset(["app", "audit", "metrics"])

  bucket = "myorg-logs-${each.key}-${var.environment}"
}
```

```typescript
// Pulumi：创建 S3 bucket
import * as aws from "@pulumi/aws";

const buckets = ["app", "audit", "metrics"].map(name =>
    new aws.s3.Bucket(`logs-${name}`, {
        bucket: `myorg-logs-${name}-${environment}`,
        tags: { Environment: environment, Owner: "platform" },
    })
);

export const bucketNames = buckets.map(b => b.bucket);
```

## 选型决策树

```
Q1：团队是否熟悉编程？
  ├─ 是 → Pulumi（TS / Python / Go 都可以）
  └─ 否 → Terraform（HCL 易学）

Q2：需要多云管理（AWS / GCP / Azure 都有资源）？
  ├─ 是 → Terraform（Provider 生态最完整）
  └─ 否 → Pulumi 也可以

Q3：基础设施规模（> 100 资源 / > 50 模块）？
  ├─ 是 → Pulumi（编程语言抽象能力更强）
  └─ 否 → Terraform（够用）

Q4：是否需要单元测试 + CI 集成？
  ├─ 是 → Pulumi（原生测试框架）
  └─ 否 → Terraform（terratest 也能用）

Q5：是否已经在用 Terraform？
  ├─ 是 → 继续用（迁移成本高）
  └─ 否 → 新项目看上面 Q1-Q4
```

## 混合方案

```bash
# 常见模式：Terraform 管基础设施，Pulumi 管应用
# - Terraform：VPC / Subnet / IAM / EKS
# - Pulumi：应用 K8s manifest / ArgoCD Application

# 通过 data source 共享
# Terraform output
output "vpc_id" { value = aws_vpc.main.id }

# Pulumi 引用
const vpcId = require("./terraform-output").vpcId;
```

## 关联章节

- **02-iac/terraform**：Terraform 详情
- **02-iac/pulumi**：Pulumi 详情
- **02-iac/ansible**：Ansible（配置管理）

## 一句话总结

> **Terraform = 默认选择 / 生态优先**；**Pulumi = 编程团队 / 大规模项目 / 测试驱动**。**两者可共存：Terraform 管云基础设施，Pulumi 管应用层**。


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
