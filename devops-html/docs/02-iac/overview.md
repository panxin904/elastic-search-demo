---
title: IaC 基础设施即代码 总览
date: 2026-08-15  # date-auto-injected
---

# IaC 总览

Infrastructure as Code 把"服务器 / 网络 / 数据库"从手工操作变成可版本化、可审计、可复用的代码。本章对比 4 大 IaC 工具的设计取舍。

## IaC 的 3 个流派

```
声明式 (Declarative)
  ├─ 你描述"目标状态"
  ├─ 工具自动 diff 并应用
  └─ 代表：Terraform / Pulumi / CloudFormation
命令式 (Imperative)
  ├─ 你写"具体步骤"
  ├─ 工具按顺序执行
  └─ 代表：Ansible / Shell / Chef
混合式
  ├─ 默认声明式 + 局部命令式
  └─ 代表：Pulumi（声明式 + 完整编程语言）
```

## 4 大工具横向对比

| 维度 | Terraform | Pulumi | Ansible | CloudFormation |
|------|-----------|--------|---------|----------------|
| **语言** | HCL（自有 DSL） | TypeScript / Python / Go | YAML | JSON / YAML |
| **状态管理** | state 文件 | state 文件（可远端） | 无状态 | 托管 |
| **执行模型** | Plan / Apply | Preview / Up | Playbook | Stack |
| **多云支持** | ★★★★★ | ★★★★ | ★★★ | AWS only |
| **K8s 支持** | Provider | Provider | Module | 不擅长 |
| **复用机制** | Module | Function / Class | Role | Nested Stack |
| **最佳场景** | 多云 / 复杂编排 | 强类型团队 / 编程习惯 | 配置管理 / 运维脚本 | AWS 单一云 |
| **学习曲线** | 中 | 中低 | 低 | 中 |

## Terraform vs Pulumi 核心差异

```hcl
# Terraform HCL：声明式 + 有限函数
resource "aws_s3_bucket" "logs" {
  bucket = "my-app-logs-${var.env}"
  acl    = "private"
}
```

```typescript
// Pulumi TypeScript：完整编程语言
import * as aws from "@pulumi/aws";
const logsBucket = new aws.s3.Bucket("logs", {
  bucket: `my-app-logs-${env}`,
  acl: "private",
});
```

| 维度 | Terraform | Pulumi |
|------|-----------|--------|
| **表达力** | HCL 限制（for / if / loop 勉强可用） | 完整语言（循环 / 抽象 / 类型） |
| **类型安全** | 弱（runtime error 多） | 强（编译期捕获） |
| **抽象能力** | Module + 输出变量 | Function / Class / 包管理 |
| **状态后端** | S3 / Consul / Terraform Cloud | Pulumi Cloud / S3 / Azure Blob |
| **供应商锁定** | 低（多云） | 中（Pulumi 自有 runtime） |

## IaC 黄金实践

1. **State 远端化**：本地 state 是反模式，必须用 S3 + DynamoDB 锁 / Pulumi Cloud / Terraform Cloud
2. **模块化**：把通用模式（VPC / RDS / IAM Role）封装为 Module，跨环境复用
3. **环境分离**：`prod` / `staging` / `dev` 用不同 state file 或 workspace，互不影响
4. **Drift 检测**：定期 `terraform plan` / `pulumi refresh`，对比实际状态与声明，发现未授权变更
5. **CI/CD 集成**：`terraform plan` 走 PR 评论，`terraform apply` 走 main 分支合并触发

## 选型决策树

```
Q1: 团队是否强类型背景？
  ├─ 是 → Pulumi（TS / Go / Python）
  └─ 否 → Terraform（HCL 学习成本低）

Q2: 多云还是单云？
  ├─ 多云 → Terraform（生态成熟）
  └─ 单云（AWS）→ CloudFormation（深度集成）

Q3: 是配置管理还是基础设施？
  ├─ 配置管理（apt install / 启停服务）→ Ansible
  └─ 基础设施（VPC / RDS / K8s）→ Terraform / Pulumi
```

## 关联章节

- **01-pipeline** → Pipeline 如何调用 IaC 工具
- **03-gitops** → IaC 状态文件如何进入 Git
- **06-best-practices/secrets-management** → Terraform 变量如何管理 Secrets


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
