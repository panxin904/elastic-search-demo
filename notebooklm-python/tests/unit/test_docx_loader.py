"""Unit tests for the DOCX loader."""
from __future__ import annotations

from pathlib import Path

import docx
import pytest

from notebooklm.ingestion.loaders.docx_loader import DocxLoader


def _write_docx(path: Path, paragraphs: list[str]) -> None:
    doc = docx.Document()
    for text in paragraphs:
        doc.add_paragraph(text)
    doc.save(str(path))


class TestDocxLoader:
    def test_loads_paragraphs(self, tmp_path: Path) -> None:
        path = tmp_path / "doc.docx"
        _write_docx(path, ["First paragraph", "Second paragraph"])
        docs = DocxLoader().load(path)
        assert len(docs) == 1
        assert "First paragraph" in docs[0].text
        assert "Second paragraph" in docs[0].text
        assert docs[0].source == str(path)

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            DocxLoader().load(tmp_path / "missing.docx")

    def test_empty_docx_returns_empty_list(self, tmp_path: Path) -> None:
        path = tmp_path / "empty.docx"
        _write_docx(path, [])
        assert DocxLoader().load(path) == []
