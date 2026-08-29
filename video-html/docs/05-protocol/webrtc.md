---
title: WebRTC
date: 2026-08-15  # date-auto-injected
---

# WebRTC（Web Real-Time Communication）

<span class="kg-badge kg-badge-protocol">协议</span>
<span class="kg-badge kg-badge-app">实时</span>
<span class="kg-badge kg-badge-ai">互动</span>

**WebRTC** = 浏览器原生**实时音视频通信**协议栈，延迟 <500ms，支持 P2P。

## 📊 基本信息

| 项 | 值 |
| --- | --- |
| 标准 | W3C + IETF |
| 推出 | 2011（Google 开源） |
| 延迟 | **<500ms**（P2P）、<200ms（理想） |
| 传输 | UDP / SRTP / SCTP |
| 编码 | VP8 / VP9 / H.264 / AV1 + Opus |
| 用途 | 视频会议、互动直播、低延迟 |
| 浏览器 | Chrome/Firefox/Safari/Edge |

## 🏗️ WebRTC 三大组件

| 组件 | 作用 |
| --- | --- |
| **MediaStream (getUserMedia)** | 音视频采集 |
| **RTCPeerConnection** | P2P 媒体传输 |
| **RTCDataChannel** | 数据通道（任意数据） |

## 📐 协议栈

```
┌────────────────────────────────┐
│         JavaScript API         │  ← 浏览器提供
├────────────────────────────────┤
│  RTCPeerConnection / DataChannel│
├────────────────────────────────┤
│ SRTP (Secure RTP) / SCTP / DTLS│  ← 媒体加密传输
├────────────────────────────────┤
│      ICE / STUN / TURN         │  ← NAT 穿透
├────────────────────────────────┤
│   UDP / TCP                    │
└────────────────────────────────┘
```

## 📊 关键协议

| 协议 | 作用 |
| --- | --- |
| **RTP / RTCP** | 实时传输协议 |
| **SRTP** | Secure RTP（加密） |
| **DTLS** | UDP 上的 TLS |
| **ICE** | Interactive Connectivity Establishment |
| **STUN** | NAT 穿透客户端 |
| **TURN** | 中继穿透（兜底） |
| **SDP** | Session Description Protocol |
| **SCTP** | 数据通道传输 |

## 🔄 WebRTC 建立连接流程

```
1. MediaStream 采集（getUserMedia）

2. RTCPeerConnection 创建
   pc = new RTCPeerConnection()

3. 信令交换（Signaling）- 通过 WebSocket/SIP
   A → SDP Offer (SDP, ICE candidates)
   B → SDP Answer

4. ICE 连接性检查
   STUN 请求 → 收集 Candidate
   选择最佳路径

5. DTLS 握手（加密）

6. SRTP 媒体流传输

7. 双向 RTCP 反馈（带宽、丢包）

8. 媒体协商（编码器）
   Codec negotiation via SDP
```

## 📐 SDP 示例

```
v=0
o=- 123456 2 IN IP4 0.0.0.0
s=-
t=0 0
m=audio 9 UDP/TLS/RTP/SAVPF 111 63 9 0 8 13
c=IN IP4 0.0.0.0
a=rtpmap:111 opus/48000/2
a=rtpmap:63 red/48000/2
a=rtpmap:9 G722/8000
a=rtpmap:0 PCMU/8000
a=rtpmap:8 PCMA/8000
a=rtpmap:13 CN/32000
a=rtcp:9 IN IP4 0.0.0.0
a=ice-ufrag:xxxx
a=ice-pwd:xxxxxxxxxxxxxxxxxxxxxxxxxxxx
a=fingerprint:sha-256 xx:xx:xx...
a=setup:actpass
a=mid:0
a=sendrecv
m=video 9 UDP/TLS/RTP/SAVPF 96 97 98 99 100 101 102 121 125 107 108 109 35 36 124 119 123 118 117 38 40 43 97 98 99 100 101 112 113 116
c=IN IP4 0.0.0.0
a=rtpmap:96 VP8/90000
a=rtpmap:97 rtx/90000
a=rtpmap:98 VP9/90000
...
a=rtpmap:125 H264/90000
a=rtpmap:107 H265/90000
a=rtcp:9 IN IP4 0.0.0.0
...
```

## 📊 NAT 穿透（ICE）

```
ICE Candidate 类型:
  - host: 本地 IP（局域网）
  - srflx: STUN 返回的公网 IP
  - relay: TURN 中继地址
  - prflx: 对端反射

连接建立:
  1. Host ↔ Host（局域网直连）← 最低延迟
  2. Srflx ↔ Srflx（STUN 穿透）← 多数情况
  3. Relay ↔ Relay（TURN 中继）← 兜底，延迟高
```

## 📐 WebRTC 拥塞控制

| 算法 | 厂商 |
| --- | --- |
| **GCC** | Google |
| **SCReAM** | Ericsson |
| **NADA** | Cisco |
| **RMCAT** | IETF 标准 |
| **BBR** | Google（实验） |

### GCC 工作原理

```
基于延迟变化估计带宽:
  1. 监测 RTT 变化
  2. 计算过载程度
  3. 调整发送码率

基于丢包率:
  丢包 > 10% → 降速
  丢包 < 2%  → 加速
```

## 📊 WebRTC vs RTMP vs HLS

| 协议 | 延迟 | 传输 | 用途 |
| --- | --- | --- | --- |
| **WebRTC** | <500ms | UDP/SRTP | 实时互动 |
| **RTMP** | 1-3s | TCP | 直播推流 |
| **HLS** | 5-30s | HTTP | 点播/直播播放 |

## 📐 SFU vs MCU vs P2P

### P2P（Mesh）

```
3 人会议: 3×2 = 6 个连接

优点: 最低延迟
缺点: 上行带宽大（多人不可扩展）
```

### SFU（Selective Forwarding Unit）

```
所有客户端 → SFU → 所有客户端

优点: 客户端上行只需 1 路
缺点: SFU 服务端压力大
主流: Janus / Mediasoup / LiveKit
```

### MCU（Multipoint Control Unit）

```
所有客户端 → MCU 混流 → 客户端

优点: 客户端负载小
缺点: 服务端混流延迟高
```

## 📊 主流 WebRTC 服务

| 服务 | 特点 |
| --- | --- |
| **LiveKit** | 开源 SFU，云原生 |
| **Mediasoup** | Node.js SFU |
| **Janus** | C 语言 SFU |
| **mediasoup-client** | 浏览器 |
| **PeerJS** | 简化 P2P |
| **Agora** | 商业 + SDK |
| **声网 Agora** | 中国领先 |
| **Twilio** | 商业 |

## 🛠️ FFmpeg WebRTC

```bash
# FFmpeg 不直接支持 WebRTC，但可通过 libwebrtc
# 通常使用 Web 客户端或专用 SDK

# FFmpeg → WebRTC 推流（用 go2rtc 等中转）
ffmpeg -re -i input.mp4 -c:v libx264 -preset ultrafast \
       -tune zerolatency -f rtp rtp://127.0.0.1:5004
```

## 📊 浏览器 API 示例

```javascript
// 1. 获取媒体流
const stream = await navigator.mediaDevices.getUserMedia({
  audio: true,
  video: { width: 1280, height: 720 }
});

// 2. 创建连接
const pc = new RTCPeerConnection({
  iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
});

// 3. 添加本地流
stream.getTracks().forEach(t => pc.addTrack(t, stream));

// 4. 创建 Offer
const offer = await pc.createOffer();
await pc.setLocalDescription(offer);

// 5. 通过信令服务器发送 Offer，等待 Answer
signalChannel.send(JSON.stringify(offer));

// 6. 接收 Answer
const answer = JSON.parse(await signalChannel.receive());
await pc.setRemoteDescription(answer);

// 7. 监听远端流
pc.ontrack = e => {
  remoteVideo.srcObject = e.streams[0];
};
```

## 📌 面试考点

1. WebRTC 为什么延迟低？
   - UDP + 无 chunk buffer + NACK 快速重传
2. WebRTC vs RTMP？
   - WebRTC <500ms 互动；RTMP 1-3s 单向推流
3. P2P vs SFU？
   - 2-3 人 P2P；3+ 人 SFU
4. ICE 穿透原理？
   - STUN 探测公网 IP；TURN 中继兜底

## 🔗 下一步

- [RTMP](/05-protocol/rtmp)
- [HLS](/05-protocol/hls)
- [CDN 架构](/05-protocol/cdn-arch)
- [视频会议](/10-application/conference)