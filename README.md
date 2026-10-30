# agent-buywise-shop

An AI shopping assistant that helps customers choose, order and track electronic devices.

Start here: [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), then [docs/00_Architecture_Overview.md](docs/00_Architecture_Overview.md)

Everything about a module lives inside it: `<module>/README.md`, `Makefile`, `docs/design.md`, `docs/learning.md`.

| Module | Deployable | Stack | Module README | Design |
|---|---|---|---|---|
| `buywise-web/` | buywise-web | Angular 22 + NestJS 12 (Fastify), Node.js 24 | [buywise-web](buywise-web/README.md) | [design](buywise-web/docs/design.md) |
| `buywise-services/` | buywise-services | Java 25, Spring Boot 4.1, Spring Modulith | [buywise-services](buywise-services/README.md) | [design](buywise-services/docs/design.md) |
| `buywise-agent/` | buywise-agent | Python 3.12, LangGraph 1.2, RAG | [buywise-agent](buywise-agent/README.md) | [design](buywise-agent/docs/design.md), [RAG](buywise-agent/docs/rag.md) |
| `buywise-mcp/` | buywise-mcp | Python, MCP Python SDK v2 | [buywise-mcp](buywise-mcp/README.md) | [design](buywise-mcp/docs/design.md) |
| `buywise-events/` | buywise-event-publisher, buywise-event-consumers | Java, Kafka | [buywise-events](buywise-events/README.md) | [design](buywise-events/docs/design.md) |
| `data/` | - | Seed data, knowledge documents, eval sets | [data](data/README.md) | [design](data/docs/design.md) |
| `deploy/` | - | Docker Compose, kind, Helm, GitHub Actions | [deploy](deploy/README.md) | [design](deploy/docs/design.md) |

**One repo, one editor per module.** All IDEs share this Git repo; each opens only its module folder:

| Editor | Open folder | Notes |
|---|---|---|
| WebStorm | `buywise-web/` | Angular app (`web/`) + NestJS BFF (`bff/`), each its own npm project; chat contract |
| PyCharm | `buywise-agent/` + attach `buywise-mcp/` | Each with its own `.venv` interpreter, created by uv (ADR-042) |
| IntelliJ IDEA | `buywise-services/` (+ `buywise-events/` in phase 4) | Spring Boot / Java |
| Any (IntelliJ or VS Code) | repo root, `deploy/`, `data/`, `docs/` | Compose, data, cross-module docs |

Cross-module documents (`docs/`): [architecture overview](docs/00_Architecture_Overview.md), [decisions (ADR log)](docs/adr/ADR_Log.md), [roadmap](docs/09_Implementation_Roadmap.md), learning index: [Phase 0](docs/learning/Phase-0.md), [Local end-to-end build](docs/learning/Phase-1.md).

## Run it on the Mac
Prerequisites: Docker Desktop, Java 25, Node 24, uv (`brew install uv`), Ollama running (`ollama serve`) with
`qwen2.5:7b` and `bge-m3` pulled.

**First time only**
```bash
make up                       # Postgres (+pgvector), Redis, Keycloak, LiteLLM in Docker
make migrate                  # create the tables (Flyway V1-V4)
# load seed data: data/docs/walkthroughs/load-seed-data.md (catalog, stores, stock)
#   then: docker exec -i buywise-postgres-1 psql -U postgres -d services < data/docs/walkthroughs/load-seed-customers-orders.sql
make demo-user                # local login: username demo, password in deploy/compose/.env
make agent-dev                # Python env for the agent
make -C buywise-mcp dev       # Python env for the MCP servers
make -C buywise-web install   # npm packages for the web app and BFF
make -C buywise-agent ingest  # load help articles and policies into pgvector
```

**Every day**
```bash
make start    # everything -> http://localhost:3000   (logs in logs/)
make stop     # stop the app processes (make down also stops Docker)
```

Try: "Is the iPhone 18 Pro in stock at the Austin store?", "How long will the store hold my pickup order?", then
**Log in** (demo) and "I want the 256GB Silver for pickup in Austin" -> quote -> "yes", or "Where is my latest order?".

| Part | Address | Started by |
|---|---|---|
| Web app + BFF | http://localhost:3000 | `make -C buywise-web run` |
| Agent API | http://localhost:8000 | `make -C buywise-agent run` |
| MCP servers | http://localhost:8090/mcp/{catalog,inventory,orders} | `make -C buywise-mcp run` |
| Services REST | http://localhost:8081/api | `make -C buywise-services run` |
| Keycloak | http://localhost:8080 | `make up` |

Terminal checks: `make -C buywise-agent turn Q="..." C=cu-demo`, `make -C buywise-mcp smoke`, `make test`.
