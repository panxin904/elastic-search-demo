---
title: 视频修复 Inpainting
date: 2026-08-15  # date-auto-injected
---

# 视频修复（Video Inpainting）

<span class="kg-badge kg-badge-ai">AI</span>
<span class="kg-badge kg-badge-algorithm">算法</span>

用 AI 模型**填充**视频中的缺失区域（去水印、去字幕、去物体）。

## 🧠 任务定义

```
输入:
  - 视频帧
  - Mask（标记要修复的区域）

输出:
  - 修复后的视频帧

用途:
  - 去水印
  - 去字幕
  - 去物体
  - 旧片修复（划痕、噪点）
```

## 📐 应用场景

| 场景 | 描述 |
| --- | --- |
| **去水印** | 移除电视台 logo |
| **去字幕** | 翻译前移除硬字幕 |
| **去物体** | 移除不需要的物体 |
| **旧片修复** | 划痕、霉斑、补帧 |
| **遮挡恢复** | 修复拍摄遮挡 |
| **隐私保护** | 打码（逆向） |

## 📊 图像修复模型

| 模型 | 年份 | 特点 |
| --- | --- | --- |
| **Context Encoder** | 2016 | 第一篇深度学习 |
| **PatchMatch** | - | 传统 |
| **DeepFill v1** | 2018 | 自由形式 |
| **DeepFill v2** | 2019 | 门控卷积 |
| **EdgeConnect** | 2019 | 边缘引导 |
| **MEDFE** | 2020 | 多尺度 |
| **LaMa** | 2022 | 大感受野 |
| **MAT** | 2022 | Mask-Aware Transformer |
| **ZITS** | 2022 | Transformer + 边缘 |
| **CoModGAN** | 2022 | 大规模 GAN |
| **RePaint** | 2022 | 扩散模型 |
| **Diffusion Inpainting** | 2023 | SD 修复 |

### LaMa（Large Mask Inpainting）

```
原理:
  - Fourier 卷积（大感受野）
  - 简单架构
  - 高分辨率训练

效果:
  - 大 mask 修复好
  - 速度快
  - 开源
```

### Stable Diffusion Inpainting

```
原理:
  - 扩散模型
  - 用 mask 引导生成
  - 文本 prompt 可控

效果:
  - 真实感强
  - 可控（prompt）
  - 慢
```

## 📊 视频修复模型

| 模型 | 年份 | 特点 |
| --- | --- | --- |
| **Deep Video Inpainting** | 2019 | 时域一致 |
| **DFVI** | 2020 | 深度流引导 |
| **FuseFormer** | 2021 | Transformer 视频 |
| **STTN** | 2020 | 时空 Transformer |
| **Flow-Guided** | - | 光流引导 |
| **E2FGVI** | 2022 | 端到端流引导 |
| **ProPainter** | 2023 | 传播修复 |
| **DiffusionVIP** | 2023 | 扩散视频 |

### ProPainter 原理

```
1. 双输入：当前帧 + 邻帧
2. 提取光流
3. 传播（warp + mask 传播）
4. Transformer 融合

效果: SOTA
```

## 🛠️ ProPainter 使用

```bash
# GitHub: sczhou/ProPainter

# 安装
pip install -r requirements.txt

# 下载模型
bash scripts/download_weights.sh

# 推理
python inference.py \
  --video inputs/object_removal/bmx-trees.mp4 \
  --mask inputs/object_removal/bmx-trees_mask.mp4 \
  --output outputs/bmx-trees.mp4
```

## 🛠️ LaMa 命令行

```bash
# GitHub: advimman/lama

# Docker
docker build -t lama .
docker run --gpus all -v $(pwd)/data:/data lama \
  python bin/predict.py model.path=/data/big-lama.pt \
    indir=/data/input outdir=/data/output
```

## 🛠️ SD Inpainting

```python
from diffusers import StableDiffusionInpaintPipeline

pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "runwayml/stable-diffusion-inpainting",
    torch_dtype=torch.float16
).to("cuda")

prompt = "a beautiful landscape"
image = PIL.Image.open("image.png")
mask_image = PIL.Image.open("mask.png")

result = pipe(
    prompt=prompt,
    image=image,
    mask_image=mask_image,
).images[0]

result.save("output.png")
```

## 📊 修复 vs 超分

| 维度 | 修复 | 超分 |
| --- | --- | --- |
| 输入 | 缺损 + mask | 低清 |
| 输出 | 完整 | 高清 |
| 难度 | 较高 | 较低 |
| 应用 | 去水印、修复 | 放大 |

## 📐 Mask 类型

| 类型 | 说明 |
| --- | --- |
| **细线 mask** | 字幕、划痕 |
| **矩形 mask** | 简单遮挡 |
| **自由 mask** | 任意形状 |
| **关键点 mask** | 指点 |

## 📐 评估指标

| 指标 | 含义 |
| --- | --- |
| **PSNR** | 像素级 |
| **SSIM** | 结构 |
| **LPIPS** | 感知 |
| **FID** | 分布 |
| **User Study** | 人工评分 |
| **时域一致性** | 帧间一致 |

## ⚠️ 局限

| 局限 | 说明 |
| --- | --- |
| **大 mask 修复** | 仍可能不自然 |
| **时域闪烁** | 视频修复常见 |
| **结构错乱** | 复杂场景 |
| **计算慢** | 视频逐帧处理 |

## 📌 面试考点

1. 修复 vs 超分？
   - 修复 = 补全；超分 = 放大
2. 时域一致性怎么做？
   - 帧间约束、传播、光流
3. SD 修复原理？
   - Mask 引导扩散生成
4. 视频去水印难点？
   - 时域一致性 + 运动场景

## 🔗 下一步

- [AI 超分](/07-ai/super-res-ai)
- [视频分割](/07-ai/segmentation)
- [视频生成](/07-ai/generation)