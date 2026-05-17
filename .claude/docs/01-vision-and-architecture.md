# Vision and Architecture

## What we're building

A platform of cooperating AI agents that help people across the organization work with data. The agents are organized as a guild, each specialized for one domain, all sharing a common foundation built on MCP (Model Context Protocol).

## The guild

| Agent | Role | Status |
|-------|------|--------|
| **Lorekeeper** | Data Specialist — answers data questions with production-grade SQL, navigates schemas and lineage | In development |
| **Streamwright** | Pipeline Agent — designs and operates data pipelines (Airflow, dbt). Delegates data discovery to Lorekeeper. | Planned |
| **Farstone** | Dashboard/BI Agent — builds and queries dashboards (Metabase). Delegates data work to Lorekeeper. | Planned |
| **Watchwarden** | Monitoring/Alerting Agent — watches data quality, freshness, and pipeline health | Future |
| **Deepwalker** | ML/Prediction Agent — builds and evaluates models against curated data | Future |

## Architectural principles

**MCP is the connective tissue.** Every external system is exposed via an MCP server. Agents do not contain hard-coded API clients.

**Use existing MCP servers.** We do not build MCP servers from scratch when community or official ones exist. We configure, evaluate, and extend them if needed. Building custom servers is a last resort.

**Specialist agents are reusable.** Lorekeeper can be invoked by Streamwright, Farstone, or any future orchestrator. It is the single source of truth for data questions.

**Model-agnostic by design.** Anthropic API during development; local models (Qwen, Llama via Ollama) for sensitive workloads or offline use. Swapping models is a config change.

**Tools over prompts.** Anything the agent does repeatedly belongs as a tool, not as instructions in a system prompt.

**Read before write.** Lorekeeper queries metadata before generating SQL. Streamwright reads existing DAGs before writing new ones.

## Layered topology

```
┌─────────────────────────────────────────────────────────────┐
│  Orchestrator agents                                        │
│  Streamwright    Farstone    (Future agents…)               │
└───────────┬────────────┬────────────────────────────────────┘
            │            │
            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│  Specialist agents                                          │
│  Lorekeeper (Data Specialist)                               │
└───────────┬────────────┬────────────────────────────────────┘
            │            │
            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│  MCP servers (external, configured by us)                   │
│  trino-mcp     openmetadata-mcp     (airflow-mcp, …)       │
└───────────┬────────────┬────────────────────────────────────┘
            │            │
            ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│  Infrastructure                                             │
│  Trino cluster      OpenMetadata catalog      (Airflow, …) │
└─────────────────────────────────────────────────────────────┘
```

## Boundaries

- Lorekeeper **never** writes data. SELECT and metadata queries only.
- Orchestrator agents **never** talk to MCP servers directly when a specialist exists.
- Specialist agents **never** assume schema details. They ask the metadata source first.

## Out of scope (for now)

- Multi-tenant authentication and authorization
- Production deployment topology
- Web UI for non-CLI users
- Cross-organization sharing of agents
