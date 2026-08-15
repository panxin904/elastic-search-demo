"""Cross-encoder reranker.

Takes the top-K hits from the hybrid retriever and rescores each
``(query, chunk_text)`` pair with a cross-encoder model. Cross-encoders
are slower than bi-encoders but far more accurate at the top of the
list, which is exactly what we need for the small final context the
LLM sees.
"""
from __future__ import annotations

from typing import Any

from notebooklm.retrieval.es_store import HybridHit


class Reranker:
    """Wrap a sentence-transformers CrossEncoder.

    Args:
        model_name: HF model name (e.g.
            ``cross-encoder/ms-marco-MiniLM-L-6-v2``). Only used when
            ``_encoder`` is None.
        _encoder: Optional injected cross-encoder (test seam).
    """

    def __init__(self, model_name: str, _encoder: Any | None = None) -> None:
        if _encoder is None:
            from sentence_transformers import CrossEncoder

            self._encoder = CrossEncoder(model_name)
        else:
            self._encoder = _encoder

    def rerank(
        self, query: str, hits: list[HybridHit], top_n: int
    ) -> list[HybridHit]:
        if not hits:
            return []
        pairs = [(query, h.text) for h in hits]
        scores = self._encoder.predict(pairs, show_progress_bar=False)
        scored = list(zip(hits, scores, strict=True))
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:top_n]
        out: list[HybridHit] = []
        for hit, s in top:
            out.append(
                HybridHit(
                    chunk_id=hit.chunk_id,
                    text=hit.text,
                    source=hit.source,
                    page=hit.page,
                    chunk_index=hit.chunk_index,
                    metadata=hit.metadata,
                    score=float(s),
                )
            )
        return out
