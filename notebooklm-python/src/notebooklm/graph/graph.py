"""LangGraph StateGraph definition for the grounded RAG flow.

Flow:
    START
      ↓
    [analyze_query]  → classifies query type, decides if retrieval needed
      ↓
    [retrieve]       → calls the retriever, populates `contexts`/`context_chunks`
      ↓
    [generate]       → calls the LLM with the grounding prompt, sets `raw_response`
      ↓
    [parse]          → extracts `[source_N]` markers, builds `citations`
      ↓
    [validate]       → decides grounded vs retry; if retry, loops back to generate
      ↓
    END

The `analyze_query → retrieve` edge is conditional: it only retrieves
when `needs_retrieval is True`. For chat queries, we skip retrieval.

The `validate → generate` edge is conditional: it only loops when
`grounded is False` and `retry_count < max_retries`. After `max_retries`
we give up and end with whatever the LLM said.
"""
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from notebooklm.generation.llm_provider import ChatProvider
from notebooklm.graph.nodes import (
    make_analyze_query_node,
    make_generate_node,
    make_parse_citations_node,
    make_retrieve_node,
    make_validate_grounding_node,
)
from notebooklm.graph.state import NotebookState
from notebooklm.retrieval.hybrid_retriever import Retriever


def build_graph(
    retriever: Retriever,
    provider: ChatProvider,
    max_retries: int = 2,
):
    g = StateGraph(NotebookState)

    g.add_node("analyze_query", make_analyze_query_node(provider))
    g.add_node("retrieve", make_retrieve_node(retriever))
    g.add_node("generate", make_generate_node(provider))
    g.add_node("parse", make_parse_citations_node())
    g.add_node("validate", make_validate_grounding_node())

    g.add_edge(START, "analyze_query")

    def _route_after_analysis(state: NotebookState) -> str:
        if state.get("needs_retrieval", True):
            return "retrieve"
        return "generate"

    g.add_conditional_edges(
        "analyze_query",
        _route_after_analysis,
        {"retrieve": "retrieve", "generate": "generate"},
    )

    g.add_edge("retrieve", "generate")
    g.add_edge("generate", "parse")
    g.add_edge("parse", "validate")

    def _route_after_validate(state: NotebookState) -> str:
        if state.get("grounded"):
            return END
        if int(state.get("retry_count", 0)) >= int(state.get("max_retries", max_retries)):
            return END
        return "generate"

    g.add_conditional_edges(
        "validate",
        _route_after_validate,
        {END: END, "generate": "generate"},
    )

    return g.compile()
