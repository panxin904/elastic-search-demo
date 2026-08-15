---
title: 实时流性能
---

# 实时流性能优化

<span class="kg-badge kg-badge-perf">性能</span>
<span class="kg-badge kg-badge-protocol">实时</span>
<span class="kg-badge kg-badge-tools">FFmpeg</span>

实时视频流（直播、视频会议、监控）对 **端到端延迟**、**稳定性**、**画质** 要求严苛。

## ⏱️ 延迟构成

```
┌────────────┬─────────────┬─────────────┐
│ 采集端     │   网络       │  播放端      │
├────────────┼─────────────┼─────────────┤
│ 采集编码   │ 上行传输     │ 接收缓冲     │
│ 60-500ms   │ 50-300ms    │ 100-1000ms  │
│ + 摄像头   │ + 推流协议   │ + 解码渲染  │
└────────────┴─────────────┴─────────────┘
         总延迟：200ms ~ 数秒
```

### 延迟分布参考

| 阶段 | 监控直播 | 视频会议 | 超低延迟直播 |
| --- | --- | --- | --- |
| 采集+编码 | 200ms | 50ms | 30ms |
| 网络传输 | 200-500ms | 80-200ms | 50-100ms |
| 接收解码 | 500-2000ms | 100-200ms | 30-80ms |
| **总延迟** | **1-3s** | **300-500ms** | **100-300ms** |

## 🎯 关键指标

| 指标 | 含义 | 目标 |
| --- | --- | --- |
| **端到端延迟** | 采集→播放总时长 | < 1s (直播) < 400ms (会议) |
| **首屏时间** | 拉到第一帧 | < 1s |
| **卡顿率** | 卡顿时长占比 | < 1% |
| **FPS** | 实际帧率 | = 目标帧率 |
| **码率波动** | 码率抖动 | < 10% |

## 🔧 FFmpeg 实时编码参数

### 低延迟编码

```bash
ffmpeg -re -i input.mp4 \
  -c:v libx264 \
  -preset ultrafast \
  -tune zerolatency \
  -g 60 \
  -keyint_min 60 \
  -bf 0 \           # 禁用 B 帧
  -refs 1 \         # 减少参考帧
  -rc cbr \         # 固定码率
  -b:v 4000k \
  -f flv rtmp://...
```

### x264 zerolatency 调优

| 参数 | 默认 | zerolatency |
| --- | --- | --- |
| `preset` | medium | ultrafast |
| `tune` | 无 | zerolatency |
| `bf` | 16 | 0 |
| `refs` | 3 | 1 |
| `b-adapt` | 1 | 0 |
| `bframes` | - | 0 |
| `slice-max-size` | - | 100 |
| `sync-lookahead` | -1 | 0 |
| `rc-lookahead` | 40 | 0 |
| `scenecut` | 40 | 0 |

### x265 zerolatency

```bash
ffmpeg -i input.mp4 \
  -c:v libx265 \
  -x265-params "keyint=60:min-keyint=60:bframes=0:rc-lookahead=0:scenecut=0:ref=1" \
  -preset ultrafast \
  output.mp4
```

## 🚀 硬件加速推流

### NVENC 实时推流

```bash
ffmpeg -hwaccel cuda \
  -i input.mp4 \
  -c:v h264_nvenc \
  -preset ll \           # low latency
  -rc cbr \
  -b:v 4000k \
  -bf 0 \
  -f flv rtmp://...
```

### NVENC preset

| preset | 速度 | 质量 | 适合场景 |
| --- | --- | --- | --- |
| `ll` | 最快 | 中 | 实时直播 |
| `hp` | 快 | 中高 | 直播/会议 |
| `mq` | 中 | 高 | 录播 |
| `hq` | 慢 | 很高 | 离线编码 |

## 📡 协议延迟对比

| 协议 | 延迟 | 适用场景 |
| --- | --- | --- |
| **WebRTC** | 100-300ms | 视频会议、互动直播 |
| **RTMP** | 1-3s | 传统直播 |
| **HTTP-FLV** | 1-3s | 直播 |
| **HLS** | 5-30s | 点播、大规模直播 |
| **LL-HLS** | 1-3s | 低延迟直播 |
| **DASH** | 5-20s | 点播、自适应 |
| **SRT** | 100-500ms | 跨区域推流 |
| **RTSP** | 200-500ms | 监控 |

## 🛠️ GStreamer 实时流水线

```bash
# 摄像头采集 + H.264 编码 + RTMP 推流
gst-launch-1.0 \
  v4l2src device=/dev/video0 ! \
  video/x-raw,width=1280,height=720,framerate=30/1 ! \
  videoconvert ! \
  video/x-raw,format=NV12 ! \
  nvh264enc preset=low-latency-hq bitrate=4000 ! \
  h264parse ! \
  flvmux streamable=true ! \
  rtmpsink location="rtmp://server/live/key"
```

## 📊 缓冲区优化

### FFmpeg 推流参数

| 参数 | 作用 |
| --- | --- |
| `-rtbufsize` | 实时缓冲区大小 |
| `-flush_packets 1` | 立即刷新 packet |
| `-max_delay` | 最大 mux 延迟 |

```bash
ffmpeg -re \
  -rtbufsize 50M \      # 50MB 实时缓冲
  -flush_packets 1 \    # 立即发送
  -i input.mp4 \
  -c:v copy -c:a aac \
  -f flv rtmp://...
```

### 播放端缓冲区

| 场景 | 缓冲 |
| --- | --- |
| 直播 | 0.5-1s |
| 视频会议 | 100-200ms |
| 点播 | 3-10s |

## 🎬 降低 GOP 提升随机访问

```bash
# 短 GOP（直播）
ffmpeg -i input.mp4 -g 60 -keyint_min 60 output.mp4

# 极短 GOP（互动直播）
ffmpeg -i input.mp4 -g 30 -keyint_min 30 output.mp4

# 接近全 I 帧（超低延迟）
ffmpeg -i input.mp4 -g 1 output.mp4   # 每帧都是 I 帧
```

## 🔄 自适应码率 ABR

### 直播 ABR

```bash
# 多分辨率推流
for res in "640x360 800k" "1280x720 2500k" "1920x1080 5000k"; do
  W=$(echo $res | cut -d' ' -f1 | cut -dx -f1)
  H=$(echo $res | cut -d' ' -f1 | cut -dx -f2)
  BR=$(echo $res | cut -d' ' -f2)
  ffmpeg -re -i input.mp4 \
    -vf scale=${W}:${H} \
    -b:v ${BR} \
    -f flv rtmp://server/live/${BR}/key &
done
```

### 编码参数自适应

根据网络状况调整：
- 带宽充足：高质量 + 高帧率
- 带宽不足：降低码率 + 跳帧
- 网络抖动：增大缓冲 + 重传

## 🖥️ 服务端转码性能

### 多 worker 架构

```
                         ┌─ worker 1 (1080p H.264)
  推流 → ingest → [分发] ┼─ worker 2 (720p H.264)
                         ├─ worker 3 (480p H.265)
                         └─ worker 4 (240p H.264)
```

### 任务调度

- **CPU 转码**：单机 8-16 路 1080p
- **GPU 转码**：单机 50-200 路 1080p (NVENC)
- **集群**：Kubernetes + 任务队列

## 🔬 监控与调优

### 关键监控指标

```bash
# 实时查看推流状态
ffmpeg -re -i input.mp4 -c:v copy -f flv rtmp://... \
  -progress pipe:1
```

输出：
```
frame=300
fps=30.01
bitrate=4000.5kbps
total_size=45000000
```

### 服务端监控

- CPU / GPU 使用率
- 内存 / 显存
- 丢帧率 / 卡顿率
- 推流码率稳定性
- 编码延迟

## 📚 实战案例

### 案例 1：游戏直播（1-3s 延迟）

```bash
ffmpeg -f x11grab -framerate 60 -video_size 1920x1080 -i :0.0 \
  -f alsa -i default \
  -c:v h264_nvenc -preset ll -rc cbr -b:v 6000k -maxrate 6000k \
  -g 120 -bf 2 \
  -c:a aac -b:a 128k \
  -f flv rtmp://server/live/key
```

### 案例 2：视频会议（< 400ms）

```bash
ffmpeg -f video4linux2 -framerate 30 -video_size 1280x720 -i /dev/video0 \
  -f alsa -ar 16000 -ac 1 -i default \
  -c:v libx264 -preset ultrafast -tune zerolatency \
  -bf 0 -refs 1 -g 60 \
  -c:a opus -b:a 64k \
  -f mpegts udp://peer:5000
```

### 案例 3：监控摄像头

```bash
ffmpeg -rtsp_transport tcp -i rtsp://camera/stream \
  -c:v copy -an \
  -f hls -hls_time 2 -hls_list_size 5 \
  -hls_flags delete_segments \
  /var/www/stream.m3u8
```

## 🎓 性能调优清单

### 编码端
- [x] 启用硬件加速（NVENC/QSV）
- [x] preset = ultrafast 或 low-latency
- [x] tune = zerolatency
- [x] 禁用 B 帧（bf=0）
- [x] 减少参考帧（refs=1）
- [x] 关闭 lookahead
- [x] 短 GOP（g=30~60）

### 网络端
- [x] 选择低延迟协议（WebRTC/SRT）
- [x] TCP 低延迟或 UDP
- [x] 边缘节点减少跳数
- [x] CDN 预热

### 播放端
- [x] 缩小播放缓冲
- [x] 启用快速解码
- [x] 跳帧策略
- [x] 预加载策略
