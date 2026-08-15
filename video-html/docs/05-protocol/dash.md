---
title: DASH 协议
---

# DASH（MPEG-DASH）

<span class="kg-badge kg-badge-protocol">协议</span>
<span class="kg-badge kg-badge-app">播放</span>

**DASH** = Dynamic Adaptive Streaming over HTTP，MPEG 主导的 HTTP 自适应流协议，对标 HLS。

## 📊 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 2012 |
| 标准 | ISO/IEC 23009-1 |
| 传输 | HTTP/HTTPS |
| 延迟 | 5-30 秒 |
| 用途 | **点播 / 直播播放** |
| 容器 | fMP4 / WebM / TS |
| 索引 | MPD (XML) |

## 🏗️ DASH 架构

```
原始视频 → 切片 + 编码多版本 → MPD 索引

播放器: 下载 MPD → 选择 Representation → 下载 Segment → 播放
```

## 📐 MPD 结构

```xml
<?xml version="1.0"?>
<MPD xmlns="urn:mpeg:dash:schema:mpd:2011"
     type="dynamic"
     minBufferTime="PT2S"
     profiles="urn:mpeg:dash:profile:isoff-live:2011"
     publishTime="2026-08-06T10:00:00Z">

  <Period id="1" start="PT0S">
    <AdaptationSet contentType="video" mimeType="video/mp4">
      <Representation id="1" bandwidth="200000" width="640" height="360">
        <BaseURL>video_360p/</BaseURL>
        <SegmentTemplate media="$RepresentationID$/seg-$Number$.m4s"
                        initialization="$RepresentationID$/init.mp4"
                        timescale="1000" duration="4000"
                        startNumber="1"/>
      </Representation>
      <Representation id="2" bandwidth="500000" width="1280" height="720">
        <BaseURL>video_720p/</BaseURL>
        ...
      </Representation>
    </AdaptationSet>

    <AdaptationSet contentType="audio" mimeType="audio/mp4">
      <Representation id="audio" bandwidth="128000">
        <BaseURL>audio/</BaseURL>
        ...
      </Representation>
    </AdaptationSet>
  </Period>

</MPD>
```

## 📐 MPD 核心概念

| 元素 | 含义 |
| --- | --- |
| **MPD** | 根元素，描述整个流 |
| **Period** | 时间段（一段连续内容） |
| **AdaptationSet** | 同一媒体类型的多码率集合 |
| **Representation** | 单个码率版本 |
| **Segment** | 实际切片 |

### MPD 类型

| 类型 | 含义 |
| --- | --- |
| `static` | 静态（点播） |
| `dynamic` | 动态（直播） |

## 📊 DASH 切片容器

| 容器 | 支持 |
| --- | --- |
| **fMP4** (CMAF) | 标准 |
| **WebM** | 开源 |
| **TS** | 兼容 HLS |

## 🛠️ FFmpeg 生成 DASH

```bash
# 单码率 DASH
ffmpeg -i input.mp4 \
       -c:v libx264 -c:a aac \
       -f dash \
       -seg_duration 4 \
       -use_template 1 \
       -use_timeline 1 \
       -adaptation_sets "id=0,streams=v id=1,streams=a" \
       manifest.mpd

# 多码率 DASH
ffmpeg -i input.mp4 \
       -map 0:v -map 0:v -map 0:a \
       -c:v libx264 -b:v:0 800k -s:v:0 640x360 \
       -c:v libx264 -b:v:1 2M -s:v:1 1280x720 \
       -c:a aac -b:a 128k \
       -f dash -seg_duration 4 \
       -use_template 1 \
       manifest.mpd
```

## 📊 DASH vs HLS

| 特性 | HLS | DASH |
| --- | --- | --- |
| 推出 | 2009 (Apple) | 2012 (MPEG) |
| 标准组织 | Apple (RFC 8216) | MPEG (ISO) |
| 索引格式 | m3u8 (文本) | MPD (XML) |
| 切片容器 | TS / CMAF fMP4 | fMP4 / WebM |
| 加密 | AES-128 | CENC + CBC/CTR |
| 多 DRM | FairPlay | Widevine / PlayReady |
| 浏览器 | Safari 原生 | MSE |
| 移动 | iOS 原生 | Android 原生 |
| 低延迟 | LL-HLS | LL-DASH |

## 📐 DASH 加密 (CENC)

```xml
<ContentProtection 
  schemeIdUri="urn:mpeg:dash:mp4protection:2011"
  value="cenc"
  cenc:default_KID="9c7db877-8570-d05c-3177-c349fd9236af"/>
```

| 加密 | 模式 |
| --- | --- |
| **CENC** | Common Encryption |
| **CBC** | Cipher Block Chaining |
| **CTR** | Counter |

## 📊 DASH 行业支持

| 平台 | DASH |
| --- | --- |
| **Netflix** | 主用 |
| **YouTube** | 主用 |
| **Amazon Prime** | 主用 |
| **Apple TV+** | FairPlay + DASH |
| **Disney+** | DASH |
| **Twitch** | DASH |
| **Hulu** | DASH |

## 📐 播放器

| 播放器 | 平台 |
| --- | --- |
| **dash.js** | Web |
| **Shaka Player** | Web / Android |
| **ExoPlayer** | Android |
| **AVPlayer** | iOS |
| **Bitmovin** | 商业 |
| **THEOplayer** | 商业 |

## 📊 CMAF（Common Media Application Format）

CMAF = 让 HLS 和 DASH 共用 **fMP4 切片**。

```
输入视频
  ↓
编码为 fMP4（CMAF 切片）
  ↓
[用于 HLS] → m3u8 索引
[用于 DASH] → MPD 索引

一份切片，两套协议 → CDN 缓存复用
```

## 🎯 DASH 优势

✅ 工业标准
✅ 多 DRM 支持
✅ 灵活的 ABR
✅ 与 HLS 共用切片
✅ 可表达复杂场景（多视角、字幕）
✅ 直播 + 点播统一

## 🎯 DASH 劣势

❌ 比 HLS 复杂
❌ 浏览器需 MSE
❌ MPD 难以手写
❌ 切片长度兼容性

## 📌 面试考点

1. DASH vs HLS 选择？
   - 跨平台播放选 DASH；iOS 生态选 HLS
2. CMAF 优势？
   - HLS + DASH 共用切片，CDN 友好
3. MPD 主要元素？
   - Period / AdaptationSet / Representation / Segment
4. DASH 如何加密？
   - CENC + CBC/CTR + DRM

## 🔗 下一步

- [HLS](/05-protocol/hls)
- [WebRTC](/05-protocol/webrtc)
- [CDN 架构](/05-protocol/cdn-arch)