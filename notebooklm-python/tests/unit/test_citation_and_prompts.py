"""Unit tests for the citation parser and grounding prompt builder."""
from __future__ import annotations

from notebooklm.generation.citation_parser import (
    parse_citations,
    strip_citation_markers,
)
from notebooklm.generation.prompts import NO_CONTEXT_RESPONSE, build_grounded_prompt


class TestParseCitations:
    def test_single_citation(self) -> None:
        text = "NotebookLM uses RAG [source_1]."
        result = parse_citations(text)
        assert result.citation_ids == [1]
        assert result.clean_text == "NotebookLM uses RAG ."
        assert len(result.citations) == 1
        assert result.citations[0].marker == 1

    def test_multiple_citations(self) -> None:
        text = "LangGraph [source_1] orchestrates RAG [source_2] flows [source_3]."
        result = parse_citations(text)
        assert result.citation_ids == [1, 2, 3]
        assert len(result.citations) == 3

    def test_duplicate_citation_dedupes_ids(self) -> None:
        text = "foo [source_1] bar [source_1] baz"
        result = parse_citations(text)
        assert result.citation_ids == [1]
        assert len(result.citations) == 1

    def test_no_citations_returns_empty(self) -> None:
        text = "Just plain text without any markers."
        result = parse_citations(text)
        assert result.citation_ids == []
        assert result.clean_text == text
        assert result.citations == []

    def test_citation_with_whitespace(self) -> None:
        text = "Foo [source_ 2 ] bar"
        result = parse_citations(text)
        assert result.citation_ids == [2]

    def test_out_of_range_ids_still_parsed(self) -> None:
        text = "foo [source_99] bar"
        result = parse_citations(text)
        assert result.citation_ids == [99]


class TestStripCitationMarkers:
    def test_removes_brackets(self) -> None:
        assert strip_citation_markers("foo [source_1] bar") == "foo  bar"

    def test_handles_no_markers(self) -> None:
        assert strip_citation_markers("plain text") == "plain text"


class TestBuildGroundedPrompt:
    def test_includes_query(self) -> None:
        msgs = build_grounded_prompt(
            query="What is RAG?",
            contexts=["RAG is retrieval augmented generation."],
        )
        user = next(m for m in msgs if m.role == "user")
        assert "What is RAG?" in user.content
        assert "RAG is retrieval augmented generation" in user.content

    def test_includes_system_prompt(self) -> None:
        msgs = build_grounded_prompt(query="q", contexts=["c"])
        system = next(m for m in msgs if m.role == "system")
        assert "源文件中未提及" in system.content or "not mentioned" in system.content.lower()
        assert "[source_N]" in system.content

    def test_empty_context_uses_no_context_response(self) -> None:
        msgs = build_grounded_prompt(query="q", contexts=[])
        user = next(m for m in msgs if m.role == "user")
        system = next(m for m in msgs if m.role == "system")
        assert "无相关内容" in user.content
        assert NO_CONTEXT_RESPONSE in system.content
