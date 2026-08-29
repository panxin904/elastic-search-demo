---
title: AWS Lambda / GCP Cloud Run
date: 2026-08-15  # date-auto-injected
---

# 托管 Serverless

> 不用自己运维 K8s + Knative。直接用云厂商的 FaaS / 容器服务。

## 🤔 为什么用托管 Serverless

```
自建 K8s + Knative：
  ❌ 运维负担（etcd / control plane）
  ❌ 冷启动优化靠自己
  ❌ 多 region 部署靠自己

托管：
  ✅ 零运维
  ✅ 自动扩缩（0 → N → 0）
  ✅ 按调用计费
  ✅ 多 region 内置
```

## 🟠 AWS Lambda

> 事件驱动的 Function as a Service。

```yaml
# template.yaml (SAM)
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Resources:
  HelloFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: index.handler
      Runtime: nodejs20.x
      MemorySize: 512
      Timeout: 10
      CodeUri: ./src
      Events:
        ApiEvent:
          Type: Api
          Properties:
            Path: /hello
            Method: get
```

```js
// src/index.js
exports.handler = async (event) => {
  return { statusCode: 200, body: 'Hello!' };
};
```

```bash
# 部署
sam build
sam deploy --guided
```

### 触发源

| 触发 | 用途 |
|------|------|
| API Gateway / ALB | HTTP |
| S3 | 文件上传 |
| SNS / EventBridge | 事件总线 |
| SQS | 队列 |
| DynamoDB Stream | 库变更 |
| CloudWatch | 定时（Cron） |
| WebSocket | 实时双向 |

### 冷启动

```yaml
# Provisioned Concurrency（预留实例）
HelloFunction:
  Properties:
    ProvisionedConcurrencyConfig:
      ProvisionedConcurrentExecutions: 5    # 始终 5 个热实例
```

### 冷启动优化

- 编译（AOT）— 选 Provisioned Concurrency / SnapStart
- 减少依赖（树摇 / 懒加载）
- 容器镜像（Lambda Container Image）— 选 Alpine / distroless
- 静态初始化（DB 连接放外面）

## 🔵 GCP Cloud Run

> AWS Fargate / 阿里云 EDAS 的"无服务版"。

```bash
# 部署
gcloud run deploy web \
  --image=gcr.io/myorg/web:1.0 \
  --region=asia-east1 \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --concurrency=80 \
  --min-instances=0 \
  --max-instances=100
```

- 任何容器镜像（Dockerfile / Buildpacks）
- 自动 HTTPS / URL
- 缩到 0 / N
- 按请求计费
- 类似 Cloudflare Workers / Azure Container Apps

### Cloud Run Jobs（批处理）

```bash
gcloud run jobs create myjob \
  --image=gcr.io/myorg/job:1.0 \
  --region=us-central1 \
  --task-timeout=3600 \
  --max-retries=3
```

## 🔴 阿里云 / 腾讯云

| 厂商 | 服务 | 特点 |
|------|------|------|
| 阿里云 | 函数计算 FC / SAE | 事件 + 容器 |
| 阿里云 | ACK Serverless | Knative 包装 |
| 腾讯云 | SCF / TKE Serverless | 类似 |
| 华为云 | FunctionGraph | 自家产品 |
| AWS | Lambda / Fargate / App Runner | 完整 |

## 🆚 选型

| 场景 | 推荐 |
|------|------|
| 事件驱动函数 | Lambda |
| 容器 + 0 副本 | Cloud Run / Fargate / Knative |
| 多语言 / 旧代码迁移 | Cloud Run（容器） |
| AWS 深度整合 | Lambda |
| 不想锁定 / 内部部署 | Knative |

## 🪛 实战

### Lambda + S3 触发

```bash
# 写函数
echo 'exports.handler = async (e) => { console.log(e.Records[0].s3.bucket); }' > index.js
zip function.zip index.js

# 部署
aws lambda create-function \
  --function-name resize-image \
  --runtime nodejs20.x \
  --role arn:aws:iam::xxx:role/lambda-exec \
  --handler index.handler \
  --code fileb://function.zip

# 加 S3 触发
aws s3api put-bucket-notification-configuration \
  --bucket my-bucket \
  --notification-configuration file://trigger.json
```

```json
// trigger.json
{
  "LambdaFunctionConfigurations": [{
    "LambdaFunctionArn": "arn:aws:lambda:...",
    "Events": ["s3:ObjectCreated:*"]
  }]
}
```

## 🩹 故障

```bash
# Lambda 超时
# 解决：增加 timeout / 拆分函数 / 异步调用

# Lambda 内存不够
# 解决：增加 MemorySize（CPU 也跟着加）

# Cloud Run 启动慢
# 解决：min-instances=1 保活 / 减小镜像 / 静态优化
```

## 💰 计费对比

| | Lambda | Cloud Run | Knative（自建） |
|--|--------|------------|----------------|
| 计费 | 调用 + GB-秒 | 请求 + vCPU-秒 + GB-秒 | 自己机器费 |
| 空闲 | 0 | 0 | 0（缩到 0） |
| 适合 | 突发 / 不定流量 | 类似 | 自建 k8s |

## 🔗 下一步

- [Knative Serving](/12-serverless/knative)
- [Deployment](/03-k8s-workload/deployment)
- [HPA / 自动扩缩容（待补）]