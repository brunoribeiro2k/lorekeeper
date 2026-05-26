"""Command-line interface for Lorekeeper."""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from lorekeeper.agent.runtime import AgentRuntime
from lorekeeper.core.config import Settings

app = typer.Typer(
    name="lorekeeper",
    help="Ask Lorekeeper natural-language questions about data.",
    add_completion=False,
)
console = Console()


@app.command()
def ask(
    question: str = typer.Argument(..., help="Natural-language data question"),
    backend: str = typer.Option(
        None,
        "--backend",
        "-b",
        help="Model backend to use once concrete adapters are wired.",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show trace metadata."),
) -> None:
    """Ask Lorekeeper a question."""
    settings = Settings()
    if backend is not None:
        settings.default_backend = backend

    runtime = AgentRuntime(settings=settings)
    response = asyncio.run(runtime.answer(question))

    console.print(Panel(Markdown(response.answer), title="[bold]Lorekeeper", border_style="blue"))
    if verbose:
        console.print(f"[dim]status: {response.status}[/dim]")
        console.print(f"[dim]trace: {response.trace_id}[/dim]")


if __name__ == "__main__":
    app()
