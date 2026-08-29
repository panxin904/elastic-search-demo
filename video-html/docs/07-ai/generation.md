---
title: AI 视频生成 - Sora / Runway
date: 2026-08-15  # date-auto-injected
---

# AI 视频生成

<span class="kg-badge kg-badge-ai">AI</span>
<span class="kg-badge kg-badge-cases">前沿</span>
<span class="kg-badge kg-badge-app">应用</span>

用 AI 模型从**文本/图像**生成视频，是 2024-2025 最热门的 AI 应用。

## 📊 主流视频生成模型

| 模型 | 厂商 | 推出 | 时长 | 分辨率 |
| --- | --- | --- | --- | --- |
| **Sora** | OpenAI | 2024.02 | 60s | 1080p |
| **Sora 2** | OpenAI | 2024.12 | 25s | 1080p |
| **Veo 2** | Google | 2024.12 | 多段 | 4K |
| **Runway Gen-3 Alpha** | Runway | 2024 | 10s | 1080p |
| **Gen-4** | Runway | 2025 | - | 1080p |
| **Pika 1.5** | Pika Labs | 2024 | 4s | 1080p |
| **Pika 2.0** | Pika Labs | 2025 | - | 1080p |
| **Kling 1.6** | 快手 | 2024 | 10s | 1080p |
| **Kling 2.0** | 快手 | 2025 | - | 1080p |
| **Hailuo** | MiniMax | 2024 | 6s | 720p |
| **HunyuanVideo** | 腾讯 | 2024 | 5s | 720p |
| **Wan 2.1** | 阿里 | 2025 | 5s+ | 1080p |
| **Mochi** | Genmo | 2024 | - | 480p |
| **CogVideoX** | 智谱 | 2024 | 6s | 720p |
| **Vidu** | 生数 | 2024 | 8s | 1080p |
| **Jimeng AI** | ByteDance | 2024 | 5s | 1080p |

## 🧠 视频生成原理

### 三大主流架构

```
1. 扩散模型 (Diffusion)
   代表: Sora / Kling / HunyuanVideo / CogVideoX
   原理: 噪声 → 去噪 → 视频

2. Transformer / DiT
   代表: Sora (DiT)
   原理: 把视频切成 patch，用 Transformer 处理

3. GAN
   代表: 早期 StyleGAN-V
   已被超越
```

## 📐 Diffusion Transformer (DiT)

Sora 使用的架构，结合 Diffusion + Transformer。

```
流程:
  1. 视频 → 时空 patch (3D)
  2. Patch → Token
  3. DiT 去噪
  4. Token → 视频

关键:
  - Spacetime Latent Patches
  - 大规模数据
  - 多模态（文 + 图 + 视频）
```

## 📐 主要技术细节

### Sora 创新点

```
1. Spacetime Patches
   把视频统一表示为时空 patches
   类似 NLP 的 token

2. 视频压缩网络
   专门的 VAE 压缩视频到 latent

3. 扩散 Transformer (DiT)
   在 latent 空间去噪

4. 大规模训练
   海量视频数据
```

### 关键能力

| 能力 | 说明 |
| --- | --- |
| **文生视频 (T2V)** | 文本 → 视频 |
| **图生视频 (I2V)** | 单图 + 文本 → 视频 |
| **视频生视频 (V2V)** | 视频 → 视频 |
| **视频拼接** | 多个片段拼接 |
| **相机控制** | 推拉、旋转、平移 |
| **角色一致性** | 同一角色多段 |

## 📐 应用场景

| 场景 | 描述 |
| --- | --- |
| **影视特效** | 镜头生成 |
| **广告** | 快速生成创意 |
| **短视频** | 创意视频 |
| **游戏** | CG 预告 |
| **教育** | 可视化教学 |
| **新闻** | 视频生成 |
| **社交媒体** | 表情包、梗图 |

## 🛠️ 开源模型

### HunyuanVideo（腾讯）

```bash
# GitHub: Tencent/HunyuanVideo

pip install -r requirements.txt

python sample.py \
  --prompt "A cat walking in the garden" \
  --video-length 5 \
  --infer-steps 50
```

### CogVideoX（智谱）

```python
# GitHub: zai-org/CogVideo

from diffusers import CogVideoXPipeline

pipe = CogVideoXPipeline.from_pretrained(
    "THUDM/CogVideoX-5b",
    torch_dtype=torch.bfloat16
).to("cuda")

prompt = "A cat walking in the garden"
video = pipe(prompt=prompt, num_frames=49, height=480, width=720).frames[0]
```

### Wan 2.1（阿里）

```bash
# GitHub: Alibaba-PAI/Wan2.1

python generate.py \
  --task t2v-14B \
  --prompt "A cat walking" \
  --size 1280*720 \
  --frame_num 81
```

### Kling（快手 API）

```python
import requests

url = "https://api.klingai.com/v1/videos/text2video"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
data = {
    "model": "kling-v1",
    "prompt": "A cat walking",
    "duration": "5",
    "aspect_ratio": "16:9"
}

response = requests.post(url, json=data, headers=headers)
task_id = response.json()['data']['task_id']

# 轮询结果
# ...
```

## 📐 评估指标

| 指标 | 含义 |
| --- | --- |
| **FVD** | Fréchet Video Distance |
| **IS** | Inception Score |
| **CLIP Score** | 文本对齐 |
| **Temporal Consistency** | 时域一致 |
| **User Study** | 人工评分 |
| **VBench** | 全面评估 |

## ⚠️ 当前局限

| 局限 | 说明 |
| --- | --- |
| **时长** | 多数 <30s |
| **物理** | 物理规律不真实 |
| **文字** | 文字渲染差 |
| **多角色** | 复杂交互难 |
| **角色一致** | 长视频难保持 |
| **成本** | 推理贵 |

## 📊 商业产品

| 产品 | 厂商 |
| --- | --- |
| **Sora** | OpenAI / ChatGPT Plus |
| **Veo** | Google / Gemini |
| **Runway** | Runway 公司 |
| **Pika** | Pika Labs |
| **Kling** | 快手 |
| **Hailuo** | MiniMax |
| **Jimeng** | 字节跳动 |
| **Vidu** | 生数科技 |
| **PixVerse** | 爱诗科技 |

## 📌 面试考点

1. Sora 核心创新？
   - Spacetime Patches + DiT
2. 扩散模型 vs GAN？
   - Diffusion 效果好；GAN 快
3. 视频生成 vs 图像生成？
   - 多时域一致性要求
4. 当前主流时长？
   - 多数 5-10 秒

## 🔗 下一步

- [AI 超分](/07-ai/super-res-ai)
- [数字人](/07-ai/digital-human)
- [唇形同步](/07-ai/lip-sync)