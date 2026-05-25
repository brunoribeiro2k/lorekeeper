"""Tests for settings and MCP server config helpers."""

from __future__ import annotations

from lorekeeper.core.config import Settings
from lorekeeper.mcp.client import build_server_configs


def test_settings_defaults() -> None:
    """Settings expose the default local MCP endpoints."""
    settings = Settings()

    assert settings.openmetadata_mcp_url == "http://localhost:8585/mcp"
    assert settings.trino_mcp_url == "http://localhost:8082/mcp"


def test_build_server_configs_includes_auth_header() -> None:
    """OpenMetadata token is converted into an Authorization header."""
    settings = Settings(openmetadata_token="abc123")

    configs = build_server_configs(settings)
    openmetadata = next(config for config in configs if config.name == "openmetadata")

    assert openmetadata.headers["Authorization"] == "Bearer abc123"
