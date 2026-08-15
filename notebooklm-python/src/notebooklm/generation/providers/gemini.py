"""Google Gemini chat provider."""
from __future__ import annotations

import os

from langchain_google_genai import ChatGoogleGenerativeAI

from notebooklm.generation.types import Message


class GeminiProvider:
    def __init__(self, model: str | None = None) -> None:
        self.name = "gemini"
        self._model_name = model or os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        self._client = ChatGoogleGenerativeAI(
            model=self._model_name,
            temperature=0.0,
            convert_system_message_to_human=True,
        )

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
