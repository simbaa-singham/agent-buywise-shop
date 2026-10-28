# agent-buywise-shop - Architecture Overview

An AI shopping assistant that helps customers choose, order and track electronic devices.

Main design document. Module-level detail lives in the linked module docs (01-08).
Decisions are recorded in [adr/ADR_Log.md](adr/ADR_Log.md).

| Field | Value |
|---|---|
| Owner / Architect | Sachin Wakade |
| Purpose | Learning and portfolio project: production-grade design and code, run locally at small scale |
| Status | Draft - under review |
| Last updated | 2026-10-28 |

## 1. Purpose and scope

AI shopping assistant for an online electronics store (Apple products as the sample catalog, US). It helps customers:
1. Choose a device (discover, compare, configure).
2. Place an order (stock check, cart, checkout; delivery or in-store pickup).
3. Track an order (delivery tracking or pickup readiness).
4. Get answers to product and store questions, and reach store staff when needed.

**Out of scope (v1):** returns, exchanges, refunds, trade-ins, voice channel, real payment processing (mock payment links only).

**Runtime:** not hosted. Runs on a Mac with production-shaped infrastructure at small scale; production sizing is configuration only.

## 2. Key decisions (summary)

| Area | Decision | ADR |
|---|---|---|
| Repository | One monorepo with modules | ADR-001 |
| Language split | Java for business services; Python for AI and MCP; TypeScript for UI/BFF | ADR-002 |
| UI | Angular 22 | ADR-003 |
| BFF | Node.js 24 LTS, NestJS 11 + Fastify; serves the Angular build | ADR-004 |
| Business services | One Spring Boot 4.1 modular monolith (Spring Modulith) | ADR-014 |
| MCP | Separate `buywise-mcp` deployable, MCP Python SDK v2, spec 2026-07-28 | ADR-015 |
| Deployables | 6 deployables (see section 5) | ADR-016 |
| Edge | Envoy Gateway (Kubernetes Gateway API); no internal gateway; service mesh as future option | ADR-017 |
| Agent orchestration | LangGraph 1.2 with Postgres checkpointer | ADR-008 |
| Events | Apache Kafka; separate publisher and consumer deployables | ADR-009 |
| Primary database | PostgreSQL, schema per module | ADR-010 (proposed) |
| Vector store | Postgres + pgvector + full-text (hybrid) | ADR-011 (proposed) |
| Runtime | Local-first, small scale; production sizing via config only | ADR-013 |

## 3. System context

| Actor / system | Interaction |
|---|---|
| Customer | Website chat: browse, order, track, questions |
| Store staff | Staff console: tickets, take over conversations |
| Identity provider (Keycloak) | Customer and staff login, service tokens, MCP authorization |
| Payment provider (mock) | Payment links and payment status callbacks |
| Shipping carrier (mock) | Tracking numbers and delivery events |
| LLM provider | Ollama on the Mac (dev/local); model gateway -> vLLM or hosted API (production design) |

## 4. High-level architecture

**Layers**
1. **Edge** - Envoy Gateway: TLS, routing, rate limits for browser traffic.
2. **Experience** - `buywise-web`: Angular 22 app + NestJS BFF (session, SSE streaming, screen aggregation).
3. **AI** - `buywise-agent`: LangGraph agent + RAG pipeline.
4. **Tools** - `buywise-mcp`: MCP servers wrapping the business REST APIs.
5. **Business** - `buywise-services`: Spring Boot modular monolith (catalog, inventory, order, customer, payment mock, helpdesk).
6. **Events** - `buywise-event-publisher` and `buywise-event-consumers` with Kafka.
7. **Data and platform** - Postgres, Redis, Kafka, Keycloak, observability, Kubernetes.

**Request path (chat message)**
1. Browser -> Envoy Gateway -> `buywise-web` (HTTP POST to send; SSE stream to receive).
2. BFF -> `buywise-agent` (streaming HTTP).
3. Agent: load state -> sentiment -> intent router -> intent handler.
4. Handler -> `buywise-mcp` (MCP, stateless) -> `buywise-services` REST.
5. Handler -> RAG retrieval for knowledge questions.
6. Agent -> guardrails -> streamed response -> BFF -> browser.

**Screen path (e.g. order history)**
1. Browser -> `buywise-web` BFF -> `buywise-services` REST (JWT from the session).

**Event path**
1. `buywise-services` commits state + event record in one DB transaction.
2. `buywise-event-publisher` publishes committed events to Kafka (mechanism deferred, see section 8).
3. `buywise-event-consumers` react: notifications, staff console updates, projections.
4. RAG re-indexing on catalog changes (location deferred, see section 8).

## 5. Deployables and modules

| # | Deployable | Contains | Stack | Detailed design |
|---|---|---|---|---|
| 1 | `buywise-web` | Angular app + NestJS BFF (BFF serves the Angular build) | Angular 22, Node.js 24, NestJS 11 + Fastify | [01](01_UI_Angular_BFF_Design.md) |
| 2 | `buywise-services` | Modular monolith: catalog, inventory, order, customer, payment (mock), helpdesk | Java 25, Spring Boot 4.1, Spring Modulith | [02](02_Services_SpringBoot_Design.md) |
| 3 | `buywise-agent` | LangGraph agent, RAG pipeline, evals | Python 3.12, LangGraph 1.2 | [03](03_Agent_Python_Design.md), [04](04_RAG_Design.md) |
| 4 | `buywise-mcp` | MCP servers wrapping `buywise-services` REST APIs | Python 3.12, MCP Python SDK v2 (spec 2026-07-28) | [05](05_MCP_Design.md) |
| 5 | `buywise-event-publisher` | Kafka producers for committed business events | Java (Spring Kafka) - design deferred | [06](06_Eventing_Kafka_Design.md) |
| 6 | `buywise-event-consumers` | Kafka consumers for async reactions | Java (Spring Kafka) - design deferred | [06](06_Eventing_Kafka_Design.md) |

Data stores are covered in [07](07_Data_Database_Design.md); environments and deployment in [08](08_Deployment_Design.md).

## 6. Repository layout

```
agent-buywise-shop/
├── ui/                  # buywise-web: Angular 22 app + NestJS BFF
│   ├── web/             # Angular workspace (customer-web, staff-console, shared)
│   └── bff/             # NestJS 11 + Fastify
├── services/            # buywise-services: one Spring Boot app (modules as packages)
├── mcp/                 # buywise-mcp: Python MCP servers
├── agent/               # buywise-agent: LangGraph agent, RAG, evals
├── events/
│   ├── publisher/       # buywise-event-publisher
│   └── consumers/       # buywise-event-consumers
├── data/                # local infra (Postgres, Redis, Kafka, Keycloak), seed data, knowledge docs
├── deploy/              # Docker Compose, Helm charts, GitHub Actions
└── docs/
```

## 7. Non-functional requirements

| Category | Production design target | Local verified target |
|---|---|---|
| Scale | 200k customers; 50k chats/day; 2,000 concurrent chats; 10x launch spikes | 50 concurrent chats (k6 load test) |
| Chat latency | First token p95 < 1.5 s; full answer p95 < 6 s | Measured and reported on Grafana |
| Tool latency | MCP tool call p95 < 300 ms | Measured |
| Availability | Chat 99.9%; checkout 99.95% | Zero failed requests when one pod of a 2-replica deployable is killed |
| Correctness | Prices, stock, status only from services; cited answers | Scenario eval suite passes |
| Security | OAuth2/JWT; least-privilege tools; no card data; PII masked | Same |
| Data | RPO 5 min, RTO 1 h (order data) | Documented, not tested |

NFR targets are assumptions pending confirmation.

## 8. Cross-cutting concerns

- **Security:** Keycloak for customers, staff and service accounts; BFF session pattern; Spring Security JWT checks in `buywise-services`; OAuth for `buywise-mcp`; OTP for order status. Service mesh (mTLS) is the future path for service-to-service security.
- **Observability:** OpenTelemetry end to end (browser -> BFF -> agent -> MCP -> services); Langfuse for LLM traces; Prometheus/Grafana; structured logs.
- **Resilience:** timeouts, retries, circuit breakers (Resilience4j, LangGraph node policies); fallback to human handoff.
- **Evaluation:** RAG and agent scenario suites in CI (Ragas, DeepEval); contract tests for MCP tools and REST APIs.
- **Governance:** versioned tool schemas and APIs; ADRs for every major decision.

## 9. Open and deferred decisions

| # | Decision | Status |
|---|---|---|
| 1 | Confirm NFR targets (section 7) | Open |
| 2 | Event publishing mechanism: polling outbox relay vs Debezium CDC | Deferred to implementation |
| 3 | Where RAG re-indexing runs: agent vs event consumers | Deferred to implementation |
| 4 | Vector store: pgvector (proposed) vs Qdrant | Open |
| 5 | Production LLM: self-hosted (vLLM) vs hosted API behind a gateway | Open |
| 6 | Event schema format: JSON Schema vs Avro (+ schema registry) | Open |
| 7 | Angular component library | Open |
