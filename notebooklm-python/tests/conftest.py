"""Shared pytest fixtures for all tests.

Currently exposes a `reset_agent_caches` autouse fixture for the
`notebooklm.agent` module: the agent module holds process-wide
singletons (Embedder, Reranker, compiled graph) that need to be wiped
between tests so patching via `unittest.mock.patch` takes effect.
"""
from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def reset_agent_caches():
    """Reset the agent module's module-level caches before each test."""
    try:
        from notebooklm import agent
    except ImportError:
        yield
        return
    agent.reset_caches()
    yield
    agent.reset_caches()
