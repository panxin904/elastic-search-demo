# NotebookLM 架构复原 (LangGraph 版) — 设计方案

> **目标**：使用 LangGraph 框架复原 Google NotebookLM 的核心 RAG 架构，
> 落地为 `elastic-search-demo/notebooklm-python/` 子项目。
> **范围**：仅 RAG 核心（不含播客生成 / 代码沙箱）。
> **栈**：Python 3.13 + LangGraph + LangChain + Elasticsearch 7.17.10 (dense_vector) + sentence-transformers

---

## 1. 顶层架构（对齐 notebooklm_architecture.md §1）

```
┌────────────────────┐      ┌──────────────────────┐      ┌─────────────────────┐
│ 1. 数据摄入层       │ ───▶ │ 2. 检索增强引擎       │ ───▶ │ 3. Gemini 核心大模型  │
│                    │      │                      │      │                     │
│ • 文档解析器        │      │ • 混合检索 (BM25+vec) │      │ • 多提供商工厂        │
│ • 语义分块          │      │ • 交叉编码器重排       │      │ • Grounding 隔离提示  │
│ • Embedding (mE5)  │      │ • Top-K 召回          │      │ • 指针式引用生成      │
│ • ES dense_vector  │      │                      │      │                     │
└────────────────────┘      └──────────────────────┘      └─────────────────────┘
            ▲                                                      │
            │                                                      ▼
            │                  ┌──────────────────────┐      ┌─────────────────┐
            └────────────────  │  LangGraph StateGraph │ ◀─── │ 用户查询 CLI    │
                               │  (orchestration)     │      └─────────────────┘
                               └──────────────────────┘
```

**LangGraph StateGraph 节点流**：

```
START
  ↓
[analyze_query]  ← 解析查询意图、决定是否需要 RAG
  ↓
[hybrid_retrieve]  ← ES BM25 + dense 混合召回 Top-20
  ↓
[rerank]  ← 交叉编码器重排到 Top-5
  ↓
[grounded_generate]  ← 拼接 system prompt + context + query
  ↓                   ← 强制要求"未提及则答不知道"
[parse_citations]  ← 解析 `[source_n]` 标记，生成结构化引用
  ↓
[validate_grounding]  ← 校验回答是否每句都有引用；否则回到 [grounded_generate] 重试
  ↓
END
```

**关键设计点**：
- **Source-Grounding 隔离**：system prompt 明确禁止使用预训练知识，
  所有回答必须基于召回 chunks；未提及则必须回答"源文件中未提及"。
- **指针式引用**：LLM 在生成时输出 `[source_1] [source_2]` 标记，
  前端/CLI 解析为 `{chunk_id, source_file, page, text_snippet}` 卡片。
- **Grounding 校验循环**：重试最多 2 次，避免无限循环。

---

## 2. 项目结构

```
notebooklm-python/
├── pyproject.toml              # uv 管理
├── README.md
├── .env.example
├── src/notebooklm/
│   ├── __init__.py
│   ├── config.py               # pydantic-settings 配置
│   ├── ingestion/
│   │   ├── loaders/            # pdf, docx, md, url, txt
│   │   │   ├── base.py         # DocumentLoader 协议
│   │   │   ├── pdf_loader.py
│   │   │   ├── docx_loader.py
│   │   │   ├── md_loader.py
│   │   │   ├── url_loader.py   # trafilatura
│   │   │   └── txt_loader.py
│   │   ├── chunker.py          # 语义分块 (sentence-aware)
│   │   ├── embedder.py         # mE5 wrapper
│   │   └── pipeline.py         # 摄入编排
│   ├── retrieval/
│   │   ├── es_store.py         # ES dense_vector 封装
│   │   ├── hybrid_retriever.py # BM25 + dense + RRF 融合
│   │   └── reranker.py         # cross-encoder
│   ├── generation/
│   │   ├── llm_provider.py     # ChatProvider 协议 + 工厂
│   │   ├── providers/
│   │   │   ├── openai.py
│   │   │   ├── gemini.py
│   │   │   └── ollama.py
│   │   ├── prompts.py          # 系统提示词（Grounding 隔离）
│   │   └── citation_parser.py  # [source_n] 解析
│   ├── graph/
│   │   ├── state.py            # NotebookState (TypedDict)
│   │   ├── nodes.py            # 各节点实现
│   │   └── graph.py            # StateGraph 构建
│   └── cli/
│       └── app.py              # typer CLI
└── tests/
    ├── conftest.py             # testcontainers ES fixture
    ├── unit/
    │   ├── test_chunker.py
    │   ├── test_embedder.py
    │   ├── test_citation_parser.py
    │   └── test_llm_provider.py
    └── integration/
        ├── test_ingestion_pipeline.py
        ├── test_hybrid_retrieval.py
        ├── test_langgraph_flow.py
        └── test_grounding_isolation.py
```

---

## 3. 关键模块设计

### 3.1 ES 向量存储 (es_store.py)
- Index: `notebooklm_chunks`，mapping:
  - `text: text` (BM25)
  - `embedding: dense_vector[768]` (cosine)
  - `source: keyword` (文件名)
  - `chunk_id: keyword` (UUID)
  - `page: integer` / `timestamp: float` (元数据)
- **混合检索**：ES `multi_match` (BM25) + `script_score` (cosine) → RRF 融合

### 3.2 LLM Provider 工厂
```python
class ChatProvider(Protocol):
    def chat(self, messages: list[Message], **kw) -> str: ...

def get_provider(name: str) -> ChatProvider:
    if name == "openai": return OpenAIProvider()
    if name == "gemini": return GeminiProvider()
    if name == "ollama": return OllamaProvider()
```
通过 `NOTEBOOKLM_LLM` 环境变量切换。

### 3.3 Grounding System Prompt（核心）
```
你是 NotebookLM 助手。你必须只使用 <context> 标签内的源文件内容回答。
规则：
1. 回答中每个事实主张都必须有 <context> 中的原文支撑。
2. 在引用处插入 [source_N] 标记，N 是 context 块编号。
3. 若 <context> 没有相关信息，必须回答："源文件中未提及此内容。"
4. 严禁使用预训练知识、严禁编造。
```

### 3.4 测试策略 (TDD)
- **Unit**：纯函数（分块、citation 解析、prompt 构造）
- **Integration**：testcontainers-python 拉起 ES 7.17.10，验证完整流程
- **E2E**：用 mock LLM provider，跑通 LangGraph 状态机

---

## 4. 落地步骤 (Phase 顺序)

| Phase | 内容 | 验证方式 |
|---|---|---|
| 0 | uv init + 依赖 + .env.example | `uv sync` 成功 |
| 1 | Loaders (txt, md, pdf, docx, url) | unit: 各 loader 返回非空 Document |
| 2 | Chunker + Embedder | unit: 分块数量符合预期 |
| 3 | ES Store (CRUD + hybrid query) | integration: testcontainers |
| 4 | LLM Provider 工厂 | unit: mock API 验证 prompt |
| 5 | Hybrid Retriever + Reranker | integration: 召回 Top-5 |
| 6 | Citation Parser + Grounding Prompt | unit: 解析 `[source_1]` |
| 7 | LangGraph StateGraph 编排 | e2e: mock LLM 跑通 |
| 8 | CLI (typer) | 手动 E2E：摄入 PDF → 提问 → 拿引用 |
| 9 | README + 演示 | 文档完整 |

---

## 5. 关键风险与缓解

| 风险 | 缓解 |
|---|---|
| testcontainers 需要 Docker，本机可能没跑 | 提供 `NOTEBOOKLM_ES_URL` 环境变量，未设置则用 TC；两者都支持 |
| mE5 模型首次下载慢 | 离线缓存到 `~/.cache/huggingface`；README 说明 |
| LLM 假装引用（幻觉引用） | Citation Parser 校验 N 必须在 context 范围内；不合法则重试 |
| ES 7 dense_vector 限制 | 用 768 维（mE5-base），cosine similarity 在 7.6+ 支持 |
