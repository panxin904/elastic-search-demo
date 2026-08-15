"""LangGraph node implementations for the grounded RAG flow."""
from __future__ import annotations

from typing import Any

from notebooklm.generation.citation_parser import parse_citations
from notebooklm.generation.llm_provider import ChatProvider, Message
from notebooklm.generation.prompts import NO_CONTEXT_RESPONSE, build_grounded_prompt
from notebooklm.graph.state import CitationEntry, NotebookState
from notebooklm.retrieval.es_store import HybridHit
from notebooklm.retrieval.hybrid_retriever import Retriever


def make_analyze_query_node(provider: ChatProvider):
    """Classify query type and decide if document retrieval is needed.

    Returns dict with query_type (factual/chat/summary/unknown) and
    needs_retrieval boolean.
    """

    def analyze_query(state: NotebookState) -> dict[str, Any]:
        query = state.get("query", "")
        if not query:
            return {"query_type": "empty", "needs_retrieval": False}

        query_lower = query.lower().strip()

        chat_patterns = [
            "hello", "hi", "hey", "good morning", "good afternoon",
            "good evening", "how are you", "what's up", "thanks",
            "thank you", "bye", "goodbye",
        ]
        if any(query_lower.startswith(p) or query_lower == p for p in chat_patterns):
            return {"query_type": "chat", "needs_retrieval": False}

        document_patterns = [
            "document", "file", "upload", "source", "context",
            "according to", "based on", "in the text", "in the document",
        ]
        if any(p in query_lower for p in document_patterns):
            return {"query_type": "factual", "needs_retrieval": True}

        summary_patterns = ["summarize", "summary", "overview", "tldr", "main points"]
        if any(p in query_lower for p in summary_patterns):
            return {"query_type": "summary", "needs_retrieval": True}

        question_words = ["what", "who", "where", "when", "why", "how", "which"]
        if any(query_lower.startswith(w) for w in question_words):
            return {"query_type": "factual", "needs_retrieval": True}

        return {"query_type": "unknown", "needs_retrieval": True}

    return analyze_query


def make_retrieve_node(retriever: Retriever):
    def retrieve(state: NotebookState) -> dict[str, Any]:
        query = state.get("query", "")
        if not query:
            return {"error": "empty query", "grounded": False}
        hits: list[HybridHit] = retriever.retrieve(query)
        contexts = [h.text for h in hits]
        chunks_meta = [
            {
                "chunk_id": h.chunk_id,
                "text": h.text,
                "source": h.source,
                "page": h.page,
            }
            for h in hits
        ]
        return {"contexts": contexts, "context_chunks": chunks_meta}

    return retrieve


def make_generate_node(provider: ChatProvider):
    def generate(state: NotebookState) -> dict[str, Any]:
        query = state.get("query", "")
        contexts = state.get("contexts", [])
        msgs: list[Message] = build_grounded_prompt(query, contexts)
        text = provider.chat(msgs)
        return {"raw_response": text}

    return generate


def make_parse_citations_node():
    def parse(state: NotebookState) -> dict[str, Any]:
        raw = state.get("raw_response", "")
        parsed = parse_citations(raw)
        chunks_meta = state.get("context_chunks", [])

        citations: list[CitationEntry] = []
        for marker in parsed.citation_ids:
            idx = marker - 1
            if 0 <= idx < len(chunks_meta):
                c = chunks_meta[idx]
                citations.append(
                    {
                        "marker": marker,
                        "chunk_id": c.get("chunk_id", ""),
                        "text": c.get("text", ""),
                        "source": c.get("source", ""),
                        "page": c.get("page"),
                    }
                )
        return {
            "parsed": {
                "clean_text": parsed.clean_text,
                "citation_ids": parsed.citation_ids,
            },
            "citations": citations,
        }

    return parse


def make_validate_grounding_node():
    def validate(state: NotebookState) -> dict[str, Any]:
        raw = state.get("raw_response", "")
        contexts = state.get("contexts", [])
        retry = int(state.get("retry_count", 0))

        no_context_requested = not contexts
        no_context_given = NO_CONTEXT_RESPONSE in raw

        if no_context_requested and no_context_given:
            return {"grounded": True, "retry_count": retry}

        citations_count = len(state.get("citations", []))
        grounded = citations_count > 0
        return {
            "grounded": grounded,
            "retry_count": retry if grounded else retry + 1,
        }

    return validate
