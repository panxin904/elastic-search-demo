---
title: 直播技术
---

# 直播技术体系

<span class="kg-badge kg-badge-app">应用</span>
<span class="kg-badge kg-badge-protocol">实时</span>
<span class="kg-badge kg-badge-cloud">云端</span>

直播是 **实时音视频传输** 场景的代表，覆盖 **娱乐 / 带货 / 教育 / 体育** 等行业。

## 🏗️ 直播技术架构

```
┌────────────────────────────────────────────────────┐
│ 推流端                                              │
│ 摄像采集 + 美颜 + 编码 + 推流                       │
├────────────────────────────────────────────────────┤
│ 服务端                                              │
│ 接入集群 ── 转码集群 ── 录制集群 ── 审核集群 ── CDN │
│     ↓          ↓          ↓          ↓           ↓ │
│   RTMP      实时转码     录制        AI         边缘分发│
├────────────────────────────────────────────────────┤
│ 播放端                                              │
│ 多端播放器 + 弹幕 / 互动 + 心跳统计                 │
└────────────────────────────────────────────────────┘
```

## 📊 直播分类

| 类型 | 延迟 | 协议 | 场景 |
| --- | --- | --- | --- |
| **传统直播** | 1-3s | RTMP / HTTP-FLV | 娱乐、带货 |
| **互动直播** | 300-500ms | WebRTC / LLS | 互动连麦 |
| **超低延迟直播** | < 1s | WebRTC / Quic | 赛事、电竞 |
| **AI 直播** | 异步 | 自动化 | 数字人直播 |

## 📤 推流端技术

### 推流协议

| 协议 | 延迟 | 兼容 | 用法 |
| --- | --- | --- | --- |
| **RTMP** | 1-3s | 高（传统） | 主播推流 |
| **SRT** | < 1s | 中 | 跨区域 |
| **WebRTC** | < 300ms | 新 | 互动直播 |
| **QUIC** | < 500ms | 新 | 替代 RTMP |

### OBS / 编码器推流

```bash
# RTMP 推流
ffmpeg -re -i input.mp4 \
  -c:v libx264 -preset veryfast -tune zerolatency \
  -b:v 4000k -maxrate 4000k -bufsize 8000k \
  -g 60 -bf 0 \
  -c:a aac -b:a 128k -ar 44100 \
  -f flv rtmp://server/live/stream-key
```

### 移动端推流（Android 例子）

```java
// 硬编 + RTMP 推流
MediaCodec encoder = MediaCodec.createEncoderByType("video/avc");
encoder.configure(format, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE);

// 原始数据 → 编码 → RTMP 推流
// 简化版：使用第三方 SDK（如金山云、阿里云 SDK）
```

### 推流 SDK

| 厂商 | iOS / Android / Web |
| --- | --- |
| **腾讯云移动直播** | ✅ |
| **阿里云音视频** | ✅ |
| **声网 Agora** | ✅ |
| **七牛云** | ✅ |
| **即构 ZEGO** | ✅ |

## 🎬 推流参数详解

### 视频参数

| 参数 | 推荐范围 |
| --- | --- |
| **分辨率** | 720p (1280×720) |
| **帧率** | 25-30 fps |
| **码率** | 2000-4000 kbps |
| **GOP** | 2-4s (50-100) |
| **Profile** | High |
| **编码器** | libx264 / NVENC |

### 音频参数

| 参数 | 推荐 |
| --- | --- |
| **采样率** | 44.1kHz |
| **声道** | 双声道 |
| **码率** | 128kbps |
| **编码** | AAC-LC / Opus |

### x264 zerolatency 推流参数

```bash
-x264-params "keyint=60:min-keyint=60:scenecut=0:bframes=0:ref=1:rc-lookahead=0:sync-lookahead=0"
```

## 🔄 服务端处理

### 接入集群

```
RTMP 推流 (1935) → Nginx-RTMP / SRS / 自研集群
                        ↓
                   协议转换
                        ↓
           HLS / HTTP-FLV / DASH 输出
                        ↓
                   录制到对象存储
                        ↓
                   转码 (可选)
```

### 主流流媒体服务器

| 服务 | 语言 | 特点 |
| --- | --- | --- |
| **Nginx-RTMP** | C | 轻量、模块化 |
| **SRS (Simple RTMP Server)** | C++ | 高性能、国人开源 |
| **ZLMediaKit** | C++ | 多协议、WebRTC |
| **MediaServer** | C++ | ZLMediaKit 同上 |
| **自研** | Go/C++ | 大厂定制 |

### SRS 推流配置

```nginx
# SRS 配置
listen 1935;
max_connections 1000;

vhost __defaultVhost__ {
    enable_hls on;
    hls_path /tmp/hls;
    hls_fragment 5s;
    hls_window 10s;

    # HTTP-FLV
    http_remux {
        enabled on;
        mount v1/live;
    }
}
```

### 转码集群

```
RTMP Ingest → GOP 切分 → 多 worker (GPU) → RTMP / HLS Out
                                          ↓
                                      对象存储
```

## 🎥 录制与回放

### 实时录制

| 方式 | 描述 |
| --- | --- |
| **拉流录制** | 服务端拉流写盘 |
| **推流旁路** | 边推流边录制 |
| **录制转码** | 录制后自动转码 |

### HLS 切片

```
HLS (HTTP Live Streaming)
├─ playlist.m3u8          ← 主清单
├─ playlist_720p.m3u8     ← 720p
├─ playlist_540p.m3u8     ← 540p
├─ segment_001.ts         ← 切片
├─ segment_002.ts
└─ ...
```

### MP4 录制（按需点播）

```python
# ffmpeg 拉流录制
import subprocess

subprocess.run([
    'ffmpeg', '-y', '-i', 'rtmp://server/live/key',
    '-c', 'copy',
    '-f', 'mp4',
    'record.mp4'
])
```

## 📡 播放端技术

### 播放器选型

| 平台 | 自研 / 三方 |
| --- | --- |
| **iOS** | AVPlayer / 阿里云播放器 |
| **Android** | ExoPlayer / 阿里云播放器 |
| **Web** | video.js / hls.js / 腾讯云 TCPlayer |
| **小程序** | live-player 组件 |

### Web 播放 RTMP（过时，仅列举）

- 不再推荐 RTMP，需要 HTTP-FLV / HLS

### Web 播放 HLS

```html
<video id="player" controls></video>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
<script>
  const video = document.getElementById('player');
  if (Hls.isSupported()) {
    const hls = new Hls();
    hls.loadSource('https://cdn.example/live/playlist.m3u8');
    hls.attachMedia(video);
  }
</script>
```

### Web 播放 WebRTC

```javascript
const pc = new RTCPeerConnection();
pc.addTransceiver('video', {direction: 'recvonly'});
pc.addTransceiver('audio', {direction: 'recvonly'});

pc.ontrack = (event) => {
    document.getElementById('remoteVideo').srcObject = event.streams[0];
};

pc.setRemoteDescription(new RTCSessionDescription(answer));
```

## 💬 互动系统

### 弹幕

```
WebSocket → Server (群发) → 所有 Client
                            ↓
                     礼物 / 评论 / 点赞
```

### 连麦（PK / 多人视频）

```
推流端 A ──┐
推流端 B ──┼─→ MCU 混流 → 主播端 → CDN → 观众
推流端 C ──┘
```

### 实时消息（IM）

- WebSocket 长连接
- 弹幕 / 评论 / 礼物 / 系统通知

## 📈 直播 SLA 与监控

### 关键指标

| 指标 | 监控方式 |
| --- | --- |
| **推流成功率** | 推流回调 |
| **播放秒开率** | 首帧日志 |
| **卡顿率** | buffer 数据 |
| **延迟分布** | 端到端探测 |
| **推流码率** | 服务端统计 |

### 典型 SLA

| 指标 | 目标 |
| --- | --- |
| 推流成功 | > 99.5% |
| 播放秒开 | > 95% (< 1s) |
| 卡顿率 | < 2% |
| 延迟 | < 1-3s（直播） |

## 🔥 场景案例

### 案例 1：电商带货

```
主播端 ── 推流 ──→ 接入 ──→ 转码 ──→ CDN
   ↓                                 ↓
 弹幕/礼物/商品推送               观众播放
   ↓
 商品 RPC 服务
```

特殊功能：
- 商品悬浮窗
- 倒计时推送
- AI 自动回复
- 多机位切换

### 案例 2：游戏直播

```
采集卡 → 编码器 → RTMP 推流 → CDN
                              ↓
                        弹幕服务器
                              ↓
                        录制 (录播存放对象存储)
```

### 案例 3：体育赛事 / 电竞

```
摄像机多机位 → 切换台 → 编码器 → RTMP/SRT
                                       ↓
                              LLS / WebRTC 输出
                                       ↓
                              互动直播
```

### 案例 4：在线教育大班课

```
教师端 → 推流 → CDN → 学生端
                         ↓
                  PPT 同步、答题、连麦
```

## 🤖 数字人直播（AI 直播）

```
数字人主播 (虚拟形象)
   ↓
   实时渲染
   ↓
   TTS 语音合成 (文本 → 语音)
   ↓
   Wav2Lip (唇形同步)
   ↓
   编码推流
   ↓
   实时互动直播
```

数字人组件：
- **SadTalker** / **MuseTalk**：唇形 + 表情
- **Wav2Lip** / **VideoReTalking**：口型同步
- **GPT-SoVITS** / **CosyVoice**：TTS 语音
- **Live2D** / **VRoid**：2D/3D 形象
- **HeyGen** / **D-ID**：商业数字人

## 💡 性能优化要点

### 推流端
- 硬编 (iOS: VTCompressionSession / Android: MediaCodec)
- 网络自适应（断线重连 + 码率调整）
- 弱网监控 + 降级

### 服务端
- 接入 + 转码分离
- 边缘计算 + 近距离转码
- GPU 批量转码

### 播放端
- 多 CDN 调度
- 首帧优化（预解析 m3u8）
- 缓冲策略（弱网减小）
- TCP/QUIC 双通道

## ⚠️ 合规与监管

### 必备资质

| 资质 | 用途 |
| --- | --- |
| **ICP 备案** | 国内合法域名 |
| **视听许可** | 直播业务 |
| **公安网监** | 网安要求 |
| **CDN 资质** | 跨网分发 |

### 内容合规

- 实时审核（违规内容实时屏蔽）
- 关键词过滤
- 黑名单管理
- 上传记录
- 用户实名

## 📚 推荐学习

- 《FFmpeg 从入门到精通》
- 《WebRTC 权威指南》
- 《实时音视频开发》
- SRS 官方文档
- ZLMediaKit Wiki
