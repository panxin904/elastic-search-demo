"""LangGraph state schema for the grounded RAG flow."""
from __future__ import annotations

from typing import Any, TypedDict


class CitationEntry(TypedDict):
    marker: int
    chunk_id: str
    text: str
    source: str
    page: int | None


class NotebookState(TypedDict, total=False):
    """All nodes read and write to fields on this dict.

    Fields:
        query: The user's question.
        query_type: Classified query type (factual, chat, summary, etc.).
        needs_retrieval: Whether the query requires document retrieval.
        contexts: Text of the retrieved chunks (in citation order).
        context_chunks: Full hit metadata for citation rendering.
        raw_response: LLM text output.
        parsed: Output of `parse_citations` (clean text + markers).
        citations: Structured citation entries mapping marker -> chunk.
        grounded: True when the response is acceptable (citation ratio
            high enough, or a no-context response).
        retry_count: How many times we have re-generated.
        max_retries: Cap for the validation-retry loop.
        error: Optional error string surfaced from any node.
        extra: Catch-all for downstream extensions (e.g. streaming).
    """

    query: str
    query_type: str
    needs_retrieval: bool
    contexts: list[str]
    context_chunks: list[dict[str, Any]]
    raw_response: str
    parsed: dict[str, Any]
    citations: list[CitationEntry]
    grounded: bool
    retry_count: int
    max_retries: int
    error: str
    extra: dict[str, Any]
