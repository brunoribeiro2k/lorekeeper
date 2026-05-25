"""Runtime settings for Lorekeeper."""

from __future__ import annotations

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration loaded from environment variables and `.env`."""

    openmetadata_mcp_url: str = "http://localhost:8585/mcp"
    openmetadata_token: str = ""
    trino_mcp_url: str = "http://localhost:8082/mcp"

    anthropic_model: str = "claude-sonnet-4-6"
    ollama_model: str = "qwen2.5:14b"
    default_backend: str = "anthropic"

    prompt_path: Path = Path("prompts/lorekeeper-system.md")
    trace_dir: Path = Path(".lorekeeper/traces")
    max_agent_turns: int = Field(default=12, ge=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
