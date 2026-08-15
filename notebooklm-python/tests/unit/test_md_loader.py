"""Unit tests for the Markdown loader."""
from __future__ import annotations

from pathlib import Path

import pytest

from notebooklm.ingestion.loaders.md_loader import MdLoader


class TestMdLoader:
    def test_loads_simple_markdown(self, tmp_path: Path) -> None:
        path = tmp_path / "doc.md"
        path.write_text("# Title\n\nSome **bold** text.\n", encoding="utf-8")
        docs = MdLoader().load(path)
        assert len(docs) == 1
        assert "bold" in docs[0].text
        assert "Title" in docs[0].text
        assert "**" not in docs[0].text
        assert docs[0].source == str(path)

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            MdLoader().load(tmp_path / "missing.md")

    def test_empty_file_returns_empty_list(self, tmp_path: Path) -> None:
        path = tmp_path / "empty.md"
        path.write_text("", encoding="utf-8")
        assert MdLoader().load(path) == []
