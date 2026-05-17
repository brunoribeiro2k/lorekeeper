# Development Environment

## Host

- Ubuntu 26.04 LTS, kernel 7.0.0-15-generic
- NVIDIA RTX 3070 laptop, 8 GB VRAM
- 16 GB system RAM
- NVIDIA driver 595.58.03, CUDA 13.2

## Container runtime

- Podman 5.7 via apt, running rootless
- Podman Desktop via Flatpak (GUI wrapper around system Podman)
- Compose extension enabled
- Default registry: `docker.io` (set in `/etc/containers/registries.conf`)

### GPU passthrough

CDI (Container Device Interface) configured:

- CDI specs at `/etc/cdi/nvidia.yaml` and `~/.config/cdi/nvidia.yaml`
- Verified with `nvidia-ctk cdi list` (3 devices)
- Container GPU test:
  ```bash
  podman run --rm \
    --device nvidia.com/gpu=all \
    --security-opt=label=disable \
    nvidia/cuda:12.3.0-base-ubuntu22.04 \
    nvidia-smi
  ```

## Local model

- Ollama (official install script)
- Model: `qwen2.5:14b` (Q4_K_M, ~8 GB VRAM)
- API: `http://localhost:11434` (OpenAI-compatible)

## Trino

- Pre-existing at `http://localhost:8081`
- Catalogs: `hive`, `iceberg` (see `05-data-model.md`)
- No auth (development only)

## Python

- pyenv, pinned to 3.13.13 via `.python-version`
- venv at `.venv/` (gitignored)

### Dependencies

| Package | Purpose |
|---------|---------|
| `trino` | Trino Python client (for direct testing) |
| `anthropic` | Anthropic API client |
| `pydantic` | Data models |
| `pytest` | Tests |
| `ruff` | Lint + format |
| `python-dotenv` | Env var loading |

## Not installed yet

- OpenMetadata — Phase 2, Podman compose
- Airflow — Phase 4, Podman compose

## Memory budget

| Service | RAM |
|---------|-----|
| OpenMetadata stack | ~5–6 GB |
| Trino | ~2–3 GB |
| Ollama + Qwen 14B | ~8 GB VRAM (separate) |
| Agent + MCP servers | ~200 MB |
| OS + browser + editor | ~3–4 GB |

Stop services not in active use during development.
