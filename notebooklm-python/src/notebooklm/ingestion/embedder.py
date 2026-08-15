"""Embedding wrapper around sentence-transformers.

The first call to `Embedder(...)` loads the model into memory; subsequent
calls reuse the cached instance. This is the slowest step of the whole
pipeline (hundreds of MB for `multilingual-e5-base`), so we keep the
embedder a long-lived object.
"""
from __future__ import annotations

from sentence_transformers import SentenceTransformer


class Embedder:
    """Compute dense embeddings via sentence-transformers.

    Args:
        model_name: Any HF model supported by sentence-transformers
            (e.g. ``intfloat/multilingual-e5-base``). For e5 models the
            ``query:`` and ``passage:`` prefixes are added automatically.
        batch_size: Encoding batch size.
        device: ``cpu`` / ``cuda`` / ``mps``. ``None`` lets
            sentence-transformers pick.
    """

    def __init__(
        self,
        model_name: str = "intfloat/multilingual-e5-base",
        batch_size: int = 32,
        device: str | None = None,
    ) -> None:
        kwargs: dict[str, object] = {}
        if device is not None:
            kwargs["device"] = device
        self._model = SentenceTransformer(model_name, **kwargs)
        self._batch_size = batch_size
        self._is_e5 = "e5" in model_name.lower()
        self.dimension = self._model.get_embedding_dimension()
        assert isinstance(self.dimension, int)

    def _prefix(self, text: str, kind: str) -> str:
        if self._is_e5:
            return f"{kind}: {text}"
        return text

    def embed_query(self, text: str) -> list[float]:
        vec = self._model.encode(
            [self._prefix(text, "query")],
            batch_size=self._batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )[0]
        return vec.tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        prefixed = [self._prefix(t, "passage") for t in texts]
        vecs = self._model.encode(
            prefixed,
            batch_size=self._batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return [v.tolist() for v in vecs]
