"""Unit tests for the plain-text loader."""
from __future__ import annotations

from pathlib import Path

import pytest

from notebooklm.ingestion.loaders.txt_loader import TxtLoader


class TestTxtLoader:
    def test_loads_simple_text(self, tmp_path: Path) -> None:
        path = tmp_path / "hello.txt"
        path.write_text("hello world\n", encoding="utf-8")
        docs = TxtLoader().load(path)
        assert len(docs) == 1
        assert docs[0].text == "hello world"
        assert docs[0].source == str(path)

    def test_strips_trailing_newlines(self, tmp_path: Path) -> None:
        # Long blocks of trailing whitespace inflate embedding cost and
        # add no semantic value.
        path = tmp_path / "padded.txt"
        path.write_text("content\n\n\n", encoding="utf-8")
        docs = TxtLoader().load(path)
        assert docs[0].text == "content"

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            TxtLoader().load(tmp_path / "missing.txt")

    def test_empty_file_returns_empty_list(self, tmp_path: Path) -> None:
        path = tmp_path / "empty.txt"
        path.write_text("", encoding="utf-8")
        assert TxtLoader().load(path) == []

    def test_whitespace_only_file_returns_empty_list(self, tmp_path: Path) -> None:
        path = tmp_path / "blank.txt"
        path.write_text("   \n\t  \n", encoding="utf-8")
        assert TxtLoader().load(path) == []
