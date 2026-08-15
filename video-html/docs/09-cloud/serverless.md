---
title: Serverless 视频处理
---

# Serverless 视频处理

<span class="kg-badge kg-badge-cloud">云服务</span>
<span class="kg-badge kg-badge-tools">函数计算</span>
<span class="kg-badge kg-badge-codec">转码</span>

Serverless 视频处理通过 **事件触发 + 函数计算** 实现按需伸缩、无需运维。

## 🎯 Serverless 视频优势

| 优势 | 说明 |
| --- | --- |
| **按量付费** | 按转码任务 / 时长计费 |
| **自动伸缩** | 突发流量自动扩容 |
| **零运维** | 无服务器管理 |
| **事件驱动** | 上传即处理 |
| **成本优化** | 闲时 0 费用 |

## 🏗️ 主流 Serverless 视频方案

| 云厂商 | 函数服务 | 视频服务 |
| --- | --- | --- |
| **AWS** | Lambda | MediaConvert |
| **阿里云** | 函数计算 FC | MPS + 阿里云 OSS |
| **腾讯云** | SCF | CI + COS |
| **Azure** | Functions | Media Services |
| **Google** | Cloud Functions | Transcoder API |

## 🚀 AWS Lambda + MediaConvert

### 架构

```
用户上传 → S3 (触发) → Lambda
                          ↓
                    创建 MediaConvert Job
                          ↓
                     MediaConvert 转码
                          ↓
                  SNS 完成回调 → Lambda
                          ↓
                  写入 DynamoDB / 通知前端
```

### S3 触发器

```json
{
  "LambdaFunctionConfigurations": [{
    "Events": ["s3:ObjectCreated:*"],
    "Filter": {
      "Key": {
        "FilterRules": [
          {"Name": "suffix", "Value": ".mp4"}
        ]
      }
    }
  }]
}
```

### Lambda 函数

```python
import json
import os
import boto3

mediaconvert = boto3.client(
    'mediaconvert',
    endpoint_url='https://xxx.mediaconvert.us-east-1.amazonaws.com'
)

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    response = mediaconvert.create_job(
        Role=os.environ['MEDIA_CONVERT_ROLE'],
        Settings={
            'Inputs': [{'FileInput': f's3://{bucket}/{key}'}],
            'OutputGroups': [
                # 1080p
                {'Name': '1080p', 'OutputGroupSettings': {...}, 'Outputs': [{...}]},
                # 720p
                {'Name': '720p', 'OutputGroupSettings': {...}, 'Outputs': [{...}]},
                # 480p
                {'Name': '480p', 'OutputGroupSettings': {...}, 'Outputs': [{...}]}
            ]
        }
    )
    return {'jobId': response['Job']['Id']}
```

## ⚙️ 阿里云函数计算 FC

### 配置 OSS 触发器

```yaml
trigger:
  type: oss
  config:
    bucket: my-bucket
    events:
      - oss:ObjectCreated:*
    filter:
      suffix:
        - .mp4
```

### 函数实现

```python
import json
import oss2
from aliyunsdkcore.client import AcsClient
from aliyunsdkmts.request.v20140618 import SubmitJobsRequest

def handler(event, context):
    evt = json.loads(event)
    bucket = evt['events'][0]['oss']['bucket']['name']
    key = evt['events'][0]['oss']['object']['key']

    # 提交 MPS 任务
    client = AcsClient(os.environ['AK'], os.environ['SK'], 'cn-shanghai')
    req = SubmitJobsRequest.SubmitJobsRequest()
    req.set_Input(f'oss://{bucket}/{key}')
    req.set_OutputBucket(bucket)
    req.set_Output('output/')
    req.set_PipelineId(1)

    return client.do_action_with_exception(req)
```

### 函数计算 + FFmpeg

```python
# 自定义 runtime 调用 FFmpeg 二进制
import subprocess
import oss2

def handler(event, context):
    # 下载到本地
    oss2.get_object_to_file(bucket, key, '/tmp/input.mp4')

    # 执行 FFmpeg
    subprocess.run([
        'ffmpeg', '-y', '-i', '/tmp/input.mp4',
        '-c:v', 'libx264', '-preset', 'fast',
        '-c:a', 'aac',
        '/tmp/output.mp4'
    ])

    # 上传结果
    oss2.put_object_from_file(bucket, 'output/output.mp4', '/tmp/output.mp4')

    return 'ok'
```

## 🐍 腾讯云 SCF

```python
from qcloud_cos_v5 import CosConfig, CosS3Client
from tencentcloud.mps.v20190612 import mps_client, models

def main_handler(event, context):
    # 解析 COS 事件
    evt = event['Records'][0]['cos']
    bucket = evt['cos']['bucket']['name']
    key = evt['cos']['object']['key']

    # 提交 MPS 转码
    client = mps_client.MpsClient(cred, "ap-shanghai")
    req = models.CreateWorkflowRequest()
    # ...
```

## 🎯 适用于 Serverless 的视频处理

### ✅ 适合

| 任务 | 原因 |
| --- | --- |
| **缩略图生成** | 短时执行、按量付费 |
| **格式转换** | 异步执行 |
| **水印添加** | 1-2 秒完成 |
| **元数据提取** | MediaInfo 解析 |
| **关键帧截图** | 一次性输出 |
| **AI 标签** | 调用 API 即可 |
| **字幕生成** | 转写文本 |

### ❌ 不太适合

| 任务 | 原因 |
| --- | --- |
| **长时间转码** | 函数 15min 上限 |
| **大型 AI 模型** | 显存受限 |
| **实时编码** | 无状态不适合 |

## ⚡ Lambda 限制与变通

### Lambda 限制

| 项 | 限制 |
| --- | --- |
| 超时 | 15 分钟（最大） |
| 内存 | 128MB - 10GB |
| 临时磁盘 | 512MB - 10GB |
| 并发 | 1000 (默认) |

### 长任务变通

**方案 1**：拆分为多个 Lambda
```python
# Lambda 1: 下载文件 + 启动 ffmpeg 子进程
# Lambda 2: 处理完成后清理
```

**方案 2**：Lambda 调用 Container（ECR）
- 嵌入大型容器镜像
- 视频处理脚本作为容器入口

**方案 3**：Lambda 调用 ECS / Fargate
- 长任务用 Fargate 更稳定
- 适合 30 分钟以上的转码

## 🌊 Lambda Container Image

```dockerfile
FROM public.ecr.aws/lambda/python:3.11

RUN yum install -y ffmpeg
RUN pip install boto3

COPY app.py ${LAMBDA_TASK_ROOT}

CMD [ "app.handler" ]
```

```python
# app.py - 直接使用 FFmpeg
import subprocess

def handler(event, context):
    # 从 S3 下载
    ...
    # 调用镜像内的 ffmpeg
    subprocess.run(['ffmpeg', '-i', 'in.mp4', '...', 'out.mp4'], check=True)
    # 上传回 S3
    ...
    return {'statusCode': 200}
```

## 💡 Serverless 视频实战案例

### 案例：短视频自动处理

```
用户上传 MP4 → S3 触发 → Lambda 收到
                            ├─ 触发 MediaConvert 转码
                            ├─ 调用 Rekognition 检测内容
                            ├─ 生成缩略图
                            └─ 触发 SNS 通知前端
```

### 案例：直播录制 + 切片

```
MediaLive 录制 → S3 触发 → Lambda
                              ├─ MediaConvert 转多分辨率
                              ├─ HLS 切片
                              └─ CDN 预热
```

### 案例：AI 短视频智能剪辑

```
1. 用户上传原始视频 → S3
2. Lambda 触发 → 函数调用 AI 服务
3. AI 识别精彩片段 → 输出剪辑信息
4. Lambda → MediaConvert 剪辑合成
5. 输出高光集锦
```

## 🔧 CDN 预热集成

```python
import boto3

cloudfront = boto3.client('cloudfront')

def handler(event, context):
    # 转码完成后
    paths = [
        '/video/1080p/playlist.m3u8',
        '/video/720p/playlist.m3u8',
        # ...
    ]
    cloudfront.create_invalidation(
        DistributionId='E1234ABC',
        InvalidationBatch={'Paths': {'Quantity': len(paths), 'Items': paths}, 'CallerReference': str(time.time())}
    )
```

## 💰 Serverless 成本对比

### 场景：1000 个 1080p 视频转码（每视频 10 分钟）

| 方案 | 单价 | 总成本 |
| --- | --- | --- |
| **自建 GPU 服务器** | ¥2/小时 | ¥300-2000/月（基础） |
| **AWS MediaConvert** | $0.025/分钟 | ¥1750 |
| **Lambda + FFmpeg** | $0.0166/GB-s | ¥500-1500 |
| **阿里云 MPS** | ¥0.018/分钟 | ¥180 |
| **腾讯云 MPS** | ¥0.018/分钟 | ¥180 |

## 🛡️ 最佳实践

1. **幂等处理**：可能重复触发，需做去重
2. **错误重试**：DLQ + 重试机制
3. **冷启动**：预热常驻实例
4. **并发限制**：设置 Lambda 并发上限
5. **监控告警**：CloudWatch / SLS
6. **事件解耦**：使用 SQS / 队列缓冲
7. **大文件分块**：避免单函数超时
