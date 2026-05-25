"""Tests for Lorekeeper public contracts."""

from __future__ import annotations

from lorekeeper.contracts import LorekeeperRequest, LorekeeperResponse, ToolCallTrace


def test_request_generates_trace_id() -> None:
    """A request gets a trace id when one is not supplied."""
    request = LorekeeperRequest(question="What tables are in hive?")

    assert request.trace_id


def test_response_defaults_are_empty_lists() -> None:
    """Response list fields are independent empty lists by default."""
    first = LorekeeperResponse(trace_id="one", status="succeeded", answer="ok")
    second = LorekeeperResponse(trace_id="two", status="succeeded", answer="ok")

    first.assumptions.append("orders means hive.sales.orders")

    assert second.assumptions == []


def test_tool_call_trace_records_server_and_tool() -> None:
    """Tool call traces preserve MCP server and tool names."""
    trace = ToolCallTrace(
        server="trino",
        tool_name="execute_query",
        arguments={"query": "SELECT 1"},
    )

    assert trace.server == "trino"
    assert trace.tool_name == "execute_query"
