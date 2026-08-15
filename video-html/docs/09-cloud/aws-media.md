---
title: AWS 媒体服务
---

# AWS 媒体服务

<span class="kg-badge kg-badge-cloud">云服务</span>
<span class="kg-badge kg-badge-tools">SDK</span>
<span class="kg-badge kg-badge-codec">转码</span>

AWS 提供完整的 **媒体生产到分发** 服务栈：**MediaConvert / MediaLive / MediaPackage / MediaStore / IVS**。

## 🌐 AWS 媒体服务全景

```
┌────────────────────┬─────────────────────┬────────────────┐
│ 制作与处理          │ 实时音视频           │ 内容分发        │
├────────────────────┼─────────────────────┼────────────────┤
│ MediaConvert       │ MediaLive           │ CloudFront     │
│ MediaPackage       │ IVS                 │ MediaConnect   │
│ MediaTailor        │ MediaConnect        │ MediaStore     │
│ MediaLive          │                     │                │
│ Media2 (S3+Lambda) │                     │                │
└────────────────────┴─────────────────────┴────────────────┘
```

## 🎬 MediaConvert（转码）

核心服务：批量音视频转码 + 离线工作负载。

### 核心概念

| 概念 | 含义 |
| --- | --- |
| **Job** | 转码任务 |
| **Preset** | 编码预设 |
| **Template** | 转码模板 |
| **JobTemplate** | 任务模板 |
| **Queue** | 任务队列 |

### 创建转码任务（Python Boto3）

```python
import boto3

mediaconvert = boto3.client('mediaconvert', endpoint_url='https://xxx.mediaconvert.us-east-1.amazonaws.com')

response = mediaconvert.create_job(
    Role='arn:aws:iam::123456789012:role/MediaConvertRole',
    Settings={
        'Inputs': [{
            'FileInput': 's3://input-bucket/video.mp4'
        }],
        'OutputGroups': [{
            'Name': 'Apple HLS',
            'OutputGroupSettings': {
                'Type': 'HLS_GROUP_SETTINGS',
                'HlsGroupSettings': {
                    'Destination': 's3://output-bucket/hls/'
                }
            },
            'Outputs': [{
                'VideoDescription': {
                    'Width': 1920, 'Height': 1080,
                    'CodecSettings': {
                        'Codec': 'H_264',
                        'H264Settings': {
                            'Bitrate': 5000000,
                            'RateControlMode': 'CBR'
                        }
                    }
                },
                'AudioDescriptions': [{
                    'CodecSettings': {'Codec': 'AAC', 'AacSettings': {'Bitrate': 128000}}
                }]
            }]
        }]
    }
)
job_id = response['Job']['Id']
```

### ABR 阶梯（自适应）

```python
'Outputs': [
    # 1080p
    {'NameModifier': '_1080p', 'VideoDescription': {...}},
    # 720p
    {'NameModifier': '_720p', 'VideoDescription': {...}},
    # 480p
    {'NameModifier': '_480p', 'VideoDescription': {...}},
    # 360p
    {'NameModifier': '_360p', 'VideoDescription': {...}}
]
```

### 输出格式

| 格式 | 用途 |
| --- | --- |
| **HLS** | Apple 设备、iOS |
| **DASH** | 跨平台、自适应 |
| **MP4** | 单文件点播 |
| **MSS** | Smooth Streaming |
| **CMAF** | HLS + DASH |

## 🔴 MediaLive（实时编码）

**AWS 直播服务**，支持 RTMP / HLS 输入，输出 HLS / DASH / CMAF。

### 架构

```
摄像机/RTMP → MediaLive Channel
                  ↓
         Output Group 1: HLS
         Output Group 2: MediaPackage
         Output Group 3: DASH
                  ↓
         MediaPackage / MediaStore / S3
                  ↓
         CloudFront CDN
```

### 推流到 MediaLive

```bash
# MediaLive RTMP Input
rtmp://1.2.3.4:1935/live/stream-key

# MediaLive HLS Input (push)
https://medialive-input.example/live/hls/stream.m3u8
```

### 创建 Channel

```python
medialive = boto3.client('medialive')

medialive.create_channel(
    Name='my-channel',
    InputSpecification={'Codec': 'AVC', 'Resolution': 'HD', 'MaximumBitrate': 'MAX_20_MBPS'},
    InputAttachments=[{'InputId': 'input-1'}],
    Destinations=[{'Id': 'dest-1', 'Settings': [{'Url': 'https://medialive-output/...'}]}],
    EncoderSettings={
        'VideoDescriptions': [{
            'Width': 1920, 'Height': 1080,
            'CodecSettings': {'Codec': 'H_264', 'H264Settings': {'Bitrate': 5000000}}
        }]
    }
)
```

## 📦 MediaPackage（实时打包 + DRM）

将单路 HLS 直播打包为多格式，**支持加密**：

```
MediaLive → MediaPackage
              ├── Apple HLS
              ├── DASH
              ├── CMAF (HLS+DASH 通用)
              └── 加密 (Speke)
```

### DRM 加密

```python
mediapackage.create_packaging_configuration(
    Id='drm-config',
    PackagingGroupId='pg-123',
    MssPackage={'MssManifests': [...], 'Encryption': {'SpekeKeyProvider': {...}}},
    HlsPackage={'HlsManifests': [...], 'Encryption': {'SpekeKeyProvider': {...}}}
)
```

支持的 DRM：
- **Widevine** (Google)
- **PlayReady** (Microsoft)
- **FairPlay** (Apple)
- **PrimeTime** (Adobe)

## 🗃️ MediaStore / S3 输出

| 存储 | 用途 |
| --- | --- |
| **MediaStore** | 高速实时打包（多读单写） |
| **S3** | 静态转码输出、归档 |

## 🌐 MediaTailor（广告插入）

**服务端广告插入 (SSAI)**：

- 在视频流中动态插入广告
- 不被广告拦截工具屏蔽
- 支持 VAST 4 / VPAID

```
CDN → MediaTailor
        ↓
  ├─ 检测 SCTE-35 广告标记
  ├─ 请求 VAST 广告
  └─ 拼接 → HLS 输出
        ↓
      CloudFront
```

### 广告配置

```python
mediatailor.create_program(
    Name='my-program',
    SourceLocationName='live-source',
    AdBreaks=[{'OffsetMillis': 30000, 'DurationMillis': 15000}]
)
```

## 🎤 IVS（互动直播）

**实时互动直播** 服务，专注于 **低延迟直播（< 5s）**。

| 特点 | 描述 |
| --- | --- |
| **延迟** | < 5s（典型 1-3s） |
| **SDK** | iOS / Android / Web / Unity |
| **互动** | 实时评论、点赞 |
| **录制** | 自动录制到 S3 |
| **认证** | 私有频道支持 |

### 推流

```bash
# Web SDK
const streamConfig = {
    channel: "my-channel",
    ingestEndpoint: "rtmps://global-live-ps.main.bcv.live.use1.devtunnels.aws:443"
};
```

## 📊 转码任务监控

```python
# 查询任务状态
response = mediaconvert.get_job(Id=job_id)
status = response['Job']['Status']  # 'SUBMITTED'|'PROGRESSING'|'COMPLETE'|'ERROR'
```

### 回调通知

```python
# SNS 订阅
def handle_sns(event):
    job = event['Records'][0]['Sns']['Message']
    if job['Status'] == 'COMPLETE':
        publish_to_queue(job['OutputGroupDetails'])
```

## 💰 AWS 媒体服务定价（us-east-1）

| 服务 | 价格 |
| --- | --- |
| MediaConvert SD | $0.0075 / 分钟 |
| MediaConvert HD | $0.015 / 分钟 |
| MediaConvert FHD | $0.025 / 分钟 |
| MediaConvert 4K | $0.038 / 分钟 |
| MediaLive SD | $0.014 / 分钟 |
| MediaLive HD | $0.028 / 分钟 |
| MediaPackage | $0.05 / GB |
| IVS SD | $0.004 / 分钟 |
| IVS HD | $0.012 / 分钟 |

## 🔗 与 S3 + Lambda 集成

### Lambda 触发转码

```python
import json
import boto3

def handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    mediaconvert = boto3.client('mediaconvert')
    response = mediaconvert.create_job(
        Role=os.environ['ROLE_ARN'],
        Settings={
            'Inputs': [{'FileInput': f's3://{bucket}/{key}'}],
            'OutputGroups': [...]
        }
    )
```

### CloudFront + Lambda@Edge

- 边缘节点即时转码
- 缩略图生成
- 播放器兼容

## 🛠️ 实战案例

### 案例 1：视频点播平台

```
用户上传 → S3 (触发器) → Lambda → MediaConvert (转码多分辨率)
                                          ↓
                                    写入媒资数据库
                                          ↓
                                  CloudFront CDN 边缘缓存
```

### 案例 2：24/7 直播频道

```
 摄制 → MediaLive (Channel)
         ↓
   MediaPackage (打包 DRM)
         ↓
   MediaTailor (广告插入)
         ↓
   CloudFront
```

### 案例 3：体育赛事直播 + 录像回放

```
MediaLive (Camera A) ─┐
MediaLive (Camera B) ─┼─→ MediaPackage → CloudFront → Web
MediaLive (Audio) ────┘
                       ↓
                       S3 (录制存档)
                       ↓
                       MediaConvert (转码 + 切片)
```

## ⚠️ 注意点

1. **权限角色**：IAM Role 含 S3FullAccess + MediaConvert
2. **区域**：MediaLive / MediaPackage 在特定 region
3. **配额**：MediaConvert 默认 100 队列（可申请提升）
4. **网络成本**：跨 region 数据传输需规划
5. **延迟要求**：实时场景用 MediaLive

## 📚 最佳实践

1. **使用 Job Templates**：预设编码参数复用
2. **CloudFront 缓存**：长 TTL + 边缘函数
3. **S3 Lifecycle**：原片归档到 Glacier
4. **实时监控**：CloudWatch Alarms
5. **DRM 选择**：苹果用 FairPlay、安卓用 Widevine
