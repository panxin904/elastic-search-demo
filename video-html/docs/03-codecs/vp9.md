---
title: VP9 / VP8
---

# VP9 / VP8（Google 视频编码）

<span class="kg-badge kg-badge-codecs">编码</span>
<span class="kg-badge kg-badge-protocol">开源</span>
<span class="kg-badge kg-badge-tools">Web</span>

**VP9** = Google 开发，**开源免专利**，与 AV1 同源（VP10 → AV1）。

## 📊 VP9 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 2013 |
| 开发者 | Google |
| 现状 | YouTube、WebRTC 主流 |
| 压缩率 | 较 H.264 节省 30-50% |
| 复杂度 | 中高 |
| 专利 | **完全免费**（Google 授权） |
| 容器 | WebM（主）、MP4（次） |

## 🏗️ VP9 关键特性

| 特性 | 说明 |
| --- | --- |
| **块大小** | 64×64 superblock |
| **块划分** | 四叉树 |
| **预测模式** | 10 种帧内（含 TM/Paeth） |
| **变换** | DCT / ADST |
| **MV 精度** | 1/8 像素 |
| **环路滤波** | 去块 + 全像素重建 |
| **熵编码** | 布尔编码器 |

## 📐 VP9 帧内预测

| 模式 | 含义 |
| --- | --- |
| **DC** | 平均值 |
| **True Motion** | 基于邻块预测 |
| **Paeth** | 三个方向选最近 |
| **H/V/45/135/D45/D135** | 角度预测 |

## 📐 VP9 块划分

```
Superblock 64×64
  ├─ 64×64
  ├─ 32×32
  ├─ 16×16
  └─ 8×8

可递归到 4 层
```

## 📊 VP9 Profile

| Profile | 特点 |
| --- | --- |
| **Profile 0** | 8bit 4:2:0 |
| **Profile 1** | 8bit 4:4:4 |
| **Profile 2** | 10/12bit 4:2:0 |
| **Profile 3** | 10/12bit 4:4:4 |

## 🛠️ FFmpeg 编码

```bash
# VP9 编码
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 31 -b:v 0 output.webm

# 两遍编码（高压缩）
ffmpeg -i input.mp4 -c:v libvpx-vp9 -b:v 2M -pass 1 -f null /dev/null
ffmpeg -i input.mp4 -c:v libvpx-vp9 -b:v 2M -pass 2 output.webm

# 实时 VP9（libvpx-VP9）
ffmpeg -i input.mp4 -c:v libvpx-vp9 -deadline realtime -speed 8 output.webm

# WebM 容器
ffmpeg -i input.mp4 -c:v libvpx-vp9 -c:a libopus output.webm
```

## ⚙️ libvpx-vp9 编码速度

| speed | fps | 压缩率 |
| --- | --- | --- |
| 0 | 极慢 | 最高 |
| 4 | 慢 | 高 |
| 8 | 中 | 默认 |
| 12 | 快 | 中 |

## 📊 VP8 vs VP9

| 特性 | VP8 | VP9 |
| --- | --- | --- |
| 推出 | 2008 | 2013 |
| 块大小 | 16×16 max | 64×64 superblock |
| 压缩率 | -25% vs H.264 | -50% vs H.264 |
| 复杂度 | 低 | 中高 |
| 当前 | 已被替代 | Web 标准 |

## 📊 VP9 vs AV1 vs H.265

| 编码 | 推出 | 压缩率 | 复杂度 | 专利 |
| --- | --- | --- | --- | --- |
| **H.264** | 2003 | 基准 | 中 | 付费 |
| **VP9** | 2013 | -50% vs H.264 | 中高 | **免费** |
| **H.265** | 2013 | -50% vs H.264 | 高 | 付费 |
| **AV1** | 2018 | -30% vs HEVC | 极高 | **免费** |

## 📌 应用场景

| 场景 | 原因 |
| --- | --- |
| **YouTube 4K** | 2014 起 VP9 |
| **WebRTC** | VP8 + Opus 标准 |
| **Chrome 浏览器** | 原生支持 |
| **Firefox** | 原生支持 |
| **Android** | 系统支持 |
| **HTML5 video** | WebM 容器 |

## ⚠️ VP9 局限

- 编码慢于 H.265
- 浏览器支持参差不齐（Safari 部分版本）
- 不支持 4:2:2/4:4:4 高端
- 已被 AV1 渐进替代

## 🔗 VP8（已淘汰）

| 用途 | 现状 |
| --- | --- |
| WebRTC 视频 | 仍可选 |
| WhatsApp 视频 | 部分使用 |
| Skype (旧) | 视频通话 |

```bash
# VP8 编码
ffmpeg -i input.mp4 -c:v libvpx -b:v 1M output.webm
```

## 🔗 下一步

- [AV1](/03-codecs/av1)
- [H.265](/03-codecs/h265)
- [WebRTC](/05-protocol/webrtc)