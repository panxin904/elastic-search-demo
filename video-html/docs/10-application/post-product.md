---
title: 影视后期
date: 2026-08-15  # date-auto-injected
---

# 影视后期与调色

<span class="kg-badge kg-badge-app">应用</span>
<span class="kg-badge kg-badge-codec">专业</span>
<span class="kg-badge kg-badge-tools">DAW</span>

影视后期（Post-Production）涵盖 **剪辑、调色、特效合成、声音、输出母版**。

## 🎬 影视后期流程

```
原始素材 → 套底 (DIT/数据管理) → 剪辑 → 调色 → 视觉特效 → 声音 → 合成 → 输出
   RAW       Asset Manager           Edit  Color VFX           Audio  Comp   Master
   ARRIRAW                            AAF  OCN  CG               M&E    DPX  DCP
   ProRes                                                                      IMSC
```

## 📼 原始格式（ProRes / BRAW / ARRIRAW）

### 主流相机格式

| 格式 | 来源 | 特点 |
| --- | --- | --- |
| **ARRIRAW** | ARRI Alexa | 电影级 RAW |
| **RED RAW (.r3d)** | RED V-Raptor | 高分辨率 RAW |
| **BRAW** | Blackmagic | 12-bit RAW |
| **ProRes RAW** | 多种相机 | Apple 生态 |
| **X-OCN** | Sony Venice | 16-bit RAW |
| **ProRes 4444 XQ** | Apple / Final Cut | 高码率中间片 |
| **DPX** | 数字中间片 | 序列帧 |
| **EXR** | OpenEXR | 高动态范围 |

### 转码中间格式

```
RAW 输入 → 解拜尔 → ProRes 4444 → 剪辑 / 调色
                                     ↓
                                后期合成 / 输出母版
```

### FFmpeg 中间格式

```bash
# RAW 转 ProRes 422 HQ
ffmpeg -i input.ari \
  -c:v prores_ks -profile:v 3 -vendor ap10 \
  -bits_per_mastored_sample 10 \
  output.mov
```

## 🎞️ 剪辑（Editing）

### 主流 NLE

| 软件 | 厂商 | 特点 |
| --- | --- | --- |
| **DaVinci Resolve** | Blackmagic | 调色 + 剪辑一体 |
| **Final Cut Pro** | Apple | macOS 优化 |
| **Premiere Pro** | Adobe | 行业标准 |
| **Avid Media Composer** | Avid | 行业电影标准 |
| **Vegas Pro** | Magix | 高效 |

### 时间线概念

```
时间线:
V1: 主视频
V2: 画中画 / 字幕
V3: 合成 / 特效
A1: 主音频
A2: 音乐
A3: 音效
A4: 配音
```

### 剪辑关键帧

```
关键点1       关键点2
  ↓              ↓
  ●──────◇──────●
   慢速 -> 正常 -> 快速
```

## 🎨 调色（Color Grading）

### 一级调色（Primary）

```python
# OpenColorIO 处理一级调色
import PyOpenColorIO as ocio

# 加载 .cube 文件
processor = ocio.Processor();
transform = ocio.FileTransform(src='primaries.cube');
processor.apply(transform);
```

工具：
- Lift / Gamma / Gain（RGB 阴影 / 中间 / 高光）
- 饱和度
- 对比度
- 色相

### 二级调色（Secondary）

- 限定器（HSL / 亮度 / 范围）
- 蒙版（窗口 / Power Window）
- 跟踪（运动跟踪）

### 主流调色软件

| 软件 | 厂商 | 特点 |
| --- | --- | --- |
| **DaVinci Resolve** | Blackmagic | 行业标准、电影级 |
| **Baselight** | FilmLight | 高端电影 |
| **Nuke** | Foundry | 合成 + 调色 |
| **Lustre** | Autodesk | 高端色彩 |
| **Mistika** | SGO | 实时 HDR |

### LUT 制作与应用

```bash
# 创建 .cube LUT（3D LUT）
# 通常 33x33x33 或 64x64x64
# 文件结构：
TITLE "my-lut"
LUT_3D_SIZE 33
DOMAIN_MIN 0.0 0.0 0.0
DOMAIN_MAX 1.0 1.0 1.0
0.000000 0.000000 0.000000
0.100000 0.050000 0.030000
...
```

### HDR 调色

| 类型 | 范围 | 用途 |
| --- | --- | --- |
| **SDR** | 100 nit | 传统电视 |
| **HDR10** | 1000-4000 nit | 主流 HDR |
| **Dolby Vision** | 最高 10000 nit | 影院 HDR |
| **HLG** | 自适应 | 广播 HDR |

## ✨ 视觉特效（VFX）

### 合成工具

| 软件 | 用途 |
| --- | --- |
| **Nuke** | 节点合成 |
| **After Effects** | 2D 动画 + MG |
| **Fusion** | Resolve 自带 |
| **Houdini** | 粒子 / 流体 / 程序化 |
| **Blender** | 开源 3D + 2D |

### VFX 工作流

```
CG 元素 (多通道 EXR)
   ↓
跟踪 (3D Camera Solve)
   ↓
节点合成 (Nuke)
   ↓
输出 (DPX/EXR 序列)
```

### 抠像（Keying）

| 方法 | 适合 |
| --- | --- |
| **Chroma Key**（绿幕 / 蓝幕） | 影棚拍摄 |
| **Rotoscope**（描边） | 复杂场景 |
| **AI Matting**（MODNet / RVM） | 视频抠像 |
| **Primatte Keyer** | 专业色键 |

```python
# OpenCV 绿幕抠像 (简化版)
def chroma_key(frame, bg_color=(0, 255, 0)):
    # HSV 空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([35, 100, 100])
    upper = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)  # 绿幕区域
    # 与背景合成
    return frame * (1 - mask[..., None]/255.0)
```

## 🔊 声音后期

### 5.1 声道布局

```
┌──────────────────────────────┐
│           L (左前)            │
│                              │
│   Ls        C        Rs      │
│  (左环)    (中)      (右环)   │
│                              │
│           R (右前)            │
│                              │
│           LFE (低音)         │
└──────────────────────────────┘
```

### 7.1.4 Atmos

```
L  R  C  LFE  Ls  Rs  Lss Rss  Ltf Rtf Ltr Rtr
5 主声道 + 2 环绕 + 2 天花 + 2 后置
```

### 音频处理

- **降噪**：iZotope RX / Davinci Resolve Fairlight
- **混响**：Altiverb / Valhalla Room
- **EQ**：Pro-Q / FabFilter
- **压缩**：CLA-2A / SSL Bus Compressor
- **限幅**：L2 / Maxim

## 📦 输出母版

### 数字电影母版 DCP

```
DCP (Digital Cinema Package)
├── ASSETMAP.xml          ← 主清单
├── PKL_<hash>.xml         ← 打包清单
├── CPL_<hash>.xml         ← 内容清单
├── J2K_<hash>.mxf         ← JPEG 2000 视频流（4-12 Mbps)
├── pcm_<hash>.mxf         ← 音频流（24-bit / 48kHz）
└── subtitles_<hash>.xml  ← 字幕
```

### DCP 创建工具

- **easyDCP**
- **DCP-o-matic**（开源）
- **Clipster**（DVS）

### 流媒体母版

| 平台 | 分辨率 | 码率 | 容器 |
| --- | --- | --- | --- |
| **Netflix** | 4K HDR | 16-25 Mbps | .mp4 (x265 / AV1) |
| **YouTube** | 4K HDR | 35-68 Mbps | .mp4 (x264) |
| **Disney+** | 4K HDR10 | 15 Mbps | x265 |
| **Amazon** | 4K HDR | 15-25 Mbps | x265 |

## 🎨 OpenColorIO（OCIO）

影视调色行业标准的色彩管理框架。

```python
import PyOpenColorIO as ocio

# 配置色彩管理
config = ocio.Config.CreateFromEnv()

# ACES 配置示例
config = ocio.Config.CreateFromFile('aces_1.3/config.ocio')
```

OCIO 角色（Role）：
- **reference**: 参考色
- **scene_linear**: 场景线性
- **display_linear**: 显示线性
- **data**: 数据
- **texture**: 纹理

## 🧰 工作管线（Pipeline）

### 调度工具

| 工具 | 类型 | 特点 |
| --- | --- | --- |
| **Deadline** | 渲染农场 | 商业 / 开源 |
| **OpenCue** | 渲染农场 | Google 开源 |
| **Royal Render** | 渲染农场 | 商业 |
| **Tractor** | 调度 | Pixar |

### 数据库

- **PostgreSQL**（项目数据）
- **MongoDB**（文档）
- **MySQL**（资产）

### 资产库

- **Object Storage**（S3 / OSS / COS）
- **SAN**（高速本地）
- **NAS**（工作共享）

## 📊 视频编解码在影视中的应用

### 中间格式

| 格式 | 用途 | 文件大小 |
| --- | --- | --- |
| **ProRes 422 LT** | 剪辑代理 | 中 |
| **ProRes 422 HQ** | 较后期 | 较大 |
| **ProRes 4444 XQ** | 包含 alpha 通道 | 极大 |
| **DNxHR HQX** | Avid 剪辑 | 较大 |
| **CineForm** | GoPro 生态 | 较大 |

### 输出格式

```bash
# Prores 422 HQ 转 H.265 高质量输出
ffmpeg -i input.mov \
  -c:v libx265 \
  -pix_fmt yuv422p10le \
  -preset slow \
  -x265-params "hdr-opt=1:repeat-headers=1:colorprim=bt2020:transfer=smpte2084:colormatrix=bt2020nc" \
  output_hdr.mp4
```

## 🤖 AI 后期工具

### 主流 AI 工具

| 工具 | 用途 |
| --- | --- |
| **Runway ML** | 视频生成、修复、抠像 |
| **Topaz Video AI** | 放大、插帧、降噪 |
| **Resolve Speed Editor** | 自动剪辑 |
| **Adobe Firefly** | AI 素材生成 |
| **Magisto** | 自动剪辑 |
| **Luma AI** | 3D 视频重建 |

### Topaz 工具链

```python
# Topaz Video AI CLI
topaz-video-ai \
  --input input.mp4 \
  --output output_4k.mp4 \
  --aperture-model:hv-03 \
  --noise-reduction:motion-deblur \
  --frame-rate:60 \
  --resolution:4k
```

## 📚 实战案例

### 案例 1：纪录片后期

```
RAW (300h)
   ↓
DIT 套底 (ProRes 422 HQ)
   ↓
剪辑 (Premiere Pro)
   ↓
调色 (DaVinci Resolve)
   ↓
声音后期 (Pro Tools)
   ↓
字幕 + 后期合成 (AE)
   ↓
输出 DCP + 流媒体版
```

### 案例 2：电影后期

```
原始拍摄 (RAW 300h)
   ↓
Offline 剪辑 (代理剪辑)
   ↓
Online 重对位 (原画幅)
   ↓
调色 (ACES / DaVinci)
   ↓
VFX 合成 (Nuke + Houdini)
   ↓
声音 5.1 / Dolby Atmos
   ↓
DCP 输出
```

### 案例 3：广告 TVC

```
拍摄 (1d) → 数据管理
   ↓
剪辑 (1d)
   ↓
调色 (1d)
   ↓
合成 (2-3d)
   ↓
声音 (1d)
   ↓
TV 版 + 网络版输出
```

## 🛠️ 最佳实践

1. **项目管理**：使用 Flowerbox / ProjectLibre
2. **色彩管理**：统一 ACES / Rec.709
3. **数据备份**：3-2-1 规则（3 副本 / 2 介质 / 1 异地）
4. **元数据**：嵌入 XMP + BWF
5. **输出母版**：多种格式（IMSC / DCP / 流媒体）
6. **合作评审**：Frame.io / Wipster
7. **规范命名**：按场景/镜次/版本
8. **网络带宽**：万兆局域 + 4G 备份
9. **算力**：GPU 节点 + 渲染农场
