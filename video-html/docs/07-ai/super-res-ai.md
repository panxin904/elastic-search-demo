---
title: AI 超分辨率
date: 2026-08-15  # date-auto-injected
---

# AI 视频超分辨率

<span class="kg-badge kg-badge-ai">AI</span>
<span class="kg-badge kg-badge-algorithm">算法</span>
<span class="kg-badge kg-badge-tools">模型</span>

用**深度学习**模型对低分辨率视频**重建**高分辨率，效果远超传统算法。

## 🧠 任务定义

```
输入: LR (Low Resolution)  W × H
输出: HR (High Resolution) kW × kH
缩放倍数: 2x / 4x / 8x

LR → 模型 → HR
```

## 📊 单图 vs 视频超分

| 类型 | 优势 | 局限 |
| --- | --- | --- |
| **SISR** | 简单 | 单帧无时域信息 |
| **VSR** | 时域一致 | 计算贵、可能闪烁 |

## 🤖 主流模型

### 单图超分（SISR）

| 模型 | 年份 | 创新 |
| --- | --- | --- |
| **SRCNN** | 2014 | 第一篇 |
| **FSRCNN** | 2016 | 实时 |
| **VDSR** | 2016 | 残差 |
| **LapSRN** | 2017 | 拉普拉斯金字塔 |
| **SRGAN** | 2017 | GAN |
| **ESRGAN** | 2018 | 改进 GAN |
| **Real-ESRGAN** | 2021 | 真实场景 |
| **SwinIR** | 2021 | Transformer |
| **Restormer** | 2021 | Efficient Transformer |
| **StableSR** | 2023 | 扩散模型 |
| **SeeSR** | 2024 | 真实退化 |

### 视频超分（VSR）

| 模型 | 特点 |
| --- | --- |
| **BasicVSR** | 双向传播 |
| **BasicVSR++** | 改进传播 |
| **IconVSR** | 信息补偿 |
| **RealBasicVSR** | 真实视频 |
| **TTVSR** | Transformer |
| **RVRT** | Recurrent VRT |
| **CUGAN** | 动漫 |

## 📐 Real-ESRGAN 详解

**最流行**的开源超分模型。

### 架构

```
Generator (RRDB):
  - 23 个 RRDB 块
  - Residual-in-Residual Dense Block
  - 每个块 5 个 Dense + 残差

Discriminator (Patch GAN):
  - 判别局部 patch
  - 避免全局平均模糊

Loss:
  - L1 像素损失
  - Perceptual loss (VGG)
  - GAN loss
```

### 退化建模

```
Real-ESRGAN 关键创新：高阶退化

训练输入生成:
  1. HR → 模糊 → 噪声 → JPEG → resize → LR

模拟真实低清:
  - 各向异性模糊
  - 相机噪声
  - JPEG 压缩
  - 多次下采样
```

### 模型变体

| 模型 | 用途 |
| --- | --- |
| **RealESRGAN_x4plus** | 真实世界 4x |
| **RealESRGAN_x2plus** | 2x |
| **RealESRGAN_x4plus_anime** | 动漫 4x |
| **realesr-animevideov3** | 动漫视频 |
| **RealESRGANv3-anime** | 动漫 3 |

## 🛠️ 命令行使用

```bash
# 单图
realesrgan-ncnn-vulkan -i input.jpg -o output.png -n 0 -s 4

# 视频
realesrgan-ncnn-vulkan -i input.mp4 -o output.mp4 -n 0 -s 4

# 参数
  -i: 输入
  -o: 输出
  -n: 模型 (0=realesrgan-x4plus, 1=realesrgan-x4plus-anime, ...)
  -s: 缩放倍数 (2/3/4/8)
  -t: tile size (默认 0，自动)
  -f: 输出格式 png/jpg/webp
  -v: 详细输出

# 推荐配置
-n 0 -s 4 -t 512 -f png  # 通用 4x
-n 1 -s 2 -t 256 -f png  # 动漫 2x
```

## 🛠️ Python API

```python
import cv2
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64,
                num_block=23, num_grow_ch=32, scale=4)
upsampler = RealESRGANer(
    scale=4,
    model_path='weights/RealESRGAN_x4plus.pth',
    model=model,
    tile=512,
    tile_pad=10,
    pre_pad=0,
    half=True,    # FP16
    device='cuda' # GPU
)

img = cv2.imread('lr.png')
output, _ = upsampler.enhance(img, outscale=4)
cv2.imwrite('hr.png', output)
```

## 📐 视频批量超分

```bash
# 方法 1: 直接处理视频
realesrgan-ncnn-vulkan -i in.mp4 -o out.mp4 -s 4 -n 0

# 方法 2: 帧序列（更稳）
mkdir frames_in frames_out
ffmpeg -i in.mp4 frames_in/%08d.png
for f in frames_in/*.png; do
  realesrgan-ncnn-vulkan -i "$f" -o "frames_out/$(basename $f)" -s 4
done
ffmpeg -r 30 -i frames_out/%08d.png -c:v libx264 -crf 18 out.mp4

# 方法 3: Video2X 集成
video2x -i in.mp4 -o out.mp4 -p realesrgan -s 4
```

## 📊 评价指标

| 指标 | 含义 |
| --- | --- |
| **PSNR** | 像素级 |
| **SSIM** | 结构 |
| **LPIPS** | 感知 |
| **NIQE** | 无参考 |
| **FID** | 分布 |

## 🎯 应用场景

| 场景 | 模型 | 倍数 |
| --- | --- | --- |
| **老片修复** | Real-ESRGAN | 4x |
| **动漫超分** | realesrgan-anime | 2x |
| **监控清晰化** | Real-ESRGAN | 4-8x |
| **手机拍照** | 内置 AI | 实时 |
| **视频会议** | FSRCNN | 实时 |
| **影视后期** | Topaz Video AI | 4x |

## ⚠️ AI 超分局限

```
1. 8x+ 易失真（脑补）
2. 文字可能变形
3. 人脸可能不自然
4. 时域闪烁（视频）
5. 显存消耗大
```

## 📌 面试考点

1. Real-ESRGAN 创新点？
   - 高阶退化建模 + RRDB 架构
2. AI 超分 vs 传统？
   - AI 学习数据，效果远超传统
3. 视频超分难点？
   - 时域一致
4. 超分上限？
   - 4x 是常用上限

## 🔗 下一步

- [视频超分原理](/04-algorithm/super-res)
- [视频修复](/07-ai/inpainting)
- [视频生成](/07-ai/generation)