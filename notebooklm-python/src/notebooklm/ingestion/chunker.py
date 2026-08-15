"""Sentence-aware semantic chunker.

A naive char-count splitter breaks mid-sentence and corrupts embeddings.
This chunker splits on sentence boundaries, then greedily packs sentences
into chunks of up to ``chunk_size`` characters, carrying the last
``overlap`` characters of each chunk forward as the seed of the next.
"""
from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from typing import Any

from notebooklm.ingestion.loaders.base import Document


@dataclass
class Chunk:
    """A single retrieval unit.

    Attributes:
        text: The chunk text (a sequence of whole sentences).
        metadata: Propagated from the source `Document`, plus chunk-local
            keys added by the chunker (``chunk_index``, ``source``).
        id: Stable identifier used as the ES doc id and in citation
            markers. Defaults to a fresh UUID4.
    """

    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


_SENTENCE_SPLIT = re.compile(r"(?<=[.!?。！？])\s+")


def _split_sentences(text: str) -> list[str]:
    text = text.strip()
    if not text:
        return []
    parts = _SENTENCE_SPLIT.split(text)
    return [p.strip() for p in parts if p.strip()]


class Chunker:
    """Sentence-aware chunker with character-budget packing and overlap.

    Args:
        chunk_size: Maximum characters per chunk (approximate; respects
            sentence boundaries, so the actual size may be slightly lower).
        overlap: Number of characters from the tail of one chunk to seed
            the next. Overlap helps preserve context across boundaries.
    """

    def __init__(self, chunk_size: int = 512, overlap: int = 64) -> None:
        if chunk_size <= 0:
            raise ValueError("chunk_size must be > 0")
        if overlap < 0 or overlap >= chunk_size:
            raise ValueError("overlap must be in [0, chunk_size)")
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk_documents(self, documents: list[Document]) -> list[Chunk]:
        chunks: list[Chunk] = []
        for doc in documents:
            chunks.extend(self._chunk_one(doc))
        return chunks

    def _chunk_one(self, doc: Document) -> list[Chunk]:
        sentences = _split_sentences(doc.text)
        if not sentences:
            return []

        base_meta = {"source": doc.source, **doc.metadata}
        out: list[Chunk] = []
        buffer: list[str] = []
        buffer_len = 0
        seed = ""

        for sentence in sentences:
            if buffer and buffer_len + len(sentence) + 1 > self._chunk_size:
                chunk_text = " ".join(buffer).strip()
                if seed and not chunk_text.startswith(seed):
                    chunk_text = (seed + " " + chunk_text).strip()
                out.append(
                    Chunk(
                        text=chunk_text,
                        metadata={**base_meta, "chunk_index": len(out)},
                    )
                )
                seed = chunk_text[-self._overlap :] if self._overlap else ""
                buffer = [sentence]
                buffer_len = len(sentence)
            else:
                buffer.append(sentence)
                buffer_len += len(sentence) + 1

        if buffer:
            chunk_text = " ".join(buffer).strip()
            if seed and not chunk_text.startswith(seed):
                chunk_text = (seed + " " + chunk_text).strip()
            out.append(
                Chunk(
                    text=chunk_text,
                    metadata={**base_meta, "chunk_index": len(out)},
                )
            )

        return out
