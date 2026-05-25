"""Public contracts for Lorekeeper requests, responses, and traces."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

RunStatus = Literal["succeeded", "clarification_needed", "refused", "failed"]


class LorekeeperRequest(BaseModel):
    """A natural-language data question submitted to Lorekeeper."""

    question: str
    trace_id: str = Field(default_factory=lambda: uuid4().hex)


class ToolCallTrace(BaseModel):
    """A single MCP tool call made during an agent run."""

    server: str
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    result_summary: str | None = None
    latency_ms: float | None = None
    error: str | None = None


class LorekeeperTrace(BaseModel):
    """Debug record for one Lorekeeper run."""

    trace_id: str
    question: str
    backend: str
    model: str
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    finished_at: datetime | None = None
    tool_calls: list[ToolCallTrace] = Field(default_factory=list)
    generated_sql: str | None = None
    row_count: int | None = None
    final_answer: str | None = None
    assumptions: list[str] = Field(default_factory=list)
    clarification_question: str | None = None
    refusal_reason: str | None = None
    error: str | None = None


class LorekeeperResponse(BaseModel):
    """Structured response returned by Lorekeeper."""

    trace_id: str
    status: RunStatus
    answer: str
    sql: str | None = None
    tables_used: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    clarification_question: str | None = None
    refusal_reason: str | None = None
    tool_calls: list[ToolCallTrace] = Field(default_factory=list)


class EvalQuestion(BaseModel):
    """One benchmark question and its expected behaviours."""

    id: str
    question: str
    expected_tool: str | None = None
    expected_sql_contains: list[str] = Field(default_factory=list)
    expected_min_rows: int | None = None
    expected_refusal: bool = False
    expected_clarification: bool = False
    notes: str = ""
