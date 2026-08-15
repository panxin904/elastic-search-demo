---
title: 去隔行
---

# 去隔行（Deinterlacing）

<span class="kg-badge kg-badge-algorithm">算法</span>
<span class="kg-badge kg-badge-basics">基础</span>

把**隔行扫描**视频转换为**逐行扫描**视频，消除梳齿状边缘。

## 🧠 隔行 vs 逐行

### 隔行扫描（Interlaced）

```
一帧 = 两个场（Field）
  - 顶场（Top Field）: 1, 3, 5, 7... 行
  - 底场（Bottom Field）: 2, 4, 6, 8... 行

1080i: 1920×540 × 2 = 1920×1080 / 30fps
```

### 逐行扫描（Progressive）

```
一帧 = 完整图像

1080p: 1920×1080 / 30fps
```

### 隔行问题

```
运动场景下:
  帧 N 顶场（时间 t）
  帧 N 底场（时间 t+16.67ms）

两场时间不同 → 边缘呈梳齿状
```

## 📐 去隔行算法

### 1. 场合并（Weave）

```
把顶场和底场交错合并

顶场:    顶
底场:       底
合并:    顶 底 顶 底 ...

适合: 静止画面
问题: 运动场景有梳齿
```

### 2. 场丢弃（Bob）

```
只保留一个场，另一个场插值生成

顶场:    A . A . A
底场:    . B . B .
合并:    A C B C A

适合: 快速运动
问题: 分辨率减半
```

### 3. 线性插值（Linear）

```
底场像素 = (上行 + 下行) / 2

适合: 低速运动
```

### 4. 运动自适应（Motion Adaptive）

```
检测运动:
  静止 → 场合并
  运动 → 场插值

效果最好，复杂度高
```

### 5. 时域插值（Motion Compensated）

```
使用光流估计运动矢量
按运动矢量场插值

效果最佳，计算昂贵
```

### 6. AI 去隔行

```
神经网络学习场→帧映射
输入两场 → 输出完整帧

DAIN / RIFE / FILM 等模型
```

## 🛠️ FFmpeg 去隔行

```bash
# 自动检测 + yadif（默认）
ffmpeg -i in.mp4 -vf "yadif" out.mp4

# yadif 参数
yadif=mode:parity:auto
  mode:
    0 = frame & picture are interlaced
    1 = frame is content of top field first
  parity:
    0 = top field first
    1 = bottom field first
  auto:
    0 = disabled
    1 = auto detect

# 例子
ffmpeg -i in.mp4 -vf "yadif=1:0:0" out.mp4

# 复杂自适应
ffmpeg -i in.mp4 -vf "yadif=mode=1:parity=0:auto=1" out.mp4

# 高级算法 bwdif
ffmpeg -i in.mp4 -vf "bwdif=mode=1:parity=0" out.mp4

# 强制按帧率输出
ffmpeg -i in.mp4 -vf "yadif,scale=1920:1080,fps=30" out.mp4
```

### FFmpeg 检测场序

```bash
# 检测隔行
ffprobe -i in.mp4 -show_streams -select_streams v:0 | grep field_order

输出:
  field_order=tt  # 顶场优先
  field_order=bb  # 底场优先
  field_order=progressive  # 逐行
```

## 📊 算法对比

| 算法 | 速度 | 画质 | 复杂度 |
| --- | --- | --- | --- |
| **Weave** | 最快 | 静态好/运动差 | 极低 |
| **Bob** | 快 | 分辨率减半 | 低 |
| **Linear** | 快 | 中 | 低 |
| **Motion Adaptive** | 中 | 好 | 中 |
| **YADIF** | 中 | 较好 | 中 |
| **BWDIF** | 中 | 很好 | 中高 |
| **MC** | 慢 | 优秀 | 高 |
| **AI** | GPU | **最佳** | 高 |

## 🤖 AI 去隔行模型

| 模型 | 特点 |
| --- | --- |
| **DAIN** | 深度感知插帧 |
| **RIFE** | 实时帧插值 |
| **FILM** | Google 大场景插帧 |
| **ST-MFNet** | 时空多帧网络 |
| **Real-Time VFI** | 实时 |

## 📌 应用场景

| 场景 | 说明 |
| --- | --- |
| **老 DVD 转码** | 480i/576i → 480p/576p |
| **广播电视录制** | 1080i → 1080p |
| **体育直播** | 高运动场景 |
| **电影归档** | 24fps 隔行 |

## 📌 面试考点

1. 隔行扫描的优缺点？
   - 优点：同样带宽可传双倍帧率
   - 缺点：运动场景有梳齿
2. yadif vs bwdif？
   - bwdif 是 yadif 升级版，5 字段检测，效果更好
3. 何时需要去隔行？
   - 输出逐行显示（电脑/手机）或转码时
4. 1080i 和 1080p 区别？
   - 1080i 是隔行扫描；1080p 是逐行扫描

## 🔗 下一步

- [帧率转换 插帧](/04-algorithm/frc)
- [AI 插帧](/07-ai/interpolation-ai)
- [FFmpeg 实战](/06-tools/ffmpeg)