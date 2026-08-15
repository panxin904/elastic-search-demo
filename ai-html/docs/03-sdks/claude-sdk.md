---
title: Claude SDK / Anthropic
---

# Claude SDK（Anthropic）

> 官方 SDK：Python / Node.js / Go / Java / Ruby / C#。OpenAI 兼容 API 也有。

## 📦 安装

```bash
# Python
pip install anthropic

# Node.js / TypeScript
npm install @anthropic-ai/sdk

# Go
go get github.com/anthropics/anthropic-sdk-go

# Java
# https://github.com/anthropics/anthropic-sdk-java

# 多语言 SDK
# https://docs.anthropic.com/en/api/client-sdks
```

## 🚀 Python 基础

```python
from anthropic import Anthropic

client = Anthropic()  # 读 ANTHROPIC_API_KEY

# 基础调用
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "你好"}]
)
print(msg.content[0].text)

# 多轮
resp = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Python 是什么"},
        {"role": "assistant", "content": "Python 是高级解释型语言..."},
        {"role": "user", "content": "用它能做什么？"}
    ]
)

# 流式
with client.messages.stream(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role":"user","content":"讲个笑话"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

# 系统提示
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    system="你是资深 Python 工程师，回答简洁",
    messages=[{"role":"user","content":"asyncio 是？"}]
)
```

## 🛠 Tool use（Function calling）

```python
import json
from anthropic import Anthropic

client = Anthropic()

tools = [{
    "name": "get_weather",
    "description": "Get current weather for a city",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name"}},
        "required": ["city"]
    }
}]

def get_weather(city: str) -> str:
    # 实际调天气 API
    return f"{city} 今天 25°C 晴"

def process_tool_call(tool_name, tool_input):
    if tool_name == "get_weather":
        return get_weather(**tool_input)

# 多轮调
messages = [{"role": "user", "content": "北京天气怎样？"}]

while True:
    msg = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )
    if msg.stop_reason != "tool_use":
        print("AI:", msg.content[0].text)
        break

    # 处理 tool call
    tool_results = []
    for block in msg.content:
        if block.type == "tool_use":
            result = process_tool_call(block.name, block.input)
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result
            })
            messages.append({"role":"assistant","content":msg.content})
            messages.append({"role":"user","content":tool_results})
```

## 🖼 Vision

```python
import base64, httpx
from anthropic import Anthropic

client = Anthropic()

# URL 图片
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role":"user","content":[
        {"type":"image","source":{"type":"url","url":"https://..."}},
        {"type":"text","text":"描述"}
    ]}]
)

# 本地图片（base64）
with open("photo.jpg", "rb") as f:
    img = base64.standard_b64encode(f.read()).decode()
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role":"user","content":[
        {"type":"image","source":{"type":"base64","media_type":"image/jpeg","data":img}},
        {"type":"text","text":"这张图有什么？"}
    ]}]
)
print(msg.content[0].text)

# PDF
with open("doc.pdf", "rb") as f:
    pdf = base64.standard_b64encode(f.read()).decode()
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2048,
    messages=[{"role":"user","content":[
        {"type":"document","source":{"type":"base64","media_type":"application/pdf","data":pdf}},
        {"type":"text","text":"总结"}
    ]}]
)
```

## 💰 Prompt cache（省 90% 成本）

```python
# 长 system prompt 加 cache_control
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    system=[
        {"type": "text", "text": "你是资深 Python 工程师"},
        {"type": "text", "text": "<你的 50KB 文档>",
         "cache_control": {"type": "ephemeral"}}
    ],
    messages=[{"role":"user","content":"解释 asyncio"}]
)
# 同样 system 重复 → 命中 cache，省 90% input cost
```

## 🔧 Node.js

```js
import Anthropic from "@anthropic-ai/sdk"
const client = new Anthropic()

const msg = await client.messages.create({
  model: "claude-sonnet-4-5",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Hi" }]
})
console.log(msg.content[0].text)

// 流式
const stream = client.messages.stream({
  model: "claude-sonnet-4-5",
  max_tokens: 1024,
  messages: [{ role: "user", content: "讲个笑话" }]
})
for await (const text of stream.textStream) {
  process.stdout.write(text)
}
```

## 🔌 Agent SDK（Beta）

```python
# 高层 API（自动 tool use + 多轮）
from claude_agent_sdk import Agent

agent = Agent(
    system_prompt="你是研发工程师",
    tools=["Read", "Edit", "Bash", "Grep"],
    model="claude-sonnet-4-5"
)
result = await agent.run("给 fib.py 加 docstring")
print(result)
```

## 🔗 下一步

- [OpenAI SDK](/03-sdks/openai-sdk)
- [LangChain](/03-sdks/langchain)
- [Tool Use 模式](/11-tools/tool-use)
- [Function Calling](/11-tools/function-calling)