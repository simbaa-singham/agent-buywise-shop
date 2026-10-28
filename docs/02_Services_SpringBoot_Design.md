# Domain Services (Spring Boot) - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md). Status: Draft.

## 1. Purpose and responsibilities
Own all business data and rules. Expose REST APIs (for BFF) and MCP tools (for the agent). Publish domain events.

| Service | Owns |
|---|---|
| catalog-service | Products, variants, prices, compatibility |
| inventory-service | Stock per variant/location, reservations |
| order-service | Carts, orders, status, shipments, pickups |
| customer-service | Profiles, OTP verification |
| payment-service (mock) | Payment links, payment status |
| helpdesk-service | Tickets, staff handoff |
| gateway | Spring Cloud Gateway (internal) |

## 2. Technology and versions
| Concern | Choice |
|---|---|
| Runtime | Java 25, Spring Boot 4.1 / Spring Framework 7 |
| API | Spring Web (REST) + OpenAPI (springdoc) |
| Data | Spring Data JPA + Flyway on Postgres |
| Events | Spring Kafka, transactional outbox |
| Security | Spring Security OAuth2 resource server (JWT) |
| Resilience | Resilience4j |
| Observability | Micrometer + OpenTelemetry |
| MCP | Spring AI 2.0 (`@McpTool`), MCP Java SDK 2.0 |
| Testing | JUnit 5, Testcontainers, contract tests |
| Build | Maven multi-module |

## 3. Module structure
```
services/
├── pom.xml
├── common/
├── gateway/
├── catalog-service/
├── inventory-service/
├── order-service/
├── customer-service/
├── payment-service/
└── helpdesk-service/
```

## 4. Interfaces
- REST APIs per service (OpenAPI) - TBD.
- MCP tools - see [05_MCP_Design.md](05_MCP_Design.md).
- Events - see [06_Eventing_Kafka_Design.md](06_Eventing_Kafka_Design.md).

## 5. Key flows
- Checkout: cart -> stock reservation -> order -> payment link -> paid. TBD in detail.

## 6. Non-functional
- TBD (idempotency keys, optimistic locking on stock, rate limits, timeouts).

## 7. Testing
- Unit, integration (Testcontainers), contract (OpenAPI + MCP schemas) - TBD.

## 8. Open decisions
1. Service-to-service calls: synchronous REST only, or events for some flows.
2. Stock reservation strategy and timeout.
