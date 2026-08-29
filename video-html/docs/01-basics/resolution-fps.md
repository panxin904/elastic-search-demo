---
title: 分辨率 / 帧率 / 码率
date: 2026-08-15  # date-auto-injected
---

# 分辨率 / 帧率 / 码率

<span class="kg-badge kg-badge-basics">基础</span>
<span class="kg-badge kg-badge-tools">FFmpeg</span>

视频三**核心参数**，决定画质、流畅度与文件大小。

## 📐 分辨率（Resolution）

视频画面**像素数**，宽度 × 高度。

| 名称 | 分辨率 | 像素总数 | 用途 |
| --- | --- | --- | --- |
| **480p** | 640×480 | 307,200 | 标清 |
| **720p (HD)** | 1280×720 | 921,600 | 高清 |
| **1080p (FHD)** | 1920×1080 | 2,073,600 | 全高清 |
| **2K (QHD)** | 2560×1440 | 3,686,400 | 2K |
| **4K (UHD)** | 3840×2160 | 8,294,400 | 超高清 |
| **8K (FUHD)** | 7680×4320 | 33,177,600 | 8K |

> p = 逐行扫描（Progressive）；i = 隔行扫描（Interlaced），如 1080i

### 像素与数据量

```
未压缩 1 帧 YUV420 (8bit):
  Y:   W × H × 1 byte
  Cb:  (W/2) × (H/2) × 1 byte
  Cr:  (W/2) × (H/2) × 1 byte
  Total ≈ W × H × 1.5 byte

1080p: 1920 × 1080 × 1.5 ≈ 3.1 MB / 帧
4K:    3840 × 2160 × 1.5 ≈ 12.4 MB / 帧
```

## 🎞️ 帧率（Frame Rate, fps）

每秒显示**帧数**，决定流畅度。

| 帧率 | 用途 |
| --- | --- |
| **8-12 fps** | 早期电影 |
| **24 fps** | 电影（电影标准） |
| **25 fps** | PAL 制（欧洲、中国） |
| **30 fps** | NTSC 制（美、日） |
| **50 fps** | PAL 高清直播 |
| **60 fps** | 游戏 / NTSC 高清直播 |
| **120+ fps** | 高速摄影 / 高刷游戏 |

### 帧率与人眼

```
< 10 fps:  卡顿
10-15 fps:  能接受
24 fps:     电影感（最佳艺术）
30-60 fps:  自然流畅
> 60 fps:   极流畅（电竞）
```

### 变帧率（VFR）与恒定帧率（CFR）

| 类型 | 含义 | 场景 |
| --- | --- | --- |
| **CFR** | 每帧时长固定 | 直播、广播电视 |
| **VFR** | 帧时长可变 | 电影、屏幕录像 |

```bash
# FFmpeg CFR
ffmpeg -i input.mp4 -r 30 -vsync cfr output.mp4

# FFmpeg VFR
ffmpeg -i input.mp4 -vsync vfr output.mp4
```

## 💾 码率（Bitrate, bps）

每秒传输的**比特数**，单位 `bps`（bits per second）。

| 名称 | 大小 | 场景 |
| --- | --- | --- |
| **128 Kbps** | 低 | 语音 |
| **500 Kbps** | 中低 | 480p 视频 |
| **1-2 Mbps** | 中 | 720p 视频 |
| **5-8 Mbps** | 高 | 1080p 视频 |
| **15-25 Mbps** | 很高 | 1080p 高清直播 |
| **50+ Mbps** | 极清 | 4K HDR |

### CBR vs VBR

| 模式 | 含义 | 优点 | 缺点 |
| --- | --- | --- | --- |
| **CBR** 恒定码率 | 每秒码率固定 | 带宽稳定 | 浪费 / 画质波动 |
| **VBR** 可变码率 | 复杂场景高码率 | 画质稳定 | 带宽波动 |
| **ABR** 平均码率 | 长期平均 | 平衡 | 短期仍波动 |

```bash
# FFmpeg CBR
ffmpeg -i input.mp4 -b:v 5M -minrate 5M -maxrate 5M -bufsize 5M output.mp4

# FFmpeg VBR
ffmpeg -i input.mp4 -b:v 5M -qmin 18 -qmax 28 output.mp4
```

## 📊 三者关系

```
文件大小 = 码率 × 时长 / 8
         = 码率 × 时长 / 8 (byte)

例：5Mbps 视频 1 小时
  = 5 × 10^6 × 3600 / 8 byte
  = 2.25 × 10^9 byte ≈ 2.1 GB
```

## 🎯 推荐参数

| 场景 | 分辨率 | 帧率 | 码率（H.264） | 码率（H.265） |
| --- | --- | --- | --- | --- |
| 标清直播 | 480p | 25 | 800K | 400K |
| 高清直播 | 720p | 25 | 2M | 1M |
| 蓝光 | 1080p | 24 | 8M | 4M |
| 4K 蓝光 | 2160p | 24 | 35M | 18M |
| 短视频 | 720p | 30 | 1.5M | 800K |

## 📌 关键公式

```
像素带宽 (Mbps) = W × H × fps × bits_per_pixel
例：1080p 30fps 8bit
  = 1920 × 1080 × 30 × 8 = 497 Mbps (未压缩)

压缩比 = 未压缩带宽 / 实际码率
  = 497 / 5 = 99 : 1
```

## 🔗 下一步

- [容器格式 MP4/AVI](/01-basics/container-format)
- [FFmpeg 实战](/06-tools/ffmpeg)