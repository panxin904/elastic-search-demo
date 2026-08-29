---
title: MoviePy Python
date: 2026-08-15  # date-auto-injected
---

# MoviePy Python 视频库

<span class="kg-badge kg-badge-tools">工具</span>
<span class="kg-badge kg-badge-basics">Python</span>

**MoviePy** = Python 视频编辑库，基于 FFmpeg，简单易用，适合**快速脚本处理**。

## 📊 基本信息

| 项 | 值 |
| --- | --- |
| 推出 | 2014 |
| 语言 | Python |
| 许可 | MIT |
| 后端 | FFmpeg / ImageMagick |
| 版本 | 2.x |

## 📐 安装

```bash
pip install moviepy

# 依赖
pip install imageio imageio-ffmpeg
```

## 🛠️ 基础用法

```python
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips

# 加载视频
clip = VideoFileClip('input.mp4')

# 查看信息
print(f"时长: {clip.duration}s")
print(f"分辨率: {clip.size}")
print(f"帧率: {clip.fps}")

# 播放
clip.preview()

# 保存
clip.write_videofile('output.mp4')
```

## 🎬 剪辑

```python
# 切割
sub1 = clip.subclip(0, 10)   # 0-10 秒
sub2 = clip.subclip(30, 60)  # 30-60 秒

# 拼接
final = concatenate_videoclips([sub1, sub2])

# 裁剪
cropped = clip.crop(x1=100, y1=100, x2=800, y2=600)

# 缩放
resized = clip.resize(width=1280)  # 按宽度
resized = clip.resize(height=720)   # 按高度
resized = clip.resize((1280, 720))  # 指定尺寸

# 旋转
rotated = clip.rotate(90)          # 旋转 90°
rotated = clip.rotate(-45)         # 旋转 -45°

# 翻转
flipped_h = clip.fx(vfx.mirror_x)
flipped_v = clip.fx(vfx.mirror_y)
```

## 🎨 效果

```python
from moviepy.editor import *
from moviepy.video.fx import fadein, fadeout

# 淡入淡出
clip = clip.fx(fadein, 2)    # 淡入 2 秒
clip = clip.fx(fadeout, 2)   # 淡出 2 秒

# 调速
fast = clip.fx(vfx.speedx, 2.0)  # 2 倍速
slow = clip.fx(vfx.speedx, 0.5)  # 0.5 倍速

# 颜色调整
clip = clip.fx(vfx.colorx, 1.5)  # 颜色 × 1.5
clip = clip.fx(vfx.lum_contrast, lum=1.2, contrast=1.1)

# 黑白
bw = clip.fx(vfx.blackwhite)

# 反色
inv = clip.fx(vfx.invert_colors)
```

## 📊 文字水印

```python
from moviepy.editor import TextClip, CompositeVideoClip

# 文字
txt_clip = TextClip(
    "Hello World",
    fontsize=50,
    color='white',
    font='Arial-Bold',
    stroke_color='black',
    stroke_width=2
).set_duration(5)

# 位置
txt_clip = txt_clip.set_position(('center', 'bottom'))

# 合成
final = CompositeVideoClip([clip, txt_clip])
```

## 📐 音频处理

```python
# 加载音频
audio = AudioFileClip('sound.mp3')

# 设置音频
clip = clip.set_audio(audio)

# 提取音频
audio = clip.audio
audio.write_audiofile('sound.mp3')

# 音量
clip = clip.volumex(2.0)

# 音频淡入淡出
clip = clip.audio_fadein(2)
clip = clip.audio_fadeout(2)

# 拼接音频
from moviepy.editor import concatenate_audioclips
combined = concatenate_audioclips([audio1, audio2])
```

## 🎬 合成与图层

```python
# 视频叠加
video1 = VideoFileClip('main.mp4')
video2 = VideoFileClip('overlay.mp4').resize(0.3)  # 30% 大小

# 画中画
video2 = video2.set_position(('right', 'top'))

# 合成
final = CompositeVideoClip([video1, video2], size=video1.size)

# 图片作为图层
from moviepy.editor import ImageClip
logo = ImageClip('logo.png').set_duration(10)
logo = logo.set_position(('right', 'top')).resize(0.2)
final = CompositeVideoClip([video1, logo])
```

## 📊 GIF 与帧

```python
# 保存 GIF
clip.write_gif('out.gif', fps=15)

# 提取帧
frame = clip.get_frame(5.0)  # 第 5 秒的帧 (H,W,3)

# 保存帧
from PIL import Image
Image.fromarray(frame).save('frame.png')

# 帧列表
frames = []
for t in range(0, int(clip.duration), 1):
    frames.append(clip.get_frame(t))
```

## 🛠️ 高级

```python
# 自定义帧函数
from moviepy.Clip import Clip
from moviepy.video.VideoClip import VideoClip

def make_frame(t):
    import numpy as np
    img = np.zeros((480, 640, 3))
    img[:, :, 0] = int(255 * t / 10)
    return img

clip = VideoClip(make_frame, duration=10)
clip.write_videofile('out.mp4', fps=24)
```

## 📊 性能与局限

| 优点 | 局限 |
| --- | --- |
| 简单易用 | 性能一般（不适合实时） |
| Pythonic API | 不支持 GPU |
| 依赖 FFmpeg | 大文件可能内存爆炸 |
| 适合快速脚本 | 视频稳定、超分不支持 |

## 📌 应用场景

| 场景 | 用途 |
| --- | --- |
| **自动化剪辑** | 批量处理视频 |
| **社交媒体** | 添加字幕、logo |
| **数据可视化** | 生成动画 |
| **短视频工具** | 快速合成 |
| **教学/研究** | 视频处理原型 |

## 📌 面试考点

1. MoviePy 与 FFmpeg？
   - MoviePy 基于 FFmpeg，提供 Python API
2. 视频拼接方法？
   - `concatenate_videoclips`
3. 如何提取帧？
   - `clip.get_frame(t)`
4. 大视频怎么处理？
   - 切割后分块处理

## 🔗 下一步

- [FFmpeg](/06-tools/ffmpeg)
- [OpenCV](/06-tools/opencv)
- [HandBrake](/06-tools/handbrake)