---
title: 硬件加速 NVENC / QSV
date: 2026-08-15  # date-auto-injected
---

# 硬件加速 NVENC / QSV

<span class="kg-badge kg-badge-perf">性能</span>
<span class="kg-badge kg-badge-tools">硬件</span>
<span class="kg-badge kg-badge-app">实时</span>

利用**GPU / 专用硬件**进行视频编解码，相比 CPU 软编可提速 **10-50 倍**。

## 📊 主流硬件加速方案

| 方案 | 厂商 | 平台 | 支持编码 |
| --- | --- | --- | --- |
| **NVENC** | NVIDIA | RTX / Quadro / Tesla | H.264, H.265, AV1 |
| **NVDEC** | NVIDIA | 同上 | H.264, H.265, AV1, VP9 |
| **Quick Sync (QSV)** | Intel | iGPU / Arc | H.264, H.265, AV1 |
| **VAAPI** | Intel/AMD | Linux | H.264, H.265, VP9 |
| **VideoToolbox** | Apple | M1/M2/M3 + iGPU | H.264, H.265 |
| **AMF** | AMD | Radeon | H.264, H.265, AV1 |
| **VPU** | Intel/各家 | 专用芯片 | H.264, H.265 |
| **专用 ASIC** | 谷歌/各家 | TPU 类 | 视频专用 |

## 🏗️ NVIDIA NVENC

**NVIDIA Encoder**，RTX 系列自带专用编码器。

### NVENC 性能

| GPU | NVENC 引擎 | 支持 | 推荐场景 |
| --- | --- | --- | --- |
| **RTX 4090** | 2x NVENC | H.264/HEVC/AV1 | 直播、8K |
| **RTX 4080** | 1x NVENC | 同上 | 直播、4K |
| **RTX 4070** | 1x NVENC | 同上 | 直播 |
| **RTX 3090** | 1x NVENC | H.264/HEVC | 直播 |
| **RTX 3080** | 1x NVENC | 同上 | 直播 |

### NVENC 特点

| 优点 | 局限 |
| --- | --- |
| 实时 4K/8K | 质量略低于软编（x265 veryslow） |
| 几乎不耗 CPU | 预设有限 |
| AV1 支持（40 系） | 部分高级特性缺 |

## 🛠️ FFmpeg + NVENC

```bash
# H.264 NVENC
ffmpeg -i in.mp4 -c:v h264_nvenc -preset p4 out.mp4

# H.265 NVENC
ffmpeg -i in.mp4 -c:v hevc_nvenc -preset p4 out.mp4

# AV1 NVENC (RTX 40 系)
ffmpeg -i in.mp4 -c:v av1_nvenc -preset p4 out.mp4

# NVENC 预设
-preset p1  # 最快（最高码率）
-preset p2  # 较快
-preset p3  # 默认
-preset p4  # 推荐（直播）
-preset p5
-preset p6
-preset p7  # 最慢（最佳质量）

# NVENC 参数
-b:v 5M          # 目标码率
-cq 23           # 恒定质量（Q）
-rc vbr          # VBR 模式
-rc cbr          # CBR 模式
-rc cbr_hq       # CBR HQ
-bufsize 5M      # 缓冲
-2pass 1         # 两遍编码
-profile:v high  # Profile
```

### NVENC 性能 vs 质量

```
NVENC vs x264 medium:
  速度: 20x 快
  质量: 相当（PSNR 接近）

NVENC vs x265 medium:
  速度: 5-10x 快
  质量: 略低（NVENC HEVC 略差）

NVENC AV1 vs SVT-AV1:
  速度: 相当
  质量: 接近
```

## 📐 Intel Quick Sync Video (QSV)

**Intel 核显 / Arc 独显** 加速。

### QSV 性能

| 硬件 | 支持编码 |
| --- | --- |
| **Intel Arc A770** | H.264/HEVC/AV1 |
| **Intel Arc A380** | H.264/HEVC/AV1 |
| **Intel Iris Xe** | H.264/HEVC/AV1 |
| **Intel UHD 770** | H.264/HEVC |
| **老 iGPU** | 仅 H.264 |

### FFmpeg QSV

```bash
# H.264 QSV
ffmpeg -i in.mp4 -c:v h264_qsv -preset faster out.mp4

# H.265 QSV
ffmpeg -i in.mp4 -c:v hevc_qsv -preset faster out.mp4

# AV1 QSV (Arc)
ffmpeg -i in.mp4 -c:v av1_qsv -preset faster out.mp4

# QSV 预设
-preset veryfast
-preset faster
-preset fast
-preset medium
-preset slow
-preset veryslow

# QSV 模式
-look_ahead 1        # 视觉优化
-adaptive_i 1        # 自适应 I 帧
-adaptive_b 1        # 自适应 B 帧
```

## 📐 AMD AMF

```bash
# H.264 AMF
ffmpeg -i in.mp4 -c:v h264_amf -quality balanced out.mp4

# H.265 AMF
ffmpeg -i in.mp4 -c:v hevc_amf -quality balanced out.mp4

# AMF 预设
-quality speed           # 最快
-quality balanced        # 平衡
-quality quality         # 高质量
```

## 📐 Apple VideoToolbox

```bash
# H.264 VideoToolbox
ffmpeg -i in.mp4 -c:v h264_videotoolbox -b:v 5M out.mp4

# H.265 VideoToolbox
ffmpeg -i in.mp4 -c:v hevc_videotoolbox -b:v 3M out.mp4

# VideoToolbox 预设
-vt_preset fast
-vt_preset balanced
```

## 📐 Linux VAAPI

```bash
# H.264 VAAPI
ffmpeg -vaapi_device /dev/dri/renderD128 \
  -i in.mp4 -c:v h264_vaapi -b:v 5M out.mp4

# H.265 VAAPI
ffmpeg -vaapi_device /dev/dri/renderD128 \
  -i in.mp4 -c:v hevc_vaapi -b:v 3M out.mp4

# 转码到 VAAPI
ffmpeg -hwaccel vaapi -vaapi_device /dev/dri/renderD128 \
  -i in.mp4 -c:v h264_vaapi out.mp4
```

## 📊 硬件加速对比

| 方案 | 速度 | 质量 | 兼容性 | 实时 |
| --- | --- | --- | --- | --- |
| **NVENC** | **最快** | 高 | 高 | **是** |
| **QSV** | 快 | 中高 | 高 | 是 |
| **AMF** | 快 | 中 | 中 | 是 |
| **VideoToolbox** | 快 | 高 | macOS | 是 |
| **VAAPI** | 快 | 中 | Linux | 是 |
| **x264 veryslow** | 慢 | **最高** | 最高 | 否 |
| **x265 veryslow** | 极慢 | **最高** | 最高 | 否 |

## 🎯 选择建议

| 场景 | 推荐 |
| --- | --- |
| **直播** | NVENC / QSV |
| **录播** | x264 medium / x265 medium |
| **高质量归档** | x265 veryslow |
| **8K 实时** | NVENC (RTX 40) |
| **AV1 编码** | NVENC AV1 (40 系) / SVT-AV1 |
| **Apple 生态** | VideoToolbox |

## 📊 多 GPU 并行

```bash
# 多 GPU 编码（NVENC）
# FFmpeg 需要分别调用

# GPU 0
ffmpeg -i in.mp4 -c:v h264_nvenc -gpu 0 out1.mp4 &

# GPU 1
ffmpeg -i in2.mp4 -c:v h264_nvenc -gpu 1 out2.mp4 &
```

## 📌 面试考点

1. NVENC vs x264 速度？
   - NVENC 20x 快；质量接近
2. AV1 硬件支持？
   - RTX 40 / Intel Arc / AMD RX 7000
3. 直播为什么用硬件编码？
   - CPU 留给业务逻辑
4. 硬件编码画质差？
   - 预设一致时，PSNR 差 0.5-1 dB

## 🔗 下一步

- [GPU CUDA](/08-perf/gpu-cuda)
- [多线程并行](/08-perf/threading)
- [实时流性能](/08-perf/realtime)