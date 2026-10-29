# Business Services (`buywise-services`) - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md) - agent-buywise-shop. Status: Draft.

## 1. Purpose and responsibilities
One Spring Boot application (modular monolith) that owns all business data and rules and exposes REST APIs to the BFF, `buywise-mcp` and event consumers.

| Module | Owns |
|---|---|
| catalog | Products, variants, prices, compatibility |
| inventory | Stock per variant/location, reservations |
| order | Carts, orders, status, shipments, pickups |
| customer | Profiles, OTP verification |
| payment (mock) | Payment links, payment status |
| helpdesk | Tickets, staff handoff |
| shared | Common types, errors, security config |

## 2. Technology and versions
| Concern | Choice |
|---|---|
| Runtime | Java 25, Spring Boot 4.1 / Spring Framework 7 |
| Modularity | Spring Modulith 2.x: boundary verification, module events, Event Publication Registry, per-module Flyway |
| API | Spring Web (REST), controllers per use case, OpenAPI (springdoc) |
| Data | Spring Data JPA + Flyway on Postgres (schema per module) |
| Security | Spring Security OAuth2 resource server (JWT, verified locally via Keycloak JWKS). User calls: `aud: buywise-services`, scopes (`catalog:read`, `cart:write`, `orders:read`, `orders:write`, `tickets:write`, staff scopes) + ownership check on `sub`; `act` chain logged on writes (ADR-028). Staff: staff token via BFF. Event consumers: client-credentials service token (`events-service`), no user |
| PII protection | Field-level envelope encryption for email, phone, address (KMS master key in production, Kubernetes secret locally); blind index (HMAC) for lookups; audited "reveal" for staff (ADR-036) |
| Resilience | Resilience4j; Bucket4j for per-caller rate limits |
| Jobs | Scheduled jobs guarded by ShedLock (run once across replicas) |
| Observability | Micrometer + OpenTelemetry |
| Testing | JUnit 5, Spring Modulith module tests, Testcontainers, contract tests |

## 3. Module structure
```
services/
└── src/main/java/.../buywise/
    ├── catalog/     # api (controllers), application (services), domain, infrastructure (repositories)
    ├── inventory/
    ├── order/
    ├── customer/
    ├── payment/
    ├── helpdesk/
    └── shared/
```

## 4. Rules
- Modules call each other only through public module APIs or module events; never internals.
- No cross-module joins; each module owns its schema.
- Stateless instances: any of the replicas can serve any request.
- Business events recorded in the same transaction as the state change.

## 5. Interfaces
- REST APIs per module (OpenAPI) - TBD.
- Consumed as tools via `buywise-mcp` - see [05_MCP_Design.md](05_MCP_Design.md).
- Events - see [06_Eventing_Kafka_Design.md](06_Eventing_Kafka_Design.md).

## 6. Key flows
- Checkout: cart -> price from catalog -> stock reservation -> order -> payment link -> paid -> reservation confirmed. TBD in detail.

## 7. Open decisions
1. Stock reservation strategy and timeout.
2. Future path: extract a module into its own service if it needs independent scaling.
