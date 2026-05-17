"""Evaluation harness — run the Lorekeeper benchmark and print a results table.

Usage:
    uv run python evals/run_eval.py
    uv run python evals/run_eval.py --backend ollama
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent))

from lorekeeper.runtime import AgentResponse, AgentRuntime

console = Console()


def load_questions(path: Path) -> list[dict[str, Any]]:
    """Load benchmark questions from YAML."""
    with path.open() as f:
        data = yaml.safe_load(f)
    return data.get("questions", [])


def score(response: AgentResponse | Exception, question: dict[str, Any]) -> tuple[bool, str]:
    """Check whether a response satisfies the question's expected criteria."""
    if isinstance(response, Exception):
        return False, f"error: {response}"

    if question.get("expected_refusal"):
        refused = "cannot" in response.answer.lower() or "blocked" in response.answer.lower()
        return refused, "refused" if refused else "not refused"

    if question.get("expected_clarification"):
        asked = "?" in response.answer
        return asked, "asked" if asked else "did not ask"

    if fragments := question.get("expected_sql_contains"):
        sql = (response.sql or response.answer).upper()
        for fragment in fragments:
            if fragment.upper() not in sql:
                return False, f"SQL missing: {fragment!r}"

    return True, "ok"


async def run_eval(backend: str = "anthropic") -> None:
    """Run all benchmark questions and print a summary table."""
    questions_path = Path(__file__).parent / "questions.yaml"
    questions = load_questions(questions_path)

    runtime = AgentRuntime()
    results: list[dict[str, Any]] = []

    console.print(f"\n[bold]Lorekeeper eval — backend: {backend}[/bold]\n")

    for q in questions:
        console.print(f"  [dim]{q['id']}[/dim] {q['question'][:70]}")
        try:
            response: AgentResponse | Exception = await runtime.answer(q["question"])
        except Exception as exc:  # noqa: BLE001
            response = exc

        passed, reason = score(response, q)
        results.append({"id": q["id"], "passed": passed, "reason": reason})

    table = Table(title="\nResults", show_lines=False)
    table.add_column("ID", style="dim", width=5)
    table.add_column("Pass", width=6)
    table.add_column("Reason")

    for r in results:
        status = "[green]PASS[/green]" if r["passed"] else "[red]FAIL[/red]"
        table.add_row(r["id"], status, r["reason"])

    console.print(table)

    passed_count = sum(1 for r in results if r["passed"])
    total = len(results)
    pct = int(passed_count / total * 100) if total else 0
    console.print(f"\n[bold]{passed_count}/{total}[/bold] passed ({pct}%)\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default="anthropic", choices=["anthropic", "ollama"])
    args = parser.parse_args()

    asyncio.run(run_eval(backend=args.backend))
