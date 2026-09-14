---
title: DeepSeek 经典架构
date: 2026-09-14  # date-auto-injected
---

# 🏛️ DeepSeek 经典架构

> 生产级 DeepSeek 落地的 8 种典型架构模式：从单点 API 到企业级 RAG 平台。

## 🏗️ 架构 1：单点 API（个人 / 小团队）

```
┌──────────┐    HTTPS    ┌──────────────────┐
│  App/Web  │ ─────────► │ api.deepseek.com │
└──────────┘             └──────────────────┘
                                  │
                                  ▼
                          DeepSeek-V3.2 / R1
```

**适用**：个人项目、原型验证、月调用 < 100 万 token

**配置**：
```python
client = OpenAI(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com/v1"
)
```

## 🏢 架构 2：自部署 + API 网关

```
┌──────────┐  HTTPS   ┌────────┐  HTTP   ┌────────────────┐
│  Client   │ ──────► │ Nginx  │ ──────► │ vLLM / SGLang │
└──────────┘          └────────┘         │   (GPU 集群)   │
                                          └────────────────┘
```

**适用**：企业内部服务、数据不出网

**组件**：
- Nginx：HTTPS 终结 + 反代 + 限流
- vLLM / SGLang：推理服务（多卡 MoE）
- Prometheus + Grafana：监控
- FastAPI：业务编排层

## 📚 架构 3：RAG 知识库平台

```
┌──────┐  ┌────────────┐  ┌────────┐  ┌────────┐
│ User │─►│  Web/API   │─►│ Router │─►│Retriever│
└──────┘  └────────────┘  └────┬───┘  └────┬───┘
                                │           │
                                ▼           ▼
                          ┌────────┐  ┌─────────────┐
                          │ DeepSeek│  │ Vector DB  │
                          │  LLM    │  │ (Chroma/    │
                          └────────┘  │  Milvus/    │
                                     │  ES)        │
                                     └─────────────┘
```

**关键组件**：
```python
# RAG 三段式：Retrieve → Augment → Generate
def rag(query):
    # 1. Retrieve（向量召回 + BM25 重排）
    docs = retriever.search(query, top_k=5)

    # 2. Augment（拼 prompt）
    context = "\n".join([f"[{i+1}] {d.content}" for i, d in enumerate(docs)])
    prompt = f"参考资料：\n{context}\n\n问题：{query}"

    # 3. Generate（DeepSeek）
    return deepseek.chat(prompt, citations=True)
```

## 🤖 架构 4：Multi-Agent 协作

```
┌─────────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐
│ Orchestrator│─►│ Planner  │─►│ Executor │─►│Reviewer│
└─────────────┘  └──────────┘  └────┬─────┘  └────┬───┘
                                     │             │
                                     ▼             ▼
                                 ┌────────┐    ┌─────────┐
                                 │Tools/MCP│   │Feedback │
                                 └────────┘    └─────────┘
```

**典型实现**：
- Planner：DeepSeek-V3（拆解需求）
- Executor：DeepSeek-V3 + Function Calling
- Reviewer：DeepSeek-R1（质量审查）
- Orchestrator：LangGraph / AutoGen

## 🛠️ 架构 5：Function Calling + MCP

```
┌──────────┐  tool_call  ┌─────────┐  HTTP  ┌──────────┐
│ DeepSeek │ ──────────► │ Tool    │ ─────► │ External │
│  Agent   │ ◄────────── │ Gateway │ ◄───── │ Service  │
└──────────┘   result    │ (MCP)   │ result └──────────┘
                          └─────────┘
                          │  │  │
                          ▼  ▼  ▼
                       [工具池]
                       ├ DB 查询
                       ├ API 调用
                       ├ 文件读写
                       └ 计算函数
```

**MCP Server 示例**：
```python
# mcp_server.py
from mcp.server import Server

app = Server("deepseek-tools")

@app.tool()
async def query_database(sql: str) -> str:
    """查询 PostgreSQL 数据库"""
    # 安全过滤 + 执行
    result = await db.execute(sql)
    return str(result)

@app.tool()
async def send_email(to: str, subject: str, body: str) -> bool:
    """发送邮件"""
    return await email_client.send(to, subject, body)
```

## 🌊 架构 6：流式 Web 助手

```
┌──────┐  POST /chat  ┌─────────┐  SSE   ┌──────────┐
│ Web  │ ───────────► │ FastAPI │ ─────► │ DeepSeek │
│      │ ◄─────────── │ (stream)│        │   API    │
└──────┘   EventStream └─────────┘        └──────────┘
                                              │
                  ┌────────────┐               │
                  │ Reasoning  │◄──────────────┘
                  │ Parser     │   (R1 thinking)
                  └────────────┘
```

**前端关键代码**：
```javascript
const evtSource = new EventSource(`/chat?msg=${encodeURIComponent(msg)}`);

let reasoning = "", answer = "";
evtSource.addEventListener("reasoning", e => {
    reasoning += JSON.parse(e.data).text;
    document.getElementById("thinking").textContent = reasoning;
});
evtSource.addEventListener("answer", e => {
    answer += JSON.parse(e.data).text;
    document.getElementById("answer").innerHTML = marked(answer);
});
```

## 🏛️ 架构 7：企业级 AI 中台

```
                        ┌──────────────────────────┐
                        │  AI Gateway (统一入口)   │
                        │  - 鉴权 / 计费 / 限流    │
                        │  - 模型路由              │
                        │  - 缓存                  │
                        └────────┬─────────────────┘
                                 │
        ┌────────────┬───────────┼───────────┬────────────┐
        ▼            ▼           ▼           ▼            ▼
   ┌─────────┐  ┌─────────┐ ┌────────┐ ┌──────────┐ ┌─────────┐
   │ DeepSeek│  │ Qwen    │ │ Claude │ │ GPT-5    │ │ Self-host│
   │  API    │  │  API    │ │  API   │ │  API     │ │ vLLM     │
   └─────────┘  └─────────┘ └────────┘ └──────────┘ └─────────┘
        │
        ▼
   ┌──────────────────────────────────────┐
   │  应用层                              │
   │  ├ 智能客服 (RAG + DeepSeek-V3)     │
   │  ├ 编程助手 (DeepSeek-Coder)        │
   │  ├ 数据分析 (DeepSeek-V3 + SQL Tool) │
   │  └ 文档问答 (RAG + DeepSeek-R1)     │
   └──────────────────────────────────────┘
```

**优势**：
- 模型可热切换（按 cost/quality 路由）
- 统一计费、监控、审计
- 缓存共享（节省 50%+ 成本）

## 🚀 架构 8：高并发生产部署

```
                          ┌─────────────┐
                          │ Load Balancer│
                          │   (LVS/F5)   │
                          └──────┬──────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
   ┌─────────┐              ┌─────────┐              ┌─────────┐
   │ vLLM #1 │              │ vLLM #2 │              │ vLLM #3 │
   │ V3-8卡  │              │ V3-8卡  │              │ V3-8卡  │
   │ (24 GPUs)              │ (24 GPUs)              │ (24 GPUs)│
   └─────────┘              └─────────┘              └─────────┘
        │                        │                        │
        └────────────────────────┼────────────────────────┘
                                 │
                          ┌──────┴──────┐
                          │  Redis      │
                          │ (Prefix Cache│
                          │  共享)       │
                          └─────────────┘
```

**关键优化**：
```bash
# 1. Prefix Cache（多个实例共享 KV cache）
vllm serve deepseek-ai/DeepSeek-V3 \
    --enable-prefix-caching \
    --num-gpu-blocks-override 80  # 占 80% 显存

# 3. Continuous Batching（动态调 batch）
# vLLM / SGLang 默认开启

# 4. Chunked Prefill（长 prompt 分块）
vllm serve ... --enable-chunked-prefill

# 5. Speculative Decoding（小模型 draft + 大模型 verify）
vllm serve deepseek-ai/DeepSeek-V3 \
    --speculative-model deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B \
    --num-speculative-tokens 5
```

## 📐 架构对比表

| 架构 | 适用 | 复杂度 | 成本 | 性能 |
|---|---|---|---|---|
| 1. 单点 API | 个人/小团队 | ⭐ | $ | ⭐⭐ |
| 2. 自部署+网关 | 企业内部 | ⭐⭐⭐ | $$$ | ⭐⭐⭐⭐ |
| 3. RAG 知识库 | 客服/文档 | ⭐⭐ | $$ | ⭐⭐⭐⭐ |
| 4. Multi-Agent | 复杂任务 | ⭐⭐⭐⭐ | $$ | ⭐⭐⭐ |
| 5. Function+MC | 工具集成 | ⭐⭐⭐ | $$ | ⭐⭐⭐⭐ |
| 6. 流式 Web | C 端产品 | ⭐⭐ | $ | ⭐⭐⭐⭐ |
| 7. AI 中台 | 大型企业 | ⭐⭐⭐⭐⭐ | $$$$ | ⭐⭐⭐⭐⭐ |
| 8. 高并发生产 | 互联网规模 | ⭐⭐⭐⭐⭐ | $$$$$ | ⭐⭐⭐⭐⭐ |

## 🛣️ 演进路径

```
Phase 1: 架构 1（API 验证）                  → 1 周
Phase 2: 架构 3（RAG 上线）                  → 2 周
Phase 3: 架构 6（流式 Web UI）               → 2 周
Phase 4: 架构 2（自部署，节省成本）          → 1 月
Phase 5: 架构 4（Multi-Agent，能力增强）     → 2 月
Phase 6: 架构 7（中台化，多模型）            → 3-6 月
Phase 7: 架构 8（高并发，亿级 QPS）          → 按需
```

## 📚 关键参考

```
DeepSeek-V3 论文       arxiv.org/abs/2412.19437
DeepSeek-R1 论文       arxiv.org/abs/2501.12948
DeepSeek-V3.2 技术博客  https://api-docs.deepseek.com/news/deepseek-v3-2-exp
vLLM 官方文档           docs.vllm.ai
SGLang 官方文档          docs.sglang.ai
LMDeploy 官方文档        github.com/InternLM/lmdeploy
MCP 协议规范            modelcontextprotocol.io
```
