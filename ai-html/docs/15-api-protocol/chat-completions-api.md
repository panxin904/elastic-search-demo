---
title: OpenAI Chat Completions API
date: 2026-08-29  # date-auto-injected
---

# 💬 OpenAI Chat Completions API 详解

> 行业事实标准，被 DeepSeek / 智谱 / Ollama(via shim) 等大量厂商兼容。

## 📤 请求结构

```http
POST https://api.openai.com/v1/chat/completions
Content-Type: application/json
Authorization: Bearer sk-xxxxxxxx

{
  "model": "gpt-4o",
  "messages": [
    {"role": "system", "content": "你是一个助手"},
    {"role": "user", "content": "用一句话介绍 Python"}
  ],
  "temperature": 0.7,
  "max_tokens": 1024,
  "stream": false,
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "获取指定城市的天气",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {"type": "string", "description": "城市名"}
          },
          "required": ["city"]
        }
      }
    }
  ]
}
```

## 📥 响应结构（非流式）

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1725012345,
  "model": "gpt-4o-2024-08-06",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Python 是一门简洁优雅的通用编程语言。",
        "tool_calls": null
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 12,
    "total_tokens": 37
  }
}
```

## 🔑 关键字段含义

### 请求字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `model` | string | 模型 ID（如 `gpt-4o`、`gpt-4o-mini`、`o1-preview`） |
| `messages` | array | 对话历史，按顺序排列 |
| `temperature` | float | 采样温度 0-2，越高越发散 |
| `max_tokens` | int | 最大输出 token 数 |
| `stream` | bool | 是否流式输出 |
| `tools` | array | 工具定义（Function Calling） |
| `tool_choice` | string/object | 强制调用工具：`"auto"` / `"none"` / `{"type":"function","function":{"name":"x"}}` |
| `response_format` | object | 结构化输出（`{"type":"json_object"}`） |
| `top_p` | float | 核采样阈值 0-1 |
| `frequency_penalty` | float | 频率惩罚 -2 ~ 2 |
| `presence_penalty` | float | 存在惩罚 -2 ~ 2 |
| `stop` | string/array | 停止序列 |
| `seed` | int | 随机种子（配合 `system_fingerprint` 复现结果） |
| `user` | string | 用户标识，用于滥用追踪 |

### 响应字段

| 字段 | 说明 |
|------|------|
| `choices[].finish_reason` | `stop`（自然结束）/ `length`（达到 max_tokens）/ `tool_calls`（触发工具调用）/ `content_filter`（被过滤） |
| `choices[].message.role` | 固定为 `"assistant"` |
| `choices[].message.content` | 模型输出文本（可能为 null 当 tool_calls 存在时） |
| `choices[].message.tool_calls` | 工具调用数组 |
| `usage.prompt_tokens` | 输入 token 数 |
| `usage.completion_tokens` | 输出 token 数 |
| `usage.total_tokens` | 总 token 数 |

## 🔄 消息角色（role）

| Role | 说明 |
|------|------|
| `system` | 系统提示（设定行为、风格、约束） |
| `user` | 用户输入 |
| `assistant` | 模型回复（多轮对话时回填历史） |
| `tool` | 工具执行结果（role=tool 时需 `tool_call_id`） |
| `developer` | o1 系列专用，类似 system |

## 🧮 多轮对话的消息流

```
Turn 1:
  user: "北京天气怎么样？"
  → assistant: tool_call(get_weather, {city: "北京"})
  → tool: {"temperature": 25, "weather": "晴"}  (回填 tool_call_id)
  → assistant: "北京今天晴，25°C。"

Turn 2:
  messages = [
    user, assistant(tool_call), tool, assistant  ← Turn 1 全部
    user: "那上海呢？"                              ← Turn 2 新增
  ]
```

## ⚠️ 常见陷阱

1. **`max_tokens` 不算输入 token**：很多用户误以为包含 prompt，实际只限制输出
2. **`temperature=0` 不等于确定性**：底层仍有非确定性（硬件/调度），需配合 `seed` 才接近复现
3. **多模态 image_url**：需 base64 或公网 URL，且单图大小有限制（GPT-4o 约 20MB）
4. **tool_calls 与 content 互斥**：触发工具时 `content` 为 `null`
5. **JSON Mode 强制语法**：`response_format: {type: json_object}` 时必须在 prompt 明确说"输出 JSON"，否则可能持续输出空

## 🔍 协议抓包示例

用 `mitmproxy` 或 `httpie` 抓取：

```bash
# 使用 httpie 直接调试
http POST https://api.openai.com/v1/chat/completions \
  Authorization:"Bearer $OPENAI_API_KEY" \
  model=gpt-4o-mini \
  messages:='[{"role":"user","content":"hi"}]' \
  max_tokens=10
```

## 🔗 兼容厂商

- **DeepSeek**：`base_url=https://api.deepseek.com`，模型 `deepseek-chat`
- **智谱 GLM**：`base_url=https://open.bigmodel.cn/api/paas/v4`，模型 `glm-4`
- **Ollama**：本地 `http://localhost:11434/v1`
- **vLLM / TGI**：自托管时也兼容 OpenAI 协议

> 💡 通过修改 `base_url` + `model` 字段即可切换厂商，这就是 OpenAI 协议成为事实标准的原因。
