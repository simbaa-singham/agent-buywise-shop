# buywise-mcp - Learning Notes

## Local end-to-end build (2026-10-30)
- **MCP** = a standard way to offer tools to an AI: each tool has a name, description and JSON input schema; the agent lists and calls them over HTTP.
- **Layout (ADR-031):** one process, one server per domain: `/mcp/catalog` (search_products, get_product), `/mcp/inventory` (list_stores, check_stock), `/mcp/orders` (list_my_orders, get_order, quote_order, place_order, cancel_order).
- **SDK v2:** `MCPServer` + `@server.tool()`; stateless streamable HTTP; tool errors raised as `ToolError` so the reason reaches the model.
- **Try:** `make -C buywise-mcp smoke`.

## Phase M step 1 - tool snapshots + integration tests (2026-11-22, ADR-064)
- **Why first:** every later Phase M step changes tools; tests must exist before the changes so each change is seen and checked.
- **Snapshot tests** (`tests/test_snapshots.py`, files in `tests/snapshots/{catalog,inventory,orders}.json`): the SDK `Client` connects to each `MCPServer` **in-process** (no HTTP) and lists tools, prompts, resources; the result must equal the file. A description is a prompt to the model, so any change shows up as a failing test and a git diff. After an intended change: `make -C buywise-mcp snapshots`, review the diff, commit.
- **Approach change (architect, same day):** the current MCP code is a prototype, not a base. Phase M rebuilds buywise-mcp to the M design (version 1); tests are written from the design, test-first. The first version of step 1 snapshotted today's 9 tools and had 11 tests of today's behaviour - both removed; the mechanism and the stack stay. A server without an approved snapshot is skipped until its M-design contract is reviewed.
- **Integration tests** (`tests/integration/`): Testcontainers starts Postgres (`pgvector/pgvector:pg17` + `buywise-db/database/01-databases.sh`) and `buywise-services:dev` on a private Docker network; Flyway runs on services start; the seed SQL from `buywise-db/services/02-dml` loads `03-data`; MCP runs in the test process on a free port; tools are called over Streamable HTTP like the agent does (`call(...)` fixture), and the database is checked directly (`stack.sql(...)`). `test_stack.py` checks the stack itself (services healthy, 50 products, 10 stores, orders, MCP up). ~8 s per run.
- **Services image** (`buywise-services/Dockerfile`, `make -C buywise-services image`): Java 25 JRE + the jar, non-root user; settings from environment variables. Reused for Kubernetes later.
- **Findings:** tools returning `dict` (get_product, check_stock, get_order, quote/place/cancel) send no structured result, only JSON text - list tools get `{"result": [...]}` automatically (fixed in step 2, ADR-054). Tool errors arrive as "Error executing tool <name>: <message>" text (typed in step 2, ADR-055).
- **Commands:** `make -C buywise-mcp test` (snapshots + lint), `make -C buywise-mcp snapshots`, `make -C buywise-mcp test-integration` (builds the image, runs the containers). CI job `mcp` runs both.
