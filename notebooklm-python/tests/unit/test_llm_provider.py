"""Unit tests for the LLM provider factory.

The factory must:
- Dispatch to the right provider class based on the name.
- Read the API key from the environment (no key in the constructor).
- Raise on unknown provider names.

We mock the langchain client classes to avoid hitting any real API.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from notebooklm.generation.llm_provider import (
    ChatProvider,
    Message,
    get_provider,
)
from notebooklm.generation.providers.openai import OpenAIProvider


class TestGetProvider:
    def test_openai_dispatch(self) -> None:
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test"}):
            p = get_provider("openai")
            assert isinstance(p, ChatProvider)
            assert p.name == "openai"

    def test_gemini_dispatch(self) -> None:
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "test"}):
            p = get_provider("gemini")
            assert p.name == "gemini"

    def test_ollama_dispatch_does_not_require_api_key(self) -> None:
        p = get_provider("ollama")
        assert p.name == "ollama"

    def test_unknown_provider_raises(self) -> None:
        with pytest.raises(ValueError):
            get_provider("not-a-real-provider")

    def test_openai_missing_key_raises(self) -> None:
        env = {
            k: v
            for k, v in __import__("os").environ.items()
            if k != "OPENAI_API_KEY"
        }
        with patch.dict("os.environ", env, clear=True), pytest.raises(RuntimeError):
            get_provider("openai")


class TestMessageDataclass:
    def test_minimal(self) -> None:
        m = Message(role="user", content="hi")
        assert m.role == "user"
        assert m.content == "hi"

    def test_system_role(self) -> None:
        m = Message(role="system", content="be brief")
        assert m.role == "system"


class TestOpenAIProviderChat:
    def test_chat_returns_text(self) -> None:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "the answer is 42"
        mock_client.invoke.return_value = mock_response

        with patch("notebooklm.generation.providers.openai.ChatOpenAI") as mock_chat:
            mock_chat.return_value = mock_client
            p = OpenAIProvider()
            result = p.chat([Message(role="user", content="What is 6*7?")])

        assert result == "the answer is 42"
        mock_client.invoke.assert_called_once()
        msgs_arg = mock_client.invoke.call_args.args[0]
        assert len(msgs_arg) == 1
        assert msgs_arg[0].content == "What is 6*7?"
