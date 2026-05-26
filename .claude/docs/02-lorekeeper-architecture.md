# Lorekeeper Architecture

## Mission

Lorekeeper answers data questions with production-grade SQL queries. It is the entry point for any question of the form *"what does the data say about X?"* and the worker that any higher-level agent calls when it needs data.

## Required capabilities

1. **Discover.** Given a natural-language question, find the relevant tables without being told where to look.
2. **Reason.** Understand schemas, partitioning, lineage, and column semantics before composing a query.
3. **Compose.** Generate SQL that is correct, efficient, partition-aware, and readable.
4. **Execute.** Run the query against Trino and return results with provenance.
5. **Explain.** State assumptions and clarify ambiguities. Ask follow-up questions when underspecified.

## MCP servers (external)

We use existing MCP servers, not custom-built ones. The agent connects to them as an MCP client.

### Trino MCP server

`alaturqua/mcp-trino-python` — Python implementation, readable source, fits the stack. Supports stdio, streamable HTTP, and SSE transports. Run via `uvx` (no install needed). Config via env vars: `TRINO_HOST`, `TRINO_PORT`, `TRINO_USER`, `TRINO_CATALOG`.

Expected tools: `execute_query`, `list_catalogs`, `list_schemas`, `list_tables`, `get_table_schema`, `explain_query`.

### OpenMetadata MCP server

OpenMetadata's built-in MCP server (shipped with v1.8+, confirmed working in 1.12.x). Fully integrated with the authorization engine, semantic search, lineage, and governance. Requires OpenMetadata to be running.

Endpoint: `POST $OPENMETADATA_URL/mcp` — stateless HTTP/SSE transport. Auth via `Authorization: Bearer <token>` header. Config lives in `.mcp.json` (gitignored). No separate process to spawn.

Expected capabilities: table search by keyword, table metadata with column descriptions, data lineage, tags, ownership.

## Agent runtime

A Python process that:

- Loads the system prompt from `prompts/lorekeeper-system.md`
- Connects to both MCP servers as an MCP client
- Accepts a question (CLI for now)
- Runs the agent loop with the configured model (Anthropic API or local Ollama)
- Returns the answer plus a structured record of what it did

## System prompt

Lives in `prompts/lorekeeper-system.md`. Iterated on as a first-class artifact. Versioned.

Key principles for the prompt:
- Be specific: *"Always filter on partition columns"* not *"write efficient queries."*
- Show examples of good and bad output.
- State the order of operations: search metadata → read schema → write SQL.
- Define when to ask clarifying questions vs. guess.
- Calibrate confidence: state assumptions, flag uncertainty.

## Interaction patterns

### Direct question
User asks → agent searches metadata → reads table schema → composes SQL → executes → returns result with SQL and tables used.

### Ambiguous question
User asks → agent finds multiple interpretations → asks one clarifying question → proceeds.

### Delegated question (called by another agent)
Calling agent passes structured request → Lorekeeper executes full pipeline → returns structured response (rows, sql, tables, assumptions).

## Evaluation

A benchmark of 20 questions against the local sample data. Expected SQL shapes and row counts. Run after every prompt change. Lives in `evals/`.

## Project layout

```
lorekeeper/
├── CLAUDE.md
├── .claude/
│   ├── rules/
│   │   ├── python-style.md
│   │   ├── sql-quality.md
│   │   └── guardrails.md
│   └── docs/
│       ├── 01-vision-and-architecture.md
│       ├── 02-lorekeeper-architecture.md
│       ├── 03-learning-path.md
│       ├── 04-environment.md
│       ├── 05-data-model.md
│       └── 06-glossary.md
├── prompts/
│   └── lorekeeper-system.md
├── src/
│   └── lorekeeper/
│       ├── cli.py
│       ├── agent/
│       │   └── runtime.py
│       ├── core/
│       │   ├── config.py
│       │   └── contracts.py
│       ├── mcp/
│       │   └── client.py
│       ├── model/
│       │   └── backend.py
│       └── observability/
│           └── tracing.py
├── evals/
│   ├── questions.yaml
│   └── run_eval.py
├── tests/
└── pyproject.toml
```
