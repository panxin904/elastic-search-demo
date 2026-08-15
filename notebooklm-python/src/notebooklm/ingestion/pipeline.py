"""Top-level ingestion pipeline.

Coordinates the three ingestion steps:
1. Load each path with the appropriate loader (registry dispatch).
2. Chunk every loaded `Document` via the sentence-aware `Chunker`.
3. Embed all chunk texts in a single batched call.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from notebooklm.ingestion.chunker import Chunk, Chunker
from notebooklm.ingestion.embedder import Embedder
from notebooklm.ingestion.loaders.registry import load_any


class _EmbedderProto(Protocol):
    dimension: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]: ...


@dataclass
class EmbeddedChunk:
    """A `Chunk` plus its dense vector and a stable ES document id.

    The id is generated once and used as the ES `_id`, so re-running
    ingestion with the same chunk text is idempotent (we hash the text).
    """

    text: str
    metadata: dict[str, Any]
    id: str
    embedding: list[float] = field(default_factory=list)


class IngestionPipeline:
    def __init__(
        self,
        embedder: Embedder | _EmbedderProto,
        chunk_size: int = 512,
        overlap: int = 64,
    ) -> None:
        self._embedder = embedder
        self._chunker = Chunker(chunk_size=chunk_size, overlap=overlap)

    def ingest(self, paths: list[str | Path]) -> list[EmbeddedChunk]:
        documents = [doc for p in paths for doc in load_any(p)]
        chunks: list[Chunk] = self._chunker.chunk_documents(documents)
        if not chunks:
            return []
        embeddings = self._embedder.embed_documents([c.text for c in chunks])
        return [
            EmbeddedChunk(
                text=c.text,
                metadata=c.metadata,
                id=c.id,
                embedding=emb,
            )
            for c, emb in zip(chunks, embeddings, strict=True)
        ]
