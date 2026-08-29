---
title: Function Calling
date: 2026-08-15  # date-auto-injected
---

# Function Calling（工具调用）

> 让 LLM **调用外部 API / 函数**。**Agent 的基础**。

## 🤔 为什么需要

```
LLM 限制：
  ❌ 知识截止
  ❌ 不知道实时（天气 / 股票）
  ❌ 不能写文件 / 发邮件 / 调 DB

Function calling：
  ✅ LLM 决定调哪个函数 / 传什么参数
  ✅ 应用执行函数 / 拿到结果
  ✅ 把结果喂回 LLM → 继续生成
```

## 🏗 三步流程

```
1. LLM + 工具 schema
2. LLM 决定调 get_weather(city="北京")
3. 应用调 API → "25°C 晴"
4. 结果喂回 LLM
5. LLM 生成最终回答 "北京今天 25°C 晴"
```

## 🚀 OpenAI 实战

```python
import json
from openai import OpenAI

client = OpenAI()

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get current weather for a city. Use when user asks about weather.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. Beijing"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"], "default": "celsius"}
            },
            "required": ["city"]
        }
    }
}]

def get_weather(city: str, unit: str = "celsius") -> str:
    # 实际调天气 API
    return f"{city} 25°{'C' if unit == 'celsius' else 'F'} 晴"

# 1. 第一次：用户问 + 工具
messages = [{"role": "user", "content": "北京今天天气？"}]
resp = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools
)
msg = resp.choices[0].message
print(msg.tool_calls)  # AI 决定调 get_weather

# 2. 拿到 tool_call，应用执行
if msg.tool_calls:
    call = msg.tool_calls[0]
    args = json.loads(call.function.arguments)
    result = get_weather(**args)

    # 3. 把结果喂回 LLM
    messages.append(msg)
    messages.append({
        "role": "tool",
        "tool_call_id": call.id,
        "content": result
    })
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        tools=tools
    )
    print(resp.choices[0].message.content)
    # "北京今天 25°C 晴。"
```

## 🚀 Anthropic 实战

```python
import json
from anthropic import Anthropic

client = Anthropic()

tools = [{
    "name": "get_weather",
    "description": "Get current weather for a city",
    "input_schema": {
        "type": "object",
        "properties": {
            "city": {"type": "string"}
        },
        "required": ["city"]
    }
}]

messages = [{"role": "user", "content": "北京天气？"}]
resp = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    tools=tools,
    messages=messages
)

# 处理 tool_use
if resp.stop_reason == "tool_use":
    tool = next(b for b in resp.content if b.type == "tool_use")
    result = get_weather(**tool.input)

    # 续
    messages.append({"role":"assistant","content":resp.content})
    messages.append({
        "role":"user",
        "content":[{
            "type":"tool_result",
            "tool_use_id":tool.id,
            "content":result
        }]
    })
    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )
    print(resp.content[0].text)
```

## 📐 Schema 设计

### 用 JSON Schema（OpenAI 严格 / Anthropic 严格）

```python
tools = [{
    "type": "function",
    "function": {
        "name": "search_docs",
        "description": """Search internal documentation.
        Call this when user asks about company policies, processes, or technical docs.
        Don't call for general knowledge questions.""",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query, 2-5 keywords is best"
                },
                "max_results": {
                    "type": "integer",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20
                },
                "category": {
                    "type": "string",
                    "enum": ["policy", "tech", "process", "all"],
                    "default": "all"
                }
            },
            "required": ["query"]
        }
    }
}]
```

### 复杂参数（数组 / 对象）

```python
parameters={
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of items to add"
        },
        "filter": {
            "type": "object",
            "properties": {
                "min_price": {"type": "number"},
                "max_price": {"type": "number"},
                "tags": {"type": "array", "items": {"type": "string"}}
            }
        }
    }
}
```

## 🛠 工具调用最佳实践

### 1. 清晰的 description

```python
# ❌ 不好
"name": "search", "description": "search things"

# ✅ 好
"""name": "search_docs",
description": "Search internal company documentation.
Call when user asks about HR policies, technical processes, or product specs.
Don't use for general knowledge — those should be answered directly."""
```

### 2. 错误处理

```python
def safe_get_weather(city: str):
    try:
        return get_weather(city)
    except Exception as e:
        return f"错误：{e}"

# 把 error 喂回 LLM
messages.append({
    "role":"tool",
    "tool_call_id": call.id,
    "content": f"错误：无法获取 {city} 的天气",
    # LLM 看到错误 → 调整 / 道歉
})
```

### 3. 限制 tool 数量

```python
# LLM 一次最多选 1-3 个 tool
# 太多会乱
tools = [...]  # 3-5 个
```

### 4. Tool 描述要写清边界

```python
"description": "查询数据库。只在用户明确问"销售数据"时调用。用户问一般问题时不要调。"
```

## 🆚 vs JSON mode

| | Tool calling | JSON mode |
|--|--------------|------------|
| 用途 | 调函数 | 输出结构化 JSON |
| 多次调用 | ✅ 链式 | 单次 |
| 应用执行 | ✅ 需要 | ❌ |

```python
# JSON mode
resp = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[...],
    response_format=WeatherResult
)
# LLM 直接返回符合 schema 的 JSON
```

## 🆚 vs MCP

| | Function Calling | MCP |
|--|------------------|-----|
| 范围 | 单应用 | 跨应用 / 标准化 |
| 工具定义 | 每次 inline | 注册到 server |
| 适合 | 小项目 | 复用 / 多 host |

详见 [MCP 核心概念](/06-mcp/core)。

## 🛠 实战：完整多轮 tool 循环

```python
import json
from openai import OpenAI

client = OpenAI()
TOOLS = [...]  # 多个工具

def process_tool_call(call):
    name = call.function.name
    args = json.loads(call.function.arguments)
    # 路由到对应函数
    if name == "search_docs": return search_docs(**args)
    if name == "send_email": return send_email(**args)
    raise ValueError(f"Unknown tool: {name}")

def chat(prompt, max_iter=10):
    messages = [{"role": "user", "content": prompt}]
    for _ in range(max_iter):
        resp = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOLS
        )
        msg = resp.choices[0].message

        if not msg.tool_calls:
            return msg.content  # 完成

        # 调 tool
        messages.append(msg)
        for call in msg.tool_calls:
            try:
                result = process_tool_call(call)
            except Exception as e:
                result = f"Error: {e}"
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result)
            })
    return "达到最大迭代次数"

print(chat("查 2024 差旅政策，并给 alice 发邮件"))
```

## 🔗 下一步

- [Tool Use 模式](/11-tools/tool-use)
- [Structured Output](/11-tools/structured-output)
- [MCP 核心概念](/06-mcp/core)
- [LangGraph](/04-agents/langgraph)

## 🔗 相关阅读（跨站导航）

<!-- xlink-subpage-injected:do-not-edit -->

本页相关主题的跨站入口:

- [python](https://java-px.bot.cd/python/):Python AI
- [bigdata](https://java-px.bot.cd/bigdata/):大数据训练
- [system-design](https://java-px.bot.cd/system-design/):AI 系统架构
