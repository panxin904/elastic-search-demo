---
title: Tool Use 协议
date: 2026-08-29  # date-auto-injected
---

# 🛠️ Tool Use / Function Calling 协议

> 让大模型"调用工具"的标准协议：JSON Schema 描述工具、模型返回结构化参数、应用执行后回填结果。

## 🧠 工作原理

```
┌─────────┐                 ┌─────────┐                 ┌──────────┐
│   应用  │ ── 1. 提供工具定义 ──▶ │   LLM   │                 │   工具    │
│         │ ◀── 2. 返回 tool_call ──│         │                 │ (本地/远程)│
│         │ ── 3. 执行工具 ──▶ │         │                 │          │
│         │ ◀── 4. 返回结果 ── │         │                 │          │
│         │ ── 5. 回填结果 + 再问 ──▶│         │                 │          │
│         │ ◀── 6. 自然语言回复 ──│         │                 │          │
└─────────┘                 └─────────┘                 └──────────┘
```

## 📐 OpenAI Tool Use 协议

### 工具定义

```json
{
  "model": "gpt-4o",
  "messages": [{"role": "user", "content": "北京天气怎么样？"}],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "获取指定城市的当前天气",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {
              "type": "string",
              "description": "城市名称，如'北京'"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "default": "celsius"
            }
          },
          "required": ["city"]
        }
      }
    }
  ],
  "tool_choice": "auto"  // "auto" | "none" | {"type": "function", "function": {"name": "..."}}
}
```

### 模型响应（请求调用工具）

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "call_abc123",
          "type": "function",
          "function": {
            "name": "get_weather",
            "arguments": "{\"city\": \"北京\", \"unit\": \"celsius\"}"
          }
        }
      ]
    },
    "finish_reason": "tool_calls"
  }]
}
```

### 回填工具结果

```json
{
  "messages": [
    {"role": "user", "content": "北京天气怎么样？"},
    {"role": "assistant", "content": null, "tool_calls": [
      {"id": "call_abc123", "type": "function", "function": {
        "name": "get_weather", "arguments": "{\"city\": \"北京\"}"
      }}
    ]},
    {"role": "tool", "tool_call_id": "call_abc123", "content": "{\"temperature\": 25, \"weather\": \"晴\"}"},
    {"role": "assistant", "content": "北京今天晴，25°C。"}
  ]
}
```

## 📐 Anthropic Tool Use 协议

### 工具定义（区别在 `input_schema`）

```json
{
  "model": "claude-sonnet-4-5",
  "system": "你是一个天气助手",
  "messages": [{"role": "user", "content": "北京天气怎么样？"}],
  "tools": [
    {
      "name": "get_weather",
      "description": "获取指定城市的当前天气",
      "input_schema": {
        "type": "object",
        "properties": {
          "city": {"type": "string", "description": "城市名"}
        },
        "required": ["city"]
      }
    }
  ]
}
```

### 模型响应（content 数组里嵌入 tool_use 块）

```json
{
  "content": [
    {
      "type": "text",
      "text": "我来查询北京天气。"
    },
    {
      "type": "tool_use",
      "id": "toolu_xxx",
      "name": "get_weather",
      "input": {"city": "北京"}
    }
  ],
  "stop_reason": "tool_use"
}
```

### 回填工具结果（包在 user 消息里）

```json
{
  "messages": [
    {"role": "user", "content": "北京天气怎么样？"},
    {"role": "assistant", "content": [
      {"type": "text", "text": "我来查询北京天气。"},
      {"type": "tool_use", "id": "toolu_xxx", "name": "get_weather", "input": {"city": "北京"}}
    ]},
    {"role": "user", "content": [
      {"type": "tool_result", "tool_use_id": "toolu_xxx", "content": "{\"temperature\": 25, \"weather\": \"晴\"}"}
    ]},
    {"role": "assistant", "content": [{"type": "text", "text": "北京今天晴，25°C。"}]}
  ]
}
```

## 🔑 关键概念

### JSON Schema 限制

工具参数必须是合法的 JSON Schema（OpenAI 较严格，Anthropic 更宽松）：

| 支持 | 不支持 |
|------|--------|
| `string` / `number` / `integer` / `boolean` | 任意复杂的 `$ref` |
| `enum` / `default` / `description` | `oneOf` / `anyOf`（部分支持） |
| `array` of `string` | 嵌套对象超过 5 层 |
| `required` / `nullable` | 循环引用 |

### 工具选择策略

| 场景 | 配置 |
|------|------|
| 模型决定是否调用 | `tool_choice: "auto"` |
| 强制不调用 | `tool_choice: "none"` |
| 强制调用某工具 | `tool_choice: {"type": "function", "function": {"name": "get_weather"}}` |

### 并行调用

模型可以在一次响应中**并行**调用多个工具：

```json
{
  "tool_calls": [
    {"id": "call_1", "function": {"name": "get_weather", "arguments": "{\"city\": \"北京\"}"}},
    {"id": "call_2", "function": {"name": "get_weather", "arguments": "{\"city\": \"上海\"}"}}
  ]
}
```

应用需并行执行，分别回填。

## ⚠️ 常见陷阱

1. **arguments 是字符串**：不是对象，要 `json.loads()` 解析
2. **工具调用时 content 为 null**：模型不输出自然语言，只返回 tool_calls
3. **必须回填 tool_result**：否则模型会"卡住"或幻觉结果
4. **工具数量**：超过 ~20 个会显著降低模型选择准确率，建议合并或路由
5. **错误处理**：工具执行失败要回填错误信息（让模型重试或告知用户）

## 🔧 完整 Python 示例（OpenAI）

```python
import json
from openai import OpenAI

client = OpenAI()

def get_weather(city: str) -> str:
    # 实际调用天气 API
    return json.dumps({"city": city, "temperature": 25, "weather": "晴"})

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市的当前天气",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string"}},
            "required": ["city"]
        }
    }
}]

messages = [{"role": "user", "content": "北京天气怎么样？"}]

# 第一轮：模型请求调用工具
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)
msg = response.choices[0].message
messages.append(msg)  # 把 assistant 消息（含 tool_calls）回填

# 第二轮：执行工具并回填结果
for tc in msg.tool_calls:
    args = json.loads(tc.function.arguments)
    result = get_weather(**args)
    messages.append({
        "role": "tool",
        "tool_call_id": tc.id,
        "content": result,
    })

# 第三轮：模型基于工具结果生成最终回复
response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    tools=tools,
)
print(response.choices[0].message.content)
# 输出: "北京今天晴，25°C。"
```

## 🔗 关联章节

- [structured-output](./structured-output) - Tool Use 与 JSON Mode 的取舍
- [11-tools/function-calling](../11-tools/function-calling) - Function Calling 实战
- [11-tools/tool-use](../11-tools/tool-use) - Anthropic Tool Use 实战
- [06-mcp/core](../06-mcp/core) - MCP 协议（Tool Use 的标准化）
