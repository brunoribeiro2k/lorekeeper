# Lorekeeper

A Data Specialist AI agent that answers data questions with production-grade SQL. Part of a larger guild of cooperating agents built on MCP (Model Context Protocol).

## Current phase

Phase 1 — Setting up and learning existing MCP servers for Trino and OpenMetadata. Not building MCP servers from scratch; using community/official ones.

See @.claude/docs/03-learning-path.md for the full plan.

## Tech stack

- Python 3.13.13 (pyenv + venv)
- Trino at localhost:8081 (hive + iceberg catalogs)
- OpenMetadata (to be deployed, Podman compose)
- Ollama with qwen2.5:14b for local inference
- Podman 5.7 (rootless, GPU passthrough via CDI)
- Ubuntu 26.04, RTX 3070 (8 GB VRAM), 16 GB RAM

## MCP servers (external, not built by us)

- **Trino**: `txn2/mcp-trino` (Go binary) or `alaturqua/mcp-trino-python` (Python)
- **OpenMetadata**: built-in MCP server (shipped with OpenMetadata 1.8+) or `mcp-server-openmetadata` (PyPI)

## Key commands

```bash
source .venv/bin/activate
ollama run qwen2.5:14b          # local model
podman compose up -d             # start services
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
