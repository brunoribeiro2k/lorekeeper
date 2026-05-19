# Learning Path

## Approach

Each phase produces something working end-to-end before adding the next layer. We use existing MCP servers rather than building from scratch — that's how we reach the agent layer faster, where the real learning is.

With 1 hour/day hands-on and Claude Code available for the coding work, each session should end with something observable: a server running, a tool call in a log, an answer on screen. Concepts are learned in conversation, not in solo reading blocks.

Reference reading: *AI Agents with MCP* by Kyle Stratis (read alongside phases, not upfront).

## MCP server choices (committed, not under evaluation)

- **OpenMetadata:** built-in MCP server, installed by default in OpenMetadata 1.12.x — zero extra install, officially maintained. Confirmed in [1.12.x docs](https://docs.open-metadata.org/v1.12.x/how-to-guides/mcp).
- **Trino:** `alaturqua/mcp-trino-python` — Python source is readable; fits the stack; no Go toolchain.

OpenMetadata comes first because its MCP server is already part of the product — no separate package to install or maintain.

## Local model selection (per machine)

The Ollama backend model is configured via `.env`:

```
# GPU laptop (RTX 3070)
LOREKEEPER_OLLAMA_MODEL=qwen2.5:14b

# Work laptop (CPU-only, 32GB RAM)
LOREKEEPER_OLLAMA_MODEL=qwen2.5:7b
```

`agent/models.py` reads this at startup. The model affects eval scores, so targets differ per setup — don't compare scores across machines.

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
- Read the OpenMetadata MCP docs together. Identify the tool list.
- Exit: can name three OpenMetadata MCP tools and their purpose without looking.

**Done when:** Can explain MCP in plain language, stack is confirmed, and you've seen a tool call schema.

---

## Phase 1 — OpenMetadata MCP live (Weeks 2–4)

**Goal:** OpenMetadata 1.12.18 deployed with its built-in MCP server connected to an AI client. Trino catalog ingested and enriched so metadata search has something to work with.

**Session 4–5 — Deploy OpenMetadata (2h across 2 days):**
- Download the official Podman compose file for OpenMetadata 1.12.x.
- `podman compose up -d` — confirm UI reachable at `localhost:8585`.
- Exit: OpenMetadata UI loads, services healthy.

**Session 6 — Connect built-in MCP to Claude Code (1h):**
- The MCP server is installed by default — locate it in the OpenMetadata app settings and enable it.
- Add it to Claude Code's MCP config (`.claude/mcp.json`).
- Ask: *"What entities are available?"* — watch the tool call in the log.
- Exit: tool call visible, answer returned.

**Session 7 — Ingest Trino catalog (1h):**
- Configure a Trino connector in OpenMetadata UI.
- Run ingestion — confirm tables appear in the catalog.
- Exit: at least one table visible in OpenMetadata with schema.

**Session 8 — Enrich metadata (1h):**
- Add descriptions to 3–5 tables.
- Add tags (e.g. `orders`, `customers`).
- This is what makes semantic search work later.
- Exit: tables have descriptions and tags.

**Session 9 — Explore via MCP (1h):**
- Ask: *"Find tables related to customer orders."*
- Ask: *"What does the orders table contain?"*
- Note which tools were called and in what order. Write it down.
- Exit: metadata search working end-to-end via MCP.

**Session 10 — Tool list and gaps (1h):**
- Read the built-in server's full tool list with Claude Code.
- What metadata does it expose? What's missing for Lorekeeper?
- Write a gap list in `.claude/docs/`.
- Exit: tool list documented.

**Done when:** From an AI client, *"Find tables related to customer orders"* returns meaningful results from OpenMetadata via MCP tool calls.

---

## Phase 2 — Trino MCP + both servers live (Weeks 5–6)

**Goal:** `alaturqua/mcp-trino-python` running against local Trino, both MCP servers connected to one client, end-to-end loop working.

**Session 11 — Install and configure Trino MCP (1h):**
- `pip install mcp-trino-python` (or clone + install editable).
- Write `trino_mcp_config.json` pointing at `localhost:8081`.
- Start the server, confirm it starts without error.
- Exit: server process running.

**Session 12 — Connect to Claude Code (1h):**
- Add the Trino MCP server to Claude Code's MCP config alongside OpenMetadata.
- Ask: *"What catalogs are available?"* — watch the tool call in the log.
- Exit: both MCP servers visible, tool calls distinguishable.

**Session 13 — Schema exploration (1h):**
- Ask: *"What tables are in the hive catalog?"* — observe the tool sequence.
- Ask: *"Describe the orders table."*
- Note which server was called for each question.
- Exit: schema exploration working end-to-end.

**Session 14 — Data queries and safety check (1h):**
- Ask: *"Show me 10 orders."*
- Ask: *"What's the total order value by customer?"*
- Try a destructive query — confirm it is rejected.
- Exit: SELECT works, DDL/DML blocked.

**Session 15 — End-to-end loop (1h):**
- Ask: *"Find a table about customer orders and show me 5 rows."*
- Observe: OpenMetadata search → table name → Trino query.
- This is the Lorekeeper core loop, manually triggered.
- Exit: full loop works at least once.

**Session 16 — Trino MCP source reading + retrospective (1h):**
- Read the server's source with Claude Code. Focus: how is a tool defined? How does it call Trino's REST API?
- Update the gap list with anything discovered.
- Exit: can explain how `run_query` works end-to-end.

**Done when:** *"Find a table about customer orders and show me 5 rows"* triggers OpenMetadata search then a Trino query — two servers cooperating.

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
- Session 27: Add Ollama backend to `agent/models.py`. Read model from `LOREKEEPER_OLLAMA_MODEL` env var (default: `qwen2.5:14b`). Set per machine in `.env`.
- Session 28: Run eval on Qwen. Targets: ≥10/20 on `qwen2.5:14b` (GPU laptop), ≥7/20 on `qwen2.5:7b` (work laptop). Document failure modes.

**Done when:** `lorekeeper "<question>"` produces correct answers for ≥15/20 on Claude, ≥10/20 on Qwen 14B, ≥7/20 on Qwen 7B.

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
| 1 — OpenMetadata MCP | 7 | 2–4 |
| 2 — Trino MCP + both | 6 | 5–6 |
| 3 — Lorekeeper agent | 12 | 7–10 |
| 4 — Composition | 7 | 11–13 |

Working Lorekeeper by **week 10**. Agent composition complete by **week 13**.
