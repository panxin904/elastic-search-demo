# NotebookLM Python

A LangGraph-based reconstruction of Google NotebookLM's core RAG
architecture, backed by Elasticsearch 7.x `dense_vector` and pluggable
LLM providers (OpenAI / Gemini / Ollama).

See [`notebooklm-python-design.md`](../notebooklm-python-design.md)
for the complete design and
[`../notebooklm_architecture.md`](../notebooklm_architecture.md) for
the source architecture analysis.

## Features (RAG core only)

- Multi-format document ingestion: PDF, DOCX, Markdown, plain text, URLs
- Semantic chunking with sentence-aware boundaries
- Local embeddings via `sentence-transformers` (default
  `intfloat/multilingual-e5-base`, 768-dim)
- Hybrid retrieval: BM25 + dense cosine similarity with RRF fusion
- Cross-encoder reranking (`cross-encoder/ms-marco-MiniLM-L-6-v2`)
- **Source-Grounding isolation**: answers strictly limited to retrieved context
- **Pointer-based citations**: `[source_N]` markers parsed into clickable cards
- Pluggable LLM providers: OpenAI, Gemini, Ollama
- LangGraph `StateGraph` orchestration with grounding validation loop

## Out of Scope

The Audio Overview (podcast) and Code Execution Sandbox described in
the source architecture are intentionally **not** implemented in this
version.

## Architecture

```
START → retrieve → generate → parse → validate
                                            ↓
                          (loop back to generate if !grounded)
                                            ↓
                                           END
```

Each step maps directly to a section of `notebooklm_architecture.md`:

| LangGraph Node | Architecture Doc Section |
|----------------|--------------------------|
| `retrieve`     | §2.2 RAG Engine          |
| `generate`     | §2.3 Gemini Core         |
| `parse`        | §2.3 Pointer Citations   |
| `validate`     | §2.1 Source-Grounding    |

## Quick Start

### 1. Install

```bash
cd notebooklm-python
uv sync --extra dev
cp .env.example .env
# Edit .env to add your LLM API key(s) and ES URL
```

### 2. Start Elasticsearch

Point at an existing ES 7.17+ cluster:

```bash
export NOTEBOOKLM_ES_URL=http://localhost:9200
```

Or run the integration tests with `testcontainers` (auto-spins up an
ES container, requires Docker):

```bash
uv run pytest tests/integration/ -m integration
```

### 3. Ingest documents

```bash
uv run notebooklm ingest ./sample_docs/
```

This will:
1. Load each file with the appropriate loader
2. Chunk each document (sentence-aware, 512 chars/chunk, 64 char overlap)
3. Embed each chunk with the configured model
4. Bulk-index everything into Elasticsearch

### 4. Query

```bash
uv run notebooklm query "How does LangGraph enforce source grounding?"
```

You'll see the answer followed by a citations table showing which
chunk each `[source_N]` marker points to.

## Switching LLM Providers

Set `NOTEBOOKLM_LLM` in your `.env`:

```env
NOTEBOOKLM_LLM=openai    # OpenAI
NOTEBOOKLM_LLM=gemini    # Google Gemini
NOTEBOOKLM_LLM=ollama    # Local Ollama (no API key needed)
```

The corresponding API keys (`OPENAI_API_KEY` / `GOOGLE_API_KEY`) must
be set, or the factory will refuse to construct the provider.

## Project Layout

```
notebooklm-python/
├── src/notebooklm/
│   ├── config.py                 # pydantic-settings
│   ├── ingestion/
│   │   ├── chunker.py            # sentence-aware splitter
│   │   ├── embedder.py           # sentence-transformers wrapper
│   │   ├── pipeline.py           # load + chunk + embed
│   │   └── loaders/              # txt, md, pdf, docx, url, registry
│   ├── retrieval/
│   │   ├── es_store.py           # ES dense_vector + RRF
│   │   ├── hybrid_retriever.py   # hybrid search + rerank
│   │   └── reranker.py           # cross-encoder wrapper
│   ├── generation/
│   │   ├── llm_provider.py       # factory
│   │   ├── providers/            # openai, gemini, ollama
│   │   ├── prompts.py            # Grounding system prompt
│   │   ├── citation_parser.py    # [source_N] extractor
│   │   └── types.py              # Message, ChatProvider protocol
│   ├── graph/
│   │   ├── state.py              # NotebookState (TypedDict)
│   │   ├── nodes.py              # retrieve, generate, parse, validate
│   │   └── graph.py              # StateGraph definition
│   └── cli/
│       └── app.py                # typer CLI: ingest / query
├── sample_docs/                  # ready-to-ingest sample files
└── tests/
    ├── unit/                     # 75+ unit tests
    └── integration/              # e2e (mock LLM) + testcontainers ES
```

## Testing

```bash
uv run pytest                       # everything (skips ES if no Docker)
uv run pytest -m "not integration"  # unit only
uv run pytest tests/integration/ -m integration   # needs Docker
```

## Design Decisions

- **Why RRF over native fusion?** ES 7.x has no native Reciprocal
  Rank Fusion operator (added in 8.8). We compute RRF client-side in
  Python so the code works on ES 7.17.x.
- **Why multilingual-e5-base?** Supports 100+ languages including
  Chinese, with a 768-dim embedding (compatible with `dense_vector`).
  The `query:` / `passage:` prefix protocol is applied automatically.
- **Why a custom citation parser?** The LLM is instructed to emit
  `[source_N]` markers. A small regex parser strips them, builds a
  clean text, and maps each marker to the corresponding chunk.
- **Why a validation loop?** Without it, the LLM can occasionally
  produce a fully-formed answer with zero citations. The validate
  node detects that and routes back to generate. After
  `max_retries` we accept the answer rather than loop forever.

## Limitations

- ES 7.x requires `cosineSimilarity` to be wrapped in `+ 1.0` in
  `script_score` to avoid negative scores. The store does this.
- LLM providers are not unit-tested against real APIs (would cost
  money and require keys). The factory and protocol are unit-tested
  with a mocked langchain client.
- The Grounding prompt is in Chinese because the original
  architecture doc is in Chinese.
