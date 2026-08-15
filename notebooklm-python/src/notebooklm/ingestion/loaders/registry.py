"""Loader registry: maps file extensions / URL prefixes to the right loader.

Used by the CLI and ingestion pipeline so callers can pass a mixed bag of
paths and get a uniform list of `Document` objects back.
"""
from __future__ import annotations

from pathlib import Path

from notebooklm.ingestion.loaders.base import Document, DocumentLoader
from notebooklm.ingestion.loaders.docx_loader import DocxLoader
from notebooklm.ingestion.loaders.md_loader import MdLoader
from notebooklm.ingestion.loaders.pdf_loader import PdfLoader
from notebooklm.ingestion.loaders.txt_loader import TxtLoader
from notebooklm.ingestion.loaders.url_loader import UrlLoader


def _is_url(path: str | Path) -> bool:
    s = str(path)
    return s.startswith("http://") or s.startswith("https://")


def get_loader(path: str | Path) -> DocumentLoader:
    """Return the right loader for ``path``.

    For URLs, returns `UrlLoader`. For files, dispatches by extension.
    Raises `ValueError` for unsupported types — better to fail loudly than
    silently skip.
    """
    if _is_url(path):
        return UrlLoader()

    suffix = Path(path).suffix.lower()
    if suffix in {".txt", ""}:
        return TxtLoader()
    if suffix in {".md", ".markdown"}:
        return MdLoader()
    if suffix == ".pdf":
        return PdfLoader()
    if suffix == ".docx":
        return DocxLoader()
    raise ValueError(f"Unsupported file type: {path!r} (suffix: {suffix!r})")


def load_any(path: str | Path) -> list[Document]:
    """Convenience: pick loader + load in one call."""
    return get_loader(path).load(path)
