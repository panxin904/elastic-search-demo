---
title: AV1
---

# AV1（AOMedia Video 1）

<span class="kg-badge kg-badge-codecs">编码</span>
<span class="kg-badge kg-badge-protocol">开源</span>
<span class="kg-badge kg-badge-ai">免专利</span>

**AV1** = Alliance for Open Media Video 1，**开源免专利**的新一代视频编码。

## 📊 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 2018-03 标准化 |
| 开发者 | AOMedia（Google / Mozilla / Apple / Amazon / Microsoft / Netflix / Meta / Intel） |
| 现状 | Web 标准、流媒体主流 |
| 压缩率 | 较 HEVC 节省 20-30% |
| 复杂度 | 编码极高（~HEVC 10x） |
| 专利 | **完全免费** |
| 容器 | MP4 / WebM / MKV |

## 🏗️ 关键特性

| 特性 | AV1 vs HEVC |
| --- | --- |
| **块大小** | 最大 128×128 |
| **块形状** | 方形 + 楔形 + 楔形预测 |
| **预测模式** | 56+ 帧内模式 |
| **变换** | DCT / ADST / IDTX / WHT |
| **滤波器** | CDEF + LR |
| **熵编码** | ANS（非对称数字系统） |
| **环路滤波** | DF + CDEF + LR（3 阶段） |
| **并行** | Tiles + Rows |

## 📐 编码流程

```
输入帧 → 分块 (SB 64/128) → 预测 → 变换 → 量化 → ANS 编码
                                                    ↓
                                              CDEF + LR 环路滤波
```

## 🎯 帧内预测

| 类别 | 模式数 | 说明 |
| --- | --- | --- |
| **方向模式** | 56 | 角度 45°/67°/90° 等 |
| **非方向** | 3 | DC / Paeth / Smooth |
| **递归** | 多 | 基于邻块像素递归 |
| **滤波器** | 多 | 帧内滤波器 |
| **调色板** | 1 | 屏幕内容专用 |

## 🎯 帧间预测

| 特性 | 说明 |
| --- | --- |
| **参考帧数** | 最多 7 |
| **MV 精度** | 1/8 像素 |
| **仿射运动** | 支持（仿射变换） |
| **OBMC** | 重叠块 |
| **Wedge/Seg** | 楔形分割 B 帧 |
| **Warped Motion** | 全局运动补偿 |

## 🔬 变换与量化

| 变换 | 尺寸 | 类型 |
| --- | --- | --- |
| **DCT-II** | 4-64 | 主流 |
| **DST-VII** | 4 | Intra 专用 |
| **ADST** | 4-16 | 替代 |
| **IDTX** | 4-64 | 隐式变换 |
| **WHT** | 4 | 调色板/无损 |

## 🔄 CDEF（约束方向增强滤波）

AV1 独有的环路滤波，**比 SAO 更强**。

```
约束方向增强：
  - 8 个方向
  - 自适应强度
  - 抑制块效应和振铃
```

## 🔄 LR（Loop Restoration）

```
3 种滤波器可选:
  - Wiener 滤波（自回归）
  - 双自回归（Dual Self-guided）
  - 分段平滑（Switchable）

效果：弥补量化损失，提升锐度
```

## 📊 编码工具总览

```
AV1 编码工具集:
  ┌── 块划分
  ├── 帧内预测 (56+ 模式)
  ├── 帧间预测 (MV/仿射/OBMC)
  ├── 变换 (DCT/ADST/IDTX)
  ├── 量化
  ├── 熵编码 (ANS)
  ├── CDEF 环路滤波
  └── LR 恢复滤波
```

## 📊 Profile

| Profile | 颜色 |
| --- | --- |
| **Main** | 8/10 bit 4:2:0 |
| **High** | 8/10 bit 4:4:4 |
| **Professional** | 8/10/12 bit 4:2:0/4:2:2/4:4:4 |

## ⚙️ FFmpeg 编码

```bash
# AV1 编码（libaom-AV1，慢）
ffmpeg -i input.mp4 -c:v libaom-av1 -crf 30 -b:v 0 -preset 8 output.mkv

# AV1 编码（libsvtav1，快）
ffmpeg -i input.mp4 -c:v libsvtav1 -crf 32 -preset 8 output.mp4

# 实时 AV1 硬件（AV1 支持 GPU）
ffmpeg -i input.mp4 -c:v av1_nvenc -preset p4 output.mp4
ffmpeg -i input.mp4 -c:v av1_qsv output.mp4

# WebM 容器
ffmpeg -i input.mp4 -c:v libvpx-vp9 -c:a libopus output.webm

# AV1 + MP4
ffmpeg -i input.mp4 -c:v libsvtav1 -tag:v av01 output.mp4
```

## ⚙️ 编码速度

| 编码器 | preset | fps | 压缩率 |
| --- | --- | --- | --- |
| **libaom-av1** | 0-8 | 极慢 | 最高 |
| **libsvtav1** | 0-13 | 快 | 高 |
| **libdav1d** | - | 仅解码 | - |

```bash
# libaom-av1 preset 对照
preset 0  # 最慢、压缩率最高
preset 6  # 默认
preset 8  # 推荐实时
preset 10 # 更快
preset 13 # 最快
```

## 📊 编码器实现

| 编码器 | 速度 | 压缩率 | 状态 |
| --- | --- | --- | --- |
| **libaom** | 慢 | 高 | 参考实现 |
| **libsvtav1** | 快 | 中高 | Intel / Netflix |
| **libdav1d** | 快 | - | 解码器 |
| **rav1e** | 中 | 中 | Mozilla Rust |
| **AV1 NVE** | 最快 | 中 | NVIDIA 硬件 |

## 📌 应用场景

| 平台 | 应用 |
| --- | --- |
| **YouTube** | 2018 起 AV1 |
| **Netflix** | 4K 流媒体 |
| **Meta (Facebook)** | 短视频 |
| **Apple Safari** | 浏览器支持 |
| **Chrome / Edge** | 浏览器支持 |
| **Twitch** | 直播（实验） |
| **Android 10+** | 硬件支持 |

## 🔗 下一步

- [VP9](/03-codecs/vp9)
- [H.265](/03-codecs/h265)
- [FFmpeg 实战](/06-tools/ffmpeg)