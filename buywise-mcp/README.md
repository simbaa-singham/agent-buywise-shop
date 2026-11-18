# buywise-mcp

MCP tool servers (Python, MCP SDK v2): one server per business domain, wrapping the buywise-services REST APIs as tools for the agent.

**Open in:** PyCharm -> attached to the `buywise-agent/` window (File > Open > Attach), with its own interpreter `buywise-mcp/.venv` (created by uv from `pyproject.toml` + `uv.lock`, ADR-042).

## Contents
| Path | Purpose |
|---|---|
| `buywise_mcp/app.py` | Starlette app hosting the three servers at `/mcp/catalog`, `/mcp/inventory`, `/mcp/orders` (ADR-031) |
| `buywise_mcp/servers.py` | Tools per domain - catalog: search_products, get_product; inventory: list_stores, check_stock; orders: list_my_orders, get_order, quote_order, place_order, cancel_order (customer id from the request, never a tool argument) |
| `buywise_mcp/services.py` | HTTP client for the buywise-services REST APIs (`SERVICES_URL`, default http://localhost:8081) |
| `tests/smoke.py` | Calls each tool once over HTTP |
| `pyproject.toml, uv.lock, .python-version` | Dependencies, exact pinned versions, Python version (uv, ADR-042) |
| `Makefile` | dev, run, smoke |
| `../buywise-docs/04-buywise-mcp/` | 01-design.md, 02-learning.md (docs live in buywise-docs, ADR-048) |

## Run
`make -C buywise-mcp dev` once (creates `.venv`), then `make -C buywise-mcp run` -> http://localhost:8090/mcp/{catalog,inventory,orders} (needs buywise-services on 8081). `make -C buywise-mcp smoke` calls every tool once. `make start` runs it with everything else.

## Documents
- [buywise-docs/04-buywise-mcp/01-design.md](../buywise-docs/04-buywise-mcp/01-design.md) - detailed design
- [buywise-docs/04-buywise-mcp/02-learning.md](../buywise-docs/04-buywise-mcp/02-learning.md) - learning notes per phase
- System overview: [buywise-docs/00-architecture-overview.md](../buywise-docs/00-architecture-overview.md); roadmap: [buywise-docs/09-implementation-roadmap.md](../buywise-docs/09-implementation-roadmap.md)

## Decisions that apply (central log: buywise-docs/10-adr/01-adr-log.md)
| ADR | Decision |
|---|---|
| [ADR-015](../buywise-docs/10-adr/01-adr-log.md) | `buywise-mcp` as separate deployable, MCP Python SDK v2, spec 2026-07-28, wrapping REST APIs |
| [ADR-028](../buywise-docs/10-adr/01-adr-log.md) | Identity propagation: OAuth 2.0 token exchange (RFC 8693) at each hop Node server -> agent -> MCP -> services; audience-restricted, scope-narrowed, short-l... |
| [ADR-031](../buywise-docs/10-adr/01-adr-log.md) | MCP layout: one server per domain (`/mcp/{domain}`) in one process and image; agent connects per intent; optional per-domain Deployment in production |
| [ADR-032](../buywise-docs/10-adr/01-adr-log.md) | Tool rate limits in four layers: agent per-turn caps, Envoy global per tool, MCP per user per tool (Redis), services Bucket4j |
