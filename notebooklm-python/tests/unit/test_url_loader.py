"""Unit tests for the URL loader.

URL fetching is mocked via `respx` (httpx mocking) so tests run offline.
If respx is not installed in the env, these tests are skipped.
"""
from __future__ import annotations

import pytest

respx = pytest.importorskip("respx")
import httpx  # noqa: E402

from notebooklm.ingestion.loaders.url_loader import UrlLoader  # noqa: E402

SAMPLE_HTML = """
<!doctype html>
<html>
  <head><title>Example</title></head>
  <body>
    <article>
      <h1>Hello</h1>
      <p>This is the first paragraph of useful content.</p>
      <p>This is a second paragraph with <a href="/other">a link</a>.</p>
    </article>
  </body>
</html>
"""


class TestUrlLoader:
    @respx.mock
    def test_fetches_and_extracts_text(self) -> None:
        respx.get("https://example.com/article").mock(
            return_value=httpx.Response(200, text=SAMPLE_HTML)
        )
        docs = UrlLoader().load("https://example.com/article")
        assert len(docs) == 1
        assert "first paragraph" in docs[0].text
        assert "second paragraph" in docs[0].text
        assert docs[0].source == "https://example.com/article"
        # We don't want raw HTML noise in the indexed text.
        assert "<article>" not in docs[0].text

    @respx.mock
    def test_404_raises(self) -> None:
        respx.get("https://example.com/missing").mock(
            return_value=httpx.Response(404)
        )
        with pytest.raises(httpx.HTTPStatusError):
            UrlLoader().load("https://example.com/missing")
