---
title: 编解码概览
date: 2026-08-15  # date-auto-injected
---

# 编解码概览

<span class="kg-badge kg-badge-basics">基础</span>
<span class="kg-badge kg-badge-codec">原理</span>

视频编解码（CODEC = COder + DECoder）= 视频的"压缩与解压"。

## 🗜️ 为什么需要编码？

```
未压缩 1080p 30fps 视频:
  3 MB/帧 × 30 fps × 60s = 5.4 GB/分钟 ≈ 324 GB/小时

压缩后 1080p 30fps (5Mbps):
  5 Mbps × 3600s / 8 = 2.25 GB/小时

压缩比 ≈ 99% 以上
```

## 🧬 视频压缩的两大核心

### 1️⃣ 空间冗余 → 帧内压缩

**同一帧内**相邻像素相似 → **帧内预测** + DCT

### 2️⃣ 时间冗余 → 帧间压缩

**相邻帧**之间高度相似 → **运动估计 + 运动补偿**

```
原始帧序列:        I   P   P   P   P   P
                  ↓   ↓
参考帧:           I ─→ P ─→ P ─→ P ─→ P
                     ↑    ↑    ↑
                  运动估计 + 残差
```

## 🏗️ 编码流程（编码器）

```
输入视频帧 YUV
  ↓
[预处理] 色彩转换 / 分片
  ↓
[预测] 帧内/帧间预测 + 运动估计 → 得到预测值
  ↓
[残差] 原值 - 预测值 = 残差
  ↓
[变换] DCT/DST 变换
  ↓
[量化] 量化（丢弃不重要的高频）
  ↓
[熵编码] CABAC / CAVLC → 比特流
  ↓
[环路滤波]（可选）去块效应
  ↓
输出压缩比特流
```

## 🏗️ 解码流程（解码器）

```
输入比特流
  ↓
[熵解码] CABAC / CAVLC → 反量化
  ↓
[反量化] 量化表
  ↓
[反变换] IDCT
  ↓
[预测补偿] 帧内/帧间 + 运动补偿
  ↓
[环路滤波] 去块效应
  ↓
[后处理] 色彩转换
  ↓
输出 YUV 帧 → 显示
```

## 📐 关键概念速记

| 概念 | 含义 |
| --- | --- |
| **GOP** | Group of Pictures，两个 I 帧之间的帧序列 |
| **IDR** | 即时解码刷新帧，H.264 关键 I 帧 |
| **I 帧** | 关键帧，独立编码 |
| **P 帧** | 前向参考帧 |
| **B 帧** | 双向参考帧，压缩率最高 |
| **CTU/CU** | 编码树单元（H.265 64×64） |
| **MB** | 宏块（H.264 16×16） |
| **MV** | 运动矢量（Motion Vector） |
| **ME** | 运动估计（Motion Estimation） |
| **MC** | 运动补偿（Motion Compensation） |
| **DCT** | 离散余弦变换 |
| **CABAC** | 自适应二进制算术编码 |
| **CAVLC** | 上下文自适应可变长编码 |
| **QP** | 量化参数（0-51，越大越失真） |

## 📊 主要编码标准对比

| 编码 | 标准 | 推出 | 同画质码率 | 复杂度 | 专利 |
| --- | --- | --- | --- | --- | --- |
| **H.264** | AVC | 2003 | 基准 | 中 | 需付费 |
| **H.265** | HEVC | 2013 | -50% | 高 | 需付费 |
| **AV1** | AOM | 2018 | -30% vs HEVC | 很高 | **免费** |
| **VP9** | Google | 2012 | -50% vs H.264 | 中高 | **免费** |
| **AVS3** | 中国 | 2019 | 接近 HEVC | 高 | 中国免 |
| **VVC** | H.266 | 2020 | -50% vs HEVC | 极高 | 需付费 |
| **EVC** | MPEG-5 | 2020 | 类似 HEVC | 中 | 部分免 |

## 🛠️ FFmpeg 编码命令

```bash
# H.264 编码
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac output.mp4

# H.265 编码
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -preset medium -tag:v hvc1 output.mp4

# AV1 编码
ffmpeg -i input.mp4 -c:v libaom-av1 -crf 30 -b:v 0 -preset 8 output.mkv

# VP9 编码
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 31 -b:v 0 output.webm

# 硬件加速 H.264 (NVENC)
ffmpeg -i input.mp4 -c:v h264_nvenc -preset p4 output.mp4

# 查看编码信息
ffprobe -show_streams -select_streams v:0 input.mp4
```

## 🔬 编码器评价指标

| 指标 | 说明 |
| --- | --- |
| **压缩率** | 同画质码率，越低越好 |
| **画质** | PSNR / SSIM / VMAF 分数 |
| **编码速度** | fps（实时性） |
| **解码速度** | 客户端解码帧率 |
| **复杂度** | 算法复杂度 |
| **硬件支持** | 是否有硬件加速 |

## 📌 主流编码选择

| 场景 | 推荐编码 | 理由 |
| --- | --- | --- |
| **兼容性优先** | H.264 | 所有设备支持 |
| **高压缩** | H.265 / AV1 | 节省带宽 |
| **免专利** | AV1 / VP9 | 开源免费 |
| **实时直播** | H.264 + NVENC | 低延迟 + 硬件 |
| **YouTube** | VP9 / AV1 | 平台偏好 |
| **Netflix** | AV1 / HEVC | 4K HDR |
| **微信视频** | H.264 | 兼容性 |
| **本地存储** | HEVC / AV1 | 节省空间 |

## 🔗 下一步

- [帧内预测](/02-codec/intra-prediction)
- [帧间预测](/02-codec/inter-prediction)
- [H.264](/03-codecs/h264)