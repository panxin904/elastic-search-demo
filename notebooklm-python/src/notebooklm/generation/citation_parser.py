"""Parse `[source_N]` citation markers out of LLM responses.

The LLM is instructed to insert markers like ``[source_1]`` next to each
factual claim. This module extracts them, deduplicates by id, and
returns a clean text string with the markers stripped.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_CITATION_RE = re.compile(r"\[\s*source_\s*(\d+)\s*\]", re.IGNORECASE)


@dataclass
class Citation:
    marker: int


@dataclass
class ParsedResponse:
    """Result of `parse_citations`.

    Attributes:
        clean_text: Original text with the `[source_N]` markers removed.
        citations: Deduplicated list of citations in the order they
            first appeared.
        citation_ids: Convenience: the marker ints of `citations`.
    """

    clean_text: str
    citations: list[Citation] = field(default_factory=list)
    citation_ids: list[int] = field(default_factory=list)


def parse_citations(text: str) -> ParsedResponse:
    seen: set[int] = set()
    citations: list[Citation] = []
    citation_ids: list[int] = []

    def _record(match: re.Match[str]) -> str:
        marker = int(match.group(1))
        if marker not in seen:
            seen.add(marker)
            citations.append(Citation(marker=marker))
            citation_ids.append(marker)
        return ""

    clean = _CITATION_RE.sub(_record, text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return ParsedResponse(clean_text=clean, citations=citations, citation_ids=citation_ids)


def strip_citation_markers(text: str) -> str:
    return _CITATION_RE.sub("", text)
