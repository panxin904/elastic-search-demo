---
title: RTSP / SRT
date: 2026-08-15  # date-auto-injected
---

# RTSP / SRT 流媒体协议

<span class="kg-badge kg-badge-protocol">协议</span>
<span class="kg-badge kg-badge-app">监控</span>

**RTSP**（传统监控） + **SRT**（新一代安全传输）= 监控和广电领域的**主力协议**。

## 📊 RTSP（Real-Time Streaming Protocol）

### 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 1998（哥伦比亚/Netscape） |
| 标准 | RFC 2326 |
| 传输 | TCP（控制）+ UDP（媒体） |
| 端口 | 554（RTSP）/ 5004/5005（RTP） |
| 延迟 | <1s |
| 用途 | **监控**、IP 摄像头、视频会议 |
| 编码 | H.264/H.265 + AAC/G.711 |

### RTSP URL 格式

```
rtsp://[user:pass@]host[:port]/path

例:
  rtsp://admin:12345@192.168.1.100:554/Streaming/Channels/101
  rtsp://camera.local:554/live/stream1
```

### RTSP 流程

```
C → S: OPTIONS
S → C: Public methods

C → S: DESCRIBE
S → C: SDP (媒体描述)

C → S: SETUP
S → C: Transport (端口/模式)

C → S: PLAY
S → C: 开始 RTP 传输

C → S: TEARDOWN
S → C: 停止
```

### RTSP 方法

| 方法 | 含义 |
| --- | --- |
| `OPTIONS` | 询问支持的方法 |
| `DESCRIBE` | 媒体描述 |
| `ANNOUNCE` | 推送描述 |
| `SETUP` | 建立传输 |
| `PLAY` | 开始播放 |
| `PAUSE` | 暂停 |
| `TEARDOWN` | 停止 |
| `GET_PARAMETER` | 读取参数 |
| `SET_PARAMETER` | 修改参数 |

### RTSP 与 RTP/RTCP

```
RTSP: 控制协议（PLAY, PAUSE...）
RTP:  实时传输（媒体数据）
RTCP: 实时控制（QoS 反馈）

RTSP over TCP
RTP over UDP（实时）
```

## 📊 SRT（Secure Reliable Transport）

### 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 2017（Haivision） |
| 标准 | 开源 |
| 传输 | UDP（可靠） |
| 延迟 | <1s（可调） |
| 用途 | 广电、远程制作、直播推流 |
| 加密 | AES-128/256 |
| 抗丢包 | ARQ + FEC |

### SRT 工作原理

```
SRT 在 UDP 上实现可靠传输：

1. 加密：AES-128/256
2. 压缩：可选
3. 抗丢包：
   - ARQ（Automatic Repeat reQuest）自动重传
   - FEC（Forward Error Correction）前向纠错
4. 拥塞控制：实时监测
```

### SRT URL 格式

```
srt://host:port?option=value

例:
  srt://192.168.1.100:9000?mode=caller&latency=120
  srt://server:9999?passphrase=mysecret&pbkeylen=16&latency=200

参数:
  mode: caller / listener / rendezvous
  latency: 缓冲区延迟 (ms)
  passphrase: AES 密钥
  pbkeylen: 密钥长度 (16/24/32)
  oheadbw: 开销带宽比例
  rcvbuf/sndbuf: 缓冲区大小
```

### SRT 三种模式

| 模式 | 说明 |
| --- | --- |
| **Caller** | 主动连接 |
| **Listener** | 等待连接 |
| **Rendezvous** | 双向握手 |

### SRT vs RTMP vs RTSP

| 协议 | 抗丢包 | 加密 | 延迟 | 用途 |
| --- | --- | --- | --- | --- |
| **RTMP** | TCP 重传 | 无 | 1-3s | 直播 |
| **RTSP** | UDP 无 | 无 | <1s | 监控 |
| **SRT** | ARQ + FEC | AES-128 | <1s | 广电、远程 |
| **WebRTC** | NACK | DTLS | <500ms | 互动 |
| **RIST** | ARQ + FEC | DTLS | <1s | 广电 |

## 📊 RIST（Reliable Internet Stream Transport）

### 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 2017 |
| 状态 | 业界标准 |
| 传输 | UDP + ARQ + FEC |
| 用途 | 广电远程制作 |
| 与 SRT 关系 | 类似目标，不同实现 |

### RIST vs SRT

| 特性 | SRT | RIST |
| --- | --- | --- |
| 加密 | AES | DTLS |
| 抗丢包 | ARQ + FEC | ARQ + FEC |
| 多路 | 简单 | 复杂 |
| 厂商 | Haivision | 开放标准 |

## 📊 监控协议对比

| 协议 | 厂商 | 用途 |
| --- | --- | --- |
| **RTSP** | ONVIF 标准 | 主流 |
| **ONVIF** | 行业标准 | 设备兼容 |
| **GB/T 28181** | 国标 | 中国监控 |
| **PSIA** | 物理互操作 | 历史 |

### GB/T 28181

```
中国国标监控协议：

- SIP 信令
- RTP 媒体
- 注册到中心平台
- 跨厂商互连
```

## 📊 FFmpeg RTSP / SRT

```bash
# RTSP 拉流
ffmpeg -rtsp_transport tcp -i rtsp://admin:12345@192.168.1.100:554/stream \
       -c copy out.mp4

# RTSP 推流
ffmpeg -re -i input.mp4 \
       -c:v libx264 -c:a aac \
       -f rtsp rtsp://server/live/stream

# SRT 推流
ffmpeg -re -i input.mp4 \
       -c:v libx264 -preset ultrafast \
       -f mpegts 'srt://server:9999?mode=caller&latency=120'

# SRT 拉流
ffmpeg -i 'srt://server:9999?mode=listener&latency=120' \
       -c copy out.ts

# RTSP → HLS 转换
ffmpeg -rtsp_transport tcp -i rtsp://camera/stream \
       -c:v libx264 -c:a aac \
       -hls_time 4 -hls_list_size 6 \
       live.m3u8
```

## 🛠️ 流媒体服务器

| 服务器 | 协议 |
| --- | --- |
| **MediaMTX** | RTSP / SRT / WebRTC / RTMP |
| **Live555** | RTSP（参考实现） |
| **FFmpeg** | 通用 |
| **SRS** | RTMP / HLS / WebRTC / SRT |
| **Nginx-RTMP** | RTMP / HLS |
| **OBS** | 推流客户端 |

## 📌 面试考点

1. RTSP 怎么用？
   - URL: `rtsp://user:pass@ip:554/path`
2. SRT 抗丢包原理？
   - ARQ 自动重传 + FEC 前向纠错
3. SRT vs RTMP？
   - SRT UDP 抗丢包 + 加密；RTMP TCP 简单
4. GB/T 28181 是什么？
   - 中国国标监控协议

## 🔗 下一步

- [RTMP](/05-protocol/rtmp)
- [WebRTC](/05-protocol/webrtc)
- [CDN 架构](/05-protocol/cdn-arch)
- [安防监控](/10-application/surveillance)