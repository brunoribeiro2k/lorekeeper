"""MCP client interfaces and server registry for Lorekeeper."""

from __future__ import annotations

from typing import Any, Protocol

from pydantic import BaseModel, Field

from lorekeeper.config import Settings
from lorekeeper.models import ToolDefinition


class McpServerConfig(BaseModel):
    """Connection details for an external MCP server."""

    name: str
    url: str
    headers: dict[str, str] = Field(default_factory=dict)


class McpToolCall(BaseModel):
    """A namespaced MCP tool call requested by a model."""

    server: str
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class McpToolResult(BaseModel):
    """Normalized MCP tool result returned to the agent loop."""

    content: str
    raw: Any | None = None


class McpClient(Protocol):
    """Small interface the agent loop needs from an MCP client."""

    async def list_tools(self) -> list[ToolDefinition]:
        """Return tools exposed by one MCP server."""
        ...

    async def call_tool(self, call: McpToolCall) -> McpToolResult:
        """Execute one MCP tool call."""
        ...


def build_server_configs(settings: Settings) -> list[McpServerConfig]:
    """Build the known external MCP server configs from settings."""
    openmetadata_headers = {}
    if settings.openmetadata_token:
        openmetadata_headers["Authorization"] = f"Bearer {settings.openmetadata_token}"

    return [
        McpServerConfig(
            name="openmetadata",
            url=settings.openmetadata_mcp_url,
            headers=openmetadata_headers,
        ),
        McpServerConfig(
            name="trino",
            url=settings.trino_mcp_url,
        ),
    ]
