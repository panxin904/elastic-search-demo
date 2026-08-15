"""Integration tests for the ES store.

These tests spin up a real Elasticsearch container via testcontainers.
They are marked ``integration`` and will be skipped automatically if
Docker is not running on the host.
"""
from __future__ import annotations

import pytest
from testcontainers.elasticsearch import ElasticSearchContainer

from notebooklm.ingestion.pipeline import EmbeddedChunk
from notebooklm.retrieval.es_store import EsStore

ES_IMAGE = "docker.elastic.co/elasticsearch/elasticsearch:7.17.10"


@pytest.fixture(scope="module")
def es_url() -> str:
    """Start an Elasticsearch container and yield its URL.

    Skips the test if Docker is not available, so unit tests can still
    run on machines without a Docker daemon.
    """
    try:
        with ElasticSearchContainer(ES_IMAGE, mem_limit="1g") as es:
            yield es.get_url()
    except Exception as exc:  # pragma: no cover - depends on host env
        pytest.skip(f"Elasticsearch container not available: {exc}")


@pytest.fixture
def store(es_url: str) -> EsStore:
    s = EsStore(es_url=es_url, index="test_chunks", embedding_dim=4)
    s.delete_index()
    s.ensure_index()
    yield s
    s.delete_index()


def _chunk(text: str, source: str, emb: list[float], idx: int) -> EmbeddedChunk:
    return EmbeddedChunk(
        text=text,
        metadata={"source": source, "chunk_index": idx},
        id=f"{source}-{idx}",
        embedding=emb,
    )


@pytest.mark.integration
class TestEsStoreIntegration:
    def test_index_and_bm25_search(self, store: EsStore) -> None:
        chunks = [
            _chunk("The cat sat on the mat.", "a.txt", [1.0, 0.0, 0.0, 0.0], 0),
            _chunk("Dogs are loyal animals.", "b.txt", [0.0, 1.0, 0.0, 0.0], 0),
        ]
        store.index_chunks(chunks)
        store.refresh()
        hits = store.bm25_search("cat", top_k=5)
        assert len(hits) >= 1
        assert hits[0].text.startswith("The cat")

    def test_index_and_vector_search(self, store: EsStore) -> None:
        chunks = [
            _chunk("Vector A", "a.txt", [1.0, 0.0, 0.0, 0.0], 0),
            _chunk("Vector B", "b.txt", [0.0, 1.0, 0.0, 0.0], 0),
            _chunk("Vector C", "c.txt", [0.0, 0.0, 1.0, 0.0], 0),
        ]
        store.index_chunks(chunks)
        store.refresh()
        hits = store.vector_search([1.0, 0.0, 0.0, 0.0], top_k=2)
        assert len(hits) == 2
        assert hits[0].text == "Vector A"

    def test_hybrid_search_merges_both_signals(self, store: EsStore) -> None:
        chunks = [
            _chunk("Cats love fish", "a.txt", [0.9, 0.1, 0.0, 0.0], 0),
            _chunk("Cars are vehicles", "b.txt", [0.0, 0.9, 0.1, 0.0], 0),
            _chunk("Felines hunt mice", "c.txt", [0.7, 0.3, 0.0, 0.0], 0),
        ]
        store.index_chunks(chunks)
        store.refresh()
        hits = store.hybrid_search("cat", embedding=[0.85, 0.15, 0.0, 0.0], top_k=3)
        assert len(hits) >= 1
        # The "Cats love fish" chunk matches both text and vector; it should
        # rank highly.
        assert any("Cats" in h.text for h in hits)
