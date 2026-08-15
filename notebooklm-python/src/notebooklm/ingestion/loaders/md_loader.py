"""Markdown loader.

Strips Markdown formatting (headers, bold/italic, links, code fences)
before indexing. The retrieval step operates on the resulting plain text;
the original Markdown syntax is not relevant for semantic matching and
adds noise to embeddings.
"""
from __future__ import annotations

from pathlib import Path

import markdown

from notebooklm.ingestion.loaders.base import Document


class MdLoader:
    """Load a Markdown file, convert to plain text."""

    def load(self, path: str | Path) -> list[Document]:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(p)
        raw = p.read_text(encoding="utf-8")
        # Convert MD to HTML, then strip tags to plain text. The `markdown`
        # package defaults to all extensions we need.
        html = markdown.markdown(raw)
        # A minimal HTML stripper: drop tags. We deliberately keep the text
        # inside <code> blocks because code is semantically meaningful.
        import re

        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return []
        return [Document(text=text, source=str(p), metadata={"path": str(p)})]
