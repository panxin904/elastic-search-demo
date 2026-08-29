---
title: 音频编码 - AAC / MP3 / Opus
date: 2026-08-15  # date-auto-injected
---

# 音频编码 - AAC / MP3 / Opus

<span class="kg-badge kg-badge-codecs">音频</span>
<span class="kg-badge kg-badge-tools">FFmpeg</span>
<span class="kg-badge kg-badge-protocol">流媒体</span>

视频文件中的**音频流**编码标准，决定音质、延迟与兼容性。

## 🎵 主流音频编码

| 编码 | 推出 | 比特率 | 延迟 | 专利 | 用途 |
| --- | --- | --- | --- | --- | --- |
| **MP3** | 1993 | 128-320 Kbps | 高 | 已过期 | 音乐存储 |
| **AAC** | 1997 | 96-256 Kbps | 中 | 付费 | 流媒体 |
| **Opus** | 2012 | 32-128 Kbps | **低** | **免费** | WebRTC、实时 |
| **AC-3 / E-AC-3** | 1992 | 192-640 Kbps | 中 | 付费 | DVD / 蓝光 |
| **DTS** | 1993 | 754-1509 Kbps | 中 | 付费 | 蓝光 |
| **FLAC** | 2001 | 600-1100 Kbps | - | **免费** | 无损 |
| **Vorbis (OGG)** | 2000 | 80-320 Kbps | 中 | **免费** | 开源 |
| **AMR-WB** | 2001 | 6.6-23.85 Kbps | 中 | 付费 | 移动语音 |
| **WMA** | 1999 | 64-192 Kbps | 中 | 付费 | Windows |
| **ALAC** | 2004 | - | - | Apple | Apple 无损 |

## 🎯 MP3（MPEG-1 Layer III）

### 基本信息

| 项 | 值 |
| --- | --- |
| 标准 | ISO/IEC 11172-3 |
| 推出 | 1993 |
| 比特率 | 32-320 Kbps（CBR） / 8-320 Kbps（VBR） |
| 采样率 | 8K/11.025K/12K/16K/22.05K/24K/32K/44.1K/48K |
| 专利 | **2017 年起已过期** |

### 原理

```
输入 PCM
  ↓
[心理声学模型]
  ↓
[滤波器组] 32 子带
  ↓
[MDCT] 1024 频点
  ↓
[哈夫曼编码]
  ↓
MP3 比特流
```

## 🎯 AAC（Advanced Audio Coding）

### 基本信息

| 项 | 值 |
| --- | --- |
| 标准 | ISO/IEC 13818-7 / 14496-3 |
| 推出 | 1997 |
| 比特率 | 96-320 Kbps |
| 压缩率 | 较 MP3 高 30% |
| 专利 | 付费 |

### Profile

| Profile | 特点 |
| --- | --- |
| **AAC LC** | 低复杂度，最常用 |
| **AAC HE** | HE-AAC / AAC+SBR，高效 |
| **AAC LD** | 低延迟，直播 |
| **AAC ELD** | 超低延迟 |

### 原理

```
输入 PCM
  ↓
[滤波器组] MDCT 1024 / 128 窗
  ↓
[TNS] 时间噪声整形
  ↓
[预测] 帧间预测
  ↓
[立体声] MS / Intensity
  ↓
[哈夫曼] 无噪编码
  ↓
AAC 比特流
```

## 🎯 Opus（现代音频编码）

### 基本信息

| 项 | 值 |
| --- | --- |
| 标准 | IETF RFC 6716 |
| 推出 | 2012 |
| 比特率 | 6-510 Kbps |
| 延迟 | **最低 5ms**（CELT） |
| 专利 | **完全免费** |
| 用途 | WebRTC、Discord、Zoom |

### 组成

| 子编解码器 | 用途 |
| --- | --- |
| **SILK** | 语音（基于 LPC） |
| **CELT** | 音乐（基于 MDCT） |
| **混合模式** | SILK + CELT |

### 模式

| 模式 | 比特率 | 延迟 | 适用 |
| --- | --- | --- | --- |
| **VoIP** | 6-40 Kbps | 20ms | 语音 |
| **Audio** | 32-128 Kbps | 20ms | 音乐 |
| **Restricted Low Delay** | 32-128 Kbps | **5ms** | 实时互动 |

### FFmpeg

```bash
# Opus 编码
ffmpeg -i in.wav -c:a libopus -b:a 96k out.opus

# WebM 用 Opus
ffmpeg -i in.mp4 -c:v libvpx-vp9 -c:a libopus out.webm
```

## 🎯 AC-3 / Dolby Digital

### 基本信息

| 项 | 值 |
| --- | --- |
| 标准 | ATSC A/52 |
| 推出 | 1992 |
| 比特率 | 32-640 Kbps |
| 通道 | 1.0 / 2.0 / 5.1 / 7.1 |
| 用途 | DVD / 蓝光 / ATSC 电视 |

### E-AC-3（Enhanced）

| 特性 | 改进 |
| --- | --- |
| 比特率 | 高达 6.144 Mbps |
| 通道 | 更多声道 |
| 编码 | 改进 |

## 🎯 FLAC（无损）

| 项 | 值 |
| --- | --- |
| 标准 | Xiph.Org |
| 推出 | 2001 |
| 压缩率 | 50-60% |
| 质量 | **无损** |
| 专利 | 免费 |

### 原理

```
输入 PCM
  ↓
[预测] 线性预测
  ↓
[残差] 减去预测
  ↓
[Rice 编码]
  ↓
FLAC 比特流
```

## 📊 编码对比

| 编码 | 同等音质比特率 | 推荐码率 |
| --- | --- | --- |
| **MP3 128** | 128 Kbps | 256-320 Kbps（高质量） |
| **AAC LC 128** | ≈ MP3 192 Kbps | 128-192 Kbps（流媒体） |
| **Opus 96** | ≈ MP3 192 Kbps | 96-128 Kbps（音乐） |
| **Opus 32** | ≈ MP3 96 Kbps | 32-48 Kbps（语音） |
| **FLAC** | **无损** | 700-1100 Kbps |

## 🛠️ FFmpeg 实操

```bash
# AAC 编码（推荐）
ffmpeg -i input.mp4 -c:a aac -b:a 192k output.mp4

# Opus 编码
ffmpeg -i input.mp4 -c:a libopus -b:a 128k output.webm

# MP3 编码
ffmpeg -i input.wav -c:a libmp3lame -q:a 2 output.mp3

# 提取音频
ffmpeg -i input.mp4 -vn -c:a copy output.aac

# 多音轨合并
ffmpeg -i video.mp4 -i audio.opus -c:v copy -c:a copy output.mp4

# 音频转码
ffmpeg -i in.aac -c:a libopus out.opus
```

## 📌 面试考点

1. AAC vs MP3？
   - AAC 压缩率高 30%，更高效
2. Opus 优势？
   - 免费、低延迟、覆盖语音+音乐
3. 直播用什么编码？
   - AAC LC（流媒体）/ Opus（实时互动）
4. 无损 vs 有损？
   - FLAC 是无损（压缩但不丢信息）；MP3/AAC 是有损

## 🔗 下一步

- [H.264](/03-codecs/h264)
- [WebRTC](/05-protocol/webrtc)
- [FFmpeg 实战](/06-tools/ffmpeg)