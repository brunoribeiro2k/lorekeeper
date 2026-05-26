"""Model backend interfaces used by the agent loop."""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single conversation turn sent to a model backend."""

    role: str
    content: str | list[dict[str, Any]]


class ToolDefinition(BaseModel):
    """Tool metadata exposed to a model."""

    name: str
    description: str = ""
    input_schema: dict[str, Any] = Field(default_factory=dict)


class ModelTurn(BaseModel):
    """A model response for one agent-loop turn."""

    content: str = ""
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    stop_reason: str = "stop"


class ModelBackend(Protocol):
    """Common interface for Anthropic, Ollama, and test backends."""

    name: str
    model: str

    def complete(
        self,
        *,
        system: str,
        messages: list[Message],
        tools: list[ToolDefinition],
    ) -> ModelTurn:
        """Run one model turn."""
        ...


class NotConfiguredBackend:
    """Placeholder backend used until a concrete model adapter is wired."""

    name = "not-configured"
    model = "none"

    def complete(
        self,
        *,
        system: str,
        messages: list[Message],
        tools: list[ToolDefinition],
    ) -> ModelTurn:
        """Return a clear skeleton response instead of calling a live model."""
        del system, messages, tools
        return ModelTurn(
            content=(
                "Lorekeeper's project skeleton is ready. Wire a concrete model "
                "backend and MCP clients to answer live data questions."
            )
        )
