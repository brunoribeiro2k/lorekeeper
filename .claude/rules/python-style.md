# Python conventions

- Python 3.13 is the floor.
- `ruff` for linting and formatting.
- Type hints on every function signature.
- Pydantic models for all tool inputs and outputs. No untyped dicts at API boundaries.
- Docstrings on every public function. First line is a one-sentence summary.
- Tests in `tests/`, mirroring the package layout.
- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- Secrets in `.env`, loaded via `python-dotenv` or `pydantic-settings`. Never logged.
- Package names lowercase: `lorekeeper`, `trino_mcp`, `openmetadata_mcp`.
- Tool functions follow `verb_noun` style: `list_tables`, `describe_table`, `run_query`.
