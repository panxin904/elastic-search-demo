---
title: 结构化输出协议
date: 2026-08-29  # date-auto-injected
---

# 📋 结构化输出协议

> 强制模型输出合法 JSON 的两种方式：JSON Mode 与 Tool Use Mode。

## 🆚 两种方案对比

| 维度 | JSON Mode | Tool Use Mode |
|------|----------|---------------|
| 实现 | `response_format: {type: json_object}` | `tools: [{function: {name: "x", parameters: schema}}]` + `tool_choice` |
| 输出位置 | `message.content`（字符串 JSON） | `message.tool_calls[].function.arguments`（字符串 JSON） |
| Schema 控制 | 无（只保证合法 JSON） | 有（强制按 schema 输出） |
| 多字段校验 | ❌ 需客户端 Zod/Pydantic 校验 | ✅ 强制符合 schema |
| 可同时对话 | ❌（专注 JSON 输出） | ✅ 可混合自然语言 |
| 适用场景 | 简单提取 | 复杂结构化 |

## 📤 JSON Mode（OpenAI）

### 请求

```json
{
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "system", "content": "提取用户信息，输出 JSON。"},
    {"role": "user", "content": "我叫张三，30 岁，住在上海，邮箱 zhang@example.com"}
  ],
  "response_format": {"type": "json_object"}
}
```

### 响应

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "{\"name\": \"张三\", \"age\": 30, \"city\": \"上海\", \"email\": \"zhang@example.com\"}"
    }
  }]
}
```

### ⚠️ 限制

1. **prompt 必须明确说"输出 JSON"**：否则模型可能输出空对象 `{}`
2. **不保证 schema 字段**：模型可能漏字段或多字段
3. **JSON 模式禁用 system 外的对话**：不能"先聊天再输出 JSON"

## 📤 Tool Use Mode（结构化最强）

### 请求

```json
{
  "model": "gpt-4o-2024-08-06",
  "messages": [{"role": "user", "content": "提取：张三 30 岁 上海 zhang@example.com"}],
  "tools": [{
    "type": "function",
    "function": {
      "name": "extract_user",
      "description": "提取用户信息",
      "parameters": {
        "type": "object",
        "properties": {
          "name": {"type": "string", "description": "姓名"},
          "age": {"type": "integer", "description": "年龄", "minimum": 0, "maximum": 150},
          "city": {"type": "string", "description": "城市"},
          "email": {"type": "string", "format": "email"}
        },
        "required": ["name", "age"],
        "additionalProperties": false
      }
    }
  }],
  "tool_choice": {"type": "function", "function": {"name": "extract_user"}}
}
```

### 响应（强制走工具）

```json
{
  "choices": [{
    "message": {
      "tool_calls": [{
        "id": "call_xxx",
        "type": "function",
        "function": {
          "name": "extract_user",
          "arguments": "{\"name\":\"张三\",\"age\":30,\"city\":\"上海\",\"email\":\"zhang@example.com\"}"
        }
      }]
    }
  }]
}
```

### ✅ 优势

1. **强制 schema 校验**：服务端拒绝不符合 schema 的输出
2. **字段类型保证**：age 一定是 integer，email 一定是 email 格式
3. **`additionalProperties: false`**：禁止额外字段
4. **可声明 enum 限制**：如 `role: {enum: ["user", "admin"]}`

## 📐 复杂 Schema 示例

```json
{
  "name": "analyze_code",
  "description": "分析代码质量",
  "parameters": {
    "type": "object",
    "properties": {
      "language": {"type": "string", "enum": ["python", "javascript", "go", "rust"]},
      "issues": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "line": {"type": "integer", "minimum": 1},
            "severity": {"type": "string", "enum": ["error", "warning", "info"]},
            "message": {"type": "string"},
            "suggestion": {"type": "string"}
          },
          "required": ["line", "severity", "message"]
        }
      },
      "score": {"type": "number", "minimum": 0, "maximum": 10}
    },
    "required": ["language", "issues", "score"]
  }
}
```

## 🛡️ 客户端再校验（兜底）

即使使用 Tool Use Mode，**仍建议客户端二次校验**（模型可能输出畸形 JSON）：

```python
import json
from pydantic import BaseModel, Field, ValidationError

class User(BaseModel):
    name: str
    age: int = Field(ge=0, le=150)
    city: str | None = None
    email: str | None = None

raw_args = tool_call.function.arguments
try:
    user = User.model_validate_json(raw_args)
except ValidationError as e:
    # 重试或 fallback
    log.error(f"Schema validation failed: {e}")
    # 可选：把错误回填给模型，让它修正
    messages.append({"role": "tool", "tool_call_id": ..., "content": f"Error: {e}"})
```

## 🔄 重试策略

```python
def extract_with_retry(messages, tools, tool_name, validator, max_retry=2):
    for attempt in range(max_retry + 1):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": tool_name}},
        )
        tc = response.choices[0].message.tool_calls[0]
        try:
            return validator(tc.function.arguments)
        except ValidationError as e:
            if attempt == max_retry: raise
            # 把错误回填给模型，让它修正
            messages.append(response.choices[0].message)
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": f"Validation error: {e}. Please fix and retry.",
            })
```

## 🎯 Anthropic 的结构化输出

Anthropic 没有 JSON Mode，但可以用 Tool Use Mode 实现完全相同的效果。

如果不需要严格 schema，可以用 Prompt + ```json 代码块：

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": """提取用户信息，严格输出 JSON，不要其他文字：

Input: 我叫张三，30 岁，住在上海

Output format:
{"name": "...", "age": int, "city": "..."}"""
    }],
)
text = response.content[0].text
data = json.loads(text)  # 客户端解析
```

## 🔗 关联章节

- [tool-use-protocol](./tool-use-protocol) - Tool Use 完整协议
- [11-tools/structured-output](../11-tools/structured-output) - Pydantic / Zod 集成
- [context-tokens](./context-tokens) - 结构化输出的 Token 成本
