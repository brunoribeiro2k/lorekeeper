"""Model backend protocol and concrete implementations (Anthropic + Ollama)."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

import httpx
from anthropic import Anthropic
from pydantic import BaseModel


class Message(BaseModel):
    """A single conversation turn."""

    role: str
    content: str | list[dict[str, Any]]


@runtime_checkable
class ModelBackend(Protocol):
    """Common interface for model inference backends.

    Both AnthropicBackend and OllamaBackend implement this. Swapping backends
    is a config change — the agent loop in runtime.py never knows which one it's using.
    """

    def complete(
        self,
        system: str,
        messages: list[Message],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Run one completion turn and return the raw API response dict."""
        ...


class AnthropicBackend:
    """Anthropic API backend using the Messages API with tool use."""

    def __init__(self, model: str = "claude-sonnet-4-6") -> None:
        self.model = model
        self._client = Anthropic()

    def complete(
        self,
        system: str,
        messages: list[Message],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Run one completion turn via the Anthropic API."""
        response = self._client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=system,
            messages=[m.model_dump() for m in messages],
            tools=tools,  # type: ignore[arg-type]
        )
        return response.model_dump()


class OllamaBackend:
    """Local Ollama backend via its OpenAI-compatible /v1/chat/completions endpoint."""

    def __init__(
        self,
        model: str = "qwen2.5:14b",
        base_url: str = "http://localhost:11434",
    ) -> None:
        self.model = model
        self.base_url = base_url

    def complete(
        self,
        system: str,
        messages: list[Message],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Run one completion turn via Ollama's OpenAI-compatible endpoint."""
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}]
            + [m.model_dump() for m in messages],
            "tools": tools,
            "stream": False,
        }
        response = httpx.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            timeout=120.0,
        )
        response.raise_for_status()
        return response.json()
