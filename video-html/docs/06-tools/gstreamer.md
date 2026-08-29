---
title: GStreamer 框架
date: 2026-08-15  # date-auto-injected
---

# GStreamer 多媒体框架

<span class="kg-badge kg-badge-tools">工具</span>
<span class="kg-badge kg-badge-protocol">流媒体</span>
<span class="kg-badge kg-badge-protocol">Linux</span>

**GStreamer** = Linux 平台强大的**多媒体框架**，基于**管道（pipeline）**构建流处理。

## 📊 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 2001 |
| 语言 | C |
| 许可 | LGPL |
| 平台 | Linux/Mac/Windows/Android/iOS |
| 主页 | gstreamer.freedesktop.org |

## 🏗️ 架构：管道（Pipeline）

```
Pipeline = Element + Pad + Bin + Bus

┌─────────┐    ┌──────────┐    ┌──────────┐
│  Source │ →  │  Filter  │ →  │   Sink   │
│ (filesrc)│   │ (decode) │   │ (autovideosink) │
└─────────┘    └──────────┘    └──────────┘
```

## 📐 Element 类型

| 类型 | 作用 |
| --- | --- |
| **Source** | 数据源（filesrc / v4l2src / rtspsrc） |
| **Sink** | 数据输出（autovideosink / filesink / udpsink） |
| **Filter** | 处理（decode / encode / scale / convert） |
| **Demuxer** | 解封装（qtdemux / mpegtsdemux） |
| **Muxer** | 封装（qtmux / mpegtsmux） |
| **Decoder** | 解码（avdec_h264 / vpxdec） |
| **Encoder** | 编码（x264enc / x265enc / vpxenc） |

## 📊 Pad 与 Bin

| 概念 | 含义 |
| --- | --- |
| **Pad** | Element 之间的连接点 |
| **Src Pad** | 输出 |
| **Sink Pad** | 输入 |
| **Bin** | 容器，组合多个 Element |
| **Pipeline** | 顶层 Bin |

## 🛠️ gst-launch-1.0 命令

```bash
# 基本格式
gst-launch-1.0 [element1] ! [element2] ! [element3] ! [sink]

# 播放本地文件
gst-launch-1.0 filesrc location=in.mp4 ! decodebin ! autovideosink

# 转码 MP4 → MKV
gst-launch-1.0 filesrc location=in.mp4 \
    ! qtdemux ! h264parse ! x264enc ! matroskamux \
    ! filesink location=out.mkv

# 拉 RTSP 流
gst-launch-1.0 rtspsrc location=rtsp://camera/stream latency=200 \
    ! rtph264depay ! h264parse ! decodebin ! autovideosink

# HLS 切片
gst-launch-1.0 filesrc location=in.mp4 \
    ! qtdemux ! h264parse \
    ! splitmuxsink location=seg%05d.ts max-size-time=4000000000 \
    ! playlist-inject location=playlist.m3u8
```

## 📐 视频处理示例

```bash
# 缩放 + 编码
gst-launch-1.0 filesrc location=in.mp4 \
    ! decodebin \
    ! videoscale ! video/x-raw,width=1280,height=720 \
    ! videoconvert \
    ! x264enc tune=zerolatency bitrate=2000 \
    ! h264parse \
    ! mp4mux \
    ! filesink location=out.mp4

# 叠加水印
gst-launch-1.0 filesrc location=in.mp4 \
    ! decodebin \
    ! videoconvert \
    ! textoverlay text="Hello" valignment=bottom \
    ! videoconvert \
    ! autovideosink

# 录像 + 实时预览
gst-launch-1.0 v4l2src ! decodebin \
    ! tee name=t \
    t. ! autovideosink \
    t. ! x264enc ! h264parse ! mp4mux ! filesink location=recording.mp4
```

## 🛠️ 编程 API（C）

```c
#include <gst/gst.h>

int main(int argc, char *argv[]) {
    gst_init(&argc, &argv);

    // 创建 pipeline
    GstElement *pipeline = gst_parse_launch(
        "filesrc location=in.mp4 ! decodebin ! autovideosink",
        NULL);

    // 设置播放状态
    gst_element_set_state(pipeline, GST_STATE_PLAYING);

    // 等待结束
    GstBus *bus = gst_element_get_bus(pipeline);
    gst_bus_timed_pop_filtered(bus, GST_CLOCK_TIME_NONE,
        GST_MESSAGE_ERROR | GST_MESSAGE_EOS);

    // 清理
    gst_object_unref(bus);
    gst_element_set_state(pipeline, GST_STATE_NULL);
    gst_object_unref(pipeline);

    return 0;
}
```

## 🛠️ Python API

```python
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

Gst.init(None)

pipeline = Gst.parse_launch("""
    filesrc location=in.mp4
    ! decodebin
    ! videoconvert
    ! autovideosink
""")

pipeline.set_state(Gst.State.PLAYING)

# 主循环
bus = pipeline.get_bus()
msg = bus.timed_pop_filtered(
    Gst.CLOCK_TIME_NONE,
    Gst.MessageType.ERROR | Gst.MessageType.EOS
)

pipeline.set_state(Gst.State.NULL)
```

## 📊 GStreamer vs FFmpeg

| 特性 | GStreamer | FFmpeg |
| --- | --- | --- |
| 类型 | 框架 | 工具集 |
| 编程 | 灵活、易扩展 | 命令行为主 |
| Pipeline | 灵活构建 | 滤镜图（受限） |
| 性能 | 优秀 | 优秀 |
| 协议 | 完整 | 完整 |
| 应用 | 桌面、嵌入式 | 转码、流媒体 |
| 代表 | Linux 桌面、Total | OBS、FFmpeg |

## 📐 GStreamer 常用插件

| 插件 | 用途 |
| --- | --- |
| `gst-plugins-base` | 基础 |
| `gst-plugins-good` | 常用 |
| `gst-plugins-bad` | 实验 |
| `gst-plugins-ugly` | 专利 |
| `gst-libav` | FFmpeg 集成 |
| `gst-rtsp-server` | RTSP 服务 |
| `gst-webrtc` | WebRTC |

## 🛠️ WebRTC 推流

```bash
# WHIP 推流
gst-launch-1.0 filesrc location=in.mp4 \
    ! decodebin ! videoconvert \
    ! x264enc tune=zerolatency \
    ! whipclientsink uri=https://server/whip/stream
```

## 📊 调试工具

```bash
# 详细日志
export GST_DEBUG=3
gst-launch-1.0 ...

# 特定模块日志
export GST_DEBUG=videotestsrc:5

# 查看 pipeline 图
export GST_DEBUG_DUMP_DOT_DIR=/tmp/dots
gst-launch-1.0 ...
dot -Tpng /tmp/dots/*.dot -o pipeline.png
```

## 📌 面试考点

1. GStreamer vs FFmpeg？
   - 框架 vs 工具，编程 vs 命令
2. Pipeline 是什么？
   - Element + Pad 组成的数据流图
3. tee 元素作用？
   - 分流到多个下游
4. 编程模型？
   - C / Python / Rust API

## 🔗 下一步

- [FFmpeg](/06-tools/ffmpeg)
- [OpenCV](/06-tools/opencv)
- [WebRTC](/05-protocol/webrtc)