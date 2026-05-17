# Learning Path

## Approach

Each phase produces something working end-to-end before adding the next layer. We use existing MCP servers rather than building from scratch, which means we reach the agent layer faster — that's where the real learning is.

Reference reading: *AI Agents with MCP* by Kyle Stratis.

## Phase 0 — Ground (Week 1–2)

**Goal:** Understand MCP conceptually and confirm the local environment works.

- Read the MCP specification at `modelcontextprotocol.io`. Understand the distinction between *tools*, *resources*, and *prompts*.
- Read Anthropic's tool use documentation. Understand how a model decides when to call a tool.
- Confirm local stack: Podman GPU passthrough working, Trino reachable at `localhost:8081`, Ollama serving `qwen2.5:14b`.
- Draw the architecture from `01-vision-and-architecture.md` from memory.

**Done when:** Can explain in plain language what an MCP server is, what an MCP client is, and what a tool call looks like in flight.

## Phase 1 — Deploy and learn Trino MCP server (Week 3–4)

**Goal:** A working Trino MCP server connected to the local Trino, with an AI client using it.

- Evaluate `txn2/mcp-trino` (Go) and `alaturqua/mcp-trino-python` (Python). Pick one based on ease of setup, tool completeness, and readability.
- Install and configure against the local Trino at `localhost:8081`.
- Connect it to Claude Desktop or Claude Code. Ask it to explore schemas and run queries.
- Study the tool list: what does each tool expose? What are the input schemas? What's missing?
- Test with real questions against the local data. Observe tool call sequences.
- Read the server's source code to understand how it wraps Trino's API. This is how you learn MCP server design without building one.

**Done when:** From an AI client, the question *"What tables are in the hive catalog?"* triggers the right tools and returns the right answer. *"Show me 10 orders"* returns data. Destructive SQL is rejected.

## Phase 2 — Deploy and learn OpenMetadata MCP (Week 5–6)

**Goal:** Metadata discovery via MCP, so the agent finds tables by meaning not just name.

- Run OpenMetadata locally via Podman compose.
- Ingest the local Trino catalog into OpenMetadata.
- Add descriptions and tags to tables so search has something to work with.
- Evaluate OpenMetadata's built-in MCP server vs `mcp-server-openmetadata` (PyPI). Pick one.
- Connect both MCP servers to a single AI client. Test the end-to-end loop: discover a table by description in OpenMetadata, then query it in Trino.
- Read the OpenMetadata MCP server's tool list. Understand what metadata it exposes.

**Done when:** From an AI client, asking *"Find a table about customer orders and show me 5 rows"* triggers metadata search then a Trino query.

## Phase 3 — Lorekeeper agent (Week 7–9)

**Goal:** A standalone agent with a real system prompt and a CLI.

- Write `prompts/lorekeeper-system.md`. Focus: discovery before SQL, partition awareness, CTE style, assumptions, clarifying questions.
- Build `agent/runtime.py` — the agent loop that connects to both MCP servers.
- Build `agent/cli.py` — `lorekeeper "which customers have pending shipments?"`
- Build `agent/models.py` with Anthropic backend first, then Ollama backend.
- Build the evaluation harness in `evals/`. Run after every prompt change.

**Done when:** `lorekeeper "<question>"` produces correct answers for at least 15 of 20 benchmark questions on Claude, 10 of 20 on local Qwen.

## Phase 4 — Agent composition (Week 10–12)

**Goal:** Lorekeeper callable by another agent.

- Study agent-to-agent communication patterns. Two main options: (a) Lorekeeper exposed as a tool to the parent agent, or (b) Lorekeeper wrapped as an MCP server itself.
- Build a minimal Streamwright that drafts Airflow DAGs and delegates data questions to Lorekeeper.
- Find or deploy an Airflow MCP server. Connect Streamwright to it.
- Test: Streamwright asked to *"Build a DAG that copies orders to a daily summary table"* calls Lorekeeper to discover the schema, then composes the DAG.

**Done when:** The composition works for at least one realistic example. Lorekeeper was reused unchanged from Phase 3.

## Phase 5 — Production hardening (Ongoing)

- Authentication on MCP servers
- Observability: structured logging of every tool call
- Cost tracking for API models
- PII detection and masking
- Eval expansion to 50+ questions
- Extend or fork MCP servers if tools are missing or insufficient

## Time budget

~1 hour focused per day. Working Lorekeeper by week 9.
