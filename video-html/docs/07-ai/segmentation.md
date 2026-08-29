---
title: 视频分割 / 抠像
date: 2026-08-15  # date-auto-injected
---

# 视频分割 / 抠像

<span class="kg-badge kg-badge-ai">AI</span>
<span class="kg-badge kg-badge-algorithm">算法</span>
<span class="kg-badge kg-badge-app">视频会议</span>

把视频中的**前景**与**背景**分离，应用广泛。

## 🧠 任务定义

```
输入: 视频帧
输出: 每像素的标签 / 掩码

类型:
  - 语义分割 (Semantic): 分类
  - 实例分割 (Instance): 区分个体
  - 全景分割 (Panoptic): 综合
  - 视频目标分割 (VOS): 跟踪指定目标
```

## 📐 应用场景

| 场景 | 描述 |
| --- | --- |
| **视频会议** | 背景虚化/替换 |
| **影视抠像** | 绿幕替代（无需绿幕） |
| **自动驾驶** | 道路场景分割 |
| **AR** | 虚拟物体叠加 |
| **短视频** | 人像分割、特效 |
| **医学影像** | 器官分割 |

## 📊 图像分割模型

| 模型 | 年份 | 特点 |
| --- | --- | --- |
| **FCN** | 2015 | 第一篇深度分割 |
| **U-Net** | 2015 | 医学影像 |
| **SegNet** | 2017 | Encoder-Decoder |
| **DeepLab v3+** | 2018 | ASPP + Decoder |
| **PSPNet** | 2017 | Pyramid Pooling |
| **Mask R-CNN** | 2017 | 实例分割 |
| **HRNet** | 2019 | 高分辨率 |
| **Segment Anything (SAM)** | 2023 | 通用分割 |
| **SAM 2** | 2024 | 视频分割 |

## 📊 视频分割模型

### VOS（Video Object Segmentation）

| 模型 | 年份 | 特点 |
| --- | --- | --- |
| **MaskTrack** | 2017 | 跟踪 + 分割 |
| **OSMN** | 2018 | 一次性 |
| **FEELVOS** | 2019 | 嵌入学习 |
| **STM** | 2019 | 时空记忆 |
| **CFBI** | 2020 | 前后景 |
| **HMMN** | 2021 | 多尺度记忆 |
| **STCN** | 2021 | 时空通信 |
| **AOT** | 2021 | 多对象 |
| **DEVA** | 2023 | 解耦视频分割 |
| **SAM 2** | 2024 | Meta 视频分割 |

### VOS 任务类型

| 任务 | 含义 |
| --- | --- |
| **Semi-supervised VOS** | 第一帧给 mask |
| **Unsupervised VOS** | 自动发现前景 |
| **Interactive VOS** | 用户点击 |
| **Refer VOS** | 文本/参考 |

## 📐 SAM / SAM 2（Segment Anything）

**Meta AI 通用分割模型**，2023/2024。

### SAM (Image)

```
能力:
  - 点提示分割
  - 框提示分割
  - 自动分割（everything mode）

应用:
  - 标注加速
  - 任意物体分割
```

### SAM 2 (Video)

```
能力:
  - 视频传播分割
  - 时域一致
  - 实时（接近）

应用:
  - 视频编辑
  - 特效
  - 标注
```

## 🛠️ SAM 2 使用

```python
# GitHub: facebookresearch/segment-anything-2

from sam2.build_sam import build_sam2_video_predictor

predictor = build_sam2_video_predictor(
    config_file="configs/sam2/sam2_hiera_l.yaml",
    ckpt_path="checkpoints/sam2_hiera_large.pt",
    device="cuda"
)

# 推理
with predictor.init_state(video_path="video.mp4"):
    predictor.add_new_points_or_box(
        frame_idx=0,  # 第一帧
        obj_id=1,
        points=[[100, 200]],  # 提示点
        labels=[1]
    )

    for frame_idx, obj_ids, masks in predictor.propagate_in_video():
        # 处理分割结果
        pass
```

## 📐 抠像（Matting）

**Matting** = 把前景分割为 **F (前景) + α (透明度)**

```
输出:
  - F: 前景 RGB
  - α: alpha mask (0-1)

应用:
  - 影视抠像
  - 视频会议
  - AR
```

### 主流 Matting 模型

| 模型 | 年份 | 特点 |
| --- | --- | --- |
| **Deep Image Matting** | 2017 | 第一篇 |
| **MODNet** | 2020 | 人像抠像 |
| **Background Matting v2** | 2021 | 无背景 |
| **Robust Video Matting (RVM)** | 2021 | 视频抠像 |
| **Matting Anything** | 2024 | SAM + Matting |

## 🛠️ Robust Video Matting

```bash
# GitHub: PeterL1n/RobustVideoMatting

# 安装
pip install torch torchvision
pip install -r requirements.txt

# 命令行
python inference.py \
  --input input.mp4 \
  --output-dir output \
  --variant resnet50  # mobilenetv3 / resnet50
```

输出：
- `pha_*.png`（alpha 通道）
- `fgr_*.png`（前景）
- `com_*.png`（合成）

## 📊 视频会议应用

```
Zoom / Teams / 腾讯会议
  ↓
背景模糊 / 替换
  ↓
RVM 或 MediaPipe Selfie Segmentation
  ↓
实时抠像 + 合成
```

### MediaPipe Selfie Segmentation

```python
import mediapipe as mp
import cv2

mp_selfie = mp.solutions.selfie_segmentation
seg = mp_selfie.SelfieSegmentation(model_selection=1)  # 0: general, 1: landscape

cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()
    if not ret: break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = seg.process(rgb)
    mask = result.segmentation_mask

    # 背景模糊
    blurred = cv2.GaussianBlur(frame, (55, 55), 0)
    condition = mask > 0.5
    output = np.where(condition[:, :, None], frame, blurred)
    cv2.imshow('output', output)
    if cv2.waitKey(1) & 0xFF == ord('q'): break
```

## 🛠️ 视频分割评估

| 指标 | 含义 |
| --- | --- |
| **IoU** | 交并比 |
| **mIoU** | 平均 IoU |
| **Dice** | Dice 系数 |
| **Boundary IoU** | 边界 IoU |
| **J&F** | VOS 标准（J + F） |

## 📌 面试考点

1. 图像分割 vs 实例分割？
   - 语义 = 分类；实例 = 区分个体
2. SAM 优势？
   - 零样本、可提示、通用
3. 视频分割难点？
   - 时域一致 + 大运动
4. 抠像 vs 分割？
   - 抠像有透明度

## 🔗 下一步

- [视频修复](/07-ai/inpainting)
- [数字人](/07-ai/digital-human)
- [视频生成](/07-ai/generation)