---
title: 短视频处理
date: 2026-08-15  # date-auto-injected
---

# 短视频技术体系

<span class="kg-badge kg-badge-app">应用</span>
<span class="kg-badge kg-badge-tools">端云协同</span>
<span class="kg-badge kg-badge-cloud">云端转码</span>

短视频 App（抖音、快手、TikTok、Reels）的技术体系覆盖 **客户端采集 / 上传 / 云端转码 / CDN 分发 / 推荐 / 播放** 全链路。

## 🏗️ 短视频技术架构

```
┌─────────────────────────────────────────────────────┐
│                    客户端                            │
│ 拍摄 → 滤镜 → 剪辑 → 特效 → 编码 → 上传            │
│   ↓       ↓      ↓      ↓      ↓       ↓             │
│ 相机SDK  GPU   时间线  AI特效 硬编   断点续传         │
├─────────────────────────────────────────────────────┤
│                    服务端                            │
│ 上传服务 → 媒资库 → 转码集群 → 审核 → 封面           │
│    ↓         ↓         ↓          ↓      ↓          │
│  CDN       元数据   多分辨率    AI机审 智能封面        │
│    ↓                                     ↓          │
│    └──── 推荐系统 + 内容分发 ────────────┘          │
└─────────────────────────────────────────────────────┘
```

## 📱 客户端拍摄

### 核心能力

| 能力 | 技术方案 |
| --- | --- |
| **拍摄** | Camera2 / AVCaptureSession / AVFoundation |
| **实时美颜** | GPU Shader + AI 人脸检测 |
| **滤镜** | GLES lookup table / Metal |
| **特效** | 3D Mesh + 粒子系统 |
| **分段录制** | 多段 MP4 拼接 |
| **音频混合** | AudioMix / Oboe |

### Android 拍摄框架

```java
// Camera2 预览 + 录制
CameraDevice device = manager.openCamera(id, stateCallback, handler);
CaptureRequest.Builder builder = device.createCaptureRequest(CameraDevice.TEMPLATE_RECORD);
builder.addTarget(mediaRecorder.getSurface());
builder.addTarget(previewSurface);
```

### iOS 拍摄框架

```swift
// AVCaptureSession
let session = AVCaptureSession()
session.sessionPreset = .high
let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .back)
let input = try AVCaptureDeviceInput(device: device)
session.addInput(input)
let output = AVCaptureMovieFileOutput()
session.addOutput(output)
session.startRunning()
```

## 🎨 实时美颜与滤镜

### 美颜流程

```python
# OpenCV + Dlib 美颜
def beautify(frame):
    # 1. 检测人脸关键点
    landmarks = dlib_faces(frame)
    # 2. 磨皮（双边滤波）
    smooth = cv2.bilateralFilter(frame, 9, 75, 75)
    # 3. 提亮
    bright = adjust_brightness(smooth)
    # 4. 大眼、瘦脸（局部变形）
    warped = warp_face(bright, landmarks)
    return warped
```

### GPU 美颜

- **GLSL Shader**：直接在 GPU 上执行
- **Metal (iOS)**：自定义渲染管线
- **Vulkan (Android)**：现代 GPU API

```glsl
// 磨皮 shader
uniform sampler2D inputImage;
uniform vec2 facePoints[68];
varying vec2 textureCoord;
void main() {
    vec4 color = texture2D(inputImage, textureCoord);
    vec4 smooth = bilinearBlur(uv, 4.0);
    gl_FragColor = mix(color, smooth, 0.5);
}
```

### AI 美颜

```
Real-ESRGAN 修复细节
├── GFPGAN 人脸恢复
├── CodeFormer 高保真
└── 抖音特效: 漫画脸、AI 换脸
```

## 🎞️ 客户端剪辑

### 时间线（Timeline）

```
[片段1] [转场] [片段2] [滤镜] [片段3] [音频]
   ↓        ↓        ↓        ↓        ↓        ↓
  30s     0.5s      20s      全段      15s      BGM
```

### 关键能力

| 能力 | 实现 |
| --- | --- |
| **多轨道** | 时间线 + 渲染管线 |
| **剪辑** | AvMediaExtractor 抽帧 |
| **滤镜** | GLES Surface |
| **音乐对齐** | 节拍检测 |
| **字幕** | BAF / SSA 解析 |
| **特效** | 粒子 + Mesh |

## 📤 上传与断点续传

### 直接上传

```http
POST /api/upload HTTP/1.1
Content-Type: multipart/form-data

{
  "file": <binary>,
  "metadata": {
    "size": 12345678,
    "duration": 30,
    "md5": "abc..."
  }
}
```

### 分片上传（断点续传）

```
客户端                          服务端
  │                              │
  ├── INIT ─────────────────→  │
  │   {total: 100MB, chunks: 100} │
  │                          ───┤ 分配 uploadId
  │                          ←─┤  {uploadId: "u-123"}
  │                              │
  ├── CHUNK 1 (1MB) ────────→  │
  ├── CHUNK 2 (1MB) ────────→  │
  ├── ... (断网重传) ...         │
  ├── CHUNK 5 (1MB) ────────→  │
  │   (跳过已上传)               │
  ├── CHUNK 100 (1MB) ───────→ │
  │                          ───┤ 合并分片
  │                          ←─┤  {url: "..."}
  │                              │
```

#### S3 Multipart Upload

```python
s3 = boto3.client('s3')

# 初始化
response = s3.create_multipart_upload(Bucket='bucket', Key='video.mp4')
upload_id = response['UploadId']

# 分片
parts = []
for i in range(0, file_size, chunk_size):
    part = s3.upload_part(
        Bucket='bucket', Key='video.mp4', PartNumber=i+1,
        UploadId=upload_id, Body=chunk_data
    )
    parts.append({'PartNumber': i+1, 'ETag': part['ETag']})

# 完成
s3.complete_multipart_upload(
    Bucket='bucket', Key='video.mp4',
    UploadId=upload_id, MultipartUpload={'Parts': parts}
)
```

### 压缩上传

- 客户端先转 720p / 540p 上传
- 云端再做高分辨率转码
- 大幅节省带宽

## 🔄 云端转码

### 输入 → 多输出

```
源视频（1080p / H.264 / 50Mbps / 60s）
     │
     ├─→ 1080p H.264 (4Mbps)  → 高清
     ├─→ 720p H.264 (2Mbps)   → 标清
     ├─→ 540p H.265 (1Mbps)   → 流畅
     ├─→ 240p H.264 (200kbps) → 极省流
     ├─→ 动图封面 (5s)
     ├─→ 雪碧图 (screenshot)
     └─→ HLS 切片 (3s)
```

### 异步任务系统

```python
# 提交转码任务
def submit_transcode(video_id, source_url):
    job = {
        'video_id': video_id,
        'source': source_url,
        'outputs': [
            {'profile': 'h264-1080p'},
            {'profile': 'h264-720p'},
            {'profile': 'h265-540p'},
            {'profile': 'cover'},
            {'profile': 'hls'}
        ]
    }
    queue.put(job)
```

## 🤖 AI 内容审核

### 审核维度

| 维度 | 实现 |
| --- | --- |
| **图像违规** | 色情、低俗、暴恐 |
| **文字违规** | OCR + 文本分类 |
| **音频违规** | ASR + 敏感词 |
| **人脸违规** | 名人识别、未成年人 |
| **复合审核** | 多模态 AI |

### 多级审核

```
上传 → AI 机审 → 通过 → 用户可见
              ↓ 风险
       人工复审 → 通过
                  ↓ 违规
                 屏蔽 + 警告
```

## 🎨 智能封面

### 封面策略

| 策略 | 描述 |
| --- | --- |
| **视觉精选** | 美学评分、显著性 |
| **人脸检测** | 选有人脸的笑脸帧 |
| **关键帧** | 场景突变点 |
| **文字突出** | 有标题/字幕的帧 |
| **服装/动作** | 高辨识度帧 |

### 实现

```python
def extract_cover(video_path):
    # 抽帧
    frames = extract_frames(video_path, n=10)
    # 评分
    scores = [score_frame(f) for f in frames]
    # 选择最佳
    best_idx = np.argmax(scores)
    return frames[best_idx]
```

## 📡 播放器与 CDN

### 播放器选型

| 平台 | 推荐 |
| --- | --- |
| **iOS** | AVPlayer + 自研内核 |
| **Android** | ExoPlayer / 阿里云播放器 |
| **Web** | video.js / shaka-player |
| **小程序** | 官方 + 自定义组件 |

### 播放器优化

```javascript
// HLS 预加载策略
player.on('hlsManifestParsed', () => {
    player.qualityLevels().forEach(q => {
        // 预加载第一个 GOP
    });
});

// 渐进式播放
player.liveSyncDurationCount = 2;  // 直播只同步 2 个片段
```

### CDN 分发策略

| 区域 | 策略 |
| --- | --- |
| **同 region** | CDN 直连 OSS |
| **跨 region** | CDN 中转 |
| **海外** | 专线 + 边缘节点 |
| **短视频重点** | 边缘预热 |

## 📊 推荐系统集成

### 用户行为分析

| 指标 | 计算方式 |
| --- | --- |
| **完播率** | 播放完成时长 / 总时长 |
| **点赞率** | 点赞 / 曝光 |
| **评论率** | 评论 / 曝光 |
| **转发率** | 转发 / 曝光 |
| **二跳率** | 进入作者主页 / 曝光 |

### 训练数据

```python
# 用户向量
user_embedding = {
    'gender': 'F',
    'age': 25,
    'interest_tags': ['美妆', '美食'],
    'behavior_embedding': [0.1, 0.5, ...]
}

# 内容向量
video_embedding = {
    'category': '美食',
    'tags': ['烘焙', '甜品'],
    'visual_embedding': [...],
    'audio_embedding': [...]
}

# 召回
similarity = dot(user_vec, video_vec)
```

## 🎯 性能指标

| 指标 | 目标 | 行业基准 |
| --- | --- | --- |
| **首帧时间** | < 500ms | 抖音 < 200ms |
| **FPS** | 60 | 满帧 |
| **上传速度** | 5MB/s+ | 取决于网络 |
| **转码时效** | < 5min（10s 视频） | < 1min |
| **审核时效** | < 30s | 实时 |

## 📚 实战案例：抖音技术选型

| 模块 | 方案 |
| --- | --- |
| **客户端** | 自研 + ByteDance EffectSDK |
| **AI 特效** | 自研深度学习推理引擎 |
| **上传** | 自研 P2P + 边缘加速 |
| **转码** | 自研集群 + 硬件加速 |
| **存储** | 自研对象存储 |
| **CDN** | 自建 + 第三方 |
| **审核** | 多模态 AI + 人工 |
| **推荐** | 自研深度推荐 |
| **播放器** | 自研 + Effects SDK |

## 🛠️ 开发建议

### 客户端
1. **GPU 优先**：美颜、滤镜、特效全部 GPU
2. **异步化**：上传、压缩、转码异步执行
3. **断点续传**：服务端分配 uploadId
4. **客户端预处理**：上传前转 H.265 压缩
5. **预加载**：基于播放历史预热

### 服务端
1. **消息队列**：上传、转码、审核解耦
2. **弹性伸缩**：突发流量自动扩容
3. **监控告警**：每任务 SLA 监控
4. **审核分级**：风险内容多级处理
5. **CDN 预热**：热门内容提前缓存

## 📚 跨站参考：📊 监控告警

<!-- xlink-dedup:do-not-edit -->

本节在 3 站展开，最权威版本位于 **observability** 站（[https://java-px.bot.cd/observability/](https://java-px.bot.cd/observability/)）。

其他站参考：[kafka](https://java-px.bot.cd/kafka/) / [mysql](https://java-px.bot.cd/mysql/) / [video](https://java-px.bot.cd/video/)

跨站关联由 `xlink-injector.py` + `crosslink-dedup.py` 自动生成（§8.68）。
