---
title: 速记卡
date: 2026-08-15  # date-auto-injected
---

# 速记卡

<span class="kg-badge kg-badge-interview">速记</span>
<span class="kg-badge kg-badge-cases">面试</span>

一页速记，覆盖**最常用**的编解码参数、FFmpeg 命令、面试题，便于快速回顾。

## 1. 像素格式速记

| 格式 | 含义 | 用途 |
| --- | --- | --- |
| YUV420 | 4:2:0 降采样 | H.264/H.265 默认 |
| YUV422 | 4:2:2 降采样 | 专业广播 |
| YUV444 | 4:4:4 全采样 | 高质量 |
| RGB24 | 8bit RGB | 显示器 |
| RGB48 | 16bit RGB | 高质量 |

## 2. 分辨率代号速记

| 名称 | 分辨率 |
| --- | --- |
| 480p | 640×480 |
| 720p | 1280×720 |
| 1080p | 1920×1080 |
| 2K | 2560×1440 |
| 4K UHD | 3840×2160 |
| 8K UHD | 7680×4320 |

## 3. 帧类型速记

| 帧 | 全称 | 含义 |
| --- | --- | --- |
| I | Intra | 关键帧，独立编码 |
| P | Predictive | 前向参考 |
| B | Bi-predictive | 双向参考 |
| IDR | Instantaneous Decoder Refresh | 即时刷新 I 帧 |

## 4. 编码标准速记

| 编码 | 推出 | 压缩率 | 专利 |
| --- | --- | --- | --- |
| H.264/AVC | 2003 | 基准 | 付费 |
| H.265/HEVC | 2013 | -50% | 付费 |
| VP9 | 2012 | -50% | 免费 |
| AV1 | 2018 | -30% vs HEVC | 免费 |
| VVC/H.266 | 2020 | -50% vs HEVC | 付费 |

## 5. 码率速记

| 场景 | H.264 | H.265 |
| --- | --- | --- |
| 480p 直播 | 800K | 400K |
| 720p 直播 | 2M | 1M |
| 1080p 蓝光 | 8M | 4M |
| 4K 蓝光 | 35M | 18M |

## 6. FFmpeg 必记命令

```bash
# 格式转换
ffmpeg -i in.mp4 out.avi

# 提取音频
ffmpeg -i in.mp4 -vn -c:a copy out.aac

# 提取视频
ffmpeg -i in.mp4 -an -c:v copy out.h264

# 压缩视频
ffmpeg -i in.mp4 -c:v libx264 -crf 23 -preset medium out.mp4

# 截图
ffmpeg -i in.mp4 -ss 00:00:10 -vframes 1 out.jpg

# 裁剪
ffmpeg -i in.mp4 -vf "crop=640:480:100:50" out.mp4

# 缩放
ffmpeg -i in.mp4 -vf "scale=1280:720" out.mp4

# 拼接
ffmpeg -f concat -i list.txt -c copy out.mp4

# 直播推流
ffmpeg -re -i in.mp4 -c:v libx264 -c:a aac -f flv rtmp://server/live/stream

# HLS 切片
ffmpeg -i in.mp4 -c:v libx264 -c:a aac -hls_time 4 -hls_list_size 0 out.m3u8

# 硬件加速
ffmpeg -i in.mp4 -c:v h264_nvenc out.mp4

# 查看信息
ffprobe -show_streams in.mp4
```

## 7. 流媒体协议速记

| 协议 | 端口 | 延迟 | 适用 |
| --- | --- | --- | --- |
| RTMP | 1935 | 1-3s | 推流 |
| HLS | 80/443 | 5-30s | 点播/直播 |
| DASH | 80/443 | 5-30s | 点播/直播 |
| WebRTC | 动态 | <500ms | 实时互动 |
| RTSP | 554 | <1s | 监控 |
| SRT | 动态 | <1s | 广电 |

## 8. 关键数字速记

| 数字 | 含义 |
| --- | --- |
| 1920×1080×1.5 | 1 帧 YUV420 ≈ 3MB |
| 30 fps × 3MB | 1 秒 ≈ 90MB（未压缩） |
| 99% | 视频压缩比 |
| 41.67ms | 24fps 1 帧时长 |
| 16ms | 60fps 1 帧时长 |
| 24fps | 电影帧率 |
| 16×16 | H.264 宏块 |
| 64×64 | H.265 CTU |
| 0-51 | QP 量化参数 |
| 188 byte | TS 包大小 |

## 9. 面试 8 问（速答）

| 问题 | 速答 |
| --- | --- |
| 为什么用 YUV 不用 RGB | 人眼对色度不敏感，可降采样 |
| H.264 I 帧压缩原理 | 帧内预测 + DCT + CABAC |
| 三种帧的区别 | I 独立 / P 前向 / B 双向 |
| RTMP vs HLS | RTMP 1-3s 直播推流，HLS 5-30s 切片 |
| 缩放算法优劣 | Lanczos > 双三次 > 双线性 > 最近邻 |
| AI 超分原理 | GAN/扩散 + 大数据训练 |
| NVENC 是什么 | NVIDIA 硬件编码器 |
| WebRTC 优势 | 超低延迟，P2P |

## 10. 必记缩写

| 缩写 | 全称 |
| --- | --- |
| GOP | Group of Pictures |
| IDR | Instantaneous Decoder Refresh |
| CTU | Coding Tree Unit |
| CU | Coding Unit |
| PU | Prediction Unit |
| TU | Transform Unit |
| MV | Motion Vector |
| ME | Motion Estimation |
| MC | Motion Compensation |
| DCT | Discrete Cosine Transform |
| CABAC | Context-Adaptive Binary Arithmetic Coding |
| CAVLC | Context-Adaptive Variable-Length Coding |
| QP | Quantization Parameter |
| PSNR | Peak Signal-to-Noise Ratio |
| SSIM | Structural Similarity |
| VMAF | Video Multimethod Assessment Fusion |

## 11. 性能优化速记

```bash
# 硬件加速编码
-c:v h264_nvenc       # NVIDIA
-c:v h264_qsv         # Intel Quick Sync
-c:v h264_videotoolbox # Apple
-c:v h264_amf         # AMD

# FFmpeg 预设
-preset ultrafast     # 最快
-preset fast
-preset medium        # 默认
-preset slow          # 慢而质量高
-preset veryslow

# CRF 质量（libx264）
-crf 18  # 视觉无损
-crf 23  # 默认
-crf 28  # 高压缩
-crf 51  # 最低质量
```

## 12. 关键 FFmpeg 滤镜速记

| 滤镜 | 用途 |
| --- | --- |
| `scale=W:H` | 缩放 |
| `crop=W:H:X:Y` | 裁剪 |
| `transpose=1` | 旋转 90° |
| `fps=30` | 改帧率 |
| `eq=brightness=0.1` | 亮度 |
| `hue=h=90` | 色调 |
| `unsharp` | 锐化 |
| `hqdn3d` | 高质量去噪 |
| `yadif` | 去隔行 |
| `overlay` | 水印 |
| `drawtext` | 文字 |

## 13. 视频标准速记

| 标准 | 用途 |
| --- | --- |
| BT.601 | 标清 |
| BT.709 | 高清 |
| BT.2020 | 4K/8K |
| BT.2100 | HDR |
| Rec.709 | HDTV 色域 |
| Rec.2020 | UHD 色域 |

## 14. AI 视频模型速记

| 模型 | 公司 | 用途 |
| --- | --- | --- |
| Real-ESRGAN | Tencent | 视频超分 |
| Video2X | 开源 | 视频超分 |
| RIFE | 开源 | 视频插帧 |
| FILM | Google | 视频插帧 |
| SAM2 | Meta | 视频分割 |
| Sora | OpenAI | 视频生成 |
| Runway Gen-3 | Runway | 视频生成 |
| Pika | Pika Labs | 视频生成 |
| HeyGen | HeyGen | 数字人 |
| Wav2Lip | 开源 | 唇形同步 |

## 15. 关键 RFC / 标准

| RFC | 主题 |
| --- | --- |
| RFC 6184 | RTP/H.264 |
| RFC 7798 | RTP/H.265 |
| RFC 8216 | HLS |
| ITU-T H.264 | H.264/AVC |
| ITU-T H.265 | H.265/HEVC |
| AOM AV1 | AV1 |
| W3C WebRTC | WebRTC |