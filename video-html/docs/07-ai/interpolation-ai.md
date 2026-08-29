---
title: AI 插帧 RIFE / FILM
date: 2026-08-15  # date-auto-injected
---

# AI 视频插帧

<span class="kg-badge kg-badge-ai">AI</span>
<span class="kg-badge kg-badge-algorithm">算法</span>
<span class="kg-badge kg-badge-app">应用</span>

用 AI 模型在两帧之间**生成**中间帧，实现高帧率、慢动作。

## 🧠 任务定义

```
输入: 帧 0, 帧 1
时间: 0, t (0<t<1)
输出: 帧 t (中间帧)

应用:
  - 24fps → 60fps
  - 慢动作（240fps）
  - 补帧（防卡顿）
```

## 📊 主流模型

| 模型 | 年份 | 特点 |
| --- | --- | --- |
| **DAIN** | 2019 | Depth-Aware |
| **AdaCoF** | 2020 | Adaptive Collaboration |
| **CAIN** | 2019 | Channel Attention |
| **FILM** | 2022 | Google 大场景 |
| **RIFE** | 2020 | Real-Time VFI |
| **RIFE v4.6** | 2022 | 实时 SOTA |
| **AMT** | 2023 | Transformer VFI |
| **EMA-VFI** | 2023 | Efficient |
| **Diffusion VFI** | 2024 | 扩散模型 |

## 📐 RIFE 原理

**Real-Time Intermediate Flow Estimation**

```
架构:
  1. IFBlock (Intermediate Flow Block)
     - 估计中间帧时间的光流
  2. Warp 操作
     - 双线性 warp 两帧到中间
  3. 融合网络
     - 合并 warp 结果

关键创新:
  - 残差学习（不需要 ground-truth 中间帧）
  - 实时推理
```

### RIFE 训练

```
无监督训练:
  - 输入连续 3 帧
  - 预测中间帧
  - 与真实中间帧对比
  - 损失函数包括 L1 + 时域约束
```

## 📐 FILM 原理

**Frame Interpolation for Large Motion**（Google）

```
架构:
  1. 多尺度特征提取
  2. 双向光流估计
  3. 仿射变换
  4. 残差细化
  5. Pyramid 处理

关键:
  - 大运动场景
  - 多尺度
  - SOTA 效果
```

## 📐 DAIN 原理

**Depth-Aware Video Frame Interpolation**

```
1. 深度估计
   单目深度网络估计深度图
   
2. 光流估计
   计算双向光流
   
3. 深度感知 warp
   用深度调整 warp
   
4. 上下文合成
   填补 warp 后空洞
```

## 🛠️ RIFE 使用

```bash
# GitHub: megvii-research/ECCV2022-RIFE

# 命令行
python inference.py \
  --img input/frames \
  --output output/frames \
  --scale 2.0  # 2 倍插帧

# 4 倍插帧
python inference.py --img frames --output out --scale 4.0
```

### rife-ncnn-vulkan

```bash
# GitHub: nicknisi/rife-ncnn-vulkan

# 2x 插帧
rife-ncnn-vulkan -i input_frames/ -o output_frames/ -n 3.4 -s 2

# 参数
  -i: 输入目录
  -o: 输出目录
  -n: 模型版本 (3.0/3.1/3.2/3.3/3.4/4.0/4.1/4.2/4.3/4.4/4.5/4.6)
  -s: 缩放 (2x / 4x / 8x)
  -t: tile size
```

## 🛠️ FFmpeg + RIFE

```bash
# 提取帧
mkdir frames
ffmpeg -i in.mp4 frames/%08d.png

# 插帧
rife-ncnn-vulkan -i frames/ -o frames_2x/ -n 4.6 -s 2

# 合成视频
ffmpeg -r 60 -i frames_2x/%08d.png -c:v libx264 -crf 18 out_60fps.mp4
```

## 🛠️ Video2X（GUI/CLI）

```bash
# GitHub: k4yt3x/video2x

# 安装
pip install video2x

# 用 RIFE 插帧
video2x -i in.mp4 -o out_60fps.mp4 -p rife -s 2
```

## 📐 应用场景

| 场景 | 帧率转换 | 算法 |
| --- | --- | --- |
| **电影 24→60fps** | 上转换 | FILM |
| **体育慢动作** | 4x 慢 | RIFE |
| **手机慢动作** | 240fps | RIFE |
| **OLED 高刷** | 30→120 | AI 插帧 |
| **游戏补帧** | 60→120 | DLSS / FSR |

## 📐 评估指标

| 指标 | 含义 |
| --- | --- |
| **PSNR** | 像素级 |
| **SSIM** | 结构 |
| **LPIPS** | 感知 |
| **FloLPIPS** | 流体感知 |
| **User Study** | 人工评分 |

## ⚠️ 局限

| 局限 | 说明 |
| --- | --- |
| **大运动场景** | 可能失真 |
| **遮挡** | 出现/消失物体难处理 |
| **透明度** | 玻璃、水、烟雾 |
| **重复纹理** | 易糊 |

## 📌 面试考点

1. RIFE 为什么快？
   - 轻量网络 + 实时优化
2. AI 插帧 vs 帧混合？
   - AI 自然；混合有鬼影
3. 大运动场景如何处理？
   - 多尺度、运动补偿
4. 慢动作倍数上限？
   - 8x + 可能失真

## 🔗 下一步

- [帧率转换](/04-algorithm/frc)
- [视频生成](/07-ai/generation)
- [数字人](/07-ai/digital-human)