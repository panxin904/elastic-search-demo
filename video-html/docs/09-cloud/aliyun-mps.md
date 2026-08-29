---
title: 阿里云媒体处理
date: 2026-08-15  # date-auto-injected
---

# 阿里云媒体处理 MPS

<span class="kg-badge kg-badge-cloud">云服务</span>
<span class="kg-badge kg-badge-tools">SDK</span>
<span class="kg-badge kg-badge-codec">转码</span>

阿里云媒体处理（Media Processing Service, MPS）提供 **音视频转码、截图、剪辑、智能审核、AI 处理** 等一站式服务。

## 🎯 MPS 核心能力

| 能力 | 描述 |
| --- | --- |
| **转码** | 多格式、多分辨率 |
| **截图** | 时间点截图、雪碧图 |
| **剪辑** | 云端剪辑合成 |
| **水印** | 静态 / 动态水印 |
| **切片** | HLS / DASH |
| **加密** | HLS-AES、DRM |
| **AI 处理** | 字幕、审核、超分 |
| **媒体库** | 媒资管理 |

## 💡 适用场景

```
┌──────────────────────────────────────┐
│ 短视频 / 直播回放转码                 │
│ 在线教育课件转码                       │
│ 影视后期处理                           │
│ 监控录像压缩归档                       │
│ 媒资管理 + 智能审核                    │
│ 跨区域分发 + CDN 一体化                │
└──────────────────────────────────────┘
```

## 🚀 快速开始

### 1. 创建 MPS 集群

```bash
# 在阿里云控制台创建 MPS 项目
# 或通过 OpenAPI
aliyun mps CreatePipeline \
  --Name "my-pipeline" \
  --SpeedLevel 1 \
  --SpeedType Standard
```

### 2. 提交转码任务

```json
{
  "Input": "oss://bucket/input.mp4",
  "Output": "oss://bucket/output/",
  "PipelineId": "pipe-1234",
  "TranscodeOutput": {
    "Container": "mp4",
    "Video": {"Codec": "H.264", "Bitrate": 4000, "Width": 1920, "Height": 1080},
    "Audio": {"Codec": "AAC", "Bitrate": 128}
  }
}
```

### 3. 转码模板

| 模板 | 用途 |
| --- | --- |
| **MP4-HD** | 1080p 高清 |
| **MP4-SD** | 720p 标清 |
| **MP4-LD** | 480p 流畅 |
| **HLS-HD** | HLS 切片 1080p |
| **HLS-AES** | 加密 HLS |
| **DASH-AST** | DASH 自适应 |

## 💻 SDK 调用

### Java SDK

```java
import com.aliyun.mps20140618.Client;
import com.aliyun.mps20140618.models.*;

Client client = new Client(accessKey, secret);

// 提交转码任务
SubmitJobsRequest request = new SubmitJobsRequest();
request.setInput("oss://bucket/input.mp4");
request.setOutputBucket("bucket");
request.setOutput("output/");
request.setPipelineId(1L);

SubmitJobsResponse response = client.submitJobs(request);
String jobId = response.getSubmitJobsResponse().getJobResultList().get(0).getJob().getJobId();
```

### Python SDK

```python
from aliyunsdkcore.client import AcsClient
from aliyunsdkmts.request.v20140618 import SubmitJobsRequest

client = AcsClient('<access_key>', '<secret>', 'cn-shanghai')

request = SubmitJobsRequest.SubmitJobsRequest()
request.set_Input('oss://bucket/input.mp4')
request.set_OutputBucket('bucket')
request.set_Output('output/')
request.set_PipelineId(1)

response = client.do_action_with_exception(request)
```

## 📐 预置模板

### 标清 (SD)

```json
{
  "Container": "MP4",
  "Video": {"Codec": "H.264", "Bitrate": 1000, "Width": 848, "Height": 480, "Fps": 25},
  "Audio": {"Codec": "AAC", "Bitrate": 64, "Samplerate": 44100, "Channels": 2}
}
```

### 高清 (HD)

```json
{
  "Container": "MP4",
  "Video": {"Codec": "H.265", "Bitrate": 3000, "Width": 1920, "Height": 1080, "Fps": 30},
  "Audio": {"Codec": "AAC", "Bitrate": 128, "Samplerate": 44100, "Channels": 2}
}
```

### 超清 (UHD)

```json
{
  "Container": "MP4",
  "Video": {"Codec": "H.265", "Bitrate": 8000, "Width": 3840, "Height": 2160, "Fps": 60, "Profile": "Main10"}
}
```

## 🎨 智能媒体处理

### 媒体审核

```json
{
  "Input": "oss://video.mp4",
  "PipelineId": 1,
  "MediaCoverConfig": {
    "VideoReview": {
      "ReviewContents": ["violence", "porn", "terrorism"],
      "IntervalSec": 5
    }
  }
}
```

### 智能封面

```json
{
  "MediaCoverConfig": {
    "ExtractVideoCover": {
      "TimePoints": [5, 15, 30, 60],
      "Format": "jpg",
      "Width": 1280,
      "Height": 720
    }
  }
}
```

### AI 字幕

```json
{
  "AIMediaProduceConfig": {
    "ASRConfig": {
      "Enabled": true,
      "Language": "zh-CN"
    }
  }
}
```

## ⚡ 流水线 SpeedLevel

| Level | 速度 | 价格 | 适合 |
| --- | --- | --- | --- |
| 0 | 极速 | 高 | 直播流 |
| 1 | 标准 | 中 | 常规 |
| 2 | 慢速 | 低 | 离线 |
| 5 | 经济 | 低 | 大批量 |

## 🌐 Media Flow（新版）

更灵活的媒体处理编排：

```json
{
  "MediaFlow": {
    "Name": "transcode-flow",
    "Topology": [
      {"Ref": "source"},
      {"Ref": "transcode", "Type": "Transcode", "Input": "$source", "OutputBucket": "out"},
      {"Ref": "snapshot", "Type": "Snapshot", "Input": "$transcode", "OutputBucket": "out"}
    ]
  }
}
```

## 📊 MPS 价格（参考）

| 项 | 价格 |
| --- | --- |
| 普通转码 | ¥0.0243 / 分钟 |
| 极速转码 | ¥0.243 / 分钟 |
| 转封装 | ¥0.0121 / 分钟 |
| 截图 | ¥0.0162 / 千次 |
| 媒体审核 | ¥0.038 / 分钟 |
| 媒资存储 | ¥0.02 / GB / 天 |

## 🔗 与其他服务集成

| 服务 | 集成方式 |
| --- | --- |
| **OSS** | 输入 / 输出存储 |
| **CDN** | 转码后 + CDN 分发 |
| **Live** | 直播 + 录制转码 |
| **RAM** | 权限管理 |
| **MNS** | 任务完成回调 |
| **函数计算** | 自定义处理节点 |

## 🛠️ 实战案例

### 案例：短视频上传转码

```
客户端上传 OSS → 触发 OSS 事件 → MPS 转码 → 完成通知 → 写入数据库
                                                                  │
                              CDN 预热 ← 媒资信息返回 ←───────────┘
```

```java
// OSS 触发的 Lambda 监听器
@FunctionCompute
public void handleOSSEvent(OSSEvent event) {
    String input = event.getObjectKey();
    mpsClient.submitTranscodeJob(input, "template-hd");
}
```

## 🚧 注意事项

1. **存储**：输入文件在 OSS 同区域可减少延迟
2. **回调**：使用 MNS 队列或 RocketMQ 监听完成事件
3. **权限**：RAM 子账号授权 oss:*, mts:*
4. **API 限流**：默认 100 QPS

## 📚 最佳实践

1. **多任务并行**：同一文件提交多模板同时转码
2. **优先级**：直播流用极速 + 短队列
3. **断点续传**：切片后分片转码
4. **水印 + 加密**：配合 CDN 防盗链
5. **审核自动化**：上传即审 → 阻塞高风险内容
