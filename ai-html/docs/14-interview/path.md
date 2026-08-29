---
title: 学习路径
date: 2026-08-15  # date-auto-injected
---

# AI 工程学习路径

> 6 条路径，按角色和目标选。

## 🛤️ 路径 1：AI 应用开发者（1-2 周）

适合**刚开始 / 想做 AI 应用**的开发者。

1. [Claude 模型家族](/01-models/claude) — 最强闭源
2. [OpenAI SDK](/03-sdks/openai-sdk) — 主流接入
3. [OpenAI SDK](/03-sdks/openai-sdk) — 多家切换
4. [Claude Code / OpenCode](/02-coding-tools/claude-code) — 写代码 AI
5. [RAG 模式详解](/05-rag/patterns) — 让 LLM 知道私有数据
6. [Function Calling](/11-tools/function-calling) — 让 LLM 调 API
7. [API Key 管理](/13-security/api-keys) — 不泄露

**目标**：能用 OpenAI / Anthropic SDK 做一个带 RAG 的 Q&A 应用。

## 🛤️ 路径 2：Agent / 多 Agent 工程师（2-3 周）

适合**做 Agent / 复杂工具调用**的工程师。

- 完成"应用开发者"路径
- [LangGraph](/04-agents/langgraph) — **生产首选**框架
- [LangChain](/03-sdks/langchain) — LCEL 链式
- [Tool Use 模式](/11-tools/tool-use) — ReAct / Plan-Execute
- [MCP 核心概念](/06-mcp/core) — 工具调用新标准
- [MCP Server / Client 开发](/06-mcp/dev) — 写自己的 server
- [Structured Output](/11-tools/structured-output) — JSON 强约束
- [成本控制 / Token](/13-security/cost) — agent 容易烧钱

**目标**：能用 LangGraph + MCP 做一个生产可用的多 Agent 系统。

## 🛤️ 路径 3：RAG / 知识库工程师（2 周）

适合**做企业知识库 / 文档问答**。

- 完成"应用开发者"路径
- [RAG 模式详解](/05-rag/patterns) — 各种 RAG 模式
- [向量数据库](/05-rag/vector-db) — Qdrant / Milvus / pgvector
- [嵌入模型 Embedding](/05-rag/embedding) — BGE-M3 / OpenAI
- [MCP 核心概念](/06-mcp/core) — 检索 server 化
- [项目案例](/14-interview/cases) — 智能客服 / 知识库

**目标**：能设计 + 实现生产级 RAG 系统（含 rerank / hybrid / 评估）。

## 🛤️ 路径 4：算法 / 微调工程师（3-4 周）

适合**做模型微调 / 行业模型**。

- 完成"应用开发者"路径
- [DeepSeek](/01-models/deepseek) — 开源 MoE 之王
- [开源模型 Llama / Mistral](/01-models/open-source) — 各种开源
- [LoRA / QLoRA](/08-finetuning/lora) — 低成本微调
- [数据准备](/08-finetuning/data) — 怎么准备
- [量化 GGUF / GPTQ](/08-finetuning/quantization) — 模型压缩
- [vLLM / TGI 服务](/10-deploy/vllm-tgi) — 推理部署
- [CUDA / GPU 环境](/12-install/cuda-gpu) — 装 GPU
- [RLHF / DPO](/09-eval/alignment) — 对齐

**目标**：能在自己的数据上微调 + 量化 + 部署 + 评估。

## 🛤️ 路径 5：AI 平台 / SRE（3 周）

适合**做模型推理平台 / 内部 AI 基础设施**。

- 完成"应用开发者"路径
- [vLLM / TGI 服务](/10-deploy/vllm-tgi) — 高吞吐推理
- [Ollama 本地推理](/10-deploy/ollama) — 单机推理
- [API 托管](/10-deploy/hosted) — 多家对比
- [Docker 一键部署](/12-install/docker) — Ollama / vLLM / Dify
- [成本控制 / Token](/13-security/cost) — 路由 / 配额
- [Guardrails / Content Safety](/13-security/guardrails) — LiteLLM 代理
- [Eval 框架](/09-eval/frameworks) — 看质量

**目标**：能搭一个生产 LLM 网关（LiteLLM / Helicone / Portkey）。

## 🛤️ 路径 6：面试 / 跳槽（2-3 周）

适合**1-3 个月要面试 AI Engineer**。

- 复习 [Claude SDK](/03-sdks/claude-sdk) + [OpenAI SDK](/03-sdks/openai-sdk)
- 复习 [LangChain](/03-sdks/langchain) + [LangGraph](/04-agents/langgraph)
- 复习 [RAG 模式详解](/05-rag/patterns) + [MCP 核心概念](/06-mcp/core)
- 复习 [Function Calling](/11-tools/function-calling) + [Structured Output](/11-tools/structured-output)
- 复习 [LoRA / QLoRA](/08-finetuning/lora) + [量化 GGUF / GPTQ](/08-finetuning/quantization)
- 复习 [Ollama 本地推理](/10-deploy/ollama) + [vLLM / TGI 服务](/10-deploy/vllm-tgi)
- [高频面试题](/14-interview/questions) — 真实题 + 答案
- [项目案例](/14-interview/cases) — 面试可以讲的项目

**目标**：能讲清 LLM / RAG / Agent / 微调 / 部署的工程实现。

## 🎯 速查卡片

| 我想 | 推荐先看 |
|------|---------|
| 调 LLM | [OpenAI SDK](/03-sdks/openai-sdk) |
| 写代码 | [Claude Code / OpenCode](/02-coding-tools/claude-code) |
| 做 Agent | [LangGraph](/04-agents/langgraph) |
| 知识库 | [RAG 模式详解](/05-rag/patterns) |
| 工具调用 | [Function Calling](/11-tools/function-calling) |
| MCP | [MCP 核心概念](/06-mcp/core) |
| 跑本地 | [Ollama 本地推理](/10-deploy/ollama) |
| 微调 | [LoRA / QLoRA](/08-finetuning/lora) |
| 找工作 | [高频面试题](/14-interview/questions) |
| 看项目 | [项目案例](/14-interview/cases) |