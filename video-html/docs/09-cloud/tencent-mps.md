---
title: 腾讯云媒体处理
date: 2026-08-15  # date-auto-injected
---

# 腾讯云媒体处理 CI

<span class="kg-badge kg-badge-cloud">云服务</span>
<span class="kg-badge kg-badge-tools">SDK</span>
<span class="kg-badge kg-badge-codec">转码</span>

腾讯云媒体数据处理 CI（Cloud Infinite）提供 **音视频转码、AI 增强、媒体审核、极速高清** 等能力。

## 🎯 核心服务

| 服务 | 说明 |
| --- | --- |
| **MPS（媒体处理）** | 音视频转码、截图 |
| **CI 数据万象** | 媒体处理 + 内容审核 |
| **极速高清** | AI 编码增强 |
| **媒体智能** | 内容理解、审核 |
| **直播 LVB** | 实时音视频 |

## 🚀 MPS 核心能力

```
输入（COS）→ 转码 → 输出（COS）
                 ├─ 多种分辨率
                 ├─ 多种编码格式
                 ├─ 截图 / 雪碧图
                 ├─ 视频水印
                 ├─ 智能封面
                 └─ 切片 (HLS/DASH)
```

## 💡 极速高清（IEH）

腾讯云自研的 **AI 编码增强** 服务：

- 比 x265 节省 30-50% 码率
- 同等画质下体积更小
- 支持 H.264 / H.265 输出

```json
{
  "TranscodeTask": {
    "DefinitionName": "极速高清-1080P",
    "EnhanceConfig": {
      "EnhanceVideo": true,
      "VideoSuperResolution": "sr-2x"
    }
  }
}
```

## 🎬 任务结构

```
Workflow（工作流）
  ├─ Trigger (COS 上传事件)
  ├─ Transcode (转码任务)
  │   ├─ Container: HLS/MP4/DASH
  │   ├─ Video: H.264/H.265/AV1
  │   ├─ Audio: AAC/MP3/Opus
  │   └─ Multiple Output (多输出)
  ├─ Snapshot (截图)
  ├─ SmartCover (智能封面)
  ├─ AnimatedGraphics (动图)
  └─ SnapshotByTimeOffset (指定时间截图)
```

## 💻 SDK 调用

### Python SDK

```python
from tencentcloud.mps.v20190612 import mps_client, models

client = mps_client.MpsClient(cred, "ap-shanghai")

# 创建转码任务
req = models.CreateWorkflowRequest()
req.Name = "my-workflow"
req.Trigger.Type = "CosFileUpload"
req.Trigger.CosBucketId = "example-123456"
req.Output.Storage = "COS"
req.Output.CosOutput = {"Bucket": "example-123456", "Region": "ap-shanghai"}

# 转码节点
transcode = models.MediaProcessTaskInput()
transcode.TranscodeTaskSet = [
    models.TranscodeTaskInput(
        Definition=10,     # 模板 ID
        WatermarkSet=[]
    )
]
req.MediaProcess = transcode

client.CreateWorkflow(req)
```

### 触发工作流

```bash
# COS 上传触发
cosutil cp input.mp4 cos://bucket/path/input.mp4
# 自动触发工作流
```

### 监听完成事件

```python
# 监听 CMQ 回调
def handle_callback(event):
    task_id = event["TaskId"]
    status = event["Status"]
    if status == "FINISH":
        output_url = event["Output"]["Url"]
```

## 📐 系统预设模板

| 预设模板 ID | 名称 | 参数 |
| --- | --- | --- |
| 10 | MP4-HD (H.264) | 1080p / 4000k |
| 20 | MP4-SD (H.264) | 720p / 1200k |
| 30 | MP4-FHD (H.265) | 1080p / 3000k |
| 40 | MP4-4K (H.265) | 4K / 12000k |
| 100 | HLS-HD | 1080p HLS |
| 110 | HLS-SD | 720p HLS |
| 200 | DASH-AST | 自适应 DASH |
| 1000 | 极速高清-1080P | H.264 + AI |
| 1100 | 极速高清-1080P-H.265 | H.265 + AI |

## 🎨 自定义模板

```json
{
  "Definition": "my-template",
  "Container": {
    "Type": "mp4",
    "SubConfs": ["H.264"]
  },
  "Video": {
    "Codec": "H.265",
    "Bitrate": 4000000,
    "Width": 1920,
    "Height": 1080,
    "Fps": 30,
    "Profile": "Main"
  },
  "Audio": {
    "Codec": "AAC",
    "Bitrate": 128000,
    "SampleRate": 44100,
    "Channels": 2
  }
}
```

## 🤖 内容审核

### 媒体审核（博通 PRocessMedia）

```python
req = models.ProcessMediaRequest()
req.InputInfo = {"Type": "COS", "CosInput": {"Bucket": "bucket", "Region": "ap-shanghai", "Object": "input.mp4"}}

# 审核配置
content_review = models.ContentReviewTaskInput()
content_review.Definition = 50
req.MediaProcess.MediaProcessTask.MediaContentReviewTask = content_review
```

### AI 智能标签

| 能力 | 描述 |
| --- | --- |
| **视频分类** | 短视频 / 长视频 / 直播 |
| **场景识别** | 室内 / 户外 / 自然 |
| **人物标签** | 识别性别、年龄段 |
| **语音转文字** | ASR 字幕生成 |
| **OCR** | 视频内文字提取 |

## 💰 价格参考

| 项 | 价格 |
| --- | --- |
| 普通转码 (H.264) | ¥0.018 / 分钟 |
| 普通转码 (H.265) | ¥0.027 / 分钟 |
| 极速高清 | ¥0.061 / 分钟 |
| 极速高清 HEVC | ¥0.108 / 分钟 |
| 媒体审核 | ¥0.025 / 分钟 |
| 截图 | ¥0.002 / 千次 |
| 内容识别 | ¥0.005 / 分钟 |

## 🔗 一体化场景

### 直播 + 云端转码 + CDN

```
采集 → LVB 直播 → MCS 录制 → CI 转码 → CDN 分发
                                          ↓
                                       极速高清
                                          ↓
                                       媒资存储（COS）
```

### 短视频上传流程

```
用户上传到 COS → CI 工作流自动触发 → 多种分辨率转码 → AI 审核 → CDN 缓存
```

## 🛠️ 实战案例

### 案例：在线教育平台

```python
# 多清晰度转码 + 字幕 + 智能审核
workflow = {
    "Name": "edu-transcode",
    "Trigger": {"Type": "CosFileUpload", "Bucket": "edu-video"},
    "MediaProcess": {
        "TranscodeTaskSet": [
            {"Definition": 110},     # 720p HLS
            {"Definition": 111}      # 480p HLS
        ],
        "MediaContentReview": {"Definition": 50}
    },
    "Output": {"Bucket": "edu-output"}
}
```

### 案例：UGC 短视频

```python
# 单输入多输出
req.TranscodeTaskSet = [
    {"Definition": 10},             # 1080p MP4
    {"Definition": 100},            # 1080p HLS
    {"Definition": "animated_task"} # 动图封面
]
```

## ⚠️ 限制与最佳实践

### 限制

| 项 | 限制 |
| --- | --- |
| 任务并发 | 50 / 队列 |
| 单文件大小 | 50GB |
| 时长 | 24h |

### 最佳实践

1. **复用模板**：同名模板可共享
2. **批量提交**：多个任务一次提交
3. **优先级**：直播流使用极速队列
4. **事件回调**：使用 SCF 处理回调
5. **缓存预热**：配合 CDN 边缘预热
6. **跨国优化**：使用全球加速 + 多 region 转码

## 🚀 与其他服务对比

| 维度 | 腾讯云 MPS | AWS MediaConvert |
| --- | --- | --- |
| 价格 | 中等 | 较高 |
| AI 能力 | 极速高清 + 内容审核 | 较丰富 |
| 集成度 | 与 CDN/直播一体化 | Lambda 友好 |
| 国内速度 | 快 | 需走国际 |
| 国际化 | 较弱 | 强 |
