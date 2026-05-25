"""Evaluation harness skeleton for Lorekeeper.

Usage:
    uv run python evals/run_eval.py
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.table import Table

sys.path.insert(0, str(Path(__file__).parent.parent))

from lorekeeper.contracts import EvalQuestion, LorekeeperResponse
from lorekeeper.runtime import AgentRuntime

console = Console()


def load_questions(path: Path) -> list[EvalQuestion]:
    """Load benchmark questions from YAML."""
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return [EvalQuestion(**item) for item in data.get("questions", [])]


def score(response: LorekeeperResponse | Exception, question: EvalQuestion) -> dict[str, str]:
    """Score one response across the planned eval layers."""
    if isinstance(response, Exception):
        reason = f"error: {response}"
        return {
            "tool": "fail",
            "sql": "fail",
            "execution": "fail",
            "answer": reason,
            "safety": "fail",
        }

    sql_text = (response.sql or response.answer).upper()
    expected_sql = all(fragment.upper() in sql_text for fragment in question.expected_sql_contains)
    refused = response.status == "refused" or bool(response.refusal_reason)
    clarified = response.status == "clarification_needed" or bool(response.clarification_question)

    return {
        "tool": "pending" if question.expected_tool else "n/a",
        "sql": "pass" if expected_sql else "fail",
        "execution": "pending",
        "answer": "pending",
        "safety": _score_safety(question, refused, clarified),
    }


def _score_safety(question: EvalQuestion, refused: bool, clarified: bool) -> str:
    """Score refusal and clarification expectations."""
    if question.expected_refusal:
        return "pass" if refused else "fail"
    if question.expected_clarification:
        return "pass" if clarified else "fail"
    return "n/a"


async def run_eval() -> None:
    """Run all benchmark questions and print layered skeleton scores."""
    questions = load_questions(Path(__file__).parent / "questions.yaml")
    runtime = AgentRuntime()
    rows: list[dict[str, Any]] = []

    for question in questions:
        try:
            response: LorekeeperResponse | Exception = await runtime.answer(question.question)
        except Exception as exc:  # noqa: BLE001
            response = exc
        rows.append({"id": question.id, **score(response, question)})

    table = Table(title="Lorekeeper Eval Skeleton")
    table.add_column("ID", style="dim")
    table.add_column("Tool")
    table.add_column("SQL")
    table.add_column("Execution")
    table.add_column("Answer")
    table.add_column("Safety")

    for row in rows:
        table.add_row(
            row["id"],
            row["tool"],
            row["sql"],
            row["execution"],
            row["answer"],
            row["safety"],
        )

    console.print(table)
    console.print(
        "\n[dim]Pending layers become meaningful after live MCP clients and model "
        "adapters are wired.[/dim]"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args()
    asyncio.run(run_eval())
