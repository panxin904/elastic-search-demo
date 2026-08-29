---
title: Anthropic Messages API
date: 2026-08-29  # date-auto-injected
---

# 🧠 Anthropic Messages API 协议

> Anthropic Claude 的协议设计，与 OpenAI 高度相似但有 5 个关键差异点。

## 📤 请求结构

```http
POST https://api.anthropic.com/v1/messages
Content-Type: application/json
x-api-key: sk-ant-xxx
anthropic-version: 2023-06-01

{
  "model": "claude-sonnet-4-5",
  "system": "你是一个友好的助手",
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "max_tokens": 1024,
  "temperature": 0.7,
  "tools": [
    {
      "name": "get_weather",
      "description": "获取指定城市的天气",
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

## 🔑 与 OpenAI 的 5 大差异

| # | 差异点 | OpenAI | Anthropic |
|---|--------|--------|-----------|
| 1 | **system 位置** | 放 `messages` 第一条（role=system） | 独立顶级字段 `system` |
| 2 | **tool schema 字段名** | `function.parameters` | `input_schema` |
| 3 | **工具调用响应** | `message.tool_calls[]` | `message.content[]` 里 `type: tool_use` 块 |
| 4 | **工具结果回填** | `role: tool` + `tool_call_id` | `role: user` + `content[]` 里 `type: tool_result` 块 |
| 5 | **max_tokens 必填** | 可选（默认无限制） | **必填**（防止账单爆炸） |

## 📥 响应结构

```json
{
  "id": "msg_xxx",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "你好！有什么我可以帮你的吗？"
    }
  ],
  "model": "claude-sonnet-4-5-20250929",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 25,
    "output_tokens": 12
  }
}
```

## 🧩 Content Blocks 设计（Anthropic 特色）

Anthropic 的 `content` 是**数组**，每个元素是一个"内容块"，类型可混搭：

```json
{
  "role": "assistant",
  "content": [
    {
      "type": "thinking",
      "thinking": "用户问天气，应该调用工具..."
    },
    {
      "type": "text",
      "text": "我来查一下北京天气。"
    },
    {
      "type": "tool_use",
      "id": "toolu_xxx",
      "name": "get_weather",
      "input": {"city": "北京"}
    }
  ]
}
```

| 块类型 | 说明 |
|--------|------|
| `text` | 纯文本回复 |
| `image` | 图片（多模态） |
| `tool_use` | 模型请求调用工具 |
| `tool_result` | 工具执行结果（必须回填） |
| `thinking` | 思维链（Extended Thinking 模式） |
| `document` | PDF 文档 |

## 🛠️ 工具调用流程

```
Turn 1:
  user: "北京天气怎么样？"
  → assistant.content: [
       {type: thinking, ...},
       {type: tool_use, id: "toolu_01", name: "get_weather", input: {city: "北京"}}
     ]
  → user.content: [
       {type: tool_result, tool_use_id: "toolu_01", content: "晴，25°C"}
     ]
  → assistant.content: [
       {type: text, text: "北京今天晴，25°C。"}
     ]
```

## 🔄 多轮对话结构

```json
{
  "messages": [
    {"role": "user", "content": "北京天气？"},
    {"role": "assistant", "content": [
      {"type": "tool_use", "id": "toolu_01", "name": "get_weather", "input": {"city": "北京"}}
    ]},
    {"role": "user", "content": [
      {"type": "tool_result", "tool_use_id": "toolu_01", "content": "晴 25°C"}
    ]},
    {"role": "assistant", "content": [
      {"type": "text", "text": "北京今天晴，25°C。"}
    ]},
    {"role": "user", "content": "那上海呢？"}
  ]
}
```

## ⚠️ Anthropic 特有陷阱

1. **必须传 max_tokens**：不传会返回 400 错误
2. **anthropic-version 必填**：HTTP header，至少 `2023-06-01`
3. **tool_result 必须包在 user 消息里**：不能像 OpenAI 用独立 role=tool
4. **image base64 格式**：`{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "..."}}`
5. **Extended Thinking**：`thinking: {type: "enabled", budget_tokens: 5000}` 才能拿到思维链

## 🎯 何时选 Anthropic

- ✅ 需要长上下文（200K tokens）
- ✅ 看重推理 / 代码 / 写作质量
- ✅ 需要 Extended Thinking 看思维链
- ❌ 国内直接调用不便（需代理）
