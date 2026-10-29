# Implementation Roadmap - agent-buywise-shop

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md). Status: Draft for architect review.

## 1. Approach
- **Thin vertical slice first:** one real chat turn end to end (browser -> BFF -> agent -> MCP -> services -> back) before widening any layer. Every later phase adds features to a system that already works end to end.
- **Production practices from day one:** contracts, tests, CI, tracing, accessibility checks and PII-safe logging start in phase 0/1, not at the end.
- **Scope rule (docs/00 section 7.4):** only "implemented locally" items are built; "design only" items stay documented.
- **Before each phase:** recap the listed ADRs and what they mean in code; any new decision is raised to the architect, never made silently.
- **Local usage (docs/08 section 4b):** each phase runs only the components it needs.

## 2. Cross-cutting from phase 0 (applies to every phase)
| Practice | Decision |
|---|---|
| Contract-first: JSON Schema in `shared/contracts/`, generated TS + Pydantic, drift check in CI | ADR-024 |
| OpenTelemetry tracing in every deployable; PII masked before logs/traces | ADR-027, ADR-036 |
| Identity never a tool argument; token exchange per hop | ADR-028 |
| Accessibility: angular-eslint a11y rules + axe-core in Playwright | ADR-025 |
| No brand/maker names, no images (placeholders) | ADR-033 |
| Each module has its own tests; CI runs build, unit, contract tests | docs/08 section 7 |

## 3. Phases

### Phase 0 - Foundations
| Item | Detail | ADRs |
|---|---|---|
| Local-dev stack (Docker Compose) | Postgres + pgvector (databases per ADR-010), Redis, Keycloak (realm as code), LiteLLM -> Ollama on host | ADR-010, ADR-011, ADR-013, ADR-026 |
| Repo tooling | Makefile (`make up`, `make seed`, `make ingest`, `make test`), linters/formatters per language, GitHub Actions skeleton | ADR-001 |
| Contracts package | ADR-024 event JSON Schemas + codegen (TS, Pydantic) + CI drift check | ADR-024, ADR-029 |
| Seed data v1 | Catalog generator: phones category only, specs/prices verified; stores; stock; Faker customers | ADR-033 |
| Benchmark `k` | Script measuring local tokens/s; writes `k` to local config | docs/00 section 7.1 |

**Done when:** `make up && make seed` gives a running stack with seeded data; CI green on an empty-but-wired repo.

### Phase 1 - Thin slice: "Is the iPhone 17 Pro in stock at my store?" (guest)
| Layer | Build | ADRs |
|---|---|---|
| `buywise-services` | Spring Modulith app; catalog + inventory modules; Flyway; REST + OpenAPI; JWT resource server; Modulith verification test | ADR-014, ADR-010 |
| `buywise-mcp` | `/mcp/catalog`, `/mcp/inventory` servers: `search_products`, `get_product`, `check_stock`; inbound token check, outbound token exchange | ADR-015, ADR-028, ADR-031 |
| `buywise-agent` | FastAPI `POST /turns` (202) + background run; LangGraph: load_context -> route (rules + LLM classifier, phase 1) -> stock_check handler -> respond; events to `conv:{id}` Redis Stream; LLM client via LiteLLM | ADR-008, ADR-026, ADR-029, ADR-030 |
| `buywise-web` BFF | Guest session (Redis), `POST /api/chat/messages` (idempotent), `GET /api/chat/stream` SSE with `Last-Event-ID` replay, token exchange to agent | ADR-004, ADR-020, ADR-021, ADR-024, ADR-029 |
| `customer-web` | Chat widget: CDK-based message list, streaming text, `status.updated`, `block.product_card` (placeholder image); chat SignalStore + SSE adapter | ADR-018, ADR-019, ADR-022, ADR-024, ADR-025 |

**Done when:** a Playwright test asks a stock question as a guest and gets a streamed, tool-grounded answer; killing the BFF mid-reply and reconnecting completes the reply; contract tests and axe pass; one trace spans all five hops.

### Phase 2 - Login, identity and customer data
| Item | ADRs |
|---|---|
| Keycloak clients (customer, staff, ops-admin roles), BFF login/logout/callback, session rotation, CSRF, timeout warning | ADR-021, ADR-025 |
| Full token exchange with per-intent scopes and `act` chain; verify Keycloak `act` support | ADR-028 |
| Customer module: profiles, field-level envelope encryption + blind index, OTP (`verify_customer`) with lockout | ADR-036, ADR-032 |
| Guest -> customer conversation linking | docs/01 section 5.1 |

**Done when:** login mid-conversation keeps the chat; a customer can only see their own data (negative tests); OTP brute force is locked out.

### Phase 3 - Knowledge and RAG
| Item | ADRs |
|---|---|
| Knowledge docs in many formats (DOCX, digital PDF, scanned PDF/PNG, HTML, XLSX/CSV, PPTX, EML with attachment, Markdown/TXT, generated JSON) from the approved outline | ADR-033, ADR-039 |
| Ingestion worker: detect -> parser plugins -> Document model -> normalize -> validate -> clean -> chunk -> embed; quarantine; golden tests per format; upload + drop folder | ADR-039 |
| Chunking on the Document model, parent-child, context headers, metadata, embeddings, pgvector + full-text | ADR-011, ADR-034 |
| Retrieval: filters, hybrid search, RRF, rerank, citations; retriever interface | ADR-011 |
| Handlers: product_question, compatibility, store_question, browse/recommend | docs/03 section 5 |
| Ragas + RAG eval set in CI; "no price from chunks" check | NFR 8 |
| Seed data v2: remaining categories | ADR-033 |

**Done when:** every format parses to the expected Document model (golden tests); a corrupted file lands in quarantine with a reason; RAG eval thresholds met (NFR 8); citations point to page / slide / row; zero prices taken from chunks.

### Phase 4 - Ordering
| Item | ADRs |
|---|---|
| Order + payment (mock) modules: cart, checkout with confirmation (MCP `input_required`), payment link, order status, pickup | ADR-014, ADR-015 |
| MCP `/mcp/order`, `/mcp/customer`; per-user rate limits | ADR-031, ADR-032 |
| Product/category pages prerendered; cart, checkout, account client-rendered | ADR-023 |
| Kafka + `buywise-event-publisher` + `buywise-event-consumers`; order/payment/catalog events; idempotent consumers | ADR-009, ADR-016 |

**Blocked on architect decisions:** event schema format (docs/00 #6), partitions/retention/DLQ (docs/06), outbox relay vs Debezium (deferred to this phase), RAG re-indexing location (deferred to this phase).

**Done when:** a customer orders through chat with explicit confirmation; order status flows through events; consumers are idempotent under redelivery.

### Phase 5 - Staff console and handoff
| Item | ADRs |
|---|---|
| `staff-console` app: ticket queue (Material table), live updates via SSE composite cursor | ADR-018, ADR-019, ADR-020 |
| Helpdesk module: tickets, assignment, conversation ownership + audit; BFF owner cache | ADR-037 |
| Takeover flow: accept, pause agent, customer <-> staff messages, release/resume | docs/01 section 5.3 |
| Masked contact details with audited reveal; staff MFA | ADR-036, ADR-021 |

**Done when:** a handoff completes end to end in Playwright; customer messages never reach the agent while staff own the chat.

### Phase 6 - LLM operations, budgets and guardrails
| Item | ADRs |
|---|---|
| LiteLLM shadow pricing, global budget; agent per-turn/conversation/customer caps; degradation ladder; admission control queue | ADR-026, docs/00 section 7.3 |
| `turns`, `llm_calls`, `router_decisions` recording; AI Operations (live summary, explorer, budget view) with ECharts wrapper; dev overlay (`message.metrics`) | ADR-027, ADR-038 |
| Presidio placeholders before every LLM call | ADR-036 |
| Router phase 2: train fast classifier, enable cascade tier 2 | ADR-030 |
| Prompt-injection eval set; agent tool-call caps | NFR 9, ADR-032 |

**Blocked on architect decision:** production LLM (docs/00 #5) sets the shadow prices and global budget; placeholder prices can be used until then.

**Done when:** budget limits trigger the ladder (never a bare error); AI Operations shows per-stage latency/tokens/cost; injection evals pass.

### Phase 7 - Production-shaped runtime (local-k8s)
| Item | ADRs |
|---|---|
| Helm chart per deployable; `values-local.yaml` with `S` and `k`; kind cluster; Envoy Gateway (TLS, routing, rate limits) | ADR-013, ADR-017, docs/08 |
| Observability stack: OTel Collector (redaction processor), Prometheus, Grafana (SLO + budget alerts), Tempo, Loki | ADR-027, ADR-036 |
| Probes, limits, graceful shutdown, PDBs, rolling deploys, HPA 2 -> 3 | docs/08 section 6 |
| Failure scenarios (docs/00 section 7.2 #6) and k6 at local scale | NFR 1, 6, 7 |
| Lighthouse CI (Core Web Vitals) | NFR 3 |

**Done when:** all local NFR targets in docs/00 section 7.2 are met and reported on Grafana.

### Phase 8 - Data lifecycle and hardening
| Item | ADRs |
|---|---|
| Retention jobs (transcripts 90 d, logs 30 d, traces 14 d) | NFR 11, ADR-036 |
| Privacy export/deletion jobs from the staff console, audited | ADR-036 |
| Full accessibility manual checklist pass | ADR-025 |
| Review design-only items (docs/00 section 7.4) against what was built | - |

## 4. Open decisions by phase
| Decision | Needed by |
|---|---|
| Event schema format (docs/00 #6) | Phase 4 |
| Partitions, retention, dead-letter topics (docs/06) | Phase 4 |
| Outbox relay vs Debezium (deferred) | Phase 4 |
| RAG re-indexing location (deferred) | Phase 4 |
| Production LLM (docs/00 #5) | Phase 6 (placeholder prices until then) |
| Secrets management (docs/08) | Production design only; local uses Kubernetes secrets |
