# buywise-mcp

MCP tool servers (Python, MCP SDK v2): one server per business domain, wrapping the buywise-services REST APIs as tools for the agent.

**Open in:** PyCharm -> attached to the `buywise-agent/` window (File > Open > Attach), with its own interpreter `buywise-mcp/.venv` (created in phase 1 by uv: `pyproject.toml` + `uv.lock`, ADR-042).

## Contents
| Path | Purpose |
|---|---|
| `../buywise-docs/buywise-mcp/` | design.md (docs live in buywise-docs, ADR-048) |

## Run
Built from phase 1.

## Documents
- [buywise-docs/buywise-mcp/design.md](../buywise-docs/buywise-mcp/design.md) - detailed design
- System overview: [buywise-docs/00_Architecture_Overview.md](../buywise-docs/00_Architecture_Overview.md); roadmap: [buywise-docs/09_Implementation_Roadmap.md](../buywise-docs/09_Implementation_Roadmap.md)

## Decisions that apply (central log: buywise-docs/adr/ADR_Log.md)
| ADR | Decision |
|---|---|
| [ADR-015](../buywise-docs/adr/ADR_Log.md) | `buywise-mcp` as separate deployable, MCP Python SDK v2, spec 2026-07-28, wrapping REST APIs |
| [ADR-028](../buywise-docs/adr/ADR_Log.md) | Identity propagation: OAuth 2.0 token exchange (RFC 8693) at each hop Node server -> agent -> MCP -> services; audience-restricted, scope-narrowed, short-l... |
| [ADR-031](../buywise-docs/adr/ADR_Log.md) | MCP layout: one server per domain (`/mcp/{domain}`) in one process and image; agent connects per intent; optional per-domain Deployment in production |
| [ADR-032](../buywise-docs/adr/ADR_Log.md) | Tool rate limits in four layers: agent per-turn caps, Envoy global per tool, MCP per user per tool (Redis), services Bucket4j |
