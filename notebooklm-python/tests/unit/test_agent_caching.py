"""Tests for the cached agent factory.

`make_agent()` is called per-request by langgraph-api. It must:
- Build the graph once and reuse it across calls (avoid re-constructing
  heavy models like the embedding model and cross-encoder).
- Allow explicit invalidation when config changes (for hot-reload).
"""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest


class TestMakeAgentCaching:
    @pytest.mark.asyncio
    async def test_second_call_returns_same_graph(self) -> None:
        with (
            patch.dict(os.environ, {"NOTEBOOKLM_ES_URL": "http://fake:9200"}),
            patch("notebooklm.retrieval.es_store.EsStore") as mock_store,
            patch("notebooklm.ingestion.embedder.Embedder") as mock_embed,
            patch("notebooklm.retrieval.reranker.Reranker"),
            patch("notebooklm.generation.llm_provider.get_provider") as mock_get,
        ):
            mock_get.return_value.name = "openai"
            from notebooklm.agent import make_agent

            g1 = await make_agent()
            g2 = await make_agent()
            assert g1 is g2
            assert mock_store.call_count == 1
            assert mock_embed.call_count == 1

    @pytest.mark.asyncio
    async def test_heavy_models_are_singletons_across_reload(self) -> None:
        with (
            patch.dict(os.environ, {"NOTEBOOKLM_ES_URL": "http://fake:9200"}),
            patch("notebooklm.retrieval.es_store.EsStore"),
            patch("notebooklm.ingestion.embedder.Embedder") as mock_embed,
            patch("notebooklm.retrieval.reranker.Reranker") as mock_rerank,
            patch("notebooklm.generation.llm_provider.get_provider") as mock_get,
        ):
            mock_get.return_value.name = "openai"
            from notebooklm.agent import get_embedder, get_reranker, make_agent

            e1 = await get_embedder()
            e2 = await get_embedder()
            r1 = await get_reranker()
            r2 = await get_reranker()
            assert e1 is e2
            assert r1 is r2
            assert mock_embed.call_count == 1
            assert mock_rerank.call_count == 1

            g1 = await make_agent()
            g2 = await make_agent()
            assert mock_embed.call_count == 1
            assert mock_rerank.call_count == 1

    @pytest.mark.asyncio
    async def test_reset_clears_cache(self) -> None:
        with (
            patch.dict(os.environ, {"NOTEBOOKLM_ES_URL": "http://fake:9200"}),
            patch("notebooklm.retrieval.es_store.EsStore"),
            patch("notebooklm.ingestion.embedder.Embedder") as mock_embed,
            patch("notebooklm.retrieval.reranker.Reranker"),
            patch("notebooklm.generation.llm_provider.get_provider") as mock_get,
        ):
            mock_get.return_value.name = "openai"
            from notebooklm.agent import (
                get_embedder,
                make_agent,
                reset_caches,
            )

            await make_agent()
            assert mock_embed.call_count == 1
            reset_caches()
            await make_agent()
            assert mock_embed.call_count == 2
