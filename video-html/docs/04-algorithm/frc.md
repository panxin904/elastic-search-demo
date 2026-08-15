---
title: 帧率转换 / 插帧
---

# 帧率转换 / 插帧（FRC）

<span class="kg-badge kg-badge-algorithm">算法</span>
<span class="kg-badge kg-badge-ai">AI 插帧</span>

通过**插帧**技术改变视频帧率（24fps → 60fps）或补帧生成**慢动作**。

## 🧠 帧率转换类型

| 类型 | 含义 | 用途 |
| --- | --- | --- |
| **上转换** | 24 → 60fps | 高刷显示 |
| **下转换** | 60 → 24fps | 节省带宽 |
| **慢动作** | 30 → 120fps | 体育、动作 |
| **抽帧** | 30 → 15fps | 监控降帧 |

## 📐 帧率转换算法

### 1. 帧重复（Frame Duplication）

```
24fps → 60fps: 每帧重复 2-3 次

实现最简单，但卡顿（motion judder）
```

### 2. 帧混合（Frame Blending）

```
24fps → 60fps:
  输出帧 = (1-α) × 帧N + α × 帧N+1

α = 输出时间 - 帧N 时间
α ∈ [0, 1]

会出现"鬼影"（ghosting）
```

### 3. 运动补偿（Motion Compensated）

```
24fps → 60fps:
  1. 计算光流（运动矢量）
  2. 按运动矢量 warp 中间帧

效果最好，复杂度高
```

### 4. AI 插帧（Neural Interpolation）

```
基于深度学习的中间帧生成
DAIN / RIFE / FILM 等

效果最佳，需 GPU
```

## 📐 帧率转换参数

```
输入: 24fps
输出: 60fps

输出时间间隔: 1000/60 = 16.67ms
输入时间间隔: 1000/24 = 41.67ms

插入 36 帧到原 24 帧中（每两帧插 1.5 帧）
```

## 📊 帧率转换算法对比

| 算法 | 速度 | 画质 | 计算 |
| --- | --- | --- | --- |
| **帧重复** | 最快 | 差 | 无 |
| **帧混合** | 快 | 鬼影 | 低 |
| **MC 简单** | 中 | 中 | 中 |
| **MC 复杂** | 慢 | 好 | 高 |
| **AI 插帧** | GPU | **最佳** | 高 |

## 🤖 AI 插帧模型

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

### RIFE 原理

```
输入: 帧 0, 帧 1
目标: 帧 0.5

RIFE 网络:
  1. 提取两帧特征
  2. 估计双向光流
  3. 融合中间帧

输出: 帧 0.5（自然、清晰）
```

### FILM 原理

```
Google 大场景插帧：
  1. 特征金字塔
  2. 多尺度运动估计
  3. 双向融合
  4. 残差细化
```

### DAIN 原理

```
Depth-Aware Video Frame Interpolation:
  1. 深度估计
  2. 光流估计
  3. 深度感知 warp
  4. 上下文合成
```

## 🛠️ FFmpeg 帧率转换

```bash
# 24 → 60fps（帧混合，默认）
ffmpeg -i in.mp4 -vf "fps=60" out.mp4

# 24 → 60fps（保留原帧）
ffmpeg -i in.mp4 -vf "fps=60:round=near" out.mp4

# 慢动作（30 → 120fps）
ffmpeg -i in.mp4 -vf "fps=120" slowmo.mp4

# 抽帧（30 → 15fps）
ffmpeg -i in.mp4 -vf "fps=15" out.mp4

# 改变播放速度（不插帧）
ffmpeg -i in.mp4 -filter:v "setpts=0.5*PTS" -filter:a "atempo=2.0" fast.mp4
```

### minterpolate 滤镜

```bash
# 运动补偿插帧
ffmpeg -i in.mp4 -vf "minterpolate=fps=60:mi_mode=mci" out.mp4

# 混合模式
ffmpeg -i in.mp4 -vf "minterpolate=fps=60:mi_mode=blend" out.mp4

# 重复模式
ffmpeg -i in.mp4 -vf "minterpolate=fps=60:mi_mode=duplicate" out.mp4
```

## 🛠️ RIFE 集成

```bash
# 安装 rife-ncnn-vulkan
git clone https://github.com/nicknisi/rife-ncnn-vulkan

# 60fps 插帧
rife-ncnn-vulkan -i in_frames/ -o out_frames/ -n 3 -s 2

# 倍数（2 = 2x 倍率）
```

## 🛠️ FFmpeg + AI VFI 集成

```bash
# RIFE ONNX 模型
ffmpeg -i in.mp4 -vf "vfrc=rife_4.6" out.mp4

# Real-Time
ffmpeg -i in.mp4 -vf "vfrc=model=best:fps=60" out.mp4
```

## 📊 应用场景

| 场景 | 帧率转换 | 算法 |
| --- | --- | --- |
| **电影 24→60fps** | 上转换 | FILM/RIFE |
| **体育慢动作** | 4x 慢 | RIFE 实时 |
| **动画补帧** | 24→60 | 帧混合即可 |
| **监控抽帧** | 30→5 | 抽帧 |
| **OLED 高刷** | 30→120 | AI 插帧 |
| **手机慢动作** | 240fps | AI 插帧 |

## 📌 面试考点

1. 帧重复 vs 帧混合？
   - 帧重复快速但卡顿；帧混合平滑但有鬼影
2. AI 插帧为什么好？
   - 学习真实运动规律，无鬼影
3. RIFE 为什么快？
   - 轻量网络 + 实时推理
4. 帧率转换会改变播放速度吗？
   - **不会**，只改变帧数；播放速度由 PTS 决定

## 🔗 下一步

- [AI 插帧 RIFE](/07-ai/interpolation-ai)
- [AI 视频生成](/07-ai/generation)
- [FFmpeg 实战](/06-tools/ffmpeg)