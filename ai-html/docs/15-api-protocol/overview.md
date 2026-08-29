---
title: 大模型 API 协议全景
date: 2026-08-29  # date-auto-injected
---

# 🌐 大模型 API 协议全景

> 从一个 HTTP 请求出发，看大模型 API 是怎么把"提示词"变成"回答"的。

## 🔁 调用流程

```
┌─────────────┐     HTTP POST      ┌──────────────┐
│   Client    │ ─────────────────▶ │  API Gateway │
│ (SDK/CLI)   │                    │  (推理服务)  │
└─────────────┘                    └──────────────┘
       ▲                                  │
       │  SSE / JSON                       │ 排队
       │                                  ▼
       │                          ┌──────────────┐
       └─────────────────────────│   LLM 推理   │
                                  │ (vLLM/TGI)   │
                                  └──────────────┘
```

## 📋 协议栈分层

| 层 | 协议 | 说明 |
|---|------|------|
| **传输层** | HTTPS / HTTP/2 / gRPC | 主流 HTTPS，少量厂商支持 gRPC |
| **消息格式** | JSON（REST） / Protobuf（gRPC） | OpenAI / Anthropic 用 JSON |
| **认证** | Bearer Token / API Key | `Authorization: Bearer sk-xxx` |
| **流式输出** | Server-Sent Events (SSE) | `Content-Type: text/event-stream` |
| **工具调用** | JSON Schema / Tool Use 协议 | OpenAI `tools[]` / Anthropic `tools[]` |
| **结构化输出** | JSON Mode / Tool Use Mode | 强制模型输出合法 JSON |

## 🏗️ 主流厂商对比

| 厂商 | 端点风格 | 特色 |
|------|---------|------|
| **OpenAI** | `POST /v1/chat/completions` | 行业事实标准，Tool Use / JSON Mode |
| **Anthropic** | `POST /v1/messages` | 系统提示分离 + 思维链可见 |
| **Google Gemini** | `POST /v1beta/models/{model}:generateContent` | 多模态原生（图片/PDF/音频） |
| **DeepSeek** | 兼容 OpenAI | 国内可用，价格低 |
| **Ollama（本地）** | `POST /api/chat` | 完全本地，OpenAI 兼容 |
| **vLLM / TGI** | OpenAI 兼容 | 自托管推理服务 |

## 📐 通用请求结构

虽然各家 API 不一样，但核心字段相似：

```json
{
  "model": "claude-sonnet-4-5",
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "temperature": 0.7,
  "max_tokens": 1024,
  "stream": false,
  "tools": [...],
  "response_format": {...}
}
```

## 🔑 关键差异点

1. **system 提示位置**：OpenAI 放 messages 第一条，Anthropic 独立 `system` 字段
2. **多模态**：Gemini 原生支持图片/PDF，OpenAI/Anthropic 需 `image_url` 类型
3. **工具调用响应**：OpenAI 用 `tool_calls`，Anthropic 用 `tool_use` 内容块
4. **思维链**：Anthropic 默认返回 `thinking` 块，OpenAI 用 o1 推理模型
5. **流式块格式**：各家 SSE event 不同（详见 [streaming-protocol](./streaming-protocol)）

## 🔗 进入详细章节

- [chat-completions-api](./chat-completions-api) - OpenAI 标准协议详解
- [messages-api](./messages-api) - Anthropic 协议详解
- [streaming-protocol](./streaming-protocol) - SSE 原理与各家差异
- [tool-use-protocol](./tool-use-protocol) - Tool Use 协议
- [structured-output](./structured-output) - JSON 模式
- [multimodal-input](./multimodal-input) - 多模态输入
- [context-tokens](./context-tokens) - Token 计算原理
- [rate-limit-retry](./rate-limit-retry) - 限流与重试
