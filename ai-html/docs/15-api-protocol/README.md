---
title: API 协议与原理
date: 2026-08-29  # date-auto-injected
---

# 📡 API 协议与原理

> 深入理解大模型 API 的底层协议：HTTP REST 消息格式、SSE 流式原理、Tool Use 协议、多模态输入、Token 计算、限流与重试。本章聚焦"为什么这样设计"，而非"怎么调用"（用法见 03-sdks/）。

## 📚 本节目录

- [overview](./overview) - 大模型 API 协议全景图
- [chat-completions-api](./chat-completions-api) - OpenAI Chat Completions API 详解
- [messages-api](./messages-api) - Anthropic Messages API 协议
- [streaming-protocol](./streaming-protocol) - SSE 流式输出原理
- [tool-use-protocol](./tool-use-protocol) - Tool Use / Function Calling 协议
- [structured-output](./structured-output) - JSON Mode / Tool Use Mode 原理
- [multimodal-input](./multimodal-input) - Vision / Audio / File 输入协议
- [context-tokens](./context-tokens) - 上下文窗口与 Token 计算
- [rate-limit-retry](./rate-limit-retry) - 限流 / 重试 / 错误码

## 🎯 适合人群

- 想深入理解大模型 API 工作原理的工程师
- 正在做 SDK / Agent / RAG 框架的开发者
- 排查 API 异常（流中断、Token 超限、Tool 调用失败）
- 设计自己的模型路由 / 代理层

## 🔗 关联章节

- [03-sdks/](../03-sdks/claude-sdk) - SDK 用法（怎么调）
- [11-tools/](../11-tools/tool-use) - Tool Use 实战案例
- [13-security/api-keys](../13-security/api-keys) - API Key 安全

## 🚧 状态

本章按 §8.81 计划逐步完善，每篇配套可运行示例 + 协议抓包分析。
