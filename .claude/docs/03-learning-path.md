# Learning Path

## Approach

Each phase produces something working end-to-end before adding the next layer. We use existing MCP servers rather than building from scratch — that's how we reach the agent layer faster, where the real learning is.

With 1 hour/day hands-on and Claude Code available for the coding work, each session should end with something observable: a server running, a tool call in a log, an answer on screen. Concepts are learned in conversation, not in solo reading blocks.

Reference reading: *AI Agents with MCP* by Kyle Stratis (read alongside phases, not upfront).

## MCP server choices (committed, not under evaluation)

- **Trino:** `alaturqua/mcp-trino-python` — Python source is readable; fits the stack; no Go toolchain.
- **OpenMetadata:** built-in MCP server shipped with OpenMetadata 1.8+ — zero extra install, officially maintained.

---

## Phase 0 — Ground (Week 1)

**Goal:** Understand MCP concepts well enough to reason about tool calls, and confirm the local stack works.

**Session 1 — Concepts (1h):**
- Talk through MCP with Claude Code: what is a server, client, tool, resource, prompt?
- Trace one full tool call in flight: model → client → server → response.
- Exit: can draw the Lorekeeper architecture from memory and explain each hop.

**Session 2 — Environment check (1h):**
- Confirm Trino reachable: `curl localhost:8081/v1/info`.
- Confirm Ollama: `ollama run qwen2.5:14b` responds.
- Confirm Podman GPU: `podman run --device nvidia.com/gpu=all nvidia/cuda nvidia-smi`.
- Exit: all three green.

**Session 3 — Tool use mental model (1h):**
- Ask Claude Code to show what a raw MCP tool call JSON looks like.
- Ask: how does a model decide to call a tool vs answer directly?
- Read the `alaturqua/mcp-trino-python` README together. Identify the tool list.
- Exit: can name three Trino MCP tools and their purpose without looking.

**Done when:** Can explain MCP in plain language, stack is confirmed, and you've seen a tool call schema.

---

## Phase 1 — Trino MCP live (Weeks 2–3)

**Goal:** `alaturqua/mcp-trino-python` running against local Trino, with an AI client querying it.

**Session 4 — Install and configure (1h):**
- `pip install mcp-trino-python` (or clone + install editable).
- Write `trino_mcp_config.json` pointing at `localhost:8081`.
- Start the server, confirm it starts without error.
- Exit: server process running.

**Session 5 — Connect to Claude Code (1h):**
- Add the Trino MCP server to Claude Code's MCP config (`.claude/mcp.json`).
- Ask: *"What catalogs are available?"* — watch the tool call in the log.
- Exit: tool call visible, answer returned.

**Session 6 — Schema exploration (1h):**
- Ask: *"What tables are in the hive catalog?"* — observe the tool sequence.
- Ask: *"Describe the orders table."*
- Note which tools were called and in what order. Write it down.
- Exit: schema exploration working end-to-end.

**Session 7 — Data queries (1h):**
- Ask: *"Show me 10 orders."*
- Ask: *"What's the total order value by customer?"*
- Try a destructive query — confirm it is rejected.
- Exit: SELECT works, DDL/DML blocked.

**Session 8 — Source reading (1h):**
- Read the server's source with Claude Code. Focus: how is a tool defined? How does it call Trino's REST API? How is the response mapped back to MCP?
- Exit: can explain how one tool (e.g. `run_query`) works end-to-end.

**Session 9 — Gaps and retrospective (1h):**
- What tools are missing? What would Lorekeeper need that isn't there?
- Write a short gap list in `.claude/docs/` (or a comment in the config).
- Exit: gap list written.

**Done when:** *"What tables are in the hive catalog?"* returns the right answer. *"Show me 10 orders"* returns data. Destructive SQL is rejected. You can explain how the server works.

---

## Phase 2 — OpenMetadata + both MCPs (Weeks 4–6)

**Goal:** Metadata discovery via MCP so the agent finds tables by meaning, not just name. Both servers connected to one client.

**Session 10–11 — Deploy OpenMetadata (2h across 2 days):**
- Download the official Podman compose file for OpenMetadata 1.8+.
- `podman compose up -d` — confirm UI reachable at `localhost:8585`.
- Exit: OpenMetadata UI loads.

**Session 12 — Ingest Trino catalog (1h):**
- Configure a Trino connector in OpenMetadata UI.
- Run ingestion — confirm tables appear in the catalog.
- Exit: at least one table visible in OpenMetadata with schema.

**Session 13 — Enrich metadata (1h):**
- Add descriptions to 3–5 tables.
- Add tags (e.g. `orders`, `customers`).
- This is what makes semantic search work later.
- Exit: tables have descriptions and tags.

**Session 14 — Enable and connect built-in MCP server (1h):**
- Enable OpenMetadata's built-in MCP server in its config.
- Add it to Claude Code's MCP config alongside the Trino server.
- Ask: *"What tables exist about orders?"* — watch which server is called.
- Exit: two MCP servers visible in Claude Code.

**Session 15 — End-to-end loop (1h):**
- Ask: *"Find a table about customer orders and show me 5 rows."*
- Observe: OpenMetadata search → table name → Trino query.
- This is the Lorekeeper core loop, manually triggered.
- Exit: full loop works at least once.

**Session 16 — OpenMetadata MCP source reading (1h):**
- Read the built-in server's tool list and schemas.
- Note: what metadata does it expose? What's missing for Lorekeeper?
- Exit: tool list documented, gaps noted.

**Done when:** From an AI client, asking *"Find a table about customer orders and show me 5 rows"* triggers metadata search then a Trino query — two servers cooperating.

---

## Phase 3 — Lorekeeper agent (Weeks 7–10)

**Goal:** A standalone agent with a real system prompt and a working CLI.

Claude Code writes the boilerplate; your job is to shape the prompt, test the outputs, and tune.

**Week 7 — System prompt and skeleton (4 sessions):**
- Session 17: Draft `prompts/lorekeeper-system.md` together. Key behaviors: discovery before SQL, partition awareness, CTE style, clarifying questions, stating assumptions.
- Session 18: Claude Code scaffolds `pyproject.toml`, `agent/cli.py` entrypoint, `agent/models.py` with Anthropic backend.
- Session 19: Wire the CLI to both MCP servers. `lorekeeper "list tables"` works.
- Session 20: First real question end-to-end. Fix what breaks.

**Week 8 — Eval harness (3 sessions):**
- Session 21: Write `evals/questions.yaml` — 20 benchmark questions covering schema discovery, aggregation, filtering, ambiguity.
- Session 22: Claude Code builds `evals/run_eval.py`.
- Session 23: Run baseline eval. Score it. Fix the most common failure mode.

**Week 9 — Tuning (3 sessions):**
- Session 24–26: Iterate on the system prompt based on eval results. Run eval after each change. Target: 15/20 on Claude.

**Week 10 — Ollama backend (2 sessions):**
- Session 27: Add Ollama backend to `agent/models.py`. Switch to `qwen2.5:14b`.
- Session 28: Run eval on Qwen. Target: 10/20. Document failure modes.

**Done when:** `lorekeeper "<question>"` produces correct answers for ≥15/20 on Claude, ≥10/20 on local Qwen.

---

## Phase 4 — Agent composition (Weeks 11–13)

**Goal:** Lorekeeper callable by another agent. Validate the specialist pattern.

- Session 29: Study agent-to-agent patterns with Claude Code. Choose: (a) Lorekeeper as a tool exposed to a parent agent, or (b) Lorekeeper wrapped as an MCP server.
- Sessions 30–32: Build a minimal Streamwright agent that drafts Airflow DAGs and delegates data questions to Lorekeeper.
- Session 33: Find or configure an Airflow MCP server.
- Session 34–35: Test: *"Build a DAG that copies orders to a daily summary table"* — Streamwright calls Lorekeeper for schema, then composes the DAG.

**Done when:** The composition works for at least one realistic example. Lorekeeper was reused unchanged from Phase 3.

---

## Phase 5 — Production hardening (Ongoing)

Pick one item per sprint based on what's actually painful:

- Authentication on MCP servers
- Structured logging of every tool call
- Cost tracking for API models
- PII detection and masking
- Eval expansion to 50+ questions
- Fork or extend MCP servers where tools are missing

---

## Session rhythm

Each 1-hour session should follow this pattern:
1. **5 min:** State what you're trying to accomplish and where you left off.
2. **45 min:** Hands-on work with Claude Code — configure, test, explore, ask questions.
3. **10 min:** Write down what you learned or what broke. Update the gap list if needed.

Avoid starting sessions with reading. Start with doing; reading happens when you hit something you don't understand.

## Time summary

| Phase | Sessions | Calendar weeks |
|-------|----------|----------------|
| 0 — Ground | 3 | 1 |
| 1 — Trino MCP | 6 | 2–3 |
| 2 — OpenMetadata | 7 | 4–6 |
| 3 — Lorekeeper agent | 12 | 7–10 |
| 4 — Composition | 7 | 11–13 |

Working Lorekeeper by **week 10**. Agent composition complete by **week 13**.
