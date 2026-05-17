"""Tests for AgentRuntime and Settings.

Phase 1 tests are intentionally narrow — they validate configuration loading
and pure logic that doesn't need live MCP servers. Integration tests come in Phase 3.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from lorekeeper.runtime import AgentRuntime, Settings


def test_settings_defaults() -> None:
    """Settings load with sane defaults when no .env file is present."""
    s = Settings()
    assert s.trino_host == "localhost"
    assert s.trino_port == 8081
    assert s.anthropic_model.startswith("claude")


def test_settings_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Environment variables override defaults."""
    monkeypatch.setenv("TRINO_HOST", "trino.internal")
    monkeypatch.setenv("TRINO_PORT", "9090")
    s = Settings()
    assert s.trino_host == "trino.internal"
    assert s.trino_port == 9090


def test_system_prompt_fallback() -> None:
    """When the prompt file is missing, runtime falls back gracefully."""
    with patch("pathlib.Path.exists", return_value=False):
        runtime = AgentRuntime.__new__(AgentRuntime)
        runtime.settings = Settings()
        prompt = runtime._load_system_prompt()
    assert "Lorekeeper" in prompt


def test_extract_text_from_anthropic_response() -> None:
    """_extract_text parses Anthropic-style content blocks."""
    runtime = AgentRuntime.__new__(AgentRuntime)
    response = {
        "content": [
            {"type": "text", "text": "Here is the answer."},
            {"type": "tool_use", "name": "trino__execute_query", "input": {}},
        ]
    }
    assert runtime._extract_text(response) == "Here is the answer."


def test_extract_tool_calls() -> None:
    """_extract_tool_calls returns only tool_use blocks."""
    runtime = AgentRuntime.__new__(AgentRuntime)
    response = {
        "content": [
            {"type": "text", "text": "Calling tool…"},
            {"type": "tool_use", "id": "tu_1", "name": "trino__list_tables", "input": {}},
        ]
    }
    calls = runtime._extract_tool_calls(response)
    assert len(calls) == 1
    assert calls[0]["name"] == "trino__list_tables"
