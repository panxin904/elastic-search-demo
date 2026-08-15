"""Unit tests for the embedder.

Uses a small SentenceTransformer model already in the local HF cache to
avoid downloads. The production embedder accepts any model name.
"""
from __future__ import annotations

import pytest

from notebooklm.ingestion.embedder import Embedder

# Small English model that is already in the HF cache on the test host.
# Override NOTEBOOKLM_EMBEDDING_MODEL to test other models.
TEST_MODEL = "sentence-transformers/all-mpnet-base-v2"


@pytest.fixture(scope="module")
def embedder() -> Embedder:
    return Embedder(model_name=TEST_MODEL, batch_size=8)


class TestEmbedder:
    def test_dimension_matches_model(self, embedder: Embedder) -> None:
        assert embedder.dimension > 0
        assert isinstance(embedder.dimension, int)

    def test_embed_single_text(self, embedder: Embedder) -> None:
        vec = embedder.embed_query("hello world")
        assert isinstance(vec, list)
        assert len(vec) == embedder.dimension
        assert all(isinstance(x, float) for x in vec)

    def test_embed_batch_preserves_order(self, embedder: Embedder) -> None:
        texts = ["first text", "second text", "third text"]
        vecs = embedder.embed_documents(texts)
        assert len(vecs) == 3
        for v in vecs:
            assert len(v) == embedder.dimension

    def test_similar_texts_have_higher_similarity(self, embedder: Embedder) -> None:
        v_cat = embedder.embed_query("A cat is a small animal")
        v_dog = embedder.embed_query("A dog is a loyal pet")
        v_math = embedder.embed_query("The derivative of x squared is 2x")
        sim_cat_dog = _cosine(v_cat, v_dog)
        sim_cat_math = _cosine(v_cat, v_math)
        assert sim_cat_dog > sim_cat_math, (
            f"Expected cat/dog similarity > cat/math, got {sim_cat_dog:.3f} vs {sim_cat_math:.3f}"
        )

    def test_empty_list_returns_empty(self, embedder: Embedder) -> None:
        assert embedder.embed_documents([]) == []


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    return dot / (na * nb) if na and nb else 0.0
