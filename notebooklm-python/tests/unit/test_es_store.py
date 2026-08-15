"""Unit tests for the ES store.

The hybrid query body is pure data construction, so we can unit-test it
without a live Elasticsearch. The full CRUD path is exercised by an
integration test that uses testcontainers (marked ``integration`` so it
can be skipped when Docker is unavailable).
"""
from __future__ import annotations

from notebooklm.retrieval.es_store import HybridHit, build_hybrid_query


class TestBuildHybridQuery:
    def test_returns_two_clauses(self) -> None:
        body = build_hybrid_query(query="hello world", embedding=[0.1] * 4, top_k=10)
        assert "query" in body
        # The query dict should combine BM25 + knn vector search.
        assert "bool" in body["query"]

    def test_top_k_propagates(self) -> None:
        body = build_hybrid_query(query="x", embedding=[0.0, 0.0], top_k=7)
        assert body["size"] == 7
        assert body["knn"]["k"] == 7

    def test_knn_includes_vector(self) -> None:
        emb = [0.5, -0.5, 0.25, 0.0]
        body = build_hybrid_query(query="x", embedding=emb, top_k=3)
        assert body["knn"]["query_vector"] == emb

    def test_knn_uses_cosine(self) -> None:
        body = build_hybrid_query(query="x", embedding=[0.0, 0.0], top_k=3)
        assert body["knn"]["similarity"] == "cosine"


class TestHybridHit:
    def test_construction(self) -> None:
        hit = HybridHit(
            chunk_id="abc",
            text="hello",
            source="a.txt",
            page=1,
            score=0.9,
        )
        assert hit.chunk_id == "abc"
        assert hit.score == 0.9
        assert hit.page == 1

    def test_optional_page_defaults_to_none(self) -> None:
        hit = HybridHit(chunk_id="abc", text="hi", source="x", score=0.1)
        assert hit.page is None
