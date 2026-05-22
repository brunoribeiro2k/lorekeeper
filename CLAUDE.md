# Lorekeeper

A Data Specialist AI agent that answers data questions with production-grade SQL. Part of a larger guild of cooperating agents built on MCP (Model Context Protocol).

## Current phase

Phase 1 — Setting up and learning existing MCP servers for Trino and OpenMetadata. Not building MCP servers from scratch; using community/official ones.

See @.claude/docs/03-learning-path.md for the full plan.

## Tech stack

- Python 3.13.13 (pyenv + venv)
- Trino at localhost:8081 (hive + iceberg catalogs)
- OpenMetadata 1.12.x at localhost:8585 (compose stack)
- Ollama for local inference; model selected per machine via `LOREKEEPER_OLLAMA_MODEL`
- Container runtime: Docker on both laptops (GPU passthrough on the primary)
- Primary laptop (GPU): Ubuntu 26.04, RTX 3070 (8 GB VRAM), 16 GB RAM, runs `qwen2.5:14b`
- Secondary laptop (RAM): Ubuntu 24.04, CPU-only, 32 GB RAM, runs `qwen2.5:7b`

## MCP servers (external, not built by us)

- **OpenMetadata**: built-in MCP server, installed by default in OpenMetadata 1.12.x — zero extra install
- **Trino**: `alaturqua/mcp-trino-python` — Python, readable source, fits the stack

## Key commands

```bash
source .venv/bin/activate
ollama run "$LOREKEEPER_OLLAMA_MODEL"   # local model (set in .env)
docker compose up -d                     # start services
```

## Reference docs

Detailed architecture, data model, environment setup, and glossary are in `.claude/docs/`. Read them when working on architecture decisions, data questions, or onboarding context. Don't load them for routine coding tasks.

## Project layout

```
lorekeeper/
├── CLAUDE.md
├── .claude/
│   ├── rules/              # Auto-loaded conventions
│   └── docs/               # On-demand reference
├── prompts/
│   └── lorekeeper-system.md
├── agent/
│   ├── runtime.py
│   ├── models.py
│   └── cli.py
├── evals/
│   ├── questions.yaml
│   └── run_eval.py
├── tests/
└── pyproject.toml
```
