---
title: 容器格式 - MP4/AVI/MKV
date: 2026-08-15  # date-auto-injected
---

# 容器格式 - MP4 / AVI / MKV

<span class="kg-badge kg-badge-basics">基础</span>
<span class="kg-badge kg-badge-tools">FFmpeg</span>

**容器格式**（Container Format）= 视频的"包装盒"，包含视频流、音频流、字幕、元数据等。

## 📦 容器 vs 编码

| 概念 | 含义 | 关系 |
| --- | --- | --- |
| **容器** | 文件格式（MP4/MKV/AVI） | "盒子" |
| **编码** | 视频/音频压缩算法（H.264/AAC） | "内容" |

> 📌 **同一编码可以装在不同容器中**，例如 H.264 视频可以是 `.mp4`、`.mkv`、`.ts` 等。

## 🎬 主流容器对比

| 容器 | 扩展名 | 视频编码 | 音频编码 | 特点 |
| --- | --- | --- | --- | --- |
| **MP4** | .mp4 | H.264/H.265/AV1 | AAC | 最通用、流媒体标准 |
| **MKV** | .mkv | 几乎所有 | 几乎所有 | 开源、强大、字幕支持 |
| **AVI** | .avi | 几乎所有 | 几乎所有 | 老旧、微软、文件大 |
| **MOV** | .mov | 几乎所有 | AAC/PCM | Apple QuickTime |
| **FLV** | .flv | H.264/VP6 | AAC/MP3 | 直播（已被淘汰） |
| **WebM** | .webm | VP8/VP9/AV1 | Opus | HTML5 标准、YouTube |
| **TS** | .ts | H.264/H.265 | AAC | 广播电视、流媒体切片 |
| **MTS** | .mts | H.264 | AC-3 | Sony AVCHD 摄像机 |
| **3GP** | .3gp | H.263/H.264 | AMR | 早期手机视频 |
| **WMV** | .wmv | WMV | WMA | 微软 |
| **RMVB** | .rmvb | RV | RealAudio | 早期 BT 下载 |

## 📊 MP4 容器详解

### MP4 盒子结构

```
MP4 File
├── ftyp (File Type Box)
├── moov (Movie Box)
│   ├── mvhd (Movie Header)
│   ├── trak (Track Box)
│   │   ├── tkhd (Track Header)
│   │   ├── mdia (Media Box)
│   │   │   ├── mdhd (Media Header)
│   │   │   ├── hdlr (Handler Reference)
│   │   │   └── minf (Media Information)
│   │   │       ├── vmhd/smhd (Video/Sound Header)
│   │   │       ├── dinf (Data Information)
│   │   │       └── stbl (Sample Table)
│   │   │           ├── stsd (Sample Description)
│   │   │           ├── stts (Time-to-Sample)
│   │   │           ├── stss (Sync Sample = I帧)
│   │   │           └── stco (Chunk Offset)
│   └── udta (User Data)
└── mdat (Media Data - 实际音视频数据)
```

### moov 位置

| 模式 | 含义 |
| --- | --- |
| **moov 在前** | 文件可边下边播（推荐） |
| **moov 在后** | 必须下载完才能播 |

```bash
# moov 前移
ffmpeg -i input.mp4 -movflags +faststart output.mp4

# 使用 qt-faststart
qt-faststart input.mp4 output.mp4
```

## 📊 MKV 容器详解

**Matroska Video** = 开源通用容器，功能强大。

### MKV 特性

| 特性 | 说明 |
| --- | --- |
| 多轨道 | 无数视频/音频/字幕轨 |
| 章节 | 内置章节标记 |
| 元数据 | 标签、封面、章节 |
| 错误恢复 | 容错强 |
| 字幕 | SRT/ASS/SSA/VTT |
| 几乎所有编码 | 通用性强 |

```bash
# FFmpeg 选轨道
ffmpeg -i input.mkv -map 0:v:0 -map 0:a:1 -c copy output.mp4

# 选第一个视频轨 + 第一个音频轨
ffmpeg -i input.mkv -map 0:v:0 -map 0:a:0 -c copy out.mkv
```

## 📊 TS（Transport Stream）

**MPEG-TS** = 广播级容器，专门为传输设计。

| 特性 | 说明 |
| --- | --- |
| 包大小 | 固定 188 字节 |
| 错误恢复 | FEC 前向纠错 |
| 多节目 | 一路传输多频道 |
| HLS 切片 | 直播切片常用 |
| 延迟 | 较低 |

```bash
# HLS 切片（生成 .ts 文件 + .m3u8）
ffmpeg -i input.mp4 -c:v libx264 -c:a aac -hls_time 4 -hls_list_size 0 output.m3u8
```

## 🎬 选容器原则

| 场景 | 推荐 | 理由 |
| --- | --- | --- |
| **通用点播** | MP4 | 兼容性最好 |
| **高质量本地** | MKV | 灵活、支持多音轨 |
| **Web HTML5** | MP4 / WebM | 浏览器原生支持 |
| **直播** | TS / FLV | 切片传输 |
| **Apple 生态** | MOV | QuickTime 原生 |
| **微信/抖音上传** | MP4 | 平台要求 |
| **老设备** | MP4 | 兼容性最强 |

## 🛠️ FFmpeg 容器转换

```bash
# MP4 → MKV
ffmpeg -i input.mp4 -c copy output.mkv

# MKV → MP4（重编码）
ffmpeg -i input.mkv -c:v libx264 -c:a aac output.mp4

# 提取视频轨（无重编码）
ffmpeg -i input.mkv -map 0:v -c copy video.h264

# 提取音频轨
ffmpeg -i input.mp4 -map 0:a -c copy audio.aac

# 合并多轨
ffmpeg -i video.mp4 -i audio.aac -c copy output.mp4

# WebM 编码
ffmpeg -i input.mp4 -c:v libvpx-vp9 -c:a libopus output.webm
```

## 📌 面试考点

1. MP4 和 MKV 的区别？
   - MP4 标准严格、兼容性最强；MKV 开源、功能强、支持多轨
2. moov 是什么？为什么需要 faststart？
   - moov 存放元数据；faststart 把 moov 移到文件开头，支持边下边播
3. 为什么直播用 TS 不用 MP4？
   - TS 固定 188 字节包，适合流式传输；MP4 是完整文件格式
4. WebM 和 MP4 的区别？
   - WebM 用 VP8/VP9/AV1 + Opus，开源免专利；MP4 用 H.264/H.265 + AAC

## 🔗 下一步

- [编解码概览](/01-basics/codec-overview)
- [H.264](/03-codecs/h264)
- [FFmpeg 实战](/06-tools/ffmpeg)