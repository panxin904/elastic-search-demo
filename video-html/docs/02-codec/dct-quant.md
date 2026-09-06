---
title: DCT 变换与量化
date: 2026-08-15  # date-auto-injected
---

# DCT 变换与量化
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 480" font-family="-apple-system,BlinkMacSystemFont,'PingFang SC',sans-serif">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
    </marker>
  </defs>
  <rect class="at-svg-bg" width="600" height="480"/>
  <text class="at-svg-title" x="300" y="32" text-anchor="middle" font-size="20" font-weight="600">视频编码核心：DCT + 量化</text>
  <text x="300" y="56" text-anchor="middle" font-size="13" fill="#64748b">空域 → 频域 · 量化丢高频 · 主流 H.264/265/AV1 都用</text>

  <!-- 编码流程 -->
  <g>
    <text x="50" y="90" font-size="13" font-weight="700" fill="#1e293b">① 视频编码核心 6 步</text>

    <rect class="at-hover-card" x="40" y="105" width="80" height="60" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="80" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">像素</text>
    <text x="80" y="148" text-anchor="middle" font-size="9" fill="#475569">YUV 帧</text>

    <path d="M120,135 L145,135" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="145" y="105" width="80" height="60" rx="6" fill="#dcfce7" stroke="#10b981" stroke-width="1.5"/>
    <text x="185" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#047857">分块</text>
    <text x="185" y="148" text-anchor="middle" font-size="9" fill="#10b981">8×8 / 4×4</text>

    <path d="M225,135 L250,135" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="250" y="105" width="80" height="60" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="290" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">DCT</text>
    <text x="290" y="148" text-anchor="middle" font-size="9" fill="#f59e0b">→ 频域</text>

    <path d="M330,135 L355,135" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="355" y="105" width="80" height="60" rx="6" fill="#e9d5ff" stroke="#8b5cf6" stroke-width="1.5"/>
    <text x="395" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#5b21b6">量化</text>
    <text x="395" y="148" text-anchor="middle" font-size="9" fill="#8b5cf6">丢高频</text>

    <path d="M435,135 L460,135" stroke="#64748b" stroke-width="1.5" fill="none" marker-end="url(#arr)"/>

    <rect class="at-hover-card" x="460" y="105" width="100" height="60" rx="6" fill="#fee2e2" stroke="#dc2626" stroke-width="1.5"/>
    <text x="510" y="128" text-anchor="middle" font-size="11" font-weight="700" fill="#991b1b">熵编码</text>
    <text x="510" y="148" text-anchor="middle" font-size="9" fill="#dc2626">→ 比特流</text>
  </g>

  <!-- DCT 8x8 示意 -->
  <g>
    <text x="50" y="195" font-size="13" font-weight="700" fill="#1e293b">② 8×8 DCT 块频域分布</text>

    <rect class="at-hover-card" x="40" y="205" width="240" height="160" rx="6" fill="#fef3c7" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="160" y="227" text-anchor="middle" font-size="11" font-weight="700" fill="#92400e">8×8 频域系数</text>

    <!-- 简化的 8x8 矩阵示意（用 4x4 表示） -->
    <text x="50" y="247" font-size="10" fill="#10b981" font-weight="700">+ 低频 DC</text>
    <text x="50" y="262" font-size="10" fill="#475569">- 中频</text>
    <text x="50" y="277" font-size="10" fill="#dc2626">- 高频 → 量化置零</text>

    <!-- 矩阵 -->
    <g transform="translate(155, 245)">
      <rect x="0" y="0" width="22" height="22" fill="#10b981" opacity="0.9"/>
      <rect x="22" y="0" width="22" height="22" fill="#f59e0b" opacity="0.7"/>
      <rect x="44" y="0" width="22" height="22" fill="#94a3b8" opacity="0.5"/>
      <rect x="66" y="0" width="22" height="22" fill="#94a3b8" opacity="0.3"/>
      <rect x="0" y="22" width="22" height="22" fill="#f59e0b" opacity="0.6"/>
      <rect x="22" y="22" width="22" height="22" fill="#94a3b8" opacity="0.4"/>
      <rect x="44" y="22" width="22" height="22" fill="#94a3b8" opacity="0.2"/>
      <rect x="66" y="22" width="22" height="22" fill="#dc2626" opacity="0.2"/>
      <rect x="0" y="44" width="22" height="22" fill="#94a3b8" opacity="0.4"/>
      <rect x="22" y="44" width="22" height="22" fill="#94a3b8" opacity="0.3"/>
      <rect x="44" y="44" width="22" height="22" fill="#dc2626" opacity="0.1"/>
      <rect x="66" y="44" width="22" height="22" fill="#dc2626" opacity="0.05"/>
      <rect x="0" y="66" width="22" height="22" fill="#94a3b8" opacity="0.2"/>
      <rect x="22" y="66" width="22" height="22" fill="#dc2626" opacity="0.1"/>
      <rect x="44" y="66" width="22" height="22" fill="#dc2626" opacity="0.05"/>
      <rect x="66" y="66" width="22" height="22" fill="#dc2626" opacity="0.02"/>
    </g>
    <text x="220" y="265" text-anchor="middle" font-size="9" fill="#64748b">左上是低频</text>
    <text x="220" y="290" text-anchor="middle" font-size="9" fill="#64748b">右下是高频</text>
    <text x="160" y="350" text-anchor="middle" font-size="10" font-weight="700" fill="#92400e">Z 字扫描 → 0 多 → RLE 压缩</text>

    <rect class="at-hover-card" x="295" y="205" width="265" height="160" rx="6" fill="#dbeafe" stroke="#3b82f6" stroke-width="1.5"/>
    <text x="427" y="227" text-anchor="middle" font-size="11" font-weight="700" fill="#1e40af">量化矩阵（QP 调节）</text>

    <rect x="310" y="245" width="240" height="20" rx="3" fill="#f1f5f9"/>
    <text x="430" y="259" text-anchor="middle" font-size="9" font-family="monospace" fill="#475569">16 11 10 16 24 40 51 61</text>

    <rect x="310" y="270" width="240" height="20" rx="3" fill="#f1f5f9"/>
    <text x="430" y="284" text-anchor="middle" font-size="9" font-family="monospace" fill="#475569">12 12 14 19 26 58 60 55</text>

    <rect x="310" y="295" width="240" height="20" rx="3" fill="#f1f5f9"/>
    <text x="430" y="309" text-anchor="middle" font-size="9" font-family="monospace" fill="#475569">14 13 16 24 40 57 69 56</text>

    <rect x="310" y="320" width="240" height="20" rx="3" fill="#f1f5f9"/>
    <text x="430" y="334" text-anchor="middle" font-size="9" font-family="monospace" fill="#475569">14 17 22 29 51 87 80 62</text>

    <text x="310" y="358" font-size="9" fill="#3b82f6">特点：左上小（保留低频），右下大（丢弃高频）</text>
  </g>

  <!-- 关键点 -->
  <text x="50" y="395" font-size="10" fill="#64748b">💡 DCT 是有损压缩的根因，量化步长 QP 决定画质：QP 小 → 高质量大文件；QP 大 → 低质量小文件</text>
  <text x="50" y="412" font-size="10" fill="#10b981">📌 现代编码（H.265/AV1）用 4×4 / 8×8 / 16×16 / 32×32 多种块尺寸自适应</text>
  <text x="50" y="430" font-size="10" fill="#f59e0b">⚠️ I 帧内所有块都做 DCT，P/B 帧用残差（预测差）做 DCT → 压缩率更高</text>
</svg>


<span class="kg-badge kg-badge-codec">原理</span>
<span class="kg-badge kg-badge-codecs">频域</span>

视频编码中两个**最关键的步骤**，负责把空间域数据转换到频域并丢弃不重要的细节。

## 🧠 DCT（离散余弦变换）

将**空间域**像素转换为**频域**系数，便于后续量化压缩。

### 二维 DCT 公式

```
F(u, v) = C(u)·C(v) · ΣΣ f(x, y)·cos[(2x+1)uπ/2N]·cos[(2y+1)vπ/2N]

反变换 IDCT:
f(x, y) = ΣΣ C(u)·C(v)·F(u, v)·cos[(2x+1)uπ/2N]·cos[(2y+1)vπ/2N]

C(k) = 1/√2  (k=0)
     = 1     (其他)
```

### 8×8 DCT 示例

```
原始 8×8 块（空间域）       DCT 系数（频域）
┌────────────────────┐      ┌────────────────────┐
│ 200 200 200 200 200 │      │ 1500  -50   20  ... │  ← DC + 低频
│ 200 200 200 200 200 │      │ -30   10    5   ... │  ← 中频
│ 200 200 200 200 200 │  →   │  15   -8    3   ... │  ← 高频（多为 0）
│ 200 200 200 200 200 │      │ ...                 │
└────────────────────┘      └────────────────────┘

能量集中在左上角（低频）
```

## 📊 DCT 块尺寸

| 编码 | DCT 块 |
| --- | --- |
| H.264 | 4×4, 8×8 |
| H.265 | 4×4 ~ 32×32 |
| AV1 | 4×4 ~ 64×64 |
| VVC | 4×4 ~ 64×64 |

## 📐 量化（Quantization）

将 DCT 系数**映射**到更稀疏的表示，是**有损压缩的关键步骤**。

### 量化公式

```
量化值 = round(DCT 系数 / Qstep)
反量化 = 量化值 × Qstep

Qstep = 2^((QP - 4) / 6)

QP 0  → Qstep 1    （无损）
QP 18 → Qstep ~10  （高质量）
QP 23 → Qstep ~20  （默认）
QP 28 → Qstep ~40  （高压缩）
QP 51 → Qstep 224  （最低质量）
```

### QP 与码率关系

```
QP +6  ≈ 码率减半
QP +12 ≈ 码率减 1/4
QP -6  ≈ 码率翻倍
```

## 🔢 量化矩阵（Quantization Matrix）

对不同频率分量使用**不同量化步长**：

```
亮度量化矩阵（H.264 默认 8×8）:
Q =  [16  11  10  16  24  40  51  61]
     [12  12  14  19  26  58  60  55]
     [14  13  16  24  40  57  69  56]
     [14  17  22  29  51  87  80  62]
     [18  22  37  56  68 109 103  77]
     [24  35  55  64  81 104 113  92]
     [49  64  78  87 103 121 120 101]
     [72  92  95  98 112 100 103  99]

低频（重要）→ 量化步长小 → 精细保留
高频（细节）→ 量化步长大 → 粗糙丢失
```

## 📊 DCT 系数扫描

把 8×8 二维系数转换为**一维序列**：

| 方式 | 扫描方式 |
| --- | --- |
| **Z 字形**（Zig-Zag） | 低频在前，高频在后 |
| **水平** | 按行 |
| **垂直** | 按列 |

```
8×8 Z 字形扫描顺序（数字 = 扫描顺序）:

 0  1  5  6 14 15 27 28
 2  4  7 13 16 26 29 42
 3  8 12 17 25 30 41 43
 9 11 18 24 31 40 44 53
10 19 23 32 39 45 52 54
20 22 33 38 46 51 55 60
21 34 37 47 50 56 59 61
35 36 48 49 57 58 62 63
```

## 🎯 RDOQ（率失真优化量化）

```
对每个 DCT 系数，比较量化到 N vs N+1：
  码率差 = R(N+1) - R(N)
  失真差 = D(N+1) - D(N)
  
若 失真差 < λ × 码率差
  → 选择 N+1（更小码率）

RDOQ 平均节省 5-10% 码率
```

## 🔧 高级技术

| 技术 | 编码 | 作用 |
| --- | --- | --- |
| **变换跳过** | H.265 | 跳过 DCT，对屏幕内容高效 |
| **RDOQ** | H.264 | 率失真优化 |
| **DST** | H.265 | 离散正弦变换（亮度 4×4） |
| **ADST/DCT** | AV1/VVC | 自适应变换 |
| **MTS** | H.265 | 多变换选择 |
| **LFNST** | VVC | 低频不可分变换 |

## 📊 失真度量

| 指标 | 公式 | 特点 |
| --- | --- | --- |
| **MSE** | Σ(A-B)² / N | 简单 |
| **PSNR** | 10·log(MAX²/MSE) | 单位 dB，越高越好 |
| **SSIM** | 结构相似度 | 0-1，越高越好 |
| **VMAF** | Netflix 多指标融合 | 0-100，越高越好 |

## 🛠️ FFmpeg 编码参数

```bash
# 设置 QP
ffmpeg -i in.mp4 -c:v libx264 -qp 23 out.mp4

# 设置 CRF（推荐）
ffmpeg -i in.mp4 -c:v libx264 -crf 23 out.mp4

# 设置 preset（编码速度/压缩率）
ffmpeg -i in.mp4 -c:v libx264 -preset slow out.mp4
```

## 📌 面试考点

1. DCT 为什么用余弦不用正弦？
   - 实信号用余弦变换更高效，且实变换
2. 为什么有损压缩主要靠量化？
   - 量化丢弃不重要的细节（高频），人眼不敏感
3. QP 与压缩比关系？
   - QP +6 码率减半
4. PSNR 局限？
   - 不符合人眼主观感受，建议用 VMAF/SSIM

## 🔗 下一步

- [熵编码 CABAC/CAVLC](/02-codec/entropy-codec)
- [环路滤波](/02-codec/loop-filter)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [frontend](https://java-px.bot.cd/frontend/):Web 播放器
- [ai](https://java-px.bot.cd/ai/):视频 AI
- [python](https://java-px.bot.cd/python/):Python 处理
