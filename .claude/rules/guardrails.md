# Guardrails

## What code enforces (not prompts)

- SQL statement allowlist: SELECT, SHOW, DESCRIBE, EXPLAIN only.
- Row cap on query results: default 1000.
- Query timeout: default 30 seconds.
- No multi-statement queries.

## What prompts shape (not code)

- Query style and quality (see sql-quality rule).
- Discovery before action: always check metadata before writing SQL.
- Clarifying questions when the request is ambiguous.
- Stating assumptions explicitly in responses.

The split matters. Guardrails belong in code because prompts can be jailbroken. Quality belongs in prompts because it's about judgment.

## Agent behavior

- Lorekeeper never writes data. Read-only always.
- Orchestrator agents never bypass the specialist. They go through Lorekeeper, not directly to MCP servers.
- Specialists never assume schema details. They ask the metadata source first.
