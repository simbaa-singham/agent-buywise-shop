# Phase 0 - Learning Index

Phase 0 (foundations) built nothing a customer sees: it prepared the database with products and stock, the login server, the AI gateway and the chat message format that phase 1 needs.
The detailed notes live **inside each module**; this page is the map. Status: steps 1-4 done; 5-7 in progress.

## Steps and where to read them
| Step | What | Learning notes |
|---|---|---|
| 1 | Supporting programs in Docker (Postgres, Redis, Keycloak, LiteLLM), compose.yaml, .env, health checks, make | [deploy/docs/learning.md](../../deploy/docs/learning.md) |
| 2 | Separate databases and users | [deploy/docs/learning.md](../../deploy/docs/learning.md#separate-databases-step-2) |
| 3 | Tables with Flyway, schemas | [buywise-services/docs/learning.md](../../buywise-services/docs/learning.md) |
| 4 | Loading data by hand (SQL from JSON, transactions, UI tools) | [data/docs/learning.md](../../data/docs/learning.md) |
| 5 | Chat message contract (JSON Schema, generated code, tests) - in progress | [buywise-web/docs/learning.md](../../buywise-web/docs/learning.md), [buywise-agent/docs/learning.md](../../buywise-agent/docs/learning.md) |
| 6 | Measuring AI speed, k = 2.96 | [deploy/docs/learning.md](../../deploy/docs/learning.md#measuring-ai-speed---k-step-6) |
| 7 | Glue: Makefiles, CI, README - to be completed | this page |
| - | Build tools decided mid-phase: Gradle Kotlin DSL for Java (ADR-041), uv for Python (ADR-042) | [buywise-agent/docs/learning.md](../../buywise-agent/docs/learning.md#switching-from-pip-to-uv-adr-042) |

Data created before phase 0 (catalog, synthetic people, 103 documents, eval sets): [data/docs/learning.md](../../data/docs/learning.md).

## Cross-module concepts

**Design before code.** The system was designed decision by decision: each Architecture Decision Record (ADR) has context, options, decision and consequences ([docs/adr/ADR_Log.md](../adr/ADR_Log.md)). NFRs set ideal production targets; local targets scale down (volumes / S = 40, AI speed x k). Production-scale operations (backups, DR, replicas, mesh, pooling) are design only ([docs/00 section 7.4](../00_Architecture_Overview.md)).

**Project layout - everything about a module lives in the module.**
```
<module>/
  README.md        what the module is, how to run it, which ADRs apply
  Makefile         the module's own commands
  docs/design.md   detailed design
  docs/learning.md learning notes per phase
```
Cross-module documents stay in `docs/`: architecture overview, ADR log, roadmap, this learning index. The root `Makefile` keeps short commands (`make up`, `make test`) that delegate to module Makefiles.

## Step 7 - Glue (to be completed)
- Root and module Makefiles (see layout above).
- CI on GitHub (`.github/workflows/ci.yml`): contract drift check + tests, compose file validation, migrations applied against a real Postgres.
- `README.md`: module index and local quick start.
