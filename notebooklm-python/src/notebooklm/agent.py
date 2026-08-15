"""LangGraph-API factory entrypoint.

`langgraph dev` (from the `langgraph-api` package) imports the module
referenced in `langgraph.json` and calls the named attribute as a
factory. We expose an async `make_agent()` that:

1. Reads configuration from the environment (no globals, no import-time
   work).
2. Wires up a real `EsStore`, `Embedder`, `Reranker`, and `ChatProvider`
   — the same components our CLI uses.
3. Returns a compiled `Pregel` graph that langgraph-api can serve.

## Why the heavy models are singletons

`make_agent()` is invoked by langgraph-api **per request** (see
`langgraph_api/_factory_utils.py:invoke_factory`). Without caching, every
Studio tab / API call would re-instantiate `Embedder` and `Reranker`,
which forces `sentence-transformers` to re-validate the local HF cache
(HEAD requests to `huggingface.co/cross-encoder/...`) on each call —
that's the "constant HF traffic" symptom users see in dev.

The fix:
- `get_embedder()` and `get_reranker()` are module-level singletons,
  constructed once per process.
- `make_agent()` is itself a cache: the first call builds the compiled
  graph, every subsequent call returns the same object.
- `reset_caches()` exists for hot-reload: when source files change in
  `langgraph dev`, callers can wipe the cache and rebuild.

The compiled `Pregel` object is safe to share across requests because
langgraph-api injects a fresh `checkpointer` and per-thread state via
`_generate_graph` (see `langgraph_api/graph.py:342`).
"""
from __future__ import annotations

import asyncio
import os
from typing import Any


_embedder: Any | None = None
_reranker: Any | None = None
_agent: Any | None = None


def _require_es_url() -> str:
    es_url = os.environ.get("NOTEBOOKLM_ES_URL")
    if not es_url:
        raise RuntimeError(
            "NOTEBOOKLM_ES_URL is not set. "
            "Configure it in .env or the deployment environment."
        )
    return es_url


def _load_embedder() -> Any:
    from notebooklm.config import load_settings
    from notebooklm.ingestion.embedder import Embedder

    return Embedder(model_name=load_settings().embedding_model)


def _load_reranker() -> Any:
    from notebooklm.config import load_settings
    from notebooklm.retrieval.reranker import Reranker

    return Reranker(model_name=load_settings().reranker_model)


async def get_embedder() -> Any:
    """Return the process-wide Embedder singleton."""
    global _embedder
    if _embedder is None:
        _embedder = await asyncio.to_thread(_load_embedder)
    return _embedder


async def get_reranker() -> Any:
    """Return the process-wide Reranker singleton."""
    global _reranker
    if _reranker is None:
        _reranker = await asyncio.to_thread(_load_reranker)
    return _reranker


async def _build_graph():
    """Construct a fresh compiled graph using the cached singletons."""
    from notebooklm.config import load_settings
    from notebooklm.generation.llm_provider import get_provider
    from notebooklm.graph.graph import build_graph
    from notebooklm.retrieval.es_store import EsStore
    from notebooklm.retrieval.hybrid_retriever import Retriever

    settings = load_settings()
    es_url = _require_es_url()
    embedder = await get_embedder()
    store = EsStore(
        es_url=es_url,
        index=settings.es_index,
        embedding_dim=embedder.dimension,
    )
    retriever = Retriever(
        store=store,
        embedder=embedder,
        reranker=await get_reranker(),
        top_k=settings.top_k,
        top_n=settings.top_n,
    )
    provider = get_provider(settings.llm_provider)
    return build_graph(retriever, provider, max_retries=settings.max_retries)


async def make_agent() -> Any:
    """Build and return a compiled LangGraph agent for the API server.

    Cached: the first call constructs the graph, subsequent calls return
    the same compiled `Pregel`. Safe across requests because langgraph-api
    injects per-request checkpointer / store via `_generate_graph`.
    """
    global _agent
    if _agent is None:
        _agent = await _build_graph()
    return _agent


def reset_caches() -> None:
    """Drop the cached graph and model singletons.

    Useful for hot-reload scenarios where configuration has changed and
    we need a fresh build. Not called by langgraph-api automatically.
    """
    global _embedder, _reranker, _agent
    _embedder = None
    _reranker = None
    _agent = None
