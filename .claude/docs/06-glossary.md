# Glossary

## MCP terms

**MCP (Model Context Protocol)** — Open protocol from Anthropic for connecting language models to external tools and data sources.

**MCP server** — A process exposing tools, resources, and/or prompts to MCP clients. Runs locally (stdio) or remotely (HTTP/SSE).

**MCP client** — Software that connects to MCP servers and makes their capabilities available to a model.

**Tool** — A function the agent can call. Has a name, description (read by the model), input schema, and return value.

**Resource** — Read-only context an agent can fetch. Files, documents, URLs. Not for actions.

**Prompt** — A reusable prompt template exposed by a server.

**Tool call** — The act of a model invoking a tool with structured arguments. Result returns in the next turn.

## Agent terms

**Agent** — A language model running in a loop with access to tools, working toward a goal.

**System prompt** — Instructions shaping the agent's behavior, role, and style. Loaded once, not visible to users.

**Agent loop** — Receive input → model generates → if tool call, execute and return result → repeat until done.

**Orchestrator agent** — Delegates work to specialist agents. In this project: Streamwright, Farstone.

**Specialist agent** — Narrowly scoped to one domain. In this project: Lorekeeper.

**Eval / benchmark** — Fixed inputs with expected outputs, used to measure agent quality and catch regressions.

## Data terms

**Trino** — Distributed SQL query engine. Federates queries across data sources via connectors.

**Connector** — Trino plugin for a specific data source (Hive, Iceberg, MySQL, etc).

**Catalog** — Named set of schemas in Trino, backed by one connector.

**Schema** — Namespace inside a catalog containing tables.

**Iceberg** — Open table format with schema evolution, time travel, partition evolution.

**Hive** — Legacy table format and metadata layer.

**Partition** — Physical division of a table by column values. Filtering on partition columns avoids scanning unrelated data.

**OpenMetadata** — Open-source metadata platform for discovery, lineage, ownership, quality, and governance.

**Lineage** — The graph of which tables feed which other tables.

## The guild

Fantasy-guild naming for memorability and distinct roles.

**Lorekeeper** — Keeper of data lore. Knows where everything is and how to ask it questions. Data Specialist.

**Streamwright** — Builder of streams. Designs and operates data pipelines. Pipeline Agent.

**Farstone** — A seeing-stone showing distant things. Dashboard/BI Agent.

**Watchwarden** — Stands watch, raises alarms. Monitoring/Alerting Agent.

**Deepwalker** — Goes into the depths, returns with foresight. ML/Prediction Agent.
