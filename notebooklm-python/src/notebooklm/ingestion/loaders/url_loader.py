"""URL loader.

Fetches an HTML page and extracts the main text using trafilatura, which
is robust against ads, navigation, and other boilerplate. URLs are
treated as documents with a single chunk.
"""
from __future__ import annotations

from pathlib import Path

import httpx
import trafilatura

from notebooklm.ingestion.loaders.base import Document


class UrlLoader:
    """Fetch a URL and extract its main textual content."""

    def __init__(self, timeout: float = 30.0, user_agent: str = "notebooklm/0.1") -> None:
        self._timeout = timeout
        self._headers = {"User-Agent": user_agent}

    def load(self, path: str | Path) -> list[Document]:
        # `path` is a URL in this loader's contract; Path is supported for
        # protocol-uniformity with other loaders.
        url = str(path)
        with httpx.Client(timeout=self._timeout, headers=self._headers, follow_redirects=True) as client:
            response = client.get(url)
            response.raise_for_status()
            html = response.text

        text = trafilatura.extract(html, include_links=False, include_images=False) or ""
        text = text.strip()
        if not text:
            return []
        return [Document(text=text, source=url, metadata={"url": url})]
