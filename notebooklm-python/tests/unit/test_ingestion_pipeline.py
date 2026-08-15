"""Unit tests for the ingestion pipeline (load + chunk + embed)."""
from __future__ import annotations

from pathlib import Path

from notebooklm.ingestion.pipeline import IngestionPipeline


class _FakeEmbedder:
    def __init__(self, dim: int = 4) -> None:
        self.dimension = dim

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(t))] + [0.0] * (self.dimension - 1) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return [float(len(text))] + [0.0] * (self.dimension - 1)


class TestIngestionPipeline:
    def test_pipeline_produces_chunks_with_embeddings(self, tmp_path: Path) -> None:
        path = tmp_path / "doc.txt"
        path.write_text("First sentence. Second sentence. " * 20, encoding="utf-8")
        embedder = _FakeEmbedder()
        pipeline = IngestionPipeline(embedder=embedder, chunk_size=120, overlap=20)
        chunks = pipeline.ingest([path])
        assert len(chunks) > 1
        for c in chunks:
            assert c.embedding is not None
            assert len(c.embedding) == embedder.dimension
            assert c.metadata["source"] == str(path)

    def test_empty_input_returns_empty(self) -> None:
        pipeline = IngestionPipeline(embedder=_FakeEmbedder())
        assert pipeline.ingest([]) == []
