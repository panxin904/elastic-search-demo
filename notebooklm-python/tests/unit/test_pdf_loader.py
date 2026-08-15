"""Unit tests for the PDF loader."""
from __future__ import annotations

from pathlib import Path

import pypdf
import pytest

from notebooklm.ingestion.loaders.pdf_loader import PdfLoader


def _write_pdf_with_text(path: Path, pages: list[str]) -> None:
    """Build a tiny PDF where each page contains a known text string.

    Uses pypdf's high-level writer and a hand-rolled content stream so
    the test fixture doesn't depend on reportlab.
    """
    from pypdf.generic import (
        DecodedStreamObject,
        DictionaryObject,
        NameObject,
    )

    writer = pypdf.PdfWriter()
    for text in pages:
        page = writer.add_blank_page(width=300, height=300)
        # Build a content stream: "BT /F1 12 Tf 50 270 Td (text) Tj ET"
        escaped = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        content = f"BT /F1 12 Tf 50 270 Td ({escaped}) Tj ET"
        stream = DecodedStreamObject()
        stream.set_data(content.encode("latin-1"))
        page[NameObject("/Contents")] = stream
        # Add a resources dictionary with a font reference (required by some
        # PDF readers; harmless for pypdf).
        resources = DictionaryObject()
        font = DictionaryObject()
        font[NameObject("/BaseFont")] = NameObject("/Helvetica")
        font[NameObject("/Subtype")] = NameObject("/Type1")
        resources[NameObject("/Font")] = DictionaryObject({NameObject("/F1"): font})
        page[NameObject("/Resources")] = resources

    with path.open("wb") as fh:
        writer.write(fh)


class TestPdfLoader:
    def test_loads_single_page(self, tmp_path: Path) -> None:
        path = tmp_path / "single.pdf"
        _write_pdf_with_text(path, ["Hello PDF"])
        docs = PdfLoader().load(path)
        assert len(docs) == 1
        assert "Hello PDF" in docs[0].text
        assert docs[0].metadata.get("page") == 1
        assert docs[0].source == str(path)

    def test_loads_multiple_pages(self, tmp_path: Path) -> None:
        path = tmp_path / "multi.pdf"
        _write_pdf_with_text(path, ["Page one", "Page two", "Page three"])
        docs = PdfLoader().load(path)
        assert len(docs) == 3
        assert [d.metadata["page"] for d in docs] == [1, 2, 3]
        assert "Page one" in docs[0].text
        assert "Page two" in docs[1].text
        assert "Page three" in docs[2].text

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            PdfLoader().load(tmp_path / "nope.pdf")
