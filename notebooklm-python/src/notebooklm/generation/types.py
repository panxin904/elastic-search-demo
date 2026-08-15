"""Shared types for the LLM provider layer.

Kept in its own module to break the circular import between
`llm_provider` (the factory) and the per-vendor provider modules.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


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
