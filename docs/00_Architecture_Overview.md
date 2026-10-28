# agent-buywise-shop - Architecture Overview

An AI shopping assistant that helps customers choose, order and track electronic devices.

Main design document. Module-level detail lives in the linked module docs (01-08).
Decisions are recorded in [adr/ADR_Log.md](adr/ADR_Log.md).

| Field | Value |
|---|---|
| Owner / Architect | Sachin Wakade |
| Status | Draft - under review |
| Last updated | 2026-10-28 |

## 1. Purpose and scope

AI assistant for an online store selling Apple products (US). It helps customers:
1. Place an order (discover, compare, configure, check stock, checkout).
2. Check order status (delivery tracking or pickup readiness).
3. Get answers to product and store questions.
4. Reach store staff when needed (human handoff).

**Out of scope (v1):** returns, exchanges, refunds, trade-ins, voice channel, payments processing (mock payment links only).

## 2. Key decisions (summary)

| Area | Decision | ADR |
|---|---|---|
| Repository | One monorepo with modules (ui, services, data, agent, deploy) | ADR-001 |
| Language split | Java for business services; Python for AI; TypeScript for UI/BFF | ADR-002 |
| UI | Angular 22 | ADR-003 |
| BFF | Node.js 24 LTS, NestJS 11 + Fastify adapter | ADR-004 |
| Internal gateway | Spring Cloud Gateway in front of all Java services | ADR-005 |
| Business services | Java 25, Spring Boot 4.1 microservices | ADR-006 |
| Tools for the agent | MCP servers inside Java services (Spring AI 2.0); Python MCP client (SDK v2) | ADR-007 |
| Agent orchestration | LangGraph 1.2 with Postgres checkpointer | ADR-008 |
| Events | Apache Kafka with transactional outbox | ADR-009 |
| Primary database | PostgreSQL (schema per service) | ADR-010 (proposed) |
| Vector store | Postgres + pgvector + full-text (hybrid) | ADR-011 (proposed) |

## 3. System context

| Actor / system | Interaction |
|---|---|
| Customer | Website chat: browse, order, status, questions |
| Store staff | Staff console: tickets, take over conversations |
| Identity provider (Keycloak) | Customer and staff login, service tokens |
| Payment provider (mock) | Payment links and payment status callbacks |
| Shipping carrier (mock) | Tracking numbers and delivery events |
| LLM provider | Ollama (dev); model gateway -> vLLM or hosted API (prod) |

## 4. High-level architecture

**Layers**
1. **Experience layer** - Angular 22 web app (chat widget + staff console).
2. **BFF layer** - NestJS 11 BFF: session/auth, WebSocket streaming, screen aggregation.
3. **AI layer** - Python agent (LangGraph), RAG pipeline, MCP client, evaluation.
4. **Edge (internal)** - Spring Cloud Gateway: routing, JWT validation, rate limits.
5. **Domain services** - Spring Boot microservices with REST APIs + MCP tools.
6. **Data and events** - Postgres, Redis, Kafka.
7. **Platform** - Kubernetes, CI/CD, observability.

**Request path (chat message)**
1. Angular -> BFF (WebSocket).
2. BFF -> Agent API.
3. Agent: load state -> sentiment -> intent router -> intent handler.
4. Handler -> MCP tools -> internal gateway -> domain service.
5. Handler -> RAG retrieval for knowledge questions.
6. Agent -> guardrails -> streamed response -> BFF -> Angular.

**Event path**
1. Domain service writes state + outbox row in one DB transaction.
2. Outbox relay publishes to Kafka.
3. Consumers react: notifications, RAG re-indexing, staff console updates.

## 5. Modules

| Module | Responsibility | Detailed design |
|---|---|---|
| UI + BFF | Customer chat, staff console, session, streaming | [01_UI_Angular_BFF_Design.md](01_UI_Angular_BFF_Design.md) |
| Domain services | Catalog, inventory, order, customer, payment (mock), helpdesk, gateway | [02_Services_SpringBoot_Design.md](02_Services_SpringBoot_Design.md) |
| Agent | LangGraph graph, intents, guardrails, handoff | [03_Agent_Python_Design.md](03_Agent_Python_Design.md) |
| RAG | Knowledge ingestion, hybrid retrieval, reranking, evaluation | [04_RAG_Design.md](04_RAG_Design.md) |
| MCP | Tool servers, client, contracts, versioning, auth | [05_MCP_Design.md](05_MCP_Design.md) |
| Eventing | Kafka topics, event schemas, outbox, consumers | [06_Eventing_Kafka_Design.md](06_Eventing_Kafka_Design.md) |
| Data | Postgres schemas, pgvector, Redis, data ownership | [07_Data_Database_Design.md](07_Data_Database_Design.md) |
| Deployment | Environments, Compose, Kubernetes + Helm, CI/CD, runbooks | [08_Deployment_Design.md](08_Deployment_Design.md) |

## 6. Non-functional requirements (assumptions - to confirm)

| Category | Target |
|---|---|
| Scale | 200k registered customers; 50k chats/day; 2,000 concurrent chats peak; 10x spike on product launch days |
| Chat latency | First streamed token p95 < 1.5 s; full answer p95 < 6 s |
| Tool latency | MCP tool call p95 < 300 ms |
| Availability | Chat 99.9%; order/checkout APIs 99.95% |
| Correctness | Prices, stock, order status always from services (never LLM); answers cite sources |
| Security | OAuth2/JWT everywhere; least-privilege tools; no card data in chat; PII masked in logs |
| Data | RPO 5 min, RTO 1 h for order data |
| Cost | LLM cost per conversation tracked; semantic cache for repeated questions |

## 7. Cross-cutting concerns

- **Security:** Keycloak (customers, staff, service accounts); gateway JWT validation; MCP OAuth; OTP for order status.
- **Observability:** OpenTelemetry traces end to end (UI -> BFF -> agent -> MCP -> service); Langfuse for LLM traces; Prometheus/Grafana metrics; structured logs.
- **Resilience:** timeouts, retries, circuit breakers (Resilience4j, LangGraph node policies); graceful fallback to human handoff.
- **Evaluation:** RAG and agent scenario suites in CI (Ragas, DeepEval); contract tests for tools.
- **Governance:** versioned tool schemas, ADRs for every major decision, deprecation policy for APIs/events.

## 8. Open decisions

1. Confirm NFR targets (section 6).
2. Vector store: pgvector (proposed) vs Qdrant.
3. Production LLM: self-hosted (vLLM) vs hosted API behind a gateway.
4. Database topology: schema per service (proposed) vs database per service.
5. Event schema format: JSON Schema vs Avro (+ schema registry).
6. Deployment target: local Kubernetes vs cloud managed Kubernetes.
7. Angular component library.
