---
title: 视频会议
---

# 视频会议技术

<span class="kg-badge kg-badge-app">应用</span>
<span class="kg-badge kg-badge-protocol">WebRTC</span>
<span class="kg-badge kg-badge-ai">AI</span>

视频会议强调 **超低延迟、稳定性、互动性**，代表产品：Zoom、腾讯会议、钉钉、Teams。

## 🏗️ 视频会议架构

```
┌───────────────────────────────────────────────┐
│ 终端                                          │
│ PC / Mac / iOS / Android / 浏览器 / Web / 会议机 │
├───────────────────────────────────────────────┤
│ 信令媒体                                      │
│ 准入 / 房间管理 / 麦克风调度 / 屏幕共享         │
├───────────────────────────────────────────────┤
│ 媒体处理                                      │
│ MCU / SFU / 录制 / 转码 / AI                   │
├───────────────────────────────────────────────┤
│ 服务层                                        │
│ 用户 / 会议 / IM / 鉴权 / 计费                  │
└───────────────────────────────────────────────┘
```

## 📡 媒体架构模型

### 三种模型对比

| 模型 | 描述 | 优 / 劣 | 适合 |
| --- | --- | --- | --- |
| **Mesh** | 全互联 | 延迟低 / 带宽差 | 2-4 人 |
| **MCU** | 中央混流 | 兼容好 / 延迟+带宽 | 大型会议 |
| **SFU** | 选择性转发 | 平衡 / 服务器负担 | 中型会议 |

### Mesh（网状）

```
用户A ↔ 用户B
用户A ↔ 用户C
用户B ↔ 用户C
4 人会议 = 6 条连接
N 人会议 = N*(N-1)/2 条连接
```

### SFU（Selective Forwarding Unit）

```
        用户A (上行 1 路)
            ↓
    ┌────→ SFU
    │        ↓↓↓↓
    └────→ 用户B/C/D/E
        （下行 N-1 路）
```

SFU 当前主流：
- **mediasoup**
- **Janus**
- **Jitsi Videobridge**
- **LiveKit**

### MCU（Multipoint Control Unit）

```
用户A、B、C → MCU 合成 → 一路混流
                                  ↓
                              用户D、E、F
```

适合电信级会议（每用户带宽小）。

## 📞 WebRTC 协议栈

```
┌─────────────────────────────────┐
│  应用层：媒体协商 + 信令         │
├─────────────────────────────────┤
│  ICE：NAT 穿透                   │
├─────────────────────────────────┤
│  DTLS：加密传输                  │
├─────────────────────────────────┤
│  RTP：媒体传输                   │
├─────────────────────────────────┤
│  UDP / TCP                       │
└─────────────────────────────────┘
```

### 协商流程

```
SDP Offer/Answer:
  ├── 协商编解码（H.264 / VP8 / Opus）
  ├── 协商媒体类型（audio/video/data）
  ├── 协商传输协议（UDP/TCP）
  ├── 协商 DTLS 加密
  └── 协商 ICE candidates

ICE Connectivity Check:
  ├── STUN 协议 NAT 穿透
  ├── TURN 中继（对称 NAT）
  └── DTL-SRTP 传输加密
```

### WebRTC 核心类

```javascript
// 信令
const ws = new WebSocket('wss://server/signal');

// 客户端
const pc = new RTCPeerConnection({
    iceServers: [
        {urls: 'stun:stun.l.google.com:19302'},
        {urls: 'turn:turn.example.com', username: 'u', credential: 'p'}
    ]
});

pc.addTransceiver('audio', {direction: 'sendrecv'});
pc.addTransceiver('video', {direction: 'sendrecv'});

// SDP 协商
const offer = await pc.createOffer();
await pc.setLocalDescription(offer);
ws.send(JSON.stringify({type: 'offer', sdp: offer.sdp}));
```

## 📊 编码参数

### 视频会议参数

| 参数 | 推荐 |
| --- | --- |
| **分辨率** | 360p / 540p / 720p / 1080p |
| **帧率** | 15-30 fps（屏幕 30-60） |
| **码率** | 250-3000 kbps |
| **编码** | H.264 / VP8 / VP9 / AV1 |
| **Profile** | Constrained Baseline (兼容性最佳) |

### 屏幕共享参数

| 参数 | 推荐 |
| --- | --- |
| **分辨率** | 原尺寸 / 缩放（最大 1920） |
| **帧率** | 15 fps（视频会议） / 30-60 fps（协作） |
| **码率** | 500-3000 kbps |
| **编码** | H.264 (硬编) |

## 🤖 AI 增强

### AI 美颜 / 虚拟背景

| 能力 | 实现 |
| --- | --- |
| **美颜** | GPU 磨皮 + AI 提亮 |
| **虚拟背景** | Selfie Segmentation (MediaPipe) |
| **智能跟焦** | 人脸追踪 + 自动构图 |
| **背景降噪** | RNNoise / Krisp |

### 会议实时转写

```
音频 → ASR 引擎 → 实时字幕
                  ↓
             翻译（多语言）
                  ↓
             会议纪要生成
```

主流 ASR：
- **Whisper**（开源、本地/云端）
- **Azure Speech**（英文强）
- **腾讯云 ASR**
- **阿里云 ASR**
- **讯飞**

### AI 会议助手

- 实时记录 + 总结
- 多人声纹识别
- 议程提醒
- 关键词检索

## 🎬 Screen Share（屏幕共享）

### 编码策略

- **CPU 软编**：通用、H.264 / H.265
- **硬件编码**（推荐）：
  - macOS: VideoToolbox
  - Windows: NVENC / QSV / AMF
  - Linux: VAAPI / NVENC

```cpp
// macOS VideoToolbox 编码
VTCompressionSessionRef session;
VTCompressionSessionCreate(
    allocator, width, height, kCMVideoCodecType_H264,
    NULL, NULL, NULL,
    compressionCallback, NULL,
    &session
);

VTCompressionSessionEncodeFrame(
    session, imageBuffer, presentationTimeStamp,
    kCMTimeInvalid, frameProperties, NULL, errorOut
);
```

### 文本共享 + 协作

```
媒体轨道:
├── 视频（摄像头 + 屏幕）
├── 音频（麦克风 + 系统）
├── 应用（白板、文档）
└── 数据（聊天、协作）
```

## 📊 多人会议性能

### SFU 节点容量参考

| 节点 | 同时在线 | 带宽 | 服务器 |
| --- | --- | --- | --- |
| **小型** | 50 人 | 100 Mbps | 1 台 4 核 |
| **中型** | 200 人 | 1 Gbps | 1 台 8 核 |
| **大型** | 1000 人 | 10 Gbps | 多台集群 |

### 部署模式

```
小型: 1 MCU + 1 DB
中型: SFU 主备 + DB
大型: SFU 集群 + 转码集群 + AI + DB
```

## 🌐 全球分布式会议

### 挑战

- 跨 region 网络延迟
- 跨国带宽
- 异构终端兼容

### 解决方案

```
Region A        Region B
  媒体 SFU         媒体 SFU
    ↓               ↓
  跨 region 互联     ↓
       ↓            ↓
    Bridge SFU（中转）
       ↓
  Region C / D
```

### 边缘加速

- Web 端通过最近 PoP 接入
- 媒体就近接入 SFU
- 跨国走专线 / CDN

## 🛡️ 安全与质量

### 安全要点

| 维度 | 措施 |
| --- | --- |
| **传输加密** | SRTP + DTLS |
| **房间密码** | JWT + 一次性会议号 |
| **入会审核** | Waiting Room |
| **录制加密** | AES-256 |
| **权限分级** | 主持人 / 参会者 / 旁听 |

### 质量监控

```
QoS 指标:
├── 端到端延迟 (< 300ms)
├── 抖动 (< 50ms)
├── 丢包率 (< 3%)
├── 帧率稳定 (FPS)
└── 带宽利用
```

### 弱网对策

- NACK：丢包重传
- FEC：前向纠错
- RED：冗余编码
- RTX：重传 RTX 包
- Simulcast：多分辨率自适应

## 🛠️ 主流会议系统

### 商用服务

| 系统 | 特点 |
| --- | --- |
| **Zoom** | 全球稳定、SFU + MCU 混合 |
| **腾讯会议** | 国内、企业级 |
| **钉钉会议** | OA 集成 |
| **Teams** | Office 整合 |
| **Webex** | 企业级、跨平台 |
| **华为云会议** | 国产化 |

### 开源方案

| 方案 | 特点 |
| --- | --- |
| **Jitsi Meet** | 全开源 WebRTC |
| **MediaSoup Demo** | SFU 示例 |
| **LiveKit** | 云原生 SFU |
| **BigBlueButton** | 在线教学 |

## 💡 主流会议 SDK

| 厂商 | SDK | 平台 |
| --- | --- | --- |
| **声网 Agora** | iOS/Android/Web/Windows/Mac | 全平台 |
| **即构 Zego** | 全平台 SDK | 全平台 |
| **腾讯云音视频** | TRTC SDK | 全平台 |
| **阿里云音视频** | RTC SDK | 全平台 |
| **融云** | RC RTC | 全平台 |

## 📱 客户端实现要点

### 音频处理

```cpp
// 音频采集 → 3A 处理 → 编码 → 发送
// 3A: AEC (回声消除) + ANS (噪声抑制) + AGC (自动增益)
audio_capture();
audio_3a_process(aec, ans, agc);
audio_encode_opus();
rtp_send();
```

### 视频处理

```cpp
video_capture();
video_mirror_flip();      // 本地镜像
video_rotation();          // 设备旋转
video_encode_h264();       // 硬编
rtp_send();
```

### 网络适配

```cpp
// 探测网络带宽 + 调整编码参数
network_estimate = bandwidth_estimator();
if (network_estimate > 2mbps) {
    config.bitrate = 2000k;
} else if (network_estimate > 800kbps) {
    config.bitrate = 800k;
} else {
    config.bitrate = 300k;
}
config.width = 640; config.height = 360;
```

## 🎯 互动功能

| 功能 | 实现 |
| --- | --- |
| **举手** | IM 信令 |
| **聊天** | IM + 表情包 |
| **投票** | IM + 实时统计 |
| **白板** | 数据轨道 + Canvas |
| **分组讨论** | 多个 SFU 房间切换 |
| **录播** | MCU 合成 + 云端存储 |

### 分组讨论（Breakout）

```
主会场
    ├── 子房间 1 (SFU 1)
    ├── 子房间 2 (SFU 2)
    ├── 子房间 3 (SFU 3)
    └── 主持人在主会场巡视
```

## 📚 最佳实践

1. **终端兼容**：测试各端（Chrome、Safari、安卓、iOS）
2. **网络适配**：Simulcast + SVC
3. **编码器选型**：硬编优先（H.264 Baseline/Main）
4. **音频 3A**：必启用 AEC
5. **录制格式**：H.265 (云端存储) + 服务端合成
6. **回声消除**：SpeakerMode 适配
7. **多端同步**：MCU 方案更稳定
8. **AI 加载**：GPU 推理在云端
9. **证书管理**：DTLS 证书定期轮换
10. **CDN + 边缘**：全球 Web 用户就近接入

## 🚀 实战案例

### 案例 1：在线教育 1000 人

- SFU 集群（10+ 节点）
- 分组讨论
- 屏幕分享 + 白板
- 互动答题 + 弹幕

### 案例 2：远程面试

- 1V1 高清视频
- AI 行为分析（眼神、表情）
- 实时转写 + 关键词提醒
- 录像回放

### 案例 3：跨国会议

- 多 SFU region 部署
- 中转 Bridge SFU
- AI 实时翻译（多语言字幕）
- 自动纪要
