---
title: 多线程并行处理
date: 2026-08-15  # date-auto-injected
---

# 多线程并行处理

<span class="kg-badge kg-badge-perf">性能</span>
<span class="kg-badge kg-badge-tools">FFmpeg</span>
<span class="kg-badge kg-badge-codec">编解码</span>

视频编解码是 **计算密集型** 任务，合理利用多核 CPU 可大幅提升性能。

## 📊 并行层级

```
┌──────────────────────────────────────────┐
│ 任务级并行 (任务级 pipeline)              │
│   ├─ 解码 task ─┐                        │
│   ├─ 处理 task ─┼→ 不同线程              │
│   └─ 编码 task ─┘                        │
├──────────────────────────────────────────┤
│ 帧级并行 (frame-level parallelism)        │
│   ├─ 帧 A → thread 1                     │
│   ├─ 帧 B → thread 2                     │
│   └─ 帧 C → thread 3                     │
├──────────────────────────────────────────┤
│ Slice 级并行 (slice-level)                │
│   一帧多个 slice → 不同线程             │
├──────────────────────────────────────────┤
│ Tile / CTU 级并行                          │
│   帧内 tile 分块并行                      │
└──────────────────────────────────────────┘
```

## 🎬 FFmpeg 多线程参数

### 全局参数

| 参数 | 含义 | 说明 |
| --- | --- | --- |
| `-threads n` | 线程数 | 0=自动 |
| `-filter_threads n` | filter 线程数 | |
| `-filter_complex_threads n` | complex filter 线程数 | |
| `-loop` | 循环输入 | |

```bash
# 设置 8 线程编码
ffmpeg -i input.mp4 -threads 8 -c:v libx264 output.mp4

# 自动（推荐）
ffmpeg -i input.mp4 -threads 0 -c:v libx264 output.mp4
```

## 🎥 x264 多线程

### 三种并行方式

| 方式 | 命令参数 | 说明 |
| --- | --- | --- |
| **Slice** | `--slice-max-size` | 多 slice，零延迟，但损失压缩率 |
| **Frame** | `x264 --threads N --lookahead-threads M` | 默认，帧级并行 |
| **Pools** | `--pools` | 多 slice 帧级 |

```bash
# x264 帧级多线程
ffmpeg -i input.mp4 \
  -c:v libx264 \
  -x264-params "threads=8:lookahead-threads=4:sync-lookahead=0" \
  -preset fast \
  output.mp4
```

### x264 关键线程参数

| 参数 | 作用 | 推荐值 |
| --- | --- | --- |
| `threads` | 总线程数 | 物理核数 |
| `lookahead-threads` | 预分析线程 | 1-4 |
| `sync-lookahead` | lookahead 缓冲 | 0=自动 |
| `pools` | slice 池 | - |
| `slice-max-size` | 每 slice MB 数 | 越大压缩率越高 |

## 🎞️ x265 线程模型

```
Frame-level (并行 frame)
  │
  ├─ Wavefront (行级流水线 CTU)
  │
  └─ Frame Pool (帧池)
```

```bash
# x265 多线程
ffmpeg -i input.mp4 \
  -c:v libx265 \
  -x265-params "pools=8:frame-threads=4:wpp=1:pmode=1:pme=1" \
  -preset medium \
  output.mp4
```

### x265 参数

| 参数 | 含义 |
| --- | --- |
| `pools` | slice 线程池 |
| `frame-threads` | 帧级并行线程 |
| `wpp` | Wavefront Parallel Processing |
| `pmode` | Parallel Merge Mode |
| `pme` | Parallel Motion Estimation |

## 🎞️ SVT-AV1 线程

```bash
# SVT-AV1 线程数控制
ffmpeg -i input.mp4 \
  -c:v libsvtav1 \
  -svtav1-params "preset=6:lp=2:threads=8" \
  output.mp4
```

## 🛠️ 解码并行

### FFmpeg 解码

```bash
# 多线程解码
ffmpeg -threads 8 -i input.mp4 -f null -
```

### 软件解码（多线程）

| 解码器 | 线程支持 |
| --- | --- |
| libavcodec | 自动多线程 |
| dav1d | 多线程默认开启 |
| libaom-av1 | 线程数可配 |
| ffvp9 | 多线程 |

### 硬件解码器

| 解码器 | 多线程方式 |
| --- | --- |
| NVDEC | 硬件多 session |
| QSV | 硬件多 session |
| VideoToolbox | 系统调度 |

## 🐍 Python 多进程/线程

### threading 模块

```python
import threading
from concurrent.futures import ThreadPoolExecutor

def process_frame(idx):
    # 处理一帧
    pass

# 4 线程处理
with ThreadPoolExecutor(max_workers=4) as ex:
    ex.map(process_frame, range(1000))
```

### multiprocessing（CPU 密集型）

```python
from multiprocessing import Pool

def process_chunk(frames):
    # 适合 CPU 密集型
    pass

with Pool(8) as p:
    p.map(process_chunk, frame_chunks)
```

### GIL 释放技巧

```python
import cv2
import numpy as np

# 视频处理中可以释放 GIL 的库:
# - numpy 大数组操作
# - cv2 大量函数
# - ffmpeg-python 调用
```

## 🖥️ OpenCV 多线程

```cpp
cv::setNumThreads(8);   // 设置 OpenCV 线程
cv::Mat frame = cv::imread("input.jpg");
cv::cvtColor(frame, frame, cv::COLOR_BGR2RGB);
// OpenCV 自动利用多核
```

## 🖥️ FFmpeg filter 多线程

```bash
# filter 单独线程数
ffmpeg -i input.mp4 \
  -filter_threads 8 \
  -filter_complex "[0:v]scale=1920:1080[v]" \
  -map "[v]" output.mp4
```

## 🎯 多 GPU 调度

### FFmpeg 多 GPU

```bash
# GPU 0 转码任务 1
ffmpeg -hwaccel cuda -i in1.mp4 -c:v h264_nvenc out1.mp4 &

# GPU 1 转码任务 2
CUDA_VISIBLE_DEVICES=1 ffmpeg -hwaccel cuda -i in2.mp4 -c:v h264_nvenc out2.mp4 &

wait
```

### 任务调度器

```python
import os
# 用 CUDA_VISIBLE_DEVICES 控制每进程可见的 GPU
def pick_gpu(task_id):
    return task_id % num_gpus
```

## ⚠️ 线程数设置原则

| 场景 | 推荐线程 |
| --- | --- |
| 单任务编码 | = 物理核数 |
| 多任务编码 | 物理核数 / 任务数 |
| 解码 | = 物理核数 |
| 实时流 | 物理核数 - 1 |
| AI 推理 | 1-4（CPU 推理） |

## 🔬 性能数据参考

### x264 1080p 编码

| 线程 | 速度 (fps) | 倍数 |
| --- | --- | --- |
| 1 | 30 | 1x |
| 2 | 58 | 1.9x |
| 4 | 110 | 3.7x |
| 8 | 200 | 6.7x |
| 16 | 350 | 11.7x |

### x265 4K 编码

| 线程 | 速度 (fps) |
| --- | --- |
| 1 | 2 |
| 4 | 7.5 |
| 8 | 14 |
| 16 | 26 |

## 🧰 排查命令

```bash
# CPU 信息
lscpu
nproc

# 查看 FFmpeg 线程状态
ffmpeg -threads 1 -benchmark -i input.mp4 -f null -

# 性能分析（Linux）
perf record -g ffmpeg -i input.mp4 ...
perf report
```

## 📚 最佳实践

1. **避免过度并行**：H.264 帧内预测存在波前依赖，过多线程收益递减
2. **确认内存**：每线程消耗 100-300MB 内存
3. **NUMA 优化**：双 CPU 服务器注意跨 NUMA 内存
4. **亲和性**：`taskset` 命令绑定 CPU 核心
5. **实时任务**：单线程 + 硬件加速比多线程软编稳定

```bash
# CPU 亲和性
taskset -c 0-7 ffmpeg -i input.mp4 ...   # 绑定前 8 核
```
