---
title: OpenAI SDK
---

# OpenAI SDK

> 官方 SDK + **生态最大**（LangChain / LlamaIndex / vLLM 等都走 OpenAI 兼容 API）。

## 📦 安装

```bash
pip install openai
# Node.js
npm install openai
# Go
go get github.com/openai/openai-go
```

## 🚀 Python 基础

```python
from openai import OpenAI

client = OpenAI()  # OPENAI_API_KEY

# Chat
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
    messages=[{"role":"user","content":"讲个笑话"}],
    stream=True
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)

# 视觉
import base64
with open("img.png","rb") as f:
    img = base64.b64encode(f.read()).decode()
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role":"user","content":[
        {"type":"image_url","image_url":{"url":f"data:image/png;base64,{img}"}},
        {"type":"text","text":"描述"}
    ]}]
)
```

## 🛠 Tool use

```python
from openai import OpenAI
import json

client = OpenAI()
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

def get_weather(city): return f"{city} 25°C 晴"

messages = [{"role": "user", "content": "北京天气？"}]
while True:
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools
    )
    if resp.choices[0].finish_reason != "tool_calls":
        print("AI:", resp.choices[0].message.content)
        break

    messages.append(resp.choices[0].message)
    for call in resp.choices[0].message.tool_calls:
        result = get_weather(**json.loads(call.function.arguments))
        messages.append({
            "role": "tool",
            "tool_call_id": call.id,
            "content": result
        })
```

## 🎯 Structured Output（JSON Schema 强约束）

```python
from pydantic import BaseModel
from openai import OpenAI

class UserInfo(BaseModel):
    name: str
    age: int
    email: str

client = OpenAI()
resp = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",  # 支持 structured output 的模型
    messages=[
        {"role": "system", "content": "Extract user info from text"},
        {"role": "user", "content": "Alice, 30, alice@example.com"}
    ],
    response_format=UserInfo
)
user = resp.choices[0].message.parsed
print(user)  # name='Alice' age=30 email='alice@example.com'
```

## 🆚 与 Anthropic SDK 区别

| | OpenAI | Anthropic |
|--|---------|------------|
| `messages.create` | ✅ | ✅ |
| `messages.stream` | ✅ | ✅ |
| Tool use | `tool_calls` 列表 | `content` 块 |
| 视觉 | `image_url` | `image` source |
| PDF | 略麻烦 | 原生 `document` |
| System prompt | 单条 `system` | 可缓存多块 |
| 兼容 | 多数第三方 | Anthropic |

## 🌐 OpenAI 兼容生态

```python
# DeepSeek
client = OpenAI(api_key="sk-...", base_url="https://api.deepseek.com")
resp = client.chat.completions.create(model="deepseek-chat", messages=[...])

# vLLM（自部署）
client = OpenAI(base_url="http://localhost:8000/v1", api_key="EMPTY")

# Ollama（本地）
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
resp = client.chat.completions.create(
    model="qwen2.5",
    messages=[{"role":"user","content":"hi"}]
)
```

## 🔧 Node.js

```js
import OpenAI from "openai"
const client = new OpenAI()

const resp = await client.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: "Hi" }]
})
console.log(resp.choices[0].message.content)

// 流式
const stream = await client.chat.completions.create({
  model: "gpt-4o",
  messages: [{ role: "user", content: "讲个笑话" }],
  stream: true
})
for await (const chunk of stream) {
  process.stdout.write(chunk.choices[0]?.delta?.content || "")
}
```

## 🔗 下一步

- [Claude SDK / Anthropic](/03-sdks/claude-sdk)
- [LangChain](/03-sdks/langchain)
- [Function Calling](/11-tools/function-calling)
- [Ollama 本地推理](/10-deploy/ollama)