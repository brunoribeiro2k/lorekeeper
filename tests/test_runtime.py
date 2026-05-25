"""Tests for the Lorekeeper runtime skeleton."""

from __future__ import annotations

from pathlib import Path

import pytest

from lorekeeper.config import Settings
from lorekeeper.runtime import AgentRuntime


def test_load_system_prompt_fallback(tmp_path: Path) -> None:
    """Runtime falls back gracefully when the prompt file is missing."""
    prompt = AgentRuntime._load_system_prompt(tmp_path / "missing.md")

    assert "Lorekeeper" in prompt


@pytest.mark.asyncio
async def test_runtime_returns_skeleton_response(tmp_path: Path) -> None:
    """The skeleton runtime returns a clear not-configured response."""
    settings = Settings(
        prompt_path=tmp_path / "missing.md",
        trace_dir=tmp_path / "traces",
    )
    runtime = AgentRuntime(settings=settings)

    response = await runtime.answer("What tables are in hive?")

    assert response.status == "failed"
    assert "skeleton is ready" in response.answer
    assert response.trace_id
    assert list((tmp_path / "traces").glob("*.jsonl"))
