---
title: 去噪算法
---

# 去噪算法

<span class="kg-badge kg-badge-algorithm">算法</span>
<span class="kg-badge kg-badge-ai">AI</span>

去除视频采集、压缩、传输过程中引入的**噪声**，提升画质。

## 🔬 噪声类型

| 噪声 | 特征 | 来源 |
| --- | --- | --- |
| **高斯噪声** | 正态分布 | 低光照传感器 |
| **椒盐噪声** | 黑白点 | 老旧设备、传输 |
| **泊松噪声** | 散粒噪声 | 相机传感器 |
| **量化噪声** | 量化误差 | 编码压缩 |
| **散斑噪声** | 相干斑 | 雷达、医学成像 |
| **块效应** | 块边界 | 视频编码 |
| **振铃** | 边缘振荡 | 锐化、压缩 |

## 📊 传统去噪算法

### 空间域滤波

| 算法 | 原理 | 速度 |
| --- | --- | --- |
| **均值滤波** | 邻域像素平均 | 极快 |
| **中值滤波** | 邻域中值 | 快 |
| **高斯滤波** | 加权平均 | 快 |
| **双边滤波** | 空间 + 颜色加权 | 慢 |
| **非局部均值 (NLM)** | 整图相似块加权 | 极慢 |

### 时空域滤波

| 算法 | 特点 |
| --- | --- |
| **VBM3D** | 视频 3D 块匹配 + 协同滤波（SOTA 传统） |
| **VNLB** | 非局部 Bayes |
| **快时均值** | 多帧平均（适合静态场景） |

### 变换域滤波

| 算法 | 原理 |
| --- | --- |
| **小波去噪** | 小波域阈值 |
| **DCT 阈值** | 频域置零 |
| **Curvelet** | 多尺度几何分析 |

## 📐 双边滤波（Bilateral Filter）

```
BF[I]_p = (1/Wp) · Σ_q G_σs(||p-q||)·G_σr(|I_p - I_q|)·I_q

G_σs: 空间高斯（距离权重）
G_σr: 范围高斯（颜色权重）

保边去噪，但速度慢
```

## 📐 非局部均值（NLM）

```
NLM[I]_p = (1/Z(p)) · Σ_q w(p,q)·I_q

w(p,q) = exp(-||P(p) - P(q)||² / h²)

P(p): 以 p 为中心的 patch
w(p,q): patch 相似度

相似 patch 平均去噪，效果极佳
```

## 📐 BM3D（块匹配 3D 滤波）

```
SOTA 传统去噪算法，分两阶段：

第一阶段（硬阈值）:
  1. 块匹配找相似块
  2. 堆叠成 3D 组
  3. 3D DCT 变换
  4. 硬阈值（去噪）
  5. 3D IDCT
  6. 聚合

第二阶段（维纳滤波）:
  基于第一阶段结果
  使用维纳滤波（更精细）
```

### BM3D 衍生

| 算法 | 改进 |
| --- | --- |
| **BM3D-SAPCA** | 形状自适应 PCA |
| **VBM3D** | 视频版本 |
| **V-BM3D** | 视频 + 光流 |
| **VBM4D** | 时空 4D |

## 🤖 AI 去噪

### 图像去噪

| 模型 | 年份 | 特点 |
| --- | --- | --- |
| **DnCNN** | 2016 | 残差学习 |
| **FFDNet** | 2018 | 灵活噪声水平 |
| **CBDNet** | 2019 | 真实噪声 |
| **RIDNet** | 2019 | 残差图像去噪 |
| **Restormer** | 2021 | Transformer |
| **NAFNet** | 2022 | 简化激活 |

### 视频去噪

| 模型 | 特点 |
| --- | --- |
| **FastDVDnet** | 实时 |
| **DUFNet** | 时空滤波 |
| **BasicVSR++** | 视频超分 + 去噪 |
| **RVRT** | Recurrent Video Restoration Transformer |
| **EMT** | Efficient Multi-frame Transformer |

### 真实噪声去噪

| 模型 | 特点 |
| --- | --- |
| **DnCNN-S** | 真实噪声 |
| **CycleISP** | 相机噪声建模 |
| **LMDNet** | 自适应噪声 |

## 🛠️ FFmpeg 去噪

```bash
# 高质量去噪（hqdn3d）
ffmpeg -i in.mp4 -vf "hqdn3d=4:3:6:4.5" out.mp4

# nlmeans 非局部均值
ffmpeg -i in.mp4 -vf "nlmeans=s=7:p=7:r=7" out.mp4

# 双重去噪
ffmpeg -i in.mp4 -vf "hqdn3d=4:3:6:4.5,unsharp=5:5:1.0" out.mp4

# 数字夜视（极低光）
ffmpeg -i in.mp4 -vf "nlmeans=h=10" out.mp4
```

### hqdn3d 参数

```
hqdn3d=luma_spatial:luma_temporal:chroma_spatial:chroma_temporal

默认: hqdn3d=4:3:6:4.5
  luma_spatial = 4
  luma_temporal = 3
  chroma_spatial = 6
  chroma_temporal = 4.5
```

## 🛠️ OpenCV 去噪

```python
import cv2

# 非局部均值去噪
dst = cv2.fastNlMeansDenoisingColored(
    img, h=10, hColor=10,
    templateWindowSize=7, searchWindowSize=21
)

# 视频去噪（多帧平均）
def denoise_video(frames):
    return np.mean(frames, axis=0)
```

## 🛠️ AI 去噪 (PyTorch)

```python
# Real-ESR-GAN 视频去噪
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet

model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                num_block=23, num_grow_ch=32, scale=4)
upsampler = RealESRGANer(scale=4, model_path='RealESRGAN_x4plus.pth',
                         model=model, device='cuda')

output, _ = upsampler.enhance(img, outscale=4)
```

## 📌 面试考点

1. 高斯滤波 vs 中值滤波？
   - 高斯平滑但模糊；中值保边去椒盐
2. BM3D 为什么好？
   - 块匹配 + 3D 变换域 + 协同滤波
3. AI 去噪优势？
   - 学习真实噪声分布，效果远超传统
4. 视频去噪 vs 图像去噪？
   - 视频可利用时域冗余，效果更好

## 🔗 下一步

- [超分辨率](/04-algorithm/super-res)
- [AI 超分](/07-ai/super-res-ai)
- [锐化算法](/04-algorithm/sharpen)