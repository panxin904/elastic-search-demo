"""Smoke test for the CLI.

Runs the typer app via `CliRunner` and asserts the help / arg parsing
work end-to-end. Doesn't actually start ES or call the LLM — those
paths are exercised by the integration tests.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from notebooklm.cli.app import app

runner = CliRunner()


class TestCliHelp:
    def test_top_level_help(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "ingest" in result.stdout
        assert "query" in result.stdout

    def test_ingest_help(self) -> None:
        result = runner.invoke(app, ["ingest", "--help"])
        assert result.exit_code == 0
        assert "PATHS" in result.stdout or "paths" in result.stdout

    def test_query_help(self) -> None:
        result = runner.invoke(app, ["query", "--help"])
        assert result.exit_code == 0
        assert "question" in result.stdout


class TestIngestCli:
    def test_ingest_nonexistent_file_reports_no_files(self, tmp_path: Path) -> None:
        # No matching files in the dir; pipeline should print a message and exit 0.
        empty = tmp_path / "empty"
        empty.mkdir()
        result = runner.invoke(app, ["ingest", str(empty)])
        assert result.exit_code == 0
        assert "No files" in result.stdout or "No chunks" in result.stdout

    def test_ingest_without_es_url_fails_cleanly(self, tmp_path: Path) -> None:
        f = tmp_path / "a.txt"
        f.write_text("hello", encoding="utf-8")
        # Don't set NOTEBOOKLM_ES_URL; CLI should fail before talking to ES
        # because resolve_es_url() raises when it's not configured.
        env = {k: v for k, v in __import__("os").environ.items() if k != "NOTEBOOKLM_ES_URL"}
        with patch.dict("os.environ", env, clear=True):
            result = runner.invoke(app, ["ingest", str(f)])
        # Either the settings raise early, or the ES client fails to connect;
        # both are acceptable — what we care about is non-zero exit.
        assert result.exit_code != 0
