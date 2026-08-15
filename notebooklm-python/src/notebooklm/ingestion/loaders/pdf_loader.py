"""PDF loader.

Each page becomes a separate `Document` with ``page`` in metadata. This
matches NotebookLM's behaviour: every page in a PDF is its own retrieval
unit, so the citation can point to a specific page.
"""
from __future__ import annotations

from pathlib import Path

import pypdf

from notebooklm.ingestion.loaders.base import Document


class PdfLoader:
    """Load a PDF, one `Document` per page."""

    def load(self, path: str | Path) -> list[Document]:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)

        reader = pypdf.PdfReader(str(p))
        docs: list[Document] = []
        for i, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:
                # Encrypted or malformed page: skip rather than abort the
                # whole ingestion.
                text = ""
            text = text.strip()
            if not text:
                continue
            docs.append(
                Document(
                    text=text,
                    source=str(p),
                    metadata={"path": str(p), "page": i, "total_pages": len(reader.pages)},
                )
            )
        return docs
