# mcp - buywise-mcp

MCP tool servers (Python, MCP SDK v2): one server per business domain, wrapping the buywise-services REST APIs as tools for the agent.

## Contents
| Path | Purpose |
|---|---|
| `docs/` | design.md |

## Run
Built from phase 1.

## Documents
- [docs/design.md](docs/design.md) - detailed design
- System overview: [docs/00_Architecture_Overview.md](../docs/00_Architecture_Overview.md); roadmap: [docs/09_Implementation_Roadmap.md](../docs/09_Implementation_Roadmap.md)

## Decisions that apply (central log: docs/adr/ADR_Log.md)
| ADR | Decision |
|---|---|
| [ADR-015](../docs/adr/ADR_Log.md) | `buywise-mcp` as separate deployable, MCP Python SDK v2, spec 2026-07-28, wrapping REST APIs |
| [ADR-028](../docs/adr/ADR_Log.md) | Identity propagation: OAuth 2.0 token exchange (RFC 8693) at each hop BFF -> agent -> MCP -> services; audience-restricted, scope-narrowed, short-l... |
| [ADR-031](../docs/adr/ADR_Log.md) | MCP layout: one server per domain (`/mcp/{domain}`) in one process and image; agent connects per intent; optional per-domain Deployment in production |
| [ADR-032](../docs/adr/ADR_Log.md) | Tool rate limits in four layers: agent per-turn caps, Envoy global per tool, MCP per user per tool (Redis), services Bucket4j |
