---
title: RTMP 协议
---

# RTMP（Real-Time Messaging Protocol）

<span class="kg-badge kg-badge-protocol">协议</span>
<span class="kg-badge kg-badge-app">直播</span>

**RTMP** = 基于 TCP 的**实时消息传输协议**，由 Macromedia（Adobe）开发，广泛用于直播推流。

## 📊 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 2002（Macromedia） |
| 当前 | Adobe 拥有，已开源 |
| 传输 | TCP（端口 1935） |
| 延迟 | 1-3 秒 |
| 用途 | 直播**推流**（主播端 → 服务器） |
| 编码 | H.264/AAC/MP3 |
| 容器 | FLV / F4V |

## 🏗️ RTMP 架构

```
推流端              RTMP 服务器             拉流端
 (OBS / FFmpeg)   (Nginx-RTMP / SRS)    (VLC / Web)

RTMP推流 → 1935 → [接收 → 转码 → 分发] ← RTMP/HLS ← 播放
```

## 📐 RTMP 消息格式

```
RTMP Message:
  Header (12 byte):
    Format Type (1 bit)
    Chunk Stream ID (6 bit)
    Timestamp (3 byte)
    Message Length (3 byte)
    Message Type ID (1 byte)
    Message Stream ID (4 byte) [或 chunk stream id 之后]
  Body / Payload

Chunk (12+ byte):
  Basic Header (1-3 byte)
  Message Header (0/3/7/11 byte)
  Extended Timestamp (0/4 byte)
  Chunk Data
```

### 消息类型

| Type | 含义 |
| --- | --- |
| **1** | Set Chunk Size |
| **3** | Acknowledgement |
| **4** | User Control |
| **5** | Window Acknowledgement Size |
| **6** | Set Peer Bandwidth |
| **8** | Audio Message |
| **9** | Video Message |
| **15** | Data AMF0 (metadata) |
| **18** | Command Message AMF0 |
| **20** | Command Message AMF3 |

## 📊 RTMP 流程

```
1. Handshake (握手)
   C0 → S0: 版本号
   C1 → S1: 时间戳 + random
   C2 → S2: 验证
   S0, S1, S2 → C: 验证

2. Connect (连接)
   C → S: "connect" 命令
   S → C: Window Acknowledgement Size
   S → C: Set Peer Bandwidth
   S → C: Set Chunk Size
   S → C: "_result" 响应

3. Create Stream
   C → S: "releaseStream" / "FCPublish" / "createStream"

4. Publish / Play
   C → S: "publish" (推流) 或 "play" (拉流)

5. Stream Data
   C → S: Video / Audio Message

6. Close
   C → S: "deleteStream" / 关闭连接
```

## 📐 RTMP URL 格式

```
rtmp://server/app/streamKey

例:
  rtmp://live.example.com/live/stream123
  rtmp://push-hls.example.com:1935/live/mystream

常用端口: 1935
```

## 📊 变体协议

| 变体 | 含义 |
| --- | --- |
| **RTMP** | 原始（TCP） |
| **RTMPS** | RTMP + TLS 加密 |
| **RTMPE** | RTMP + 加密 |
| **RTMPT** | RTMP + HTTP 隧道 |
| **RTMFP** | UDP 版（已淘汰） |
| **Enhanced RTMP** | HEVC/AV1 支持 |

## 🛠️ FFmpeg RTMP 推流

```bash
# 推流到 RTMP 服务器
ffmpeg -re -i input.mp4 -c:v libx264 -c:a aac \
       -f flv rtmp://server/live/stream123

# 拉流（RTMP）
ffmpeg -i rtmp://server/live/stream123 -c copy out.flv

# RTMP → HLS（转换协议）
ffmpeg -i rtmp://server/live/stream123 \
       -c:v libx264 -c:a aac -hls_time 4 -hls_list_size 0 \
       out.m3u8

# RTMP → RTMP（转码）
ffmpeg -i rtmp://server/live/stream123 \
       -c:v libx264 -preset veryfast -b:v 2M \
       -c:a aac -b:a 128k \
       -f flv rtmp://server2/live/stream456
```

## 🛠️ 推流工具

| 工具 | 用途 |
| --- | --- |
| **OBS Studio** | 桌面推流 |
| **FFmpeg** | 命令行推流 |
| **Streamlabs** | 直播一体化 |
| **XSplit** | 专业推流 |
| **Wirecast** | 广电级 |

## 🛠️ RTMP 服务器

| 服务器 | 特点 |
| --- | --- |
| **Nginx-RTMP** | 经典、轻量 |
| **SRS (Simple Realtime Server)** | 国人开发、强大 |
| **MediaMTX** | Go 实现、多协议 |
| **Red5** | Java |
| **Wowza** | 商业、流媒体全功能 |

## 📊 RTMP 现状

```
✅ 优点:
  - 推流稳定（TCP）
  - 延迟低（1-3s）
  - 工具链成熟
  - 广泛支持（OBS/SRS）

❌ 缺点:
  - Adobe 不再维护规范
  - 不支持 HEVC（需 Enhanced RTMP）
  - 浏览器原生不支持（Flash 已死）
  - TCP 在弱网下表现差

当前: 仍为推流主流，HLS/WebRTC 用于播放
```

## 🎯 Enhanced RTMP

```
由 SRS 项目发起：
  - HEVC / AV1 支持
  - 多音轨
  - 改进 metadata
  - 向后兼容

URL: rtmp://server/live/stream (不变)
```

## 📌 面试考点

1. RTMP 延迟多少？
   - 1-3 秒（TCP + chunk buffer）
2. RTMP vs HLS？
   - RTMP 延迟低、适合推流；HLS 延迟高、适合播放
3. RTMP 怎么转 HLS？
   - 服务器收到 RTMP → 切片 → 生成 HLS
4. 浏览器为什么不支持 RTMP？
   - Flash 已淘汰（2020）

## 🔗 下一步

- [HLS](/05-protocol/hls)
- [WebRTC](/05-protocol/webrtc)
- [CDN 架构](/05-protocol/cdn-arch)