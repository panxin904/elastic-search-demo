---
title: 运动估计与补偿
date: 2026-08-15  # date-auto-injected
---

# 运动估计与补偿（ME/MC）

<span class="kg-badge kg-badge-codec">原理</span>
<span class="kg-badge kg-badge-codecs">P / B 帧</span>

帧间预测的**核心机制**，决定 P/B 帧的压缩效率。

## 🧠 概念区分

| 缩写 | 全称 | 作用 |
| --- | --- | --- |
| **ME** | Motion Estimation 运动估计 | 找最佳匹配块的位置 |
| **MC** | Motion Compensation 运动补偿 | 根据 MV 重建预测值 |

```
ME: 在参考帧中搜索 → 输出 MV (dx, dy)
MC: 用 MV 取参考像素 → 输出预测块
```

## 🎯 运动估计搜索算法

### 全搜索（Full Search）

```
遍历搜索窗口内所有可能位置
复杂度 = (2W+1)(2H+1) × 块大小
例：±16 搜索范围, 16×16 块 = 1089 × 256 = 278K 次

最准确，最慢
```

### 快速算法

| 算法 | 步骤 | 复杂度 |
| --- | --- | --- |
| **三步法 TSS** | 3 步搜索 | O(N²/9) |
| **菱形 DS** | 大菱形→小菱形 | O(N) |
| **六边形 HS** | 六边形→小菱形 | O(N) |
| **EPZS** | 预测起点 + 菱形 | O(N) |
| **UMH** | 不均匀多六边形 | O(N) |
| **TZSearch** | H.265/HEVC | O(N) |

### TZSearch 流程（H.265/HEVC）

```
1. AMVP 起点
2. 起点周围菱形/六边形搜索
3. Raster 扫描
4. 全搜索（最后 fallback）
```

## 📐 块匹配准则

```
SAD  = Σ |A(x,y) - B(x+dx, y+dy)|       // 最常用
SSE  = Σ (A - B)²
SATD = Σ |Hadamard(A - B)|             // H.264/HEVC 模式选择
```

### 复杂度对比

```
SAD < SATD < SSE
速度   SAD > SATD > SSE
```

## 📐 亚像素运动估计

### 像素精度

| 精度 | 编码 | 复杂度 |
| --- | --- | --- |
| **整像素** | 所有 | 1× |
| **1/2 像素** | H.264 | 4× |
| **1/4 像素** | H.264+ | 16× |
| **1/8 像素** | H.265/AV1 | 64× |
| **1/16 像素** | VVC | 256× |

### H.264 1/2 像素插值（6-tap）

```
1/2 像素 = (A - 5B + 20C + 20D - 5E + F) / 32

A B C D E F  G
        ↓
        h
```

### H.265 1/4 像素插值（8-tap）

```
更高精度，更多参考像素
```

## 📊 运动矢量编码

### MV 预测（MVP）

```
MV_pred = Median(MV_left, MV_top, MV_top_right)

MV_diff = MV - MV_pred
```

只编码 MV_diff，节省大量比特。

### H.265 AMVP

```
候选 MV 列表（最多 5 个）:
  1. 左邻块 MV（缩放）
  2. 上邻块 MV（缩放）
  3. 右上邻块 MV
  4. 时间共位块 MV
  5. 零 MV

选择最优作为 MVP
```

### Merge / Skip 模式

```
Merge: 直接用邻块 MV，不传 MV
Skip: 同上 + 全零残差
```

## 🎯 双向预测（B 帧）

```
B 帧预测 = α × R0 + β × R1

权重 α、β 可等于 1/2（默认）或自适应
```

### 多参考帧

```
R0 R1 R2 R3 ... R15
 ↑      ↑      ↑
 B帧可任选2个参考帧

提高压缩率 5-10%
```

## 🎬 GOP 结构

```
GOP = Group of Pictures

典型:
IBBPBBPBBPBBPBB IBBPBBPBBPBBPBB IB...
└── GOP1 ───┘└── GOP2 ───┘└─ GOP3

长度 N = 25/30/50/100/250
```

## 🔬 高级技术

| 技术 | 编码 | 作用 |
| --- | --- | --- |
| **OBMC** | H.263/H.264 | 重叠块补偿 |
| **加权预测** | H.264 | 场景切换 |
| **Wedge/Geo** | VVC | 分割 B 帧块 |
| **BIO** | H.265 | 双向光流补偿 |
| **PROF** | VVC | 预测细化 |
| **Affine ME** | H.266 | 仿射运动（缩放/旋转） |

## 🛠️ FFmpeg 调参

```bash
# x264 运动估计
-x264-params "me=umh:merange=24:subq=7"

# x265 运动估计
-x265-params "me=star:merange=57:subq=3"

# 强制整像素（最低复杂度）
-x264-params "me=esa:subme=0"
```

## 📌 面试考点

1. 全搜索和菱形搜索的取舍？
   - 全搜索最优但极慢；菱形搜索速度快，结果接近
2. 1/4 像素 ME 提升多少？
   - 提升 10-20% 压缩率
3. ME 复杂度占比？
   - 编码器 60-80% 时间花在 ME
4. OBMC 是什么？
   - 重叠块运动补偿，平滑块边界

## 🔗 下一步

- [帧间预测](/02-codec/inter-prediction)
- [环路滤波](/02-codec/loop-filter)
- [硬件加速](/08-perf/nvenc-qsv)