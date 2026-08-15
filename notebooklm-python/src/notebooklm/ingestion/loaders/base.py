"""Base types and protocol for document loaders.

A `Document` is the canonical in-memory representation of a piece of source
content. Each loader converts a specific file format / URL into one or more
`Document` objects with structured metadata (page number, timestamp, etc.).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@dataclass(frozen=False)
class Document:
    """A single parsed unit of source content.

    Attributes:
        text: The extracted plain text. For multi-page sources, each page
            typically becomes a separate Document.
        source: The origin of the content (filename, URL, or other identifier).
        metadata: Free-form structured metadata. Common keys: ``page``,
            ``timestamp``, ``author``, ``title``. The chunker and embedder
            are expected to copy metadata into the resulting chunks.
    """

    text: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class DocumentLoader(Protocol):
    """Protocol every concrete loader must satisfy."""

    def load(self, path: str | Path) -> list[Document]:
        """Parse ``path`` and return a list of `Document` objects.

        Implementations must:
        * Return an empty list (not raise) for files that exist but contain
          no extractable text.
        * Raise ``FileNotFoundError`` for missing paths.
        """
        ...
