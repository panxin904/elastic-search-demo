"""Typer CLI for the NotebookLM reconstruction.

Usage:
    notebooklm ingest <path> [<path> ...]    load, chunk, embed, index
    notebooklm query "<question>"            RAG flow with citations
    notebooklm serve (TODO)                  (not implemented)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from notebooklm.config import load_settings
from notebooklm.generation.llm_provider import get_provider
from notebooklm.graph.graph import build_graph
from notebooklm.ingestion.embedder import Embedder
from notebooklm.ingestion.pipeline import IngestionPipeline
from notebooklm.retrieval.es_store import EsStore
from notebooklm.retrieval.hybrid_retriever import Retriever
from notebooklm.retrieval.reranker import Reranker

app = typer.Typer(add_completion=False, help="NotebookLM-style RAG over your files.")
console = Console()


def _build_store(settings, embedder: Embedder) -> EsStore:
    return EsStore(
        es_url=settings.resolved_es_url(),
        index=settings.es_index,
        embedding_dim=embedder.dimension,
    )


@app.command()
def ingest(
    paths: list[Path] = typer.Argument(..., help="Files or directories to ingest"),  # noqa: B008
) -> None:
    """Load, chunk, embed, and index one or more files into Elasticsearch."""
    settings = load_settings()
    console.print(f"[bold]Using LLM provider:[/bold] {settings.llm_provider}")
    console.print(f"[bold]Embedding model:[/bold] {settings.embedding_model}")
    console.print(f"[bold]ES index:[/bold] {settings.es_index}")

    embedder = Embedder(model_name=settings.embedding_model)
    pipeline = IngestionPipeline(
        embedder=embedder,
        chunk_size=settings.chunk_size,
        overlap=settings.chunk_overlap,
    )
    all_paths: list[Path] = []
    for p in paths:
        if p.is_dir():
            all_paths.extend(_iter_dir(p))
        else:
            all_paths.append(p)

    if not all_paths:
        console.print("[yellow]No files to ingest.[/yellow]")
        return

    console.print(f"[bold]Loading and chunking {len(all_paths)} file(s)...[/bold]")
    chunks = pipeline.ingest(all_paths)
    console.print(f"  → {len(chunks)} chunks produced")

    if not chunks:
        console.print("[yellow]No chunks to index.[/yellow]")
        return

    store = _build_store(settings, embedder)
    store.ensure_index()
    n = store.index_chunks(chunks)
    store.refresh()
    console.print(f"[green]✓ Indexed {n} chunks into '{settings.es_index}'[/green]")


@app.command()
def query(
    question: str = typer.Argument(..., help="The question to ask"),  # noqa: B008
    show_citations: bool = typer.Option(True, "--citations/--no-citations"),
) -> None:
    """Run the RAG flow and print the grounded answer with citations."""
    settings = load_settings()
    embedder = Embedder(model_name=settings.embedding_model)
    store = _build_store(settings, embedder)
    reranker = Reranker(model_name=settings.reranker_model)
    retriever = Retriever(
        store=store,
        embedder=embedder,
        reranker=reranker,
        top_k=settings.top_k,
        top_n=settings.top_n,
    )
    provider = get_provider(settings.llm_provider)
    graph = build_graph(retriever, provider, max_retries=settings.max_retries)

    result: dict[str, Any] = graph.invoke(
        {"query": question, "max_retries": settings.max_retries}
    )

    console.print(Panel(result.get("parsed", {}).get("clean_text", ""), title="Answer"))

    if show_citations and result.get("citations"):
        table = Table(title="Citations")
        table.add_column("#", style="cyan")
        table.add_column("Source", style="green")
        table.add_column("Page", style="magenta")
        table.add_column("Snippet", style="white", overflow="fold")
        for c in result["citations"]:
            table.add_row(
                f"[{c['marker']}]",
                c["source"],
                str(c.get("page") or "-"),
                c["text"][:120] + ("..." if len(c["text"]) > 120 else ""),
            )
        console.print(table)

    if not result.get("grounded"):
        console.print(
            "[yellow]Warning: response did not pass grounding validation "
            "after max retries.[/yellow]"
        )


def _iter_dir(d: Path) -> list[Path]:
    out: list[Path] = []
    for p in sorted(d.rglob("*")):
        if p.is_file() and p.suffix.lower() in {".txt", ".md", ".markdown", ".pdf", ".docx"}:
            out.append(p)
    return out


def main() -> None:
    app()


if __name__ == "__main__":
    main()
