"""Plain-text loader.

The simplest loader: read the file, strip trailing whitespace, return a
single Document. Multi-document text files are not in scope; a user with
multiple documents should put them in separate files.
"""
from __future__ import annotations

from pathlib import Path

from notebooklm.ingestion.loaders.base import Document


class TxtLoader:
    """Load a plain-text file as a single `Document`."""

    def load(self, path: str | Path) -> list[Document]:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        text = p.read_text(encoding="utf-8").rstrip()
        if not text.strip():
            return []
        return [Document(text=text, source=str(p), metadata={"path": str(p)})]
