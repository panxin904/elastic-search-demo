---
title: Pulumi
date: 2026-08-15  # date-auto-injected
---

# Pulumi - 现代 IaC

> Pulumi = 用 **真实编程语言**（TS / Python / Go）写 IaC。比 Terraform 更灵活，状态更可控。

## 🤔 为什么用 Pulumi

```
Terraform HCL：
  ❌ 单独学 DSL（不是通用语言）
  ❌ 抽象能力弱（for / if 有限）
  ❌ 写复杂逻辑痛苦
  ❌ 测试要靠 Terratest

Pulumi：
  ✅ TypeScript / Python / Go / Java / C#
  ✅ 完整 IDE（跳转 / 重构 / 自动完成）
  ✅ 包管理（npm / pip / go mod）
  ✅ 单元测试原生支持
  ✅ 复用现有生态（lodash / axios / 等等）
  ✅ 状态自管（cloud / S3 / 任意后端）
```

## 🏗️ 架构

```
┌────────────────────────────┐
│  Program（Pulumi 代码）       │
│  import * as aws from "@pulumi/aws" │
│  const bucket = new aws.s3.Bucket(...) │
└──────────┬─────────────────┘
           │ pulumi up
           ▼
┌────────────────────────────┐
│  Pulumi Engine               │
└──────┬──────────┬──────────┘
       │          │
   ┌───▼───┐  ┌───▼─────────┐
   │Cloud  │  │  State backend │
   │API    │  │ (Pulumi cloud) │
   └───────┘  └──────────────┘
```

| 概念 | 含义 |
|------|------|
| **Stack** | 一组资源的集合（一个环境） |
| **Resource** | 单个资源（aws.s3.Bucket） |
| **Output** | 导出值（IP / Endpoint） |
| **StackReference** | 跨 Stack 引用 |
| **State** | 部署状态（云后端默认） |

## 📜 基础（TypeScript）

```typescript
// index.ts
import * as aws from "@pulumi/aws";
import * as pulumi from "@pulumi/pulumi";

// 资源
const bucket = new aws.s3.Bucket("myapp-bucket", {
  bucket: "myapp-prod-data",
  versioning: { enabled: true },
  tags: { Environment: "prod" }
});

// 变量
const config = new pulumi.Config();
const environment = config.require("environment");

// 输出
export const bucketName = bucket.bucket;
export const bucketArn = bucket.arn;

// 引用其他 Stack
const network = new pulumi.StackReference("network");
const vpcId = network.getOutput("vpcId");
```

## 🔧 命令

```bash
# 装 CLI
curl -fsSL https://get.pulumi.com | sh

# 登录 Pulumi Cloud（免费）
pulumi login

# 新项目
mkdir my-pulumi && cd my-pulumi
pulumi new aws-typescript

# 改 .ts
# ...

# 看
pulumi preview                     # dry-run
pulumi up                         # 应用
pulumi stack output               # 看 output
pulumi stack ls                    # 列 Stack
pulumi destroy                    # 删所有
```

## 🌟 vs Terraform

| | Terraform | Pulumi |
|--|------------|--------|
| 语言 | HCL（DSL） | TS / Python / Go |
| 状态 | 自己管（S3 等） | Pulumi Cloud（托管） |
| 抽象 | 弱 | 强（可写函数 / 类） |
| 测试 | Terratest / 外部 | 内置（mocha / jest） |
| 生态 | 巨大 | 快速增长 |
| 学习曲线 | 平（专门 DSL） | 需懂语言 |
| 适合 | 团队 / 多云 | 开发者体验 |

**生产**：两者都很强。Terraform 生态大；Pulumi DX 好。

## 🪜 高级特性

### Component（自封装）

```typescript
class WebApp extends pulumi.ComponentResource {
  constructor(name: string, args: WebAppArgs, opts?) {
    super("custom:webapp", name, args, opts);

    // 自动建 deployment + service + ingress
    const deploy = new k8s.apps.v1.Deployment(`${name}-deploy`, { ...args.spec }, { parent: this });
    const svc = new k8s.core.v1.Service(`${name}-svc`, { ...args.spec }, { parent: this });

    this.registerOutputs({ serviceName: svc.metadata.name });
  }
}

// 用
new WebApp("web", {
  spec: { ... },
  image: "myapp:1.0"
});
```

### Stack 引用（跨环境）

```typescript
// base 栈
export const vpcId = vpc.id;

// dev 栈
const base = new pulumi.StackReference("base");
const vpcId = base.getOutput("vpcId");
const subnets = base.getOutput("subnetIds");
```

### Policy as Code（OPA）

```typescript
// 检查所有 S3 bucket 都开了 versioning
const policy: PolicyPack = {
  policies: [{
    name: "s3-versioning-required",
    validateStack: async (args) => {
      // ... 校验
    }
  }]
};
pulumi preview --policy-pack
```

## 🛠 实战

### 1. 创建 k8s Deployment

```typescript
import * as k8s from "@pulumi/kubernetes";

new k8s.apps.v1.Deployment("web", {
  metadata: { namespace: "prod", labels: { app: "web" } },
  spec: {
    replicas: 3,
    selector: { matchLabels: { app: "web" } },
    template: {
      metadata: { labels: { app: "web" } },
      spec: {
        containers: [{
          name: "web",
          image: "nginx:1.25-alpine",
          ports: [{ containerPort: 80 }]
        }]
      }
    }
  }
});
```

```bash
# 装 k8s provider
npm install @pulumi/kubernetes

# 跑
pulumi up
```

### 2. 跨 Stack 引用

```typescript
// infra/index.ts — 基础设施
const vpc = new awsx.ec2.Vpc("main", { cidrBlock: "10.0.0.0/16" });
export const vpcId = vpc.id;

// app/index.ts — 应用
import * as pulumi from "@pulumi/pulumi";
const infra = new pulumi.StackReference("infra");
const vpcId = infra.getOutput("vpcId");
const sg = new aws.ec2.SecurityGroup("app", { vpcId, ... });
```

## 🆚 vs Crossplane

| | Pulumi | Crossplane |
|--|---------|------------|
| 风格 | 通用 IaC | k8s 风格（CRD） |
| 运行 | Pulumi Engine | k8s operator |
| 适合 | 传统云资源 | k8s + 云服务都管 |

## 🩹 故障

```bash
# Preview / Apply 失败
pulumi preview --logtostderr -v=9    # 详细日志

# 状态损坏
pulumi stack export > backup.json
# 重建
pulumi stack import < backup.json

# 凭据
pulumi config set aws:region us-east-1
```

## 🔗 下一步

- [Terraform](/10-iac/terraform)
- [Helmfile / Kustomize](/10-iac/helmfile)
- [GitOps 思想](/09-cicd/gitops)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [cloud](https://java-px.bot.cd/cloud/):Spring Cloud 微服务
- [linux](https://java-px.bot.cd/linux/):Linux 内核基础
- [devops](https://java-px.bot.cd/devops/):DevOps 流程
