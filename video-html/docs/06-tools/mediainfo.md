---
title: MediaInfo 元数据
date: 2026-08-15  # date-auto-injected
---

# MediaInfo 元数据工具

<span class="kg-badge kg-badge-tools">工具</span>
<span class="kg-badge kg-badge-basics">基础</span>

**MediaInfo** = 查看媒体文件**详细元数据**的工具，支持几乎所有音视频格式。

## 📊 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 2002 |
| 语言 | C++ |
| 许可 | BSD |
| 平台 | Win/Mac/Linux + GUI + CLI |

## 🛠️ 命令行

```bash
# 默认输出
mediainfo input.mp4

# 详细输出
mediainfo -f input.mp4

# XML 输出
mediainfo -f --output=XML input.mp4 > info.xml

# JSON 输出
mediainfo --output=JSON input.mp4

# 仅视频信息
mediainfo --Inform="Video;%Format%,%Width%x%Height%,%BitRate%" input.mp4
```

## 📊 输出示例

```
General
Complete name                            : input.mp4
Format                                   : MPEG-4
Format profile                           : Base Media
Codec ID                                 : isom (isom/iso2/avc1/mp41)
File size                                : 145.6 MiB
Duration                                 : 1 h 32 min
Overall bit rate mode                    : Variable
Overall bit rate                         : 220 kb/s
Writing application                      : Lavf60.3.100

Video
ID                                       : 1
Format                                   : AVC
Format/Info                              : Advanced Video Codec
Format profile                           : High@L4.1
Format settings                          : CABAC / 4 Ref Frames
Codec ID                                 : avc1
Duration                                 : 1 h 32 min
Bit rate mode                            : Variable
Bit rate                                 : 2 000 kb/s
Maximum bit rate                         : 5 000 kb/s
Width                                    : 1 920 pixels
Height                                   : 1 080 pixels
Display aspect ratio                     : 16:9
Frame rate mode                          : Constant
Frame rate                               : 24.000 FPS
Color space                              : YUV
Chroma subsampling                       : 4:2:0
Bit depth                                : 8 bits
Scan type                                : Progressive

Audio
ID                                       : 2
Format                                   : AAC LC
Format/Info                              : Advanced Audio Codec Low Complexity
Codec ID                                 : mp4a-40-2
Duration                                 : 1 h 32 min
Bit rate mode                            : Variable
Bit rate                                 : 192 kb/s
Channel(s)                               : 2 channels
Channel layout                           : L R
Sampling rate                            : 48.0 kHz
```

## 📐 关键信息

| 字段 | 含义 |
| --- | --- |
| **Complete name** | 文件路径 |
| **Format** | 容器格式 |
| **File size** | 文件大小 |
| **Duration** | 时长 |
| **Overall bit rate** | 总码率 |
| **Codec ID** | 编码 ID |
| **Width × Height** | 分辨率 |
| **Frame rate** | 帧率 |
| **Chroma subsampling** | 色度采样 |
| **Bit depth** | 位深 |
| **Channel(s)** | 声道数 |
| **Sampling rate** | 采样率 |

## 🛠️ GUI 版

```
MediaInfo GUI:
  - 文件 → 打开
  - Tree 视图 / Text 视图
  - Sheet 视图（导出 HTML）
  - 可比较多个文件
```

## 📊 批量脚本

```bash
# 批量输出文件名 + 时长
for f in *.mp4; do
  info=$(mediainfo --Inform="General;%FileName%,%Duration/String1%" "$f")
  echo "$info"
done

# 找出所有 4K 文件
for f in *.mp4; do
  resolution=$(mediainfo --Inform="Video;%Width%x%Height%" "$f")
  if [[ "$resolution" == "3840x2160" ]]; then
    echo "$f is 4K"
  fi
done
```

## 🛠️ Python 集成

```python
import subprocess
import json

def get_media_info(filepath):
    result = subprocess.run(
        ['mediainfo', '--output=JSON', filepath],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

info = get_media_info('input.mp4')
print(info['media']['track'][0]['Duration'])
```

## 📐 FFmpeg 替代

FFmpeg 的 ffprobe 也能查元数据，但 MediaInfo 显示更详细。

```bash
# ffprobe
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4
```

## 📊 应用场景

| 场景 | 用途 |
| --- | --- |
| **质量检测** | 验证编码参数 |
| **版权审查** | 查看元数据 |
| **批量处理** | 自动化脚本 |
| **内容分析** | 提取关键信息 |
| **技术调研** | 对比不同编码 |

## 📌 面试考点

1. MediaInfo 与 ffprobe？
   - MediaInfo 显示更详细；ffprobe 是 FFmpeg 自带
2. 关键元数据？
   - 编码、分辨率、帧率、码率、时长、声道
3. 批量提取信息？
   - shell for 循环 + mediainfo
4. JSON 输出？
   - `--output=JSON`

## 🔗 下一步

- [FFmpeg](/06-tools/ffmpeg)
- [HandBrake](/06-tools/handbrake)
- [音频编码](/03-codecs/audio-codec)