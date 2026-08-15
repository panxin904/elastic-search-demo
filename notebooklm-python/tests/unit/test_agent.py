"""Unit tests for the langgraph-api agent factory.

`make_agent()` is an async factory that langgraph-api calls per request.
It must:
- Read credentials from env at call time (not import time), so the
  graph can be served even when ES/LLM aren't reachable.
- Return a compiled `Pregel` graph (what `build_graph()` returns).
- Build a working graph when ES URL and LLM key are set.
- Raise with a clear error if config is missing.
"""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest


class TestMakeAgent:
    @pytest.mark.asyncio
    async def test_returns_compiled_graph(self) -> None:
        with (
            patch.dict(os.environ, {"NOTEBOOKLM_ES_URL": "http://fake:9200"}),
            patch("notebooklm.retrieval.es_store.EsStore") as mock_store,
            patch("notebooklm.ingestion.embedder.Embedder") as mock_embed,
            patch("notebooklm.retrieval.reranker.Reranker"),
            patch("notebooklm.generation.llm_provider.get_provider") as mock_get,
        ):
            mock_get.return_value.name = "openai"
            mock_store.return_value.dummy = None
            from notebooklm.agent import make_agent

            graph = await make_agent()
            from langgraph.pregel import Pregel

            assert isinstance(graph, Pregel)
            assert mock_store.called
            assert mock_embed.called

    @pytest.mark.asyncio
    async def test_missing_es_url_raises(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "NOTEBOOKLM_ES_URL"}
        with patch.dict(os.environ, env, clear=True):
            from notebooklm.agent import make_agent

            with pytest.raises(RuntimeError, match="ES"):
                await make_agent()

    @pytest.mark.asyncio
    async def test_uses_env_provider(self) -> None:
        with (
            patch.dict(
                os.environ,
                {
                    "NOTEBOOKLM_ES_URL": "http://fake:9200",
                    "NOTEBOOKLM_LLM": "openai",
                    "OPENAI_API_KEY": "sk-fake",
                },
            ),
            patch("notebooklm.retrieval.es_store.EsStore"),
            patch("notebooklm.ingestion.embedder.Embedder"),
            patch("notebooklm.retrieval.reranker.Reranker"),
            patch("notebooklm.generation.llm_provider.get_provider") as mock_get,
        ):
            mock_get.return_value.name = "openai"
            from notebooklm.agent import make_agent

            await make_agent()
            mock_get.assert_called_once_with("openai")
