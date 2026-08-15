"""Unit tests for the base Document type and DocumentLoader protocol."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from notebooklm.ingestion.loaders.base import Document, DocumentLoader


class TestDocument:
    """Document is the canonical in-memory representation of a parsed source."""

    def test_minimal_construction(self) -> None:
        doc = Document(text="hello", source="a.txt")
        assert doc.text == "hello"
        assert doc.source == "a.txt"
        assert doc.metadata == {}

    def test_with_metadata(self) -> None:
        doc = Document(text="x", source="x.pdf", metadata={"page": 3, "author": "Alice"})
        assert doc.metadata["page"] == 3
        assert doc.metadata["author"] == "Alice"

    def test_metadata_defaults_to_empty_dict(self) -> None:
        # A loader that produces a Document without explicit metadata must not
        # see a mutable shared default (the classic Python gotcha).
        doc1 = Document(text="a", source="a.txt")
        doc2 = Document(text="b", source="b.txt")
        doc1.metadata["page"] = 1
        assert doc2.metadata == {}, "metadata must not be shared across instances"


class _RecordingLoader:
    """Minimal concrete loader used to validate the protocol shape."""

    def __init__(self, docs: list[Document]) -> None:
        self._docs = docs
        self.calls: list[Any] = []

    def load(self, path: str | Path) -> list[Document]:
        self.calls.append(path)
        return list(self._docs)


class TestDocumentLoaderProtocol:
    def test_protocol_accepts_any_load_method(self) -> None:
        loader: DocumentLoader = _RecordingLoader([Document("x", "x.txt")])
        result = loader.load("x.txt")
        assert len(result) == 1
        assert result[0].text == "x"

    def test_load_accepts_pathlib_path(self) -> None:
        loader: DocumentLoader = _RecordingLoader([])
        loader.load(Path("/tmp/example.txt"))
        assert loader.calls == [Path("/tmp/example.txt")]
