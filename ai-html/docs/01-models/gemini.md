---
title: Gemini
date: 2026-08-15  # date-auto-injected
---

# Google Gemini 模型

> Google DeepMind 出品。**长上下文（1M-2M tokens）+ 多模态（图/音/视）+ 工具调用**。

## 🧬 模型族

| 模型 | 上下文 | 定位 |
|------|--------|------|
| **Gemini 2.5 Pro** | 1M-2M | 旗舰 · 推理强 · 多模态 |
| **Gemini 2.5 Flash** | 1M | 性价比主力 |
| **Gemini 2.0 Flash** | 1M | 上一代快 + 便宜 |
| **Gemini 2.0 Pro Exp** | 2M | 实验版 |
| **Gemma 3** | 128K | 开源（本地跑） |

## 🚀 调用（Vertex AI / Google AI Studio）

```python
# 方式 1：Google AI Studio（API key）
import google.generativeai as genai
genai.configure(api_key="AIza...")
model = genai.GenerativeModel("gemini-2.5-pro")

resp = model.generate_content("你好 Gemini")
print(resp.text)

# 流式
for chunk in model.generate_content("讲个笑话", stream=True):
    print(chunk.text, end="", flush=True)

# 视觉
import PIL.Image
img = PIL.Image.open("photo.jpg")
resp = model.generate_content(["描述这张图", img])
print(resp.text)

# 方式 2：Vertex AI（生产 GCP）
from vertexai.generative_models import GenerativeModel, Part
import vertexai
vertexai.init(project="my-proj", location="us-central1")
model = GenerativeModel("gemini-2.5-pro")
resp = model.generate_content("Hi")
print(resp.text)
```

## 🆚 vs 其他

| | Gemini 2.5 Pro | Claude 4.5 | GPT-5 |
|--|----------------|-----------|-------|
| 上下文 | **1M-2M** | 200K | 200K |
| 视频 | **原生** | 图 / PDF | 图 |
| 实时 API | ✅ Live API | ❌ | ❌ |
| Vertex AI | ✅ | ❌ | ❌（Azure） |

## 🛠 实战

```python
# Tool use
model = genai.GenerativeModel(
    "gemini-2.5-pro",
    tools=[{
        "function_declarations": [{
            "name": "search_docs",
            "description": "search internal KB",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }]
    }]
)
chat = model.start_chat(enable_automatic_function_calling=True)
resp = chat.send_message("查最新报销政策")
# 自动调 function，最后给文字回复
```

## 🔗 下一步

- [Claude 模型家族](/01-models/claude)
- [Gemini / Vertex AI SDK](/03-sdks/gemini-sdk)
- [模型对比与选型](/01-models/compare)