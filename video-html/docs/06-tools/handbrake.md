---
title: HandBrake 转码工具
date: 2026-08-15  # date-auto-injected
---

# HandBrake 转码工具

<span class="kg-badge kg-badge-tools">工具</span>
<span class="kg-badge kg-badge-cases">日常</span>

**HandBrake** = 开源**视频转码工具**，主打易用 GUI，也提供 CLI。

## 📊 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 2003 |
| 语言 | C / GTK |
| 许可 | BSD |
| 平台 | Win/Mac/Linux |
| 默认编码 | H.264 / H.265 / VP9 / AV1 |

## 🛠️ 安装

```bash
# macOS
brew install handbrake

# Linux (Ubuntu)
sudo apt install handbrake-cli handbrake-gtk

# CLI only
sudo apt install handbrake-cli
```

## 🎯 CLI 用法

```bash
# 基本转码
HandBrakeCLI -i input.mp4 -o output.mp4

# 指定预设
HandBrakeCLI -i input.mp4 -o output.mp4 --preset "Fast 1080p30"

# H.265 编码
HandBrakeCLI -i input.mp4 -o output.mp4 -e x265 -q 28

# AV1 编码
HandBrakeCLI -i input.mp4 -o output.mp4 -e av1 -q 35

# 指定分辨率
HandBrakeCLI -i input.mp4 -o output.mp4 -w 1280 -l 720

# 指定码率
HandBrakeCLI -i input.mp4 -o output.mp4 -b 2000

# 裁剪
HandBrakeCLI -i input.mp4 -o output.mp4 --crop 0:100:0:100
```

## 📐 常用参数

| 参数 | 含义 |
| --- | --- |
| `-i` | 输入文件 |
| `-o` | 输出文件 |
| `-e` | 编码器（x264/x265/vp9/av1） |
| `-q` | 质量（CRF，0-51） |
| `-b` | 平均码率 |
| `--vb` | 视频码率 |
| `--ab` | 音频码率 |
| `-w` `-l` | 宽度 / 高度 |
| `--crop` | 裁剪 |
| `--preset` | 预设 |
| `--audio-lang-list` | 音频语言 |
| `--subtitle-lang-list` | 字幕语言 |

## 📊 内置预设

| 类别 | 预设 |
| --- | --- |
| **General** | Very Fast 1080p30 / Fast 1080p30 / HQ 1080p30 Surround |
| **Web** | Vimeo YouTube HQ / Gmail |
| **Apple** | iPhone iPad / Apple TV |
| **Matroska** | MKV 1080p30 / MKV 4K HEVC |
| **Mobile** | Android / iPod |

```bash
# 列出所有预设
HandBrakeCLI --preset-list

# 应用预设
HandBrakeCLI -i input.mp4 -o output.mp4 --preset "Fast 1080p30"
```

## 🎬 高级特性

### 滤镜

```bash
# 去隔行
HandBrakeCLI -i input.mp4 -o output.mp4 --deinterlace

# 去噪
HandBrakeCLI -i input.mp4 -o output.mp4 --denoise="hqdn3d:4:3:6:4.5"

# 锐化
HandBrakeCLI -i input.mp4 -o output.mp4 --unsharp="5:5:1.0"

# 缩放算法
HandBrakeCLI -i input.mp4 -o output.mp4 --vfilter="scale=lanczos"
```

### 字幕

```bash
# 烧入字幕
HandBrakeCLI -i input.mp4 -o output.mp4 --subtitle "1" --subtitle-burn

# 选择字幕轨
HandBrakeCLI -i input.mp4 -o output.mp4 --subtitle-lang-list eng,chi
```

### 音轨

```bash
# 选择音轨
HandBrakeCLI -i input.mp4 -o output.mp4 --audio-lang-list eng

# 多音轨输出
HandBrakeCLI -i input.mp4 -o output.mp4 --audio 1,2
```

## 🛠️ 批量转码

```bash
# 单文件
for f in *.mp4; do
  HandBrakeCLI -i "$f" -o "converted/${f%.mp4}_h265.mp4" -e x265 -q 28
done

# 多线程并行
ls *.mp4 | xargs -P 4 -I {} \
  HandBrakeCLI -i {} -o converted/{} -e x265 -q 28
```

## 📊 GUI 使用

```
HandBrake GUI:
1. 打开文件 / 文件夹 / 视频源
2. 选择预设（Summary）
3. 修改参数（Picture / Video / Audio / Subtitle）
4. 选输出位置
5. Start Encode
```

## 📐 HandBrake vs FFmpeg

| 特性 | HandBrake | FFmpeg |
| --- | --- | --- |
| 上手 | 简单（GUI） | 难（命令行） |
| 灵活 | 中 | **极高** |
| 预设 | 丰富 | 无 |
| 自动化 | CLI | **最佳** |
| 性能 | 优秀 | 优秀 |
| 功能 | 转码为主 | 全能 |

## 📊 性能调优

```bash
# 速度优先
HandBrakeCLI -i in.mp4 -o out.mp4 --encoder-preset ultrafast

# 压缩率优先
HandBrakeCLI -i in.mp4 -o out.mp4 --encoder-preset veryslow

# 多线程
HandBrakeCLI -i in.mp4 -o out.mp4 -e x265 --encoder-preset slow -q 28
# (HandBrake 默认使用所有 CPU 核心)
```

## 📐 常见场景配置

### 高质量蓝光备份

```bash
HandBrakeCLI -i movie.mkv -o movie.mp4 \
  -e x265 -q 22 \
  --encoder-preset slow \
  --audio 1,1 -E av_aac -B 192k \
  --subtitle 1 --subtitle-burned=none
```

### 移动端适配

```bash
HandBrakeCLI -i movie.mp4 -o mobile.mp4 \
  --preset "Fast 720p30" \
  -e x264 -q 23
```

### Web 上传

```bash
HandBrakeCLI -i movie.mp4 -o web.mp4 \
  --preset "Vimeo YouTube HQ" \
  -e x264 -q 22
```

### 压缩存储

```bash
HandBrakeCLI -i movie.mp4 -o compressed.mp4 \
  -e x265 -q 30 \
  --encoder-preset medium \
  -w 1280 -l 720
```

## 📌 面试考点

1. HandBrake vs FFmpeg？
   - HandBrake 简单易用；FFmpeg 更灵活
2. HandBrake 默认编码？
   - H.264（兼容性好）
3. CRF 和平均码率区别？
   - CRF 质量优先；平均码率固定大小
4. preset 怎么选？
   - 速度 → ultrafast；压缩 → veryslow

## 🔗 下一步

- [FFmpeg](/06-tools/ffmpeg)
- [MediaInfo](/06-tools/mediainfo)
- [硬件加速](/08-perf/nvenc-qsv)