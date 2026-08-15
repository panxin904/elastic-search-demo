"""Elasticsearch store for chunks.

Index mapping (compatible with ES 7.17.x):

    {
      "mappings": {
        "properties": {
          "text":       { "type": "text" },
          "embedding":  { "type": "dense_vector", "dims": <dim> },
          "source":     { "type": "keyword" },
          "chunk_id":   { "type": "keyword" },
          "page":       { "type": "integer" },
          "chunk_index":{ "type": "integer" }
        }
      }
    }

The hybrid query body is exposed via `build_hybrid_query` so it can be
unit-tested without a live cluster. RRF fusion is done client-side in
`hybrid_search` (ES 7.x doesn't have native RRF; ES 8.8+ does).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from notebooklm.ingestion.pipeline import EmbeddedChunk


@dataclass
class HybridHit:
    """One retrieved chunk with its hybrid score."""

    chunk_id: str
    text: str
    source: str
    score: float
    page: int | None = None
    chunk_index: int | None = None
    metadata: dict[str, Any] | None = None


def build_hybrid_query(query: str, embedding: list[float], top_k: int) -> dict[str, Any]:
    """Construct the ES request body for hybrid retrieval.

    Uses ``bool.must`` (BM25) + ``knn`` section. RRF fusion is applied
    client-side by `EsStore.hybrid_search` because ES 7.x has no native
    RRF operator (added in 8.8).
    """
    return {
        "size": top_k,
        "query": {
            "bool": {
                "must": [{"match": {"text": query}}],
            }
        },
        "knn": {
            "field": "embedding",
            "query_vector": embedding,
            "k": top_k,
            "num_candidates": max(top_k * 5, 50),
            "similarity": "cosine",
        },
    }


class EsStore:
    """Thin wrapper over the official `elasticsearch` Python client."""

    def __init__(
        self,
        es_url: str,
        index: str = "notebooklm_chunks",
        embedding_dim: int = 768,
    ) -> None:
        self._es = Elasticsearch(es_url)
        self._index = index
        self._dim = embedding_dim

    @property
    def index(self) -> str:
        return self._index

    def ensure_index(self) -> None:
        """Create the index with our mapping if it doesn't exist."""
        if self._es.indices.exists(index=self._index):
            return
        self._es.indices.create(
            index=self._index,
            body={
                "mappings": {
                    "properties": {
                        "text": {"type": "text"},
                        "embedding": {
                            "type": "dense_vector",
                            "dims": self._dim,
                        },
                        "source": {"type": "keyword"},
                        "chunk_id": {"type": "keyword"},
                        "page": {"type": "integer"},
                        "chunk_index": {"type": "integer"},
                    }
                }
            },
        )

    def delete_index(self) -> None:
        """Drop the index (test helper)."""
        if self._es.indices.exists(index=self._index):
            self._es.indices.delete(index=self._index)

    def index_chunks(self, chunks: list[EmbeddedChunk]) -> int:
        """Bulk-index a batch of chunks. Returns the number indexed."""
        if not chunks:
            return 0
        actions = [
            {
                "_op_type": "index",
                "_index": self._index,
                "_id": c.id,
                "_source": {
                    "text": c.text,
                    "embedding": c.embedding,
                    "source": c.metadata.get("source", ""),
                    "chunk_id": c.id,
                    "page": c.metadata.get("page"),
                    "chunk_index": c.metadata.get("chunk_index"),
                },
            }
            for c in chunks
        ]
        success, _ = bulk(self._es, actions, refresh="wait_for")
        return success

    def bm25_search(self, query: str, top_k: int) -> list[HybridHit]:
        res = self._es.search(
            index=self._index,
            body={"size": top_k, "query": {"match": {"text": query}}},
        )
        return [_hit_to_hybrid(h) for h in res["hits"]["hits"]]

    def vector_search(
        self, embedding: list[float], top_k: int
    ) -> list[HybridHit]:
        res = self._es.search(
            index=self._index,
            body={
                "size": top_k,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.q, 'embedding') + 1.0",
                            "params": {"q": embedding},
                        },
                    }
                },
            },
        )
        return [_hit_to_hybrid(h) for h in res["hits"]["hits"]]

    def hybrid_search(
        self,
        query: str,
        embedding: list[float],
        top_k: int = 20,
        rrf_k: int = 60,
    ) -> list[HybridHit]:
        """Reciprocal Rank Fusion of BM25 + dense results."""
        bm25 = self.bm25_search(query, top_k)
        dense = self.vector_search(embedding, top_k)
        return _rrf_fuse(bm25, dense, k=rrf_k)[:top_k]

    def refresh(self) -> None:
        self._es.indices.refresh(index=self._index)


def _hit_to_hybrid(hit: dict[str, Any]) -> HybridHit:
    src = hit["_source"]
    return HybridHit(
        chunk_id=src.get("chunk_id", hit["_id"]),
        text=src.get("text", ""),
        source=src.get("source", ""),
        score=float(hit.get("_score") or 0.0),
        page=src.get("page"),
        chunk_index=src.get("chunk_index"),
        metadata=src,
    )


def _rrf_fuse(
    bm25: list[HybridHit], dense: list[HybridHit], k: int = 60
) -> list[HybridHit]:
    """Reciprocal Rank Fusion: score(d) = sum 1 / (k + rank) per list."""
    scores: dict[str, float] = {}
    by_id: dict[str, HybridHit] = {}
    for rank, hit in enumerate(bm25, start=1):
        scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1.0 / (k + rank)
        by_id[hit.chunk_id] = hit
    for rank, hit in enumerate(dense, start=1):
        scores[hit.chunk_id] = scores.get(hit.chunk_id, 0.0) + 1.0 / (k + rank)
        by_id.setdefault(hit.chunk_id, hit)

    fused: list[HybridHit] = []
    for cid, score in scores.items():
        hit = by_id[cid]
        fused.append(
            HybridHit(
                chunk_id=hit.chunk_id,
                text=hit.text,
                source=hit.source,
                page=hit.page,
                chunk_index=hit.chunk_index,
                metadata=hit.metadata,
                score=score,
            )
        )
    fused.sort(key=lambda h: h.score, reverse=True)
    return fused
