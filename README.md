# agent-buywise-shop

An AI shopping assistant that helps customers choose, order and track electronic devices.

Start here: [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), then [buywise-docs/00-architecture-overview.md](buywise-docs/00-architecture-overview.md)

Each module holds its code, `README.md` and `Makefile`. All documentation lives in `buywise-docs/`: application-level docs at its top, module docs in `buywise-docs/NN-<module>/` (`01-design.md`, `0N-learning.md`); everything numbered in reading order (00 overview, 01-08 modules, 09 roadmap, 10 ADRs, 11 learning, 12 archive; files inside each folder 01, 02, ...) - ADR-048.

| Module | Deployable | Stack | Module README | Design |
|---|---|---|---|---|
| `buywise-web/` | buywise-web | Angular 22 + NestJS 12 (Fastify), Node.js 24 | [buywise-web](buywise-web/README.md) | [design](buywise-docs/01-buywise-web/01-design.md) |
| `buywise-services/` | buywise-services | Java 25, Spring Boot 4.1, Spring Modulith | [buywise-services](buywise-services/README.md) | [design](buywise-docs/02-buywise-services/01-design.md) |
| `buywise-agent/` | buywise-agent | Python 3.12, LangGraph 1.2, RAG | [buywise-agent](buywise-agent/README.md) | [design](buywise-docs/03-buywise-agent/01-design.md), [RAG](buywise-docs/03-buywise-agent/02-rag.md) |
| `buywise-mcp/` | buywise-mcp | Python, MCP Python SDK v2 | [buywise-mcp](buywise-mcp/README.md) | [design](buywise-docs/04-buywise-mcp/01-design.md) |
| `buywise-events/` | buywise-event-publisher, buywise-event-consumers | Java, Kafka | [buywise-events](buywise-events/README.md) | [design](buywise-docs/05-buywise-events/01-design.md) |
| `buywise-data/` | - | Knowledge documents, eval sets, generators (seed JSON goes to buywise-db) | [buywise-data](buywise-data/README.md) | [design](buywise-docs/07-buywise-data/01-design.md) |
| `buywise-db/` | - | Every database script + seed data: `database/`, `services/{01-ddl,02-dml,03-data}`, `agent/` (ADR-046) | [buywise-db](buywise-db/README.md) | [design](buywise-docs/06-buywise-db/01-design.md) |
| `buywise-deploy/` | - | Docker Compose, kind, Helm, GitHub Actions; `local/` run scripts + logs | [buywise-deploy](buywise-deploy/README.md) | [design](buywise-docs/08-buywise-deploy/01-design.md) |
| `buywise-docs/` | - | All documentation: application level at the top, module docs in `buywise-docs/NN-<module>/` (ADR-048) | [index](buywise-docs/README.md) | - |

**One repo, one editor per module.** All IDEs share this Git repo; each opens only its module folder:

| Editor | Open folder | Notes |
|---|---|---|
| WebStorm | `buywise-web/` | Angular app (`web/`) + Node server (NestJS) (`server/`), each its own npm project; chat contract |
| PyCharm | `buywise-agent/` + attach `buywise-mcp/` | Each with its own `.venv` interpreter, created by uv (ADR-042) |
| IntelliJ IDEA | `buywise-services/` (+ `buywise-events/` in phase 4) | Spring Boot / Java |
| Any (IntelliJ or VS Code) | repo root, `buywise-deploy/`, `buywise-db/`, `buywise-data/`, `buywise-docs/` | Compose, database scripts (all databases, ADR-046), data, cross-module docs |

Cross-module documents (`buywise-docs/`): [architecture overview](buywise-docs/00-architecture-overview.md), [decisions (ADR log)](buywise-docs/10-adr/01-adr-log.md), [roadmap](buywise-docs/09-implementation-roadmap.md), learning index: [Phase 0](buywise-docs/11-learning/01-phase-0-foundations.md), [Local end-to-end build](buywise-docs/11-learning/02-phase-1-local-end-to-end.md).

## Run it on the Mac
Prerequisites: Docker Desktop, Java 25, Node 24, uv (`brew install uv`), Ollama running (`ollama serve`) with both
models pulled once: `ollama pull qwen2.5:7b && ollama pull bge-m3`.

**First time only**
```bash
make up                       # Postgres (+pgvector), Redis, Keycloak, LiteLLM in Docker
make migrate                  # create the tables in services + agent (Flyway; scripts in buywise-db/)
make seed                     # load seed data: catalog, stores, stock, customers, orders, tax
make demo-user                # local login: username demo, password in buywise-deploy/compose/.env
make agent-dev                # Python env for the agent
make -C buywise-mcp dev       # Python env for the MCP servers
make -C buywise-web install   # npm packages for the web app and Node server
make ingest                   # load help articles and policies into pgvector (needs Ollama running)
```

**Every day**
```bash
make start    # everything -> http://localhost:3000   (logs in buywise-deploy/local/logs/)
make stop     # stop the app processes (make down also stops Docker)
```

Try: "Is the iPhone 18 Pro in stock at the Austin store?", "How long will the store hold my pickup order?", then
**Log in** (demo) and "I want the 256GB Silver for pickup in Austin" -> quote -> "yes", or "Where is my latest order?".

| Part | Address | Started by |
|---|---|---|
| Web app + Node server | http://localhost:3000 | `make -C buywise-web run` |
| Agent API | http://localhost:8000 | `make -C buywise-agent run` |
| MCP servers | http://localhost:8090/mcp/{catalog,inventory,orders} | `make -C buywise-mcp run` |
| Services REST | http://localhost:8081/api | `make -C buywise-services run` |
| Keycloak | http://localhost:8080 | `make up` |

Terminal checks: `make -C buywise-agent turn Q="..." C=cu-demo`, `make -C buywise-mcp smoke`, `make test`.
