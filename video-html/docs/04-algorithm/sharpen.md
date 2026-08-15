---
title: 锐化算法
---

# 锐化算法

<span class="kg-badge kg-badge-algorithm">算法</span>
<span class="kg-badge kg-badge-tools">FFmpeg</span>

增强视频**边缘对比度**，让画面看起来更清晰锐利。

## 🧠 锐化原理

```
锐化 = 原图 + (原图 - 模糊图) × 强度

Unsharp Mask (USM):
  原图:        I
  模糊图:      blur(I)
  高频:        H = I - blur(I)
  锐化图:      I_sharp = I + α × H

α 越大，锐化越强
```

## 📊 锐化算法

| 算法 | 原理 | 特点 |
| --- | --- | --- |
| **拉普拉斯** | 2 阶微分 | 简单、噪声敏感 |
| **Sobel** | 1 阶微分 | 边缘检测 |
| **Prewitt** | 1 阶微分 | 类似 Sobel |
| **Robert** | 1 阶微分 | 2×2 核 |
| **USM** | Unsharp Mask | 最常用 |
| **Laplacian Filter** | 拉普拉斯核 | FFmpeg unsharp |
| **高通滤波** | 频域高通 | 频域方法 |

## 📐 拉普拉斯算子

```
4 邻域:        8 邻域:
 0  1  0        1  1  1
 1 -4  1        1 -8  1
 0  1  0        1  1  1

锐化图 = 原图 - 拉普拉斯
       = I + α·(I - Laplacian)
```

## 📐 Sobel 算子

```
Gx: 水平       Gy: 垂直
-1  0  1      -1 -2 -1
-2  0  2       0  0  0
-1  0  1       1  2  1

G = sqrt(Gx² + Gy²)
```

## 📐 Unsharp Mask（USM）

```
原图:   I
模糊图: B = Gaussian(I, σ)
掩模:   M = I - B
锐化:   I_sharp = I + k × M

σ: 高斯核大小（控制锐化范围）
k: 强度（0-2）

实际: 在相机、手机、显示器中都用
```

## 📐 FFmpeg unsharp 滤镜

```
unsharp=l_msize_x:l_msize_y:l_amount:h_msize_x:h_msize_y:h_amount

l: 亮度（luma）
h: 色度（chroma）

默认: unsharp=5:5:1.0:5:5:0.0
```

### 用法

```bash
# 默认锐化
ffmpeg -i in.mp4 -vf "unsharp" out.mp4

# 强锐化（luma）
ffmpeg -i in.mp4 -vf "unsharp=5:5:1.5" out.mp4

# 大核锐化（柔和）
ffmpeg -i in.mp4 -vf "unsharp=9:9:2.0" out.mp4

# 锐化 + 降噪组合
ffmpeg -i in.mp4 -vf "hqdn3d=4:3:6:4.5,unsharp=5:5:1.0" out.mp4
```

### 参数详解

| 参数 | 含义 | 默认 | 范围 |
| --- | --- | --- | --- |
| `l_msize_x/y` | 亮度核大小 | 5 | 3-23 (奇数) |
| `l_amount` | 亮度锐化强度 | 1.0 | 0-10 |
| `h_msize_x/y` | 色度核大小 | 5 | 3-23 |
| `h_amount` | 色度锐化强度 | 0.0 | 0-10 |

## 🤖 AI 锐化

| 模型 | 特点 |
| --- | --- |
| **零样本锐化** | Zero-Shot |
| **DeepDeblur** | 模糊 → 锐利 |
| **SR-UKAN** | 超分 + 锐化 |
| **Diffusion Sharpener** | 扩散模型 |
| **StableSR** | 感知细节 |

## 🛠️ OpenCV 锐化

```python
import cv2
import numpy as np

# 方法1: USM
def usm(img, sigma=2.0, amount=1.5):
    blurred = cv2.GaussianBlur(img, (0, 0), sigma)
    sharpened = cv2.addWeighted(img, 1 + amount, blurred, -amount, 0)
    return sharpened

# 方法2: 卷积核锐化
kernel = np.array([[0, -1, 0],
                   [-1, 5, -1],
                   [0, -1, 0]])
sharpened = cv2.filter2D(img, -1, kernel)

# 方法3: 高斯差分 (DOG)
blur1 = cv2.GaussianBlur(img, (0, 0), 1)
blur2 = cv2.GaussianBlur(img, (0, 0), 3)
sharpened = cv2.addWeighted(img, 2.5, blur2, -1.5, 0)
```

## 🎯 应用场景

| 场景 | 强度 |
| --- | --- |
| **直播** | 轻度（amount=0.5） |
| **蓝光转码** | 中度（amount=1.0） |
| **老片修复** | 重度（amount=2.0） |
| **监控清晰化** | 重度（amount=2.5） |
| **AI 生成** | 不需要（已锐利） |

## ⚠️ 锐化的副作用

```
过度锐化导致:
  - 边缘光晕（halo）
  - 噪声放大
  - 振铃（ringing）
  - 图像不自然

解决:
  - 控制强度 amount < 2
  - 与去噪组合
  - 阈值锐化（仅锐化边缘）
```

## 📌 面试考点

1. 锐化为什么会放大噪声？
   - USM 高频 = 边缘 + 噪声，一起放大
2. unsharp 参数如何选择？
   - msize 控制范围（越大越柔和）
   - amount 控制强度（越大越锐）
3. 锐化和超分区别？
   - 锐化是局部增强；超分是改变分辨率
4. AI 锐化优势？
   - 真实纹理细节，非简单边缘增强

## 🔗 下一步

- [去噪算法](/04-algorithm/denoise)
- [超分辨率](/04-algorithm/super-res)
- [缩放插值](/04-algorithm/scaling)