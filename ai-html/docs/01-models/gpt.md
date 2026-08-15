---
title: GPT / OpenAI
---

# GPT / OpenAI 模型

> OpenAI 出品的旗舰闭源模型。**生态最广 / 文档最全 / 工具链最丰富**。

## 🧬 模型族（截至 2025）

| 模型 | 上下文 | 定位 | 何时用 |
|------|--------|------|--------|
| **GPT-5** | 200K | 旗舰（推理强） | 复杂任务 / 多步 Agent |
| **GPT-4o** | 128K | 多模态主力 | 日常 / 视觉 / 语音 |
| **GPT-4o mini** | 128K | 便宜快速 | 高频轻量任务 |
| **o1 / o3** | 200K | 推理专精（CoT） | 数学 / 代码 / 复杂推理 |
| **o4-mini** | 200K | o1 系列轻量 | 推理 + 速度平衡 |

## 🚀 调用

```python
from openai import OpenAI

client = OpenAI()  # OPENAI_API_KEY

# Chat Completion
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "你是资深 Python 工程师"},
        {"role": "user", "content": "解释 async/await"}
    ]
)
print(resp.choices[0].message.content)

# 流式
stream = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "讲个笑话"}],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

# Function calling
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        }
    }
}]
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role":"user","content":"北京天气？"}],
    tools=tools
)
```

## 🔐 API Key 与费用

```bash
export OPENAI_API_KEY=sk-...

# 查用量
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

| 模型 | 输入 ($/MTok) | 输出 ($/MTok) |
|------|--------------|---------------|
| GPT-5 | 5 | 20 |
| GPT-4o | 2.5 | 10 |
| GPT-4o mini | 0.15 | 0.6 |
| o1 | 15 | 60 |
| o4-mini | 1.1 | 4.4 |

## 🛠 高级用法

```python
# Structured output（JSON Schema 强约束）
from pydantic import BaseModel

class Weather(BaseModel):
    city: str
    temperature: float
    condition: str

resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role":"user","content":"北京今天天气"}],
    response_format=Weather,
    tools=[{
        "type":"function","function":{
            "name":"get_weather",
            "description":"...",
            "parameters":Weather.model_json_schema()
        }
    }]
)
weather = Weather.model_validate_json(resp.choices[0].message.tool_calls[0].function.arguments)

# Vision
import base64
with open("img.png", "rb") as f:
    img = base64.b64encode(f.read()).decode()
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role":"user","content":[
        {"type":"image_url","image_url":{"url":f"data:image/png;base64,{img}"}},
        {"type":"text","text":"描述"}
    ]}]
)
```

## 🔗 下一步

- [Claude 模型家族](/01-models/claude)
- [Gemini](/01-models/gemini)
- [OpenAI SDK](/03-sdks/openai-sdk)