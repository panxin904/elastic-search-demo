---
title: 学习路径
---

# 📖 AI 工程学习路径

> 根据你的角色选择对应路径。

## 🛤️ 路径 1：纯新手（1 周）

适合**没碰过大模型**的开发者。

1. [Claude 模型家族](/01-models/claude) — 当前最强闭源模型
2. [模型对比与选型](/01-models/compare) — 决定用哪个
3. [Claude Code / OpenCode](/02-coding-tools/claude-code) — AI 编程工具入门
4. [OpenAI SDK](/03-sdks/openai-sdk) — 最简单的 SDK
5. [Function Calling](/11-tools/function-calling) — LLM 调外部 API

**目标**：能用 OpenAI SDK 调 GPT-4，会用 Claude Code 写代码。

## 🛤️ 路径 2：应用开发者（2-3 周）

适合**做 AI 应用 / Agent 集成**的开发者。

- 完成"新手"路径
- [GPT / OpenAI](/01-models/gpt) — 最广泛使用
- [Claude SDK / Anthropic](/03-sdks/claude-sdk) — Claude SDK 接入
- [LangChain](/03-sdks/langchain) — 主流 LLM 框架
- [LangGraph](/04-agents/langgraph) — 现代 agent 框架
- [RAG 模式详解](/05-rag/patterns) — 检索增强
- [MCP 核心概念](/06-mcp/core) — 工具调用新范式
- [Tool Use 模式](/11-tools/tool-use) — Agent 与外部系统交互
- [Ollama 本地推理](/10-deploy/ollama) — 跑本地模型

**目标**：能用 LangChain + LangGraph 做一个 RAG + Tool use 的 Agent。

## 🛤️ 路径 3：Agent / 多 Agent 系统（3-4 周）

适合**做复杂 Agent / CrewAI / AutoGen**。

- 完成"应用开发者"路径
- [CrewAI](/04-agents/crewai) — 多 Agent 协作
- [AutoGen / Semantic Kernel](/04-agents/autogen) — Microsoft / 微软
- [MCP Server / Client 开发](/06-mcp/dev) — 给 Claude Code 写 MCP server
- [Codex MCP 集成](/06-mcp/codex-integration) — 在 OpenAI Codex 里用 MCP
- [结构化 Prompt](/07-prompt/structured) — 让 Agent 输出更稳定
- [API Key 管理](/13-security/api-keys) — 多 agent 共享 / 轮换
- [成本控制 / Token](/13-security/cost) — Agent 调一次花多少钱

**目标**：能设计 + 实现一个生产可用的多 Agent 系统。

## 🛤️ 路径 4：算法 / 微调（4-6 周）

适合**做模型训练 / RAG 优化**。

- 完成"应用开发者"路径
- [DeepSeek](/01-models/deepseek) — 当前最强开源 MoE
- [开源模型 Llama / Mistral](/01-models/open-source) — 自己跑 / 微调
- [LoRA / QLoRA](/08-finetuning/lora) — 低成本微调
- [数据准备](/08-finetuning/data) — 怎么准备训练集
- [量化 GGUF / GPTQ](/08-finetuning/quantization) — 模型量化部署
- [vLLM / TGI 服务](/10-deploy/vllm-tgi) — 高吞吐推理
- [RAG 模式详解](/05-rag/patterns) — 检索 / 重排 / 评估
- [向量数据库](/05-rag/vector-db) — Pinecone / Chroma / Weaviate
- [嵌入模型 Embedding](/05-rag/embedding) — 选对 Embedding
- [Eval 框架](/09-eval/frameworks) — 怎么评估效果

**目标**：能在自己的数据上微调 + 量化 + 部署 + 评估。

## 🛤️ 路径 5：面试 / 跳槽（2-3 周）

适合**1-3 个月内要面试 AI Engineer**。

- 复习 [Claude SDK / Anthropic](/03-sdks/claude-sdk) + [OpenAI SDK](/03-sdks/openai-sdk)
- 复习 [LangChain](/03-sdks/langchain) + [LangGraph](/04-agents/langgraph)
- 复习 [RAG 模式详解](/05-rag/patterns) + [MCP 核心概念](/06-mcp/core)
- 复习 [Function Calling](/11-tools/function-calling) + [Structured Output](/11-tools/structured-output)
- [高频面试题](/14-interview/questions) — 真实题 + 答案
- [项目案例](/14-interview/cases) — 面试可以讲的项目

**目标**：能讲清 LLM / RAG / Agent / 微调 / 部署的工程实现。

## 🎯 速查卡片

| 我想 | 推荐先看 |
|------|---------|
| 选模型 | [模型对比与选型](/01-models/compare) |
| 写代码 | [Claude Code / OpenCode](/02-coding-tools/claude-code) |
| 调 LLM | [OpenAI SDK](/03-sdks/openai-sdk) |
| 做 Agent | [LangGraph](/04-agents/langgraph) |
| RAG 系统 | [RAG 模式详解](/05-rag/patterns) |
| 工具调用 | [Function Calling](/11-tools/function-calling) |
| MCP 协议 | [MCP 核心概念](/06-mcp/core) |
| 跑本地模型 | [Ollama 本地推理](/10-deploy/ollama) |
| 微调 | [LoRA / QLoRA](/08-finetuning/lora) |
| 找工作 | [高频面试题](/14-interview/questions) |