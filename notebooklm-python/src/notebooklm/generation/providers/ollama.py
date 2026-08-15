"""Ollama (local) chat provider.

Talks to a local Ollama daemon over HTTP. No API key required.
"""
from __future__ import annotations

import os

from langchain_ollama import ChatOllama

from notebooklm.generation.types import Message


class OllamaProvider:
    def __init__(self, model: str | None = None) -> None:
        self.name = "ollama"
        self._model_name = model or os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self._client = ChatOllama(model=self._model_name, base_url=base_url, temperature=0.0)

    def chat(self, messages: list[Message], **kwargs: object) -> str:
        from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

        lc_messages = []
        for m in messages:
            if m.role == "system":
                lc_messages.append(SystemMessage(content=m.content))
            elif m.role == "assistant":
                lc_messages.append(AIMessage(content=m.content))
            else:
                lc_messages.append(HumanMessage(content=m.content))
        result = self._client.invoke(lc_messages, **kwargs)
        return result.content if isinstance(result.content, str) else str(result.content)
