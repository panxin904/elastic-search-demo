"""LLM provider abstraction.

A `ChatProvider` is a thin wrapper over a langchain `BaseChatModel`. The
goal is a single uniform interface so the LangGraph nodes don't care
which vendor they're talking to.

Add a new provider by:
1. Implementing `ChatProvider` in `providers/<name>.py`.
2. Adding a case to `get_provider`.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from notebooklm.generation.providers.gemini import GeminiProvider
from notebooklm.generation.providers.ollama import OllamaProvider
from notebooklm.generation.providers.openai import OpenAIProvider


@dataclass
class Message:
    role: str
    content: str


@runtime_checkable
class ChatProvider(Protocol):
    """Uniform interface every LLM provider exposes."""

    name: str

    def chat(self, messages: list[Message], **kwargs: object) -> str:
        """Send ``messages`` and return the assistant text."""
        ...


def get_provider(name: str) -> ChatProvider:
    """Construct a provider by name. Reads credentials from env."""
    n = name.lower().strip()
    if n == "openai":
        if not os.environ.get("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is not set")
        return OpenAIProvider()
    if n == "gemini":
        if not os.environ.get("GOOGLE_API_KEY") and not os.environ.get(
            "GOOGLE_API_KEY"
        ):
            raise RuntimeError("GOOGLE_API_KEY is not set")
        return GeminiProvider()
    if n == "ollama":
        return OllamaProvider()
    raise ValueError(f"Unknown LLM provider: {name!r}")
