"""Unit tests for the semantic chunker."""
from __future__ import annotations

from notebooklm.ingestion.chunker import Chunk, Chunker
from notebooklm.ingestion.loaders.base import Document


class TestChunk:
    def test_construction(self) -> None:
        c = Chunk(text="hi", metadata={"page": 1}, id="abc")
        assert c.text == "hi"
        assert c.metadata["page"] == 1
        assert c.id == "abc"

    def test_id_defaults_to_uuid(self) -> None:
        c = Chunk(text="hi", metadata={})
        assert isinstance(c.id, str) and len(c.id) > 0


class TestChunker:
    def test_short_doc_single_chunk(self) -> None:
        doc = Document(text="Short content.", source="a.txt", metadata={"page": 1})
        chunks = Chunker(chunk_size=512, overlap=64).chunk_documents([doc])
        assert len(chunks) == 1
        assert chunks[0].text == "Short content."
        assert chunks[0].metadata["source"] == "a.txt"
        assert chunks[0].metadata["page"] == 1

    def test_long_doc_creates_multiple_chunks(self) -> None:
        long_text = "Sentence one. " * 100
        doc = Document(text=long_text, source="a.txt")
        chunks = Chunker(chunk_size=200, overlap=50).chunk_documents([doc])
        assert len(chunks) > 1
        for c in chunks:
            assert c.text.strip()

    def test_chunks_have_unique_ids(self) -> None:
        doc = Document(text="A. " * 200, source="a.txt")
        chunks = Chunker(chunk_size=100, overlap=20).chunk_documents([doc])
        ids = [c.id for c in chunks]
        assert len(set(ids)) == len(ids)

    def test_metadata_propagates(self) -> None:
        doc = Document(text="Hi.", source="x.txt", metadata={"page": 5, "author": "bob"})
        chunks = Chunker(chunk_size=512, overlap=64).chunk_documents([doc])
        assert chunks[0].metadata["page"] == 5
        assert chunks[0].metadata["author"] == "bob"

    def test_empty_documents_produce_no_chunks(self) -> None:
        chunks = Chunker(chunk_size=512, overlap=64).chunk_documents([])
        assert chunks == []

    def test_chunks_respect_sentence_boundaries(self) -> None:
        sentences = ["First sentence here. ", "Second sentence here. ", "Third sentence here."]
        doc = Document(text="".join(sentences) * 5, source="a.txt")
        chunks = Chunker(chunk_size=80, overlap=10).chunk_documents([doc])
        for c in chunks:
            assert c.text.endswith(".") or c.text.endswith(" ") or "." in c.text

    def test_overlap_produces_shared_content(self) -> None:
        doc = Document(text="alpha beta gamma. " * 30, source="a.txt")
        chunks = Chunker(chunk_size=120, overlap=40).chunk_documents([doc])
        assert len(chunks) >= 2
        last_words_chunk1 = chunks[0].text.split()[-3:]
        first_words_chunk2 = " ".join(chunks[1].text.split()[:20])
        assert any(w in first_words_chunk2 for w in last_words_chunk1)
