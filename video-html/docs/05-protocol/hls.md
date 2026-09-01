---
title: HLS 协议
date: 2026-08-15  # date-auto-injected
---

![流媒体协议对比](/video-streaming-protocols.svg)

# HLS（HTTP Live Streaming）

<span class="kg-badge kg-badge-protocol">协议</span>
<span class="kg-badge kg-badge-app">播放</span>

**HLS** = Apple 开发的**基于 HTTP 的流媒体协议**，将视频切分为**小 TS 文件 + m3u8 索引**，CDN 友好。

## 📊 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 2009 (Apple) |
| 标准 | RFC 8216 |
| 传输 | HTTP/HTTPS |
| 延迟 | 5-30 秒（普通），2-5 秒（LL-HLS） |
| 用途 | **点播 / 直播播放** |
| 容器 | TS / CMAF / fMP4 |
| 编码 | 任意（H.264/H.265/AV1） |

## 🏗️ HLS 工作原理

```
原始视频 → 切片 → N 个 .ts 文件 + 索引 .m3u8

m3u8 (索引)
├─ #EXTM3U
├─ #EXT-X-VERSION:3
├─ #EXT-X-TARGETDURATION:6
├─ #EXT-X-MEDIA-SEQUENCE:0
├─ #EXTINF:6.0,
├─ segment0.ts
├─ #EXTINF:6.0,
├─ segment1.ts
└─ ...

播放器: 下载 m3u8 → 按顺序下载 ts → 拼接播放
```

## 📐 M3U8 标签

### 主索引（Master Playlist）

```m3u8
#EXTM3U
#EXT-X-VERSION:6
#EXT-X-STREAM-INF:BANDWIDTH=2000000,RESOLUTION=1280x720,CODECS="avc1.64001f,mp4a.40.2"
720p.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=500000,RESOLUTION=640x360
360p.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=128000
audio.m3u8
```

### 媒体索引（Media Playlist）

```m3u8
#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:6
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-PLAYLIST-TYPE:VOD
#EXTINF:5.005,
segment0.ts
#EXTINF:5.005,
segment1.ts
...
#EXT-X-ENDLIST
```

### 关键标签

| 标签 | 含义 |
| --- | --- |
| `#EXTM3U` | 标记 M3U8 起始 |
| `#EXT-X-VERSION` | 版本 |
| `#EXT-X-TARGETDURATION` | 最大切片时长 |
| `#EXT-X-MEDIA-SEQUENCE` | 起始序号 |
| `#EXTINF:duration,` | 单个切片时长 |
| `#EXT-X-ENDLIST` | 结束标记（点播） |
| `#EXT-X-STREAM-INF` | 多码率描述 |
| `#EXT-X-PLAYLIST-TYPE` | VOD / EVENT |
| `#EXT-X-KEY` | 加密 |
| `#EXT-X-DISCONTINUITY` | 不连续 |

## 📊 HLS 切片策略

| 切片时长 | 延迟 | 适用 |
| --- | --- | --- |
| 1-2s | 2-5s | LL-HLS |
| 4-6s | 8-12s | 标准直播 |
| 10s | 20-30s | 大切片、点播 |
| 30s+ | - | 点播优化 |

## 🎬 多码率自适应（ABR）

```
播放器根据网络速度选择合适码率：

带宽 1 Mbps → 360p
带宽 3 Mbps → 720p
带宽 5 Mbps → 1080p
带宽 10 Mbps → 1080p 高码率

播放器逻辑:
  1. 下载 master.m3u8
  2. 下载 360p.m3u8 起始切片
  3. 测量下载速度
  4. 切换码率
```

### ABR 算法

| 算法 | 厂商 |
| --- | --- |
| **BOLA** | MIT |
| **Pensieve** | MIT |
| **Throughput-based** | 多数播放器 |
| **Buffer-based** | BBA |
| **Hybrid** | 结合 |

## 📐 HLS 加密

```m3u8
#EXT-X-KEY:METHOD=AES-128,URI="https://keyserver.com/key",IV=0x9c7db8778570d05c3177c349fd9236af

加密: AES-128-CBC
密钥: 服务器动态下发
IV: 初始化向量
```

## 🛠️ FFmpeg 生成 HLS

```bash
# 点播 HLS
ffmpeg -i input.mp4 \
       -c:v libx264 -c:a aac \
       -hls_time 6 -hls_list_size 0 \
       -hls_segment_filename "segment%03d.ts" \
       playlist.m3u8

# 直播 HLS（滑动窗口）
ffmpeg -i input.mp4 \
       -c:v libx264 -c:a aac \
       -hls_time 4 -hls_list_size 6 \
       -hls_flags delete_segments \
       live.m3u8

# 多码率 HLS（需要 x264+x265 两路）
ffmpeg -i input.mp4 -map 0 -map 0 \
       -c:v libx264 -b:v:0 800k -s:v:0 640x360 \
       -c:v libx265 -b:v:1 2M -s:v:1 1280x720 \
       -c:a aac -ac 2 -ar 48000 \
       -f hls -hls_time 4 -hls_list_size 0 \
       -hls_segment_filename "v%v/seg%03d.ts" \
       -master_pl_name master.m3u8 \
       -var_stream_map "v:0,a:0 v:1,a:0" \
       master.m3u8

# CMAF (fMP4)
ffmpeg -i input.mp4 \
       -c:v libx264 -c:a aac \
       -hls_segment_type fmp4 \
       -hls_time 4 -hls_list_size 0 \
       playlist.m3u8
```

## 📊 HLS vs DASH

| 特性 | HLS | DASH |
| --- | --- | --- |
| 推出 | 2009 (Apple) | 2012 (MPEG) |
| 索引 | m3u8 | MPD (XML) |
| 切片 | TS / fMP4 | fMP4 / WebM |
| 浏览器 | Safari / iOS 原生 | 需 MSE |
| 加密 | AES-128 | Common Encryption |
| CDN | 友好 | 友好 |

## 🎯 LL-HLS（低延迟 HLS）

**Low-Latency HLS**（2020）：延迟从 5-30s 降至 2-5s

```
LL-HLS 特性:
  - HTTP/2 push
  - 部分片段（partial segments）
  - 预加载提示（preload hint）
  - 块请求（blocking playlist）

需要: HTTP/2 服务器 + 客户端支持
```

## 📊 播放器

| 播放器 | 平台 | HLS 支持 |
| --- | --- | --- |
| **Safari** | iOS/Mac | 原生 |
| **hls.js** | Web | MSE 模拟 |
| **Video.js** | Web | 通过 hls.js |
| **ExoPlayer** | Android | 原生 |
| **AVPlayer** | iOS | 原生 |
| **VLC** | 跨平台 | 原生 |

## 📌 面试考点

1. HLS 延迟为什么高？
   - 切片 + m3u8 + 缓冲 ≈ 5-30s
2. HLS vs RTMP？
   - HLS 延迟高但 CDN 友好；RTMP 延迟低但需专门服务器
3. CMAF 优势？
   - 同一 fMP4 切片 HLS/DASH 共用
4. LL-HLS 如何实现？
   - HTTP/2 + 部分片段 + 预加载

## 🔗 下一步

- [DASH](/05-protocol/dash)
- [WebRTC](/05-protocol/webrtc)
- [CDN 架构](/05-protocol/cdn-arch)