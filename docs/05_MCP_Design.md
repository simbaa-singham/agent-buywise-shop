# MCP (`buywise-mcp`) - Detailed Design

Part of [00_Architecture_Overview.md](00_Architecture_Overview.md) - agent-buywise-shop. Status: Draft.

## 1. Purpose
Expose business capabilities to agents as versioned, scoped, secure tools. A separate deployable so any agent can reuse the tools (production practice: MCP as a thin layer over existing APIs).

## 2. Technology
| Concern | Choice |
|---|---|
| Servers | Python 3.12, MCP Python SDK v2 (stable since 2026-07-28) |
| Spec | MCP 2026-07-28 (stateless core) |
| Transport | Streamable HTTP behind Envoy Gateway / Kubernetes Service |
| Server layout | One MCP server per domain, mounted in one process: `/mcp/catalog`, `/mcp/inventory`, `/mcp/order`, `/mcp/customer`, `/mcp/helpdesk` (ADR-031) |
| Backend | Wraps `buywise-services` REST APIs |
| Auth | OAuth 2.0 resource server, Keycloak as authorization server; accepts only tokens with `aud: buywise-mcp`; calls services with an exchanged token (RFC 8693), never passes tokens through (ADR-028) |
| Tracing | OpenTelemetry (on by default in SDK v2), W3C trace context in `_meta` |

## 3. How the 2026-07-28 spec is used
| Spec feature | Use in buywise-mcp |
|---|---|
| Stateless requests, no session IDs | Any replica serves any request; plain load balancing |
| `server/discover` | Agent discovers tools and capabilities on demand |
| `Mcp-Method` / `Mcp-Name` headers | Gateway routing, rate limits and logs per tool |
| Multi-round-trip requests (`input_required`) | Checkout confirmation and OTP prompts; signed, expiring `requestState` |
| Cache hints (`ttlMs`, `cacheScope`) | Agent caches `tools/list` |
| Explicit handles | `cart_id`, `order_id` passed as arguments |
| JSON Schema 2020-12 | Versioned tool input/output schemas |
| Extensions (Tasks, MCP Apps) | Optional, later |

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
| Envoy | Global per-tool limit via `Mcp-Name` header | Overload |
| MCP server | Per user (`sub`) or guest session, per tool; Redis token buckets | Abuse, brute force |
| `buywise-services` | Bucket4j per caller | Last line of defence |

Per-user MCP limits (production):
| Tool | Limit |
|---|---|
| `verify_customer` | 3 attempts / 15 min per contact and per IP, then lockout |
| `checkout` | 5 / min per user |
| `create_ticket` | 3 / hour per conversation |
| search and read tools | 60 / min per user |

- Local: per-user limits unchanged; global Envoy limits / S (docs/00 section 7.1).
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
- Tool -> scope map (initial): catalog/inventory/knowledge tools `catalog:read`; cart tools `cart:write`; `checkout` `orders:write` (+ confirmation); `list_orders`, `get_order_status` `orders:read`; `create_ticket` `tickets:write`; `verify_customer` public.
- Guests: public scopes only, plus their own cart via `cart_id`. `verify_customer` (OTP) returns a short-lived grant limited to that contact's orders; MCP sends it with order tools. Details at implementation.

## 6. Open decisions
1. ~~Server grouping~~ - decided: one server per domain in one process (ADR-031).
2. ~~Tool-level rate limits~~ - decided: four layers (ADR-032).
3. ~~User identity propagation~~ - decided: token exchange per hop (ADR-028).
