"""Application configuration loaded from environment + .env file."""
from __future__ import annotations

import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider: str = Field(default="openai", alias="NOTEBOOKLM_LLM")
    embedding_model: str = Field(
        default="intfloat/multilingual-e5-base",
        alias="NOTEBOOKLM_EMBEDDING_MODEL",
    )
    reranker_model: str = Field(
        default="cross-encoder/ms-marco-MiniLM-L-6-v2",
        alias="NOTEBOOKLM_RERANKER_MODEL",
    )

    es_url: str = Field(default="", alias="NOTEBOOKLM_ES_URL")
    es_index: str = Field(default="notebooklm_chunks", alias="NOTEBOOKLM_ES_INDEX")

    top_k: int = Field(default=20, alias="NOTEBOOKLM_TOP_K")
    top_n: int = Field(default=5, alias="NOTEBOOKLM_TOP_N")
    chunk_size: int = Field(default=512, alias="NOTEBOOKLM_CHUNK_SIZE")
    chunk_overlap: int = Field(default=64, alias="NOTEBOOKLM_CHUNK_OVERLAP")
    max_retries: int = Field(default=2, alias="NOTEBOOKLM_MAX_RETRIES")

    def resolved_es_url(self) -> str:
        """If env is empty, raise so callers can fall back to testcontainers."""
        if self.es_url:
            return self.es_url
        raise RuntimeError(
            "NOTEBOOKLM_ES_URL is not set. Set it in .env or environment."
        )


def load_settings() -> Settings:
    return Settings()


def env_or(name: str, default: str) -> str:
    return os.environ.get(name, default)
