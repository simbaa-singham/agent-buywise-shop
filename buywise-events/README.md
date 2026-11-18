# buywise-events (event publisher and consumers)

Kafka event publisher (committed business events) and event consumers (notifications, projections, staff console updates). Several design decisions are still open.

**Open in:** IntelliJ IDEA -> added to the `buywise-services/` window (Gradle Kotlin DSL build added in phase 4, ADR-041).

## Contents
| Path | Purpose |
|---|---|
| `publisher/, consumers/` | Built in phase 4 |
| `../buywise-docs/buywise-events/` | design.md (docs live in buywise-docs, ADR-048) |

## Run
Built in phase 4.

## Documents
- [buywise-docs/buywise-events/design.md](../buywise-docs/buywise-events/design.md) - detailed design
- System overview: [buywise-docs/00_Architecture_Overview.md](../buywise-docs/00_Architecture_Overview.md); roadmap: [buywise-docs/09_Implementation_Roadmap.md](../buywise-docs/09_Implementation_Roadmap.md)

## Decisions that apply (central log: buywise-docs/adr/ADR_Log.md)
| ADR | Decision |
|---|---|
| [ADR-009](../buywise-docs/adr/ADR_Log.md) |  |
| [ADR-016](../buywise-docs/adr/ADR_Log.md) | Six deployables: web, services, agent, mcp, event-publisher, event-consumers |
