---
title: GPU 处理 CUDA
---

# GPU 处理 - CUDA

<span class="kg-badge kg-badge-perf">性能</span>
<span class="kg-badge kg-badge-tools">硬件</span>
<span class="kg-badge kg-badge-ai">AI</span>

利用 **GPU** 进行视频处理和 AI 推理，速度可达 CPU 的 10-100 倍。

## 📊 主流 GPU 加速方案

| 平台 | API | 厂商 |
| --- | --- | --- |
| **CUDA** | NVIDIA | NVIDIA 独占 |
| **OpenCL** | 跨平台 | Khronos |
| **Vulkan Compute** | 跨平台 | Khronos |
| **DirectML** | Windows | Microsoft |
| **ROCm** | AMD | AMD |
| **Metal** | macOS | Apple |
| **OpenGL Compute** | 跨平台 | Khronos |
| **TensorRT** | NVIDIA | NVIDIA AI 推理 |

## 🏗️ CUDA 简介

**Compute Unified Device Architecture**，NVIDIA 2007 推出。

```
CPU (主机)  ←────── PCIe / NVLink ──────→  GPU (设备)
                                           ├─ 上千核心
                                           ├─ 大显存
                                           └─ 高带宽
```

### CUDA 关键概念

| 概念 | 含义 |
| --- | --- |
| **Thread** | 线程（最小单位） |
| **Block** | 线程块（共享内存） |
| **Grid** | 网格（所有 block） |
| **Warp** | 32 线程（执行单位） |
| **SM** | Streaming Multiprocessor |
| **Kernel** | GPU 函数 |
| **Host/Device** | CPU/GPU |

## 📊 视频处理中的 GPU 应用

### 1. 视频编解码（硬件）

- NVENC/NVDEC（专用硬件）
- 比 CPU 快 10-50 倍

### 2. 视频处理（通用计算）

```python
# OpenCV CUDA
import cv2

# 上传到 GPU
gpu_img = cv2.cuda_GpuMat()
gpu_img.upload(cv2.imread('in.png'))

# GPU 处理
gpu_gray = cv2.cuda.cvtColor(gpu_img, cv2.COLOR_BGR2GRAY)
gpu_blur = cv2.cuda.GaussianBlur(gpu_gray, (15, 15), 0)

# 下载到 CPU
result = gpu_blur.download()
```

### 3. AI 推理

```python
import torch

# CUDA 张量
x = torch.randn(100, 100).cuda()

# 模型
model = MyModel().cuda()

# 推理
output = model(x.cuda())
```

## 📐 NVIDIA Video Codec SDK

NVIDIA 提供的硬件编解码 API。

```cpp
#include <cuda_runtime.h>
#include <nvEncodeAPI.h>

// 创建编码器
NVENCSTATUS enc_status = nvEncodeAPICreateInstance(&nv_enc);

// 初始化
nv_enc->NvEncInitializeEncoder(&initialize_params);

// 编码一帧
nv_enc->NvEncEncodeFrame(&encode_params);

// 取出码流
nv_enc->NvEncLockBitstream(&lock_params);
```

## 📐 NPP（NVIDIA Performance Primitives）

NVIDIA GPU 加速图像/视频库。

```cpp
#include <npp.h>

// 缩放
nppiResize_8u_C3R(src, src_pitch, dst, dst_pitch,
                   oSizeROI, eInterpolationMode);

// 色彩转换
nppiRGBToYUV_8u_C3R(...);

// 边缘
nppiFilterSobel_8u_C1R(...);
```

## 📐 FFmpeg CUDA / NVDEC

```bash
# CUDA 解码
ffmpeg -hwaccel cuda -i in.mp4 -c:v h264_nvenc out.mp4

# NVDEC 解码 + NVENC 编码（端到端 GPU）
ffmpeg -hwaccel cuda -hwaccel_output_format cuda \
  -i in.mp4 \
  -c:v h264_nvenc -preset p4 \
  out.mp4

# CUDA 缩放
ffmpeg -hwaccel cuda -i in.mp4 \
  -vf "scale_cuda=1280:720" \
  -c:v h264_nvenc out.mp4
```

### CUDA 滤镜

```bash
# CUDA 缩放
scale_cuda=1280:720

# CUDA 上采样
scale_cuda=3840:2160:interp_algo=lanczos

# CUDA 锐化
unsharp_cuda=5:5:1.0

# CUDA 去噪
nlmeans_cuda
```

## 📐 TensorRT（AI 推理加速）

NVIDIA 的深度学习推理引擎。

```python
import tensorrt as trt
import torch

# 1. 导出 ONNX
torch.onnx.export(model, dummy_input, "model.onnx")

# 2. TensorRT 构建
logger = trt.Logger(trt.Logger.WARNING)
builder = trt.Builder(logger)
network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
parser = trt.OnnxParser(network, logger)
parser.parse_from_file("model.onnx")

# 3. 优化
config = builder.create_builder_config()
config.set_flag(trt.BuilderFlag.FP16)  # 半精度

engine = builder.build_serialized_network(network, config)

# 4. 推理
# (略)
```

## 📊 PyTorch CUDA

```python
import torch

# 检查 CUDA
print(torch.cuda.is_available())
print(torch.cuda.get_device_name(0))
print(torch.cuda.get_device_properties(0))

# 模型迁到 GPU
model = MyModel().cuda()

# 张量迁到 GPU
x = torch.randn(10, 10).cuda()

# 异步传输
x = x.cuda(non_blocking=True)

# 多 GPU
model = torch.nn.DataParallel(model)

# 半精度
model = model.half()

# 清理
torch.cuda.empty_cache()
```

## 📐 视频 AI 推理示例

```python
import cv2
import torch
from ultralytics import YOLO

# 加载模型
model = YOLO('yolov8n.pt').cuda()

# 视频
cap = cv2.VideoCapture('in.mp4')
while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    # GPU 推理
    results = model(frame, device='cuda')

    # 绘制
    annotated = results[0].plot()
    cv2.imshow('output', annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'): break
```

## 📊 性能对比

| 操作 | CPU | GPU |
| --- | --- | --- |
| **H.264 软编** | 1x | - |
| **H.264 NVENC** | - | **20-50x** |
| **AI 推理 (ResNet)** | 1x | **20x** |
| **AI 推理 (YOLO)** | 1x | **10-30x** |
| **OpenCV 缩放** | 1x | 5-10x |
| **超分 (RTX 4090)** | - | 4K 30fps |

## ⚠️ 注意事项

| 注意 | 说明 |
| --- | --- |
| **数据传输** | CPU↔GPU PCIe 带宽限制 |
| **显存** | 大模型需要大显存 |
| **兼容性** | 不同 GPU 算力不同 |
| **驱动** | NVIDIA 驱动版本重要 |

## 📌 面试考点

1. CUDA 是什么？
   - NVIDIA GPU 编程模型
2. NVENC vs CUDA 编码？
   - NVENC 专用硬件；CUDA 通用
3. CPU → GPU 数据传输开销？
   - PCIe 4.0 ×16 = ~32 GB/s
4. 多 GPU 怎么用？
   - DataParallel / DistributedDataParallel

## 🔗 下一步

- [硬件加速 NVENC](/08-perf/nvenc-qsv)
- [多线程并行](/08-perf/threading)
- [AI 视频处理](/07-ai/super-res-ai)