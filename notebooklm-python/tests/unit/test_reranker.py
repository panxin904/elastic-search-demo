"""Unit tests for the cross-encoder reranker."""
from __future__ import annotations

from notebooklm.retrieval.es_store import HybridHit
from notebooklm.retrieval.reranker import Reranker


class _FakeCrossEncoder:
    """Returns deterministic scores based on token overlap with the query."""

    def predict(self, pairs, show_progress_bar=False):  # type: ignore[no-untyped-def]
        results = []
        for query, doc in pairs:
            q_tokens = set(query.lower().split())
            d_tokens = set(doc.lower().split())
            results.append(float(len(q_tokens & d_tokens)))
        return results


class TestReranker:
    def test_rerank_returns_top_n(self) -> None:
        hits = [
            HybridHit(chunk_id=f"c{i}", text=f"doc {i}", source="a.txt", score=1.0 - i * 0.1)
            for i in range(5)
        ]
        reranker = Reranker(model_name="unused", _encoder=_FakeCrossEncoder())
        out = reranker.rerank("doc 2", hits, top_n=3)
        assert len(out) == 3

    def test_rerank_preserves_relevant_doc(self) -> None:
        hits = [
            HybridHit(chunk_id="a", text="the quick brown fox", source="a.txt", score=0.5),
            HybridHit(chunk_id="b", text="the lazy dog sleeps", source="a.txt", score=0.5),
            HybridHit(chunk_id="c", text="completely unrelated content here", source="a.txt", score=0.5),
        ]
        reranker = Reranker(model_name="unused", _encoder=_FakeCrossEncoder())
        out = reranker.rerank("fox quick", hits, top_n=2)
        assert out[0].chunk_id == "a"

    def test_empty_input(self) -> None:
        reranker = Reranker(model_name="unused", _encoder=_FakeCrossEncoder())
        assert reranker.rerank("query", [], top_n=5) == []

    def test_top_n_larger_than_input(self) -> None:
        hits = [HybridHit(chunk_id="x", text="x", source="a", score=0.1)]
        reranker = Reranker(model_name="unused", _encoder=_FakeCrossEncoder())
        out = reranker.rerank("q", hits, top_n=10)
        assert len(out) == 1
