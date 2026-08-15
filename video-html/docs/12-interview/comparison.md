---
title: 编码对比表
---

# 视频编码对比速查

<span class="kg-badge kg-badge-interview">面试</span>
<span class="kg-badge kg-badge-codec">对比</span>

## 🎥 一、视频编码标准对比

### 总览对比

| 特性 | H.264 | H.265 | AV1 | VP9 |
| --- | --- | --- | --- |
| **发布年** | 2003 | 2013 | 2018 | 2013 |
| **制定方** | MPEG-ITU | MPEG-ITU | AOM (Google+...) | Google |
| **免版税** | ❌ | ❌ | ✅ | ✅ |
| **压缩率** | 基准 | -50% | -60% | -55% |
| **编码复杂度** | 1x | 5-10x | 10-30x | 5-10x |
| **解码复杂度** | 1x | 2-3x | 2-5x | 2-3x |
| **硬件支持** | 普及 | 普及 | 发展中 | 少 |
| **主流应用** | 流媒体、存储 | 4K 流媒体 | YouTube、Netflix | Web |
| **Profile** | Baseline/Main/High | Main/Main10 | Main/High/Pro | 0/1/2/3 |
| **Max 像素** | 4K | 8K | 8K | 8K |
| **BitDepth** | 8/10 | 8/10/12 | 8/10/12 | 8/10/12 |

### 编码工具差异

| 工具 | H.264 | H.265 | AV1 |
| --- | --- | --- | --- |
| **块大小** | 16x16 | 64x64 | 128x128 |
| **预测模式** | 9 Intra/16 Inter | 35 Intra/35 Inter | 56+ |
| **DCT 类型** | 8x8 / 4x4 | 4x4 / 8x8 / 16x16 / 32x32 | 16x16 / 32x32 / 64x64 |
| **熵编码** | CAVLC/CABAC | CABAC | ANS + Bool |
| **环路滤波** | DB | DBF + SAO | CDEF / LR |
| **MV 精度** | 1/4 像素 | 1/16 像素 | 1/8 像素 |
| **WPP** | ❌ | ✅ | ✅ |

## 🎵 二、音频编码标准对比

### 总览

| 标准 | 比特率 | 延迟 | 音质 | 应用 |
| --- | --- | --- | --- | --- |
| **MP3** | 128-320k | 高 | 好 | 通用 |
| **AAC-LC** | 64-256k | 中 | 很好 | 流媒体 |
| **AAC-HE** | 32-96k | 中 | 好 | 低带宽 |
| **Opus** | 32-256k | 低 | 优秀 | WebRTC |
| **FLAC** | 无损 | 中 | 无损 | 归档 |
| **AC-3 / E-AC3** | 192-640k | 中 | 良好 | 影院 |
| **Dolby TrueHD** | 18Mbps | 高 | 无损 | 蓝光 |
| **DTS-HD MA** | 18Mbps | 高 | 无损 | 蓝光 |

### 音频编码选择

```
流媒体 / 直播 → AAC-LC
低带宽（声网） → Opus
电影 / 蓝光 → AC-3 / DTS
存储归档 → FLAC / WAV
WebRTC → Opus
```

## 📺 三、流媒体协议对比

| 协议 | 延迟 | 传输 | 适用 |
| --- | --- | --- | --- |
| **RTMP** | 1-3s | TCP | 主播推流（被替代） |
| **HTTP-FLV** | 1-3s | TCP | 端上拉流 |
| **HLS** | 5-30s | TCP | 点播、大规模直播 |
| **LL-HLS** | 1-3s | TCP | 低延迟直播 |
| **DASH** | 5-20s | TCP | 自适应点播 |
| **WebRTC** | < 500ms | UDP | 互动直播 |
| **SRT** | < 1s | UDP | 跨区域 |
| **QUIC** | < 500ms | UDP | 新一代 |

## 🎨 四、容器格式对比

| 格式 | 创始 | 流支持 | 用途 |
| --- | --- | --- | --- |
| **MP4** | Apple/ISO | H.264 + AAC | 通用 |
| **MKV** | Matroska | 任意 | 影视 |
| **WebM** | Google | VP8/VP9/AV1 + Opus | Web |
| **AVI** | Microsoft | 任意 | 古老 |
| **TS / MPEG-TS** | MPEG | H.264/H.265 + AAC | 广播 |
| **FLV** | Macromedia | H.264 + AAC/MP3 | RTMP |
| **3GP** | 3GPP | H.263/AMR | 移动 |
| **HEVC** | MPEG | H.265 | 高清 |

## 🖥️ 五、硬件编码对比

| 厂商 | 编码 | 方案 | 兼容性 |
| --- | --- | --- | --- |
| **NVIDIA** | NVENC | GPU 独立芯片 | RTX 20+ |
| **Intel** | QSV | 集显内置 | Skylake+ |
| **AMD** | AMF | GPU 内置 | RX 400+ |
| **Apple** | VideoToolbox | SoC 内置 | macOS / iOS |
| **Linux** | VAAPI | 通用 | Intel/AMD |
| **Android** | MediaCodec | 系统级 | Android 4.3+ |

### NVENC preset 对比

| Preset | 速度 | 质量 | 适合 |
| --- | --- | --- | --- |
| **ll** | 很快 | 中 | 实时直播 |
| **llhp** | 快 | 中 | 直播 |
| **llhq** | 中 | 中高 | 高质量直播 |
| **hp** | 中 | 高 | 录播 |
| **hq** | 慢 | 很高 | 制作 |
| **bd** | 很慢 | 极高 | 蓝光 |
| **lossless** | 慢 | 无损 | 后期 |

## 📊 六、画质评估方法

| 指标 | 类型 | 适用 |
| --- | --- | --- |
| **PSNR** | 像素差 | 通用 |
| **SSIM** | 结构相似 | 通用 |
| **MS-SSIM** | 多尺度 | 通用 |
| **VMAF** | 多特征融合 | 流媒体（Netflix） |
| **VIF** | 信息论 | 研究 |
| **LPIPS** | 感知 | AI 模型 |
| **DISTS** | 深度图像结构 | AI 模型 |

### PSNR 范围

```
PSNR (dB)    质量
> 40         几乎无感知损失 (高质量)
30-40        良好
25-30        可接受
20-25        一般
< 20         明显失真
```

## 🎯 七、码率与画质（参考）

### 1080p 视频推荐码率

| 场景 | 编码 | 码率 | CRF |
| --- | --- | --- | --- |
| **网络视频** | H.264 | 4000-6000kbps | 23-26 |
| **4K HDR 流** | H.265 | 12-16 Mbps | 23-25 |
| **YouTube 默认** | H.264 | 8-12 Mbps | 18-23 |
| **高质量存储** | H.265 | 10-15 Mbps | 18-20 |
| **极高质量** | AV1 | 6-8 Mbps | 30-35 |

### 帧率与运动

| 内容 | 推荐帧率 |
| --- | --- |
| **电影** | 24 fps |
| **戏剧** | 30 fps |
| **游戏** | 60 fps |
| **体育** | 50-60 fps |
| **慢动作** | 120-240 fps |

## 🔧 八、FFmpeg 编码器对比

### 视频编码器

| 编码器 | 类型 | 速度 | 质量 | 推荐场景 |
| --- | --- | --- | --- | --- |
| **libx264** | 软件 | 中 | 很好 | 通用 |
| **libx265** | 软件 | 慢 | 极高 | 存档 |
| **h264_nvenc** | 硬件 | 极快 | 中好 | 直播 |
| **hevc_nvenc** | 硬件 | 极快 | 好 | 4K 直播 |
| **h264_qsv** | 硬件 | 快 | 中 | 集显机器 |
| **libsvtav1** | 软件 | 中 | 极高 | 多机 |
| **libaom-av1** | 软件 | 极慢 | 极高 | 离线 |
| **rav1e** | 软件 | 慢 | 高 | 灵活 |

### 编码器速度参考

```
libx264 medium:        100% (基准)
libx264 ultrafast:     500%
libx265 slow:           25%
libx265 medium:         50%
hevc_nvenc:           1500%
libsvtav1 preset 6:    300%
libaom-av1 cpu-used 6: 20%
```

## 💻 九、CPU vs GPU 编码对比

| 维度 | CPU 编码 | GPU 编码 |
| --- | --- | --- |
| **质量** | 更优 | 略差（-5%） |
| **速度** | 较慢 | 10-20x CPU |
| **延迟** | 低 | 极低 |
| **并发** | 单流 | 8-16 路并行 |
| **成本** | 中 | GPU 贵但效率高 |
| **灵活** | 任意编码 | 受限 |

### 选择建议

```
实时直播 → GPU 编码（NVENC）
高画质点播 → CPU 编码（libx265）
数量极大 → CPU + GPU 混合
影视剧后期 → CPU 软编（x265 最佳质量）
AI 处理 → NVIDIA GPU（NVDEC + TensorRT）
```

## 📚 十、常用码率配置参考

### 网络视频

```bash
# 1080p H.264 (网络视频 5Mbps)
ffmpeg -i input.mp4 -c:v libx264 -preset medium -crf 23 -b:v 5M -maxrate 5M -bufsize 10M output.mp4

# 720p H.264 (网络视频 2.5Mbps)
ffmpeg -i input.mp4 -c:v libx264 -preset medium -crf 23 -b:v 2.5M output.mp4

# 4K H.265 (网络视频 12Mbps)
ffmpeg -i input.mp4 -c:v libx265 -preset slow -crf 25 -b:v 12M output.mp4
```

### HLS 切片

```bash
ffmpeg -i input.mp4 -c:v libx264 -crf 22 \
  -hls_time 5 -hls_playlist_type vod \
  -hls_segment_filename "out_%03d.ts" \
  playlist.m3u8
```

### WebM / VP9

```bash
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 \
  -row-mt 1 -threads 8 output.webm
```

### AV1

```bash
ffmpeg -i input.mp4 -c:v libsvtav1 -preset 6 -crf 30 output.mkv
```

## 🧪 十一、画质对比工具

### VMAF 计算

```bash
# Netflix vmaf 工具
ffmpeg -i distorted.mkv -i reference.mkv -lavfi libvmaf=model_version=vmaf_v0.6.1.json -f null -

# 或 vmaf-cli
vmaf -r reference.y4m -d distorted.y4m --model vmaf_v0.6.1.json
```

### 主观评测

| 等级 | 说明 |
| --- | --- |
| **Excellent (5)** | 优秀，与原画质无可察觉差异 |
| **Good (4)** | 良好，细节略微损失 |
| **Fair (3)** | 一般，明显损失 |
| **Poor (2)** | 差，严重失真 |
| **Bad (1)** | 极差，无法接受 |

## 📌 速查技巧

### QoS 指标

```
首屏秒开 (TTFB): < 1s
卡顿率: < 1% 播放时长
码率波动: < 10%
```

### 实时直播 QoS

```
推流延迟: < 200ms（编码端到 server）
CDN 延迟: < 100ms
播放延迟: < 200ms
总延迟: < 500ms (WebRTC)
```

### VMAF 分值

```
95+ : 完美
85-95: 高质量
70-85: 中等
50-70: 较低
< 50 : 不可接受
```

## 📝 总结：技术选型参考

```
低延迟直播 → WebRTC / LLS
传统直播 → RTMP/HLS + CDN
短视频 → H.265 + 自适应 HLS
4K HDR → H.265 / AV1
电影存档 → ProRes / FFV1 / 无损
Web 流 → VP9/AV1 (HTML5)
视频会议 → WebRTC + Opus
监控录像 → H.265 + HLS
电影分发布 → 树莓 Pi + DASH
```
