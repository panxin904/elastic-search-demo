"""End-to-end test of the LangGraph RAG flow.

We inject mock retriever + mock LLM so the test runs offline and fast.
The mock LLM echoes the expected response for both the happy path and
the retry path.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from notebooklm.generation.llm_provider import Message
from notebooklm.generation.prompts import NO_CONTEXT_RESPONSE
from notebooklm.graph.graph import build_graph
from notebooklm.retrieval.es_store import HybridHit


@dataclass
class _MockRetriever:
    chunks: list[HybridHit] = field(default_factory=list)
    calls: int = 0

    def retrieve(self, query: str) -> list[HybridHit]:
        self.calls += 1
        return list(self.chunks)


@dataclass
class _MockProvider:
    responses: list[str] = field(default_factory=list)
    call_count: int = 0

    @property
    def name(self) -> str:
        return "mock"

    def chat(self, messages: list[Message], **kwargs: object) -> str:
        idx = min(self.call_count, len(self.responses) - 1)
        self.call_count += 1
        return self.responses[idx]


def _hit(chunk_id: str, text: str, page: int | None = 1) -> HybridHit:
    return HybridHit(chunk_id=chunk_id, text=text, source="a.txt", score=0.9, page=page)


class TestGroundedGraphFlow:
    def test_happy_path_with_citations(self) -> None:
        retriever = _MockRetriever(
            chunks=[
                _hit("c1", "RAG is retrieval augmented generation."),
                _hit("c2", "LangGraph is a graph-based orchestration framework."),
            ]
        )
        provider = _MockProvider(
            responses=["RAG is retrieval-augmented generation [source_1]."]
        )
        graph = build_graph(retriever, provider, max_retries=2)

        result: dict[str, Any] = graph.invoke({"query": "What is RAG?", "max_retries": 2})
        assert result["grounded"] is True
        assert "RAG" in result["parsed"]["clean_text"]
        assert result["citations"][0]["chunk_id"] == "c1"
        assert provider.call_count == 1

    def test_no_context_triggers_no_context_response(self) -> None:
        retriever = _MockRetriever(chunks=[])
        provider = _MockProvider(responses=[NO_CONTEXT_RESPONSE])
        graph = build_graph(retriever, provider)

        result = graph.invoke({"query": "Anything?", "max_retries": 2})
        assert result["grounded"] is True
        assert result["parsed"]["clean_text"] == NO_CONTEXT_RESPONSE
        assert result["citations"] == []

    def test_retry_when_first_response_lacks_citations(self) -> None:
        retriever = _MockRetriever(chunks=[_hit("c1", "Some context.")])
        provider = _MockProvider(
            responses=[
                "I cannot answer.",
                "Some context [source_1] is the answer.",
            ]
        )
        graph = build_graph(retriever, provider, max_retries=2)

        result = graph.invoke({"query": "What?", "max_retries": 2})
        assert result["grounded"] is True
        assert provider.call_count == 2
        assert result["retry_count"] == 1

    def test_gives_up_after_max_retries(self) -> None:
        retriever = _MockRetriever(chunks=[_hit("c1", "ctx")])
        provider = _MockProvider(responses=["refuses to cite."])
        graph = build_graph(retriever, provider, max_retries=2)

        result = graph.invoke({"query": "What?", "max_retries": 2})
        assert result["grounded"] is False
        assert provider.call_count == 2
        assert result["retry_count"] == 2
