---
title: Claude 模型家族
---

# Claude 模型家族

> Anthropic 公司出品的闭源大模型，以 **Constitutional AI**（宪法 AI）和 **长上下文**（200K）著称。

## 🧬 模型族

| 模型 | 上下文 | 定位 | 何时用 |
|------|--------|------|--------|
| **Claude Opus 4.5** | 200K | 最强推理 | 复杂代码 / 研究 / 多步分析 |
| **Claude Sonnet 4.5** | 200K | 平衡（默认推荐） | 日常编码 / Agent / 写作 |
| **Claude Haiku 4** | 200K | 快 + 便宜 | 高频简单任务 / 分类 / 提取 |
| Claude 3.5 Sonnet (legacy) | 200K | 上一代主力 | 已让位 Sonnet 4.5 |
| Claude 3 Opus (legacy) | 200K | 上一代旗舰 | 已让位 Opus 4.5 |

## 🔑 核心能力

- **200K tokens 上下文**（约 15 万中文字 / 500 页 PDF）
- **Tool use**（Function calling）原生支持
- **Vision**（图片 / PDF 解析）
- **Computer use**（Opus 4.x 试验）：让模型直接操作浏览器
- **MCP**（Model Context Protocol）原生支持
- **代码能力极强**（SWE-bench Verified 排名第一）

## 🚀 调用

```python
from anthropic import Anthropic

client = Anthropic()  # ANTHROPIC_API_KEY

# 基础调用
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "你好"}]
)
print(msg.content[0].text)

# 流式
with client.messages.stream(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "讲个笑话"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

# Tool use
tools = [{
    "name": "get_weather",
    "description": "Get current weather for a city",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"]
    }
}]
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "北京今天天气怎样？"}]
)
```

## 🔐 API Key 与费用

```bash
# 环境变量
export ANTHROPIC_API_KEY=sk-ant-...

# 查余额
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -d '{"model":"claude-sonnet-4-5","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}'
```

| 模型 | 输入 ($/MTok) | 输出 ($/MTok) |
|------|--------------|---------------|
| Opus 4.5 | 15 | 75 |
| Sonnet 4.5 | 3 | 15 |
| Haiku 4 | 0.80 | 4 |

## 🛠 实用技巧

```python
# Prompt cache（重复前缀可省 90% 成本）
client.messages.create(
    model="claude-sonnet-4-5",
    system=[
        {"type": "text", "text": "你是资深架构师"},
        {"type": "text", "text": "<你的超长文档 / few-shot examples>",
         "cache_control": {"type": "ephemeral"}}
    ],
    messages=[{"role": "user", "content": "分析代码"}]
)

# Streaming for 长输出
# Vision（看图 / PDF）
import base64
with open("chart.png", "rb") as f:
    img = base64.standard_b64encode(f.read()).decode()
msg = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role":"user","content":[
        {"type":"image","source":{"type":"base64","media_type":"image/png","data":img}},
        {"type":"text","text":"解释这个图"}
    ]}]
)
```

## 🆚 vs 其他模型

| | Claude 4.5 | GPT-4o | Gemini 2.5 Pro |
|--|-----------|--------|---------------|
| 长上下文 | 200K | 128K | 1M-2M |
| 推理 | 极强 | 强 | 极强 |
| 代码 | 极强 | 强 | 强 |
| 多模态 | 图 / PDF | 图 | 图 / 音 / 视 |
| 速度 | 中 | 中快 | 中 |
| 价格 | 中 | 中 | 中 |

## 🛠 实战

```python
# 多轮 + Tool use + Vision
import anthropic, base64
client = anthropic.Anthropic()

tools = [{
    "name": "search_docs",
    "description": "Search internal knowledge base",
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string"}},
        "required": ["query"]
    }
}]

resp = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2048,
    tools=tools,
    messages=[{"role":"user","content":"找到最新的报销政策"}]
)

# 处理 tool use
while resp.stop_reason == "tool_use":
    tool_call = next(b for b in resp.content if b.type == "tool_use")
    tool_result = my_search_function(tool_call.input["query"])
    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=2048,
        tools=tools,
        messages=[
            {"role": "user", "content": "找到最新的报销政策"},
            {"role": "assistant", "content": resp.content},
            {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": tool_call.id, "content": tool_result}
            ]}
        ]
    )
print(resp.content[0].text)
```

## 🔗 下一步

- [GPT / OpenAI](/01-models/gpt)
- [Claude SDK / Anthropic](/03-sdks/claude-sdk)
- [模型对比与选型](/01-models/compare)