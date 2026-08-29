---
title: 高频面试题
date: 2026-08-15  # date-auto-injected
---

# AI 工程高频面试题

> 真实面试 + 笔试常见题汇总。

## 🟢 Easy（基础）

### 1. Transformer 是什么？为什么 LLM 基于它？

```
Transformer = 注意力机制 + 前馈网络 + 残差 + 层归一化
  注意力：每个 token 都能"看到"所有其他 token
  并行：不像 RNN 必须串行
  → 解决了 RNN 长依赖 + 慢训练的问题
  → 几乎所有现代 LLM 都基于 Transformer
```

### 2. 解释 Self-Attention

```
Q = X @ W_Q      (d × d_q)
K = X @ W_K
V = X @ W_V

Attention(Q, K, V) = softmax(Q @ K.T / sqrt(d_k)) @ V
```

每步：
1. 把输入 X 投影成 Q、K、V
2. Q 和 K.T 算相似度 → softmax → 注意力分数
3. 用分数加权 V → 输出

**Self** = Q K V 都来自**同一个**输入。

### 3. RAG 是什么？什么时候用？

```
Retrieval-Augmented Generation：
  1. 用户 query
  2. 向量库检索 top-k 相关文档
  3. 把文档塞进 prompt
  4. LLM 基于文档生成

用：
  ✅ 私有数据（公司 wiki / 内部知识）
  ✅ 实时信息（最新新闻）
  ✅ 减少幻觉（答案有据可查）
  ❌ 通用知识（LLM 已经会）
  ❌ 需要复杂推理（多步规划）
```

### 4. 什么是 Embedding？

把文本 / 图 / 音 → 固定维度向量（e.g. 1536 维）。**语义相似 = 向量接近**。

```python
# OpenAI
emb = openai.embeddings.create(
    model="text-embedding-3-small",
    input="你好"
).data[0].embedding
# list of 1536 floats
```

**不是单词的 hash，而是语义的几何**。

### 5. Function Calling 是什么？

让 LLM 决定**调哪个函数 / 传什么参数**，应用执行，结果喂回。

```
Q: 北京天气？ → LLM: 调 get_weather(city="北京")
                  → app 调 API → "25°C 晴"
                  → 喂回 LLM → "北京今天 25°C 晴"
```

详见 [Function Calling](/11-tools/function-calling)。

## 🟡 Medium（工程）

### 6. CoT / ReAct / Tool use 区别？

| | CoT | ReAct | Tool use |
|--|-----|-------|----------|
| 思维 | ✅ | ✅ | ✅ |
| 行动 | ❌ | ✅ | ✅ |
| 单步 | ✅ | 多步 | 多步 |
| 例子 | 算数学 | 查资料 + 答 | 调 API |

### 7. 怎么减少 LLM 幻觉？

```python
1. RAG（用真实文档）
2. CoT（让模型展示推理）
3. Self-consistency（多次采样 + 投票）
4. Low temperature（greedy 解码）
5. System prompt 加"不确定就说不确定"
6. 工具调用（让模型查实时）
7. 事实性评估（Faithfulness / RAGAS）
```

### 8. 怎么部署 100B 模型到生产？

```
1. 量化：INT8 / INT4（GGUF / AWQ / GPTQ）
2. 推理框架：vLLM / TGI / LMDeploy
3. 分布式：tensor parallel / pipeline parallel（多 GPU / 多机）
4. 缓存：prompt cache（前缀复用）
5. 监控：latency / QPS / cost
6. 容量规划：QPS × latency × 显存
```

### 9. 怎么选 embedding 模型？

| 场景 | 选 |
|------|-----|
| 通用 / 英文 | text-embedding-3-small |
| 质量优先 | Voyage-3 / text-embedding-3-large |
| **中文** | **BGE-M3**（开源 / 中文 SOTA） |
| 多语言 | Cohere embed-multilingual-v3 |
| 离线 / 隐私 | BGE-M3 / all-MiniLM（本地） |
| 图像 / 多模态 | CLIP / SigLIP |

### 10. Prompt cache 怎么省成本？

```python
# Claude
msg = client.messages.create(
    model="claude-sonnet-4-5",
    system=[
        {"type":"text","text":"<50KB 文档>","cache_control":{"type":"ephemeral"}}
    ],
    messages=[...]
)
# 同样 system 重复 → 命中 cache → 省 90% input cost
```

**适合**：system prompt 长 + 重复调用。

### 11. 微调 vs RAG 选哪个？

| 场景 | 选 |
|------|-----|
| 知识更新 / 私有 | **RAG**（便宜 / 实时） |
| 学风格 / 学任务 | **微调** |
| 数据 < 10k | LoRA |
| 数据 > 100M | 全量微调 / 继续预训练 |
| 显存紧 | QLoRA / 量化模型 |
| 实时 | RAG |

**实际：RAG + 微调结合**。

### 12. Function Calling 错误处理

```python
try:
    result = get_weather(**args)
except Exception as e:
    # 1. 重试
    for _ in range(3):
        try: result = get_weather(**args); break
        except: time.sleep(1)
    # 2. 失败时把错误喂回 LLM
    messages.append({"role":"tool","tool_call_id":call.id,"content":f"Error: {e}"})
    # LLM 自己判断下一步（重试 / 放弃 / 换工具）
```

### 13. MCP 是什么？跟 Function Calling 区别？

```
Function Calling：协议（每家 LLM 自己实现）
MCP：标准 + 生态 + 工具市场

MCP = Function Calling 标准化版
  - 一次实现，所有 agent 都能用
  - 工具市场（MCP Server Hub）
  - 鉴权 / 状态 / 资源等
```

## 🟠 Hard（系统设计）

### 14. 设计一个 RAG 系统

```
1. 需求
   - 文档量 / 更新频率 / QPS / 延迟

2. 数据流
   文档 → 切片（500-1000 token）→ Embedding → 向量库
   query → Embedding → top-k 检索 → rerank → LLM

3. 选型
   - 切片：RecursiveCharacterTextSplitter
   - Embedding：BGE-M3 / text-embedding-3
   - 向量库：Qdrant / Milvus / Pinecone
   - 检索：dense + sparse + rerank
   - LLM：Claude 4.5 / GPT-4o

4. 关键设计
   - Parent-doc retriever（小 chunk + 返回大 block）
   - HyDE（query 太短时让 LLM 写假想答案）
   - Self-RAG（LLM 自己判断要不要检索）
   - Multi-query（一个问题多角度）
   - Re-ranking（cross-encoder）

5. 评估
   - RAGAS：faithfulness / context_recall / answer_relevancy
   - 内部评估集（100-500 条）
   - 人工 review
```

### 15. 设计一个 Agent 系统

```
1. 场景
   - 多步任务 / 工具调用 / 状态管理

2. 选框架
   - LangGraph（生产首选）
   - CrewAI（快速 demo）
   - AutoGen（研究）

3. 核心组件
   - State：消息 / 内存 / 工具结果
   - Node：LLM 调用 / 工具执行 / 决策
   - Edge：条件路由
   - Checkpointer：持久化（Redis / PG）

4. 模式
   - ReAct：通用
   - Plan-and-Execute：复杂任务
   - Multi-agent：研究 / 写作 / 审核

5. 工具设计
   - 清晰的 description（LLM 才知道何时用）
   - 边界（不要 / 必须）
   - 错误处理
   - 限速 / 超时

6. 评估
   - 任务成功率
   - 步骤数 / 成本
   - 工具调用准确率
   - 用户反馈
```

### 16. 设计 LLM 成本优化

```
1. 模型选型（小模型优先）
2. Prompt 优化（精简 + 缓存）
3. max_tokens 限制
4. 缓存（重复 query / prefix cache）
5. 限速（防 abuse）
6. 监控 + 告警
7. 路由（小模型 → 大模型 fallback）
```

## 🔗 下一步

- [项目案例](/14-interview/cases)
- [学习路径](/14-interview/path)
- [RAG 模式详解](/05-rag/patterns)
- [LangGraph](/04-agents/langgraph)