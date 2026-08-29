---
title: 色彩转换
date: 2026-08-15  # date-auto-injected
---

# 色彩转换（Color Conversion）

<span class="kg-badge kg-badge-algorithm">算法</span>
<span class="kg-badge kg-badge-basics">色彩</span>

在不同**色彩空间**之间转换（YUV ↔ RGB、BT.601 ↔ BT.709、HDR ↔ SDR）。

## 🎨 常见色彩空间

| 空间 | 含义 | 用途 |
| --- | --- | --- |
| **YUV** | 亮度 + 色度 | 视频编码 |
| **RGB** | 红绿蓝 | 显示 |
| **HSV/HSL** | 色相饱和度 | 图像处理 |
| **XYZ** | CIE 1931 | 色彩科学 |
| **Lab** | 亮度对立色 | 印刷 |
| **CMYK** | 青品黄黑 | 印刷 |
| **BT.601/709/2020** | 数字 YUV | 电视标准 |

## 📐 RGB ↔ YUV

### BT.601 (SD)

```python
# RGB → YUV
Y =  0.257·R + 0.504·G + 0.098·B + 16
U = -0.148·R - 0.291·G + 0.439·B + 128
V =  0.439·R - 0.368·G - 0.071·B + 128

# YUV → RGB
R = 1.164·(Y-16) + 1.596·(V-128)
G = 1.164·(Y-16) - 0.392·(U-128) - 0.813·(V-128)
B = 1.164·(Y-16) + 2.017·(U-128)
```

### BT.709 (HD)

```python
# RGB → YUV
Y =  0.213·R + 0.715·G + 0.072·B + 16
U = -0.117·R - 0.394·G + 0.511·B + 128
V =  0.511·R - 0.464·G - 0.047·B + 128
```

### BT.2020 (UHD)

```python
Y =  0.2627·R + 0.6780·G + 0.0593·B + 16
U = -0.1396·R - 0.3600·G + 0.5000·B + 128
V =  0.5000·R - 0.4598·G - 0.0402·B + 128
```

## 📐 不同色彩空间的转换矩阵

```
[ BT.601 ]
[ BT.709 ] = M · [ BT.601 ]
[ BT.2020 ]

实际是色彩空间 + 伽马 + 色域的综合变换
```

## 🎨 色彩转换库

| 库 | 语言 | 用途 |
| --- | --- | --- |
| **libyuv** | C++ | Google 高效 YUV 转换 |
| **libavutil** | C | FFmpeg 内置 |
| **colour-science** | Python | 完整色彩科学 |
| **Pillow** | Python | 图像基础 |
| **OpenCV** | C++/Python | 通用 |

## 🛠️ FFmpeg 色彩转换

```bash
# 像素格式转换
ffmpeg -i in.mp4 -pix_fmt yuv420p out.mp4

# BT.601 → BT.709
ffmpeg -i in.mp4 -colorspace bt601 -color_trc smpte170m \
       -colorspace bt709 -color_trc bt709 out.mp4

# RGB → YUV
ffmpeg -i rgb.png -pix_fmt yuv420p out.yuv

# YUV → RGB
ffmpeg -pix_fmt yuv420p -s 1920x1080 -i in.yuv -pix_fmt rgb24 out.png

# 添加色彩元数据
ffmpeg -i in.mp4 -colorspace bt709 -color_primaries bt709 \
       -color_trc bt709 -color_range tv out.mp4
```

### FFmpeg 关键参数

| 参数 | 含义 |
| --- | --- |
| `-pix_fmt` | 像素格式 |
| `-colorspace` | YUV 色彩空间 |
| `-color_primaries` | RGB 色域 |
| `-color_trc` | 伽马曲线 |
| `-color_range` | 范围（tv / pc） |

## 🎨 伽马校正（Gamma Correction）

```
人眼对暗部敏感 → 显示器需要非线性显示
伽马编码: V_display = V_signal^(1/gamma)

gamma = 2.2 (sRGB, BT.709)
gamma = 2.4 (BT.1886)
gamma = 2.6 (BT.2020 12bit)

HDR: PQ (SMPTE ST 2084) / HLG
```

## 🎨 HDR ↔ SDR 转换

### PQ（Perceptual Quantizer, SMPTE ST 2084）

```
PQ 是绝对亮度编码
最大 10000 cd/m²
L = ((F^(1/m2) - c1) / (c2 - c3·F^(1/m2)))^(1/m1)

F = E / 10000
m1 = 0.1593017578125
m2 = 78.84375
c1 = 0.8359375
c2 = 18.8515625
c3 = 18.6875
```

### HLG（Hybrid Log-Gamma）

```
HLG = OETF^-1 (相对亮度)
兼容 SDR，可直接显示在 SDR 屏幕（但会过曝）

HDR → SDR:
  1. Tone mapping (色调映射)
  2. 色域转换
  3. 范围压缩
```

### 色调映射（Tone Mapping）

| 方法 | 特点 |
| --- | --- |
| **Reinhard** | 简单，x/(1+x) |
| **Hable** | 电影感 |
| **ACES** | 业界标准 |
| **Filmic** | 游戏引擎 |

```bash
# FFmpeg HLG → SDR
ffmpeg -i in_hlg.mp4 -vf "zscale=t=linear:npl=100,format=yuv420p,tonemap=hable,format=yuv420p" out_sdr.mp4

# HDR → SDR (BT.2020 → BT.709)
ffmpeg -i in_hdr.mp4 \
       -vf "zscale=p=bt2020:t=bt709:m=bt709:r=tv,format=yuv420p" \
       out_sdr.mp4
```

## 🎨 色域转换

| 输入 | 输出 | 转换矩阵 |
| --- | --- | --- |
| BT.709 | BT.2020 | 3×3 矩阵 |
| BT.2020 | BT.709 | 3×3 矩阵（饱和度降低） |
| sRGB | Display P3 | 3×3 矩阵 |
| DCI-P3 | Rec.2020 | 3×3 矩阵 |

```python
import numpy as np

# BT.709 → BT.2020
M_709_to_2020 = np.array([
    [0.6274, 0.3293, 0.0433],
    [0.0691, 0.9195, 0.0114],
    [0.0164, 0.0880, 0.8956]
])

rgb_2020 = M_709_to_2020 @ rgb_709
```

## 🛠️ OpenCV 转换

```python
import cv2
import numpy as np

# BGR → YUV (BT.601)
yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)

# BGR → YUV (BT.709)
yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV_I420)

# BGR ↔ HSV
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

# BGR ↔ Lab
lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
```

## 📌 面试考点

1. YUV vs RGB 区别？
   - YUV 亮度+色度可降采样，节省带宽
2. HDR vs SDR？
   - HDR 更高亮度+色域+位深，需要 PQ/HLG 编码
3. BT.709 vs BT.2020？
   - BT.2020 色域更广，用于 4K/8K
4. 色彩转换为什么会失真？
   - 不同色域裁剪、伽马不匹配

## 🔗 下一步

- [色彩空间 YUV/RGB](/01-basics/color-space)
- [HDR 应用](/10-application/post-product)
- [FFmpeg 实战](/06-tools/ffmpeg)