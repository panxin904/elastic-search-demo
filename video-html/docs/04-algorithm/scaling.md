---
title: 缩放插值
---

# 缩放与插值算法

<span class="kg-badge kg-badge-algorithm">算法</span>
<span class="kg-badge kg-badge-tools">FFmpeg</span>

将视频从一个**分辨率**转换为另一个分辨率，需要**插值算法**填补未知像素。

## 🧠 缩放类型

| 类型 | 含义 | 用途 |
| --- | --- | --- |
| **上采样** | 小 → 大（放大） | 老片修复、低清转高清 |
| **下采样** | 大 → 小（缩小） | 4K 转 1080p |
| **重采样** | 任意 → 任意 | AI 超分 |

## 📊 插值算法对比

| 算法 | 速度 | 画质 | 计算 |
| --- | --- | --- | --- |
| **最近邻** | 最快 | 锯齿明显 | 1 tap |
| **双线性** | 快 | 较糊 | 4 tap |
| **双三次** | 中 | 较好 | 16 tap |
| **Lanczos2** | 中 | 好 | 36 tap |
| **Lanczos3** | 慢 | 很好 | 64 tap |
| **Mitchell** | 中 | 好 | 16 tap |
| **Catmull-Rom** | 中 | 好 | 16 tap |
| **Spline** | 慢 | 好 | 多 tap |
| **AI 超分** | GPU | **最佳** | 神经网络 |

## 📐 算法详解

### 最近邻（Nearest）

```
新像素 = 距离最近的源像素

  ┌───┬───┐         ┌───┬───┬───┬───┐
  │ A │ B │   →     │ A │ A │ B │ B │
  ├───┼───┤         ├───┼───┼───┼───┤
  │ C │ D │         │ A │ A │ B │ B │
  └───┴───┘         ├───┼───┼───┼───┤
                    │ C │ C │ D │ D │
                    ├───┼───┼───┼───┤
                    │ C │ C │ D │ D │
                    └───┴───┴───┴───┘
```

### 双线性（Bilinear）

```
2D 线性插值：

P(x, y) = (1-dx)(1-dy)·P11 + dx(1-dy)·P21
        + (1-dx)dy·P12 + dx·dy·P22

  P11 ──── P21
   │    *    │  * = 插值点
  P12 ──── P22
```

### 双三次（Bicubic）

```
16 tap 卷积核：

K(t) = (a+2)|t|³ - (a+3)|t|² + 1           |t| ≤ 1
     = a|t|³ - 5a|t|² + 8a|t| - 4a          1 < |t| ≤ 2
     = 0                                    |t| > 2

a = -0.5（Catmull-Rom）或 -0.75（更好锐度）

采样 16 像素 (4×4)
```

### Lanczos

```
Lanczos2: 6×6 = 36 tap
Lanczos3: 8×8 = 64 tap

K(t) = sinc(t)·sinc(t/a)   |t| < a
     = 0                   |t| ≥ a

a = 2 (Lanczos2)
a = 3 (Lanczos3)

抗锯齿强，最常用的高质量算法
```

### Mitchell

```
M(t) = ((12-9B-6C)|t|³ + (-18+12B+6C)|t|² + (6-2B)) / 6   |t| < 1
     = ((-B-6C)|t|³ + (6B+30C)|t|² + (-12B-48C)|t| + (8B+24C)) / 6   1 ≤ |t| < 2
     = 0                                                       |t| ≥ 2

B = 1/3, C = 1/3

Mitchell-Netravali 滤波器，平衡锐利和平滑
```

## 📐 抗锯齿（Anti-Aliasing）

```
缩小图像时，如果直接采样会出现摩尔纹（Moiré）

抗锯齿方法：
  1. 低通滤波后再采样
  2. 多点采样平均
  3. Lanczos/Mitchell 自带低通
```

### 摩尔纹示例

```
原始: 棋盘格
下采样 1/2 直接取 → 摩尔纹
下采样 1/2 Lanczos → 平滑
```

## 📊 算法选择指南

| 场景 | 推荐 |
| --- | --- |
| **实时预览** | 双线性 / 最近邻 |
| **高质量转码** | Lanczos3 |
| **上采样（放大）** | Lanczos3 / Catmull-Rom |
| **下采样（缩小）** | Mitchell / Lanczos2 |
| **电影修复** | Bicubic |
| **AI 增强** | Real-ESRGAN |

## 🤖 AI 超分（Neural Network）

| 模型 | 用途 |
| --- | --- |
| **ESPCN** | 实时超分 |
| **SRCNN** | 第一代深度超分 |
| **SRGAN** | 感知损失超分 |
| **ESRGAN** | 增强版 GAN |
| **Real-ESRGAN** | 真实场景超分 |
| **EDVR** | 视频超分 |
| **Video2X** | 视频无损放大 |
| **BasicVSR++** | 视频超分 SOTA |
| **StableSR** | 扩散模型超分 |

## 🛠️ FFmpeg 滤镜

```bash
# 默认（双线性）
ffmpeg -i in.mp4 -vf "scale=1920:1080" out.mp4

# Lanczos
ffmpeg -i in.mp4 -vf "scale=1920:1080:flags=lanczos" out.mp4

# Bicubic
ffmpeg -i in.mp4 -vf "scale=1920:1080:flags=bicubic" out.mp4

# Spline
ffmpeg -i in.mp4 -vf "scale=1920:1080:flags=spline" out.mp4

# 同时缩放 + 抗锯齿
ffmpeg -i in.mp4 -vf "scale=1920:1080:flags=lanczos:param0=3" out.mp4
```

## 🛠️ OpenCV 缩放

```python
import cv2
import numpy as np

img = cv2.imread('in.png')
h, w = img.shape[:2]

# 双线性
out1 = cv2.resize(img, (w*2, h*2), interpolation=cv2.INTER_LINEAR)

# 双三次
out2 = cv2.resize(img, (w*2, h*2), interpolation=cv2.INTER_CUBIC)

# Lanczos4
out3 = cv2.resize(img, (w*2, h*2), interpolation=cv2.INTER_LANCZOS4)

# AI 超分 (OpenCV DNN)
sr = cv2.dnn_superres.DnnSuperResImpl_create()
sr.readModel('ESPCN_x2.pb')
sr.setModel('espcn', 2)
out4 = sr.upsample(img)
```

## 📌 面试考点

1. 双线性 vs 双三次？
   - 双线性 4 tap、快；双三次 16 tap、画质好
2. Lanczos 为什么抗锯齿好？
   - 内置低通滤波器
3. AI 超分优势？
   - 学习真实数据分布，效果远超传统算法
4. 缩放时为什么会有摩尔纹？
   - 高频分量折叠到低频

## 🔗 下一步

- [去噪算法](/04-algorithm/denoise)
- [超分辨率](/04-algorithm/super-res)
- [AI 超分](/07-ai/super-res-ai)