"""Agent runtime: MCP client sessions and the main agentic loop."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from lorekeeper.models import AnthropicBackend, Message, ModelBackend


class Settings(BaseSettings):
    """Runtime configuration loaded from .env (or environment variables)."""

    # Trino MCP server
    trino_mcp_command: str = "mcp-trino"
    trino_host: str = "localhost"
    trino_port: int = 8081
    trino_user: str = "admin"
    trino_catalog: str = "hive"

    # OpenMetadata MCP server
    openmetadata_mcp_command: str = "uvx"
    openmetadata_mcp_args: str = "mcp-server-openmetadata"
    openmetadata_url: str = "http://localhost:8585"
    openmetadata_token: str = ""

    # Model selection
    anthropic_model: str = "claude-sonnet-4-6"
    ollama_model: str = "qwen2.5:14b"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


class AgentResponse(BaseModel):
    """Structured result returned by AgentRuntime.answer()."""

    answer: str
    sql: str | None = None
    tables_used: list[str] = []
    assumptions: list[str] = []
    tool_calls: int = 0


class AgentRuntime:
    """Orchestrates MCP sessions and the model backend to answer data questions.

    Typical call sequence:
        runtime = AgentRuntime()
        response = await runtime.answer("Which customers have pending shipments?")

    The runtime connects to both MCP servers, collects their tool lists, and
    runs an agentic loop: model → tool calls → model → … → final answer.
    """

    def __init__(self, backend: ModelBackend | None = None) -> None:
        self.settings = Settings()
        self.backend: ModelBackend = backend or AnthropicBackend(
            model=self.settings.anthropic_model
        )
        self._system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load the system prompt from prompts/lorekeeper-system.md."""
        path = Path(__file__).parent.parent / "prompts" / "lorekeeper-system.md"
        if path.exists():
            return path.read_text()
        return "You are Lorekeeper, a Data Specialist AI agent."

    async def answer(self, question: str) -> AgentResponse:
        """Answer a natural-language data question end-to-end.

        Opens MCP sessions to Trino and OpenMetadata, runs the agent loop,
        and returns a structured response.
        """
        trino_params = StdioServerParameters(
            command=self.settings.trino_mcp_command,
            env={
                "TRINO_HOST": self.settings.trino_host,
                "TRINO_PORT": str(self.settings.trino_port),
                "TRINO_USER": self.settings.trino_user,
                "TRINO_CATALOG": self.settings.trino_catalog,
            },
        )
        om_params = StdioServerParameters(
            command=self.settings.openmetadata_mcp_command,
            args=self.settings.openmetadata_mcp_args.split(),
            env={
                "OPENMETADATA_URL": self.settings.openmetadata_url,
                "OPENMETADATA_TOKEN": self.settings.openmetadata_token,
            },
        )

        async with (
            stdio_client(trino_params) as (trino_read, trino_write),
            stdio_client(om_params) as (om_read, om_write),
        ):
            async with (
                ClientSession(trino_read, trino_write) as trino_session,
                ClientSession(om_read, om_write) as om_session,
            ):
                await trino_session.initialize()
                await om_session.initialize()
                return await self._run_loop(question, trino_session, om_session)

    async def _run_loop(
        self,
        question: str,
        trino: ClientSession,
        openmetadata: ClientSession,
    ) -> AgentResponse:
        """Run the agentic loop: call model → dispatch tool calls → repeat.

        Tools from each MCP session are namespaced with a prefix so the model
        can call them unambiguously: trino__execute_query, openmetadata__search_tables, etc.
        """
        trino_tools = await self._session_tools(trino, prefix="trino")
        om_tools = await self._session_tools(openmetadata, prefix="openmetadata")
        all_tools = trino_tools + om_tools

        messages: list[Message] = [Message(role="user", content=question)]
        tool_call_count = 0

        while True:
            response = self.backend.complete(
                system=self._system_prompt,
                messages=messages,
                tools=all_tools,
            )
            stop_reason = response.get("stop_reason") or response.get("finish_reason")

            if stop_reason in ("end_turn", "stop"):
                text = self._extract_text(response)
                return AgentResponse(answer=text, tool_calls=tool_call_count)

            if stop_reason in ("tool_use", "tool_calls"):
                tool_calls = self._extract_tool_calls(response)
                tool_call_count += len(tool_calls)
                tool_results = []
                for call in tool_calls:
                    result = await self._dispatch(call, trino, openmetadata)
                    tool_results.append(result)
                messages.append(Message(role="assistant", content=response.get("content", [])))
                messages.append(Message(role="user", content=tool_results))
                continue

            break

        return AgentResponse(answer="No answer produced.", tool_calls=tool_call_count)

    async def _session_tools(
        self, session: ClientSession, prefix: str
    ) -> list[dict[str, Any]]:
        """Collect tools from an MCP session and namespace them with prefix."""
        result = await session.list_tools()
        return [
            {
                "name": f"{prefix}__{tool.name}",
                "description": tool.description or "",
                "input_schema": tool.inputSchema,
            }
            for tool in result.tools
        ]

    async def _dispatch(
        self,
        call: dict[str, Any],
        trino: ClientSession,
        openmetadata: ClientSession,
    ) -> dict[str, Any]:
        """Route a tool call to the correct MCP session based on its prefix."""
        name: str = call["name"]
        inputs: dict[str, Any] = call.get("input", {})

        if name.startswith("trino__"):
            result = await trino.call_tool(name[len("trino__"):], inputs)
        elif name.startswith("openmetadata__"):
            result = await openmetadata.call_tool(name[len("openmetadata__"):], inputs)
        else:
            return {"tool_use_id": call.get("id", ""), "content": f"Unknown tool: {name}"}

        content = result.content[0].text if result.content else ""
        return {"tool_use_id": call.get("id", ""), "content": content}

    def _extract_text(self, response: dict[str, Any]) -> str:
        """Extract plain text from a model response content block list."""
        content = response.get("content", [])
        if isinstance(content, list):
            return " ".join(
                block.get("text", "")
                for block in content
                if block.get("type") == "text"
            )
        return str(content)

    def _extract_tool_calls(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract tool_use blocks from a model response."""
        content = response.get("content", [])
        if isinstance(content, list):
            return [block for block in content if block.get("type") == "tool_use"]
        return []
