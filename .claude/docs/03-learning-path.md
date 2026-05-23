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
- ⬜ Agent loop not yet built

---

## Phase 2 — Trino MCP wired ✅

**Done.** Both servers connected, user-scoped, visible in `claude mcp list`.

**Session 9 — Full loop verification (1h):**
- Ask: *"Find a table about customer orders and show me 5 rows."*
- Observe the sequence: `search_metadata` → table FQN → Trino query → answer.
- Try a destructive query — confirm it is rejected by the MCP server.
- This is the Lorekeeper core loop, manually triggered via Claude Code.
- Exit: full loop works at least once, both MCP tools called in one turn, DDL blocked.

**Done when:** One question triggers both MCP servers cooperating end-to-end.

---

## Phase 3 — Lorekeeper agent (4–6 sessions)

**Goal:** A standalone CLI agent. `lorekeeper "how many orders per customer?"` works.

Claude Code scaffolds the code. Your job: shape the system prompt and verify outputs.

**Session 10 — Scaffold + system prompt (1h):**
- Claude Code generates: `pyproject.toml`, `agent/cli.py`, `agent/runtime.py`, `agent/models.py`.
- Draft `prompts/lorekeeper-system.md` together. Key behaviours:
  - Always search metadata before writing SQL
  - Use fully qualified table names (`catalog.schema.table`)
  - Filter on partition columns when present
  - State assumptions explicitly
  - Ask one clarifying question when the request is ambiguous
- Exit: `lorekeeper "list tables"` runs without crashing.

**Session 11 — Wire MCP servers into the agent loop (1h):**
- `agent/runtime.py` connects to both MCP servers and executes the tool call loop.
- The loop: receive question → call tools as needed → return answer.
- Exit: `lorekeeper "find tables about orders"` calls `search_metadata` and returns results.

**Session 12 — First real question end-to-end (1h):**
- `lorekeeper "how many orders per customer?"` → discovery → SQL → answer.
- Fix what breaks. Focus on the loop, not the prompt.
- Exit: at least one realistic question answered correctly.

**Session 13 — Eval harness + baseline (1h):**
- Write `evals/questions.yaml` — 20 questions covering: schema discovery, aggregation, filtering, partition-awareness, ambiguity handling.
- Claude Code builds `evals/run_eval.py`.
- Run baseline. Score it. Identify the most common failure mode.
- Exit: baseline score recorded, top failure mode identified.

**Session 14 — Prompt tuning (1h):**
- Fix the top failure mode by editing `prompts/lorekeeper-system.md`.
- Re-run eval. Target: ≥15/20 on Claude.
- Exit: score improved, at least one prompt change validated by eval.

**Session 15 — Ollama backend (1h):**
- Add Ollama backend to `agent/models.py`. Switch via `LOREKEEPER_OLLAMA_MODEL`.
- Run eval on Qwen. Targets: ≥10/20 on `qwen2.5:14b`, ≥7/20 on `qwen2.5:7b`.
- Document failure modes specific to local models (tool call formatting, hallucinated FQNs, etc.).
- Exit: both Claude and Ollama backends working, eval scores recorded.

**Done when:** `lorekeeper "<question>"` produces correct answers for ≥15/20 on Claude, ≥10/20 on Qwen 14B, ≥7/20 on Qwen 7B.

---

## Phase 4 — Agent composition (3–4 sessions)

**Goal:** Lorekeeper callable by another agent. Validate the specialist pattern.

- Session 16: Decide how Lorekeeper exposes itself — as a tool in a parent agent's tool list, or wrapped as an MCP server. Build the wrapper.
- Session 17–18: Build a minimal Streamwright agent that drafts Airflow DAGs and delegates data questions to Lorekeeper.
- Session 19: Test: *"Build a DAG that copies orders to a daily summary table"* — Streamwright calls Lorekeeper for schema, composes the DAG.

**Done when:** Composition works for at least one realistic example. Lorekeeper was reused unchanged from Phase 3.

---

## Phase 5 — Production hardening (Ongoing)

Pick one per sprint based on what's actually painful:

- Structured logging of every tool call and its latency
- Cost tracking for API models
- PII detection before returning query results
- Eval expansion to 50+ questions
- Auth rotation for MCP server tokens

---

## Session rhythm

1. **5 min:** State where you left off and what you're testing today.
2. **45 min:** Build or tune with Claude Code. Run something. Observe.
3. **10 min:** Write the session note. What worked, what didn't, what's next.

## Time summary

| Phase | Sessions | Focus |
|-------|----------|-------|
| 2 — Trino MCP | 2 | Infrastructure done |
| 3 — Agent | 6 | The actual product |
| 4 — Composition | 4 | Multi-agent pattern |

Working Lorekeeper by **session 14**. Agent composition by **session 19**.
