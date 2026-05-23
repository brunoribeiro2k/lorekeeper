# Development Environment

## Machines

### Primary laptop (GPU)

- Ubuntu 26.04 LTS, kernel 7.0.0-15-generic
- NVIDIA RTX 3070, 8 GB VRAM — 16 GB system RAM
- NVIDIA driver 595.58.03, CUDA 13.2
- Ollama model: `qwen2.5:14b` (Q4_K_M, ~8 GB VRAM, GPU-offloaded)

### Secondary laptop (RAM)

- Ubuntu 24.04 LTS
- CPU-only — 32 GB system RAM
- Ollama model: `qwen2.5:7b` (CPU inference, fits in RAM)

Both machines run the full local stack (Docker, Trino, OpenMetadata, Ollama). The repo is shared via git; `.env` is machine-local.

---

## Container runtime

Docker on both machines. Services started with `docker compose up -d`.

### GPU passthrough (primary laptop only)

```bash
docker run --rm --gpus all nvidia/cuda:12.3.0-base-ubuntu22.04 nvidia-smi
```

---

## Services

### Ollama

- Official install script, API at `http://localhost:11434` (OpenAI-compatible)
- Model set per machine via `LOREKEEPER_OLLAMA_MODEL` in `.env`

### Trino

- At `http://localhost:8081`, no auth (development only)
- Catalogs: `hive`, `iceberg` (see `05-data-model.md`)
- Compose files: `~/projects/brunoribeiro2k/local-env/trino-local/`

### Trino MCP server

- `alaturqua/mcp-trino-python`, managed by `local-env/trino-local`
- HTTP at `http://localhost:8082/mcp`
- Registered user-scoped: `claude mcp add --transport http --scope user trino http://localhost:8082/mcp`

### OpenMetadata

- At `http://localhost:8585`
- Built-in MCP server at `http://localhost:8585/mcp` (stateless HTTP, confirmed Phase 1 Session 4)
- Registered user-scoped: `claude mcp add --transport http --scope user openmetadata http://localhost:8585/mcp --header "Authorization: Bearer $OM_TOKEN"`
- Compose files: `~/projects/brunoribeiro2k/local-env/open-metadata-local/`

### Not installed yet

- Airflow — Phase 4, Docker Compose

---

## Python

- pyenv, pinned to 3.13.13 via `.python-version`
- venv at `.venv/` (gitignored)
- uv 0.11.14 — package manager and tool runner (`uvx` used to run MCP servers without installing them)

| Package | Purpose |
|---------|---------|
| `anthropic` | Anthropic API client |
| `trino` | Trino Python client (for direct testing) |
| `mcp` | MCP client/server SDK |
| `pydantic` | Data models |
| `pytest` | Tests |
| `ruff` | Lint + format |
| `python-dotenv` | Env var loading |

---

## Memory budget

### Primary laptop (GPU) — 16 GB RAM, tight

| Service | RAM |
|---------|-----|
| OpenMetadata stack | ~5–6 GB |
| Trino | ~2–3 GB |
| Ollama + Qwen 14B | ~8 GB VRAM (separate pool) |
| Agent + MCP servers | ~200 MB |
| OS + browser + editor | ~3–4 GB |

Stop services not in active use. OpenMetadata and Trino together already fill most of system RAM.

### Secondary laptop (RAM) — 32 GB RAM, comfortable

| Service | RAM |
|---------|-----|
| OpenMetadata stack | ~5–6 GB |
| Trino | ~2–3 GB |
| Ollama + Qwen 7B | ~6–8 GB (CPU) |
| Agent + MCP servers | ~200 MB |
| OS + browser + editor | ~3–4 GB |

~10–15 GB headroom. No GPU — Ollama inference is slower but all services can run simultaneously.
