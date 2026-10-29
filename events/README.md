# events - event publisher and consumers

Kafka event publisher (committed business events) and event consumers (notifications, projections, staff console updates). Several design decisions are still open.

## Contents
| Path | Purpose |
|---|---|
| `publisher/, consumers/` | Built in phase 4 |
| `docs/` | design.md |

## Run
Built in phase 4.

## Documents
- [docs/design.md](docs/design.md) - detailed design
- System overview: [docs/00_Architecture_Overview.md](../docs/00_Architecture_Overview.md); roadmap: [docs/09_Implementation_Roadmap.md](../docs/09_Implementation_Roadmap.md)

## Decisions that apply (central log: docs/adr/ADR_Log.md)
| ADR | Decision |
|---|---|
| [ADR-009](../docs/adr/ADR_Log.md) |  |
| [ADR-016](../docs/adr/ADR_Log.md) | Six deployables: web, services, agent, mcp, event-publisher, event-consumers |
