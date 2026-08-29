---
title: 熵编码 - CABAC / CAVLC
date: 2026-08-15  # date-auto-injected
---

# 熵编码 - CABAC / CAVLC

<span class="kg-badge kg-badge-codec">原理</span>
<span class="kg-badge kg-badge-codecs">无损</span>

将量化后的符号转换为**二进制比特流**，是视频编码的最后一步，**无损压缩**。

## 🧠 熵编码原理

```
符号 → 概率 → 码字（高频短码，低频长码）

例：哈夫曼编码
A (60%) → 0
B (30%) → 10
C (8%)  → 110
D (2%)  → 111
```

## 📊 主流熵编码

| 算法 | 编码 | 特点 |
| --- | --- | --- |
| **CAVLC** | H.264 Baseline | 上下文可变长编码 |
| **CABAC** | H.264 Main/High | 上下文自适应二进制算术编码 |
| **CABAC** | H.265/HEVC | 默认 |
| **ANS** | AV1 | 不对称数字系统 |
| **Arith Coding** | VVC | 算术编码 |

## 📐 CAVLC（上下文自适应可变长编码）

**H.264 Baseline Profile** 使用。

### 编码步骤

```
1. 扫描量化系数（Z 字形）
2. 编码非零系数个数（TotalCoeff）
3. 编码 TrailingOnes（±1 系数）
4. 编码符号（±）
5. 编码系数幅值（Levels）
6. 编码游程（RunBefore）
```

### 5 个码表

| 表 | 用途 |
| --- | --- |
| VLC0 | 短系数幅值 |
| VLC1 | 中等系数幅值 |
| VLC2 | 长系数幅值 |
| ChromaDC | 色度 DC |
| CoeffToken | 系数令牌 |

## 📐 CABAC（上下文自适应二进制算术编码）

**H.264 Main/High Profile 与 H.265 默认**。

### 三步骤

```
1. 二值化 (Binarization)
   符号 → 二进制串（类似 Huffman）

2. 上下文建模 (Context Modeling)
   根据邻块信息选择概率模型
   P(symbol) 基于上下文更新

3. 算术编码 (Arithmetic Coding)
   按概率区间映射为比特流
```

### 二值化方法

| 方法 | 适用 |
| --- | --- |
| **Unary** | 小数值 |
| **Truncated Unary** | 有最大值 |
| **Exp-Golomb** | 通用 |
| **k-th order Exp-Golomb** | 各种大小 |
| **Fixed Length** | 已知范围 |

### 上下文模型（H.265）

| 模型类型 | 数量 |
| --- | --- |
| **Slice Type** | I/P/B 分开 |
| **Element Type** | 不同语法元素 |
| **CTB Position** | 左邻/上邻 |
| **Coefficient Group** | 子块位置 |

```
H.265 CABAC 上下文数:
  亮度: 35 个
  色度: 35 个
  残差系数: 154 个（亮度 105 + 色度 49）
```

## 📐 ANS（不对称数字系统）

**AV1 使用**，比 CABAC 更高效。

```
原理:
  按概率分布直接编码为整数
  符号 s → x = M(s) + state
  state *= 频率

解码:
  按 state 找对应符号
```

### AV1 ANS 特点

| 优点 | 说明 |
| --- | --- |
| 高压缩率 | 比 CABAC 高 1-3% |
| 并行解码 | 符号可独立解码 |
| 整数运算 | 兼容性好 |

## 📊 编码效率对比

| 算法 | 相对压缩率 | 速度 |
| --- | --- | --- |
| CAVLC | 基准 | 快 |
| CABAC | +10-15% | 中 |
| ANS | +1-3% vs CABAC | 中 |

## 🛠️ FFmpeg 相关参数

```bash
# CABAC (默认)
ffmpeg -i in.mp4 -c:v libx264 -coder 1 out.mp4

# CAVLC
ffmpeg -i in.mp4 -c:v libx264 -coder 0 out.mp4

# 选择 profile
ffmpeg -i in.mp4 -c:v libx264 -profile:v baseline out.mp4   # CAVLC
ffmpeg -i in.mp4 -c:v libx264 -profile:v high out.mp4       # CABAC
```

## 🎯 性能优化

| 技术 | 作用 |
| --- | --- |
| **旁路编码 (Bypass)** | 等概率符号，不查表 |
| **终止符号** | 提前终止 |
| **算术编码加速** | SIMD 指令优化 |
| **ANS Range Coder** | AV1 并行友好 |

## 📌 面试考点

1. CABAC vs CAVLC？
   - CABAC 压缩率高 10-15%，但复杂度高
2. 为什么 CABAC 自适应？
   - 上下文模型根据已编码符号动态更新
3. ANS 优势？
   - 支持并行解码，整数运算
4. 熵编码是无损的吗？
   - 是的，熵编码后能完全恢复

## 🔗 下一步

- [环路滤波](/02-codec/loop-filter)
- [H.264](/03-codecs/h264)
- [AV1](/03-codecs/av1)