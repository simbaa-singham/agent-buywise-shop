# Customer Support Agent - Design

AI assistant for a store selling Apple products (US). It helps customers
place orders, check order status, and get answers to product and store questions.

## Decisions

| Topic | Decision |
|---|---|
| Business | Store selling Apple products (iPhone, Mac, iPad, Watch, AirPods, accessories) |
| Region / currency | US / USD |
| Channel | Website chat first (voice later) |
| Fulfilment | Home delivery and in-store pickup |
| Payment | Payment link (mock); the agent never handles card details |
| Out of scope (v1) | Returns, exchanges, refunds, trade-ins |

## What the agent does

1. **Place an order** - understand need -> recommend -> pick variant -> check stock/price -> add-ons -> cart -> confirm -> payment link.
2. **Check order status** - verify customer (email/phone + OTP) -> list orders -> status, tracking link or pickup time.
3. **Answer questions** - product specs, comparisons, compatibility; store hours, delivery/pickup options, warranty basics. Cites sources; says "I don't know" when not found.
4. **Hand off to store staff** - on request, low confidence, frustration, or out-of-scope asks (returns/exchanges).

## Architecture

1. Angular UI (customer chat widget + staff console) -> **Node BFF** (NestJS 11, Fastify adapter): login/session, WebSocket streaming, screen aggregation.
2. BFF -> **Agent API** (Python, LangGraph) for chat; BFF -> **internal gateway** (Spring Cloud Gateway) for screens (order history, staff console).
3. Agent loads conversation; if staff owns it, forward to staff and stop.
4. **Sentiment check** -> frustrated -> handoff.
5. **Intent router** -> intent + confidence; low confidence -> clarify.
6. **Intent handler** (LangGraph node) with only its own tools.
7. Tools called via **MCP** -> internal gateway -> MCP servers inside the Java services.
8. Java services -> **Postgres** (each service owns its schema); events via **Kafka**.
9. **RAG indexer** (Python) consumes `catalog-events` -> re-indexes pgvector.
10. **Guardrails** -> response saved -> streamed back through the BFF.

## Repository (one monorepo)

```
agent-customer-support/
├── ui/                      # TypeScript
│   ├── web/                 # Angular 22: customer chat widget + staff console
│   └── bff/                 # NestJS 11 + Fastify adapter
├── services/                # Java 25, Spring Boot 4.1 - Maven multi-module
│   ├── pom.xml              # parent POM
│   ├── common/              # shared DTOs, error model, Kafka event schemas
│   ├── gateway/             # Spring Cloud Gateway (internal)
│   ├── catalog-service/
│   ├── inventory-service/
│   ├── order-service/
│   ├── customer-service/
│   ├── payment-service/     # mock
│   └── helpdesk-service/
├── data/                    # infrastructure + content
│   ├── compose/             # local Postgres, Redis, Kafka, Keycloak
│   ├── seed/                # products, variants, stock, sample customers/orders
│   └── knowledge/           # spec sheets, store policies (RAG source docs)
├── agent/                   # Python 3.12
│   ├── pyproject.toml
│   ├── src/                 # LangGraph agent API, MCP client, RAG pipeline + indexer
│   └── evals/               # Ragas + DeepEval suites
├── deploy/                  # Docker Compose (full stack), Helm charts, GitHub Actions
└── docs/                    # design + plans
```

- Each module builds and tests on its own; CI runs only the modules a change touches.
- Flyway migrations stay inside each Java service; `data/` holds shared infrastructure and seed data.

## Technology stack

### Split by responsibility
- **Java / Spring Boot** - business services, gateway, security, transactions, events.
- **Python** - AI layer only: agent, RAG pipeline, evaluation.

### Business services (Java)

| Concern | Choice |
|---|---|
| Runtime | Java 25 + Spring Boot 4.1 / Spring Framework 7 |
| API | Spring Web (REST) + OpenAPI (springdoc) |
| Data | Spring Data JPA + Flyway on Postgres |
| Events | Spring Kafka, transactional outbox pattern |
| Security | Spring Security OAuth2 resource server (JWT) |
| Resilience | Resilience4j: timeouts, retries, circuit breakers, rate limits |
| Observability | Micrometer + OpenTelemetry -> Prometheus / Grafana / tracing |
| Testing | JUnit 5, Testcontainers (Postgres, Kafka), contract tests |
| Internal gateway | Spring Cloud Gateway in front of all Java services (routing, JWT validation, rate limits) |
| MCP servers | Spring AI 2.0 (`@McpTool`) inside each service; MCP Java SDK 2.0 (spec 2025-11-25 today, move to 2026-07-28 when Spring AI adds it) |

### Services

| Service | Owns |
|---|---|
| catalog-service | Products, variants, prices, compatibility |
| inventory-service | Stock per variant/location, reservations |
| order-service | Carts, orders, status, shipments, pickups |
| customer-service | Profiles, OTP verification |
| payment-service (mock) | Payment links, payment status |
| helpdesk-service | Tickets, staff handoff, staff console API |

### AI layer (Python)

| Concern | Choice |
|---|---|
| Orchestration | LangGraph 1.2 + Postgres checkpointer |
| MCP client | MCP Python SDK v2 (negotiates spec version per server) |
| Agent API | FastAPI (async) |
| LLM | Ollama `qwen2.5:7b` (dev); model gateway (e.g. LiteLLM) -> vLLM or hosted API (prod) |
| Embeddings | `nomic-embed-text` (dev) -> `bge-m3` (prod) |
| RAG store | Postgres + pgvector + full-text search (hybrid, RRF) |
| Reranker | `bge-reranker-v2-m3` |
| Parsing | Docling |
| Evaluation | Ragas + DeepEval (CI) |
| LLM tracing | OpenTelemetry -> Langfuse (self-hosted) |

### Platform

| Concern | Choice |
|---|---|
| Database | PostgreSQL (business data, conversations, agent state, vectors) |
| Cache | Redis (semantic cache, rate limits, OTP) |
| Events | Apache Kafka (`order-events`, `inventory-events`, `catalog-events`, `conversation-events`) |
| UI | Angular 22 (signals, Signal Forms, zoneless, Vitest; TypeScript 6) - chat widget + staff console |
| BFF | Node.js 24 LTS, NestJS 11 + Fastify adapter: OAuth2 session, WebSocket gateway, guards, OpenAPI, OpenTelemetry |
| Auth | OAuth2 / JWT (e.g. Keycloak) |
| Runtime | Docker Compose (dev) -> Kubernetes + Helm (prod) |
| CI/CD | GitHub Actions |

## Intents and tool scoping

| Intent | Example | Tools |
|---|---|---|
| browse / recommend | "Laptop for video editing" | `search_products`, `get_product`, `search_knowledge` |
| product_question | "iPhone 17 vs 17 Pro?" | `search_knowledge`, `get_product` |
| compatibility | "Does this charger work with my iPad?" | `check_compatibility`, `search_knowledge` |
| stock_check | "Is the blue one in stock for pickup?" | `check_stock` |
| place_order | "I'll take it" | `create_cart`, `add_to_cart`, `get_cart`, `checkout` |
| order_status | "Where is my order?" | `verify_customer`, `list_orders`, `get_order_status` |
| store_question | "What are your hours?" | `search_knowledge` |
| out_of_scope | "I want to return my iPad" | `create_ticket` (handoff) |
| handoff | "Talk to a person" | `create_ticket` |

## MCP tool contracts (v1)

| Server | Tool | Input | Output |
|---|---|---|---|
| catalog | `search_products` | query, filters (category, price max) | product list |
| catalog | `get_product` | product_id | details, variants, prices |
| catalog | `check_compatibility` | accessory_id, device_model | compatible yes/no + note |
| inventory | `check_stock` | variant_id, fulfilment (delivery/pickup) | available qty, pickup ready time |
| order | `create_cart` | customer_id (optional) | cart_id |
| order | `add_to_cart` | cart_id, variant_id, qty | cart summary |
| order | `get_cart` | cart_id | items, subtotal, tax, total |
| order | `checkout` | cart_id, fulfilment, address or pickup | order_id, payment_link (needs confirmation) |
| order | `list_orders` | customer_id | orders |
| order | `get_order_status` | order_id | status, tracking link or pickup time |
| customer | `verify_customer` | email/phone, otp | customer_id |
| helpdesk | `create_ticket` | conversation_id, intent, summary | ticket_id |

- Each schema is versioned (`order.v1`); the agent pins tested versions.
- `checkout` uses the MCP input-required flow for explicit customer confirmation.

## Key flows

**Place an order**
1. Customer states need -> router: browse/recommend.
2. Agent asks 1-2 questions (use, budget) -> `search_products`.
3. Customer picks product -> `get_product` -> choose variant (chip, color, storage).
4. `check_stock` for chosen fulfilment.
5. Suggest compatible add-ons (`check_compatibility`).
6. Cart built -> agent reads back items, total (tax included), fulfilment.
7. Customer confirms -> `checkout` -> stock reserved -> payment link.
8. Payment confirmed -> order `paid` -> email confirmation.

**Order status**
1. `verify_customer` (OTP) once per session.
2. `list_orders` -> customer picks one -> `get_order_status`.
3. Delivery: status + tracking link. Pickup: ready time + pickup code.

## Order lifecycle

- Delivery: `placed -> paid -> packed -> shipped -> delivered`
- Pickup: `placed -> paid -> preparing -> ready_for_pickup -> picked_up`
- Also: `cancelled`, `payment_failed`, `expired` (unpaid after 30 min; stock released)

## Data model (Postgres)

- `customers`: id, name, email, phone, created_at
- `products`: id, name, category, description
- `variants`: id, product_id, chip, color, storage, memory, price
- `compatibility`: accessory_id, device_model, compatible, note
- `inventory`: variant_id, location (warehouse/store), qty, reserved
- `carts`, `cart_items`
- `orders`: id, customer_id, fulfilment, address, status, total, tax, payment_link, created_at
- `order_items`: order_id, variant_id, qty, unit_price
- `shipments`: order_id, carrier, tracking_no, eta
- `pickups`: order_id, ready_at, pickup_code
- `conversations`, `messages`, `tickets`

## Knowledge (RAG)

- Sources: product spec sheets, comparison notes, compatibility notes, store policies (hours, delivery, pickup, warranty basics).
- Hybrid search (BM25 + vectors + RRF), metadata filters (category, model), citations.
- Prices and stock never come from RAG - only from services (live data).

## Design rules

- Prices, tax, stock and order status come only from services, never from the LLM.
- No card data in chat; payment only via link.
- Order is created only after explicit customer confirmation.
- Order status requires a verified customer.
- Each intent sees only its own tools.
- Returns/exchanges -> polite handoff to staff.

## Cross-cutting

- **Guardrails:** prompt-injection defense on customer text, PII masking in logs.
- **Contract safety:** schema snapshots + contract tests in CI; runtime output validation with handoff fallback.
- **Observability:** OpenTelemetry trace per message.
- **Evaluation:** scenario suite (recommend, compare, order delivery, order pickup, status, out-of-stock, out-of-scope return, handoff).
- **UI:** website chat widget + staff console (tickets, take over chat).
- **Deployment:** Docker Compose; one container per service + MCP, Postgres, Chroma, Ollama.

## Status
Design draft - under review. Replaces the earlier generic plan in `Customer_Support_Agent_Plan.md`.
