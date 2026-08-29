---
title: 流式输出协议 (SSE)
date: 2026-08-29  # date-auto-injected
---

# 🌊 流式输出协议 (SSE) 原理

> 大模型 API 流式输出的标准是 Server-Sent Events (SSE)。理解 SSE 原理，才能正确处理流中断、Token 累积、tool_calls 拼接等细节。

## 🔌 SSE 是什么

**Server-Sent Events (SSE)**：HTML5 标准，服务器单向推送文本流到浏览器。

```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"id":"chatcmpl-1","choices":[{"delta":{"content":"你"}}]}

data: {"id":"chatcmpl-1","choices":[{"delta":{"content":"好"}}]}

data: [DONE]
```

## 🆚 为什么用 SSE 而不是 WebSocket

| 维度 | SSE | WebSocket |
|------|-----|-----------|
| 方向 | 单向（服务器 → 客户端） | 双向 |
| 协议 | HTTP | WS（升级握手） |
| 复杂度 | 低（普通 HTTP） | 高 |
| 重连 | 浏览器原生支持 | 需手写 |
| 适用场景 | LLM 输出（只读流） | 实时聊天 / 协作 |

LLM 场景只需要"服务器推流到客户端"，SSE 足够。

## 📡 OpenAI 流式响应详解

请求：`stream: true`

```
data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1725012345,
       "model":"gpt-4o-mini","choices":[{"index":0,"delta":{"role":"assistant","content":""},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1725012345,
       "model":"gpt-4o-mini","choices":[{"index":0,"delta":{"content":"你"},"finish_reason":null}]}

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1725012345,
       "model":"gpt-4o-mini","choices":[{"index":0,"delta":{"content":"好"},"finish_reason":null}]}

...

data: {"id":"chatcmpl-xxx","object":"chat.completion.chunk","created":1725012345,
       "model":"gpt-4o-mini","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

### 关键点

| 字段 | 含义 |
|------|------|
| `choices[0].delta.content` | 本次新增的文本片段（要累积） |
| `choices[0].delta.role` | 仅第一条 chunk 有 |
| `choices[0].finish_reason` | 最后一 chunk 有 |
| `[DONE]` | 流结束标记 |

## 📡 Anthropic 流式响应

Anthropic 的 SSE 事件类型更丰富：

```
event: message_start
data: {"type":"message_start","message":{"id":"msg_xxx","role":"assistant","content":[],"usage":{"input_tokens":25}}}

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}

event: ping

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"你"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"好"}}

event: content_block_stop
data: {"type":"content_block_stop","index":0}

event: message_delta
data: {"type":"message_delta","delta":{"stop_reason":"end_turn"},"usage":{"output_tokens":12}}

event: message_stop
data: {"type":"message_stop"}
```

### 事件类型

| 事件 | 说明 |
|------|------|
| `message_start` | 流开始（包含 input_tokens） |
| `content_block_start` | 一个内容块开始（text / tool_use / thinking） |
| `content_block_delta` | 内容块增量 |
| `content_block_stop` | 内容块结束 |
| `message_delta` | 顶层字段更新（如 stop_reason、output_tokens） |
| `message_stop` | 流结束 |
| `ping` | 保活（防超时） |
| `error` | 错误 |

## 🧪 Python 流式接收示例

### OpenAI

```python
from openai import OpenAI

client = OpenAI()
stream = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "讲个笑话"}],
    stream=True,
)

full_text = ""
for chunk in stream:
    delta = chunk.choices[0].delta.content
    if delta:
        full_text += delta
        print(delta, end="", flush=True)
print()
```

### Anthropic

```python
import anthropic

client = anthropic.Anthropic()
with client.messages.stream(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "讲个笑话"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

## 🔧 实战注意事项

### 1. 增量累积（必须）

不能直接打印整个 chunk，因为每个 chunk 只是片段：

```python
# ❌ 错误：每次都打印整段
for chunk in stream:
    print(chunk.choices[0].delta.content)

# ✅ 正确：累积再打印
buf = ""
for chunk in stream:
    if chunk.choices[0].delta.content:
        buf += chunk.choices[0].delta.content
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 2. Tool Calls 拼接（OpenAI 流式）

Tool call 的 `arguments` 是字符串片段，需逐 chunk 拼接：

```python
tool_calls = {}
for chunk in stream:
    for tc in chunk.choices[0].delta.tool_calls or []:
        idx = tc.index
        if idx not in tool_calls:
            tool_calls[idx] = {"name": "", "args": ""}
        if tc.function.name:
            tool_calls[idx]["name"] += tc.function.name
        if tc.function.arguments:
            tool_calls[idx]["args"] += tc.function.arguments
# 最后 json.loads(tool_calls[i]["args"])
```

### 3. 网络中断重连

SSE 不支持断点续传，需重新发起请求：

```python
def stream_with_retry(messages, max_retry=3):
    for attempt in range(max_retry):
        try:
            stream = client.chat.completions.create(..., stream=True)
            for chunk in stream:
                yield chunk
            return  # 成功
        except (httpx.ReadError, httpx.RemoteProtocolError):
            if attempt == max_retry - 1: raise
            time.sleep(2 ** attempt)  # 指数退避
```

### 4. 浏览器前端（EventSource）

```javascript
const evtSource = new EventSource("/api/chat?prompt=hi");
evtSource.onmessage = (e) => {
  const data = JSON.parse(e.data);
  if (data.done) {
    evtSource.close();
    return;
  }
  document.getElementById("output").textContent += data.content;
};
evtSource.onerror = () => evtSource.close();
```

### 5. VitePress / Node 端

VitePress 是 SSR，**不能**用浏览器 EventSource。需直接 fetch + ReadableStream：

```javascript
const response = await fetch("/api/chat", {method: "POST", body: JSON.stringify(req)});
const reader = response.body.getReader();
const decoder = new TextDecoder();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const chunk = decoder.decode(value);
  // chunk 是 "data: {...}\n\n" 格式
  const lines = chunk.split("\n").filter(l => l.startsWith("data: "));
  for (const line of lines) {
    const data = JSON.parse(line.slice(6));
    console.log(data);
  }
}
```

## 🔗 关联章节

- [context-tokens](./context-tokens) - 流式场景下的 Token 统计
- [rate-limit-retry](./rate-limit-retry) - 流式断流的错误码
- [tool-use-protocol](./tool-use-protocol) - 流式 Tool Use 块拼接
