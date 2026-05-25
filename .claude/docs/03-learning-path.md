# Learning Path

## What we're building

Lorekeeper is a Data Specialist agent. It receives a natural-language question, uses MCP tools to discover schema and run SQL, and returns an answer. The MCP servers (OpenMetadata, Trino) are pre-built infrastructure — we consume them, we don't study them.

The interesting work is: **the agent loop, the system prompt, and the evals.**

Each phase produces something you can run and observe. Claude Code handles boilerplate; the focus is on shaping agent behaviour and verifying it works.

## MCP servers (prerequisites — not managed here)

Both are registered at user scope in Claude Code. They must be running before any session.

- **OpenMetadata:** built-in MCP at `http://localhost:8585/mcp`. Registered user-scoped. Tools: `search_metadata`, `patch_entity`, `get_entity_details`, etc.
- **Trino:** `alaturqua/mcp-trino-python`, managed by `local-env/trino-local`. HTTP at `http://localhost:8082/mcp`. Registered user-scoped.

## Local model (per machine)

```
# Primary laptop (GPU — RTX 3070)
LOREKEEPER_OLLAMA_MODEL=qwen2.5:14b

# Secondary laptop (RAM — CPU-only, 32 GB)
LOREKEEPER_OLLAMA_MODEL=qwen2.5:7b
```

Set in `.env`. `agent/models.py` reads it at startup.

---

## Current state (as of Phase 2 complete)

- ✅ OpenMetadata MCP connected, registered user-scoped
- ✅ Trino catalog ingested into OpenMetadata (8 tables across hive + iceberg)
- ✅ Metadata enriched (descriptions + Domain tags on all 8 tables)
- ✅ `search_metadata("customer orders")` returns correct results via MCP
- ✅ Trino MCP running (`local-env/trino-local`), registered user-scoped at `localhost:8082/mcp`
- ✅ `show_catalogs` confirmed via MCP: hive, iceberg, system
- ⬜ Full loop (metadata → SQL → answer) not yet verified end-to-end
- ⬜ Golden traces not yet captured
- ⬜ Standalone Lorekeeper agent not yet built

---

## Phase 2 — MCP servers wired ✅

**Done.** Both servers connected, user-scoped, visible in `claude mcp list`.

**Done when:** Both MCP servers are reachable, registered, and their basic tools work independently.

---

## Phase 2.5 — Golden traces (2 sessions)

**Goal:** Capture the ideal behaviour before building the standalone agent.

The standalone agent should imitate a trace we have already seen work manually. This phase produces reference transcripts, not production code.

**Session 9 — Golden trace: simple discovery + query (1h):**
- Ask via Claude Code: *"Find a table about customer orders and show me 5 rows."*
- Record the full sequence:
  - user question
  - OpenMetadata search terms and results
  - selected table FQN
  - schema/partition details read
  - Trino SQL
  - result rows
  - final answer and assumptions
- Save the trace in `.claude/docs/` or a session note.
- Exit: one clean reference trace exists for the simplest useful workflow.

**Session 10 — Golden traces: edge cases (1h):**
- Capture at least three more manual traces:
  - partition-aware query: *"How many orders were placed last month?"*
  - ambiguous question: *"What is the revenue?"*
  - destructive request: *"Drop the customers table."*
- Note where the answer depends on prompt judgement vs. MCP/server guardrails.
- Exit: reference traces cover success, ambiguity, partition filtering, and refusal.

**Done when:** We can point to concrete traces that define how Lorekeeper should behave.

---

## Phase 3 — Lorekeeper agent (6–8 sessions)

**Goal:** A standalone CLI agent. `lorekeeper "how many orders per customer?"` works.

Claude Code scaffolds the code. Your job: shape agent behaviour, compare runs against the golden traces, and verify outputs.

**Session 11 — Behaviour contract + eval rubric (1h):**
- Define Lorekeeper's input/output contract:
  - input question
  - final answer
  - SQL, if executed
  - tables used
  - assumptions
  - clarifying question, if needed
  - refusal reason, if blocked
  - trace id
- Define the eval rubric before writing the harness:
  - correct MCP sequence
  - correct table discovery
  - fully qualified SQL
  - partition filters where needed
  - safe refusal for writes
  - one clarifying question for ambiguity
  - answer grounded in query results
- Exit: the agent has a written contract and scoring rubric.

**Session 12 — Scaffold + system prompt (1h):**
- Claude Code generates: `pyproject.toml`, `agent/cli.py`, `agent/runtime.py`, `agent/models.py`.
- Draft `prompts/lorekeeper-system.md` together. Key behaviours:
  - Always search metadata before writing SQL
  - Use fully qualified table names (`catalog.schema.table`)
  - Filter on partition columns when present
  - State assumptions explicitly
  - Ask one clarifying question when the request is ambiguous
- Exit: `lorekeeper "list tables"` runs without crashing.

**Session 13 — Wire MCP servers into the agent loop (1h):**
- `agent/runtime.py` connects to both MCP servers and executes the tool call loop.
- The loop: receive question → call tools as needed → return answer.
- Exit: `lorekeeper "find tables about orders"` calls `search_metadata` and returns results.

**Session 14 — First real question end-to-end (1h):**
- `lorekeeper "how many orders per customer?"` → discovery → SQL → answer.
- Fix what breaks. Focus on the loop, not the prompt.
- Exit: at least one realistic question answered correctly.

**Session 15 — Structured traces (1h):**
- Record every run to a local trace file:
  - model backend and model name
  - question
  - tool calls and arguments
  - tool results summary
  - generated SQL
  - row count
  - final answer
  - assumptions/refusals/clarifications
  - latency and errors
- Use the golden traces as examples of what a good trace should show.
- Exit: every run leaves enough evidence to debug failures without guessing.

**Session 16 — Eval harness + baseline (1h):**
- Write `evals/questions.yaml` — 20 questions covering: schema discovery, aggregation, filtering, partition-awareness, ambiguity handling.
- Claude Code builds `evals/run_eval.py`.
- Score in layers:
  - tool routing
  - SQL shape
  - SQL execution
  - final answer
  - assumptions/clarification/refusal
- Run baseline. Identify the most common failure mode.
- Exit: baseline score recorded with layered failure categories.

**Session 17 — Prompt tuning (1h):**
- Fix the top failure mode by editing `prompts/lorekeeper-system.md`.
- Re-run eval. Target: ≥15/20 on Claude.
- Exit: score improved, at least one prompt change validated by eval.

**Session 18 — Ollama backend (1h):**
- Add Ollama backend to `agent/models.py`. Switch via `LOREKEEPER_OLLAMA_MODEL`.
- Run eval on Qwen. Targets: ≥10/20 on `qwen2.5:14b`, ≥7/20 on `qwen2.5:7b`.
- Document failure modes specific to local models (tool call formatting, hallucinated FQNs, etc.).
- Exit: both Claude and Ollama backends working, eval scores recorded.

**Done when:** `lorekeeper "<question>"` produces correct answers for ≥15/20 on Claude, ≥10/20 on Qwen 14B, ≥7/20 on Qwen 7B.

---

## Phase 4 — Agent composition (5 sessions)

**Goal:** Lorekeeper callable by another agent. Validate the specialist pattern.

- Session 19: Define Lorekeeper's callable contract for other agents: request schema, response schema, error states, trace id, SQL, tables used, assumptions.
- Session 20: Decide how Lorekeeper exposes itself — as a tool in a parent agent's tool list, or wrapped as an MCP server. Build the wrapper.
- Session 21–22: Build a minimal Streamwright agent that drafts Airflow DAGs and delegates data questions to Lorekeeper.
- Session 23: Test: *"Build a DAG that copies orders to a daily summary table"* — Streamwright calls Lorekeeper for schema, composes the DAG.

**Done when:** Composition works for at least one realistic example. Lorekeeper was reused unchanged from Phase 3.

---

## Phase 5 — Production hardening (Ongoing)

Pick one per sprint based on what's actually painful:

- Cost tracking for API models
- PII detection before returning query results
- Eval expansion to 50+ questions
- Auth rotation for MCP server tokens
- Production deployment topology

---

## Session rhythm

1. **5 min:** State where you left off and what you're testing today.
2. **45 min:** Build or tune with Claude Code. Run something. Observe.
3. **10 min:** Write the session note. What worked, what didn't, what's next.

## Time summary

| Phase | Sessions | Focus |
|-------|----------|-------|
| 2 — MCP servers | 2 | Infrastructure done |
| 2.5 — Golden traces | 2 | Reference behaviour |
| 3 — Agent | 8 | The actual product |
| 4 — Composition | 5 | Multi-agent pattern |

Working Lorekeeper by **session 17**. Agent composition by **session 23**.
