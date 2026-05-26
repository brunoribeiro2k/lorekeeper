# Lorekeeper

A **Data Specialist AI agent** that answers natural-language questions about data by discovering tables in OpenMetadata and executing production-grade SQL against Trino. Part of a larger guild of cooperating agents built on [MCP (Model Context Protocol)](https://modelcontextprotocol.io).

## What it does

```
you: "Which customers placed orders last month but haven't ordered since?"

lorekeeper:
  1. Searches OpenMetadata for "customers" and "orders" tables
  2. Reads schemas and checks partitioning
  3. Generates a CTE-style SQL query with partition filters
  4. Executes via Trino
  5. Returns the answer, the SQL, and the assumptions it made
```

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  Orchestrators (future)                              │
│  Streamwright (pipelines)    Farstone (dashboards)   │
└──────────────┬───────────────────────────────────────┘
               │ calls
               ▼
┌──────────────────────────────────────────────────────┐
│  Lorekeeper (this repo)                              │
│  src/lorekeeper/agent/      →  agent loop           │
│  src/lorekeeper/mcp/        →  MCP client boundary  │
│  src/lorekeeper/model/      →  model backend API    │
│  src/lorekeeper/cli.py      →  lorekeeper "<q>"     │
└──────────┬───────────────────┬───────────────────────┘
           │                   │
           ▼                   ▼
  ┌─────────────────┐  ┌───────────────────────┐
  │  Trino MCP      │  │  OpenMetadata MCP      │
  │  (txn2/mcp-     │  │  (built-in or          │
  │   trino, Go)    │  │   mcp-server-om, PyPI) │
  └────────┬────────┘  └──────────┬─────────────┘
           │                      │
           ▼                      ▼
  ┌─────────────────┐  ┌───────────────────────┐
  │  Trino          │  │  OpenMetadata catalog  │
  │  localhost:8081  │  │  localhost:8585        │
  │  hive + iceberg │  │                        │
  └─────────────────┘  └───────────────────────┘
```

MCP servers are **external processes** — not Python packages. Lorekeeper connects to them as an MCP client via stdio (or HTTP). The MCP servers handle all direct communication with Trino and OpenMetadata.

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.13+ | via pyenv |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Trino | any | running at `localhost:8081` |
| OpenMetadata | 1.8+ | Phase 2 — not needed for Phase 1 |
| Ollama | latest | optional, for local inference |

**MCP servers to install separately:**

```bash
# Option A — Go binary (recommended for Phase 1)
go install github.com/txn2/mcp-trino@latest

# Option B — Python (easier to read the source)
uvx mcp-trino-python  # or: pip install mcp-trino-python

# OpenMetadata MCP (Phase 2)
uvx mcp-server-openmetadata
```

## Setup

```bash
# 1. Clone and enter the project
git clone <repo-url>
cd lorekeeper

# 2. Create the virtual environment and install dependencies
uv sync

# 3. Configure environment
cp .env.example .env
# Edit .env — set TRINO_HOST, ANTHROPIC_API_KEY, etc.

# 4. Activate the venv (optional — uv run handles this)
source .venv/bin/activate
```

## Current status

This branch contains the project skeleton for Phase 3. The CLI, contracts, trace recorder, settings, MCP interfaces, model interfaces, and eval harness are in place. Live model adapters and live MCP transports are the next implementation steps.

## Usage

```bash
# Smoke-test the skeleton CLI
lorekeeper "What tables are in the hive catalog?"

# Show skeleton status and trace id
lorekeeper --verbose "Which customers have pending shipments?"
```

Or run directly with uv:

```bash
uv run lorekeeper "How many orders were placed last month?"
```

## Development

```bash
# Run tests
uv run pytest

# Lint and format
uv run ruff check .
uv run ruff format .

# Run the evaluation benchmark
uv run python evals/run_eval.py
```

## Project structure

```
lorekeeper/
├── README.md
├── pyproject.toml          # uv project config + dependencies
├── .env.example            # env var template
├── .python-version         # pinned to 3.13.13 (pyenv)
│
├── src/
│   └── lorekeeper/         # Python package
│       ├── __init__.py
│       ├── cli.py          # Typer CLI (entry point: lorekeeper)
│       ├── agent/          # Agent runtime and orchestration
│       ├── core/           # Settings and public contracts
│       ├── mcp/            # MCP server config + client protocols
│       ├── model/          # ModelBackend protocol + placeholder backend
│       └── observability/  # JSONL trace recorder
│
├── prompts/
│   └── lorekeeper-system.md  # System prompt (iterated, versioned)
│
├── evals/
│   ├── questions.yaml      # 20-question benchmark
│   └── run_eval.py         # Harness: run benchmark, print results
│
├── tests/
│   ├── test_config.py
│   ├── test_contracts.py
│   └── test_runtime.py
│
└── .claude/
    ├── rules/              # Auto-loaded conventions (SQL, Python, guardrails)
    └── docs/               # Architecture, environment, data model reference
```

## Learning path

This project follows a phase-by-phase plan. Each phase produces something working before adding the next layer.

| Phase | Goal | Status |
|-------|------|--------|
| 0 | Understand MCP; confirm local stack works | Done |
| 1 | Trino MCP server connected; AI client can query tables | Done |
| 2 | MCP servers wired | Done |
| 2.5 | Golden traces | Current |
| 3 | Full Lorekeeper agent with CLI and evals | Skeleton started |
| 4 | Agent composition — Streamwright delegates to Lorekeeper | Planned |
| 5 | Production hardening — auth, observability, PII masking | Future |

Full plan: [`.claude/docs/03-learning-path.md`](.claude/docs/03-learning-path.md)

## Guardrails

- **SELECT only.** DDL and DML are blocked at the MCP server level — not just by prompt.
- **Row cap.** Query results are capped at 1000 rows by default.
- **No multi-statement queries.**
- **Discovery before SQL.** Lorekeeper always reads metadata before generating a query.

## Model backends

| Backend | Config | Use case |
|---------|--------|----------|
| Anthropic (default) | `ANTHROPIC_API_KEY` in `.env` | Development, evals |
| Ollama (local) | `OLLAMA_MODEL=qwen2.5:14b` | Sensitive data, offline |

Concrete Anthropic and Ollama adapters are not wired in this skeleton yet.
