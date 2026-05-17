# SQL quality standards

Generated SQL must be code-review ready:

- Use CTEs for intermediate steps, not nested subqueries.
- Always use fully qualified table names: `catalog.schema.table`.
- Filter on partition columns when querying partitioned tables. Flag queries that don't.
- Add a comment header stating intent and assumptions.
- Prefer explicit `JOIN ... ON` over implicit joins.
- Use meaningful aliases (`o` for orders, `c` for customers), never `t1`/`t2`.
- Sort and limit where appropriate.
- Cast types explicitly when comparing across catalogs/dialects.
- SELECT only, never DDL/DML. This is enforced at the MCP server level too.
