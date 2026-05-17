"""CLI entry point — `lorekeeper "<question>"`."""

from __future__ import annotations

import asyncio

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

app = typer.Typer(
    name="lorekeeper",
    help="Lorekeeper — Data Specialist AI agent. Ask it anything about your data.",
    add_completion=False,
)
console = Console()


@app.command()
def ask(
    question: str = typer.Argument(..., help="Natural-language data question"),
    backend: str = typer.Option(
        "anthropic",
        "--backend",
        "-b",
        help="Model backend: anthropic | ollama",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show tool call count and assumptions",
    ),
) -> None:
    """Ask Lorekeeper a data question and get an answer with SQL."""
    from lorekeeper.models import AnthropicBackend, OllamaBackend
    from lorekeeper.runtime import AgentRuntime, Settings

    settings = Settings()
    if backend == "ollama":
        model_backend = OllamaBackend(model=settings.ollama_model)
    else:
        model_backend = AnthropicBackend(model=settings.anthropic_model)

    runtime = AgentRuntime(backend=model_backend)

    with console.status("[bold green]Lorekeeper is thinking…"):
        response = asyncio.run(runtime.answer(question))

    console.print(
        Panel(Markdown(response.answer), title="[bold]Lorekeeper", border_style="blue")
    )

    if response.sql:
        console.print(Panel(response.sql, title="[bold]SQL", border_style="dim"))

    if verbose:
        if response.assumptions:
            console.print("\n[dim]Assumptions:[/dim]")
            for a in response.assumptions:
                console.print(f"  [dim]· {a}[/dim]")
        console.print(f"\n[dim]Tool calls: {response.tool_calls}[/dim]")


if __name__ == "__main__":
    app()
