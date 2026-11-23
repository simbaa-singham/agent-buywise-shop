# MCP (`buywise-mcp`) - Detailed Design

Part of [00-architecture-overview.md](../00-architecture-overview.md) - agent-buywise-shop. Status: Draft.

## 1. Purpose
Expose business capabilities to agents as versioned, scoped, secure tools. A separate deployable so any agent can reuse the tools (production practice: MCP as a thin layer over existing APIs).

## 2. Technology
| Concern | Choice |
|---|---|
| Servers | Python 3.12, MCP Python SDK v2 (stable since 2026-07-28) |
| Spec | MCP 2026-07-28 (stateless core) |
| Transport | Streamable HTTP behind Envoy Gateway / Kubernetes Service |
| Server layout | One MCP server per domain, mounted in one process: `/mcp/catalog`, `/mcp/inventory`, `/mcp/order`, `/mcp/customer`, `/mcp/knowledge`, `/mcp/helpdesk` (ADR-031, ADR-058, ADR-060). Built today: catalog, inventory, orders |
| Backend | Wraps `buywise-services` REST APIs |
| Auth | OAuth 2.0 resource server, Keycloak as authorization server; accepts only tokens with `aud: buywise-mcp`; calls services with an exchanged token (RFC 8693), never passes tokens through (ADR-028) |
| Tracing | OpenTelemetry (on by default in SDK v2), W3C trace context in `_meta`; local collector + trace viewer built with the MCP production phase (ADR-063) |

## 3. How the 2026-07-28 spec is used
| Spec feature | Use in buywise-mcp |
|---|---|
| Stateless requests, no session IDs | Any replica serves any request; plain load balancing |
| `server/discover` | Agent discovers tools and capabilities on demand |
| `Mcp-Method` / `Mcp-Name` headers | MCP middleware (no internal gateway): per-tool rate limits, metrics, logs, kill switch (ADR-056) |
| Multi-round-trip requests (`input_required`) + `Elicit` | Confirmation of every non-read-only tool (place, cancel), price lock on resume, 15-min expiry, `quoteId` = idempotency key (ADR-052); OTP prompts; signed, expiring `requestState` |
| Cache hints (`ttlMs`, `cacheScope`) | Tool/resource/prompt lists cacheable 10 min, shared scope, refreshed on new server version; read-only results cached per turn (ADR-057) |
| Explicit handles | `cart_id`, `order_id` passed as arguments |
| JSON Schema 2020-12 | Versioned tool input/output schemas; Pydantic results -> `outputSchema` + `structuredContent` (ADR-054) |
| Tool annotations | readOnly / destructive / idempotent / openWorld on every tool; agent policy driven by them (ADR-053) |
| Tool errors | Typed `{code, message, retryable, hint}`; protocol errors only for protocol faults (ADR-055) |
| Resources | `buywise://stores`, `/stores/{id}`, `/catalog/categories`, `/policies/{doc}` (ADR-058) |
| Prompts | Domain prompts on their servers (`compare_products`, `order_help`, `handoff_summary`) for the intent router and staff console (ADR-059) |
| Progress, cancellation, paging | Progress -> `status.updated`; cancel on stop; cursor paging for orders and search (ADR-062) |
| `Resolve(fn)` (SDK v2) | Customer built from the validated token, invisible to the model (ADR-051) |
| Extensions: Tasks | `request_staff_handoff` on `/mcp/helpdesk` (ADR-060, phase 5) |
| Extensions: MCP Apps | One widget: product comparison with variant picker, sandboxed iframe via `block.app` (ADR-061) |

## 4. Servers and tools (v1)
| Server | Tool | Input | Output |
|---|---|---|---|
| catalog | `search_products` | query, filters | product list |
| catalog | `get_product` | product_id | details, variants, prices |
| catalog | `check_compatibility` | accessory_id, device_model | compatible + note |
| inventory | `check_stock` | variant_id, fulfilment | qty, pickup ready time |
| order | `create_cart` | - (customer from token `sub`; guest carts anonymous) | cart_id |
| order | `add_to_cart` | cart_id, variant_id, qty | cart summary |
| order | `get_cart` | cart_id | items, subtotal, tax, total |
| order | `checkout` | cart_id, fulfilment, address/pickup | order_id, payment_link (confirmation required) |
| order | `list_orders` | - (customer from token `sub`, or guest OTP grant) | orders |
| order | `get_order_status` | order_id | status, tracking/pickup info |
| customer | `verify_customer` | email/phone, otp | customer_id |
| helpdesk | `create_ticket` | conversation_id, intent, summary | ticket_id |

## 4a. Server layout (ADR-031)
- One server per domain at its own path, one container image, one deployable (ADR-016 unchanged).
- Agent connects only to the servers the current intent needs (ADR-030 tool scoping); `server/discover` / `tools/list` cached per server.
- All servers accept `aud: buywise-mcp`; per-tool scopes do fine-grained checks (ADR-028).
- Production option: run a domain (e.g. `order`) as its own Kubernetes Deployment from the same image, by config, to isolate checkout from search load.

## 4b. Rate limits (ADR-032)
| Layer | Limit | Protects against |
|---|---|---|
| Agent | Max 8 tool calls per turn; max 3 identical consecutive calls | Agent loops |
| MCP middleware | Global per-tool limit via `Mcp-Name` header (ADR-056; Envoy is edge-only and never sees agent -> MCP traffic) | Overload |
| MCP server | Per user (`sub`) or guest session, per tool; Redis token buckets | Abuse, brute force |
| `buywise-services` | Bucket4j per caller | Last line of defence |

Per-user MCP limits (production):
| Tool | Limit |
|---|---|
| `verify_customer` | 3 attempts / 15 min per contact and per IP, then lockout |
| `checkout` | 5 / min per user |
| `create_ticket` | 3 / hour per conversation |
| search and read tools | 60 / min per user |

- Local: per-user limits unchanged; global per-tool limits / S (buywise-docs/00 section 7.1).
- On limit: structured tool error with `retryAfter`; the agent explains it in plain words and never retries in a loop.

## 5. Design rules
- Read tools run freely; write tools require confirmation.
- Tool schemas versioned; contract tests against `buywise-services` OpenAPI in CI; runtime output validation.
- Per-intent tool scoping stays in the agent.
- Timeouts, retries and circuit breakers on calls to `buywise-services`.

## 5a. Identity and authorization (ADR-028)
- Identity is never a tool argument: user comes from the token `sub`; tools never accept `customer_id`.
- Inbound: JWT with `aud: buywise-mcp`, scopes narrowed by the agent per intent; MCP checks the tool's required scope before running it.
- Outbound: MCP exchanges the inbound token at Keycloak for `aud: buywise-services` with the scopes the tool needs; `act` chain records agent -> mcp. Exchanged tokens cached in memory until expiry (~5 min).
- Tool -> scope map (ADR-050, merged with the planned tools 2026-11-22): `catalog:read` (search_products, get_product, check_compatibility, knowledge resources); `inventory:read` (list_stores, check_stock); `orders:read` (list_my_orders, get_order, quote_order); `orders:write` (place_order, cancel_order, checkout - always with confirmation, ADR-052); `cart:write` (cart tools, when built); `tickets:write` (create_ticket, request_staff_handoff); `verify_customer` public.
- Guests: the agent's own client-credentials token with `catalog:read` + `inventory:read` (ADR-050), plus their own cart via `cart_id`. `verify_customer` (OTP) returns a short-lived grant limited to that contact's orders; MCP sends it with order tools. Details at implementation.

## 5b. Production MCP features (decided 2026-11-22, ADR-050 to ADR-064)
Built in the MCP production phase (buywise-docs/09) after the deep-dive week; Tasks with the staff console (phase 5).
| # | Area | ADR |
|---|---|---|
| M1 | OAuth resource server, token exchange per hop, per-tool scopes, issuer check (RFC 9207); CIMD deferred | ADR-050 |
| M2 | `Resolve(fn)` identity | ADR-051 |
| M3 | Confirmation through `input_required` + `Elicit` | ADR-052 |
| M4 | Tool annotations drive agent policy | ADR-053 |
| M5 | Structured output (Pydantic, `outputSchema`) | ADR-054 |
| M6 | Typed tool errors, circuit breaker | ADR-055 |
| M7 | Per-tool control in MCP middleware (no internal gateway) | ADR-056 |
| M8 | List caching | ADR-057 |
| M9 | Resources | ADR-058 |
| M10 | Prompts | ADR-059 |
| M11 | Tasks for staff handoff | ADR-060 |
| M12 | MCP Apps (hybrid, one widget) | ADR-061 |
| M13 | Progress, cancellation, paging, logging | ADR-062 |
| M14 | OpenTelemetry tracing | ADR-063 |
| M15 | Tool versioning, snapshots, integration tests, Inspector, tool-choice evals | ADR-064 |

## 6. Open decisions
1. ~~Server grouping~~ - decided: one server per domain in one process (ADR-031).
2. ~~Tool-level rate limits~~ - decided: four layers (ADR-032).
3. ~~User identity propagation~~ - decided: token exchange per hop (ADR-028).
