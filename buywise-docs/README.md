# buywise-docs

Every document of the project lives here (ADR-048).

## Application level
| Document | What |
|---|---|
| [00_Architecture_Overview.md](00_Architecture_Overview.md) | Requirements, NFRs, architecture, deployables, repository layout |
| [09_Implementation_Roadmap.md](09_Implementation_Roadmap.md) | Phases, what is built, simplifications to revisit |
| [adr/ADR_Log.md](adr/ADR_Log.md) | All architecture decisions |
| [learning/](learning/) | Phase learning index (Phase-0, Phase-1) and the deep-dive week |
| [archive/](archive/) | Earlier designs, kept for history |

## Modules
| Module | Docs |
|---|---|
| buywise-web | [design](buywise-web/design.md), [learning](buywise-web/learning.md) |
| buywise-services | [design](buywise-services/design.md), [learning](buywise-services/learning.md) |
| buywise-mcp | [design](buywise-mcp/design.md), [learning](buywise-mcp/learning.md) |
| buywise-agent | [design](buywise-agent/design.md), [rag](buywise-agent/rag.md), [learning](buywise-agent/learning.md) |
| buywise-events | [design](buywise-events/design.md) |
| buywise-data | [design](buywise-data/design.md), [learning](buywise-data/learning.md), [seed-data load walkthrough](buywise-data/walkthroughs/load-seed-data.md) |
| buywise-deploy | [design](buywise-deploy/design.md), [learning](buywise-deploy/learning.md) |
| buywise-db | [design](buywise-db/design.md) (databases, data model, backups, PII), scripts: [buywise-db/README.md](../buywise-db/README.md) |

Each module folder keeps its own README.md (what it is, how to run it, which ADRs apply).
