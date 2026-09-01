---
title: FFmpeg 入门精通
date: 2026-08-15  # date-auto-injected
---

![FFmpeg 转码流水线](/ffmpeg-transcode-pipeline.svg)

# FFmpeg 入门精通

<span class="kg-badge kg-badge-tools">工具</span>
<span class="kg-badge kg-badge-protocol">流媒体</span>
<span class="kg-badge kg-badge-codecs">编解码</span>

**FFmpeg** = 跨平台**多媒体处理工具集**，视频/音频/字幕/流媒体的**瑞士军刀**。

## 📊 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 2000 |
| 语言 | C |
| 许可 | LGPL/GPL |
| 平台 | Linux/Mac/Windows |
| 组件 | ffmpeg / ffprobe / ffplay |

## 🏗️ FFmpeg 组件

| 工具 | 用途 |
| --- | --- |
| **ffmpeg** | 转换处理 |
| **ffprobe** | 查看媒体信息 |
| **ffplay** | 播放器（SDL） |
| **libavformat** | 容器/封装库 |
| **libavcodec** | 编解码库 |
| **libavutil** | 工具库 |
| **libswscale** | 缩放、色彩转换 |
| **libswresample** | 音频重采样 |
| **libavfilter** | 滤镜图框架 |

## 📐 基本命令格式

```bash
ffmpeg [全局选项] -i 输入 [选项] 输出

例:
ffmpeg -i input.mp4 -c:v libx264 -crf 23 output.mp4
```

### 常用全局选项

| 选项 | 含义 |
| --- | --- |
| `-i` | 输入文件 |
| `-y` | 覆盖输出 |
| `-n` | 不覆盖 |
| `-loglevel` | 日志级别 |
| `-hide_banner` | 隐藏横幅 |

## 📊 媒体信息查询

```bash
# 查看流信息
ffprobe input.mp4

# JSON 格式
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

# 仅视频流
ffprobe -select_streams v:0 -show_streams input.mp4

# 查看编码
ffprobe -show_entries stream=codec_name,codec_type,profile input.mp4
```

## 🎯 格式转换

```bash
# MP4 → MKV
ffmpeg -i in.mp4 -c copy out.mkv

# MKV → MP4（重编码）
ffmpeg -i in.mkv -c:v libx264 -c:a aac out.mp4

# 提取音频
ffmpeg -i in.mp4 -vn -c:a copy out.aac

# 提取视频（无音频）
ffmpeg -i in.mp4 -an -c:v copy out.h264
```

## 🎯 视频编码

```bash
# H.264
ffmpeg -i in.mp4 -c:v libx264 -crf 23 -preset medium out.mp4

# H.265
ffmpeg -i in.mp4 -c:v libx265 -crf 28 -preset medium -tag:v hvc1 out.mp4

# AV1（libsvtav1 快）
ffmpeg -i in.mp4 -c:v libsvtav1 -crf 32 -preset 8 out.mkv

# VP9
ffmpeg -i in.mp4 -c:v libvpx-vp9 -crf 31 -b:v 0 out.webm

# 硬件加速
ffmpeg -i in.mp4 -c:v h264_nvenc -preset p4 out.mp4
ffmpeg -i in.mp4 -c:v h264_qsv -preset fast out.mp4
```

## 📊 编码参数

### libx264 关键参数

```bash
-preset ultrafast|fast|medium|slow|veryslow   # 编码速度
-tune film|animation|grain|stillimage|fastdecode|zerolatency  # 场景调优
-crf 0~51        # 质量（0 无损，51 最差）
-b:v 5M          # 目标码率
-minrate 5M -maxrate 5M -bufsize 5M  # CBR
-profile:v baseline|main|high
-level 4.1
-x264-params "keyint=250:min-keyint=25:bframes=3:ref=3"
```

### libx265 关键参数

```bash
-preset ultrafast...placebo
-crf 0~51
-x265-params "keyint=250:bframes=4:ref=3:rd=4"
```

## 🎯 滤镜

```bash
# 缩放
ffmpeg -i in.mp4 -vf "scale=1280:720" out.mp4

# 缩放 + Lanczos
ffmpeg -i in.mp4 -vf "scale=1280:720:flags=lanczos" out.mp4

# 裁剪
ffmpeg -i in.mp4 -vf "crop=640:480:100:50" out.mp4

# 旋转
ffmpeg -i in.mp4 -vf "transpose=1" out.mp4  # 90° 顺时针

# 去隔行
ffmpeg -i in.mp4 -vf "yadif" out.mp4

# 去噪
ffmpeg -i in.mp4 -vf "hqdn3d=4:3:6:4.5" out.mp4

# 锐化
ffmpeg -i in.mp4 -vf "unsharp=5:5:1.0" out.mp4

# 调速
ffmpeg -i in.mp4 -vf "setpts=0.5*PTS" -af "atempo=2.0" fast.mp4

# 水印
ffmpeg -i in.mp4 -i logo.png -filter_complex "overlay=10:10" out.mp4

# 文字
ffmpeg -i in.mp4 -vf "drawtext=text='Hello':fontsize=24:fontcolor=white:x=10:y=10" out.mp4

# 拼接
ffmpeg -f concat -i list.txt -c copy out.mp4
```

## 📊 流媒体

```bash
# 推流 RTMP
ffmpeg -re -i in.mp4 -c:v libx264 -preset veryfast -c:a aac \
       -f flv rtmp://server/live/stream

# 拉流 RTMP → HLS
ffmpeg -i rtmp://server/live/stream \
       -c:v libx264 -c:a aac \
       -hls_time 4 -hls_list_size 6 \
       -hls_flags delete_segments \
       live.m3u8

# HLS 切片
ffmpeg -i in.mp4 \
       -c:v libx264 -c:a aac \
       -hls_time 6 -hls_list_size 0 \
       -hls_segment_filename "seg%03d.ts" \
       playlist.m3u8

# SRT 推流
ffmpeg -re -i in.mp4 -c:v libx264 -preset ultrafast \
       -f mpegts 'srt://server:9999?mode=caller&latency=120'

# RTSP 拉流
ffmpeg -rtsp_transport tcp -i rtsp://camera/stream -c copy out.mp4
```

## 🎯 音视频处理

```bash
# 静音
ffmpeg -i in.mp4 -an -c:v copy silent.mp4

# 替换音轨
ffmpeg -i video.mp4 -i audio.aac -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 out.mp4

# 双声道 → 单声道
ffmpeg -i in.mp4 -ac 1 out.mp4

# 音量
ffmpeg -i in.mp4 -af "volume=2.0" out.mp4

# 音频淡入淡出
ffmpeg -i in.mp4 -af "afade=t=in:st=0:d=3,afade=t=out:st=27:d=3" out.mp4

# 音视频对齐
ffmpeg -i in.mp4 -itsoffset 0.5 -i in.mp4 -map 0:v -map 1:a out.mp4
```

## 📊 截图 / 抽帧

```bash
# 单张截图
ffmpeg -i in.mp4 -ss 00:00:10 -vframes 1 out.jpg

# 1 帧/秒
ffmpeg -i in.mp4 -vf "fps=1" frames_%04d.jpg

# 关键帧
ffmpeg -i in.mp4 -vf "select=eq(pict_type\,I)" -vsync vfr iframe_%04d.png

# 生成缩略图雪碧图
ffmpeg -i in.mp4 -vf "fps=1,scale=160:90,tile=10x10" thumbnail.png
```

## 📐 滤镜图（Filtergraph）

```bash
# 多个滤镜链
ffmpeg -i in.mp4 -vf "scale=1280:720,unsharp=5:5:1.0,hqdn3d=4:3:6:4.5" out.mp4

# 复杂滤镜图
ffmpeg -i in.mp4 -i logo.png \
       -filter_complex "[0:v]scale=1280:720[s];[1:v]scale=100:100[l];[s][l]overlay=10:10" \
       out.mp4

# split 分流
ffmpeg -i in.mp4 -filter_complex "split=2[out1][out2]" \
       -map "[out1]" out1.mp4 -map "[out2]" out2.mp4
```

## 🛠️ 性能优化

```bash
# 多线程编码
-threads 8

# x265 多线程
-x265-params "pools=8"

# 实时编码（zerolatency）
-tune zerolatency

# 切片并行
-segment_time 60
-f segment out_%03d.mp4
```

## 📊 调试

```bash
# 查看可用编码器
ffmpeg -encoders | grep 264

# 查看可用解码器
ffmpeg -decoders | grep 264

# 查看可用格式
ffmpeg -formats

# 查看可用滤镜
ffmpeg -filters

# 查看协议
ffmpeg -protocols

# 详细日志
ffmpeg -v verbose -i in.mp4 ...

# 调试日志
ffmpeg -v debug -i in.mp4 ...
```

## 📐 常见问题

| 问题 | 解决 |
| --- | --- |
| `Unknown encoder` | 编译时未启用 |
| `Permission denied` | 加 `-y` 或改权限 |
| `Invalid data found` | 文件损坏 |
| `moov atom not found` | `-movflags +faststart` |
| `Conversion failed` | 查看日志找原因 |

## 📌 面试考点

1. ffmpeg 关键组件？
   - ffmpeg / ffprobe / ffplay + libavformat/codec/filter
2. crf 和 bitrate 区别？
   - CRF 质量优先；bitrate 码率优先
3. preset 含义？
   - 编码速度/压缩率 tradeoff
4. 实时直播配置？
   - `-re` + zerolatency + veryfast preset

## 🔗 下一步

- [GStreamer](/06-tools/gstreamer)
- [OpenCV](/06-tools/opencv)
- [硬件加速](/08-perf/nvenc-qsv)