---
title: OpenCV 视觉库
date: 2026-08-15  # date-auto-injected
---

# OpenCV 视觉库

<span class="kg-badge kg-badge-tools">工具</span>
<span class="kg-badge kg-badge-ai">视觉</span>

**OpenCV** = Open Source Computer Vision Library，开源**计算机视觉库**，视频处理常用工具。

## 📊 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 2000（Intel） |
| 语言 | C++ / Python / Java |
| 许可 | Apache 2.0 |
| 版本 | 4.x（当前） |
| 模块 | core / imgproc / video / dnn / ml |

## 🏗️ 模块结构

| 模块 | 用途 |
| --- | --- |
| **core** | 基础数据结构 |
| **imgproc** | 图像处理 |
| **imgcodecs** | 图像读写 |
| **videoio** | 视频读写 |
| **video** | 视频分析 |
| **calib3d** | 相机标定、3D |
| **features2d** | 特征检测 |
| **objdetect** | 目标检测 |
| **dnn** | 深度学习 |
| **ml** | 机器学习 |
| **highgui** | GUI |

## 📐 视频读写

```python
import cv2

# 打开视频
cap = cv2.VideoCapture('input.mp4')

# 获取视频属性
fps = cap.get(cv2.CAP_PROP_FPS)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
total = cap.get(cv2.CAP_PROP_FRAME_COUNT)
fourcc = cap.get(cv2.CAP_PROP_FOURCC)

# 读取帧
ret, frame = cap.read()  # ret 是否成功，frame (H,W,3) BGR

# 写入视频
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))
out.write(frame)
out.release()

cap.release()
```

## 📊 图像处理

```python
import cv2
import numpy as np

img = cv2.imread('in.png')

# 缩放
resized = cv2.resize(img, (1280, 720), interpolation=cv2.INTER_LANCZOS4)

# 裁剪
crop = img[100:500, 200:800]

# 旋转
M = cv2.getRotationMatrix2D((w//2, h//2), 45, 1.0)
rotated = cv2.warpAffine(img, M, (w, h))

# 翻转
flipped = cv2.flip(img, 1)  # 1: 水平，0: 垂直

# 色彩空间
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)

# 阈值
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# 边缘
edges = cv2.Canny(gray, 50, 150)

# 模糊
blur = cv2.GaussianBlur(img, (15, 15), 0)
median = cv2.medianBlur(img, 15)

# 形态学
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
eroded = cv2.erode(binary, kernel)
dilated = cv2.dilate(binary, kernel)
```

## 📐 视频分析

```python
# 光流
cap = cv2.VideoCapture('in.mp4')
ret, frame1 = cap.read()
prvs = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
hsv = np.zeros_like(frame1)
hsv[..., 1] = 255

while True:
    ret, frame2 = cap.read()
    if not ret: break
    next = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
    flow = cv2.calcOpticalFlowFarneback(prvs, next, None,
                                        0.5, 3, 15, 3, 5, 1.2, 0)
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    hsv[..., 0] = ang * 180 / np.pi / 2
    hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    cv2.imshow('flow', bgr)
    if cv2.waitKey(1) & 0xFF == ord('q'): break
    prvs = next
```

## 📊 目标检测

### Haar Cascade

```python
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(gray, 1.3, 5)

for (x, y, w, h) in faces:
    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
```

### DNN (深度学习)

```python
# YOLO 模型
net = cv2.dnn.readNet('yolov3.weights', 'yolov3.cfg')
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
net.setInput(blob)
outs = net.forward(output_layers)
```

## 🤖 OpenCV DNN 超分

```python
import cv2

sr = cv2.dnn_superres.DnnSuperResImpl_create()
sr.readModel('ESPCN_x2.pb')
sr.setModel('espcn', 2)

img = cv2.imread('lr.png')
output = sr.upsample(img)
cv2.imwrite('hr.png', output)
```

支持的模型：
- ESPCN (x2, x3, x4)
- FSRCNN (x2, x3, x4)
- LapSRN (x2, x3, x4, x8)

## 📐 视频滤镜

```python
# 实时灰度
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
cv2.imshow('gray', gray)

# 实时边缘
edges = cv2.Canny(gray, 50, 150)
cv2.imshow('edges', edges)

# 实时叠加
overlay = frame.copy()
cv2.rectangle(overlay, (50, 50), (200, 200), (0, 255, 0), -1)
alpha = 0.5
blended = cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0)
```

## 🛠️ 视频编码格式

```python
# OpenCV 支持的四字符码
fourcc_map = {
    'mp4v': cv2.VideoWriter_fourcc(*'mp4v'),  # MP4
    'XVID': cv2.VideoWriter_fourcc(*'XVID'),  # AVI
    'MJPG': cv2.VideoWriter_fourcc(*'MJPG'),  # Motion JPEG
    'VP90': cv2.VideoWriter_fourcc(*'VP90'),  # VP9
    'H264': cv2.VideoWriter_fourcc(*'H264'),  # H.264
    'avc1': cv2.VideoWriter_fourcc(*'avc1'),  # H.264 alt
    'HEVC': cv2.VideoWriter_fourcc(*'HEVC'),  # H.265
}
```

## 📊 性能优化

```python
# 跳帧处理
cap.set(cv2.CAP_PROP_POS_FRAMES, 100)  # 跳到第 100 帧

# 多线程
import threading

def process_frame(frame):
    # 处理
    pass

# 使用 GStreamer 后端（更快）
cap = cv2.VideoCapture('in.mp4', cv2.CAP_GSTREAMER)

# 降低分辨率
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
```

## 📐 视频稳定

```python
# 视频稳定
cap = cv2.VideoCapture('in.mp4')
n_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 读取前几帧估计运动
prev_pts = []
curr_pts = []
transforms = np.zeros((n_frames-1, 3), np.float32)

prev_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
prev_pts = cv2.goodFeaturesToTrack(prev_gray, maxCorners=200, qualityLevel=0.01, minDistance=30)

for i in range(1, n_frames):
    ret, curr = cap.read()
    if not ret: break
    curr_gray = cv2.cvtColor(curr, cv2.COLOR_BGR2GRAY)
    curr_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None)

    # 估计变换
    m, _ = cv2.estimateAffine2D(prev_pts[status==1], curr_pts[status==1])
    transforms[i-1] = m

    prev_gray = curr_gray
    prev_pts = curr_pts
```

## 📌 面试考点

1. OpenCV 视频处理流程？
   - VideoCapture → 循环 read → 处理 → VideoWriter
2. OpenCV vs FFmpeg？
   - OpenCV 偏视觉算法；FFmpeg 偏编解码
3. cv2.dnn 超分支持？
   - ESPCN / FSRCNN / LapSRN
4. 视频稳定原理？
   - 光流估计运动 → 平滑变换 → 应用

## 🔗 下一步

- [FFmpeg](/06-tools/ffmpeg)
- [MoviePy](/06-tools/moviepy)
- [AI 视频处理](/07-ai/generation)