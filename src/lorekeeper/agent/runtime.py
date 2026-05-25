"""Lorekeeper agent runtime skeleton."""

from __future__ import annotations

from pathlib import Path

from lorekeeper.core.config import Settings
from lorekeeper.core.contracts import LorekeeperRequest, LorekeeperResponse, LorekeeperTrace
from lorekeeper.mcp.client import McpClient
from lorekeeper.model.backend import Message, ModelBackend, NotConfiguredBackend
from lorekeeper.observability.tracing import TraceRecorder


class AgentRuntime:
    """Coordinate prompt loading, model turns, MCP tools, and traces."""

    def __init__(
        self,
        *,
        settings: Settings | None = None,
        backend: ModelBackend | None = None,
        mcp_clients: list[McpClient] | None = None,
        trace_recorder: TraceRecorder | None = None,
    ) -> None:
        self.settings = settings or Settings()
        self.backend = backend or NotConfiguredBackend()
        self.mcp_clients = mcp_clients or []
        self.trace_recorder = trace_recorder or TraceRecorder(self.settings.trace_dir)
        self.system_prompt = self._load_system_prompt(self.settings.prompt_path)

    async def answer(self, question: str) -> LorekeeperResponse:
        """Answer a data question.

        This skeleton records the contract and trace shape. The live agent loop
        is the next implementation step in the learning path.
        """
        request = LorekeeperRequest(question=question)
        trace = LorekeeperTrace(
            trace_id=request.trace_id,
            question=request.question,
            backend=self.backend.name,
            model=self.backend.model,
        )

        tools = []
        for client in self.mcp_clients:
            tools.extend(await client.list_tools())

        turn = self.backend.complete(
            system=self.system_prompt,
            messages=[Message(role="user", content=request.question)],
            tools=tools,
        )
        trace.final_answer = turn.content
        self.trace_recorder.write(trace)

        return LorekeeperResponse(
            trace_id=request.trace_id,
            status="failed" if self.backend.name == "not-configured" else "succeeded",
            answer=turn.content,
            tool_calls=trace.tool_calls,
        )

    @staticmethod
    def _load_system_prompt(path: Path) -> str:
        """Load the system prompt, falling back to a minimal role prompt."""
        if path.exists():
            return path.read_text(encoding="utf-8")
        return "You are Lorekeeper, a Data Specialist AI agent."
