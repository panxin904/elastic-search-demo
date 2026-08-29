---
title: Dify / Coze
date: 2026-08-15  # date-auto-injected
---

# Dify / Coze - 低代码 Agent 平台

> 两个**图形化** AI Agent 平台。**不用写代码**也能搭 agent / RAG / 工作流。

## 🤖 Dify（开源 / 自托管）

> Dify = 字节系（虽然不是字节）开源的 LLMOps 平台。**生成式 AI 应用 + 可视化工作流**。

### 安装

```bash
# Docker（推荐）
git clone https://github.com/langgenius/dify.git
cd dify/docker
cp .env.example .env
docker compose up -d
# http://localhost/install
```

### 核心能力

- **聊天 / Completion**：简单 LLM 应用
- **Agent**：ReAct / Function calling 拖拽搭建
- **Workflow**：画流程图（多节点：Datasource → LLM → Code → If-else）
- **RAG**：上传文档 → 自动切片 → Embedding → 检索
- **模型管理**：统一管理多个 Provider（OpenAI / Anthropic / Ollama）
- **工具 / 数据集 / API 集成**
- **观测**：日志 / 反馈 / 评估

### 典型工作流

```
1. 数据源（PDF / URL / Notion）→ 自动切片
2. Embedding（OpenAI / Cohere）→ 存向量库
3. 检索 top-k → 喂给 LLM
4. 输出 + 引用来源
```

画流程图就能搭。

### API

```bash
curl -X POST 'https://api.dify.ai/v1/chat-messages' \
  -H 'Authorization: Bearer {API_KEY}' \
  -H 'Content-Type: application/json' \
  -d '{
    "inputs": {},
    "query": "What is RAG?",
    "response_mode": "streaming",
    "user": "user-001"
  }'
```

## 🤖 Coze（字节跳动 / 扣子）

> 字节出的 AI agent 平台。**国内可用** + 与抖音 / 飞书深度集成。

- 官网：https://www.coze.cn
- 智能体搭建（拖拽）
- 知识库（上传文档 → RAG）
- 工作流
- 插件（API / 数据库 / 搜索）
- 多渠道发布（飞书 / 抖音 / 公众号）
- **Bot Store**：别人的 agent 拿来用

## 🆚 vs LangGraph

| | Dify / Coze | LangGraph |
|--|-------------|-----------|
| 形态 | **图形化** | 代码 |
| 适合 | 业务人员 / 快速搭 | 工程师 / 复杂 agent |
| 灵活 | 中 | 高 |
| 自托管 | Dify ✅ | ✅ |
| RAG | 拖拽 | 自己写 |
| 状态机 | 弱 | **强** |

## 🔗 下一步

- [LangGraph](/04-agents/langgraph)
- [RAG 模式详解](/05-rag/patterns)
- [LangChain](/03-sdks/langchain)