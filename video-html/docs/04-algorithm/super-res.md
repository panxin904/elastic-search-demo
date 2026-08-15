---
title: 超分辨率（SR）
---

# 超分辨率（Super Resolution）

<span class="kg-badge kg-badge-algorithm">算法</span>
<span class="kg-badge kg-badge-ai">AI</span>

从低分辨率图像/视频**恢复**高分辨率细节，应用广泛。

## 🧠 任务定义

```
输入: LR (Low Resolution)  W × H
输出: HR (High Resolution) kW × kH
缩放倍数 k: 2x, 4x, 8x
```

## 📐 单图超分 vs 视频超分

| 类型 | 输入 | 优势 |
| --- | --- | --- |
| **SISR** (Single Image SR) | 1 张图 | 简单 |
| **VSR** (Video SR) | 多帧 | 可利用时域信息，效果更好 |

## 📊 传统算法

| 算法 | 原理 | 效果 |
| --- | --- | --- |
| **Bicubic** | 4 tap 插值 | 基准 |
| **Lanczos** | 高质量插值 | 较清晰 |
| **Sparse Coding** | 字典学习 | 中 |
| **Self-Exemplar** | 内部相似块 | 中 |

## 🤖 深度学习超分模型

### 早期（2014-2017）

| 模型 | 年份 | 创新 |
| --- | --- | --- |
| **SRCNN** | 2014 | 第一篇 CNN 超分 |
| **FSRCNN** | 2016 | 快速 |
| **VDSR** | 2016 | 残差学习 |
| **LapSRN** | 2017 | 拉普拉斯金字塔 |

### GAN 时代（2017-2020）

| 模型 | 年份 | 创新 |
| --- | --- | --- |
| **SRGAN** | 2017 | 感知损失 GAN |
| **ESRGAN** | 2018 | 改进 GAN |
| **Real-ESRGAN** | 2021 | 真实场景 |
| **BSRGAN** | 2022 | 盲超分 |

### Transformer 时代（2021-2023）

| 模型 | 年份 | 创新 |
| --- | --- | --- |
| **IPT** | 2021 | Image Processing Transformer |
| **SwinIR** | 2021 | Swin Transformer |
| **Restormer** | 2021 | Efficient Transformer |
| **MAXIM** | 2022 | Multi-axis MLP |

### 扩散模型时代（2022-2024）

| 模型 | 年份 | 创新 |
| --- | --- | --- |
| **SR3** | 2021 | DDPM 超分 |
| **LDM-SR** | 2022 | Latent Diffusion |
| **StableSR** | 2023 | Stable Diffusion 超分 |
| **DiffBIR** | 2023 | 盲图像修复 |
| **SeeSR** | 2024 | 真实世界超分 |

## 🎬 视频超分（VSR）

| 模型 | 年份 | 创新 |
| --- | --- | --- |
| **VSRNet** | 2016 | 视频端到端 |
| **VESPCN** | 2017 | 时空亚像素 |
| **BasicVSR** | 2021 | 双向传播 + 残差 |
| **BasicVSR++** | 2022 | 改进传播 |
| **IconVSR** | 2021 | 信息补偿 |
| **TTVSR** | 2022 | Transformer VSR |
| **RVRT** | 2023 | Recurrent VRT |
| **RealBasicVSR** | 2022 | 真实视频 |
| **CUGAN** | - | 动漫超分 |

## 📐 Real-ESRGAN 原理

```
Real-ESRGAN 是当前最流行的开源超分：

架构:
  - RRDB (Residual-in-Residual Dense Block)
  - 生成器 + 判别器 (GAN)

训练:
  - 高清 → 退化 → 模糊 → 训练对
  - 多种退化模拟：JPEG、噪声、模糊、压缩

应用:
  - 老照片修复
  - 视频 2x/4x 放大
  - 漫画/动画增强
```

## 🛠️ Real-ESRGAN 命令

```bash
# 单图
realesrgan-ncnn-vulkan -i input.jpg -o output.png -n 4 -s 4

# 视频
realesrgan-ncnn-vulkan -i input.mp4 -o output.mp4 -n 4 -s 4

# 参数
  -n: 模型 (0-12)
  -s: 缩放倍数 2/3/4
  -f: 输出格式
  -t: tile size (显存)
```

## 🛠️ Python API

```python
import torch
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet

model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                num_block=23, num_grow_ch=32, scale=4)
upsampler = RealESRGANer(scale=4, model_path='RealESRGAN_x4plus.pth',
                         model=model, tile=512, tile_pad=10, pre_pad=0)

img = cv2.imread('lr.png')
output, _ = upsampler.enhance(img, outscale=4)
cv2.imwrite('hr.png', output)
```

## 🛠️ 视频批量超分

```bash
# Video2X 集成
video2x -i in.mp4 -o out.mp4 -p realesrgan -s 4

# ffmpeg + realesrgan
mkdir frames
ffmpeg -i in.mp4 frames/%08d.png
for f in frames/*.png; do
  realesrgan-ncnn-vulkan -i "$f" -o "${f%.png}_sr.png" -s 4
done
ffmpeg -r 30 -i frames/*_sr.png -c:v libx264 -crf 18 out.mp4
```

## 📐 评价指标

| 指标 | 含义 | 范围 |
| --- | --- | --- |
| **PSNR** | 峰值信噪比 | dB, 越高越好 |
| **SSIM** | 结构相似度 | 0-1, 越高越好 |
| **LPIPS** | 感知相似度 | 0-1, 越低越好 |
| **NIQE** | 自然图像质量 | 越低越好 |
| **FID** | Fréchet 距离 | 越低越好 |

## 📊 应用场景

| 场景 | 倍数 | 模型 |
| --- | --- | --- |
| **老片修复** | 4x | Real-ESRGAN |
| **动漫超分** | 2-4x | CUGAN |
| **监控清晰化** | 4-8x | Real-ESRGAN |
| **视频会议** | 实时 2x | FSRCNN |
| **医学影像** | 2-4x | EDSR |
| **卫星图像** | 4x | SwinIR |

## 📌 面试考点

1. 传统 vs AI 超分？
   - AI 学习真实数据，效果远超传统
2. Real-ESRGAN 为什么好？
   - 真实场景退化建模 + 大模型
3. 视频超分难点？
   - 时域一致（避免抖动）
4. 超分倍数上限？
   - 8x+ 容易失真（脑补），4x 是常用上限

## 🔗 下一步

- [AI 超分](/07-ai/super-res-ai)
- [AI 视频生成](/07-ai/generation)
- [缩放插值](/04-algorithm/scaling)