"""High-level retriever that combines hybrid search + cross-encoder rerank.

This is the entry point used by the LangGraph retrieval node.
"""
from __future__ import annotations

from notebooklm.ingestion.embedder import Embedder
from notebooklm.retrieval.es_store import EsStore, HybridHit
from notebooklm.retrieval.reranker import Reranker


class Retriever:
    """Hybrid search → rerank pipeline.

    Args:
        store: An `EsStore` with an existing index.
        embedder: An `Embedder` matching the index's vector dim.
        reranker: A `Reranker`. If None, the top_n pass-through is used.
        top_k: Candidates to recall from the hybrid search.
        top_n: Final chunks to return to the LLM.
    """

    def __init__(
        self,
        store: EsStore,
        embedder: Embedder,
        reranker: Reranker | None = None,
        top_k: int = 20,
        top_n: int = 5,
    ) -> None:
        self._store = store
        self._embedder = embedder
        self._reranker = reranker
        self._top_k = top_k
        self._top_n = top_n

    def retrieve(self, query: str) -> list[HybridHit]:
        q_vec = self._embedder.embed_query(query)
        candidates = self._store.hybrid_search(query, q_vec, top_k=self._top_k)
        if self._reranker is None:
            return candidates[: self._top_n]
        return self._reranker.rerank(query, candidates, top_n=self._top_n)
