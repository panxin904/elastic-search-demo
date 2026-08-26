---
title: 计算机视觉
---

# 🖼️ 计算机视觉

> **计算机视觉（Computer Vision）**让计算机**理解和处理图像**。Python 有 OpenCV、Pillow、YOLO 等强大工具。

## 🎯 工具生态

```
基础：
  - OpenCV：图像处理、视频分析、特征检测
  - Pillow：图像读写、基本处理

深度学习：
  - torchvision：PyTorch 视觉库
  - timm：预训练图像模型
  - ultralytics：YOLOv8

高级：
  - MMDetection：目标检测框架
  - segmentation-models-pytorch：语义分割
  - mediapipe：Google 视觉应用
```

## 🚀 OpenCV 入门

### 安装

```bash
pip install opencv-python
# 包含 contrib 模块
pip install opencv-contrib-python
```

### 基础 IO

```python
import cv2

# 读取图片
img = cv2.imread("image.jpg")
print(img.shape)  # (H, W, C)

# 显示图片
cv2.imshow("Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# 保存图片
cv2.imwrite("output.jpg", img)

# 灰度
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 读取视频
cap = cv2.VideoCapture("video.mp4")
while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow("Video", frame)
    if cv2.waitKey(30) & 0xFF == ord('q'):
        break
cap.release()
```

### 基本图像处理

```python
import cv2
import numpy as np

img = cv2.imread("image.jpg")

# 1. 缩放
resized = cv2.resize(img, (640, 480))
# 按比例
h, w = img.shape[:2]
scaled = cv2.resize(img, (w // 2, h // 2))

# 2. 裁剪
crop = img[100:400, 200:600]

# 3. 旋转
center = (w // 2, h // 2)
M = cv2.getRotationMatrix2D(center, 45, 1.0)
rotated = cv2.warpAffine(img, M, (w, h))

# 4. 翻转
h_flip = cv2.flip(img, 1)   # 水平
v_flip = cv2.flip(img, 0)   # 垂直

# 5. 颜色空间
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

# 6. 阈值
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# 7. 模糊
blur = cv2.GaussianBlur(img, (5, 5), 0)

# 8. 边缘检测
edges = cv2.Canny(gray, 100, 200)

# 9. 形态学
kernel = np.ones((5, 5), np.uint8)
eroded = cv2.erode(binary, kernel)
dilated = cv2.dilate(binary, kernel)
```

## 🛠️ 特征检测

### 人脸检测

```python
import cv2

# 加载 Haar Cascade 分类器
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
eye_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_eye.xml"
)

img = cv2.imread("people.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 检测人脸
faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
print(f"检测到 {len(faces)} 张人脸")

# 画框 + 检测眼睛
for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # 在人脸区域检测眼睛
    roi_gray = gray[y:y+h, x:x+w]
    roi_color = img[y:y+h, x:x+w]
    eyes = eye_cascade.detectMultiScale(roi_gray)
    for (ex, ey, ew, eh) in eyes:
        cv2.rectangle(roi_color, (ex, ey), (ex + ew, ey + eh), (255, 0, 0), 2)

cv2.imwrite("detected.jpg", img)
```

### 特征匹配

```python
import cv2
import numpy as np

img1 = cv2.imread("object.jpg", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("scene.jpg", cv2.IMREAD_GRAYSCALE)

# 1. SIFT 特征
sift = cv2.SIFT_create()
kp1, des1 = sift.detectAndCompute(img1, None)
kp2, des2 = sift.detectAndCompute(img2, None)

# 2. 特征匹配
bf = cv2.BFMatcher()
matches = bf.knnMatch(des1, des2, k=2)

# 3. 应用 Lowe's ratio test
good = []
for m, n in matches:
    if m.distance < 0.75 * n.distance:
        good.append(m)

# 4. 绘制匹配
result = cv2.drawMatches(img1, kp1, img2, kp2, good, None, flags=2)
cv2.imwrite("matches.jpg", result)
print(f"匹配点: {len(good)}")
```

## 🛠️ Pillow

```bash
pip install Pillow
```

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 1. 基本操作
img = Image.open("image.jpg")
print(img.size, img.mode)
img_resized = img.resize((640, 480))
img_rotated = img.rotate(45)
img_cropped = img.crop((100, 100, 500, 500))

# 2. 滤镜
img_blurred = img.filter(ImageFilter.BLUR)
img_sharp = img.filter(ImageFilter.SHARPEN)
img_gray = img.convert("L")

# 3. 绘图
draw = ImageDraw.Draw(img)
draw.rectangle([(100, 100), (500, 500)], outline="red", width=3)
draw.text((100, 100), "Hello", fill="blue")

# 4. 拼接
img1 = Image.open("img1.jpg")
img2 = Image.open("img2.jpg")
combined = Image.new("RGB", (img1.width + img2.width, max(img1.height, img2.height)))
combined.paste(img1, (0, 0))
combined.paste(img2, (img1.width, 0))

# 5. 保存
img.save("output.png", "PNG")
img.save("output.jpg", "JPEG", quality=95)
```

## 🎯 YOLOv8 目标检测

### 安装

```bash
pip install ultralytics
```

### 使用预训练模型

```python
from ultralytics import YOLO

# 加载预训练模型
model = YOLO("yolov8n.pt")  # nano（最快）
# model = YOLO("yolov8s.pt")  # small
# model = YOLO("yolov8m.pt")  # medium
# model = YOLO("yolov8l.pt")  # large
# model = YOLO("yolov8x.pt")  # xlarge（最准）

# 1. 单张图片
results = model("image.jpg")
for result in results:
    boxes = result.boxes
    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].tolist()
        print(f"Class: {cls}, Conf: {conf:.2f}, Box: {xyxy}")

# 2. 视频
results = model("video.mp4", save=True)

# 3. 实时摄像头
results = model(source=0, show=True)  # 0 = 默认摄像头
```

### 自定义训练

```yaml
# dataset.yaml
path: ./datasets/coco128
train: images/train2017
val: images/train2017
test:
nc: 80
names: ['person', 'bicycle', ...]
```

```python
from ultralytics import YOLO

# 加载预训练模型
model = YOLO("yolov8n.pt")

# 训练
results = model.train(
    data="dataset.yaml",
    epochs=100,
    imgsz=640,
    batch=16,
    name="yolov8n_custom"
)
```

### 推理

```python
from ultralytics import YOLO

# 加载训练好的模型
model = YOLO("runs/detect/yolov8n_custom/weights/best.pt")

# 推理
results = model("test.jpg")

# 解析结果
for r in results:
    boxes = r.boxes
    masks = r.masks
    keypoints = r.keypoints
    probs = r.probs
    orig_shape = r.orig_shape
    img_shape = r.orig_img.shape

# 保存结果图片
results[0].save("output.jpg")

# 视频推理
results = model("video.mp4", save=True, conf=0.5)
```

## 🛠️ torchvision

```python
import torch
import torchvision
from torchvision import transforms, models

# 1. 数据预处理
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# 2. 加载预训练模型
model = models.resnet50(pretrained=True)
model.eval()

# 3. 推理
from PIL import Image
img = Image.open("cat.jpg")
input_tensor = preprocess(img)
input_batch = input_tensor.unsqueeze(0)

with torch.no_grad():
    output = model(input_batch)

# 4. 预测
probabilities = torch.nn.functional.softmax(output[0], dim=0)
top5_prob, top5_cat = torch.topk(probabilities, 5)
print("Top 5 预测：")
for i in range(5):
    print(f"  {top5_cat[i].item()}: {top5_prob[i].item():.2%}")
```

## 🛠️ OpenCV 视频处理

```python
import cv2

# 读取摄像头
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 1. 灰度
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 2. 人脸检测
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # 3. 显示
    cv2.imshow("Camera", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## 🛠️ 实战：车牌识别

```python
import cv2
import numpy as np

def recognize_license_plate(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. 边缘检测
    edges = cv2.Canny(gray, 100, 200)
    
    # 2. 形态学
    kernel = np.ones((5, 5), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    
    # 3. 找轮廓
    contours, _ = cv2.findContours(
        closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    
    # 4. 找矩形轮廓
    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        
        if len(approx) == 4:  # 矩形
            cv2.drawContours(img, [approx], -1, (0, 255, 0), 3)
            # OCR 识别（需集成 tesseract）
            x, y, w, h = cv2.boundingRect(approx)
            plate = gray[y:y+h, x:x+w]
            return plate
    
    return None

plate = recognize_license_plate("car.jpg")
if plate is not None:
    cv2.imwrite("plate.jpg", plate)
```

## 🎯 总结

**计算机视觉核心要点**：
- ✅ OpenCV：基础图像处理
- ✅ Pillow：简单图像 IO
- ✅ YOLOv8：目标检测（最流行）
- ✅ torchvision：PyTorch 视觉库
- ✅ 视频处理（摄像头、视频文件）
- ✅ 特征检测（人脸、边缘、关键点）
- ✅ 实时检测（YOLO + 摄像头）
- ✅ 自定义训练（YOLOv8 / ResNet）
- ⚠️ 大模型需要 GPU 推理
- ⚠️ 数据集标注耗时

**下一步：** [🗣️ 自然语言处理](/06-ai-ml/nlp) — spaCy / HuggingFace NLP


<!-- auto-enrich:do-not-edit -->

## 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| TODO_1 | 待补充 | - |
| TODO_2 | 待补充 | - |

## 进阶话题

> TODO: 此节可补充 3-5 段深度内容（如生产环境实战 / 常见错误 / 对比其他方案 / 未来演进）。

补充方向：
- 在生产环境如何配置 / 调优
- 与同类方案的对比（如 A vs B）
- 常见 3-5 个错误及排查
- 进阶阅读资料链接
<!-- auto-enrich:do-not-edit -->
