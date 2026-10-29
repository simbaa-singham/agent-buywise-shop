# agent-buywise-shop

An AI shopping assistant that helps customers choose, order and track electronic devices.

Start here: [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md), then [docs/00_Architecture_Overview.md](docs/00_Architecture_Overview.md)

| Module | Deployable | Stack | Design doc |
|---|---|---|---|
| `ui/` | buywise-web | Angular 22 + NestJS 11 (Fastify), Node.js 24 | [01](docs/01_UI_Angular_BFF_Design.md) |
| `services/` | buywise-services | Java 25, Spring Boot 4.1, Spring Modulith | [02](docs/02_Services_SpringBoot_Design.md) |
| `agent/` | buywise-agent | Python 3.12, LangGraph 1.2, RAG | [03](docs/03_Agent_Python_Design.md), [04](docs/04_RAG_Design.md) |
| `mcp/` | buywise-mcp | Python, MCP Python SDK v2 (spec 2026-07-28) | [05](docs/05_MCP_Design.md) |
| `events/` | buywise-event-publisher, buywise-event-consumers | Java, Kafka | [06](docs/06_Eventing_Kafka_Design.md) |
| `data/` | - | PostgreSQL, Redis, Kafka, Keycloak setup + seed data | [07](docs/07_Data_Database_Design.md) |
| `deploy/` | - | Docker Compose, kind, Helm, GitHub Actions | [08](docs/08_Deployment_Design.md) |

Decisions: [docs/adr/ADR_Log.md](docs/adr/ADR_Log.md)

Roadmap: [docs/09_Implementation_Roadmap.md](docs/09_Implementation_Roadmap.md)

## Local quick start (phase 0)
Prerequisites: Docker, Node 24, Python 3.12+, Ollama running on the host with `qwen2.5:7b` and `bge-m3` pulled.

```bash
make data-tools agent-dev   # one-time: Python tool environments
make up                     # Postgres (+pgvector), Redis, Keycloak, LiteLLM
make seed                   # Flyway schema + catalog/inventory seed into the services database
make k                      # measure the LLM hardware factor k -> deploy/local/scale.yaml
make test                   # contract tests + lint
make help                   # all targets
```
