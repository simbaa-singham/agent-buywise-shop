# Architecture Decision Log

| ADR | Decision | Status | Date |
|---|---|---|---|
| ADR-001 | One monorepo with modules (ui, services, data, agent, deploy) | Accepted | 2026-10-28 |
| ADR-002 | Java for business services, Python for AI layer, TypeScript for UI/BFF | Accepted | 2026-10-28 |
| ADR-003 | Angular 22 for the web UI | Accepted | 2026-10-28 |
| ADR-004 | NestJS 11 + Fastify adapter BFF on Node.js 24 LTS | Accepted | 2026-10-28 |
| ADR-005 | Spring Cloud Gateway as internal gateway in front of Java services | Accepted | 2026-10-28 |
| ADR-006 | Java 25 + Spring Boot 4.1 microservices | Accepted | 2026-10-28 |
| ADR-007 | MCP servers inside Java services (Spring AI 2.0); Python MCP client (SDK v2) | Accepted | 2026-10-28 |
| ADR-008 | LangGraph 1.2 for agent orchestration with Postgres checkpointer | Accepted | 2026-10-28 |
| ADR-009 | Kafka for events with transactional outbox | Accepted | 2026-10-28 |
| ADR-010 | PostgreSQL, schema per service | Proposed | 2026-10-28 |
| ADR-011 | Postgres + pgvector + full-text for RAG | Proposed | 2026-10-28 |

## Template (one section per ADR when detailed)
- **Context:** what problem / forces.
- **Options considered:** with pros and cons.
- **Decision:** what we chose.
- **Consequences:** trade-offs, risks, follow-ups.
