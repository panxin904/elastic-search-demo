"""Unit tests for the loader registry."""
from __future__ import annotations

from pathlib import Path

import pytest

from notebooklm.ingestion.loaders.registry import get_loader, load_any


class TestGetLoader:
    def test_txt_extension(self) -> None:
        loader = get_loader("a.txt")
        assert loader.__class__.__name__ == "TxtLoader"

    def test_md_extension(self) -> None:
        loader = get_loader("a.md")
        assert loader.__class__.__name__ == "MdLoader"

    def test_markdown_extension(self) -> None:
        loader = get_loader("a.markdown")
        assert loader.__class__.__name__ == "MdLoader"

    def test_pdf_extension(self) -> None:
        loader = get_loader("a.pdf")
        assert loader.__class__.__name__ == "PdfLoader"

    def test_docx_extension(self) -> None:
        loader = get_loader("a.docx")
        assert loader.__class__.__name__ == "DocxLoader"

    def test_url_dispatches_to_url_loader(self) -> None:
        loader = get_loader("https://example.com/x")
        assert loader.__class__.__name__ == "UrlLoader"

    def test_unsupported_extension_raises(self) -> None:
        with pytest.raises(ValueError):
            get_loader("a.xlsx")


class TestLoadAny:
    def test_loads_txt(self, tmp_path: Path) -> None:
        p = tmp_path / "a.txt"
        p.write_text("hi", encoding="utf-8")
        docs = load_any(p)
        assert len(docs) == 1
        assert docs[0].text == "hi"

    def test_unsupported_raises(self, tmp_path: Path) -> None:
        p = tmp_path / "a.xyz"
        p.write_text("data", encoding="utf-8")
        with pytest.raises(ValueError):
            load_any(p)
