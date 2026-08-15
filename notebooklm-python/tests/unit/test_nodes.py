"""Tests for LangGraph node implementations."""
from __future__ import annotations

from unittest.mock import MagicMock

from notebooklm.graph.nodes import make_analyze_query_node


class TestAnalyzeQueryNode:
    """Tests for the analyze_query node."""

    def _make_node(self):
        mock_provider = MagicMock()
        return make_analyze_query_node(mock_provider)

    def test_empty_query(self):
        node = self._make_node()
        result = node({"query": ""})
        assert result["query_type"] == "empty"
        assert result["needs_retrieval"] is False

    def test_chat_greeting(self):
        node = self._make_node()
        result = node({"query": "Hello"})
        assert result["query_type"] == "chat"
        assert result["needs_retrieval"] is False

    def test_chat_thanks(self):
        node = self._make_node()
        result = node({"query": "Thank you"})
        assert result["query_type"] == "chat"
        assert result["needs_retrieval"] is False

    def test_factual_query(self):
        node = self._make_node()
        result = node({"query": "What is the main topic?"})
        assert result["query_type"] == "factual"
        assert result["needs_retrieval"] is True

    def test_document_query(self):
        node = self._make_node()
        result = node({"query": "According to the document..."})
        assert result["query_type"] == "factual"
        assert result["needs_retrieval"] is True

    def test_summary_query(self):
        node = self._make_node()
        result = node({"query": "Summarize the content"})
        assert result["query_type"] == "summary"
        assert result["needs_retrieval"] is True

    def test_unknown_query_defaults_to_retrieval(self):
        node = self._make_node()
        result = node({"query": "Tell me about something"})
        assert result["query_type"] == "unknown"
        assert result["needs_retrieval"] is True

    def test_case_insensitive(self):
        node = self._make_node()
        result = node({"query": "HELLO"})
        assert result["query_type"] == "chat"
        assert result["needs_retrieval"] is False
