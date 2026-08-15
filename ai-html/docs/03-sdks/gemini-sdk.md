---
title: Gemini / Vertex AI SDK
---

# Gemini / Vertex AI SDK

> Google 官方 SDK。两个入口：
> - **Google AI Studio**（个人，免费层）
> - **Vertex AI**（企业 / GCP）

## 📦 安装

```bash
# Google AI Studio（轻）
pip install google-generativeai

# Vertex AI（企业，推荐）
pip install google-cloud-aiplatform
```

## 🚀 Google AI Studio（API key）

```python
import google.generativeai as genai

# 1. 拿 API key：https://aistudio.google.com/app/apikey
genai.configure(api_key="AIza...")
model = genai.GenerativeModel("gemini-2.5-pro")

# 基础
resp = model.generate_content("你好 Gemini")
print(resp.text)

# 流式
for chunk in model.generate_content("讲个笑话", stream=True):
    print(chunk.text, end="", flush=True)

# 多轮
chat = model.start_chat()
r1 = chat.send_message("Python 是什么？")
r2 = chat.send_message("它跟 JS 区别？")
print(r2.text)

# Vision
import PIL.Image
img = PIL.Image.open("photo.jpg")
resp = model.generate_content([
    "描述这张图",
    img
])
```

## 🏢 Vertex AI（GCP）

```python
import vertexai
from vertexai.generative_models import GenerativeModel, Part

vertexai.init(project="my-proj", location="us-central1")
model = GenerativeModel("gemini-2.5-pro")

resp = model.generate_content("Hi")
print(resp.text)

# 多模态
img = Part.from_uri("gs://my-bucket/photo.jpg")
resp = model.generate_content([img, "描述"])
```

## 🛠 Tool use（Function calling）

```python
# Google AI Studio
model = genai.GenerativeModel(
    "gemini-2.5-pro",
    tools=[{
        "function_declarations": [{
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string"}
                },
                "required": ["city"]
            }
        }]
    }]
)
chat = model.start_chat(enable_automatic_function_calling=True)
resp = chat.send_message("北京天气？")
print(resp.text)
```

## 🌐 实时 API（Live API）

Gemini 独有：**双向流式**（音 / 视频 / 文字实时交互）。

```python
# Live API：浏览器 ↔ Gemini 音视频
# Python（preview）
import asyncio
from google.genai import Client

async def main():
    client = Client(api_key="AIza...")
    async with client.aio.live.connect(model="gemini-2.5-flash") as session:
        # 推送音频 → 收文字回复
        ...
```

## 📐 长上下文优势

Gemini 1M-2M tokens，**整本 PDF / 长视频**直接传：

```python
import requests
pdf = requests.get("https://arxiv.org/pdf/1706.03762.pdf").content

model = genai.GenerativeModel("gemini-2.5-pro")
resp = model.generate_content([
    {"inline_data": {"mime_type": "application/pdf", "data": pdf}},
    "总结这篇论文的核心贡献"
])
print(resp.text)
```

## 🆚 vs OpenAI / Anthropic

| | Gemini | GPT-4o | Claude |
|--|--------|--------|---------|
| 上下文 | **1M-2M** | 128K | 200K |
| 视频 | **原生** | 静态 | 静态 |
| 实时 | **Live API** | Realtime | ❌ |
| 价格 | 便宜 | 中 | 中 |
| 部署 | GCP / 多云 | Azure / OpenAI | AWS / GCP |

## 🔗 下一步

- [Claude SDK / Anthropic](/03-sdks/claude-sdk)
- [OpenAI SDK](/03-sdks/openai-sdk)
- [Gemini 模型](/01-models/gemini)