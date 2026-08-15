---
title: Pulumi
---

# Pulumi

Pulumi 是 IaC 的现代化方案：用 TypeScript / Python / Go 等通用编程语言定义基础设施。

## 一句话总结

> **Pulumi = 编程语言 IaC**。**核心：通用语言 + 强类型 + 标准工具链（IDE / 测试 / 包管理）**。**强项：编程能力（循环 / 条件 / 函数）/ 测试友好**。**弱项：学习曲线 / 社区生态小于 Terraform**。

---

## 与 Terraform 对比

| 维度 | Terraform | Pulumi |
|------|-----------|--------|
| 语言 | HCL（DSL） | TypeScript / Python / Go / Java |
| 类型系统 | 弱类型 | 强类型（IDE 自动补全） |
| 测试 | terratest（Go） | 原生 unit test（用语言生态） |
| State | tfstate 文件 | Pulumi Service（云托管）+ 本地 |
| 复用 | Module + Terraform Registry | NPM / PyPI 包 + 任意语言 |
| 多云 | Provider 生态（成熟） | Provider（覆盖主流但较少） |
| 学习曲线 | 低（HCL 易学） | 中（需编程能力） |

## 完整示例：TypeScript

```typescript
import * as aws from "@pulumi/aws";
import * as pulumi from "@pulumi/pulumi";

const config = new pulumi.Config();
const environment = config.require("environment");

// VPC
const vpc = new aws.ec2.Vpc("main", {
    cidrBlock: "10.0.0.0/16",
    tags: { Environment: environment },
});

// Subnet
const subnet = new aws.ec2.Subnet("public", {
    vpcId: vpc.id,
    cidrBlock: "10.0.1.0/24",
    availabilityZone: "us-east-1a",
});

// EC2
const web = new aws.ec2.Instance("web", {
    ami: "ami-0c55b159cbfafe1f0",
    instanceType: "t3.medium",
    subnetId: subnet.id,
    tags: { Name: `web-${environment}` },
});

export const instanceIp = web.publicIp;
export const vpcId = vpc.id;
```

## 编程能力示例

```typescript
// 循环创建多 AZ subnet
const azs = ["us-east-1a", "us-east-1b", "us-east-1c"];
const subnets = azs.map((az, i) =>
    new aws.ec2.Subnet(`subnet-${az}`, {
        vpcId: vpc.id,
        cidrBlock: `10.0.${i + 1}.0/24`,
        availabilityZone: az,
    })
);

// 函数封装复用
function createWebServer(name: string, port: number) {
    return new aws.ec2.Instance(name, { /* ... */ });
}

const webServers = ["api", "worker", "scheduler"]
    .map(name => createWebServer(name, 8080));

// 条件
const enableLogging = config.getBoolean("logging") ?? true;
if (enableLogging) {
    new aws.cloudwatch.LogGroup("app", { /* ... */ });
}
```

## 测试（Pulumi 强项）

```typescript
import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import "mocha";
import { expect } from "chai";
import { getStack, getStackOutputs } from "./test-utils";

describe("Infrastructure", () => {
    let stack: string;
    let outputs: Record<string, any>;

    before(async () => {
        stack = await getStack();
        outputs = await getStackOutputs(stack);
    });

    it("should have 3 subnets", async () => {
        expect(outputs.subnetCount).to.equal(3);
    });

    it("should have correct VPC CIDR", async () => {
        expect(outputs.vpcCidr).to.equal("10.0.0.0/16");
    });
});
```

## 工作流

```bash
# 安装
npm install -g @pulumi/pulumi

# 初始化
pulumi new aws-typescript

# 预览
pulumi preview

# 部署
pulumi up

# 销毁
pulumi destroy

# Stack（多环境）
pulumi stack init staging
pulumi stack init prod
pulumi stack select prod
```

## 关联章节

- **02-iac/terraform**：Terraform（HCL DSL）
- **02-iac/terraform-vs-pulumi**：详细对比
- **02-iac/ansible**：Ansible（配置管理）

## 一句话总结

> **Pulumi = 开发者友好的 IaC**。**何时用：团队有强编程能力 / 需要测试 / 想用 IDE 自动补全**。**何时不用：HCL 已足够 / 团队不想学编程**。
